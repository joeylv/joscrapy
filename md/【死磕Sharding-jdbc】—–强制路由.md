  * 1 源码分析
  * 2 如何使用
    * 2.1 1、强制路由数据库
    * 2.2 2、强制路由表
    * 2.3 3、强制路由主库

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/644e9d6afd2c>

* * *

# 源码分析

位于`sharding-jdbc-core`模块下的包`com.dangdang.ddframe.rdb.sharding.hint`中，核心类
**HintManagerHolder** 的部分源码如下：

    
    
    /**
     * Hint manager holder.
     * <p>Use thread-local to manage hint.</p>
     * @author zhangliang
     */
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class HintManagerHolder {
    
        // hint特性保存数据的核心变量，即保存一个HintManager类型对象到ThreadLocal中
        private static final ThreadLocal<HintManager> HINT_MANAGER_HOLDER = new ThreadLocal<>();
    
        /**
         * Set hint manager.
         * @param hintManager hint manager instance
         */
        public static void setHintManager(final HintManager hintManager) {
            Preconditions.checkState(null == HINT_MANAGER_HOLDER.get(), "HintManagerHolder has previous value, please clear first.");
            HINT_MANAGER_HOLDER.set(hintManager);
        }
    
        public static boolean isUseShardingHint() {
            // 判断当前线程中是否使用了sharding hint--即HintManager中的shardingHint为true
            return null != HINT_MANAGER_HOLDER.get() && HINT_MANAGER_HOLDER.get().isShardingHint();
        }
    
        public static Optional<ShardingValue<?>> getDatabaseShardingValue(final ShardingKey shardingKey) {
            // 如果使用了sharding hint，那么从ThreadLocal中取数据库的sharding值
            return isUseShardingHint() ? Optional.<ShardingValue<?>>fromNullable(HINT_MANAGER_HOLDER.get().getDatabaseShardingValue(shardingKey)) : Optional.<ShardingValue<?>>absent();
        }
    
        public static Optional<ShardingValue<?>> getTableShardingValue(final ShardingKey shardingKey) {
            // 如果使用了sharding hint，那么从ThreadLocal中取表的sharding值
            return isUseShardingHint() ? Optional.<ShardingValue<?>>fromNullable(HINT_MANAGER_HOLDER.get().getTableShardingValue(shardingKey)) : Optional.<ShardingValue<?>>absent();
        }
    
        public static boolean isMasterRouteOnly() {
            // 是否强制路由主库--sharding-jdbc的特性之一：强制路由
            return null != HINT_MANAGER_HOLDER.get() && HINT_MANAGER_HOLDER.get().isMasterRouteOnly();
        }
    
        public static boolean isDatabaseShardingOnly() {
            // 是否只是数据库sharding
            return null != HINT_MANAGER_HOLDER.get() && HINT_MANAGER_HOLDER.get().isDatabaseShardingOnly();
        }
    
        /**
         * Clear hint manager for current thread-local.
         */
        public static void clear() {
            // ThreadLocal用完需要清理
            HINT_MANAGER_HOLDER.remove();
        }
    }
    

ThreadLocal中管理的 **HintManager** 定义如下：

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class HintManager implements AutoCloseable {
    
        // 数据库强制路由的值
        private final Map<ShardingKey, ShardingValue<?>> databaseShardingValues = new HashMap<>();
    
        // 表强制路由的值
        private final Map<ShardingKey, ShardingValue<?>> tableShardingValues = new HashMap<>();
    
        // 即是否使用了强制路由特性
        @Getter
        private boolean shardingHint;
    
        // 是否强制路由到主数据库
        @Getter
        private boolean masterRouteOnly;
    
        @Getter
        private boolean databaseShardingOnly;
    
        ... ...
    
        @Override
        public void close() {
            HintManagerHolder.clear();
        }
    }
    

>
sharding值保存在ThreadLocal中，所以需要在操作结束时调用HintManager.close()来清除ThreadLocal中的内容。HintManager实现了AutoCloseable接口，推荐使用`try
with resource`（JDK7新特性，参考[Java 7中的Try-with-
resources](https://link.jianshu.com?t=http%3A%2F%2Fifeve.com%2Fjava-7%25E4%25B8%25AD%25E7%259A%2584try-
with-resources%2F)）自动关闭清理ThreadLocl线程中的数据。

# 如何使用

分析了sharding-jdbc的强制路由实现的源码，接下来说说如何使用这一niubility特性，假定数据源定义如下：

    
    
    private static ShardingDataSource getShardingDataSource() throws SQLException {
        DataSourceRule dataSourceRule = new DataSourceRule(createDataSourceMap());
        TableRule orderTableRule = TableRule
                .builder("t_order")
                .actualTables(Arrays.asList("t_order_0", "t_order_1"))
                .dataSourceRule(dataSourceRule)
                .build();
        TableRule orderItemTableRule = TableRule
                .builder("t_order_item")
                .actualTables(Arrays.asList("t_order_item_0", "t_order_item_1"))
                .dataSourceRule(dataSourceRule)
                .build();
        ShardingRule shardingRule = ShardingRule.builder()
                .dataSourceRule(dataSourceRule)
                .tableRules(Arrays.asList(orderTableRule, orderItemTableRule))
                .bindingTableRules(Collections.singletonList(new BindingTableRule(Arrays.asList(orderTableRule, orderItemTableRule))))
                .databaseShardingStrategy(new DatabaseShardingStrategy("user_id", new ModuloDatabaseShardingAlgorithm()))
                .tableShardingStrategy(new TableShardingStrategy("order_id", new ModuloTableShardingAlgorithm())).build();
        return new ShardingDataSource(shardingRule);
    }
    

> 根据数据源定义可知，数据库的sharding column为user_id，表的sharding column为order_id；

## 1、强制路由数据库

  * 如何使用

    
    
    private static void printHintSimpleSelect(final DataSource dataSource) throws SQLException {
        // SQL语句并不涉及任何数据库路由和表路由信息（即where语句中没有user_id条件和order_id条件）
        String sql = "SELECT i.* FROM t_order o JOIN t_order_item i ON o.order_id=i.order_id";
        try (
                HintManager hintManager = HintManager.getInstance();
                Connection conn = dataSource.getConnection();
                PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
            // 强制路由：数据库路由sharding column即user_id的值为10
            hintManager.addDatabaseShardingValue("t_order", "user_id", 10);
            try (ResultSet rs = preparedStatement.executeQuery()) {
                //todo do something
            }
        }
    }
    

> 由于指定了强制路由数据库的值user_id=10，所以只会输出`ds_jdbc_0`这个库中符合条件的数据。而`ds_jdbc_1`会被过滤；

  * 实现原理

    
    
    private Collection<String> routeDataSources(final TableRule tableRule) {
        // 首先得到数据库sharding策略，例如：数据库按照列user_id进行sharding
        DatabaseShardingStrategy strategy = shardingRule.getDatabaseShardingStrategy(tableRule);
        // 然后从ThreadLocal中取出sharding的值
        List<ShardingValue<?>> shardingValues = HintManagerHolder.isUseShardingHint() ? getDatabaseShardingValuesFromHint(strategy.getShardingColumns())
                : getShardingValues(strategy.getShardingColumns());
        Collection<String> result = strategy.doStaticSharding(tableRule.getActualDatasourceNames(), shardingValues);
        Preconditions.checkState(!result.isEmpty(), "no database route info");
        return result;
    }
    

## 2、强制路由表

  * 如何使用

    
    
    private static void printHintSimpleSelect(final DataSource dataSource) throws SQLException {
        // SQL语句并不涉及任何数据库路由和表路由信息（即where语句中没有user_id条件和order_id条件）
        String sql = "SELECT i.* FROM t_order o JOIN t_order_item i ON o.order_id=i.order_id";
        try (
                HintManager hintManager = HintManager.getInstance();
                Connection conn = dataSource.getConnection();
                PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
            // 强制路由：表路由sharding column即order_id的值为1000
            hintManager.addTableShardingValue("t_order", "order_id", 1000);
            try (ResultSet rs = preparedStatement.executeQuery()) {
                //todo do something
            }
        }
    }
    

> 由于指定了强制路由表的值order_id=1000，所以只会输出所有库中与`t_order_0`
匹配的数据。而与`t_order_1`匹配的数据会被过滤；

  * 实现原理

    
    
    private Collection<String> routeTables(final TableRule tableRule, final String routedDataSource) {
        // 首先得到表的sharding策略，例如：表按照列order_id进行sharding
        TableShardingStrategy strategy = shardingRule.getTableShardingStrategy(tableRule);
        // 然后从ThreadLocal中取出sharding的值
        List<ShardingValue<?>> shardingValues = HintManagerHolder.isUseShardingHint() ? getTableShardingValuesFromHint(strategy.getShardingColumns())
                : getShardingValues(strategy.getShardingColumns());
        Collection<String> result = tableRule.isDynamic() ? strategy.doDynamicSharding(shardingValues) : strategy.doStaticSharding(tableRule.getActualTableNames(routedDataSource), shardingValues);
        Preconditions.checkState(!result.isEmpty(), "no table route info");
        return result;
    }
    

## 3、强制路由主库

  * 如何使用

    
    
    HintManager hintManager = HintManager.getInstance();
    hintManager.setMasterRouteOnly();
    

