  * 1 概况
  * 2 依赖的技术栈
  * 3 sharding-jdbc架构图
  * 4 sharding-jdbc-doc
  * 5 sharding-jdbc实现剖析
  * 6 Debug sharding-jdbc

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/7831817c1da8>

接下来对sharding-jdbc源码的分析基于tag为`1.5.4.1`源码，根据[sharding-jdbc
Features](https://link.jianshu.com?t=https%3A%2F%2Fgithub.com%2Fshardingjdbc%2Fsharding-
jdbc)深入学习sharding-jdbc的几个主要特性是如何实现的；

## 概况

sharding-jdbc源码主要有以下几个模块： **sharding-jdbc-config-parent** 、 **sharding-jdbc-
core** 、 **sharding-jdbc-doc** 、 **sharding-jdbc-example** 、 **sharding-jdbc-
plugin** 、 **sharding-jdbc-transaction-parent** ；由模块命名很容易知道模块的作用：

  * sharding-jdbc-config-parent：配置相关源码；
  * sharding-jdbc-core：核心源码；
  * sharding-jdbc-doc：文档，都是markdown格式，对应github上的[sharding-jdbc-doc](https://link.jianshu.com?t=https%3A%2F%2Fgithub.com%2Fshardingjdbc%2Fsharding-jdbc-doc)；
  * sharding-jdbc-example：针对各个模块的测试用例代码；
  * sharding-jdbc-plugin：目前只有KeyGenerator的三种实现；
  * sharding-jdbc-transaction-parent：事务相关源码； 

![201805031021](http://cmsblogs.qiniudn.com/201805031021.png)

## 依赖的技术栈

  1. **lombok** （能够简化java的代码，不需要显示编写setter，getter，constructor等代码，其原理是作用于javac阶段。通过反编译class文件能够看到还是有通过lombok省略的setter，getter，constructor等代码）
  2. **google-guava** （google开源的google使用的Java核心类）
  3. **elastic-job** （sharding-jdbc-transaction-async-job模块依赖elastic-job实现分布式定时任务）
  4. **inline表达式** （sharding-jdbc分库分表规则表达式采用inline语法，可以参考InlineParserTest.java这个测试类中一些inline表达式）

> 在阅读sharding-jdbc源码之前，建议对这些技术有一定的了解；

## sharding-jdbc架构图

![201805031022](http://cmsblogs.qiniudn.com/201805031022.png)

> 说明：图片来源于[sharding-
jdbc官网](https://link.jianshu.com?t=https%3A%2F%2Fgitee.com%2Fshardingjdbc%2Fsharding-
jdbc)

## sharding-jdbc-doc

请单击[sharding-jdbc-
doc](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2F1.x%2Fdocs%2F00-overview)，阅读sharding-
jdbc源码之前，建议看一下sharding-jdbc官方文档，对其原理和一些概念，以及初级使用有一个大概的了解；

## sharding-jdbc实现剖析

接下来的源码分析文章大概分析（但不局限于）sharding-jdbc的这些核心功能；

  1. 分片规则配置说明
  2. SQL解析
  3. SQL路由
  4. SQL改写
  5. SQL执行
  6. 结果归并

## Debug sharding-jdbc

学习开源组件的最好的办法就是了解它的原理后，下载它的源码，然后Run起来；sharding-jdbc的测试用例写的非常详细，`sharding-jdbc-
example-
jdbc`模块中的`com.dangdang.ddframe.rdb.sharding.example.jdbc.Main`就是一个很好的debug入口，想要正常运行这个测试用例，只需简单的如下几个步骤即可：

  1. 在本地安装一个mysql数据库；
  2. 创建两个数据库：ds_jdbc_0和ds_jdbc_1；
  3. just run it；

> 说明：sharding-jdbc源码默认使用的访问数据库的用户为root，密码为空字符串；

