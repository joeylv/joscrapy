  * 1 单表查询
    * 1.1 单表查询之路由
      * 1.1.1 SimpleRoutingEngine
      * 1.1.2 ComplexRoutingEngine
    * 1.2 单表查询之执行
    * 1.3 EventBus

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/09efada2d086>

* * *

继续以`sharding-jdbc-example-
jdbc`模块中的`com.dangdang.ddframe.rdb.sharding.example.jdbc.Main`为基础，剖析分库分表简单查询SQL实现–`printSimpleSelect(dataSource);`，即如何执行简单的查询SQL，接下来的分析以执行SQL语句`"SELECT
o.* FROM t_order o where o.user_id=? AND o.order_id=?"`为例；

# 单表查询

**Main** 中`printSimpleSelect()`方法调用`preparedStatement.executeQuery()`，即调用
**ShardingPreparedStatement** 中的`executeQuery()`方法，核心源码如下：

    
    
    @Override
    public ResultSet executeQuery() throws SQLException {
        ResultSet result;
        try {
            // 核心方法route()，即解析SQL如何路由执行
            Collection<PreparedStatementUnit> preparedStatementUnits = route();
            // 根据路由信息执行SQL
            List<ResultSet> resultSets = new PreparedStatementExecutor(
                    getConnection().getShardingContext().getExecutorEngine(), routeResult.getSqlStatement().getType(), preparedStatementUnits, getParameters()).executeQuery();
            // 对返回的结果进行merge合并
            result = new ShardingResultSet(resultSets, new MergeEngine(resultSets, (SelectStatement) routeResult.getSqlStatement()).merge());
        } finally {
            clearBatch();
        }
        currentResultSet = result;
        return result;
    }
    

> 通过上面的源码可知，SQL查询两个核心：路由和结果合并，接下来一一分析sharding-jdbc如何实现；

## 单表查询之路由

接下来分析下面这段代码是如何取得路由信息的：

    
    
    Collection<PreparedStatementUnit> preparedStatementUnits = route();
    

`route()`核心源码如下：

    
    
    private Collection<PreparedStatementUnit> route() throws SQLException {
        Collection<PreparedStatementUnit> result = new LinkedList<>();
        // 调用PreparedStatementRoutingEngine中的route()方法，route()方法调用sqlRouter.route(logicSQL, parameters, sqlStatement)
        routeResult = routingEngine.route(getParameters());
        for (SQLExecutionUnit each : routeResult.getExecutionUnits()) {
            SQLType sqlType = routeResult.getSqlStatement().getType();
            Collection<PreparedStatement> preparedStatements;
            if (SQLType.DDL == sqlType) {
                preparedStatements = generatePreparedStatementForDDL(each);
            } else {
                preparedStatements = Collections.singletonList(generatePreparedStatement(each));
            }
            routedStatements.addAll(preparedStatements);
            for (PreparedStatement preparedStatement : preparedStatements) {
                replaySetParameter(preparedStatement);
                result.add(new PreparedStatementUnit(each, preparedStatement));
            }
        }
        return result;
    }
    

>
SQLRouter接口有两个实现类：DatabaseHintSQLRouter和ParsingSQLRouter，由于这里没有用hint语法强制执行某个库，所以调用ParsingSQLRouter中的route()方法：

    
    
    private RoutingResult route(final List<Object> parameters, final SQLStatement sqlStatement) {
        Collection<String> tableNames = sqlStatement.getTables().getTableNames();
        RoutingEngine routingEngine;
        // 如果sql中只有一个表名，或者多个表名之间是绑定表关系，或者所有表都在默认数据源指定的数据库中（即不参与分库分表的表），那么用SimpleRoutingEngine作为路由判断引擎；
        if (1 == tableNames.size() || shardingRule.isAllBindingTables(tableNames) || shardingRule.isAllInDefaultDataSource(tableNames)) {
            routingEngine = new SimpleRoutingEngine(shardingRule, parameters, tableNames.iterator().next(), sqlStatement);
        } else {
            routingEngine = new ComplexRoutingEngine(shardingRule, parameters, tableNames, sqlStatement);
        }
        return routingEngine.route();
    }
    

> 接下来分析一下SimpleRoutingEngine和ComplexRoutingEngine；

### SimpleRoutingEngine

执行SQL：`"SELECT o.* FROM t_order o where o.user_id=? AND
o.order_id=?"`时，由于SQL中只有一个表（1 == tableNames.size()），所以路由引擎是
**SimpleRoutingEngine** ；`SimpleRoutingEngine.route()`源码如下：

    
    
    @Override
    public RoutingResult route() {
        // 根据逻辑表得到tableRule，逻辑表为t_order；表规则的配置为：.actualTables(Arrays.asList("t_order_0", "t_order_1"))，所以有两个实际表；
        TableRule tableRule = shardingRule.getTableRule(logicTableName);
        // 根据规则先路由数据源：即根据user_id取模路由
        Collection<String> routedDataSources = routeDataSources(tableRule);
        // routedMap保存路由到的目标数据源和表的结果：key为数据源，value为该数据源下路由到的目标表集合
        Map<String, Collection<String>> routedMap = new LinkedHashMap<>(routedDataSources.size());
        // 遍历路由到的目标数据源
        for (String each : routedDataSources) {
            // 再根据规则路由表：即根据order_id取模路由
            routedMap.put(each, routeTables(tableRule, each));
        }
        // 将得到的路由数据源和表信息封装到RoutingResult中，RoutingResult中有个TableUnits类型属性，TableUnits类中有个List<TableUnit> tableUnits属性，TableUnit包含三个属性：dataSourceName--数据源名称，logicTableName--逻辑表名称，actualTableName--实际表名称，例如：TableUnit:{dataSourceName:ds_jdbc_1, logicTableName:t_order, actualTableName: t_order_1}
        return generateRoutingResult(tableRule, routedMap);
    }
    

> **数据源路由详细解读** ：由于数据源的sharding策略为`databaseShardingStrategy(new
DatabaseShardingStrategy("user_id", new
ModuloDatabaseShardingAlgorithm()))`；且where条件为`where o.user_id=? AND
o.order_id=?`，即where条件中有user_id，根据取模路由策略，当user_id为奇数时，数据源为ds_jdbc_1；当user_id为偶数时，数据源为ds_jdbc_0；  
>  **表路由详细解读** ：表的sharding策略为`tableShardingStrategy(new
TableShardingStrategy("order_id", new
ModuloTableShardingAlgorithm()))`，即where条件中有order_id，根据取模路由策略，当order_id为奇数时，表为t_order_1；当order_id为偶数时，表为t_order_0；  
>  综上所述：最终需要执行的表数量为 _路由到的数据源个数路由到的实际表个数_ *；

>

> **实例1** ： **where o.order_id=1001 AND o.user_id=10**
，user_id=10所以路由得到数据源为ds_jdbc_0;
order_id=1001，路由得到实际表为t_order_1；那么最终只需在ds_jdbc_0这个数据源中的t_order_1表中执行即可；  
>  **实例2** ： **where o.order_id=1000**
，user_id没有值所以路由得到所有数据源ds_jdbc_0和ds_jdbc_1;
order_id=1000，路由得到实际表为t_order_0；那么最终需在ds_jdbc_0和ds_jdbc_1两个数据源中的t_order_0表中执行即可；  
>  **实例3** ： **where o.user_id=11** ，user_id=11所以路由得到数据源为ds_jdbc_1;
order_id没有值所以路由得到实际表为t_order_0和t_order_1；那么最终只需在ds_jdbc_1这个数据源中的t_order_0和t_order_1表中执行即可；

### ComplexRoutingEngine

待定… …

## 单表查询之执行

路由完成后就决定了SQL需要在哪些数据源的哪些实际表中执行，接下来以执行`SELECT o.* FROM t_order o where
o.user_id=10`为例分析下面这段Java代码sharding-jdbc是如何执行的：

> 根据前面的路由分析可知，这条SQL会路由到ds_jdbc_0这个数据源中，且在所有实际表([t_order_0,
t_order_1])中执行这个SQL；

    
    
    List<ResultSet> resultSets = new PreparedStatementExecutor(
                    getConnection().getShardingContext().getExecutorEngine(), routeResult.getSqlStatement().getType(), preparedStatementUnits, getParameters()).executeQuery();
    

执行的核心代码在 **ExecutorEngine** 中，核心源码如下：

    
    
    public <T> List<T> executePreparedStatement(
            final SQLType sqlType, final Collection<PreparedStatementUnit> preparedStatementUnits, final List<Object> parameters, final ExecuteCallback<T> executeCallback) {
        // preparedStatementUnits就是前面路由分析结果：执行SQL select o.* from t_order o where o.user_id=10时，只需在ds_jdbc_0这个数据源中的t_order_0和t_order_1两个实际表中执行即可；
        return execute(sqlType, preparedStatementUnits, Collections.singletonList(parameters), executeCallback);
    }
    
    private  <T> List<T> execute(
            final SQLType sqlType, final Collection<? extends BaseStatementUnit> baseStatementUnits, final List<List<Object>> parameterSets, final ExecuteCallback<T> executeCallback) {
        if (baseStatementUnits.isEmpty()) {
            return Collections.emptyList();
        }
        Iterator<? extends BaseStatementUnit> iterator = baseStatementUnits.iterator();
        // 第一个任务分离出来
        BaseStatementUnit firstInput = iterator.next();
        // 除第一个任务之外的任务异步执行
        ListenableFuture<List<T>> restFutures = asyncExecute(sqlType, Lists.newArrayList(iterator), parameterSets, executeCallback);
        T firstOutput;
        List<T> restOutputs;
        try {
            // 第一个任务同步执行[猜测是不是考虑到分库分表后只需路由到一个数据源中的一个表的SQL执行性能问题，优化这种SQL执行为同步执行？分库分表后，面向用户的API占用了99%的请求量，而这些API对应的SQL 99%只需要在一个数据源上的一个实际表执行即可，例如根据订单表根据user_id分库分表后，查询用户的订单信息这种场景]
            firstOutput = syncExecute(sqlType, firstInput, parameterSets, executeCallback);
            // 取得其他异步执行任务的结果
            restOutputs = restFutures.get();
            //CHECKSTYLE:OFF
        } catch (final Exception ex) {
            //CHECKSTYLE:ON
            ExecutorExceptionHandler.handleException(ex);
            return null;
        }
        List<T> result = Lists.newLinkedList(restOutputs);
        // 将第一个任务同步执行结果与其他任务异步执行结果合并就是最终的结果
        result.add(0, firstOutput);
        return result;
    }
    

异步执行核心代码：

    
    
    private final ListeningExecutorService executorService;
    
    public ExecutorEngine(final int executorSize) {
        // 异步执行的线程池是通过google-guava封装的线程池，设置了线程名称为增加了ShardingJDBC-***，增加了shutdown hook--应用关闭时最多等待60秒直到所有任务完成，从而实现优雅停机
        executorService = MoreExecutors.listeningDecorator(new ThreadPoolExecutor(
                executorSize, executorSize, 0, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<Runnable>(), new ThreadFactoryBuilder().setDaemon(true).setNameFormat("ShardingJDBC-%d").build()));
        MoreExecutors.addDelayedShutdownHook(executorService, 60, TimeUnit.SECONDS);
    }
    
    private <T> ListenableFuture<List<T>> asyncExecute(
            final SQLType sqlType, final Collection<BaseStatementUnit> baseStatementUnits, final List<List<Object>> parameterSets, final ExecuteCallback<T> executeCallback) {
        // 构造一个存放异步执行后的结果的list
        List<ListenableFuture<T>> result = new ArrayList<>(baseStatementUnits.size());
        final boolean isExceptionThrown = ExecutorExceptionHandler.isExceptionThrown();
        final Map<String, Object> dataMap = ExecutorDataMap.getDataMap();
        for (final BaseStatementUnit each : baseStatementUnits) {
            // 线程池方式异步执行所有SQL，线程池在ExecutorEngine的构造方法中初始化；
            result.add(executorService.submit(new Callable<T>() {
    
                @Override
                public T call() throws Exception {
                    return executeInternal(sqlType, each, parameterSets, executeCallback, isExceptionThrown, dataMap);
                }
            }));
        }
        // google-guava的方法--将所有异步执行结果转为list类型
        return Futures.allAsList(result);
    }
    

同步执行核心代码：

    
    
    private <T> T syncExecute(final SQLType sqlType, final BaseStatementUnit baseStatementUnit, final List<List<Object>> parameterSets, final ExecuteCallback<T> executeCallback) throws Exception {
            return executeInternal(sqlType, baseStatementUnit, parameterSets, executeCallback, ExecutorExceptionHandler.isExceptionThrown(), ExecutorDataMap.getDataMap());
        }
    

>
由同步执行核心代码和异步执行核心代码可知，最终都是调用`executeInternal()`，跟读这个方法的源码可知：最终就是在目标数据库表上执行`PreparedStatement`的`execute***()`方法；且在执行前会利用google-
guava的EventBus发布BEFORE_EXECUTE的事件（执行完成后，如果执行成功还会发布EXECUTE_SUCCESS事件，如果执行失败发布EXECUTE_FAILURE事件），部分核心源码如下：

    
    
    // 发布事件
    List<AbstractExecutionEvent> events = new LinkedList<>();
    if (parameterSets.isEmpty()) {
        // 构造无参SQL的事件（事件类型为BEFORE_EXECUTE）
        events.add(getExecutionEvent(sqlType, baseStatementUnit, Collections.emptyList()));
    }
    for (List<Object> each : parameterSets) {
        // 构造有参SQL的事件（事件类型为BEFORE_EXECUTE）
        events.add(getExecutionEvent(sqlType, baseStatementUnit, each));
    }
    // 调用google-guava的EventBus.post()提交事件
    for (AbstractExecutionEvent event : events) {
        EventBusInstance.getInstance().post(event);
    }
    
    try {
        // 执行SQL
        result = executeCallback.execute(baseStatementUnit);
    } catch (final SQLException ex) {
        // 如果执行过程中抛出SQLException，即执行SQL失败，那么post一个EXECUTE_FAILURE类型的事件
        for (AbstractExecutionEvent each : events) {
            each.setEventExecutionType(EventExecutionType.EXECUTE_FAILURE);
            each.setException(Optional.of(ex));
            EventBusInstance.getInstance().post(each);
            ExecutorExceptionHandler.handleException(ex);
        }
        return null;
    }
    for (AbstractExecutionEvent each : events) {
        // // 如果执行成功，那么post一个EXECUTE_SUCCESS类型的事件
        each.setEventExecutionType(EventExecutionType.EXECUTE_SUCCESS);
        EventBusInstance.getInstance().post(each);
    }
    

接下来需要对并行执行后得到的结果集进行merge，下面的sharding-jdbc源码分析系列文章继续对其进行分析；

## EventBus

> 说明： **EventBus** 是google-guava提供的消息发布-订阅类库；  
>  google-guava的EventBus正确打开姿势：

>

>   1. 发布事务：调用EventBus的post()–sharding-
jdbc中发布事务：EventBusInstance.getInstance().post(each)；

>   2. 订阅事务：调用EventBus的register()–sharding-
jdbc中注册事务：EventBusInstance.getInstance().register(new
BestEffortsDeliveryListener())；

>

EventBusInstance源码如下– **EventBus** 全类名为`com.google.common.eventbus.EventBus`：

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class EventBusInstance {
    
        private static final EventBus INSTANCE = new EventBus();
    
        /**
         * Get event bus instance.
         * 
         * @return event bus instance
         */
        public static EventBus getInstance() {
            return INSTANCE;
        }
    }
    

