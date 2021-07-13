# apisix 在k8s中的实践

## 一. 概述

最近在使用一个国产的云原生 API 网关（[apisix](https://apisix.apache.org/)）,功能非常强大，本文根据官方文档在 `minikube` 中进行实践，官方文档写的很详细，详情可以查看官网。

> apisix 官网：https://apisix.apache.org/

## 二. 在 k8s 中安装 ingress apisix

### 1. 环境准备

- 安装 [Minikube](https://minikube.sigs.k8s.io/docs/start/).

- 安装 [Helm](https://helm.sh/).

- 使用下面的命令创建一个命名空间 `ingress-apisix`

  ```sh
  kubectl create namespace ingress-apisix
  ```

- 使用下面的命令添加安装 apisix 的 helm 仓库

  ```sh
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo add apisix https://charts.apiseven.com
  ```

- 使用下面的命令更新 helm 仓库

  ```sh
  helm repo update
  ```

- 使用下面的命令在 helm 仓库中搜索 apisix，验证在本地仓库是否存在

  ```sh
  [root@node01 ~]# helm search repo apisix
  NAME                            	CHART VERSION	APP VERSION	DESCRIPTION                                    
  apisix/apisix                   	0.3.4        	2.6.0      	A Helm chart for Apache APISIX                 
  apisix/apisix-dashboard         	0.1.4        	2.6.0      	A Helm chart for Apache APISIX Dashboard       
  apisix/apisix-ingress-controller	0.5.0        	1.0.0      	Apache APISIX Ingress Controller for Kubernetes
  
  ```

  

### 2. 安装 apisix

[Apache APISIX](http://apisix.apache.org/) 作为 `apisix-ingress-controller` 的代理平面，所以需要提前部署。

使用下面的命令按照 `apisix`：

```sh
helm install apisix apisix/apisix \
  --set admin.allow.ipList="{0.0.0.0/0}" \
  --namespace ingress-apisix
```

需要注意的一点是，这里为了快速测试设置`admin.allow.ipList="{0.0.0.0/0}"`表示允许所有的 IP 访问 `Apache APISIX admin api` ，该字段应该根据 k8s 的 `PodCIDR`(pod的网段) 配置进行自定义。

可以使用下面的命令查看 `podCIRD`：

```sh
kubectl get node node01  -o yaml |grep podCIDR
```

安装 `apisix` 成功之后可以使用下面的命令查看创建的 service 资源：

```sh
kubectl get service --namespace ingress-apisix
```

可以看到创建了两个Service资源：

- 一个是`apisix-gateway`，处理接收的真实流量；
- 另一个是`apisix-admin`，它充当控制平面来处理所有配置更改。



### 3. 安装 apisix-ingress-controller

`apisix-ingress-controller` 是 `Kubernetes` 的另一个入口控制器，使用 `apisix` 作为高性能反向代理。它是通过使用诸如 [ApisixRoute](https://apisix.apache.org/docs/ingress-controller/concepts/apisix_route)、[ApisixUpstream](https://apisix.apache.org/docs/ingress-controller/concepts/apisix_upstream)、[Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) 等声明性配置来配置的，所有这些资源都被监视并转换为 apisix 中的相应资源。

这里使用 helm 安装 `apisix-ingress-controller`，使用下面的命令将其安装在与 `apisix` 相同的命名空间中：

```sh
helm install apisix-ingress-controller apisix/apisix-ingress-controller \
  --set image.tag=dev \
  --set config.apisix.baseURL=http://apisix-admin:9180/apisix/admin \
  --set config.apisix.adminKey=edd1c9f034335f136f87ad84b625c8f1 \
  --namespace ingress-apisix
```



### 4. 安装 apisix-dashboard

`apache apisix` 提供了一个控制台，让我们操作 apisix 更加容易，这里使用 helm 安装 `apisix-dashboard`，使用下面的命令将其安装在与 `apisix` 相同的命名空间中：

```sh
 helm install apisix-dashboard apisix/apisix-dashboard \
 --set service.type=NodePort \
 --namespace ingress-apisix
```

使用下面的命令查看 `ingress-apisix` 命令空间中的 service 资源：

```sh
[root@node01 ~]# kubectl get svc -n ingress-apisix 
NAME                        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
apisix-admin                ClusterIP   10.10.7.102    <none>        9180/TCP            9h
apisix-dashboard            ClusterIP   10.10.7.14     <none>        80/TCP              8h
apisix-etcd                 ClusterIP   10.10.4.180    <none>        2379/TCP,2380/TCP   9h
apisix-etcd-headless        ClusterIP   None           <none>        2379/TCP,2380/TCP   9h
apisix-gateway              NodePort    10.10.7.31     <none>        80:31124/TCP        9h
apisix-ingress-controller   ClusterIP   10.10.14.242   <none>        80/TCP              8h

```

修改 `apisix-dashboard ` 的 type 类型为 NodePort ，以便外部访问：

```sh
kubectl edit svc  apisix-dashboard -n ingress-apisix
```



curl 'http://127.0.0.1:10080/wolf/oauth2/token' 
-H "Content-Type: application/x-www-form-urlencoded" 
-X POST 
-d "grant_type=password&client_id=test&client_secret=yghS6isJ3PtPBz2pr8v8XN7OmR5QbuYNNuraDDgs&username=admin&password=123456"

