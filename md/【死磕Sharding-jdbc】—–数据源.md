  * 1 ①ShardingDataSource
    * 1.1 分表原则
    * 1.2 分库原则

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/28b953c5d4b2>

* * *

以`com.dangdang.ddframe.rdb.sharding.example.jdbc.Main`剖析分库分表配置与实现，其部分源码如下：

    
    
    public final class Main {
    
        public static void main(final String[] args) throws SQLException {
            // step1: 配置sharding数据源
            DataSource dataSource = getShardingDataSource();
            // step2：创建表
            createTable(dataSource);
            // step3：插入数据
            insertData(dataSource);
            printSimpleSelect(dataSource);
            printGroupBy(dataSource);
            printHintSimpleSelect(dataSource);
            dropTable(dataSource);
        }
        ... ...
    }
    

接下来分析第一步，即如何创建 **ShardingDataSource** ；

# ①ShardingDataSource

硬编码创建ShardingDataSource的核心实现源码如下：

    
    
    private static ShardingDataSource getShardingDataSource() throws SQLException {
        // 构造DataSourceRule，即key与数据源的KV对；
        DataSourceRule dataSourceRule = new DataSourceRule(createDataSourceMap());
        // 建立逻辑表是t_order，实际表是t_order_0，t_order_1的TableRule
        TableRule orderTableRule = TableRule.builder("t_order").actualTables(Arrays.asList("t_order_0", "t_order_1")).dataSourceRule(dataSourceRule).build();
        // 建立逻辑表是t_order_item，实际表是t_order_item_0，t_order_item_1的TableRule
        TableRule orderItemTableRule = TableRule.builder("t_order_item").actualTables(Arrays.asList("t_order_item_0", "t_order_item_1")).dataSourceRule(dataSourceRule).build();
        ShardingRule shardingRule = ShardingRule.builder()
                    .dataSourceRule(dataSourceRule)
                    .tableRules(Arrays.asList(orderTableRule, orderItemTableRule))
                    // 增加绑定表--绑定表代表一组表，这组表的逻辑表与实际表之间的映射关系是相同的。比如t_order与t_order_item就是这样一组绑定表关系,它们的分库与分表策略是完全相同的,那么可以使用它们的表规则将它们配置成绑定表，绑定表所有路由计算将会只使用主表的策略；
                    .bindingTableRules(Collections.singletonList(new BindingTableRule(Arrays.asList(orderTableRule, orderItemTableRule))))
                    // 指定数据库sharding策略--根据user_id字段的值取模
                    .databaseShardingStrategy(new DatabaseShardingStrategy("user_id", new ModuloDatabaseShardingAlgorithm()))
                    // 指定表sharding策略--根据order_id字段的值取模
                    .tableShardingStrategy(new TableShardingStrategy("order_id", new ModuloTableShardingAlgorithm())).build();
        return new ShardingDataSource(shardingRule);
    }
    
    // 创建两个数据源，一个是ds_jdbc_0，一个是ds_jdbc_1，并绑定映射关系key
    private static Map<String, DataSource> createDataSourceMap() {
        Map<String, DataSource> result = new HashMap<>(2);
        result.put("ds_jdbc_0", createDataSource("ds_jdbc_0"));
        result.put("ds_jdbc_1", createDataSource("ds_jdbc_1"));
        return result;
    }
    
    // 以dbcp组件创建一个数据源
    private static DataSource createDataSource(final String dataSourceName) {
        BasicDataSource result = new BasicDataSource();
        result.setDriverClassName(com.mysql.jdbc.Driver.class.getName());
        result.setUrl(String.format("jdbc:mysql://localhost:3306/%s", dataSourceName));
        result.setUsername("root");
        // sharding-jdbc默认以密码为空的root用户访问，如果修改了root用户的密码，这里修改为真实的密码即可；
        result.setPassword("");
        return result;
    }
    

>
备注：逻辑表（LogicTable）即数据分片的逻辑表，对于水平拆分的数据库(表)，同一类表的总称。例：订单数据根据订单ID取模拆分为16张表,分别是t_order_0到t_order_15，他们的逻辑表名为t_order；实际表（ActualTable）是指在分片的数据库中真实存在的物理表。即这个示例中的t_order_0到t_order_15。摘自[sharding-
jdbc核心概念](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2F1.x%2Fdocs%2F02-guide%2Fconcepts%2F)

## 分表原则

根据上面的代码中`.tableShardingStrategy(new TableShardingStrategy("order_id", new
ModuloTableShardingAlgorithm()))`这段代码可知，分表策略通过
**ModuloTableShardingAlgorithm.java** 实现，且是通过 **ShardingStrategy.java**
中的doSharding()方法调用，核心源码如下：

    
    
    private Collection<String> doSharding(final Collection<ShardingValue<?>> shardingValues, final Collection<String> availableTargetNames) {
        // shardingAlgorithm即sharding算法分为三种：NoneKey，SingleKey和MultipleKeys
        if (shardingAlgorithm instanceof NoneKeyShardingAlgorithm) {
            return Collections.singletonList(((NoneKeyShardingAlgorithm) shardingAlgorithm).doSharding(availableTargetNames, shardingValues.iterator().next()));
        }
        if (shardingAlgorithm instanceof SingleKeyShardingAlgorithm) {
            // 得到SingleKeyShardingAlgorithm的具体实现，在ShardingStrategy的构造方法中赋值
            SingleKeyShardingAlgorithm<?> singleKeyShardingAlgorithm = (SingleKeyShardingAlgorithm<?>) shardingAlgorithm;
            // ShardingValue就是sharding的列和该列的值，在这里分别为order_id和1000
            ShardingValue shardingValue = shardingValues.iterator().next();
            // sharding列的类型分为三种：SINGLE，LIST和RANGE
            switch (shardingValue.getType()) {
                // 如果是where order_id=1000，那么type就是SINGLE
                case SINGLE:
                    // doEqualSharding只返回一个值，为了doSharding()返回值的统一，用Collections.singletonList()包装成集合；
                    return Collections.singletonList(singleKeyShardingAlgorithm.doEqualSharding(availableTargetNames, shardingValue));
                case LIST:
                    return singleKeyShardingAlgorithm.doInSharding(availableTargetNames, shardingValue);
                case RANGE:
                    return singleKeyShardingAlgorithm.doBetweenSharding(availableTargetNames, shardingValue);
                default:
                    throw new UnsupportedOperationException(shardingValue.getType().getClass().getName());
            }
        }
        if (shardingAlgorithm instanceof MultipleKeysShardingAlgorithm) {
            return ((MultipleKeysShardingAlgorithm) shardingAlgorithm).doSharding(availableTargetNames, shardingValues);
        }
        throw new UnsupportedOperationException(shardingAlgorithm.getClass().getName());
    }
    

>   1. 如果SQL中分表列order_id条件为where
order_id=?，那么shardingValue的type为SINGLE，分表逻辑走doEqualSharding()；

>   2. 如果SQL中分表列order_id条件为where order_id in(?,
?)，那么shardingValue的type为LIST，那么分表逻辑走doInSharding()；

>   3. 如果SQL中分表列order_id条件为where order_id between in(?,
?)，那么shardingValue的type为RANGE，那么分表逻辑走doBetweenSharding()；

>

>

> shardingValue的type的判断依据如下代码：

    
    
    public ShardingValueType getType() {
        // 
        if (null != value) {
            return ShardingValueType.SINGLE;
        }
        if (!values.isEmpty()) {
            return ShardingValueType.LIST;
        }
        return ShardingValueType.RANGE;
    }
    

表的取模核心实现源码如下：

    
    
    public final class ModuloTableShardingAlgorithm implements SingleKeyTableShardingAlgorithm<Integer> {
        // 分析前提，假设预期分到两个表中[t_order_0,t_order_1]，且执行的SQL为SELECT o.* FROM t_order o where o.order_id=1001 AND o.user_id=10，那么分表列order_id的值为1001
        @Override
        public String doEqualSharding(final Collection<String> tableNames, final ShardingValue<Integer> shardingValue) {
            // 遍历表名[t_order_0,t_order_1]
            for (String each : tableNames) {
                // 直到表名是以分表列order_id的值1001对2取模的值即1结尾，那么就是命中的表名，即t_order_1
                if (each.endsWith(shardingValue.getValue() % tableNames.size() + "")) {
                    return each;
                }
            }
            throw new UnsupportedOperationException();
        }
    
        @Override
        public Collection<String> doInSharding(final Collection<String> tableNames, final ShardingValue<Integer> shardingValue) {
            Collection<String> result = new LinkedHashSet<>(tableNames.size());
            // 从这里可知，doInSharding()和doEqualSharding()的区别就是doInSharding()时分表列有多个值（shardingValue.getValues()），例如order_id的值为[1001,1002]，遍历这些值，然后每个值按照doEqualSharding()的逻辑计算表名
            for (Integer value : shardingValue.getValues()) {
                for (String tableName : tableNames) {
                    if (tableName.endsWith(value % tableNames.size() + "")) {
                        result.add(tableName);
                    }
                }
            }
            return result;
        }
    
        @Override
        public Collection<String> doBetweenSharding(final Collection<String> tableNames, final ShardingValue<Integer> shardingValue) {
            Collection<String> result = new LinkedHashSet<>(tableNames.size());
            // 从这里可知，doBetweenSharding()和doInSharding()的区别就是doBetweenSharding()时分表列的多个值通过shardingValue.getValueRange()得到；而doInSharding()是通过shardingValue.getValues()得到；
            Range<Integer> range = shardingValue.getValueRange();
            for (Integer i = range.lowerEndpoint(); i <= range.upperEndpoint(); i++) {
                for (String each : tableNames) {
                    if (each.endsWith(i % tableNames.size() + "")) {
                        result.add(each);
                    }
                }
            }
            return result;
        }
    }
    

>   1. 如果SQL中分表列order_id条件为where order_id=?，那么分表逻辑走doEqualSharding()；

>   2. 如果SQL中分表列order_id条件为where order_id in(?, ?)，那么分表逻辑走doInSharding()；

>   3. 如果SQL中分表列order_id条件为where order_id between in(?,
?)，那么分表逻辑走doBetweenSharding()；

>

>

>
这些条件判断依据代码如下，当SimpleRoutingEngine中调用routeTables()进行路由表判定时会调用下面的方法，且通过这段代码可知，sharding列只支持=，in和between的操作：

    
    
    public ShardingValue<?> getShardingValue(final List<Object> parameters) {
        List<Comparable<?>> conditionValues = getValues(parameters);
        switch (operator) {
            case EQUAL:
                return new ShardingValue<Comparable<?>>(column.getTableName(), column.getName(), conditionValues.get(0));
            case IN:
                return new ShardingValue<>(column.getTableName(), column.getName(), conditionValues);
            case BETWEEN:
                return new ShardingValue<>(column.getTableName(), column.getName(), Range.range(conditionValues.get(0), BoundType.CLOSED, conditionValues.get(1), BoundType.CLOSED));
            default:
                throw new UnsupportedOperationException(operator.getExpression());
        }
    }
    

## 分库原则

根据上面的代码中`.databaseShardingStrategy(new DatabaseShardingStrategy("user_id", new
ModuloDatabaseShardingAlgorithm()))`这段代码可知，分库策略通过
**ModuloDatabaseShardingAlgorithm.java** 实现；  
通过比较 **ModuloDatabaseShardingAlgorithm.java** 和
**ModuloTableShardingAlgorithm.java** ，发现两者的实现逻辑完全一致，小小的区别就是
**ModuloDatabaseShardingAlgorithm.java** 根据分库的列例如`user_id`进行分库；而
**ModuloTableShardingAlgorithm.java** 根据分表的列例如`order_id`进行分表；所以分库在这里就不分析了；

> 说明：由于模块`sharding-jdbc-example-jdbc`中的Main方法创建的数据库和表数量都是2，所以
**ModuloDatabaseShardingAlgorithm.java** 和
**ModuloTableShardingAlgorithm.java** 的逻辑代码中写死了对2取模（%
2）；这样的话，如果debug过程中，修改了数据库和表的数量为3，或者4，改动代码如下所示，就会出现问题：

    
    
    private static ShardingDataSource getShardingDataSource() throws SQLException {
        DataSourceRule dataSourceRule = new DataSourceRule(createDataSourceMap());
        TableRule orderTableRule = TableRule
                .builder("t_order")
                .actualTables(Arrays.asList("t_order_0", "t_order_1", "t_order_2"))
                .dataSourceRule(dataSourceRule)
                .build();
        TableRule orderItemTableRule = TableRule
                .builder("t_order_item")
                .actualTables(Arrays.asList("t_order_item_0", "t_order_item_1", "t_order_item_2"))
                .dataSourceRule(dataSourceRule)
                .build();
        ... ...
    }
    
    private static Map<String, DataSource> createDataSourceMap() {
        Map<String, DataSource> result = new HashMap<>(3);
        result.put("ds_jdbc_0", createDataSource("ds_jdbc_0"));
        result.put("ds_jdbc_1", createDataSource("ds_jdbc_1"));
        result.put("ds_jdbc_2", createDataSource("ds_jdbc_2"));
        return result;
    }
    

想要纠正这个潜在的错误，只需要将源代码中 **ModuloDatabaseShardingAlgorithm.java** 中的`% 2`改为`%
dataSourceNames.size()`， **ModuloTableShardingAlgorithm.java** 中的`% 2`改为`%
tableNames.size()`即可；

