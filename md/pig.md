# 使用 Apache Pig 处理数据

使用 Apache Pig 从大数据集中获得所需的信息

Tim 是我们最受欢迎的撰稿人之一，并且是一位多产撰稿人。浏览 developerWorks 上的 [所有 Tim
的文章](http://www.ibm.com/developerworks/cn/views/libraryview.jsp?search_by=tim%20jones)。查看
[Tim
的个人档案](https://www.ibm.com/developerworks/mydeveloperworks/profiles/user/MTimJones)
并在 developerWorks 社区中与 Tim、其他撰稿人以及开发伙伴们联系。

Hadoop 的普及和其生态系统的不断壮大并不令人感到意外。Hadoop 不断进步的一个特殊领域是 Hadoop 应用程序的编写。虽然编写 Map 和
Reduce 应用程序并不十分复杂，但这些编程确实需要一些软件开发经验。Apache Pig 改变了这种状况，它在 MapReduce
的基础上创建了更简单的过程语言抽象，为 Hadoop 应用程序提供了一种更加接近结构化查询语言 (SQL) 的接口。因此，您不需要编写一个单独的
MapReduce 应用程序，您可以用 Pig Latin 语言写一个脚本，在集群中自动并行处理与分发该脚本。

## Pig Latin 示例

让我们从一个简单的 Pig 示例开始介绍，并剖析该示例。Hadoop 的一个有趣的用法是，在大型数据集中搜索满足某个给定搜索条件的记录（在 Linux®
中被称为 `grep`）。[清单
1](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list1)
显示了在 Pig
中实现该过程的简单性。在所显示的三行代码中，只有一行是真正的搜索。第一行只是将测试数据集（消息日志）读取到代表元组集合的包中。用一个正则表达式来筛选该数据（元组中的惟一条目，表示为
`$0` 或 field 1），然后查找字符序列 `WARN`。最后，在主机文件系统中将这个包存储在一个名为 _warnings_
的新文件中，这个包现在代表来自消息的包含 `WARN` 的所有元组。

##### 清单 1. 一个简单的 Pig Latin 脚本  
  
<table>  
<tr>  
<td>

1

2

3

</td>  
<td>

`messages = LOAD "messages";`

`warns = FILTER messages BY $0 MATCHES ".*WARN+.*";`

`STORE warns INTO "warnings";`

</td> </tr> </table>

如您所见，这个简单的脚本实现了一个简单的流，但是，如果直接在传统的 MapReduce 模型中实现它，则需要增加大量的代码。这使得学习 Hadoop
并开始使用数据比原始开发容易得多。

现在让我们更深入地探讨 Pig 语言，然后查看该语言的一些功能的其他示例。

## Pig Latin 的基础知识

Pig Latin 是一个相对简单的语言，它可以执行语句。一调 _语句_
就是一个操作，它需要输入一些内容（比如代表一个元组集的包），并发出另一个包作为其输出。一个 _包_
就是一个关系，与表类似，您可以在关系数据库中找到它（其中，元组代表行，并且每个元组都由字段组成）。

用 Pig Latin
编写的脚本往往遵循以下特定格式，从文件系统读取数据，对数据执行一系列操作（以一种或多种方式转换它），然后，将由此产生的关系写回文件系统。您可以在 [清单
1](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list1)
中看到该模式的最简单形式（一个转换）。

Pig 拥有大量的数据类型，不仅支持包、元组和映射等高级概念，还支持简单的数据类型，如
`int`、`long`、`float`、`double`、`chararray` 和 `bytearray`。如果使用简单的类型，您会发现，除了称为
`bincond` 的条件运算符（其操作类似于 `C ternary` 运算符）之外，还有其他许多算术运算符（比如
`add`、`subtract`、`multiply`、`divide` 和
`module`）。并且，如您所期望的那样，还有一套完整的比较运算符，包括使用正则表达式的丰富匹配模式。

所有 Pig Latin 语句都需要对关系进行操作（并被称为 _关系运算符_ ）。正如您在 [清单
1](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list1)
中看到的，有一个运算符用于从文件系统加载数据和将数据存储到文件系统中。有一种方式可以通过迭代关系的行来 `FILTER`
数据。此功能常用于从后续操作不再需要的关系中删除数据。另外，如果您需要对关系的列进行迭代，而不是对行进行迭代，您可以使用 `FOREACH`
运算符。`FOREACH` 允许进行嵌套操作，如 `FILTER` 和 `ORDER`，以便在迭代过程中转换数据。

`ORDER` 运算符提供了基于一个或多个字段对关系进行排序的功能。`JOIN` 运算符基于公共字段执行两个或两个以上的关系的内部或外部联接。`SPLIT`
运算符提供了根据用户定义的表达式将一个关系拆分成两个或两个以上关系的功能。最后，`GROUP` 运算符根据某个表达式将数据分组成为一个或多个关系。[表
1](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#table1)
提供了 Pig 中的部分关系运算符列表。

##### 表 1. Pig Latin 关系运算符的不完整列表  
  
<table>  
<tr>  
<th>

运算符

</th>  
<th>

描述

</th></tr>  
<tr>  
<td>

`FILTER`

</td>  
<td>

基于某个条件从关系中选择一组元组。

</td> </tr>  
<tr>  
<td>

`FOREACH`

</td>  
<td>

对某个关系的元组进行迭代，生成一个数据转换。

</td> </tr>  
<tr>  
<td>

`GROUP`

</td>  
<td>

将数据分组为一个或多个关系。

</td> </tr>  
<tr>  
<td>

`JOIN`

</td>  
<td>

联接两个或两个以上的关系（内部或外部联接）。

</td> </tr>  
<tr>  
<td>

`LOAD`

</td>  
<td>

从文件系统加载数据。

</td> </tr>  
<tr>  
<td>

`ORDER`

</td>  
<td>

根据一个或多个字段对关系进行排序。

</td> </tr>  
<tr>  
<td>

`SPLIT`

</td>  
<td>

将一个关系划分为两个或两个以上的关系。

</td> </tr>  
<tr>  
<td>

`STORE`

</td>  
<td>

在文件系统中存储数据。

</td> </tr> </table>

虽然这不是一个详尽的 Pig Latin 运算符清单，但该表提供了一套在处理大型数据集时非常有用的操作。您可以通过
[参考资料](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#artrelatedtopics)
了解完整的 Pig Latin 语言，因为 Pig 有一套不错的在线文档。现在尝试着手编写一些 Pig Latin 脚本，以了解这些运算符的实际工作情况。

## 获得 Pig

在有关 Hadoop 的早期文章中，我采用的方法是将 Hadoop 安装和配置为一个软件包。但 Cloudera 通过用 Linux
将它打包为一个虚拟设备，使得 Hadoop 更易于使用。虽然它是一个较大的下载，但它已预建立并配置了虚拟机 (VM)，其中不仅有 Hadoop，还包括了
Apache Hive 和 Pig。因此，利用一个下载和免费提供的 2 型虚拟机管理程序（VirtualBox 或基于内核的虚拟机
[KVM]），您便可以拥有预配置的、已准备就绪的整个 Hadoop 环境。

## 让 Hadoop 和 Pig 启动并运行

下载完您的特定虚拟机文件之后，需要为您的特定虚拟机管理程序创建一个 VM。在
[参考资料](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#artrelatedtopics)
中，您可以找到该操作的分步指南。

##### Cloudera VM 内存

我发现，仅为虚拟机分配 1GB 的内存时，它无法正常工作。将该内存分配提高至两倍甚至三倍时，它才能够正常运行（也就是说，不会出现 Java™
堆内存的问题）。

一旦创建了自己的 VM，就可以通过 VirtualBox 来启动它，VirtualBox 引导 Linux 内核，并启动所有必要的 Hadoop
守护进程。完成引导后，从创建一个与 Hadoop 和 Pig 通信的终端开始相关操作。

您可以在两种模式中任选一种来使用 Pig。第一种是 Local（本地）模式，它不需要依赖 Hadoop 或 Hadoop 分布式文件系统
(HDFS)，在该模式中，所有操作都在本地文件系统上下文中的单一 Java 虚拟机 (JVM) 上执行。另一种模式是 MapReduce 模式，它使用了
Hadoop 文件系统和集群。

### Local 模式的 Pig

对于 Local 模式，只需启动 Pig 并用 `exectype` 选项指定 Local 模式即可。这样做可以将您带入 Grunt
外壳，使您能够以交互方式输入 Pig 语句：  
  
<table>  
<tr>  
<td>

1

2

3

</td>  
<td>

`$ pig -x local`

`...`

`grunt>`

</td> </tr> </table>

在这里，您能够以交互方式编写 Pig Latin 脚本的代码，并查看每个运算符后面的结果。返回 [清单
1](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list1)，并尝试使用这个脚本（参见
[清单
2](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list2)）。注意，在这种情况下，不需要将数据存储到某个文件中，只需将它转储为一组关系。您可能会在修改后的输出中看到，每个日志行（与
`FILTER` 定义的搜索条件相匹配）本身就是一个关系（以括号 [`()`] 为界）。

##### 清单 2. 在 Local 模式中以交互方式使用 Pig  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

</td>  
<td>

`grunt> messages = LOAD "/var/log/messages";`

`grunt> warns = FILTER messages BY $0 MATCHES ".*WARN+.*";`

`grunt> DUMP warns`

`...`

`(Dec 10 03:56:43 localhost NetworkManager: <``WARN``>
nm_generic_enable_loopback(): error ...`

`(Dec 10 06:10:18 localhost NetworkManager: <``WARN``> check_one_route():
(eth0) error ...`

`grunt>`

</td> </tr> </table>

如果您已经指定 `STORE` 运算符，那么它会在一个指定名称的目录（而不是一个简单的常规文件）中生成您的数据。

### Mapreduce 模式中的 Pig

对于 MapReduce 模式，必须首先确保 Hadoop 正在运行。要做到这一点，最简单的方法是在 Hadoop 文件系统树的根上执行文件列表操作，如
[清单
3](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list3)
所示。

##### 清单 3. 测试 Hadoop 可用性  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

</td>  
<td>

`$ hadoop dfs -ls /`

`Found 3 items`

`drwxrwxrwx - hue supergroup 0 2011-12-08 05:20 /tmp`

`drwxr-xr-x - hue supergroup 0 2011-12-08 05:20 /user`

`drwxr-xr-x - mapred supergroup 0 2011-12-08 05:20 /var`

`$`

</td> </tr> </table>

如清单 3 所示，如果 Hadoop 成功运行，此代码的结果会是一个或多个文件组成的​​列表。现在，让我们来测试 Pig。从启动 Pig
开始，然后将目录更改为您的 HDFS 根，以确定在 HDFS 中是否可以看到外部所看到的结果（参见 [清单
4](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list4)）。

##### 清单 4. 测试 Pig  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

10

11

12

</td>  
<td>

`$ pig`

`2011-12-10 06:39:44,276 [main] INFO org.apache.pig.Main - Logging error
messages to...`

`2011-12-10 06:39:44,601 [main] INFO org.apache.pig.... Connecting to hadoop
file \`

`system at: hdfs://0.0.0.0:8020`

`2011-12-10 06:39:44,988 [main] INFO org.apache.pig.... connecting to map-
reduce \`

`job tracker at: 0.0.0.0:8021`

`grunt> cd hdfs:///`

`grunt> ls`

`hdfs://0.0.0.0/tmp <``dir``>`

`hdfs://0.0.0.0/user <``dir``>`

`hdfs://0.0.0.0/var <``dir``>`

`grunt>`

</td> </tr> </table>

到目前为止，一切都很好。您可以在 Pig 中看到您的 Hadoop 文件系统，所以，现在请尝试从您的本地主机文件系统将一些数据读取到 HDFS 中。可以通过
Pig 将某个文件从本地复制到 HDFS（参见 [清单
5](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list5)）。

##### 清单 5. 获得一些测试数据  
  
<table>  
<tr>  
<td>

1

2

3

4

5

</td>  
<td>

`grunt> mkdir test`

`grunt> cd test`

`grunt> copyFromLocal /etc/passwd passwd`

`grunt> ls`

`hdfs://0.0.0.0/test/passwd<``r` `1> 1728`

</td> </tr> </table>

接下来，在 Hadoop 文件系统中测试数据现在是安全的，您可以尝试另一个脚本。请注意，您可以在 Pig 内 `cat`
文件，查看其内容（只是看看它是否存在）。在这个特殊示例中，将确定在 passwd 文件中为用户指定的外壳数量（在 passwd 文件中的最后一列）。

要开始执行该操作，需要从 HDFS 将您的 passwd 文件载入一个 Pig 关系中。在使用 `LOAD`
运算符之前就要完成该操作，但在这种情况下，您可能希望将密码文件的字段解析为多个独立的字段。在本例中，我们指定了 `PigStorage`
函数，您可以使用它来显示文件的分隔符（本例中，是冒号 [`:`] 字符）。您也可以用 `AS` 关键字指定独立字段（或架构），包括它们的独立类型（参见
[清单
6](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list6)）。

##### 清单 6. 将文件读入一个关系中  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

</td>  
<td>

`grunt> passwd = LOAD "/etc/passwd" USING PigStorage(":") AS (user:chararray,
\`

`passwd:chararray, uid:int, gid:int, userinfo:chararray, home:chararray, \`

`shell:chararray);`

`grunt> DUMP passwd;`

`(root,x,0,0,root,/root,/bin/bash)`

`(bin,x,1,1,bin,/bin,/sbin/nologin)`

`...`

`(cloudera,x,500,500,,/home/cloudera,/bin/bash)`

`grunt>`

</td> </tr> </table>

接下来，使用 `GROUP` 运算符根据元组的外壳将元组分组到该关系中（参见 [清单
7](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list7)）。再次转储此关系，这样做只是为了说明
`GROUP` 运算符的结果。注意，在这里，您需要根据元组正使用的特定外壳（在开始时指定的外壳）对元组进行分组（作为一个内部包）。

##### 清单 7. 将元组分组为其外壳的一个函数  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

</td>  
<td>

`grunt> grp_shell = GROUP passwd BY shell;`

`grunt> DUMP grp_shell;`

`(/bin/bash,{(cloudera,x,500,500,,/home/cloudera,/bin/bash),(root,x,0,0,...),
...})`

`(/bin/sync,{(sync,x,5,0,sync,/sbin,/bin/sync)})`

`(/sbin/shutdown,{(shutdown,x,6,0,shutdown,/sbin,/sbin/shutdown)})`

`grunt>`

</td> </tr> </table>

但是，您想要的是在 passwd 文件中指定的独特外壳的计数。所以，需要使用 `FOREACH` 运算符来遍历分组中的每个元组，`COUNT`
出现的数量（参见 [清单
8](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#list8)）。

##### 清单 8. 利用每个外壳的计数对结果进行分组  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

10

</td>  
<td>

`grunt> counts = FOREACH grp_shell GENERATE group, COUNT(passwd);`

`grunt> DUMP counts;`

`...`

`(/bin/bash,5)`

`(/bin/sync,1)`

`(/bin/false,1)`

`(/bin/halt,1)`

`(/bin/nologin,27)`

`(/bin/shutdown,1)`

`grunt>`

</td> </tr> </table>

**备注：** 如果要将该代码作为一个脚本来执行，只需将脚本输入到某个文件中，然后使用 `pig myscript.pig` 来执行它。

## 诊断运算符

Pig 支持大量诊断运算符，您可以用它们来调试 Pig 脚本。正如您在之前的脚本示例中所看到的，`DUMP`
运算符是无价的，它不仅可以查看数据，还可以查看数据架构。您还可以使用 `DESCRIBE` 运算符来生成一个关系架构的详细格式（字段和类型）。

`EXPLAIN` 运算符更复杂一些，但也很有用。对于某个给定的关系，您可以使用 `EXPLAIN` 来查看如何将物理运算符分组为 Map 和 Reduce
任务（也就是说，如何推导出数据）。

[表
2](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#table2) 对
Pig Latin 中的诊断运算符及其描述提供了一个列表。

##### 表 2. Pig Latin 诊断运算符  
  
<table>  
<tr>  
<th>

运算符

</th>  
<th>

描述

</th></tr>  
<tr>  
<td>

`DESCRIBE`

</td>  
<td>

返回关系的架构。

</td> </tr>  
<tr>  
<td>

`DUMP`

</td>  
<td>

将关系的内容转储到屏幕。

</td> </tr>  
<tr>  
<td>

`EXPLAIN`

</td>  
<td>

显示 MapReduce 执行计划。

</td> </tr> </table>

## 用户定义的函数

虽然 Pig 在本文探讨的范围内是强大且有用的，但是通过用户定义的函数 (UDF) 可以使它变得更强大。Pig
脚本可以使用您为解析输入数据、格式化输出数据甚至运算符等定义的函数。UDF 是用 Java 语言编写的，允许 Pig 支持自定义处理。UDF 是将 Pig
扩展到您的特定应用程序领域的一种方式。您可以在
[参考资料](https://www.ibm.com/developerworks/cn/linux/l-apachepigdataquery/#artrelatedtopics)
中了解有关 UDF 开发的更多信息。

## Pig 用户

正如您从这篇短文中可以看到的，Pig 是一个强大的工具，可以在 Hadoop 集群中查询数据。它是如此强大，Yahoo! 估计，其 Hadoop
工作负载中有 40% 至 60% 由 Pig Latin 脚本产生。在 Yahoo! 的 100,000 个 CPU 中，大约有 50% 的 CPU
仍在运行 Hadoop。

但 Yahoo! 并不是利用 Pig 的惟一组织。您在 Twitter 中也会发现 Pig（用于处理日志和挖掘微博数据）；在 AOL 和 MapQuest
上也会发现它（用于分析和批量数据处理）；而在 LinkedIn 上，Pig 用于发现您可能认识的人。据报道，Ebay 使用 Pig 来实现搜索优化，而
adyard 的推荐工具系统有大约一半都使用了 Pig。

## 展望未来

没有一本书可以完全列举 Pig 背后处理大数据的强大功能。即使对于非开发人员而言，Pig 也可以使得执行 Hadoop 集群上的大数据处理变得很容易。Pig
最初是由 Yahoo! 于 2006 年开发，并且此后不久被迁移到 Apache Software
Foundation，使得它在全球范围得到广泛应用。进行这种迁移是因为 Yahoo! 研究人员意识到 Pig 能为非开发人员提供强大的功能。Hadoop
作为一个基础架构已经逐渐开始普及，Hadoop 生态系统将会改变大数据的外观及其日益增长的使用情况。

#### 相关主题

    * [Apache 网站](http://pig.apache.org/) 是有关 Pig 的信息来源，包括时事新闻、最新的软件、如何入门和如何参与。
    * [Hadoop Demo VM](https://ccp.cloudera.com/display/SUPPORT/Cloudera%27s+Hadoop+Demo+VM) 是目前使 Hadoop 实例运行的最简单方式。该 VM 中包含了您所需的一切，包括 Hadoop、Hive 和一个 CentOS Linux 操作系统上的 Pig。
    * [Cloudera Training VM](http://www.cloudera.com/blog/2009/07/cloudera-training-vm-virtualbox/) 是一个极佳的 Hadoop 入门方式。它最大限度地减少所需的配置量，让您可以轻松地开始利用 Hadoop 和 Pig 处理数据集。
    * [虚拟设备和 Open Virtualization Format](http://www.ibm.com/developerworks/cn/linux/l-open-virtualization-format-toolkit/)（M. Tim Jones，developerWorks，2009 年 10 月）探讨了将虚拟设备用作一种新的软件交付形式。虚拟设备允许将预配置软件（带操作系统）作为一个 VM 进行分发。
    * Pig 有大量的在线资源，包括参考手册、操作手册和其他参考资料。Pig 也有两本写得很好的手册（[第 1 部分](http://pig.apache.org/docs/r0.7.0/piglatin_ref1.html) 和 [第 2 部分](http://pig.apache.org/docs/r0.7.0/piglatin_ref2.html)）、一本 [脚本操作手册](http://pig.apache.org/docs/r0.7.0/cookbook.html) 和一本 [UDF 指南](http://pig.apache.org/docs/r0.7.0/udf.html)。
    * 拥有由重要的 Web 资产所组成的庞大用户群。在 Apache 的 [PoweredBy](https://cwiki.apache.org/confluence/display/PIG/PoweredBy) 页面上了解使用 Pig 的多种 Web 企业。
    * 在 [developerWorks Linux 专区](http://www.ibm.com/developerworks/linux/index.html) 中，查找数百篇 [指南文章和教程](http://www.ibm.com/developerworks/views/linux/libraryview.jsp)，还有下载、论坛，以及针对 Linux 开发人员和管理员的丰富资源。
    * [developerWorks 中国网站开源技术专区](http://www.ibm.com/developerworks/cn/opensource/) 提供了有关开源工具和使用开源技术的丰富信息。
    * 以最适合您的方式 [IBM 产品评估试用版软件](http://www.ibm.com/developerworks/cn/downloads/)：下载产品试用版，在线试用产品，在云环境下试用产品，或者在 [IBM SOA 人员沙箱](http://www.ibm.com/developerworks/cn/downloads/soasandbox/people/) 中花费几个小时来学习如何高效实现面向服务架构。
    * 在 [developerWorks Linux 专区](http://www.ibm.com/developerworks/cn/linux/) 寻找为 Linux 开发人员（包括 [Linux 新手入门](http://www.ibm.com/developerworks/cn/linux/newto/)）准备的更多参考资料，查阅我们 [最受欢迎的文章和教程](http://www.ibm.com/developerworks/cn/linux/best2009/index.html)。
    * 在 developerWorks 上查阅所有 [Linux 技巧](http://www.ibm.com/developerworks/cn/views/linux/libraryview.jsp?search_by=Linux+%E6%8A%80%E5%B7%A7) 和 [Linux 教程](http://www.ibm.com/developerworks/cn/views/linux/libraryview.jsp?type_by=%E6%95%99%E7%A8%8B)。
    * 随时关注 developerWorks [技术活动](http://www.ibm.com/developerworks/cn/offers/techbriefings/)和[网络广播](http://www.ibm.com/developerworks/cn/swi/)。

