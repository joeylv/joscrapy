  * 1 问题描述
  * 2 望闻问切
  * 3 brettw如是说
  * 4 Be MECE
  * 5 大胆猜想
  * 6 拨开迷雾

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

* * *

# 问题描述

2018年4月19日早上，有业务方反馈每半小时都会打出如下异常：

    
    
    HikariPool-1 - Failed to validate connection com.mysql.jdbc.JDBC4Connection@7174224b (No operations allowed after connection closed.)
    

业务方的需求是：这种日志需要配置能够消除？我能如何调优参数才能关闭这些日志？是不是我的hikariCP的connectionTimeout是不是每个业务的查询超时时间？

首先解释一下connectionTimeout的意思，这并不是获取连接的超时时间，而是从连接池返回连接的超时时间。SQL执行的超时时间，JDBC
可以直接使用 Statement.setQueryTimeout，Spring 可以使用@Transactional(timeout=10)。

维护HikariCP相关的中间件也有8个月的时间了，我知道该异常其实是不影响业务的，但是这8个月期间经常不断的有业务方咨询同一个问题，所以我觉得很有必要认真地梳理一下该问题源码级的具体原理及根本原因来给业务方一个合理的交代。

# 望闻问切

进行了一波详细的勘查，又拿到了如下信息

  * 该业务没有上线，在线下环境暴露出的问题
  * 线上服务查了几个服务没有这样的问题
  * 业务方一开始说线下环境50～100QPS，但是实际业务方并没有调用
  * springboot微服务的health check我司每10秒执行一次，可以理解为进行一次getConnection操作
  * 业务方没有做任何配置，hikariCP的默认maxLifetime是30分钟，和业务方的表象吻合
  * **波及业务线下扫出了五个应用有同样的问题**
  * 拉取业务方代码debug，maxLifetime调整为20分钟，该异常也平均是20分钟输出一次
  * hikariCP的maximumPoolSize为10，按理说异常也应该是10，但是实际是大多落在8左右，也有可能是9，极小情况是11。当调小maxLifetime为一分钟时，异常数目每阶段时间出现暴增现象。

采用了kibana协助排查问题，得到的信息如下：

如下图所示，平均每半小时出现一波异常，规律性很强，20:00时由于我将maxLifetime调整为一分钟，异常数目飙升，之后我把maxLifetime调整为二十分钟，就呈现出每20分钟出现一波异常

    
    
    HikariPool-1 - Failed to validate connection com.mysql.jdbc.JDBC4Connection@7174224b (No operations allowed after connection closed.) 
    

![201805041101](http://cmsblogs.qiniudn.com/201805041101.jpg)

具体异常我抽样以后展示如下，按照时间倒序排列，之前是默认30分钟，后面调整为20分钟：

![201805041102](http://cmsblogs.qiniudn.com/201805041102.jpg)

![201805041104](http://cmsblogs.qiniudn.com/201805041104.jpg)

![201805041105](http://cmsblogs.qiniudn.com/201805041105.jpg)

# brettw如是说

在stackoverflow已经有用户提出了同样类似的问题：

https://stackoverflow.com/questions/41008350/no-operations-allowed-after-
connection-closed-errors-in-slick-hikaricp

![201805041106](http://cmsblogs.qiniudn.com/201805041106.jpg)

该用户每3秒运行一次查询，每次查询的时间都小于0.4s。起初一切运行正常，但大约2小时后，HikariCP开始关闭连接，导致关于’no operations
allowed after connection closed’的错误：

    
    
    15:20:38.288 DEBUG [] [rdsConfig-8] com.zaxxer.hikari.pool.HikariPool - rdsConfig - Timeout failure stats (total=30, active=0, idle=30, waiting=0)
    15:20:38.290 DEBUG [] [rdsConfig connection closer] com.zaxxer.hikari.pool.PoolBase - rdsConfig - Closing connection com.mysql.jdbc.JDBC4Connection@229960c: (connection is evicted or dead)
    15:20:38.333 DEBUG [] [rdsConfig connection closer] com.zaxxer.hikari.pool.PoolBase - rdsConfig - Closing connection com.mysql.jdbc.JDBC4Connection@229960c failed
    com.mysql.jdbc.exceptions.jdbc4.MySQLNonTransientConnectionException: No operations allowed after connection closed.
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method) ~[na:1.8.0_77]
        at sun.reflect.NativeConstructorAccessorImpl.newInstance(Unknown Source) ~[na:1.8.0_77]
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(Unknown Source) ~[na:1.8.0_77]
        at java.lang.reflect.Constructor.newInstance(Unknown Source) ~[na:1.8.0_77]
    

该用户也是期望怎么配置来避免此情况？这和我的业务方的诉求是完全一致的。该用户并不理解HikariCP关闭连接的原理，非常困惑。所以我们很有必要给用户一个交代。

作者表示，HikariCP在使用时不会关闭连接。如果使用中的连接到达，maxLifetime它将被标记为驱逐，并且在下一次线程尝试借用它时将被驱逐。

![201805041107](http://cmsblogs.qiniudn.com/201805041107.jpg)

如上图所示，作者说明在五种情况下HikariCP会关闭连接，分别是连接验证失败、连接闲置时间超过idleTimeout、一个连接到达了它maxLifetime、用户手动驱逐连接、一个JDBC调用抛出一个不可恢复的
SQLException。每一种情况都会打印不一样的异常，

有人去看医生，说他拉肚子了，那医生能开一样的药么？引起腹泻原因很多,比如肚子受凉、饮食不卫生、消化不良、食物过敏、感染病毒。针对不同的症状要采用不同的治疗手段。

同理，虽然都是No operations allowed after connection closed，该用户是打出了connection is
evicted or dead，属于第三种情况 **A connection reached its maxLifetime**
，而我们的异常是这样的，和该用户的提问其实不一样的，我们命中的是第一种情况 **The connection failed validation**

    
    
    HikariPool-1 - Failed to validate connection com.mysql.jdbc.JDBC4Connection@50962fdc (No operations allowed after connection closed.)
    

作者提及This is invisible to your application.这对应用程序是不可见的，可见这不是一个问题。  
但是总让业务方打日志也不是一个办法？不给业务方一个交代也是不行的。更何况只有线下才有这样频繁的日志，线上是没有的，这其中必有猫腻。

# Be MECE

曾经读过一篇文章提及了 Be MECE  
**MECE取自“Mutually Exclusive Collectively Exhaustive”** ，中文意思是相互独立，完全穷尽，发音读作“Me
See”。起源于麦肯锡的一位资深咨询顾问巴巴拉·明托，她在《金字塔原理》中第一次将这个概念提出，成为后来战略咨询行业的重要原则之一。

相互独立，意味着将能够影响问题的原因拆分成有明确区分，互不重叠的各个因素。完全穷尽，意味着全面周密，毫无遗漏。

通常运用MECE都是从一个最高层的问题开始，逐层向下进行分解。首先列出你亟待解决的问题，然后将问题拆分成子问题，并保证它们之间互不重叠和干扰。同时保证你把能够想到的子问题全部列了出来。

实际运用中你只用不停问自己两个问题：

  1. 我是不是把所有的可能因素都考虑到了，有没有遗漏的？如果有，再去找。
  2. 这些因素之间有没有互相重叠的部分？如果有，进行去重。

举个例子，比如你现在遇到的问题是：“我该不该现在跳槽？” 那么对这个问题的分解可以如下图所示：

![201805041108](http://cmsblogs.qiniudn.com/201805041108.jpg)

那我们按照这个思路也来分解一下：

  1. 是不是这几个服务依赖的中间件版本不同导致的？
  2. 是不是数据库给断掉了？
  3. 两种情况：被外部关闭了、有代码操作了内部的connection对象，是哪种情况干的？
  4. 异常是哪里抛出来的？

针对这些疑点，我们来分析一下：

  1. 半年来经常有业务方咨询此问题，根据出问题的五个应用，发现分布在三种主流版本里
  2. 登陆业务方数据库，show variables like ‘%timeout%’，发现mysql参数并没有问题，咨询了DBA，线下也没有做什么修改
  3. 基本可以排除第一种情况，操作了内部的connection对象可能性比较大
  4. 异常是setNetworkTimeout里面抛出来的，实现类是JDBC4Connection connectionimpl ping的时候报错了。mysql把isvalid方法里的错误吃掉了比较坑，isvalid方法里面报错了会调用close方法，然后hikari外层又调了一次settimeout就触发了这个warn

![201805041109](http://cmsblogs.qiniudn.com/201805041109.jpg)

# 大胆猜想

![201805041110](http://cmsblogs.qiniudn.com/201805041110.png)

  1. HikariCP使用List来保存打开的Statement，当Statement关闭或Connection关闭时需要将对应的Statement从List中移除。FastList是从数组的尾部开始遍历。CopyOnWriteArrayList负责存放ConcurrentBag中全部用于出借的资源，getConnection方法borrow正是ConcurrentBag的CopyOnWriteArrayList，copyonwrite是拿的数组首。所以健康检测下低QPS下连接池取出对象永远是从CopyOnWriteArrayList sharedList数组的首部取出的那个？
  2. 结合第一点猜想，数组中的其他连接（除了队首的），可能在10～20分钟之内已经被mysql断掉了？
  3. 需要把源码中核心操作流程里的对象都打印出来，去观察拿到更多的信？
  4. 一分钟没事，20分钟 30分钟有事，是不是因为一分钟数据库没有断掉？而20～30分钟的却已经断掉了？需要结合mysql的信息去看
  5. 线上高QPS所有连接都处于和数据库活跃的连接及切换状态，所以异常远远小于线下的原因是，只有数组首部取出的那个和数据库交互的流程？
  6. 数组首以外的一些连接是否被内部的connection操作了

# 拨开迷雾

鉴于篇幅原因，请大家关注明天更新的第二篇《【追光者系列】HikariCP诡异问题拨开迷雾推理破案实录（下）》，敬请期待！

