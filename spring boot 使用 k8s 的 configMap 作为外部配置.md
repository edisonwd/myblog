

# spring boot 使用 k8s 的 configMap 作为外部配置

## 一、☀️概述

`spring boot` 应用以容器的方式运行在 `k8s` 集群上面是非常方便的，但是不同的环境需要不同的配置文件，我们可以使用外部的配置中心，比如 `nacos` 、`apollo`。`k8s` 也提供了 `configMap` 用来将环境配置信息和容器镜像解耦，便于应用配置的修改。本文主要从以下几个方面介绍 `spring boot` 使用 `k8s` 的 `configMap` 作为外部配置的使用方法：

- `spring boot` 加载配置文件介绍

- `k8s` 的 `configMap` 介绍

- 使用 `k8s` 的 `configMap` 作为外部配置文件

## 二、☀️spring boot 加载配置文件介绍

当应用程序启动时，Spring Boot 会自动从以下位置查找并加载 `application.properties` 和 `application.yaml` 文件。

配置文件优先级从高到底的顺序如下：

1. `file:./config/`  - 优先级最高（项目根路径下的`/config`子目录）

2. `file:./`  - 优先级第二  （项目根路径下）

3. `classpath:/config/`  - 优先级第三（项目`resources/config`下）

4. `classpath:/`  - 优先级第四（项目`resources`根目录）

高优先级配置会覆盖低优先级配置

>  在同级目录下同时存在 `application.properties` 和 `application.yaml` 文件，那么`application.properties` 会覆盖 `application.yaml` 文件

如果我们运行时想指定运行哪个环境的配置文件，可以有三种方式：

1. 在项目 resources 文件夹下的 `application.properties` 文件中配置 `spring.profiles.active=dev` 指定加载的环境
2. 启动 jar 时，指定 `--spring.profiles.active=prod` 加载的环境
3. 启动 jar 时，指定 `--spring.config.location=target/application.properties`加载配置文件位置

## 三、☀️k8s 的 `configMap`介绍

`ConfigMap` 是一种 `API` 对象，用来将非机密性的数据保存到键值对中。使用时 `pod` 可以将其用作环境变量、命令行参数或者存储卷中的配置文件。

> **注意**：
>
> `ConfigMap` 并不提供保密或者加密功能。 如果你想存储的数据是机密的，请使用 `secret`或者使用其他第三方工具来保证你的数据的私密性，而不是用 `ConfigMap`。
>
> `ConfigMap` 在设计上不是用来保存大量数据的，在 `ConfigMap` 中保存的数据不可超过 `1 MiB`，如果需要保存超出此限制的数据，你可以考虑挂载存储卷或者使用独立的数据库或者文件服务。

创建 `configMap` 的几种方式：

1. **使用目录创建**(`--from-file` 指定在目录下的所有文件都会被用在`ConfigMap`里面创建一个键值对，有多少个文件就有多少个键值对，**键的名字就是文件名，值就是文件的内容**)

   ```sh
   kubectl create cm [configmap名称] --from-file=[目录]
   ```

2. **使用文件创建**(`--from-file` 这个参数可以使用多次，效果就跟指定整个目录是一样的)

   ```sh
   kubectl create cm [configmap名称] --from-file=[文件] --from-file=[文件]
   ```

3. **从字面值创建**(`--from-literal` 这个参数可以使用多次)

   ```sh
   kubectl create cm [configmap名称] --from-literal=[键=值] --from-literal=[键=值]
   ```

   示例：使用字面值创建一个 `configMap`

   ```sh
    kubectl create cm myconfigMap --from-literal=env=dev --from-literal=name=test
   ```

   ```sh
   [root@node01 test]# kubectl describe cm my`configMap
   Name:         myconfigmap
   Namespace:    default
   Labels:       <none>
   Annotations:  <none>
   
   Data
   ====
   env:
   ----
   dev
   name:
   ----
   test
   Events:  <none>
   
   ```

4. **使用 `yaml` 清单文件创建**

   创建一个 `game-demo.yaml` 文件，内容如下：

   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: game-demo
   data:
     # 类属性键；每一个键都映射到一个简单的值
     player_initial_lives: "3"
     ui_properties_file_name: "user-interface.properties"
   
     # 类文件键，键的名字就是文件名，值就是文件的内容
     game.properties: |
       enemy.types=aliens,monsters
       player.maximum-lives=5    
     user-interface.properties: |
       color.good=purple
       color.bad=yellow
       allow.textmode=true    
   ```

   使用下面的命令创建 `configMap`：

   ```sh
   kubectl apply -f game-demo.yaml
   ```

   

## 四、☀️使用 k8s 的 `configMap`作为外部配置文件

从前面的介绍我们可以知道，spring boot 加载配置文件的最高优先级是**项目根路径下的`/config`子目录**，所以可以将 `configMap` 中的配置文件挂载到容器中的项目根路径下的`config`子目录中。

1. 可以使用下面的命令从文件中创建一个 `configMap`：

```sh
kubectl create cm  spring-boot-demo  --from-file=application.yaml
```

2. 创建一个 `spring-boot-demo.yaml` 文件内容如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-boot-demo
  namespace: default
  labels:
    app: spring-boot-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spring-boot-demo
  template:
    metadata:
      labels:
        app: spring-boot-demo
    spec:
      containers:
        - name: spring-boot-demo
          image: ${ORIGIN_REPO}/spring-boot-demo:${IMAGE_TAG}
          imagePullPolicy: Always
          env:
            - name: TZ
              value: Asia/Shanghai
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 200m
              memory: 500Mi
          # 指定配置文件挂载到 /app/config 目录下，构建镜像时的jar包也在 /app 目录下
          volumeMounts:
            - mountPath: /app/config
              name: config
      imagePullSecrets:
        - name: docker-password
      volumes:
        - configMap:
        	# 指定我们创建的configMap的名字
            name: spring-boot-demo
          # 自定义的名字，需要跟 volumeMounts.name 匹配
          name: config

---
apiVersion: v1
kind: Service
metadata:
  name: spring-boot-demo
  namespace: default
  labels:
    app: spring-boot-demo
spec:
  ports:
    - name: port
      port: 80
      protocol: TCP
      targetPort: 8080
  selector:
    app: spring-boot-demo
  type: ClusterIP

```

3. 使用下面的命令创建挂载了配置的 deployment ：

```sh
kubectl apply -f spring-boot-demo.yaml
```

4. 使用下面的命令进入到容器中查看验证是否挂载到配置的目录：

```sh
# 查看pod
kubectl get pod -n default
# 进入容器
kubectl exec -it spring-boot-demo-76bd6c8857-kwss6  bash

```



## 五、☀️被挂载的 `configMap`内容会被自动更新

当卷中使用的 `configMap`被更新时，所投射的键最终也会被更新。 `kubelet` 组件会在每次周期性同步时检查所挂载的 `configMap`是否为最新。 不过，`kubelet` 使用的是其本地的高速缓存来获得 `configMap`的当前值。 高速缓存的类型可以通过 [KubeletConfiguration 结构](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubelet/config/v1beta1/types.go) 的 `ConfigMapAndSecretChangeDetectionStrategy` 字段来配置。

`configMap`既可以通过 watch 操作实现内容传播（默认形式），也可实现基于 TTL 的缓存，还可以直接经过所有请求重定向到 `API` 服务器。 因此，从 `configMap`被更新的那一刻算起，到新的主键被投射到 Pod 中去，这一 时间跨度可能与 `kubelet` 的同步周期加上高速缓存的传播延迟相等。 这里的传播延迟取决于所选的高速缓存类型 （分别对应 watch 操作的传播延迟、高速缓存的 TTL 时长或者 0）。

**以环境变量方式使用的 `configMap`数据不会被自动更新，更新这些数据需要重新启动 Pod。**





参考文档：

[k8s 官网](https://kubernetes.io/zh/docs/concepts/configuration/configmap/)

[spring boot 官网](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config.files)

