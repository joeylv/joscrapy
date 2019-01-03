  * 1 JDK11发布计划
  * 2 JDK11特性一览
  * 3 特性详解
    * 3.1 JEP 318: Epsilon: A No-Op Garbage Collector
    * 3.2 JEP 320: Remove the Java EE and CORBA Modules
    * 3.3 JEP 321: HTTP Client (Standard)
    * 3.4 JEP 323: Local-Variable Syntax for Lambda Parameters
    * 3.5 JEP 324: Key Agreement with Curve25519 and Curve448
    * 3.6 JEP 327: Unicode 10
    * 3.7 JEP 328: Flight Recorder
    * 3.8 JEP 329: ChaCha20 and Poly1305 Cryptographic Algorithms
    * 3.9 JEP 330: Launch Single-File Source-Code Programs
    * 3.10 JEP 331: Low-Overhead Heap Profiling
    * 3.11 JEP 332: Transport Layer Security (TLS) 1.3
    * 3.12 JEP 333: ZGC: A Scalable Low-Latency Garbage Collector (Experimental)

> 原文出处:[ 阿飞的博客](https://mp.weixin.qq.com/s/Yz8V3inWN8uErKM-IdMFWQ)

千呼万唤，JDK11 于 2018-09-25 正式发布！你是不是和笔者一样还在使用JDK8 呢？甚至有些开发者还在使用 JDK7！没关系，让我们先一睹
JDK11 的风采。

## JDK11发布计划

  * 2018/06/28 Rampdown Phase One (fork from main line)
  * 2018/07/19 All Tests Run
  * 2018/07/26 Rampdown Phase Two
  * 2018/08/16 Initial Release Candidate
  * 2018/08/30 Final Release Candidate
  * **2018/09/25 General Availability**

> 说明：GA即General Availability，也就是官方推荐可以广泛使用的版本。

##  JDK11特性一览

  * 181: Nest-Based Access Control
  * 309: Dynamic Class-File Constants
  * 315: Improve Aarch64 Intrinsics
  * 318: Epsilon: A No-Op Garbage Collector
  * 320: Remove the Java EE and CORBA Modules
  * 321: HTTP Client (Standard)
  * 323: Local-Variable Syntax for Lambda Parameters
  * 324: Key Agreement with Curve25519 and Curve448
  * 327: Unicode 10
  * 328: Flight Recorder
  * 329: ChaCha20 and Poly1305 Cryptographic Algorithms
  * 330: Launch Single-File Source-Code Programs
  * 331: Low-Overhead Heap Profiling
  * 332: Transport Layer Security (TLS) 1.3
  * 333: ZGC: A Scalable Low-Latency Garbage Collector  
(Experimental)

  * 335: Deprecate the Nashorn JavaScript Engine
  * 336: Deprecate the Pack200 Tools and API

## 特性详解

接下来对每个特性进行详细解读。

### JEP 318: Epsilon: A No-Op Garbage Collector

JDK 上对这个特性的描述是：开发一个处理内存分配但不实现任何实际内存回收机制的 GC，一旦可用堆内存用完，JVM 就会退出。

如果有 System.gc() 的调用，实际上什么也不会发生（这种场景下和 -XX:+DisableExplicitGC
效果一样），因为没有内存回收，这个实现可能会警告用户尝试强制 GC 是徒劳。

用法非常简单：`-XX:+UseEpsilonGC`。

* * *

**动机**

提供完全被动的 GC 实现，具有有限的分配限制和尽可能低的延迟开销，但代价是内存占用和内存吞吐量。

众所周知，Java 实现可广泛选择高度可配置的 GC 实现。 各种可用的收集器最终满足不同的需求，即使它们的可配置性使它们的功能相交。
有时更容易维护单独的实现，而不是在现有 GC 实现上堆积另一个配置选项。

它的主要用途如下：

  * 性能测试（它可以帮助过滤掉GC引起的性能假象）；
  * 内存压力测试（例如，知道测试用例应该分配不超过 1 GB 的内存，我们可以使用 -Xmx1g 配置 -XX:+UseEpsilonGC ，如果违反了该约束，则会 heap dump 并崩溃）；
  * 非常短的 JOB 任务（对于这种任务，接受 GC 清理堆那都是浪费空间）；
  * VM接口测试；
  * Last-drop 延迟&吞吐改进；

### JEP 320: Remove the Java EE and CORBA Modules

Java EE 和 CORBA 两个模块在 JDK9 中已经标记” **deprecated** “，在JDK11 中正式移除。JDK 中
deprecated 的意思是在不建议使用，在未来的 release 版本会被删除。

* * *

**动机**

JavaEE 由 4 部分组成：

  * JAX-WS (Java API for XML-Based Web Services),
  * JAXB (Java Architecture for XML Binding)
  * JAF (the JavaBeans Activation Framework)
  * Common Annotations.

但是这个特性和 JavaSE 关系不大。并且 JavaEE 被维护在
Github（https://github.com/javaee）中，版本同步造成维护困难。最后，JavaEE 可以单独引用，maven 中心仓库也提供了
JavaEE（http://mvnrepository.com/artifact/javax/javaee-api/8.0），所以没必要把 JavaEE
包含到 JavaSE 中。

至于 CORBA ，使用 Java 中的 CORBA 开发程序没有太大的兴趣。因此，在JavaEE 就把 CORBA 标记为 “Proposed
Optional” ，这就表明将来可能会放弃对这些技术的必要支持。

### JEP 321: HTTP Client (Standard)

将 JDK9 引进并孵化的 HTTP 客户端 API 作为标准，即 HTTP/2 Client。它定义了一个全新的实现了 HTTP/2 和
WebSocket 的 HTTP 客户端 API，并且可以取代 HttpURLConnection。

* * *

**动机**

已经存在的 HttpURLConnection 有如下问题:

  * 在设计时考虑了多种协议，但是现在几乎所有协议现已不存在。
  * API 早于 HTTP/1.1 并且太抽象；
  * 使用很不友好；
  * 只能以阻塞模式工作；
  * 非常难维护；

### JEP 323: Local-Variable Syntax for Lambda Parameters

在声明隐式类型的lambda表达式的形参时允许使用var。

* * *

**动机**

lamdba 表达式可能是隐式类型的，它形参的所有类型全部靠推到出来的。隐式类型 lambda 表达式如下：

    
    
    (x, y) -> x.process(y)
    

Java SE 10让隐式类型变量可用于本地变量:

    
    
    var foo = new Foo();
    for (var foo : foos) { ... }
    try (var foo = ...) { ... } catch ...
    

为了和本地变量保持一致，我们希望允许 var 作为隐式类型 lambda 表达式的形参：

    
    
    (var x, var y) -> x.process(y)
    

统一格式的一个好处就是 modifiers 和 notably 注解能被加在本地变量和 lambda 表达式的形参上，并且不会丢失简洁性：

    
    
    @Nonnull var x = new Foo();
    (@Nonnull var x, @Nullable var y) -> x.process(y)
    

### JEP 324: Key Agreement with Curve25519 and Curve448

用 RFC 7748 中描述到的 Curve25519 和 Curve448 实现秘钥协议。 RFC 7748 定义的秘钥协商方案更高效，更安全。这个
JEP 的主要目标就是为这个标准定义 API 和实现。

* * *

**动机**

密码学要求使用 Curve25519 和 Curve448 是因为它们的安全性和性能。JDK 会增加两个新的接口 XECPublicKey 和
XECPrivateKey，示例代码如下：

    
    
    KeyPairGenerator kpg = KeyPairGenerator.getInstance("XDH");
    NamedParameterSpec paramSpec = new NamedParameterSpec("X25519");
    kpg.initialize(paramSpec); // equivalent to kpg.initialize(255)
    // alternatively: kpg = KeyPairGenerator.getInstance("X25519")
    KeyPair kp = kpg.generateKeyPair();
    
    KeyFactory kf = KeyFactory.getInstance("XDH");
    BigInteger u = ...
    XECPublicKeySpec pubSpec = new XECPublicKeySpec(paramSpec, u);
    PublicKey pubKey = kf.generatePublic(pubSpec);
    
    KeyAgreement ka = KeyAgreement.getInstance("XDH");
    ka.init(kp.getPrivate());
    ka.doPhase(pubKey, true);
    byte[] secret = ka.generateSecret();
    

### JEP 327: Unicode 10

更新平台 API 支持 Unicode 10.0版本（Unicode 10.0 概述：Unicode 10.0 增加了 8518 个字符, 总计达到了
136,690 个字符. 并且增加了 4 个脚本, 总结 139 个脚本, 同时还有 56 个新的 emoji
表情符号。参考：http://unicode.org/versions/Unicode10.0.0/）。

* * *

**动机**

Unicode 是一个不断进化的工业标准，因此必须不断保持 Java 和 Unicode 最新版本同步。

### JEP 328: Flight Recorder

提供一个低开销的，为了排错Java应用问题，以及JVM问题的数据收集框架，希望达到的目标如下：

  * 提供用于生产和消费数据作为事件的API；
  * 提供缓存机制和二进制数据格式；
  * 允许事件配置和事件过滤；
  * 提供OS，JVM和JDK库的事件；

* * *

**动机**

排错，监控，性能分析是整个开发生命周期必不可少的一部分，但是某些问题只会在大量真实数据压力下才会发生在生产环境。

**Flight Recorder** 记录源自应用程序，JVM和OS的事件。
事件存储在一个文件中，该文件可以附加到错误报告中并由支持工程师进行检查，允许事后分析导致问题的时期内的问题。工具可以使用API从记录文件中提取信息。

> 多说一句：Flight Recorder的名字来源有点像来自于飞机的黑盒子，一种用来记录飞机飞行情况的的仪器。而Flight
Recorder就是记录Java程序运行情况的工具。

### JEP 329: ChaCha20 and Poly1305 Cryptographic Algorithms

实现RFC 7539中指定的 ChaCha20 和 ChaCha20-Poly1305 两种加密算法。

* * *

**动机**

唯一一个其他广泛采用的RC4长期以来一直被认为是不安全的，业界一致认为当下ChaCha20-Poly1305是安全的。

### JEP 330: Launch Single-File Source-Code Programs

增强Java启动器支持运行单个Java源代码文件的程序。

* * *

**动机**

单文件程序是指整个程序只有一个源码文件，通常是早期学习Java阶段，或者写一个小型工具类。以HelloWorld.java为例，运行它之前需要先编译。我们希望Java启动器能直接运行这个源码级的程序：

    
    
    java HelloWorld.java
    

等价于：

    
    
    javac -d <memory> HelloWorld.java
    java -cp <memory> helloWorld</code> <code class="">java Factorial.java 3 4 5
    

等价于：

    
    
    javac -d <memory> Factorial.java
    java -cp <memory> Factorial 3 4 5
    

到JDK10为止，Java启动器能以三种方式运行：

  1. 启动一个class文件；
  2. 启动一个JAR中的main方法类；
  3. 启动一个模块中的main方法类；

JDK11再加一个，即第四种方式：启动一个源文件申明的类。

### JEP 331: Low-Overhead Heap Profiling

提供一种低开销的Java堆分配采样方法，得到堆分配的Java对象信息，可通过JVMTI访问。希望达到的目标如下：

  * 足够低的开销，可以默认且一直开启；
  * 能通过定义好的程序接口访问；
  * 能采样所有分配；
  * 能给出生存和死亡的Java对象信息；

* * *

**动机**

对用户来说，了解它们堆里的内存是很重要的需求。目前有一些已经开发的工具，允许用户窥探它们的堆，比如：Java Flight Recorder, jmap,
YourKit, 以及VisualVM tools.。但是这工具都有一个很大的缺点：无法得到对象的分配位置。headp dump以及heap
histo都没有这个信息，但是这个信息对于调试内存问题至关重要。因为它能告诉开发者，他们的代码发生（尤其是坏的）分配的确切位置。

### JEP 332: Transport Layer Security (TLS) 1.3

实现TLS协议1.3版本。（TLS允许客户端和服务端通过互联网以一种防止窃听，篡改以及消息伪造的方式进行通信）。

* * *

**动机**

TLS 1.3是TLS协议的重大改进，与以前的版本相比，它提供了显着的安全性和性能改进。其他供应商的几个早期实现已经可用。我们需要支持TLS
1.3以保持竞争力并与最新标准保持同步。这个特性的实现动机和Unicode 10一样，也是紧跟历史潮流。

### JEP 333: ZGC: A Scalable Low-Latency Garbage Collector (Experimental)

ZGC：这应该是JDK11最为瞩目的特性，没有之一。但是后面带了 **Experimental**
，说明还不建议用到生产环境。看看官方对这个特性的目标描述：

  * GC暂停时间不会超过10ms；
  * 即能处理几百兆小堆，也能处理几个T的大堆（OMG）；
  * 和G1相比，应用吞吐能力不会下降超过15%；
  * 为未来的GC功能和利用colord指针以及Load barriers优化奠定基础；
  * 初始只支持64位系统；

* * *

**动机**

GC是Java主要优势之一。然而，当GC停顿太长，就会开始影响应用的响应时间。消除或者减少GC停顿时长，Java将对更广泛的应用场景是一个更有吸引力的平台。此外，现代系统中可用内存不断增长，
用户和程序员希望JVM能够以高效的方式充分利用这些内存，并且无需长时间的GC暂停时间。

ZGC一个并发，基于region， **压缩** 型的垃圾收集器， **只有root扫描阶段会STW**
，因此GC停顿时间不会随着堆的增长和存活对象的增长而变长。

ZGC和G1停顿时间比较：

    
    
    ZGC
                    avg: 1.091ms (+/-0.215ms)
        95th percentile: 1.380ms
        99th percentile: 1.512ms
      99.9th percentile: 1.663ms
     99.99th percentile: 1.681ms
                    max: 1.681ms
    
    G1
                    avg: 156.806ms (+/-71.126ms)
        95th percentile: 316.672ms
        99th percentile: 428.095ms
      99.9th percentile: 543.846ms
     99.99th percentile: 543.846ms
                    max: 543.846ms
    

用法：`-XX:+UnlockExperimentalVMOptions
-XX:+UseZGC`，因为ZGC还处于实验阶段，所以需要通过JVM参数UnlockExperimentalVMOptions 来解锁这个特性。

> 参考：http://openjdk.java.net/projects/jdk/11/

