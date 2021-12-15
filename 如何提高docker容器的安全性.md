# 一. 概述
Docker 容器一直是开发人员工具箱的重要组成部分，使开发人员能够以标准化的方式构建、分发和部署他们的应用程序。毫无疑问，这种吸引力的增加伴随着容器化技术的相关**安全问题**。他们可以很容易地利用[错误配置](https://blog.gitguardian.com/hunting-for-secrets-in-docker-hub/)**从容器内逃逸到主机**。


此外，“容器”这个词经常被误解，因为许多开发人员倾向于将**隔离的概念与错误的安全感联系起来**，认为这项技术本质上是安全的。

实际上容器**默认没有任何安全维度**，它们的安全性完全取决于：

-   支持的基础设施（操作系统和平台）
-   它们的嵌入式软件组件
-   它们的运行时配置


容器安全是一个广泛的话题，但好消息是，有许多最佳实践是唾手可得的，可以**快速减少**其部署**的攻击面**。

**下图是 docker 安全备忘清单**，[点击下载清晰图片](https://res.cloudinary.com/da8kiytlc/image/upload/v1627655008/Cheatsheets/Docker-Security-Cheatsheet_hp8lh3.pdf)

![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9688a44816a946b7975349ba1f73ecd6~tplv-k3u1fbpfcp-watermark.image)

> *注意：在像 Kubernetes 这样的托管环境中，大多数这些设置都可以被安全上下文或其他更高级别的安全规则覆盖。* [*查看更多*](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

下面主要从四个方面介绍如何构建安全的 docker 镜像：

- 构建配置
- 文件系统
- 联网
- 日志记录

# 二. 构建配置

## 1. 谨慎选择基础镜像

谨慎选择你的基础镜像 `docker pull image:tag`
你应该始终使用**受信任的镜像**，最好来自[Docker 官方镜像](https://docs.docker.com/docker-hub/official_repos/)，以减轻供应链攻击。
如果你需要选择基本发行版的基础镜像，[建议使用 Alpine Linux，](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) 因为它是可用的最轻量级发行版之一，可确保减少攻击面。

**我需要使用最新的还是固定的标签版本？**

首先，你需要了解 docker 标签从较少到具体的含义，如下 python 镜像标签：

```
python:3.9.6-alpine3.14

python:3.9.6-alpine

python:3.9-alpine

python:alpine
```

上面所有的标签都是指向相同的镜像，选择具体的镜像标签可以保护自己免受未来任何重大更改的影响，另一方面，使用最新版本可确保修补更多漏洞。**这是一种权衡**，但通常**建议固定到稳定版本**。考虑到这一点，我们这里会选择 `python:3.9-alpine`。

> 注意：这同样适用于在镜像构建过程中安装的包。

## 2. 始终使用非特权用户

默认情况下，容器内的进程**以 root(id=0)身份运行**。

为了执行最小权限原则，你应该设置一个默认用户。为此，你有两个选择：

- 使用以下选项指定运行容器中不存在的任意用户 ID `-u`：
  `docker run -u 4000 <image>`

> 注意：如果你以后需要挂载文件系统，你应该将你使用的用户 ID 与主机用户匹配，以便访问文件。

- 或者通过在 `Dockerfile` 中创建默认用户：

```
FROM <base image>

RUN addgroup -S appgroup \
 && adduser -S appuser -G appgroup
 
USER appuser

... <rest of Dockerfile> ...
```

> 注意：你需要在基础镜像中中检查创建用户和组的工具。

## 3. 使用单独的用户 ID 命名空间

默认情况下，Docker 守护进程使用主机的用户 ID 命名空间。因此，容器内权限提升也意味着对主机和其他容器的 root 访问。
为了降低这种风险，你应该将主机和 Docker 守护程序配置为使用带有该 `--userns-remap` 选项的单独命名空间。[查看更多](https://docs.docker.com/engine/security/userns-remap/#prerequisites)

## 4. 小心处理环境变量

你**永远不应该在 `ENV` 指令中以明文形式**包含敏感信息：它们根本不是一个安全的地方来存储你不想出现在最后一层的任何信息。例如，如果你认为像这样取消设置环境变量：

```
ENV $VAR
RUN unset $VAR
```

是安全的，你错了！`$VAR`仍将存在于容器中，并且可以随时查看！

为了防止运行时读取访问，请使用单个 RUN 命令在单个层中设置和取消设置变量（不要忘记变量**仍然可以**从镜像中**提取**）。

```
RUN export ADMIN_USER="admin" \
    && ... \
    && unset ADMIN_USER
```

更惯用的是，**使用 ARG 指令**（构建镜像后 ARG 值不可用）。

不幸的是，**secret 经常被硬编码到 docker 镜像的层中**，这就是我们开发利用 `GitGuardian` secret引擎来查找它们的[扫描工具](https://github.com/GitGuardian/ggshield)的原因：

```
ggshield scan docker <image>
```

稍后将详细介绍扫描镜像中的漏洞。

## 5. 不要暴露 Docker 守护进程套接字

除非你对自己正在做的事情非常有信心，否则永远不要暴露 Docker 正在侦听的 UNIX 套接字： `/var/run/docker.sock`

这是 Docker API 的主要入口点。授予某人访问权限等同于授予对你的主机的无限制 root 访问权限。
你永远不应该将它暴露给其他容器：

```
-v /var/run/docker.sock://var/run/docker.sock
```

## 6. 特权、能力和共享资源

首先，你的容器不应该**以特权身份运行**，否则，它将被允许在主机上拥有所有 root 权限。
为了更安全，建议明确禁止在使用选项创建容器后添加新权限的可能性`--security-opt=no-new-privileges`。

其次，**capabilities**是 Docker 使用的一种 Linux 机制，用于将二进制  `root/non-root` 二分法转变为细粒度的访问控制系统：你的容器使用一组默认启用的功能运行，而你很可能没有都需要。

建议**删除所有默认功能**并仅单独添加它们：
例如，请参阅默认功能列表，Web 服务器可能只需要 NET_BIND_SERVICE 绑定到 1024 下的端口（如端口 80）。

第三，**不要共享**主机文件系统**的敏感部分**：

- 根 （/），
- 设备 (/dev)
- 进程 (/proc)
- 虚拟 (/sys) 挂载点。

如果你需要访问主机设备，请小心使用`[r|w|m]`标志（读、写和使用 mknod）有选择地启用访问选项。

## 7. 使用Control Groups限制对资源的访问

`Control Groups(cgroups)` 是用于控制每个容器对 CPU、内存、磁盘 I/O 的访问的机制。
默认情况下，容器与`cgroup`关联，但如果`--cgroup-parent`存在该选项，则会将主机资源置于**DoS 攻击的风险中**，因为你允许主机和容器之间共享资源。

出于同样的想法，建议使用以下选项指定内存和 CPU 使用率

```
--memory=”400m”
--memory-swap=”1g”

--cpus=0.5
--restart=on-failure:5
--ulimit nofile=5
--ulimit nproc=5
```

[查看有关资源限制的更多信息](https://docs.docker.com/config/containers/resource_constraints/)

# 三. 文件系统

## 1. 只允许读访问根文件系统

容器应该是短暂的，因此大多是无状态的。这就是为什么你通常可以将挂载的文件系统限制为只读的原因。
`docker run --read-only <image>`

## 2. 对非持久性数据使用临时文件系统

如果你只需要临时存储，请使用适当的选项
`docker run --read-only --tmpfs /tmp:rw ,noexec,nosuid <image>`

## 3. 使用文件系统保存持久数据

如果你需要与主机文件系统或其他容器共享数据，你有两种选择：

- 创建具有有限可用磁盘空间的绑定挂载 ( `--mount type=bind,o=size`)
- 为专用分区创建绑定卷 ( `--mount type=volume`)
  在任何一种情况下，如果容器不需要修改共享数据，请使用只读选项。

```
docker run -v <volume-name>:/path/in/container:ro <image>`
或者
`docker run --mount source=<volume-name>,destination=/path/in/container,readonly <image>
```

# 四. 联网

## 1. 不要使用 Docker 的默认网桥 docker0

`docker0`是在启动时创建的网桥，用于将主机网络与容器网络分开。
创建容器时，Docker 的`docker0`默认将其连接到网络，因此所有容器都相互连接`docker0`并能够相互通信。
你应该通过指定选项 `--bridge=none` 禁用所有容器的默认连接，并使用以下命令**为每个连接创建一个专用网络**：

```
docker network create <network_name>
```

然后用它来访问主机网络接口

```
docker run --network=<network_name>
```

![Docker联网简单例子](https://blog.gitguardian.com/content/images/2021/07/Docker-networking.png)Docker联网简单例子

例如，要创建一个与数据库通信的 Web 服务器（在另一个容器中启动），最佳实践是创建一个桥接网络`WEB`以路由来自主机网络接口的传入流量，并使用另一个`DB`仅用于连接数据库的桥接器和网络容器。

## 2. 不要共享主机的网络命名空间

同样的想法，隔离主机的网络接口：`--network`不应使用主机选项。

# 五. 日志记录

默认日志级别为 INFO，但你可以使用以下选项指定另一个级别：
`--log-level="debug"|"info"|"warn"|"error"|"fatal"`

鲜为人知的是 Docker 的日志导出能力：如果你的容器化应用程序生成事件日志，你可以使用选项重定向`STDERR`和`STDOUT`流到外部日志服务以进行解耦`--log-driver=<logging_driver>`

你还可以启用双日志记录以在使用外部服务时保留 docker 对日志的访问。如果你的应用程序使用专用文件（通常写在 下 `/var/log`），你仍然可以重定向这些流：[请参阅官方文档](https://docs.docker.com/config/containers/logging/configure/)

# 六. 扫描漏洞和秘密

最后但并非最不重要的一点是，我希望现在你的容器将与它们运行的软件一样安全。为确保你的镜像没有漏洞，你需要对已知漏洞执行扫描。
许多工具可用于不同的用例和不同的形式：

漏洞扫描：

- 免费选项：
  - [Clair](https://github.com/quay/clair)
  - [Trivy](https://github.com/aquasecurity/trivy)
  - [Docker Bench for Security](https://github.com/docker/docker-bench-security)
- 商业的：
  - [Snyk](https://github.com/snyk/snyk) (open source and free option available)
  - [Anchore](https://github.com/anchore/anchore-engine) (open source and free option available)
  - [JFrog XRay](https://jfrog.com/fr/xray/)
  - [Qualys](https://qualysguard.qg2.apps.qualys.com/cs/help/vuln_scans/docker_images.htm)

secret 扫描：

- [ggshield](https://github.com/GitGuardian/ggshield) (open source and free option available)
- [SecretScanner](https://github.com/deepfence/SecretScanner) (free)

- https://blog.gitguardian.com/rewriting-git-history-cheatsheet/)

