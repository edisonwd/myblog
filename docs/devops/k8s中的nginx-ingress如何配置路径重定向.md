# k8s中的nginx-ingress如何配置路径重定向

# 一. 需求描述
**路径重定向的一般应用场景：**

- 调整用户浏览的URL，看起来更规范
- 为了让搜索引擎收录网站内容，让用户体验更好
- 网站更换新域名后
- 根据特殊的变量、目录、客户端信息进行跳转

我这里遇到的问题是，以前的很多服务路径配置不规范，有的服务使用项目名作为二级路径，有的服务是随意定义的访问路径，为了统一使用项目名作为访问的二级路径，避免修改代码，所以需要配置路径重定向。

举一个例子，我有一个 `a 服务`，它原来的访问路径是 `api/v1/apps`，现在我需要通过路径 `a/api/v1/apps` 访问，需要将 `a/` 重定向到 `/`。

也就是 `www.test.com/a/api/v1/apps` 重定向到 `www.test.com/api/v1/apps` 。



# 二. 解决方法

需要确保在集群中有一个 `ingress controller` 正在运行。我们可以按照如下方式配置 `ingress` ：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
  name: rewrite
  namespace: default
spec:
  ingressClassName: nginx
  rules:
  - host: www.test.com
    http:
      paths:
      - path: /a(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: http-svc
            port: 
              number: 80
```

在这个 ingress 的定义中，通过在 `annotations` 中指定了 `nginx.ingress.kubernetes.io/rewrite-target: /$2` 来进行重定向，`(.*)` 捕获的任何字符都将被分配给占位符 `$2`，然后在 `rewrite-target` 中用作参数。

应用上面的 ingress 配置，可以实现下面的重定向：

- `www.test.com/a` 重定向到 `www.test.com/`
- `www.test.com/a/` 重定向到 `www.test.com/`
- `www.test.com/a/api/v1/apps` 重定向到 `www.test.com/api/v1/apps`



**`rewriting` 可以使用下面的 `anntations` 进行控制：**

| 名称                                             | 描述                                                       | 值     |
| ------------------------------------------------ | ---------------------------------------------------------- | ------ |
| `nginx.ingress.kubernetes.io/rewrite-target`     | 必须重定向流量的目标URI                                    | string |
| `nginx.ingress.kubernetes.io/ssl-redirect`       | 表示位置部分是否可访问SSL（当Ingress包含证书时默认为True） | bool   |
| `nginx.ingress.kubernetes.io/force-ssl-redirect` | 强制重定向到HTTPS，即使入口没有启用TLS                     | bool   |
| `nginx.ingress.kubernetes.io/app-root`           | 定义应用根，如果它在'/'上下文中，控制器必须重定向它        | string |
| `nginx.ingress.kubernetes.io/use-regex`          | 表示Ingress上定义的路径是否使用正则表达式                  | bool   |

**App Root**

创建一个带有 ``nginx.ingress.kubernetes.io/app-root`` 注解的 `ingress`，如下所示：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/app-root: /app1
  name: approot
  namespace: default
spec:
  ingressClassName: nginx
  rules:
  - host: approot.bar.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: http-svc
            port: 
              number: 80
```

检查 rewrite 是否起作用：

```sh
$ curl -I -k http://approot.bar.com/
HTTP/1.1 302 Moved Temporarily
Server: nginx/1.11.10
Date: Mon, 13 Mar 2017 14:57:15 GMT
Content-Type: text/html
Content-Length: 162
Location: http://approot.bar.com/app1
Connection: keep-alive
```







参考文档
https://github.com/kubernetes/ingress-nginx/blob/main/docs/examples/rewrite/README.md
https://www.cnblogs.com/brianzhu/p/8624703.html

