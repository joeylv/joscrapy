  * 1 读写分离支持项
  * 2 读写分离不支持范围
  * 3 源码分析
  * 4 主从负载均衡分析
    * 4.1 轮询策略
    * 4.2 随机策略
    * 4.3 默认策略

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/793eaba05d16>

* * *

# 读写分离支持项

  * 提供了一主多从的读写分离配置，可独立使用，也可配合分库分表使用。
  * 同一线程且同一数据库连接内，如有写入操作，以后的读操作均从主库读取，用于保证数据一致性。
  * Spring命名空间。
  * 基于Hint的强制主库路由。

# 读写分离不支持范围

  * 主库和从库的数据同步。
  * 主库和从库的数据同步延迟导致的数据不一致。
  * 主库双写或多写。

> 读写分离支持项和不支持范围摘自[sharding-
jdbc使用指南☞读写分离](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2Fdocs_1.x%2F02-guide%2Fmaster-
slave%2F)

# 源码分析

先执行`sharding-jdbc-example-config-spring-
masterslave`模块中的的SQL脚本`all_schema.sql`，这里有读写分离测试的需要的数据库、表以及数据；

  * 两个主数据库`dbtbl_0_master`和`dbtbl_1_master`；
  * 数据库`dbtbl_0_master`有两个从库`dbtbl_0_slave_0`和`dbtbl_0_slave_1`，这个集群体系命名为`dbtbl_0`；
  * 数据库`dbtbl_1_master`有两个从库`dbtbl_1_slave_0`和`dbtbl_1_slave_1`，这个集群体系命名为`dbtbl_1`；

以`SpringNamespaceWithMasterSlaveMain.java`为入口，分析读写分离是如何实现的：

router()路由时，会尝试读写分离：

    
    
    Collection<PreparedStatement> preparedStatements;
    if (SQLType.DDL == sqlType) {
        // 路由这里生成PreparedStatement时会选主从(如果是主从的话)
        preparedStatements = generatePreparedStatementForDDL(each);
    } else {
        // 路由这里生成PreparedStatement时会选主从(如果是主从的话)
        preparedStatements = Collections.singletonList(generatePreparedStatement(each));
    }
    routedStatements.addAll(preparedStatements);``` ```private PreparedStatement generatePreparedStatement(final SQLExecutionUnit sqlExecutionUnit) throws SQLException {
            // 先获取connection数据库连接，然后得到PreparedStatement，获取conntection时就会尝试选主从(如果有主从的话)
            Connection connection = getConnection().getConnection(sqlExecutionUnit.getDataSource(), routeResult.getSqlStatement().getType());
            return connection.prepareStatement(... ...);
        }``````// 数据源名称与数据库连接关系缓存，例如：{dbtbl_0_master:Connection实例; dbtbl_1_master:Connection实例; dbtbl_0_slave_0:Connection实例; dbtbl_0_slave_1:Connection实例; dbtbl_1_slave_0:Connection实例; dbtbl_1_slave_1:Connection实例}
    private final Map cachedConnections = new HashMap();
    
    /**
     * 根据数据源名称得到数据库连接
     */
    public Connection getConnection(final String dataSourceName, final SQLType sqlType) throws SQLException {
        // 首先尝试从local cache（map类型）中获取，如果已经本地缓存，那么直接从本地缓存中获取
        if (getCachedConnections().containsKey(dataSourceName)) {
            return getCachedConnections().get(dataSourceName);
        }
        DataSource dataSource = shardingContext.getShardingRule().getDataSourceRule().getDataSource(dataSourceName);
        Preconditions.checkState(null != dataSource, "Missing the rule of %s in DataSourceRule", dataSourceName);
        String realDataSourceName;
        // 如果是主从数据库的话（例如xml中配置，那么dbtbl_0就是主从数据源）
        if (dataSource instanceof MasterSlaveDataSource) {
            // 见后面的"主从数据源中根据负载均衡策略获取数据源"的分析
            NamedDataSource namedDataSource = ((MasterSlaveDataSource) dataSource).getDataSource(sqlType);
            realDataSourceName = namedDataSource.getName();
            // 如果主从数据库元选出的数据源名称（例如：dbtbl_1_slave_0）与数据库连接已经被缓存，那么从缓存中取出数据库连接
            if (getCachedConnections().containsKey(realDataSourceName)) {
                return getCachedConnections().get(realDataSourceName);
            }
            dataSource = namedDataSource.getDataSource();
        } else {
            realDataSourceName = dataSourceName;
        }
        Connection result = dataSource.getConnection();
        // 把数据源名称与数据库连接实例缓存起来
        getCachedConnections().put(realDataSourceName, result);
        replayMethodsInvocation(result);
        return result;
    }
    

主从数据源中根据负载均衡策略获取数据源核心源码–MasterSlaveDataSource.java：

    
    
    // 主数据源, 例如dbtbl_0_master对应的数据源
    @Getter
    private final DataSource masterDataSource;
    
    // 主数据源下所有的从数据源，例如{dbtbl_0_slave_0:DataSource实例; dbtbl_0_slave_1:DataSource实例}
    @Getter
    private final Map slaveDataSources;
    
    public NamedDataSource getDataSource(final SQLType sqlType) {
        if (isMasterRoute(sqlType)) {
            DML_FLAG.set(true);
            // 如果符合主路由规则，那么直接返回主路由（不需要根据负载均衡策略选择数据源）
            return new NamedDataSource(masterDataSourceName, masterDataSource);
        }
        // 负载均衡策略选择数据源名称[后面会分析]
        String selectedSourceName = masterSlaveLoadBalanceStrategy.getDataSource(name, masterDataSourceName, new ArrayList(slaveDataSources.keySet()));
        DataSource selectedSource = selectedSourceName.equals(masterDataSourceName) ? masterDataSource : slaveDataSources.get(selectedSourceName);
        Preconditions.checkNotNull(selectedSource, "");
        return new NamedDataSource(selectedSourceName, selectedSource);
    }
    
    // 主路由逻辑
    private boolean isMasterRoute(final SQLType sqlType) {
        return SQLType.DQL != sqlType || DML_FLAG.get() || HintManagerHolder.isMasterRouteOnly();
    }
    

主路由逻辑如下：

  1. 非查询SQL（SQLType.DQL != sqlType）
  2. 当前数据源在当前线程访问过主库（数据源访问过主库就会通过ThreadLocal将DML_FLAG置为true，从而路由主库）（DML_FLAG.get()）
  3. HintManagerHolder方式设置了主路由规则（HintManagerHolder.isMasterRouteOnly()）

> 当前线程访问过主库后，后面的操作全部切主，是为了防止主从同步数据延迟导致写操作后，读不到最新的数据？我想应该是这样的^^

# 主从负载均衡分析

从对`MasterSlaveDataSource.java`的分析可知，如果不符合强制主路由规则，那么会根据负载均衡策略选多个slave中选取一个slave；
**MasterSlaveLoadBalanceStrategy** 接口有两个实现类：
**RoundRobinMasterSlaveLoadBalanceStrategy** 和
**RandomMasterSlaveLoadBalanceStrategy** ，简单分析其实现；

## 轮询策略

轮询方式的实现类为 **RoundRobinMasterSlaveLoadBalanceStrategy** ，核心源码如下：

    
    
    public final class RoundRobinMasterSlaveLoadBalanceStrategy implements MasterSlaveLoadBalanceStrategy {
    
        private static final ConcurrentHashMap<String, AtomicInteger> COUNT_MAP = new ConcurrentHashMap<>();
    
        @Override
        public String getDataSource(final String name, final String masterDataSourceName, final List<String> slaveDataSourceNames) {
            // 每个集群体系都有自己的计数器，例如dbtbl_0集群，dbtbl_1集群；如果COUNT_MAP中还没有这个集群体系，需要先初始化；
            AtomicInteger count = COUNT_MAP.containsKey(name) ? COUNT_MAP.get(name) : new AtomicInteger(0);
            COUNT_MAP.putIfAbsent(name, count);
            // 如果轮询计数器（AtomicInteger count）长到slave.size()，那么归零（防止计数器不断增长下去）
            count.compareAndSet(slaveDataSourceNames.size(), 0);
            // 计数器递增，根据计算器的值就是从slave集合中选中的目标slave的下标
            return slaveDataSourceNames.get(count.getAndIncrement() % slaveDataSourceNames.size());
        }
    }
    

## 随机策略

随机方式的实现类为 **RandomMasterSlaveLoadBalanceStrategy** ，核心源码如下：

    
    
    public final class RandomMasterSlaveLoadBalanceStrategy implements MasterSlaveLoadBalanceStrategy {
    
        @Override
        public String getDataSource(final String name, final String masterDataSourceName, final List<String> slaveDataSourceNames) {
            // 取一个随机数，就是从slave集合中选中的目标slave的下标
            return slaveDataSourceNames.get(new Random().nextInt(slaveDataSourceNames.size()));
        }
    }
    

## 默认策略

    
    
    @RequiredArgsConstructor
    @Getter
    public enum MasterSlaveLoadBalanceStrategyType {
        // 轮询策略 
        ROUND_ROBIN(new RoundRobinMasterSlaveLoadBalanceStrategy()),
        // 随机策略
        RANDOM(new RandomMasterSlaveLoadBalanceStrategy());
    
        private final MasterSlaveLoadBalanceStrategy strategy;
    
        // 默认策略为轮询
        public static MasterSlaveLoadBalanceStrategyType getDefaultStrategyType() {
            return ROUND_ROBIN;
        }
    }
    

