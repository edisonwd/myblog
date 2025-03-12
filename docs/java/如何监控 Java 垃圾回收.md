

# 如何监控 Java 垃圾回收

这是成为 Java GC 专家系列的第二篇文章，我们了解了不同 GC 算法的流程，GC 是如何工作的，什么是年轻代和老年代，你应该了解的 JDK 7 中的 5 种类型的 GC：

1. Serial GC
2. Parallel GC
3. Parallel Old GC (Parallel Compacting GC)
4. Concurrent Mark & Sweep GC  (or "CMS")
5. Garbage First (G1) GC

在本文中，我将介绍 **JVM 如何实时监控运行的垃圾收集**。

## 什么是 GC 监控？ 

**GC 监控** 是指弄清楚 JVM 如何运行 GC 的过程。例如，我们可以发现，stop-the-world 何时发生以及持续多长时间。

执行 GC 监控 **以查看 JVM 是否有效地运行 GC*，并*检查是否需要额外的调整 GC** 。根据此信息，可以编辑应用程序或更改 GC 方法（**GC 调整**）。

## 如何监控GC？

监控 GC 的方式有很多种，但唯一的区别是 GC 操作信息的显示方式。GC 是由 JVM 来完成的，由于 GC 监控工具会公开 JVM 提供的 GC 信息，所以无论你如何监控 GC 都会得到相同的结果，因此不需要学习所有的GC监控方法，但是由于学习每种GC监控方法只需要很少的时间，了解其中的几种可以帮助我们针对不同的情况和环境使用正确的方法。

首先，GC 监控方法可以根据访问接口分为 **CUI** 和 **GUI**：

CUI GC 监控方法有 **jstat** 的单独 CUI 应用程序，或在运行 JVM 时选择名为 **verbosegc** 的 JVM 选项。

GUI GC 监控是通过使用单独的 GUI 应用程序完成的，三个最常用的应用程序是 **jconsole**、**jvisualvm** 和 **Visual GC**。

让我们详细了解每种方法。

## jstat

**jstat **是 HotSpot JVM 中的一个监控工具，HotSpot JVM 的其他监控工具是 **jps** 和 **jstatd**，有时，需要所有三种工具来监视 Java 应用程序。

**jstat** 不只提供 GC 操作信息显示，它还提供类加载器操作信息或 **Just-in-Time** 编译器操作信息，在本文中我们将只介绍其*监控*GC 运行信息的功能。

**jstat** 位于`$JDK_HOME/bin`，如果我们配置好了 JDK 的环境变量，那么 jstat 也可以直接命令行运行。

在命令行中运行以下命令：

```sh
>jstat
invalid argument count
Usage: jstat -help|-options
       jstat -<option> [-t] [-h<lines>] <vmid> [<interval> [<count>]]

Definitions:
  <option>      An option reported by the -options option
  <vmid>        Virtual Machine Identifier. A vmid takes the following form:
                     <lvmid>[@<hostname>[:<port>]]
                Where <lvmid> is the local vm identifier for the target
                Java virtual machine, typically a process id; <hostname> is
                the name of the host running the target Java virtual machine;
                and <port> is the port number for the rmiregistry on the
                target host. See the jvmstat documentation for a more complete
                description of the Virtual Machine Identifier.
  <lines>       Number of samples between header lines.
  <interval>    Sampling interval. The following forms are allowed:
                    <n>["ms"|"s"]
                Where <n> is an integer and the suffix specifies the units as
                milliseconds("ms") or seconds("s"). The default units are "ms".
  <count>       Number of samples to take before terminating.
  -J<flag>      Pass <flag> directly to the runtime system.
```

**vmid**（Virtual Machine ID），顾名思义，就是VM的**ID**，可以使用 vmid 指定在本地机器或远程机器上运行的 Java 应用程序。运行在本地机器上的Java应用程序的 vmid 称为 **lvmid**（Local vmid），**通常是PID**。要找出 lvmid，您可以使用**ps**命令或 Windows 任务管理器写入 PID 值，但我们建议使用 **jps，**因为 PID 和 lvmid 并不总是匹配。**jps**代表 Java 进程，jps 显示 *vmids* 和主要方法信息，就像 ps 显示 PID 和进程名称一样。

使用 jps 找出你要监控的 Java 应用的 vmid，然后在 jstat 中作为参数使用。如果单独使用 jps，当多个 WAS 实例在一台设备上运行时，只会显示引导程序信息。我们建议您使用 `ps -ef | grep java` 命令以及**jps**。

GC性能数据需要不断观察，因此在运行jstat时，尽量定期输出GC监控信息。 

- `jstat –gc <vmid> 1000`（或1s）将每隔1秒在控制台上显示一次GC监控数据。
- `jstat –gc <vmid> 1000 10` 每1秒显示一次GC监控信息，共显示10次。

**jstat**  除了 **-gc **之外还有很多选项，下面列出了其中与 GC 相关的选项。

| 选项名称       | 描述                                                         |
| -------------- | ------------------------------------------------------------ |
| GC             | 它显示了每个堆区域的当前大小及其当前使用情况（Ede、survivor、old 等）、执行的 GC 总数以及 GC 操作的累计时间。 |
| gccapactiy     | 它显示了每个堆区域的最小大小 (ms) 和最大大小 (mx)、当前大小以及每个区域执行的 GC 次数（不显示 GC 操作的当前使用情况和累计时间。） |
| gccause        | 它显示了“-gcutil 提供的信息”+ 上次 GC 的原因和当前 GC 的原因。 |
| gcnew          | 显示新区域的 GC 性能数据。                                   |
| gcnewcapacity  | 显示新区域大小的统计信息。                                   |
| gcold          | 显示旧区域的 GC 性能数据。                                   |
| gcoldcapacity  | 显示旧区域大小的统计信息。                                   |
| gcpermcapacity | 显示永久区域的统计数据。                                     |
| gcutil         | 以百分比显示每个堆区域的使用情况，还显示执行的 GC 总数和 GC 操作的累计时间。 |

仅查看频率，您可能会按该顺序最多使用 **-gcutil**（或 -gccause），**-gc**和 **-gccapacity**。

- **-gcutil** 用于检查堆区域的使用情况、执行的 GC 次数以及 GC 操作的总累计时间，
- **-gccapacity** 选项和其他选项可用于检查分配的实际大小。

您可以使用**-gc**选项查看以下输出：

```
>jstat  -gc 15076 1000 3
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
33280.0 31744.0  0.0   22891.1 652800.0 250844.6  216064.0   51610.3   70528.0 66272.3 9088.0 8293.1     17    0.247   3      0.297    0.543
33280.0 31744.0  0.0   22891.1 652800.0 250844.6  216064.0   51610.3   70528.0 66272.3 9088.0 8293.1     17    0.247   3      0.297    0.543
33280.0 31744.0  0.0   22891.1 652800.0 250844.6  216064.0   51610.3   70528.0 66272.3 9088.0 8293.1     17    0.247   3      0.297    0.543
```

不同的 jstat 选项显示不同类型的列，如下所列。当您使用前面列出的 **jstat 选项** 时，将显示每列信息。

| 列    | 描述                                                         | Jstat 选项                                                   |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| S0C   | 以 KB 为单位显示 Survivor0 区域的当前大小                    | -gc -gccapacity -gcnew -gcnewcapacity                        |
| S1C   | 以 KB 为单位显示 Survivor1 区域的当前大小                    | -gc -gccapacity -gcnew -gcnewcapacity                        |
| S0U   | 以 KB 为单位显示 Survivor0 区域的当前使用情况                | -gc -gcnew                                                   |
| S1U   | 以 KB 为单位显示 Survivor1 区域的当前使用情况                | -gc -gcnew                                                   |
| EC    | 以 KB 为单位显示 Eden 区域的当前大小                         | -gc -gccapacity -gcnew -gcnewcapacity                        |
| EU    | 以 KB 为单位显示 Eden 区域的当前使用情况                     | -gc -gcnew                                                   |
| OC    | 以 KB 为单位显示旧区域的当前大小                             | -gc -gccapacity -gcold -gcoldcapacity                        |
| OU    | 以KB为单位显示旧区的当前使用情况                             | -gc -gcold                                                   |
| PC    | 以 KB 为单位显示永久区域的当前大小                           | -gc -gccapacity -gcold -gcoldcapacity -gcpermcapacity        |
| PU    | 以KB为单位显示永久区域的当前使用情况                         | -gc -gcold                                                   |
| YGC   | 年轻区GC事件发生次数                                         | -gc -gccapacity -gcnew -gcnewcapacity -gcold -gcoldcapacity -gcpermcapacity -gcutil -gccause |
| YGCT  | 永区GC操作累计时间                                           | -gc -gcnew -gcutil -gccause                                  |
| FGC   | full GC 事件发生的次数                                       | -gc -gccapacity -gcnew -gcnewcapacity -gcold -gcoldcapacity -gcpermcapacity -gcutil -gccause |
| FGCT  | full GC 操作的累计时间                                       | -gc -gcold -gcoldcapacity -gcpermcapacity -gcutil -gccause   |
| GCT   | GC 操作的总累计时间                                          | -gc -gcold -gcoldcapacity -gcpermcapacity -gcutil -gccause   |
| NGCMN | 新区的最小大小 (KB)                                          | -gccapacity -gcnewcapacity                                   |
| NGCMX | max area 的最大大小 (KB)                                     | -gccapacity -gcnewcapacity                                   |
| NGC   | 新区的当前大小 (KB)                                          | -gccapacity -gcnewcapacity                                   |
| OGCMN | 旧区的最小大小（KB）                                         | -gccapacity -gcoldcapacity                                   |
| OGCMX | 旧区的最大大小（KB）                                         | -gccapacity -gcoldcapacity                                   |
| OGC   | 旧区的当前大小 (KB)                                          | -gccapacity -gcoldcapacity                                   |
| PGCMN | 永久区域的最小大小 (KB)                                      | -gccapacity -gcpermcapacity                                  |
| PGCMX | 永久区域的最大大小 (KB)                                      | -gccapacity -gcpermcapacity                                  |
| PGC   | 永久代区的当前大小 (KB)                                      | -gccapacity -gcpermcapacity                                  |
| LGCC  | 上次 GC 发生的原因                                           | -gccause                                                     |
| TT    | 任期门槛。如果在年轻区域（S0 -> S1，S1-> S0）中复制了这个次数，则它们将被移动到旧区域。 | -gcnew                                                       |
| MTT   | 最大任期阈值。如果在年轻区域内复制了这么多次，那么它们将被移动到旧区域。 | -gcnew                                                       |
| DSS   | 以 KB 为单位的足够大小的幸存者                               | -gcnew                                                       |

**jstat**的优点是可以随时监控本地/远程机器上运行的Java应用的GC运行数据，只要使用控制台即可。从这些项目中，使用**-gcutil**时输出以下结果。在GC调优的时候，要特别注意**YGC、YGCT、FGC、FGCT**和**GCT**。

```
>jstat  -gcutil 15076 1000 3
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
  0.00  72.11  39.82  23.89  93.97  91.25     17    0.247     3    0.297    0.543
  0.00  72.11  39.82  23.89  93.97  91.25     17    0.247     3    0.297    0.543
  0.00  72.11  39.99  23.89  93.97  91.25     17    0.247     3    0.297    0.543
```

这些项目很重要，因为它们显示了运行 GC 花费了多少时间。

## -verbosegc

**-verbosegc** 是运行 Java 应用程序时指定的 JVM 选项之一。虽然 **jstat** 可以监控任何没有指定任何选项的 JVM 应用程序，但**-verbosegc**需要在开始时指定，因此它可以被视为一个不必要的选项（因为可以使用 jstat 代替）。但是，由于**-verbosegc**在发生 GC 时显示易于理解的输出结果，因此对于监视粗略的 GC 信息非常有帮助。

|                    | 统计数据                                                     | -verbosegc                                    |
| ------------------ | ------------------------------------------------------------ | --------------------------------------------- |
| Monitoring Target  | 在可以登录终端的机器上运行的 Java 应用程序，或者可以使用 jstatd 连接到网络的远程 Java 应用程序 | 仅当 -verbosegc 被指定为 JVM 启动选项时       |
| Output information | 堆状态（使用情况、最大大小、GC 次数/时间等）                 | GC 前后 new 和 old 区的大小，以及 GC 运行时间 |
| Output Time        | 每个指定时间                                                 | 每次 GC 发生的时间                            |
| Whenever useful    | 尝试观察堆区域大小的变化时                                   | 查看单个 GC 的效果                            |

以下是可与**-verbosegc**一起使用的其他选项。

- -XX:+PrintGCDetails
- -XX:+PrintGCTimeStamps
- -XX:+PrintHeapAtGC 
- -XX:+PrintGCDateStamps（来自 JDK 6 更新 4）

如果仅**使用 -verbosegc**，则默认应用**-XX:+PrintGCDetails**。**–verbosgc** 附加选项不是唯一的，可以混合使用。

使用 **-verbosegc** 时，只要发生 **minor GC**，就可以看到以下格式的结果。

```
[GC [<collector>: <starting occupancy1> -> <ending occupancy1>, <pause time1> secs] <starting occupancy3> -> <ending occupancy3>, <pause time3> secs]
```

| Collector           | 用于次要 gc 的收集器名称                           |
| ------------------- | -------------------------------------------------- |
| starting occupancy1 | GC前年轻区域的大小                                 |
| ending occupancy1   | GC后年轻区域的大小                                 |
| pause time1         | Java 应用程序停止运行以进行次要 GC 的时间          |
| starting occupancy3 | GC前堆区总大小                                     |
| ending occupancy3   | GC后堆区总大小                                     |
| pause time3         | Java 应用程序停止运行整个堆 GC 的时间，包括主要 GC |

这是**Full GC**的 **-verbosegc** 输出示例：

```
[Full GC [Tenured: 3485K->4095K(4096K), 0.1745373 secs] 61244K->7418K(63104K), [Perm : 10756K->10756K(12288K)], 0.1762129 secs] [Times: user=0.19 sys=0.00, real=0.19 secs]
```

由于**-verbosegc**选项在每次发生 GC 事件时都会输出日志，因此很容易看到 GC 操作导致的堆使用率的变化。

## (Java) VisualVM + Visual GC

Java Visual VM 是 Oracle JDK 提供的 GUI 分析/监控工具。

![图 1：VisualVM 屏幕截图。](https://www.cubrid.org/layouts/layout_master/img/e387fd9fbccb654f3d8db696fb215403.png)

**图 1：VisualVM 屏幕截图。**

可以直接从其网站下载 Visual VM，而不是 JDK 附带的版本。为方便起见，JDK附带的版本将被称为Java VisualVM（jvisualvm），网站提供的版本将被称为Visual VM（visualvm）。两者的功能并不完全相同，因为存在细微差别，例如在安装插件时。我个人更喜欢 Visual VM 版本，可以从网站下载。

运行 Visual VM 后，如果从左侧窗口中选择要监控的应用程序，可以在那里找到“*监控*”选项卡。您可以从此监控选项卡中获取有关 GC 和 Heap 的基本信息。 

虽然基本 GC 状态也可通过 VisualVM 的基本功能获得，但您无法访问 **jstat** 或 **-verbosegc** 选项提供的详细信息。 

如果想要jstat提供的详细信息，那么建议安装Visual GC插件。 

可以从“*工具”*菜单实时访问 Visual GC 。

![图 2：Viusal GC 安装屏幕截图。](https://www.cubrid.org/layouts/layout_master/img/28c621040950b1010adca98e19baad62.png)

**图 2：Viusal GC 安装屏幕截图。**

通过使用 Visual GC，您可以更直观地看到运行**jstatd**提供的信息。  

![图 3：Visual GC 执行截图。](https://www.cubrid.org/layouts/layout_master/img/1b37381a6b243d19cc73843dd134b86e.png)

**图 3：Visual GC 执行截图。**

## HPJMeter

[HPJMeter](https://h20392.www2.hp.com/portal/swdepot/displayProductInfo.do?productNumber=HPJMETER)便于分析**-verbosegc**输出结果。如果可以将 Visual GC 视为 **jstat** 的 GUI 等价物，那么 HPJMeter 将是 **-verbosgc** 的 GUI 等价*物*。当然，GC 分析只是 HPJMeter 提供的众多功能之一。HPJMeter 是 HP 开发的性能监控工具，它可以在 HP-UX 以及 Linux 和 MS Windows 中使用。

最初，一个名为**HPTune**的工具用于为**-verbosegc**提供 GUI 分析功能。但是，由于 HPJMeter 从 3.0 版本开始已经集成了 HPTune 功能，因此无需单独下载 HPTune。

执行应用程序时，**-verbosegc** 输出结果将被重定向到单独的文件。

您可以使用 HPJMeter 打开重定向的文件，从而通过直观的 GUI 更快、更轻松地分析 GC 性能数据。

![图 4：HPJMeter。](https://www.cubrid.org/layouts/layout_master/img/99ed9348c60cdcdfb00857ce8a7187ed.png)

**图 4：HPJMeter。**

## 总结

在本文中，重点介绍了*如何监控 GC 操作信息*，作为 GC 调优的准备阶段。从我个人的经验来看，我建议使用 **jstat** 来监控GC操作，如果你觉得执行GC的时间太长，那就试试 **-verbosegc** 选项来分析GC。一般的 GC 调优过程是在基于分析应用 **-verbosegc** 选项后，根据分析结果更改应用的 GC 选项。在下一篇文章中，我们将通过使用真实案例作为示例来了解执行 GC 调优的最佳选项。



参考文章

https://www.cubrid.org/blog/3826417

