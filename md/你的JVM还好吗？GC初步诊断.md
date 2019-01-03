    * 0.1 GC概念纠正
  * 1 FullGC触发条件
    * 1.1 健康的GC
      * 1.1.1 YGC
    * 1.2 OldGC
    * 1.3 FullGC

> 作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  链接：<https://www.jianshu.com/p/5ace2a0cafa4>

* * *

JVM的GC机制绝对是很多程序员的福音，它让Java程序员省去了自己回收垃圾的烦恼。从而可以把大部分时间专注业务身上，大大提高了业务开发速度，让产品需求尽快的落地抢占市场。但是也正因为如此，导致很多
Java 程序员对 JVM 和 GC 知之甚少，以我愚见大家对 JVM&GC 不够了解的有几个原因：

  * **门槛太高** 。我们平常接触的 spring，dubbo，java集合&J.U.C，网上都有无数优秀的文章对其深入的分析。而且都是基于 Java 语言，我们在学习的过程中，可以自己很容易的 debug 源码更深入的了解。但是 JVM 则不然，它是 C++ 开发的，能同时掌握 C++ 和 Java 的程序员还是很少的，自己也不太好 debug 分析它的源码（就是编译 jvm 源码，都要折腾一番）。 
  * **有价值的系列文章太少** 。网上几乎没有完整体系的文章，优秀的书籍也很少（可能大家听过或者看过最多的就是周志明的 **深入理解Java虚拟机** ，这确实是 JVM 领域比较少见的佳作）。

  * **接触的太少** 。虽然我们天天写 Java 代码，你写的每行代码 JVM 都会参与工作。但是很少进行 GC 调优，因为 JVM 是如此的优秀，绝大部分情况下，它只是默默的做你背后的女人（即使出问题了，也轮不到我们去排查，扎心了）。

>
R大是谁？语言是苍白的，请戳知乎链接：<https://www.zhihu.com/question/24923005/answer/29512367>。另外，如果对JVM很感兴趣的朋友，可以看一下R大在知乎上的一些答疑：<https://www.zhihu.com/people/rednaxelafx>。并且如果你也恰好看周志明的《深入理解Java虚拟机》，
**强烈建议**
结合R大的读书笔记进行阅读：<https://book.douban.com/people/RednaxelaFX/annotation/24722612/>。笔者还认识另外两位对JVM有一定研究的大牛：你假笨和占小狼，有性趣的同学可以关注并了解（网上其他文章，持保留意见）。

对于 JVM&GC ，很多人没有去了解它，很多人也没机会去了解它，甚至有部分人都不原因去了解它。然而要想成为一名优秀的 Java 程序员，了解 JVM
和它的 GC 机制，写出 JVM GC 机制更喜欢的代码。并且你能知道 JVM 这个背后的女人是否发脾气了，还知道她发脾气的原因，这是必须要掌握的一门技术，
**是通往高级甚至优秀必须具备的技能** 。

这篇文章我不打算普及 JVM&GC 基础，而是主要讲解 **如何初步诊断GC是否正常** ，重点讲解 `诊断GC`。所以看这篇文章的前提，需要你对 JVM
有一定的了解，比如常用的垃圾回收器，Java 堆的模型等。如果你还对 JVM 一无所知，并且确实想初步了解这门技术，那么请先花点时间看一下周志明的
《深入理解Java虚拟机》，重点关注” **第二部分 自动内存管理机制** “。

### GC概念纠正

初步诊断 GC 之前，先对 GC 中最常误解的几个概念普及一下。对 GC 机制有一定了解的同学都知道，GC 主要有
YoungGC，OldGC，FullGC（还有 G1 中独有的 Mixed GC，收集整个 young 区以及部分 Old
区，提及的概率相对少很多，本篇文章不打算讲解），大概解释一下这三种 GC，因为很多很多的同学对 OldGC 和 FullGC 有非常大的误解；

  * **Young GC** ：应该是最没有歧义的一种GC了，只是有些地方称之为`Minor GC`，或者简称`YGC`，都是没有问题的； 
  * **Old GC** ：截止 Java 发展到现在 JDK9 为止， **只单独回收Old区的只有CMS GC** ，并且我们常说的CMS是指它的 `background collection` 模式，这个模式包含 CMS GC 完整的5个阶段：初始化标记，并发标记，重新标记，并发清理，并发重置。由 CMS 的5个阶段可知，仍然有两个阶段需要 STW，所以 CMS 并不是完全并发，而是 **Mostly Concurrent Mark Sweep** ，G1 出来之前，CMS 绝对是 OLTP 系统标配的垃圾回收器。

  * **FullGC** ：有些地方称之为 `Major GC`，Major GC 通常是跟 FullGC 是等价的，都是收集整个 GC 堆。但因为 HotSpot VM 发展了这么多年，外界对各种名词的解读已经完全混乱了，当有人说 “Major GC” 的时候一定要问清楚他想要指的是上面的 FullGC 还是 OldGC（参考R大的 Major GC 和 Full GC 的区别：<https://www.zhihu.com/question/41922036/answer/93079526>）。大家普遍对这个 GC 的误解绝对是最大的（我可以说至少有 80% 的人都有误解），首先对于 ParallelOldGC 即默认 GC 在 Old 满了以后触发的 FullGC 是没有问题的，jstat 命令查看输出结果 `FGC` 的值也会相应的+ 1，即发生了一次 FGC 。 **FGC 误解主要来自最常用的 ParNew + CMS 组合** ，很多人误解 FullGC 可能是受到 `jstat` 命令结果的影响，因为发生 CMS G C时， FGC 也会增大（但是会 +2，这是因为 CMS GC 的初始化标记和重新标记都会完全的STW，从而FGC的值会+2）。但是，事实上这并没有发生FullGC。 **jstat命令结果中的FGC并不表示就一定发生了FullGC** ，很有可能只是发生了CMS GC而已。事实上，FullGC 的触发条件非常苛刻， **判断是否发生了FullGC最好的方法是通过GC日志** ，日志中如果有 “full gc” 的字样，就表示一定发生了 Full GC 。所以 **强烈建议生产环境开启 GC 日志** ，它的价值远大于它对性能的影响（不用权衡这个影响有多大，开启就对了）。

关于 CMS 的 foreground collect 模式，以及 FullGC ：

  * **foreground collect**  
它发生的场景，比如业务线程请求分配内存，但是内存不够了，于是可能触发一次CMS
GC，这个过程就必须要等待内存分配成功后线程才能继续往下面走，因此整个过程必须STW，因此这种CMS
GC整个过程都是暂停应用的，但是为了提高效率，它并不是每个阶段都会走的，只走其中一些阶段，这些省下来的阶段主要是并行阶段：Precleaning、AbortablePreclean，Resizing这几个阶段都不会经历，但不管怎么说如果走了类似foreground这种CMS
GC，那么整个过程业务线程都是不可用的，效率会影响挺大。相关源码可以在openjdk的concurrentMarkSweepGeneration.cpp中找到。

  * **G1下的FullGC**  
G1或者ParNew+CMS组合前提下，如果真的发生FullGC，则是单线程完全STW的回收方式（SerialGC），可以想象性能有多差，如果是es，hbase等需要几十个G的堆，那更是灾难。不过JDK10将对其进行优化，可以参考：http://openjdk.java.net/jeps/307，如下图所示：  
![201808221001](http://cmsblogs.qiniudn.com/wp-
content/uploads/2018/08/201808221001.jpg)  
后面还有一段描述（Description）：  
The G1 garbage collector is designed to avoid full collections, **but when the
concurrent collections can’t reclaim memory fast enough a fall back full GC
will occur. The current implementation of the full GC for G1 uses a single
threaded mark-sweep-compact algorithm**. We intend to parallelize the mark-
sweep-compact algorithm and use the same number of threads as the Young and
Mixed collections do. The number of threads can be controlled by the
-XX:ParallelGCThreads option, but this will also affect the number of threads
used for Young and Mixed collections.

##  FullGC触发条件

这里列举一些可能导致 FullGC 的原因，这也是一些高级面试可能问到的问题：

  * 没有配置 `-XX:+DisableExplicitGC` 情况下 `System.gc()` 可能会触发FullGC；
  * Promotion failed；
  * concurrent mode failure；
  * Metaspace Space 使用达到 MaxMetaspaceSize 阈值； 
  * 执行jmap -histo:live或者jmap -dump:live；

> 说明：统计发现之前 YGC 的平均晋升大小比目前 old gen 剩余的空间大，触发的是 CMS GC；如果配置了 CMS，并且 Metaspace
Space 使用量达到 MetaspaceSize 阈值也是触发 CMS GC；

这里可以参考笔者另外一篇文章：[PermSize&MetaspaceSize区别:http://mp.weixin.qq.com/s?__biz=MzU5ODUwNzY1Nw==&mid=2247483732&idx=1&sn=b5e1d0271c650b9483096412b17f41b7&chksm=fe4268b2c935e1a44ea4bc3be41813c6d70aa0f7843cf2d401c6f6fc0de4e2d821ed9733af9f&scene=21#wechat_redirect](http://mp.weixin.qq.com/s?__biz=MzU5ODUwNzY1Nw==&mid=2247483732&idx=1&sn=b5e1d0271c650b9483096412b17f41b7&chksm=fe4268b2c935e1a44ea4bc3be41813c6d70aa0f7843cf2d401c6f6fc0de4e2d821ed9733af9f&scene=21#wechat_redirect)

执行 `jmap -histo:live` 触发 FullGC 的 gc log 如下–关键词 **Heap Inspection Initiated
GC** ，通过 `jstat -gccause pid 2s` 的 LGCC 列也能看到同样的关键词：

    
    
    [Full GC (Heap Inspection Initiated GC) 2018-03-29T15:26:51.070+0800: 51.754: [CMS: 82418K->55047K(131072K), 0.3246618 secs] 138712K->55047K(249088K), [Metaspace: 60713K->60713K(1103872K)], 0.3249927 secs] [Times: user=0.32 sys=0.01, real=0.32 secs]
    

执行 jmap -dump:live 触发 FullGC 的 gc log 如下–关键词 **Heap Dump Initiated GC** ，通过
`jstat -gccause pid 2s` 的 LGCC 列也能看到同样的关键词：

    
    
    [Full GC (Heap Dump Initiated GC) 2018-03-29T15:31:53.825+0800: 354.510: [CMS2018-03-29T15:31:53.825+0800: 354.510: [CMS: 55047K->56358K(131072K), 0.3116120 secs] 84678K->56358K(249088K), [Metaspace: 62153K->62153K(1105920K)], 0.3119138 secs] [Times: user=0.31 sys=0.00, real=0.31 secs]
    

###  健康的GC

诊断 GC 的第一步，当然是知道你的 JVM 的 GC 是否正常。那么 GC 是否正常，首先就要看 YoungGC，OldGC 和 FullGC
是否正常；无论是定位 YoungGC，OldGC，FullGC 哪一种 GC，判断其是否正常主要从两个维度： **GC频率和STW时间**
；要得到这两个维度的值，我们需要知道 JVM 运行了多久，执行如下命令即可：

    
    
    ps -p pid -o etime
    

运行结果参考如下，表示这个 JVM 运行了 24 天 16 个小时 37 分 35 秒，如果 JVM 运行时间没有超过一天，执行结果类似这样
“16:37:35″：

    
    
    [afei@ubuntu ~]$ ps -p 11864 -o etime
        ELAPSED
    24-16:37:35
    

那么怎样的 GC 频率和 STW 时间才算是正常呢？这里以我以前开发过的一个`读多写少`的 dubbo 服务作为参考，该 dubbo 服务基本情况如下：

  * 日调用量 1 亿+次，接口平均响应时间 8ms 以内
  * 4 个 JVM
  * 每个 JVM 设置 Xmx 和 Xms 为 4G 并且 Xmn1G
  * 4 核 CPU + 8G 内存服务器
  * JDK7
  * AWS云服务器

GC情况如下图所示：

![201808221002](http://cmsblogs.qiniudn.com/wp-
content/uploads/2018/08/201808221002.jpg)

根据这张图输出数据，可以得到如下一些信息：

  1. JVM 运行总时间为 7293378 秒（80 _24_ 3600+9 _3600+56_ 60+18）
  2. YoungGC 频率为 2秒/次（7293378/3397184，jstat结果中YGC列的值）
  3. CMS GC 频率为 9天/次（因为FGC列的值为18，即 **最多** 发生9次 CMS GC ，所以 CMS GC 频率为 80/9≈9天/次）
  4. 每次 YoungGC 的时间为 6 ms（通过 YGCT/YGC 计算得出）
  5. FullGC 几乎没有（ JVM 总计运行80天，FGC 才18，即使是 18 次 FullGC ，FullG C频率也才 4.5天/次，更何况实际上F GC=18 肯定包含了若干次 CMS GC）

> 如果要清楚的统计 CMS GC 和 FullGC 的次数，只能通过 GC 日志了。

根据上面的GC情况，给个 **可参考的健康的GC状况** ：

  1. YoungGC 频率不超过2秒/次；
  2. CMS GC 频率不超过1天/次；
  3. 每次 YoungGC 的时间不超过 15ms；
  4. FullGC 频率尽可能完全杜绝；

> 说明：这里只是参考，不是绝对，不能说这个 GC 状况有多好，起码横向对比业务规模，以及服务器规格，你的 GC 状况不能与笔者的 dubbo
服务有明显的差距。

了解 GC 健康时候的样子，那么接下来把脉你的 JVM GC，看看是有疾在腠理，还是在肌肤，还是在肠胃，甚至已经在骨髓，病入膏肓没救了；

#### YGC

YGC 是最频繁发生的，发生的概率是 OldGC 和 FullGC 的的10倍，100倍，甚至 1000 倍。同时 YoungGC
的问题也是最难定位的。这里给出 YGC 定位三板斧（都是踩过坑）：

  1. 查看服务器 SWAP&IO 情况，如果服务器发生 SWAP，会严重拖慢 GC 效率，导致 STW 时间异常长，拉长接口响应时间，从而影响用户体验（推荐神器 `sar`，yum install sysstat 即可，想了解该命令，请搜索”`linux sar`“）； 
  2. 查看 StringTable 情况（请参考：[探索StringTable提升YGC性能:http://mp.weixin.qq.com/s?__biz=MzU5ODUwNzY1Nw==&mid=2247483752&idx=1&sn=3180eeb628e091ce5abf1ec2559d1740&chksm=fe42688ec935e198b3fa5020c4b0ec85898efeaea28d94f7b57a66fe4f4c556e601651218bfa&scene=21#wechat_redirect](http://mp.weixin.qq.com/s?__biz=MzU5ODUwNzY1Nw==&mid=2247483752&idx=1&sn=3180eeb628e091ce5abf1ec2559d1740&chksm=fe42688ec935e198b3fa5020c4b0ec85898efeaea28d94f7b57a66fe4f4c556e601651218bfa&scene=21#wechat_redirect)）

  3. 排查每次 YGC 后幸存对象大小（ JVM 模型基于分配的对象朝生夕死的假设设计，如果每次 YGC 后幸存对象较大，可能存在问题）
  4. 未完待续……（可以在留言中分享你的 idea）

排查每次 YGC 后幸存对象大小可通过 GC 日志中发生 YGC 的日志计算得出，例如下面两行 GC 日志，第二次 YGC 相比第一次 YGC，整个
Heap 并没有增长（都是647K），说明回收效果非常理想：

    
    
    2017-11-28T10:22:57.332+0800: [GC (Allocation Failure) 2017-11-28T10:22:57.332+0800: [ParNew: 7974K->0K(9216K), 0.0016636 secs] 7974K->647K(19456K), 0.0016865 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
    2017-11-28T10:22:57.334+0800: [GC (Allocation Failure) 2017-11-28T10:22:57.334+0800: [ParNew: 7318K->0K(9216K), 0.0002355 secs] 7965K->647K(19456K), 0.0002742 secs] [Times: user=0.00 sys=0.00, real=0.00 secs]
    

再看下面两行 GC 日志，第二次 YGC 相比第一次 YGC，整个 Heap 从 2707K 增长到了 4743K，说明回收效果不太理想，如果每次 YGC
时发现好几十 M 甚至上百 M 的对象幸存，那么可能需要着手排查了：

    
    
    2017-11-28T10:26:41.890+0800: [GC (Allocation Failure) 2017-11-28T10:26:41.890+0800: [ParNew: 7783K->657K(9216K), 0.0013021 secs] 7783K->2707K(19456K), 0.0013416 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
    2017-11-28T10:26:41.892+0800: [GC (Allocation Failure) 2017-11-28T10:26:41.892+0800: [ParNew: 7982K->0K(9216K), 0.0018354 secs] 10032K->4743K(19456K), 0.0018536 secs] [Times: user=0.00 sys=0.00, real=0.00 secs]
    

可参考的健康的GC状况给出建议YGC频率不超过2秒/次，经验值2秒~10秒/次都是比较合理的YGC频率；

  * 如果YGC频率远高于这个值，例如20秒/次，30秒/次，甚至60秒/次，这种情况下，说明JVM相当空闲，处于基本上无事可做的状态。建议缩容，减少服务器浪费；
  * 如果YoungGC频率远低于这个值，例如1秒/次，甚至1秒/好多次，这种情况下，JVM相当繁忙，建议follow如下步骤进行初步症断： 
    1. 检查Young区，Young区在整个堆占比在25%~40%比较合理，如果Young区太小，建议扩大Xmn。
    2. 检查SurvivorRatio，保持默认值8即可，Eden:S0:S1=8:1:1是一个比较合理的值；

### OldGC

上面已经提及：到目前为止 HotSpot JVM 虚拟机只单独回收 Old 区的只有CMS GC。触发CMS
GC条件比较简单，JVM有一个线程定时扫描Old区，时间间隔可以通过参数 **-XX:CMSWaitDuration**
设置（默认就是2s），扫描发现Old区占比超过参数 **-XX:CMSInitiatingOccupancyFraction**
设定值（CMS条件下默认为68%），就会触发CMS GC。建议搭配 **-XX:+UseCMSInitiatingOccupancyOnly**
参数使用，简化CMS GC触发条件， **只有** 在Old区占比满足 **-XX:CMSInitiatingOccupancyFraction**
条件的情况下才触发CMS GC；

可参考的健康的GC状况给出建议CMS GC频率不超过1天/次，如果CMS
GC频率1天发生数次，甚至上10次，说明你的GC情况病的不轻了，建议follow如下步骤进行初步症断：

  1. 检查Young区与Old区比值，尽量留60%以上的堆空间给Old区；
  2. 通过jstat查看每次YoungGC后晋升到Old区对象占比，如果发现每次YoungGC后Old区涨好几个百分点，甚至上10个点，说明有大对象，建议dump（参考`jmap -dump:format=b,file=app.bin pid`）后用MAT分析；
  3. 如果不停的CMS GC，Old区降不下去，建议先执行`jmap -histo pid | head -n10`查看TOP10对象分布，如果除了`[B和[C`，即byte[]和char[]，还有其他占比较大的实例，如下图所示中排名第一的Object数组，也可通过dump后用MAT分析问题；
  4. 如果TOP10对象中有 **StandartSession** 对象，排查你的业务代码中有没有显示使用 **HttpSession** ，例如`String id = request.getSession().getId();`，一般的OLTP系统都是无状态的，几乎不会使用 **HttpSession** ，且 **HttpSession** 的的生命周期很长，会加快Old区增长速度；

![201808221003](http://cmsblogs.qiniudn.com/wp-
content/uploads/2018/08/201808221003.jpg)

笔者曾经帮一位朋友排查过一个问题：他也是TOP对象中有 **StandartSession**
对象，并且占比较大，后面让他排查发现在接口中使用了HttpSession生成一个唯一ID，让他改成用UUID就解决了OldGC频繁的问题。

### FullGC

如果配置CMS，由于CMS采用标记清理算法，会有内存碎片的问题，推荐配置一个查看内存碎片程度的JVM参数： **PrintFLSStatistics** 。

如果配置ParallelOldGC，那么每次Old区满后，会触发FullGC，如果FullGC频率过高，也可以通过上面 **OldGC** 提及的排查方法；

如果没有配置`-XX:+DisableExplicitGC`，即没有屏蔽`System.gc()`触发FullGC，那么可以通过排查GC日志中有System字样判断是否由System.gc()触发，日志样本如下：

    
    
    558082.666: [Full GC (System) [PSYoungGen: 368K->0K(42112K)] [PSOldGen: 36485K->32282K(87424K)] 36853K->32282K(129536K) [PSPermGen: 34270K->34252K(196608K)], 0.2997530 secs]
    

或者通过`jstat -gccause pid 2s pid`判定， **LGCC** 表示最近一次GC原因，如果为 **System.gc**
，表示由System.gc()触发， **GCC** 表示当前GC原因，如果当前没有GC，那么就是No GC：

![201808221004](http://cmsblogs.qiniudn.com/wp-
content/uploads/2018/08/201808221004.jpg)

