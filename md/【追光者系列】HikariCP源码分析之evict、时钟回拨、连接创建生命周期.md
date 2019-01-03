  * 1 概念
  * 2 getConnection
  * 3 createPoolEntry
  * 4 evict Related
    * 4.1 evictConnection
    * 4.2 softEvictConnection
    * 4.3 softEvictConnections
  * 5 Hikari物理连接取用生命周期
  * 6 参考资料

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

* * *

# 概念

evict定义在com.zaxxer.hikari.pool.PoolEntry中，evict的汉语意思是驱逐、逐出，用来标记连接池中的连接不可用。

    
    
    private volatile boolean evict;
    boolean isMarkedEvicted() {
          return evict;
       }
       void markEvicted() {
          this.evict = true;
       }
    

# getConnection

在每次getConnection的时候，borrow连接（PoolEntry）的时候，如果是标记evict的，则会关闭连接，更新timeout的值，重新循环继续获取连接

    
    
     /**
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
    

如下我们聚焦一下源码，hardTimeout默认值是30000，这个值实际上就是connectionTimeout，构造器默认值是SECONDS.toMillis(30)
= 30000，默认配置validate之后的值是30000，validate重置以后是如果小于250毫秒，则被重置回30秒。

> **connectionTimeout**  
>  This property controls the maximum number of milliseconds that a client
(that’s you) will wait for a connection from the pool. If this time is
exceeded without a connection becoming available, a SQLException will be
thrown. Lowest acceptable connection timeout is 250 ms. Default: 30000 (30
seconds)

    
    
    if (poolEntry.isMarkedEvicted() || (elapsedMillis(poolEntry.lastAccessed, now) > ALIVE_BYPASS_WINDOW_MS && !isConnectionAlive(poolEntry.connection))) {
                   closeConnection(poolEntry, poolEntry.isMarkedEvicted() ? EVICTED_CONNECTION_MESSAGE : DEAD_CONNECTION_MESSAGE);
                   timeout = hardTimeout - elapsedMillis(startTime);
                }
    

关闭连接这块的源码如下，从注释可以看到（阅读hikari源码强烈建议看注释），这是永久关闭真实（底层）连接（吃掉任何异常）：

    
    
     private static final String EVICTED_CONNECTION_MESSAGE = "(connection was evicted)";
       private static final String DEAD_CONNECTION_MESSAGE = "(connection is dead)";
       /**
        * Permanently close the real (underlying) connection (eat any exception).
        *
        * @param poolEntry poolEntry having the connection to close
        * @param closureReason reason to close
        */
       void closeConnection(final PoolEntry poolEntry, final String closureReason) {
          if (connectionBag.remove(poolEntry)) {
             final Connection connection = poolEntry.close();
             closeConnectionExecutor.execute(() -> {
                quietlyCloseConnection(connection, closureReason);
                if (poolState == POOL_NORMAL) {
                   fillPool();
                }
             });
          }
       }
    

吃掉体现在quietlyCloseConnection,这是吃掉Throwable的

    
    
    // ***********************************************************************
       //                           JDBC methods
       // ***********************************************************************
       void quietlyCloseConnection(final Connection connection, final String closureReason) {
          if (connection != null) {
             try {
                LOGGER.debug("{} - Closing connection {}: {}", poolName, connection, closureReason);
                try {
                   setNetworkTimeout(connection, SECONDS.toMillis(15));
                }
                finally {
                   connection.close(); // continue with the close even if setNetworkTimeout() throws
                }
             }
             catch (Throwable e) {
                LOGGER.debug("{} - Closing connection {} failed", poolName, connection, e);
             }
          }
       }
    

![2018042710001](http://cmsblogs.qiniudn.com/2018042710001.jpeg)

# createPoolEntry

这段代码强烈建议看一下注释，maxLifetime默认是1800000=30分钟，就是让每个连接的最大存活时间错开一点，防止同时过期，加一点点随机因素，防止一件事情大量同时发生（C大语录）。

    
    
    // ***********************************************************************
       //                           Private methods
       // ***********************************************************************
       /**
        * Creating new poolEntry.  If maxLifetime is configured, create a future End-of-life task with 2.5% variance from
        * the maxLifetime time to ensure there is no massive die-off of Connections in the pool.
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
             if (poolState == POOL_NORMAL) { // we check POOL_NORMAL to avoid a flood of messages if shutdown() is running concurrently
                LOGGER.debug("{} - Cannot acquire connection from data source", poolName, (e instanceof ConnectionSetupException ? e.getCause() : e));
             }
             return null;
          }
       }
    

如果maxLifetime大于10000就是大于10秒钟，就走这个策略，用maxLifetime的2.5%的时间和0之间的随机数来随机设定一个variance，在maxLifetime
– variance之后触发evict。  
在创建poolEntry的时候，注册一个延时任务，在连接存活将要到达maxLifetime之前触发evit，用来防止出现大面积的connection因maxLifetime同一时刻失效。  
标记为evict只是表示连接池中的该连接不可用，但还在连接池当中，还会被borrow出来，只是getConnection的时候判断了，如果是isMarkedEvicted，则会从连接池中移除该连接，然后close掉。

# evict Related

## evictConnection

可以主动调用evictConnection，这里也是判断是不是用户自己调用的或者从connectionBag中标记不可borrow成功，则关闭连接

    
    
    /**
        * Evict a Connection from the pool.
        *
        * @param connection the Connection to evict (actually a {@link ProxyConnection})
        */
       public void evictConnection(Connection connection) {
          ProxyConnection proxyConnection = (ProxyConnection) connection;
          proxyConnection.cancelLeakTask();
          try {
             softEvictConnection(proxyConnection.getPoolEntry(), "(connection evicted by user)", !connection.isClosed() /* owner */);
          }
          catch (SQLException e) {
             // unreachable in HikariCP, but we"re still forced to catch it
          }
       }
    

## softEvictConnection

    
    
     /**
        * "Soft" evict a Connection (/PoolEntry) from the pool.  If this method is being called by the user directly
        * through {@link com.zaxxer.hikari.HikariDataSource#evictConnection(Connection)} then {@code owner} is {@code true}.
        *
        * If the caller is the owner, or if the Connection is idle (i.e. can be "reserved" in the {@link ConcurrentBag}),
        * then we can close the connection immediately.  Otherwise, we leave it "marked" for eviction so that it is evicted
        * the next time someone tries to acquire it from the pool.
        *
        * @param poolEntry the PoolEntry (/Connection) to "soft" evict from the pool
        * @param reason the reason that the connection is being evicted
        * @param owner true if the caller is the owner of the connection, false otherwise
        * @return true if the connection was evicted (closed), false if it was merely marked for eviction
        */
       private boolean softEvictConnection(final PoolEntry poolEntry, final String reason, final boolean owner) {
          poolEntry.markEvicted();
          if (owner || connectionBag.reserve(poolEntry)) {
             closeConnection(poolEntry, reason);
             return true;
          }
          return false;
       }
    

**com.zaxxer.hikari.util.ConcurrentBag**

    
    
     /**
        * The method is used to make an item in the bag "unavailable" for
        * borrowing.  It is primarily used when wanting to operate on items
        * returned by the <code>values(int)``` method.  Items that are
        * reserved can be removed from the bag via <code>remove(T)```
        * without the need to unreserve them.  Items that are not removed
        * from the bag can be make available for borrowing again by calling
        * the <code>unreserve(T)``` method.
        *
        * @param bagEntry the item to reserve
        * @return true if the item was able to be reserved, false otherwise
        */
       public boolean reserve(final T bagEntry) {
          return bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_RESERVED);
       }
    

##  softEvictConnections

HikariPool中还提供了HikariPoolMXBean的softEvictConnections实现，实际上是调用softEvictConnection，owner指定false（
not owner ）

    
    
     public void softEvictConnections() {
          connectionBag.values().forEach(poolEntry -&gt; softEvictConnection(poolEntry, "(connection evicted)", false /* not owner */));
       }
    

Mbean的softEvictConnections方法真正执行的是com.zaxxer.hikari.pool.HikariPool中softEvictConnections方法，这是一种“软”驱逐池中连接的方法，如果调用方是owner身份，或者连接处于空闲状态，可以立即关闭连接。否则，我们将其“标记”为驱逐，以便下次有人试图从池中获取它时将其逐出。

    
    
    public void softEvictConnections() {
          connectionBag.values().forEach(poolEntry -&gt; softEvictConnection(poolEntry, "(connection evicted)", false /* not owner */));
       }
    

**softEvictConnection**

    
    
    /**
        * "Soft" evict a Connection (/PoolEntry) from the pool.  If this method is being called by the user directly
        * through {@link com.zaxxer.hikari.HikariDataSource#evictConnection(Connection)} then {@code owner} is {@code true}.
        *
        * If the caller is the owner, or if the Connection is idle (i.e. can be "reserved" in the {@link ConcurrentBag}),
        * then we can close the connection immediately.  Otherwise, we leave it "marked" for eviction so that it is evicted
        * the next time someone tries to acquire it from the pool.
        *
        * @param poolEntry the PoolEntry (/Connection) to "soft" evict from the pool
        * @param reason the reason that the connection is being evicted
        * @param owner true if the caller is the owner of the connection, false otherwise
        * @return true if the connection was evicted (closed), false if it was merely marked for eviction
        */
       private boolean softEvictConnection(final PoolEntry poolEntry, final String reason, final boolean owner) {
          poolEntry.markEvicted();
          if (owner || connectionBag.reserve(poolEntry)) {
             closeConnection(poolEntry, reason);
             return true;
          }
          return false;
       }
    

执行此方法时我们的owner默认传false(not
owner),调用com.zaxxer.hikari.util.ConcurrentBag的reserve对方进行保留

    
    
     /**
        * The method is used to make an item in the bag "unavailable" for
        * borrowing.  It is primarily used when wanting to operate on items
        * returned by the <code>values(int)``` method.  Items that are
        * reserved can be removed from the bag via <code>remove(T)```
        * without the need to unreserve them.  Items that are not removed
        * from the bag can be make available for borrowing again by calling
        * the <code>unreserve(T)``` method.
        *
        * @param bagEntry the item to reserve
        * @return true if the item was able to be reserved, false otherwise
        */
       public boolean reserve(final T bagEntry) {
          return bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_RESERVED);
       }
    

除了 HikariPoolMXBean的调用，softEvictConnections在housekeeper中也有使用

    
    
    /**
        * The house keeping task to retire and maintain minimum idle connections.
        */
       private final class HouseKeeper implements Runnable {
          private volatile long previous = plusMillis(currentTime(), -HOUSEKEEPING_PERIOD_MS);
          @Override
          public void run()
          {
             try {
                // refresh timeouts in case they changed via MBean
                connectionTimeout = config.getConnectionTimeout();
                validationTimeout = config.getValidationTimeout();
                leakTaskFactory.updateLeakDetectionThreshold(config.getLeakDetectionThreshold());
                final long idleTimeout = config.getIdleTimeout();
                final long now = currentTime();
                // Detect retrograde time, allowing +128ms as per NTP spec.
                if (plusMillis(now, 128)  plusMillis(previous, (3 * HOUSEKEEPING_PERIOD_MS) / 2)) {
                   // No point evicting for forward clock motion, this merely accelerates connection retirement anyway
                   LOGGER.warn("{} - Thread starvation or clock leap detected (housekeeper delta={}).", poolName, elapsedDisplayString(previous, now));
                }
                previous = now;
                String afterPrefix = "Pool ";
                if (idleTimeout &gt; 0L &amp;&amp; config.getMinimumIdle() &lt; config.getMaximumPoolSize()) {
                   logPoolState(&quot;Before cleanup &quot;);
                   afterPrefix = &quot;After cleanup  &quot;;
                   final List notInUse = connectionBag.values(STATE_NOT_IN_USE);
                   int toRemove = notInUse.size() - config.getMinimumIdle();
                   for (PoolEntry entry : notInUse) {
                      if (toRemove &gt; 0 &amp;&amp; elapsedMillis(entry.lastAccessed, now) &gt; idleTimeout &amp;&amp; connectionBag.reserve(entry)) {
                         closeConnection(entry, "(connection has passed idleTimeout)");
                         toRemove--;
                      }
                   }
                }
                logPoolState(afterPrefix);
                fillPool(); // Try to maintain minimum connections
             }
             catch (Exception e) {
                LOGGER.error("Unexpected exception in housekeeping task", e);
             }
          }
       }
    

聚焦一下,这段代码也是检测时钟回拨，如果时钟在规定范围外回拨了，就驱除连接，并重置时间。

    
    
    // Detect retrograde time, allowing +128ms as per NTP spec.
                if (plusMillis(now, 128) &lt; plusMillis(previous, HOUSEKEEPING_PERIOD_MS)) {
                   LOGGER.warn(&quot;{} - Retrograde clock change detected (housekeeper delta={}), soft-evicting connections from pool.&quot;,
                               poolName, elapsedDisplayString(previous, now));
                   previous = now;
                   softEvictConnections();
                   return;
                }
      /**
        * Return the specified opaque time-stamp plus the specified number of milliseconds.
        *
        * @param time an opaque time-stamp
        * @param millis milliseconds to add
        * @return a new opaque time-stamp
        */
       static long plusMillis(long time, long millis) {
          return CLOCK.plusMillis0(time, millis);
       }
    

说到时钟回拨，是不是想起了snowflake里的时钟回拨的处理？让我们一起温习一下！

    
    
    /**
     * 自生成Id生成器.
     * 
     * 
     * 长度为64bit,从高位到低位依次为
     * 
     * 
     * <pre>
     * 1bit   符号位 
     * 41bits 时间偏移量从2016年11月1日零点到现在的毫秒数
     * 10bits 工作进程Id
     * 12bits 同一个毫秒内的自增量
     * </pre>
     * 
     * 
     * 工作进程Id获取优先级: 系统变量{@code sjdbc.self.id.generator.worker.id} 大于 环境变量{@code SJDBC_SELF_ID_GENERATOR_WORKER_ID}
     * ,另外可以调用@{@code CommonSelfIdGenerator.setWorkerId}进行设置
     * 
     * 
     * @author gaohongtao
     */
    @Getter
    @Slf4j
    public class CommonSelfIdGenerator implements IdGenerator {
        public static final long SJDBC_EPOCH;//时间偏移量，从2016年11月1日零点开始
        private static final long SEQUENCE_BITS = 12L;//自增量占用比特
        private static final long WORKER_ID_BITS = 10L;//工作进程ID比特
        private static final long SEQUENCE_MASK = (1 &lt;&lt; SEQUENCE_BITS) - 1;//自增量掩码（最大值）
        private static final long WORKER_ID_LEFT_SHIFT_BITS = SEQUENCE_BITS;//工作进程ID左移比特数（位数）
        private static final long TIMESTAMP_LEFT_SHIFT_BITS = WORKER_ID_LEFT_SHIFT_BITS + WORKER_ID_BITS;//时间戳左移比特数（位数）
        private static final long WORKER_ID_MAX_VALUE = 1L &lt;= 0L &amp;&amp; workerId &lt; WORKER_ID_MAX_VALUE);
            CommonSelfIdGenerator.workerId = workerId;
        }
        /**
         * 生成Id.
         * 
         * @return 返回@{@link Long}类型的Id
         */
        @Override
        public synchronized Number generateId() {
        //保证当前时间大于最后时间。时间回退会导致产生重复id
            long time = clock.millis();
            Preconditions.checkState(lastTime &lt;= time, &quot;Clock is moving backwards, last time is %d milliseconds, current time is %d milliseconds&quot;, lastTime, time);
            // 获取序列号
            if (lastTime == time) {
                if (0L == (sequence = ++sequence &amp; SEQUENCE_MASK)) {
                    time = waitUntilNextTime(time);
                }
            } else {
                sequence = 0;
            }
            // 设置最后时间戳
            lastTime = time;
            if (log.isDebugEnabled()) {
                log.debug(&quot;{}-{}-{}&quot;, new SimpleDateFormat(&quot;yyyy-MM-dd HH:mm:ss.SSS&quot;).format(new Date(lastTime)), workerId, sequence);
            }
            // 生成编号
            return ((time - SJDBC_EPOCH) &lt;&lt; TIMESTAMP_LEFT_SHIFT_BITS) | (workerId &lt;&lt; WORKER_ID_LEFT_SHIFT_BITS) | sequence;
        }
        //不停获得时间，直到大于最后时间
        private long waitUntilNextTime(final long lastTime) {
            long time = clock.millis();
            while (time  0 &amp;&amp; elapsedMillis(start)  0 &amp;&amp; !handoffQueue.offer(bagEntry)) {
          yield();
       }
    }
    public boolean remove(final T bagEntry) {
       // 如果资源正在使用且无法进行状态切换，则返回失败
       if (!bagEntry.compareAndSet(STATE_IN_USE, STATE_REMOVED) &amp;&amp; !bagEntry.compareAndSet(STATE_RESERVED, STATE_REMOVED) &amp;&amp; !closed) {
          LOGGER.warn("Attempt to remove an object from the bag that was not borrowed or reserved: {}", bagEntry);
          return false;
       }
       final boolean removed = sharedList.remove(bagEntry); // 从CopyOnWriteArrayList中移出
       if (!removed &amp;&amp; !closed) {
          LOGGER.warn("Attempt to remove an object from the bag that does not exist: {}", bagEntry);
       }
       return removed;
    }
    

ConcurrentBag中通过borrow方法进行数据资源借用，通过requite方法进行资源回收，注意其中borrow方法只提供对象引用，不移除对象，因此使用时通过borrow取出的对象必须通过requite方法进行放回，否则容易导致内存泄露！

    
    
    public T borrow(long timeout, final TimeUnit timeUnit) throws InterruptedException {
       // 优先查看有没有可用的本地化的资源
       final List list = threadList.get();
       for (int i = list.size() - 1; i &gt;= 0; i--) {
          final Object entry = list.remove(i);
          @SuppressWarnings("unchecked")
          final T bagEntry = weakThreadLocals ? ((WeakReference) entry).get() : (T) entry;
          if (bagEntry != null &amp;&amp; bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
             return bagEntry;
          }
       }
       final int waiting = waiters.incrementAndGet();
       try {
          // 当无可用本地化资源时，遍历全部资源，查看是否存在可用资源
          // 因此被一个线程本地化的资源也可能被另一个线程“抢走”
          for (T bagEntry : sharedList) {
             if (bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                if (waiting &gt; 1) {
                    // 因为可能“抢走”了其他线程的资源，因此提醒包裹进行资源添加
                   listener.addBagItem(waiting - 1);
                }
                return bagEntry;
             }
          }
          listener.addBagItem(waiting);
          timeout = timeUnit.toNanos(timeout);
          do {
             final long start = currentTime();
             // 当现有全部资源全部在使用中，等待一个被释放的资源或者一个新资源
             final T bagEntry = handoffQueue.poll(timeout, NANOSECONDS);
             if (bagEntry == null || bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                return bagEntry;
             }
             timeout -= elapsedNanos(start);
          } while (timeout &gt; 10_000);
          return null;
       }
       finally {
          waiters.decrementAndGet();
       }
    }
    public void requite(final T bagEntry) {
       // 将状态转为未在使用
       bagEntry.setState(STATE_NOT_IN_USE);
       // 判断是否存在等待线程，若存在，则直接转手资源
       for (int i = 0; waiters.get() &gt; 0; i++) {
          if (bagEntry.getState() != STATE_NOT_IN_USE || handoffQueue.offer(bagEntry)) {
             return;
          }
          else if ((i &amp; 0xff) == 0xff) {
             parkNanos(MICROSECONDS.toNanos(10));
          }
          else {
             yield();
          }
       }
       // 否则，进行资源本地化
       final List threadLocalList = threadList.get();
       threadLocalList.add(weakThreadLocals ? new WeakReference(bagEntry) : bagEntry);
    }
    

上述代码中的 weakThreadLocals 是用来判断是否使用弱引用，通过下述方法初始化：

    
    
    private boolean useWeakThreadLocals()
    {
       try {
          // 人工指定是否使用弱引用，但是官方不推荐进行自主设置。
          if (System.getProperty("com.dareway.concurrent.useWeakReferences") != null) { 
             return Boolean.getBoolean("com.dareway.concurrent.useWeakReferences");
          }
          // 默认通过判断初始化的ClassLoader是否是系统的ClassLoader来确定
          return getClass().getClassLoader() != ClassLoader.getSystemClassLoader();
       }
       catch (SecurityException se) {
          return true;
       }
    }
    

# Hikari物理连接取用生命周期

上面提到了很多概念，比如HikariDataSource、HikariPool、ConcurrentBag、ProxyFactory、PoolEntry等等，那么这里的关系是什么呢？

这里推荐一下这篇文章 <http://www.cnblogs.com/taisenki/p/7717912.html> ，我引用一下部分内容：

HikariCP中的连接取用流程如下：

![2018042710002](http://cmsblogs.qiniudn.com/2018042710002.png)

HikariPool负责对资源连接进行管理，而ConcurrentBag则是作为物理连接的共享资源站，PoolEntry则是对物理连接的1-1封装。

PoolEntry通过connectionBag的borrow方法从bag中取出，，之后通过PoolEntry.createProxyConnection调用工厂类生成HikariProxyConnection返回。

    
    
    /**
     * Entry used in the ConcurrentBag to track Connection instances.
     *
     * @author Brett Wooldridge
     */
    final class PoolEntry implements IConcurrentBagEntry {
       private static final Logger LOGGER = LoggerFactory.getLogger(PoolEntry.class);
       private static final AtomicIntegerFieldUpdater stateUpdater;
       Connection connection;
       long lastAccessed;
       long lastBorrowed;
       @SuppressWarnings("FieldCanBeLocal")
       private volatile int state = 0;
       private volatile boolean evict;
       private volatile ScheduledFuture endOfLife;
       private final FastList openStatements;
       private final HikariPool hikariPool;
       private final boolean isReadOnly;
       private final boolean isAutoCommit;
       static
       {
          stateUpdater = AtomicIntegerFieldUpdater.newUpdater(PoolEntry.class, "state");
       }
       PoolEntry(final Connection connection, final PoolBase pool, final boolean isReadOnly, final boolean isAutoCommit)
       {
          this.connection = connection;
          this.hikariPool = (HikariPool) pool;
          this.isReadOnly = isReadOnly;
          this.isAutoCommit = isAutoCommit;
          this.lastAccessed = currentTime();
          this.openStatements = new FastList(Statement.class, 16);
       }
       /**
        * Release this entry back to the pool.
        *
        * @param lastAccessed last access time-stamp
        */
       void recycle(final long lastAccessed) {
          if (connection != null) {
             this.lastAccessed = lastAccessed;
             hikariPool.recycle(this);
          }
       }
       /**
        * Set the end of life {@link ScheduledFuture}.
        *
        * @param endOfLife this PoolEntry/Connection"s end of life {@link ScheduledFuture}
        */
       void setFutureEol(final ScheduledFuture endOfLife) {
          this.endOfLife = endOfLife;
       }
       Connection createProxyConnection(final ProxyLeakTask leakTask, final long now) {
          return ProxyFactory.getProxyConnection(this, connection, openStatements, leakTask, now, isReadOnly, isAutoCommit);
       }
       void resetConnectionState(final ProxyConnection proxyConnection, final int dirtyBits) throws SQLException {
          hikariPool.resetConnectionState(connection, proxyConnection, dirtyBits);
       }
       String getPoolName() {
          return hikariPool.toString();
       }
       boolean isMarkedEvicted() {
          return evict;
       }
       void markEvicted() {
          this.evict = true;
       }
       void evict(final String closureReason) {
          hikariPool.closeConnection(this, closureReason);
       }
       /** Returns millis since lastBorrowed */
       long getMillisSinceBorrowed() {
          return elapsedMillis(lastBorrowed);
       }
       /** {@inheritDoc} */
       @Override
       public String toString() {
          final long now = currentTime();
          return connection
             + ", accessed " + elapsedDisplayString(lastAccessed, now) + " ago, "
             + stateToString();
       }
       // ***********************************************************************
       //                      IConcurrentBagEntry methods
       // ***********************************************************************
       /** {@inheritDoc} */
       @Override
       public int getState() {
          return stateUpdater.get(this);
       }
       /** {@inheritDoc} */
       @Override
       public boolean compareAndSet(int expect, int update) {
          return stateUpdater.compareAndSet(this, expect, update);
       }
       /** {@inheritDoc} */
       @Override
       public void setState(int update) {
          stateUpdater.set(this, update);
       }
       Connection close() {
          ScheduledFuture eol = endOfLife;
          if (eol != null &amp;&amp; !eol.isDone() &amp;&amp; !eol.cancel(false)) {
             LOGGER.warn("{} - maxLifeTime expiration task cancellation unexpectedly returned false for connection {}", getPoolName(), connection);
          }
          Connection con = connection;
          connection = null;
          endOfLife = null;
          return con;
       }
       private String stateToString() {
          switch (state) {
          case STATE_IN_USE:
             return "IN_USE";
          case STATE_NOT_IN_USE:
             return "NOT_IN_USE";
          case STATE_REMOVED:
             return "REMOVED";
          case STATE_RESERVED:
             return "RESERVED";
          default:
             return "Invalid";
          }
       }
    }
    

# 参考资料

  * <https://segmentfault.com/a/1190000013118843>
  * <http://www.cnblogs.com/taisenki/p/7717912.html>

