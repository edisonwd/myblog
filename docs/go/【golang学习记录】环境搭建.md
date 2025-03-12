# 【golang】环境搭建

# 一. 概述

本文是【golang学习记录】系列文章的第一篇，**安装Go语言及搭建Go语言开发环境**，接下来将详细记录自己学习 go 语言的过程，一方面是为了巩固自己学到的内容，另一方面希望对有同样需求的小伙伴提供一些帮助。



# 二. 下载并安装 Go

Go官网下载地址（在国内无法访问）：https://golang.org/dl/

**Go官方镜像站（推荐）**：https://golang.google.cn/dl/

> 在Windows中通过可执行文件来安装会自动配置 `GOROOT` 环境变量，省去了手动配置环境变量的麻烦，个人觉得通过下载 zip 包，配置环境变量安装能够更好理解安装流程。

我这里是在 windows 中安装 Go ，所以直接选择 windows 的安装方式即可，如下图所示：

![image-20211116143523053](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161435799.png)



下载完成后，双击下载好的文件，然后按照下图所示步骤安装：

![image-20211116144036899](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161440141.png)

如果你本地已经安装了低版本的 Go，那么点击 Next 后会提示你卸载旧版的 Go，根据提示卸载即可。



![image-20211116144438047](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161444292.png)



![image-20211116144547285](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161445469.png)

等待安装完成，出现下图，即表示安装成功：

![image-20211116145004279](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161450447.png)





因为通过可执行文件安装过程中已经自动配置好了环境变量，所以直接在 `CMD` 控制台输入 `go version` 命令验证 Go 是否安装成功：

```sh
> go version
go version go1.17.3 windows/amd64
```



# 三. Go 环境变量配置和说明

在 `CMD` 控制台输入 `go env` 命令查看配置的环境变量：

```sh
C:\Users\admin>go env
set GO111MODULE=on
set GOARCH=amd64
set GOBIN=
set GOCACHE=C:\Users\admin\AppData\Local\go-build
set GOENV=C:\Users\admin\AppData\Roaming\go\env
set GOEXE=.exe
set GOEXPERIMENT=
set GOFLAGS= -mod=
set GOHOSTARCH=amd64
set GOHOSTOS=windows
set GOINSECURE=
set GOMODCACHE=C:\Users\admin\go\pkg\mod
set GONOPROXY=
set GONOSUMDB=
set GOOS=windows
set GOPATH=C:\Users\admin\go
set GOPRIVATE=
set GOPROXY=https://goproxy.cn,direct
set GOROOT=D:\environment\Go
set GOSUMDB=sum.golang.org
set GOTMPDIR=
set GOTOOLDIR=D:\environment\Go\pkg\tool\windows_amd64
set GOVCS=
set GOVERSION=go1.17.3
set GCCGO=gccgo
set AR=ar
set CC=gcc
set CXX=g++
set CGO_ENABLED=1
set GOMOD=NUL
set CGO_CFLAGS=-g -O2
set CGO_CPPFLAGS=
set CGO_CXXFLAGS=-g -O2
set CGO_FFLAGS=-g -O2
set CGO_LDFLAGS=-g -O2
set PKG_CONFIG=pkg-config
set GOGCCFLAGS=-m64 -mthreads -fno-caret-diagnostics -Qunused-arguments -fmessage-length=0 -fdebug-prefix-map=C:\Users\admin\AppData\Local\Temp\go-build3769788971=/tmp/
go-build -gno-record-gcc-switches

```

> Go1.14版本之后，都推荐使用`go mod`模式来管理依赖环境了，也不再强制我们把代码必须写在`GOPATH`下面的src目录了，你可以在你电脑的任意位置编写go代码。

其中我们比较关心的环境变量有如下几个：

- `GOPATH`：可以理解为 go 的工作目录，此目录包含两个文件夹

  **-- bin**：存放 go 编译生成的可执行文件

  **-- pkg**：存放 go 项目依赖的第三方 module

- `GOROOT`：是我们安装 go 开发包的路径

- `GO111MODULE`：要启用`go module`支持首先要设置环境变量`GO111MODULE`，通过它可以开启或关闭模块支持，它有三个可选值：`off`、`on`、`auto`，默认值是`on`。

  1. `GO111MODULE=off`禁用模块支持，编译时会从`GOPATH`和`vendor`文件夹中查找包。
  2. `GO111MODULE=on`启用模块支持，编译时会忽略`GOPATH`和`vendor`文件夹，只根据 `go.mod`下载依赖。
  3. `GO111MODULE=auto`，当项目在`$GOPATH/src`外且项目根目录有`go.mod`文件时，开启模块支持。

  使用 go module 管理依赖后会在项目根目录下生成两个文件`go.mod`和`go.sum`。

- `GOPROXY`：Go1.13之后`GOPROXY`默认值为`https://proxy.golang.org`，在国内是无法访问的，所以十分建议大家设置`GOPROXY`，这里我推荐使用[goproxy.cn](https://studygolang.com/topics/10014)。通过如下命令设置：

  ```sh
  go env -w GOPROXY=https://goproxy.cn,direct
  ```

  

# 四. Go 开发工具

Go 采用的是 `UTF-8` 编码的文本文件存放源代码，理论上使用任何一款文本编辑器都可以做 Go 语言开发，比较常用的开发工具是 `VS Code`和`Goland`。 `VS Code`是微软开源的编辑器，而`Goland`是 jetbrains 出品的付费 IDE。

因为我是做的比较多的是 Java 开发，使用的是 idea，并且习惯了 idea 不想下载其他的开发工具，所以这里介绍在 idea 中安装 Go 插件进行开发。

打开 idea 在 Plugins 中搜索 go ，安装下图所示的插件：



![image-20211116170251306](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161702483.png)



安装完成后，最好是重启一下 idea，让插件生效。安装好插件之后，go 的开发工具其实就配置好了，



# 五. 第一个 Go 程序

现在我们来创建第一个Go项目——`hello-go`，在我们桌面创建一个`hello-go`目录。

使用 `go module` 模式新建项目时，我们需要通过 `go mod init 项目名` 命令对项目进行初始化，该命令会在项目根目录下生成 `go.mod` 文件。例如，我们使用`hello-go` 作为我们第一个Go项目的名称，在前面创建目录的 `cmd` 命令行中执行如下命令：

```sh
go mod init hello-go
```

查看生成的 `go.mod` 文件：

```sh
> cat go.mod
module hello-go

go 1.17
```

使用 idea 打开 `hello-go` 目录，idea 会提示你没有配置 `GOROOT`，我们根据提示，添加安装的 `GOROOT`路径即可。选择项目，右键新建一个 `Go File` 文件：

![image-20211116172302837](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161723138.png)



![image-20211116172405071](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161724293.png)

在 `main.go` 文件中输入如下内容：

```go
package main  // 声明 main 包，表明当前是一个可执行程序

import "fmt"  // 导入内置 fmt 包

func main(){  // main函数，是程序执行的入口
	fmt.Println("Hello World!")  // 在终端打印 Hello World!
}
```



![image-20211116172635327](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161726581.png)



在 idea 中的第一个 Go 程序就运行成功了~

在 `cmd` 终端中输入命令 `go run main.go`也可以执行程序，该命令本质上也是先编译再执行。

## 编译 Go 程序为可执行文件

`go build`命令表示将源代码编译成可执行文件。

在 idea 的终端中执行下面的命令，如下图所示：

![image-20211116173548406](https://gitee.com/peterwd/pic-oss/raw/master/image/202111161735563.png)



默认我们`go build`的可执行文件都是当前操作系统可执行的文件，它先编译源代码在当前目录生成可执行文件，所以我们可以在当前目录执行 `hello-go.exe`，如果我们希望在其他地方也可以执行，则需要使用 `go install` 命令。

`go install`表示安装的意思，它先编译源代码得到可执行文件，然后将可执行文件移动到`GOPATH`的 `bin` 目录下。因为我们的环境变量中配置了`GOPATH`下的 `bin` 目录，所以我们就可以在任意地方直接执行可执行文件了。





参考文档

https://www.liwenzhou.com/posts/Go/install_go_dev/

