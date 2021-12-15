# devops工具zadig实践

# 一. 使用 helm 安装 zadig

> 官方文档：https://docs.koderover.com/zadig/install/overview/

创建 namespace：

```sh
kubectl create ns zadig
```

添加 zadig 官方 chart 仓库：

```sh
helm repo add koderover-chart https://koderover.tencentcloudcr.com/chartrepo/chart
```

更新 chart 仓库：

```sh
helm  repo update
```

在本地 chart 仓库中搜索 zadig：

```sh
helm search repo zadig
```

下载 chart 压缩文件到本地，便于自定义配置：

```sh
helm pull koderover-chart/zadig
```

解压下载的 chart 压缩文件：

```sh
tar -zxvf zadig-1.6.0.tgz
```

进入解压后的 zadig 目录，修改 `values.yaml` 文件：

```sh
vim zadig/values.yaml
```

根据需求修改完成配置后，使用下面的命令安装 zadig：

```sh
helm install -name zadig -n zadig ./zadig
```

使用下面的命令查看安装 zadig 的 pod：

```sh
k
```

