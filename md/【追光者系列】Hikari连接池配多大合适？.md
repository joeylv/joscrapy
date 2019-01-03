  * 1 经验值&FlexyPool
  * 2 Less Is More
  * 3 Pool-locking 池锁
  * 4 具体问题具体分析
  * 5 参考资料

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

首先声明一下观点：How big should HikariCP be? Not how big but rather how
small！连接池的大小不是设置多大，不是越多越好，而是应该少到恰到好处。

本文提及的是客户端的线程池大小，数据库服务器另有不同的估算方法。

  1. 经验值&FlexyPool
  2. Less Is More  
2.1 公式：connections =（（core_count * 2）+ effective_spindle_count）  
2.2 公理：You want a small pool, saturated with threads waiting for connections.

  3. Pool-locking 池锁
  4. 具体问题具体分析

## 经验值&FlexyPool

我所在公司260多个应用的线上连接池默认经验值是如下配置的：

    
    
    maximumPoolSize: 20
    minimumIdle: 10
    
    

而Hikari的默认值是maximumPoolSize为10，而minimumIdle强烈建议不要配置、默认值与maximumPoolSize相同。我公司maximumPoolSize基本上这个值将决定到数据库后端的最大实际连接数，对此的合理价值最好由实际的执行环境决定；我公司保留minimumIdle的值（并不是不设置）是为了防止空闲很久时创建连接耗时较长从而影响RT。

不过我还是比较倾向作者的观点，尽量不要minimumIdle，允许HikariCP充当固定大小的连接池，毕竟我相信追求极致的Hikari一定可以尽最大努力快速高效地添加其他连接，从而获得最佳性能和响应尖峰需求

    
    
    minimumIdle 
    This property controls the minimum number of idle connections that HikariCP tries to maintain in the pool. If the idle connections dip below this value and total connections in the pool are less than maximumPoolSize, HikariCP will make a best effort to add additional connections quickly and efficiently. However, for maximum performance and responsiveness to spike demands, we recommend not setting this value and instead allowing HikariCP to act as a fixed size connection pool. Default: same as maximumPoolSize
    maximumPoolSize
    This property controls the maximum size that the pool is allowed to reach, including both idle and in-use connections. Basically this value will determine the maximum number of actual connections to the database backend. A reasonable value for this is best determined by your execution environment. When the pool reaches this size, and no idle connections are available, calls to getConnection() will block for up to connectionTimeout milliseconds before timing out. Please read about pool sizing. Default: 10
    

HikariCP
的初始版本只支持固定大小的池。作者初衷是，HikariCP是专门为具有相当恒定负载的系统而设计的，并且在倾向连接池大小于保持其运行时允许达到的最大大小，所以作者认为没有必要将代码复杂化以支持动态调整大小。毕竟你的系统会闲置很久么？另外作者认为配置项越多，用户配置池的难度就越大。但是呢，确实有一些用户需要动态调整连接池大小，并且没有就不行，所以作者就增加了这个功能。但是原则上，作者并不希望缺乏动态的大小支持会剥夺用户享受HikariCP的可靠性和正确性的好处。

如果想要支持动态调整不同负载的最佳池大小设置，可以配合Hikari使用同为the Mutual Admiration Society成员的Vlad
Mihalcea研究的FlexyPool。当然，连接池上限受到数据库最优并发查询容量的限制，这正是Hikari关于池大小的起作用的地方。然而，在池的最小值和最大值之间，FlexyPool不断尝试递增，确保该池大小在服务提供服务的过程中动态负载是一直正确的。

FlexyPool是一种reactive的连接池。其作者认为确定连接池大小不是前期设计决策的，在大型企业系统中，需要适应性和监控是做出正确决策的第一步。

FlexyPool具有以下默认策略

  * 在超时时递增池。此策略将增加连接获取超时时的目标连接池最大大小。连接池具有最小的大小，并可根据需要增长到最大大小。该溢出是多余的连接，让连接池增长超过其初始的缓冲区最大尺寸。每当检测到连接获取超时时，如果池未增长到其最大溢出大小，则当前请求将不会失败。
  * 重试尝试。此策略对于那些缺少连接获取重试机制的连接池非常有用。

由于本文主要谈Hikari，所以FlexyPool请各位读者自行阅读

<https://github.com/vladmihalcea/flexy-pool>

<https://vladmihalcea.com/>

<http://www.importnew.com/12342.html>

## Less Is More

众所周知，一个CPU核心的计算机可以同时执行数十或数百个线程，其实这只是操作系统的一个把戏-time-
slicing（时间切片）。实际上，该单核只能一次执行一个线程，然后操作系统切换上下文，并且该内核为另一个线程执行代码，依此类推。这是一个基本的计算法则，给定一个CPU资源，按顺序执行A和B
总是比通过时间片“同时” 执行A和B要快。一旦线程数量超过了CPU核心的数量，添加更多的线程就会变慢，而不是更快。

某用户做过测试（见参考资料），得到结论 **1个线程写10个记录比10个线程各写1个记录快**
。使用jvisualvm监控程序运行时，也可以看出来thread等待切换非常多。设计多线程是为了尽可能利用CPU空闲等待时间（等IO，等交互…），它的代价就是要增加部分CPU时间来实现线程切换。假如CPU空闲等待时间已经比线程切换更短，（线程越多，切换消耗越大）那么线程切换会非常影响性能，成为系统瓶颈。

其实还有一些因素共同作用，数据库的主要瓶颈是CPU，磁盘，网络（内存还不算最主要的）。

**公式：connections =（（core_count * 2）+ effective_spindle_count）**

effective_spindle_count is the number of disks in a RAID.就是磁盘列阵中的硬盘数，hard
disk.某PostgreSQL项目做过测试，一个硬盘的小型4核i7服务器连接池大小设置为： 9 = ((4 * 2) +
1)。这样的连接池大小居然可以轻松处理3000个前端用户在6000 TPS下运行简单查询。

我们公司线上机器标准是2核，有需求可以申请4核、8核，16核一般不开。虚拟机一般都是线程，宿主机一般是2个逻辑CPU。虚拟机默认就一块硬盘，物理机有十几块。

**公理：You want a small pool, saturated with threads waiting for connections.**

在公式的配置上，如果加大压力，TPS会下降，RT会上升，你可以适当根据情况进行调整加大。这时考虑整体系统性能，考虑线程执行需要的等待时间，设计合理的线程数目。但是，不要过度配置你的数据库。

## Pool-locking 池锁

增大连接池大小可以缓解池锁问题， **但是扩大池之前是可以先检查一下应用层面能够调优，不要直接调整连接池大小** 。

避免池锁是有一个公式的：

    
    
    pool size = Tn x (Cm - 1) + 1
    

T n是线程的最大数量，C m是单个线程持有的同时连接的最大数量。  
例如，设想三个线程`（T n = 3）`，每个线程需要四个连接来执行某个任务`（C m = 4）`。确保永不死锁的池大小是： `3 x（4 - 1）+ 1
= 10`。  
另一个例子，你最多有8个线程`（T n = 8）`，每个线程需要三个连接来执行一些任务`（C m = 3）`。确保死锁永远不可能的池大小是：
`8×（3-1）+ 1 = 17`

  * 这不一定是最佳池大小，但是是避免死锁所需的最低限度。
  * 在某些环境中，使用JTA（Java事务管理器）可以显着减少从同一个Connection返回getConnection()到当前事务中已经存储Connection的线程所需的连接数。

## 具体问题具体分析

混合了长时间运行事务和非常短的事务的系统通常是最难调整任何连接池的系统。在这些情况下，创建两个池实例可以很好地工作（例如，一个用于长时间运行的作业，另一个用于“实时”查询）。

如果长期运行的外部系统，例如只允许一定数量的作业同时运行的作业执行队列，这是作业队列大小就是连接池非常合适的大小。

最后，我要说的是：

**连接池大家是综合每个应用系统的业务逻辑特性，加上应用硬件配置，加上应用部署数量，再加上db硬件配置和最大允许连接数测试出来的。很难有一个简单公式进行计算。连接数及超时时间设置不正确经常会带来较大的性能问题，并影响整个服务能力的稳定性。具体设置多少，要看系统的访问量，可通过反复测试，找到最佳点。压测很重要。**

##  参考资料

<https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing>

<https://blog.csdn.net/cloud_ll/article/details/29212003>

