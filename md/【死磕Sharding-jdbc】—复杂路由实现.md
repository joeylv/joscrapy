  * 1 路由条件
  * 2 构造复杂路由
  * 3 ComplexRoutingEngine
  * 4 CartesianRoutingEngine

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/bef720fd070c>

* * *

# 路由条件

ParsingSQLRouter.java中决定是简单路由还是复杂路由的条件如下；

    
    
    private RoutingResult route(final List<Object> parameters, final SQLStatement sqlStatement) {
        Collection<String> tableNames = sqlStatement.getTables().getTableNames();
        RoutingEngine routingEngine;
        if (1 == tableNames.size()
                || shardingRule.isAllBindingTables(tableNames)
                || shardingRule.isAllInDefaultDataSource(tableNames)) {
            routingEngine = new SimpleRoutingEngine(shardingRule, parameters, tableNames.iterator().next(), sqlStatement);
        } else {
            // TODO config for cartesian set
            routingEngine = new ComplexRoutingEngine(shardingRule, parameters, tableNames, sqlStatement);
        }
        return routingEngine.route();
    }
    

  * 是否只有一张表–tableNames.size()

> 说明：这个”一张表”并不是指SQL中只有一张表，而是 **有分库分表规则的表数量**
，例如下面这段构造ShardingRule的源码，tableRules()有两个表，所以tableNames.size()的值为2；如果(Arrays.asList(orderTableRule))即只有1个表，那么tableNames.size()的值为1；

    
    
    ShardingRule.builder()
    .dataSourceRule(dataSourceRule)
    .tableRules(Arrays.asList(orderTableRule, userTableRule))
    .databaseShardingStrategy(*** ***).tableShardingStrategy(*** ***) .build();
    

  * 是否都是绑定表–shardingRule.isAllBindingTables(tableNames)

>
说明：isAllBindingTables(tableNames)判断tableNames是否都属于绑定表，例如下面这段构造ShardingRule的源码，.bindingTableRules()里的参数就是绑定表集合，这里是t_order和t_order_item都是绑定表，那么：`SELECT
od.user_id, od.order_id, oi.item_id, od.status FROM t_order od join
t_order_item oi on
od.order_id=oi.order_id`这个SQL只有t_order和t_order_item两个表且都是绑定表，那么shardingRule.isAllBindingTables(tableNames)为true；

    
    
    ShardingRule.builder()
    .dataSourceRule(dataSourceRule)
    .tableRules(Arrays.asList(orderTableRule, orderItemTableRule, userTableRule))
    .bindingTableRules(Collections.singletonList(new BindingTableRule(Arrays.asList(orderTableRule, orderItemTableRule))))
    . *** ***;
    

  * 是否都在默认数据源中–shardingRule.isAllInDefaultDataSource(tableNames)

> 说明：sharding-
jdbc判断逻辑源码如下，即只要在表规则集合中能够匹配到逻辑表，就认为不属于默认数据源中（默认数据源不分库分表），例如`ShardingRule.builder().dataSourceRule(dataSourceRule).tableRules(Arrays.asList(orderTableRule,
orderItemTableRule,
userTableRule))`，根据tableRules参数可知，主要SQL中有`t_user`，`t_order`，`t_order_item`三个表的任意一个表，那么shardingRule.isAllInDefaultDataSource(tableNames)都为false；

    
    
    public boolean isAllInDefaultDataSource(final Collection<String> logicTables) {
        for (String each : logicTables) {
            if (tryFindTableRule(each).isPresent()) {
                return false;
            }
        }
        return !logicTables.isEmpty();
    }
    
    public Optional<TableRule> tryFindTableRule(final String logicTableName) {
        for (TableRule each : tableRules) {
            if (each.getLogicTable().equalsIgnoreCase(logicTableName)) {
                return Optional.of(each);
            }
        }
        return Optional.absent();
    }
    

# 构造复杂路由

综上分析，如果三个条件都不满足就走复杂路由 **ComplexRoutingEngine** ，构造这种场景：  
t_order和t_order_item分库分表且绑定表关系，加入一个新的分库分表t_user；ShardingRule如下：

    
    
    ShardingRule shardingRule = ShardingRule.builder()
            .dataSourceRule(dataSourceRule)
            .tableRules(Arrays.asList(orderTableRule, orderItemTableRule, userTableRule))
            .bindingTableRules(Collections.singletonList(new BindingTableRule(Arrays.asList(orderTableRule, orderItemTableRule))))
            .databaseShardingStrategy(new DatabaseShardingStrategy("user_id", new ModuloDatabaseShardingAlgorithm()))
            .tableShardingStrategy(new TableShardingStrategy("order_id", new ModuloTableShardingAlgorithm()))
            .build();
    

执行的SQL为：

    
    
    SELECT od.user_id, od.order_id, oi.item_id, od.status 
    FROM `t_user` tu 
    join t_order od on tu.user_id=od.user_id 
    join t_order_item oi on od.order_id=oi.order_id 
    where tu.`status`="VALID" and tu.user_id=?
    

>
构造的这个场景：tableNames.size()=3（三张表t_user，t_order，t_order_item都有分库分表规则，所以值为3），shardingRule.isAllBindingTables(tableNames)为false（t_user表不属于绑定表范围）；shardingRule.isAllInDefaultDataSource(tableNames)为false（三张表都不属于默认数据源中的表）；所以这个SQL会走复杂路由的逻辑；

# ComplexRoutingEngine

复杂路由引擎的核心逻辑就是拆分成多个简单路由，然后求笛卡尔积，复杂路由核心源码如下：

    
    
    @RequiredArgsConstructor
    @Slf4j
    public final class ComplexRoutingEngine implements RoutingEngine {
    
        // 分库分表规则
        private final ShardingRule shardingRule;
    
        // SQL请求参数，猪油一个user_id的值为10
        private final List<Object> parameters;
    
        // 逻辑表集合：t_order，t_order_item，t_user，三个逻辑表
        private final Collection<String> logicTables;
    
        // SQL解析结果
        private final SQLStatement sqlStatement;
    
        // 复杂路由的核心逻辑
        @Override
        public RoutingResult route() {
            Collection<RoutingResult> result = new ArrayList<>(logicTables.size());
            Collection<String> bindingTableNames = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
            // 遍历逻辑表集合
            for (String each : logicTables) {
                Optional<TableRule> tableRule = shardingRule.tryFindTableRule(each);
                // 如果遍历的表配置了分库分表规则
                if (tableRule.isPresent()) {
                    // 如果绑定关系表已经处理过，那么不需要再处理，例如t_order处理过，由于t_order_item与其是绑定关系，那么不需要再处理
                    if (!bindingTableNames.contains(each)) {
                        // 根据当前遍历的逻辑表构造一个简单路由规则
                        result.add(new SimpleRoutingEngine(shardingRule, parameters, tableRule.get().getLogicTable(), sqlStatement).route());
                    }
    
                    // 根据当前逻辑表，查找其对应的所有绑定表，例如根据t_order就能够查询出t_order和t_order_item；假如配置了.bindingTableRules(***t_point, t_point_detail***)，那么，根据t_point能查询出t_point和t_point_detail，其目的是N个绑定表只需要路由一个绑定表即可，因为绑定表之间的路由关系完全一致。
                    Optional<BindingTableRule> bindingTableRule = shardingRule.findBindingTableRule(each);
                    if (bindingTableRule.isPresent()) {
                        bindingTableNames.addAll(Lists.transform(bindingTableRule.get().getTableRules(), new Function<TableRule, String>() {
    
                            @Override
                            public String apply(final TableRule input) {
                                return input.getLogicTable();
                            }
                        }));
                    }
                }
            }
            log.trace("mixed tables sharding result: {}", result);
            // 如果是复杂路由，但是路由结果为空，那么抛出异常
            if (result.isEmpty()) {
                throw new ShardingJdbcException("Cannot find table rule and default data source with logic tables: "%s"", logicTables);
            }
            // 如果结果的size为1，那么直接返回即可
            if (1 == result.size()) {
                return result.iterator().next();
            }
            // 对刚刚的路由结果集合计算笛卡尔积，就是最终复杂的路由结果
            return new CartesianRoutingEngine(result).route();
        }
    }
    

> 由上面源码分析可知，会分别对t_user和t_order构造简单路由（t_order_item和t_order是绑定关系，二者取其一即可）；

  * t_user只分库不分表（因为构造TableRule时逻辑表和实际表一致），且请求参数为user_id=10，所以t_user这个逻辑表的简单路由结果为：数据源ds_jdbc_0，实际表t_user；
  * t_order分库分表，且请求参数user_id被解析为t_user的条件（笛卡尔积路由引擎会处理），所以t_order的简单路由结果为：数据源ds_jdbc_0和ds_jdbc_1，实际表t_order_0和t_order_1；

debug的result如下：

![201805231001](http://cmsblogs.qiniudn.com/201805231001.png)

# CartesianRoutingEngine

如上分析，求得简单路由结果集后，求笛卡尔积就是复杂路由的最终路由结果，笛卡尔积路由引擎CartesianRoutingEngine的核心源码如下：

    
    
    @RequiredArgsConstructor
    @Slf4j
    public final class CartesianRoutingEngine implements RoutingEngine {
    
        private final Collection<RoutingResult> routingResults;
    
        @Override
        public CartesianRoutingResult route() {
            CartesianRoutingResult result = new CartesianRoutingResult();
            // getDataSourceLogicTablesMap()的分析参考下面的分析
            for (Entry<String, Set<String>> entry : getDataSourceLogicTablesMap().entrySet()) {
                // 根据数据源&逻辑表，得到实际表集合，即[["t_user"],["t_order_0","t_order_1"]]
                List<Set<String>> actualTableGroups = getActualTableGroups(entry.getKey(), entry.getValue());
                // 把逻辑表名封装，TableUnit的属性有：数据源名称，逻辑表名，实际表名（这三个属性才能确定最终访问的表）
                List<Set<TableUnit>> tableUnitGroups = toTableUnitGroups(entry.getKey(), actualTableGroups);
                // 计算所有实际表的笛卡尔积
                result.merge(entry.getKey(), getCartesianTableReferences(Sets.cartesianProduct(tableUnitGroups)));
            }
            log.trace("cartesian tables sharding result: {}", result);
            return result;
        }
    
        // 得到数据源-逻辑表集合组成的Map
        private Map<String, Set<String>> getDataSourceLogicTablesMap() {
            // 这里很关键，是得到数据源的交集（上面分析时t_user逻辑表路由到数据源ds_jdbc_0，而t_order表路由到数据源ds_jdbc_0和ds_jdbc_1，数据源交集就是ds_jdbc_0）
            Collection<String> intersectionDataSources = getIntersectionDataSources();
            Map<String, Set<String>> result = new HashMap<>(routingResults.size());
            for (RoutingResult each : routingResults) {
                for (Entry<String, Set<String>> entry : each.getTableUnits().getDataSourceLogicTablesMap(intersectionDataSources).entrySet()) {
                    if (result.containsKey(entry.getKey())) {
                        result.get(entry.getKey()).addAll(entry.getValue());
                    } else {
                        result.put(entry.getKey(), entry.getValue());
                    }
                }
            }
            // 得到的最终结果为数据源-逻辑表集合组成的Map，这里就是{"ds_jdbc_0":["t_order", "t_user"]}
            return result;
        }
        ... ...
    }
    

计算得到的笛卡尔积结果如下：

![201805231002](http://cmsblogs.qiniudn.com/201805231001.png)

`sql.show`结果如下，可以看到重写后的2条实际SQL：`t_user&t_order_0`，以及`t_user&t_order_1`（t_order_item与t_order是绑定表，保持一致即可）：

    
    
    [INFO ] 2018-05-08 11:13:02,044 --main-- [Sharding-JDBC-SQL] Logic SQL: SELECT od.user_id, od.order_id, oi.item_id, od.status FROM `t_user` tu join t_order od on tu.user_id=od.user_id join t_order_item oi on od.order_id=oi.order_id where tu.`status`="VALID" and tu.user_id=? 
    ... ...
    [INFO ] 2018-05-08 11:13:02,059 --main-- [Sharding-JDBC-SQL] Actual SQL: ds_jdbc_0 ::: SELECT od.user_id, od.order_id, oi.item_id, od.status FROM t_user tu join t_order_0 od on tu.user_id=od.user_id join t_order_item_0 oi on od.order_id=oi.order_id where tu.`status`="VALID" and tu.user_id=? ::: [10] 
    [INFO ] 2018-05-08 11:13:02,059 --main-- [Sharding-JDBC-SQL] Actual SQL: ds_jdbc_0 ::: SELECT od.user_id, od.order_id, oi.item_id, od.status FROM t_user tu join t_order_1 od on tu.user_id=od.user_id join t_order_item_1 oi on od.order_id=oi.order_id where tu.`status`="VALID" and tu.user_id=? ::: [10]
    

