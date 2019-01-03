  * 1 模拟数据库挂掉
  * 2 allowPoolSuspension
  * 3 参考资料

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

由于时间原因，本文主要内容参考了[
https://segmentfault.com/a/1190000013136251](https://segmentfault.com/a/1190000013136251)
，并结合一些思考做了增注。

## 模拟数据库挂掉

首先解释一下connectionTimeout的意思，这并不是获取连接的超时时间，而是从连接池返回连接的超时时间。  
SQL执行的超时时间，JDBC 可以直接使用 Statement.setQueryTimeout，Spring 可以使用
@Transactional(timeout=10)。

> **connectionTimeout**  
>  This property controls the maximum number of milliseconds that a client
(that’s you) will wait for a connection from the pool. If this time is
exceeded without a connection becoming available, a SQLException will be
thrown. Lowest acceptable connection timeout is 250 ms. Default: 30000 (30
seconds)

如果是没有空闲连接且连接池满不能新建连接的情况下，hikari则是阻塞connectionTimeout的时间，没有得到连接抛出SQLTransientConnectionException。

如果是有空闲连接的情况，hikari是在connectionTimeout时间内不断循环获取下一个空闲连接进行校验，校验失败继续获取下一个空闲连接，直到超时抛出SQLTransientConnectionException。（hikari在获取一个连接的时候，会在connectionTimeout时间内循环把空闲连接挨个validate一次，最后timeout抛出异常；之后的获取连接操作，则一直阻塞connectionTimeout时间再抛出异常）

如果微服务使用了连接的健康监测，如果你catch了此异常，就会 **不断的打出健康监测的错误** 。

**hikari如果connectionTimeout设置太大的话，在数据库挂的时候，很容易阻塞业务线程**

根据以上结论我们撸一遍源码，首先看一下getConnection的源码，大致流程是如果borrow的poolEntry为空，就会跳出循环，抛异常，包括超时时间也会打出来如下：

    
    
    java.sql.SQLTransientConnectionException: communications-link-failure-db - Connection is not available, request timed out after 447794ms.
        at com.zaxxer.hikari.pool.HikariPool.createTimeoutException(HikariPool.java:666)
        at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:182)
        at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:147)</code> <code class="">/**
        * Get a connection from the pool, or timeout after the specified number of milliseconds.
        *
        * @param hardTimeout the maximum time to wait for a connection from the pool
        * @return a java.sql.Connection instance
        * @throws SQLException thrown if a timeout occurs trying to obtain a connection
        */
       public Connection getConnection(final long hardTimeout) throws SQLException {
          suspendResumeLock.acquire();
          final long startTime = currentTime();
          try {
             long timeout = hardTimeout;
             do {
                PoolEntry poolEntry = connectionBag.borrow(timeout, MILLISECONDS);
                if (poolEntry == null) {
                   break; // We timed out... break and throw exception
                }
                final long now = currentTime();
                if (poolEntry.isMarkedEvicted() || (elapsedMillis(poolEntry.lastAccessed, now) > ALIVE_BYPASS_WINDOW_MS && !isConnectionAlive(poolEntry.connection))) {
                   closeConnection(poolEntry, poolEntry.isMarkedEvicted() ? EVICTED_CONNECTION_MESSAGE : DEAD_CONNECTION_MESSAGE);
                   timeout = hardTimeout - elapsedMillis(startTime);
                }
                else {
                   metricsTracker.recordBorrowStats(poolEntry, startTime);
                   return poolEntry.createProxyConnection(leakTaskFactory.schedule(poolEntry), now);
                }
             } while (timeout > 0L);
             metricsTracker.recordBorrowTimeoutStats(startTime);
             throw createTimeoutException(startTime);
          }
          catch (InterruptedException e) {
             Thread.currentThread().interrupt();
             throw new SQLException(poolName + " - Interrupted during connection acquisition", e);
          }
          finally {
             suspendResumeLock.release();
          }
       }
    

我们聚焦一下borrow源码，该方法的意思和其注释所说的一样，The method will borrow a BagEntry from the bag,
blocking for the specified timeout if none are available.  
那么final T bagEntry = handoffQueue.poll(timeout, NANOSECONDS);
这段代码就是在数据库挂掉的情况下，会产生一段耗时的地方

    
    
    /**
        * The method will borrow a BagEntry from the bag, blocking for the
        * specified timeout if none are available.
        *
        * @param timeout how long to wait before giving up, in units of unit
        * @param timeUnit a <code>TimeUnit</code> determining how to interpret the timeout parameter
        * @return a borrowed instance from the bag or null if a timeout occurs
        * @throws InterruptedException if interrupted while waiting
        */
       public T borrow(long timeout, final TimeUnit timeUnit) throws InterruptedException
       {
          // Try the thread-local list first
          final List<Object> list = threadList.get();
          for (int i = list.size() - 1; i >= 0; i--) {
             final Object entry = list.remove(i);
             @SuppressWarnings("unchecked")
             final T bagEntry = weakThreadLocals ? ((WeakReference<T>) entry).get() : (T) entry;
             if (bagEntry != null && bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                return bagEntry;
             }
          }
          // Otherwise, scan the shared list ... then poll the handoff queue
          final int waiting = waiters.incrementAndGet();
          try {
             for (T bagEntry : sharedList) {
                if (bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                   // If we may have stolen another waiter"s connection, request another bag add.
                   if (waiting > 1) {
                      listener.addBagItem(waiting - 1);
                   }
                   return bagEntry;
                }
             }
             listener.addBagItem(waiting);
             timeout = timeUnit.toNanos(timeout);
             do {
                final long start = currentTime();
                final T bagEntry = handoffQueue.poll(timeout, NANOSECONDS);
                if (bagEntry == null || bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                   return bagEntry;
                }
                timeout -= elapsedNanos(start);
             } while (timeout > 10_000);
             return null;
          }
          finally {
             waiters.decrementAndGet();
          }
       }
    

这里使用了JUC的SynchronousQueue

    
    
    /**
         * Retrieves and removes the head of this queue, waiting
         * if necessary up to the specified wait time, for another thread
         * to insert it.
         *
         * @return the head of this queue, or {@code null} if the
         *         specified waiting time elapses before an element is present
         * @throws InterruptedException {@inheritDoc}
         */
        public E poll(long timeout, TimeUnit unit) throws InterruptedException {
            E e = transferer.transfer(null, true, unit.toNanos(timeout));
            if (e != null || !Thread.interrupted())
                return e;
            throw new InterruptedException();
        }
    

此时拿到空的poolEntry在getConnection中跳出循环，抛异常

HikariPool还有一个内部类叫PoolEntryCreator

    
    
    /**
        * Creating and adding poolEntries (connections) to the pool.
        */
       private final class PoolEntryCreator implements Callable<Boolean> {
          private final String loggingPrefix;
          PoolEntryCreator(String loggingPrefix)
          {
             this.loggingPrefix = loggingPrefix;
          }
          @Override
          public Boolean call() throws Exception
          {
             long sleepBackoff = 250L;
             while (poolState == POOL_NORMAL && shouldCreateAnotherConnection()) {
                final PoolEntry poolEntry = createPoolEntry();
                if (poolEntry != null) {
                   connectionBag.add(poolEntry);
                   LOGGER.debug("{} - Added connection {}", poolName, poolEntry.connection);
                   if (loggingPrefix != null) {
                      logPoolState(loggingPrefix);
                   }
                   return Boolean.TRUE;
                }
                // failed to get connection from db, sleep and retry
                quietlySleep(sleepBackoff);
                sleepBackoff = Math.min(SECONDS.toMillis(10), Math.min(connectionTimeout, (long) (sleepBackoff * 1.5)));
             }
             // Pool is suspended or shutdown or at max size
             return Boolean.FALSE;
          }
          /**
           * We only create connections if we need another idle connection or have threads still waiting
           * for a new connection.  Otherwise we bail out of the request to create.
           *
           * @return true if we should create a connection, false if the need has disappeared
           */
          private boolean shouldCreateAnotherConnection() {
             return getTotalConnections() < config.getMaximumPoolSize() &&
                (connectionBag.getWaitingThreadCount() > 0 || getIdleConnections() < config.getMinimumIdle());
          }
       }
    

shouldCreateAnotherConnection方法决定了是否需要添加新的连接

HikariPool初始化的时候会初始化两个PoolEntryCreator,分别是POOL_ENTRY_CREATOR和POST_FILL_POOL_ENTRY_CREATOR，是两个异步线程

    
    
    private final PoolEntryCreator POOL_ENTRY_CREATOR = new PoolEntryCreator(null /*logging prefix*/);
       private final PoolEntryCreator POST_FILL_POOL_ENTRY_CREATOR = new PoolEntryCreator("After adding ");
    

POOL_ENTRY_CREATOR主要是会被private final ThreadPoolExecutor
addConnectionExecutor;调用到，一处是fillPool,从当前的空闲连接(在执行时被感知到的)填充到minimumIdle（HikariCP尝试在池中维护的最小空闲连接数，如果空闲连接低于此值并且池中的总连接数少于maximumPoolSize，HikariCP将尽最大努力快速高效地添加其他连接）。  
补充新连接也会遭遇Connection refused相关的异常。

    
    
    /**
        * Fill pool up from current idle connections (as they are perceived at the point of execution) to minimumIdle connections.
        */
       private synchronized void fillPool() {
          final int connectionsToAdd = Math.min(config.getMaximumPoolSize() - getTotalConnections(), config.getMinimumIdle() - getIdleConnections())
                                       - addConnectionQueue.size();
          for (int i = 0; i < connectionsToAdd; i++) {
             addConnectionExecutor.submit((i < connectionsToAdd - 1) ? POOL_ENTRY_CREATOR : POST_FILL_POOL_ENTRY_CREATOR);
          }
       }
    

还有一处是addBagItem

    
    
    /** {@inheritDoc} */
       @Override
       public void addBagItem(final int waiting) {
          final boolean shouldAdd = waiting - addConnectionQueue.size() >= 0; // Yes, >= is intentional.
          if (shouldAdd) {
             addConnectionExecutor.submit(POOL_ENTRY_CREATOR);
          }
       }
    

最后再补充两个属性idleTimeout和minimumIdle

> **idleTimeout**  
>  This property controls the maximum amount of time that a connection is
allowed to sit idle in the pool. This setting only applies when minimumIdle is
defined to be less than maximumPoolSize. Idle connections will not be retired
once the pool reaches minimumIdle connections. Whether a connection is retired
as idle or not is subject to a maximum variation of +30 seconds, and average
variation of +15 seconds. A connection will never be retired as idle before
this timeout. A value of 0 means that idle connections are never removed from
the pool. The minimum allowed value is 10000ms (10 seconds). Default: 600000
(10 minutes)

默认是600000毫秒，即10分钟。如果idleTimeout+1秒>maxLifetime 且
maxLifetime>0，则会被重置为0；如果idleTimeout!=0且小于10秒，则会被重置为10秒。如果idleTimeout=0则表示空闲的连接在连接池中永远不被移除。

只有当minimumIdle小于maximumPoolSize时，这个参数才生效，当空闲连接数超过minimumIdle，而且空闲时间超过idleTimeout，则会被移除。

> **minimumIdle**  
>  This property controls the minimum number of idle connections that HikariCP
tries to maintain in the pool. If the idle connections dip below this value
and total connections in the pool are less than maximumPoolSize, HikariCP will
make a best effort to add additional connections quickly and efficiently.
However, for maximum performance and responsiveness to spike demands, we
recommend not setting this value and instead allowing HikariCP to act as a
fixed size connection pool. Default: same as maximumPoolSize

控制连接池空闲连接的最小数量，当连接池空闲连接少于minimumIdle，而且总共连接数不大于maximumPoolSize时，HikariCP会尽力补充新的连接。为了性能考虑，不建议设置此值，而是让HikariCP把连接池当做固定大小的处理，默认minimumIdle与maximumPoolSize一样。

当minIdlemaxPoolSize,则被重置为maxPoolSize，该值默认为10。

Hikari会启动一个HouseKeeper定时任务，在HikariPool构造器里头初始化，默认的是初始化后100毫秒执行，之后每执行完一次之后隔HOUSEKEEPING_PERIOD_MS(30秒)时间执行。

这个定时任务的作用就是根据idleTimeout的值，移除掉空闲超时的连接。  
首先检测时钟是否倒退，如果倒退了则立即对过期的连接进行标记evict；之后当idleTimeout>0且配置的minimumIdle<maximumPoolSize时才开始处理超时的空闲连接。

取出状态是STATE_NOT_IN_USE的连接数，如果大于minimumIdle，则遍历STATE_NOT_IN_USE的连接的连接，将空闲超时达到idleTimeout的连接从connectionBag移除掉，若移除成功则关闭该连接，然后toRemove–。

在空闲连接移除之后，再调用fillPool，尝试补充空间连接数到minimumIdle值

hikari的连接泄露是每次getConnection的时候单独触发一个延时任务来处理，而空闲连接的清除则是使用HouseKeeper定时任务来处理，其运行间隔由com.zaxxer.hikari.housekeeping.periodMs环境变量控制，默认为30秒。

## allowPoolSuspension

关于这个参数，用来标记释放允许暂停连接池，一旦被暂停，所有的getConnection方法都会被阻塞。

作者是这么说的：  
https://github.com/brettwooldridge/HikariCP/issues/1060

All of the suspend use cases I have heard have centered around a pattern of:

  * Suspend the pool. 
    * Alter the pool configuration, or alter DNS configuration (to point to a new master). 
    * Soft-evict existing connections.

    * Resume the pool.

我做过试验，Suspend期间getConnection确实不会超时，SQL执行都会被保留下来，软驱除现有连接之后，一直保持到池恢复Resume时，这些SQL依然会继续执行，也就是说用户并不会丢数据。  
但是在实际生产中，不影响业务很难，即使继续执行，业务也可能超时了。  
故障注入是中间件开发应该要做的，这个点的功能在实现chaosmonkey以模拟数据库连接故障，但是监控过程中我发现hikaricp_pending_threads指标并没有提升、MBean的threadAwaitingConnections也没有改变，所以包括故障演练以后也可以不用搞得那么复杂，收拢在中间件内部做可能更好，前提是对于这个参数，中间件还需要自研以增加模拟抛异常或是一些监控指标进行加强。  
另外， **长期阻塞该参数存在让微服务卡死的风险** 。

详细推荐看一下
[【追光者系列】HikariCP源码分析之allowPoolSuspension](http://mp.weixin.qq.com/s?__biz=MzUzNTY4NTYxMA==&mid=2247483735&idx=1&sn=d8ed8446ebc5e3c3df02afb2c6c3ed77&chksm=fa80f1d2cdf778c4da61d53d37aa7123d603fc1a4abe0804cc7c03c20f83d91436301deb3fa6&scene=21#wechat_redirect)

## 参考资料

  * <https://segmentfault.com/u/codecraft/articles?page=4>

