---
typora-copy-images-to: upload
typora-root-url: ./
---

# 使用 maven 自定义插件实现 devops

# 概述

最近在研究 `devops`，前面写了一篇文章介绍如何使用 `k8s + Gitlab + Jenkins + docker` 实现 `devops`，在文章中说明需要在项目中定义三个文件：

1. `Jenkinsfile` 文件：描述项目在 Jenkins 中的执行流程，包括打包以及推送镜像等
2. `Dockerfile` 文件：描述如何构建镜像
3. `deployment.yaml` 文件：描述`k8s` 的部署清单文件

对于 spring boot 项目来说，实现 `devops` 容器化部署时，这三个文件是差不多的，需要变化的是项目名以及端口号，所以可以将这三个文件提取成一个模板，通过自定义一个 maven 插件来根据项目中的配置自动生成对应的部署文件。接下来将详细描述整个实现过程。

本文将从以下几个方面进行介绍：

- **maven 插件开发介绍**
- **自定义实现 `devops` 插件**
- **推送自定义插件到 maven 仓库**

# maven 插件开发介绍

## 什么是插件？

“Maven” 实际上只是一个包含很多 Maven 核心插件的框架，换句话说，插件是 maven 执行大部分实际操作的地方，插件用于：**创建 jar 文件、创建 war 文件、编译代码、单元测试代码、创建项目文档等等**。几乎所有你能想到的对项目执行的操作都是作为 Maven 插件实现的。

插件是 Maven 的核心功能，允许跨多个项目重用公共构建逻辑。他们通过在项目描述的上下文 **项目对象模型 (POM)** 中执行 **操作**（即创建 WAR 文件或编译单元测试）来实现这一点。插件行为可以通过一组独特的参数进行定制，这些参数由每个插件目标（或 Mojo）的描述公开。

Maven 中最简单的插件之一是 `Clean Plugin`，它是负责清除 Maven 项目的目标（target）目录。当运行 `mvn clean` 时，Maven 会执行 Clean 插件中定义的 `clean` 目标，并删除目标（target）目录。

## 什么是 mojo?

maven 插件是由一个或多个 `mojo` 组成的，每个 `mojo` 是 maven 中的一个可执行目标。其实 `mojo` 这个名字和 `pojo` （`plain-old-java-object`） 类似，使用 `maven` 代替 `plain`，所以 `mojo`全称就是（`maven-old-java-object`）。

通过将插件的 `mojo` 绑定到 `maven` 生命周期阶段来完成特定的功能，比如执行 `mvn package` 各个生命周期阶段绑定的插件目标如下图：

![image-20210727164349983](https://gitee.com/peterwd/pic-oss/raw/master/image/202111051047059.png)

# 自定义实现 `devops` 插件

## 插件命名规范

第三方定义的插件命名为：`<yourplugin>-maven-plugin`

maven 官方的插件命名为：`maven-<yourplugin>-plugin`

> 这个和 spring boot starter 的命名规则类似
>
> spring 官方的组件命名为：`spring-boot-starter-xxx`
>
> 第三方开发的组件命名为：`xxx-spring-boot-starter`

遵循 maven 插件命名约定的好处是，如果你的插件的 `artifactId` 是 `maven-first-plugin`或者`first-maven-plugin`， 通过 Maven Plugin 插件生成插件描述符的时候，你不需要显式的为你的项目设定 `goalPrefix`，当执行`maven-plugin-plugin:3.2:descriptor`这个目标的时候，maven plugin 会从  `artifactId` 中抽取前缀 `first`。



## 创建一个 maven 插件项目

在一个插件项目的 `pom.xml` 中最重要的元素是打包类型，其值为 `maven-plugin`，即 `<packaging>maven-plugin</packaging>`，该打包类型会定制Maven的生命周期，使其包含创建插件描述符必要的目标。它和 Jar 生命周期类似，但有三个例外：

- `plugin:descriptor` 被绑定到 `generate-resources` 阶段，

- `plugin:addPluginArtifactMetadata` 被添加到 `package` 阶段，

- `plugin:updateRegistry` 被添加到 `install` 阶段。

插件项目的 `pom.xml` 中另一个重要的部分是，它有一个对于 `Maven Plugin API` 的依赖。



# 推送自定义插件到 maven 仓库







参考文档：

[maven 官网](https://maven.apache.org/guides/introduction/introduction-to-plugins.html)

[maven 中文指南](http://www.kailing.pub/PdfReader/web/viewer.html?file=mavenGuide)

