  * 1 单表查询之结果合并
    * 1.1 OrderByStreamResultSetMerger
    * 1.2 LimitDecoratorResultSetMerger
    * 1.3 IteratorStreamResultSetMerger

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/b413a282cab9>

* * *

# 单表查询之结果合并

接下来以执行`SELECT o.* FROM t_order o where o.user_id=10 order by o.order_id desc
limit 2,3`分析下面这段Java代码是如何对结果进行合并的：

    
    
    result = new ShardingResultSet(resultSets, new MergeEngine(resultSets, (SelectStatement) routeResult.getSqlStatement()).merge());</code> 
    
    MergeEngine.merge()方法的源码如下：
    
    <code class="java">public ResultSetMerger merge() throws SQLException {
        selectStatement.setIndexForItems(columnLabelIndexMap);
        return decorate(build());
    }
    

build()方法源码如下:

    
    
    private ResultSetMerger build() throws SQLException {
        // 说明：GroupBy***ResultSetMerger在第六篇文章单独讲解，所以此次分析的SQL条件中没有group by
        if (!selectStatement.getGroupByItems().isEmpty() || !selectStatement.getAggregationSelectItems().isEmpty()) {
            if (selectStatement.isSameGroupByAndOrderByItems()) {
                return new GroupByStreamResultSetMerger(columnLabelIndexMap, resultSets, selectStatement);
            } else {
                return new GroupByMemoryResultSetMerger(columnLabelIndexMap, resultSets, selectStatement);
            }
        }
        // 如果select语句中有order by字段，那么需要OrderByStreamResultSetMerger对结果处理
        if (!selectStatement.getOrderByItems().isEmpty()) {
            return new OrderByStreamResultSetMerger(resultSets, selectStatement.getOrderByItems());
        }
        return new IteratorStreamResultSetMerger(resultSets);
    }
    

>
根据这段代码可知，其作用是根据sql语句选择多个不同的ResultSetMerger对结果进行合并处理，ResultSetMerger实现有这几种：GroupByStreamResultSetMerger，GroupByMemoryResultSetMerger，OrderByStreamResultSetMerger，IteratorStreamResultSetMerger，LimitDecoratorResultSetMerger；以测试SQL`SELECT
o.* FROM t_order o where o.user_id=10 order by o.order_id desc limit
2,3`为例，没有group by，但是有order
by，所以使用到了OrderByStreamResultSetMerger和LimitDecoratorResultSetMerger对结果进行合并（GroupByStreamResultSetMerger&GroupByMemoryResultSetMerger后面单独讲解）

decorate()源码如下：

    
    
    private ResultSetMerger decorate(final ResultSetMerger resultSetMerger) throws SQLException {
        ResultSetMerger result = resultSetMerger;
        // 如果SQL语句中有limist，还需要LimitDecoratorResultSetMerger配合进行结果归并；
        if (null != selectStatement.getLimit()) {
            result = new LimitDecoratorResultSetMerger(result, selectStatement.getLimit());
        }
        return result;
    }
    

> 接下来将以执行SQL：`SELECT o.* FROM t_order o where o.user_id=10 order by o.order_id
desc limit 2,3`（该SQL会被改写成`SELECT o.* , o.order_id AS ORDER_BY_DERIVED_0 FROM
t_order_0 o where o.user_id=? order by o.order_id desc limit
2,3`）为例，一一讲解OrderByStreamResultSetMerger，LimitDecoratorResultSetMerger和IteratorStreamResultSetMerger，了解这几个ResultSetMerger的原理；

## OrderByStreamResultSetMerger

OrderByStreamResultSetMerger的核心源码如下：

    
    
    private final Queue<OrderByValue> orderByValuesQueue;
    
    public OrderByStreamResultSetMerger(final List<ResultSet> resultSets, final List<OrderItem> orderByItems) throws SQLException {
        // sql中order by列的信息，实例sql是order by order_id desc，即此处就是order_id
        this.orderByItems = orderByItems;
        // 初始化一个优先级队列，优先级队列中的元素会根据OrderByValue中compareTo()方法排序，并且SQL重写后发送到多少个目标实际表，List<ResultSet>的size就有多大，Queue的capacity就有多大；
        this.orderByValuesQueue = new PriorityQueue<>(resultSets.size());
        // 将结果压入队列中
        orderResultSetsToQueue(resultSets);
        isFirstNext = true;
    }
    
    private void orderResultSetsToQueue(final List<ResultSet> resultSets) throws SQLException {
        // 遍历resultSets--在多少个目标实际表上执行SQL，该集合的size就有多大
        for (ResultSet each : resultSets) {
            // 将ResultSet和排序列信息封装成一个OrderByValue类型
            OrderByValue orderByValue = new OrderByValue(each, orderByItems);
            // 如果值存在，那么压入队列中
            if (orderByValue.next()) {
                orderByValuesQueue.offer(orderByValue);
            }
        }
        // 重置currentResultSet的位置：如果队列不为空，那么将队列的顶部(peek)位置设置为currentResultSet的位置
        setCurrentResultSet(orderByValuesQueue.isEmpty() ? resultSets.get(0) : orderByValuesQueue.peek().getResultSet());
    }
    
    @Override
    public boolean next() throws SQLException {
        // 调用next()判断是否还有值, 如果队列为空, 表示没有任何值, 那么直接返回false
        if (orderByValuesQueue.isEmpty()) {
            return false;
        }
        // 如果队列不为空, 那么第一次一定返回true；即有结果可取（且将isFirstNext置为false，表示接下来的请求都不是第一次请求next()方法）
        if (isFirstNext) {
            isFirstNext = false;
            return true;
        }
        // 从队列中弹出第一个元素（因为是优先级队列，所以poll()返回的值，就是此次要取的值）
        OrderByValue firstOrderByValue = orderByValuesQueue.poll();
        // 如果它的next()存在，那么将它的next()再添加到队列中
        if (firstOrderByValue.next()) {
            orderByValuesQueue.offer(firstOrderByValue);
        }
        // 队列中所有元素全部处理完后就返回false
        if (orderByValuesQueue.isEmpty()) {
            return false;
        }
        // 再次重置currentResultSet的位置为队列的顶部位置；
        setCurrentResultSet(orderByValuesQueue.peek().getResultSet());
        return true;
    }
    

> 继续深入剖析：这段代码初看可能有点绕，假设运行SQL`SELECT o.* FROM t_order o where o.user_id=10
order by o.order_id desc limit
3`会分发到两个目标实际表，且第一个实际表返回的结果是1，3，5，7，9；第二个实际表返回的结果是2，4，6，8，10；那么，经过OrderByStreamResultSetMerger的构造方法中的orderResultSetsToQueue()方法后，`Queue
orderByValuesQueue`中包含两个OrderByValue，一个是10，一个是9；接下来取值运行过程如下：

>

>   1.
取得10，并且10的next()是8，然后执行orderByValuesQueue.offer(8);，这时候orderByValuesQueue中包含8和9；

>   2.
取得9，并且9的next()是7，然后执行orderByValuesQueue.offer(7);，这时候orderByValuesQueue中包含7和8；

>   3.
取得8，并且8的next()是6，然后执行orderByValuesQueue.offer(6);，这时候orderByValuesQueue中包含7和6；  
>  取值数量已经达到limit 3的限制（源码在LimitDecoratorResultSetMerger中的next()方法中），退出；

>

这段代码运行示意图如下所示：

![201805051001](http://cmsblogs.qiniudn.com/201805051001.png)

![201805051002](http://cmsblogs.qiniudn.com/201805051002.png)

## LimitDecoratorResultSetMerger

LimitDecoratorResultSetMerger核心源码如下：

    
    
    public LimitDecoratorResultSetMerger(final ResultSetMerger resultSetMerger, final Limit limit) throws SQLException {
        super(resultSetMerger);
        // limit赋值（Limit对象包括limit m,n中的m和n两个值）
        this.limit = limit;
        // 判断是否会跳过所有的结果项，即判断是否有符合条件的结果
        skipAll = skipOffset();
    }
    
    private boolean skipOffset() throws SQLException {
        // 假定limit.getOffsetValue()就是offset，实例sql中为limit 2,3，所以offset=2
        for (int i = 0; i < limit.getOffsetValue(); i++) {
            // 尝试从OrderByStreamResultSetMerger生成的优先级队列中跳过offset个元素，如果.next()一直为true，表示有足够符合条件的结果，那么返回false；否则没有足够符合条件的结果，那么返回true；即skilAll=true就表示跳过了所有没有符合条件的结果；
            if (!getResultSetMerger().next()) {
                return true;
            }
        }
        // limit m,n的sql会被重写为limit 0, m+n，所以limit.isRowCountRewriteFlag()为true，rowNumber的值为0；
        rowNumber = limit.isRowCountRewriteFlag() ? 0 : limit.getOffsetValue();
        return false;
    }
    
    @Override
    public boolean next() throws SQLException {
        // 如果skipAll为true，即跳过所有，表示没有任何符合条件的值，那么返回false
        if (skipAll) {
            return false;
        }
        if (limit.getRowCountValue() > -1) {
            // 每次next()获取值后，rowNumber自增，当自增rowCountValue次后，就不能再往下继续取值了，因为条件limit 2,3（rowCountValue=3）限制了
            return ++rowNumber <= limit.getRowCountValue() && getResultSetMerger().next();
        }
        return getResultSetMerger().next();
    }
    

## IteratorStreamResultSetMerger

构造方法核心源码：

    
    
    private final Iterator<ResultSet> resultSets;
    
    public IteratorStreamResultSetMerger(final List<ResultSet> resultSets) {
        // 将List<ResultSet>改成Iterator<ResultSet>，方便接下来迭代取得结果；
        this.resultSets = resultSets.iterator();
        // 重置currentResultSet
        setCurrentResultSet(this.resultSets.next());
    }
    

