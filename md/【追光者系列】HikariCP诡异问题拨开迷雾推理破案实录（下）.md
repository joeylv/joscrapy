  * 1 直奔疑点
  * 2 拨开迷雾
  * 3 守株待兔
  * 4 抽丝剥茧
  * 5 柳暗花明
  * 6 真相大白

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

* * *

本文是
[【追光者系列】HikariCP诡异问题拨开迷雾推理破案实录（上）](http://mp.weixin.qq.com/s?__biz=MzUzNTY4NTYxMA==&mid=2247483827&idx=1&sn=9780254dc2f07caac8dcdf8405738e71&chksm=fa80f136cdf778208341bdeab66aa8ac8985b7e6eea577743a99082c56d42c00b03e96d6a22d&scene=21#wechat_redirect)的下半部分

# 直奔疑点

首先我直接怀疑是不是数据库断掉了连接，于是登上了数据库查询了数据库参数，结果是没毛病。

为了稳妥起见，我又咨询了DBA，DBA说线下环境和线上环境参数一样，并帮我看了，没有任何问题。

![2018050412001](http://cmsblogs.qiniudn.com/2018050412001.jpg)

为什么我直接奔向这个疑点，因为《Solr权威指南》的作者兰小伟大佬曾经和我分享过一个案例：他前段时间也遇到类似的问题，他用的是c3p0，碰到和我一样的碰到一样的exception，那个异常是服务器主动关闭了链接，而客户端还拿那个链接去操作，大佬加个testQuery，保持心跳即可解决。c3p0设置一个周期，是定时主动检测的。

估计是mysql服务器端链接缓存时间设置的太短，服务器端主动销毁了链接，一般做法是客户端连接池配置testQuery。  
testQuery我觉得比较影响hikariCP的性能，所以我决定跟一下源码了解一下原理并定位问题。

# 拨开迷雾

按着上一篇的推测，我们在Hikari核心源码中打一些日志记录。

第一处，在com.zaxxer.hikari.pool.HikariPool#getConnection中增加IDEA log expression

    
    
    public Connection getConnection(final long hardTimeout) throws SQLException {
          suspendResumeLock.acquire();
          final long startTime = currentTime();
          try {
             long timeout = hardTimeout;
             PoolEntry poolEntry = null;
             try {
                do {
                   poolEntry = connectionBag.borrow(timeout, MILLISECONDS);
                   if (poolEntry == null) {
                      break; // We timed out... break and throw exception
                   }
                   final long now = currentTime();
                   if (poolEntry.isMarkedEvicted() || (elapsedMillis(poolEntry.lastAccessed, now) > ALIVE_BYPASS_WINDOW_MS && !isConnectionAlive(poolEntry.connection))) {
                      closeConnection(poolEntry, "(connection is evicted or dead)"); // Throw away the dead connection (passed max age or failed alive test)
                      timeout = hardTimeout - elapsedMillis(startTime);
                   }
                   else {
                      metricsTracker.recordBorrowStats(poolEntry, startTime);
                      return poolEntry.createProxyConnection(leakTask.schedule(poolEntry), now);
                   }
                } while (timeout > 0L);
                metricsTracker.recordBorrowTimeoutStats(startTime);
             }
             catch (InterruptedException e) {
                if (poolEntry != null) {
                   poolEntry.recycle(startTime);
                }
                Thread.currentThread().interrupt();
                throw new SQLException(poolName + " - Interrupted during connection acquisition", e);
             }
          }
          finally {
             suspendResumeLock.release();
          }
          throw createTimeoutException(startTime);
       }
    

我们对于直接抛异常的代码的条件判断入口处增加调试信息

    
    
    if (poolEntry.isMarkedEvicted() || (elapsedMillis(poolEntry.lastAccessed, now) > ALIVE_BYPASS_WINDOW_MS && !isConnectionAlive(poolEntry.connection)))</code> <code class="">String.format("Evicted: %s; enough time elapse: %s;poolEntrt: %s;", poolEntry.isMarkedEvicted(), elapsedMillis(poolEntry.lastAccessed, now) > ALIVE_BYPASS_WINDOW_MS,poolEntry);
    

第二处、在com.zaxxer.hikari.pool.HikariPool#softEvictConnection处增加调试信息

    
    
    private boolean softEvictConnection(final PoolEntry poolEntry, final String reason, final boolean owner) {
          poolEntry.markEvicted();
          if (owner || connectionBag.reserve(poolEntry)) {
             closeConnection(poolEntry, reason);
             return true;
          }
          return false;
       }
       
       String.format("Scheduled soft eviction for connection %s is due; owner %s is;", poolEntry.connection,owner)
    

为什么要打在softEvictConnection这里呢？因为在createPoolEntry的时候注册了一个延时任务，并通过poolEntry.setFutureEol设置到poolEntry中  
softEvictConnection，首先标记markEvicted。然后如果是用户自己调用的，则直接关闭连接；如果从connectionBag中标记不可borrow成功，则关闭连接。

这个定时任务是在每次createPoolEntry的时候，根据maxLifetime随机设定一个variance，在maxLifetime –
variance之后触发evict。

    
    
      /**
        * Creating new poolEntry.
        */
       private PoolEntry createPoolEntry() {
          try {
             final PoolEntry poolEntry = newPoolEntry();
             final long maxLifetime = config.getMaxLifetime();
             if (maxLifetime > 0) {
                // variance up to 2.5% of the maxlifetime
                final long variance = maxLifetime > 10_000 ? ThreadLocalRandom.current().nextLong( maxLifetime / 40 ) : 0;
                final long lifetime = maxLifetime - variance;
                poolEntry.setFutureEol(houseKeepingExecutorService.schedule(
                   () -> {
                      if (softEvictConnection(poolEntry, "(connection has passed maxLifetime)", false /* not owner */)) {
                         addBagItem(connectionBag.getWaitingThreadCount());
                      }
                   },
                   lifetime, MILLISECONDS));
             }
             return poolEntry;
          }
          catch (Exception e) {
             if (poolState == POOL_NORMAL) {
                LOGGER.debug("{} - Cannot acquire connection from data source", poolName, (e instanceof ConnectionSetupException ? e.getCause() : e));
             }
             return null;
          }
       }
    

# 守株待兔

做了如上处理之后我们就安心得等结果

![2018050412002](http://cmsblogs.qiniudn.com/2018050412002.jpg)

很快来了一组数据，我们可以看到确实poolEntry.isMarkedEvicted()一直都是false,(elapsedMillis(poolEntry.lastAccessed,
now) > ALIVE_BYPASS_WINDOW_MS这个判断为true。

sharedlist 是 CopyOnWriteArrayList，每次getConnection都是数组首

![2018050412003](http://cmsblogs.qiniudn.com/2018050412003.jpg)

![2018050412004](http://cmsblogs.qiniudn.com/2018050412004.jpg)

softEvictConnection这里的信息在20分钟到了的时候也出现了

![2018050412005](http://cmsblogs.qiniudn.com/2018050412005.jpg)

从这张图我们可以看到，owner是false，第一个触发定时任务的也正好是第一个连接。删除的那个就是每次微服务健康检测healthcheck连接用的那个。

![2018050412006](http://cmsblogs.qiniudn.com/2018050412006.jpg)

我仔细数了一下，确实一共创建了十次SSL，也就是本次周期确实重新连了十次数据库TCP连接。那么问题来了，为什么每次正好是8次或者9次异常日志？

# 抽丝剥茧

定时任务的执行时间是多少？

这个定时任务是在每次createPoolEntry的时候，根据maxLifetime随机设定一个variance，在maxLifetime –
variance之后触发evict。  
maxLifetime我现在设置的是20分钟，

    
    
    // variance up to 2.5% of the maxlifetime
                final long variance = maxLifetime > 10_000 ? ThreadLocalRandom.current().nextLong( maxLifetime / 40 ) : 0;
                final long lifetime = maxLifetime - variance
    

按照20分钟1200秒来算，这个evict的操作是1170秒左右,按理说离20分钟差30秒左右。

但是通过观察，好像第一个连接创建的时间比其他连接快 4 秒。

![2018050412007](http://cmsblogs.qiniudn.com/2018050412007.jpg)

也就是说时间上被错开了，本来10个连接是相近的时间close的，第一个连接先被定时器close了，其他连接是getconnection的时候close的，这样就造成了一个循环。其他连接是getconnection的时候几乎同时被关闭的，就是哪些warn日志出现的时候。

这猜想和我debug得到的结果是一致的，第一个getConnection健康监测是被定时器close的，close之后立马fillpool，所以warn的是小于10的。和我们看到的历史数据一样，8为主，也有9。

![2018050412008](http://cmsblogs.qiniudn.com/2018050412008.jpg)

定时器close之后的那个新连接，会比其他的连接先进入定时器的调度，其他的9个被循环报错关闭。

![2018050412009](http://cmsblogs.qiniudn.com/2018050412009.jpg)

getconnection时报错关闭的那些连接，跟被定时器关闭的连接的定时器时间错开，如上图所示，有两个连接已经处于remove的状态了。

9次是比较好解释的，第一个连接是同步创建的，构造函数里调用checkFailFast会直接建一个连接，其他连接是
housekeeper里异步fillpool创建的。

做了一次测试，这一波果然打了9次日志

![20180504120010](http://cmsblogs.qiniudn.com/20180504120010.jpg)

那么9次就可以这么合理的解释了。

8次的解释应该就是如上图所示2个已经被remove掉的可能性情况。

# 柳暗花明

这时小手一抖，netstat了一把

![20180504120011](http://cmsblogs.qiniudn.com/20180504120011.jpg)

![20180504120012](http://cmsblogs.qiniudn.com/20180504120012.jpg)

发现很快就closewait了，而closewait代表已经断开了，基本不能再用了。其实就是被对方断开了。

这时我又找了DBA，告诉他我得到的结论，DBA再次帮我确认之后，焦急的等待以后，屏幕那头给我这么一段回复：

![20180504120013](http://cmsblogs.qiniudn.com/20180504120013.jpg)

这时叫了一下配置中心的同学一起看了一下这个数据库的地址，一共有5个配置连到了这个废弃的proxy，和我们线上出问题的数目和应用基本一致！

配置中心的同学和DBA说这个proxy曾经批量帮业务方改过，有些业务方居然又改回去了。。。。这时业务方的同学也说话了，“难怪我navicate
在proxy上edit一个表要等半天。。stable环境就秒出”

# 真相大白

修改了这个废弃的proxy改为真正的数据库地址以后，第二天业务方的同学给了我们反馈：

![20180504120014](http://cmsblogs.qiniudn.com/20180504120014.jpg)

图左边2个绿色箭头，下面那个是调整过配置的环境，上面是没有调整的，调整过的今天已经没有那个日志了，那17.6%是正常的业务日志。

