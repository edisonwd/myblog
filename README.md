# myblog
记录一些学习笔记

# 前言

> 纸上得来终觉浅，绝知此事要躬行

在网上看到很多大佬的优秀博客，从他们的文章中学到了很多，特别是看到博主的自我介绍以及博文列表，不得不称赞“真的太优秀了”，想到了那句：比你优秀的人比你还努力，难免产生焦虑情绪，但是对于有积极心理的人，也许就不能称之为焦虑，而是打了一针鸡血。就目前对我来说还是比较积极的，依然对技术还保持着热情，所以心里默默对自己说：应该向这些优秀的大佬学习，养成写博客的习惯，将自己学习的知识记录下来。

说实话就个人而言并不擅长写文章，是那种高考作文都写不满 800 字的人，不期待自己能写出多么优秀的文章，只希望尽自己最大的努力将写的内容尽可能描述清楚。

# 使用过的开源工具

| 开源工具   | 描述                     | 官方文档                                         | 快速安装文档                                                 | 安装到k8s                                                    |
| ---------- | ------------------------ | ------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| kubernetes | 容器编排工具             | [k8s 官网](https://kubernetes.io/zh/docs/home/)  | [k8s 快速安装](https://www.kuboard.cn/install/install-k8s.html) |                                                              |
| gitlab     | 代码托管平台             | [gitlab 官网](https://about.gitlab.com/)         | [gitlab 快速安装](https://about.gitlab.com/install/)         |                                                              |
| nexus      | maven 仓库管理工具       | [nexus 官网](https://www.sonatype.com/)          | [nexus 快速安装](https://help.sonatype.com/repomanager3/download) | [在 k8s 中安装并使用 nexus](./在k8s中安装并使用nexus.md)     |
| jenkins    | devops持续集成工具       | [jenkins 官网](https://www.jenkins.io/)          | [jenkins 快速安装](https://www.jenkins.io/download/)         | [在 k8s 中安装并使用 jenkins](./在k8s中安装并使用jenkins.md) |
| kuboard    | k8s图形化管理工具        | [kuboard 官网](https://www.kuboard.cn/)          | [kuboard 快速安装](https://www.kuboard.cn/install/install-dashboard.html#安装) | [在 k8s 中安装 kuboard ](https://www.kuboard.cn/install/install-dashboard.html#安装) |
| torna      | 企业接口文档解决方案     | [torna 官网](http://torna.cn/)                   | [torna 快速安装](https://gitee.com/durcframework/torna#%E6%96%B9%E5%BC%8F2docker%E8%BF%90%E8%A1%8C) | [在 k8s 中安装 torna](https://gitee.com/durcframework/torna/tree/master/torna-on-kubernetes) |
| sornaqube  | 代码质量管理平台         | [sornaqube 官网](https://www.sonarqube.org/)     | [sornaqube 快速安装](https://www.sonarqube.org/downloads/)   |                                                              |
| skywalking | 分布式链路追踪与监控平台 | [skywaking 官网](https://skywalking.apache.org/) | [skywalking 快速安装](https://skywalking.apache.org/downloads/) |                                                              |
| kubeview   | k8s 资源可视化工具       | [kubeview 官网](http://kubeview.benco.io/)       | [kubeview 快速安装](https://github.com/benc-uk/kubeview)     |                                                              |
| apisix     | 云原生网关平台           | [apisix 官网](https://apisix.apache.org/)        | [apisix 快速安装](https://apisix.apache.org/downloads)       |                                                              |
| xxl-job    | 分布式任务调度平台       | [xxl-job 官网](https://www.xuxueli.com/xxl-job/) | [xxl-job 快速安装](https://www.xuxueli.com/xxl-job/)         |                                                              |



# 文章目录

[归并排序图文讲解](./归并排序图文讲解.md)

[阅读阿里Java开发手册记录](./阅读阿里Java开发手册记录.md)

[使用过的开源工具](./使用过的开源工具.md)

[在 markdown 中使用表情符号](./在markdown中使用表情符号.md)

[apisix 在k8s中的实践](./apisix在k8s中的实践.md)

[spring boot 使用 k8s 的 configMap 作为外部配置](./springboot使用k8s的configMap作为外部配置.md)

[在线阅读书籍汇总](./收集的学习资料/在线阅读书籍汇总.md)

[使用 maven 自定义插件实现 devops](./使用maven自定义插件实现devops.md)

[maven 基础知识汇总](./maven基础知识汇总.md)

[在 k8s 中安装并使用 nexus](./在k8s中安装并使用nexus.md)

[在 k8s 中安装并使用 jenkins](./在k8s中安装并使用jenkins.md)

[python使用正则表达式提取json字符串的值](python使用正则表达式提取json字符串的值.md)

[【爬虫】python+selenium+firefox使用与部署详解](./【爬虫】python+selenium+firefox使用与部署详解.md)

[【爬虫】docker部署python+selenium+firefox-headless](./【爬虫】docker部署python+selenium+firefox-headless.md)

[使用python问题总结](./使用python问题总结.md)

[java中如何实现线程间通信](./java中如何实现线程间通信.md)

[Java中获取ThreadDumps的8种方式汇总](./Java中获取ThreadDumps的8种方式汇总.md)

[是什么让Java应用程序的CPU使用率飙升](./是什么让Java应用程序的CPU使用率飙升.md)

[gunicorn超时报错](./gunicorn超时报错.md)

[selenium如何拖动滚动条](./selenium如何拖动滚动条.md)

[Java异常](./Java异常.md)

[devops工具zadig实践](./devops工具zadig实践.md)

[【golang学习记录】环境搭建](./【golang学习记录】环境搭建.md)

[【golang】使用chan收集多协程执行的结果](./【golang】使用chan收集多协程执行的结果.md)

[go语言grpc框架从入门到实践](./go语言grpc框架从入门到实践.md)

[k8s中的nginx-ingress如何配置路径重定向](./k8s中的nginx-ingress如何配置路径重定向.md)

[python实现掘金定时签到抽奖](./python实现掘金定时签到抽奖.md)

[Java和go语言实现LRU算法](./Java和go语言实现LRU算法.md)

[使用Awescnb构建酷炫的博客园皮肤](./使用Awescnb构建酷炫的博客园皮肤.md)

# 收藏的博客

| 博客地址                                 | 添加时间  | 简单说明                                                     |
| ---------------------------------------- | --------- | ------------------------------------------------------------ |
| [面包的博客](https://www.himself65.com/) | 2021.9.18 | 作者是爱荷华州立大学计算机科学本科学生，作者的经历很励志，文章写的很好 |
| [二丫讲梵](https://wiki.eryajf.net/)     | 2021.9.18 | 运维相关的内容，还有很多优秀的个人记录，挺喜欢看他的周刊，能了解到很多有意思的内容 |
|                                          |           |                                                              |

