  * 1 1\. Preconditions
  * 2 2\. 自定义异常
    * 2.1 sharding-jdbc中抛出自定义日志场景
  * 3 总结

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/0b1604b6b8e6>

* * *

一般项目都会有自己的一套异常处理方式，sharding-jdbc也不以外，sharding-jdbc源码处理异常的方式主要有下面2种方式：

  1. Preconditions
  2. 自定义异常

# 1\. Preconditions

google-guava的Preconditions用于条件检查，不符合预期的话则抛出异常，并可以重写异常信息。google-
guava源码中Preconditions的注释如下：

> Static convenience methods that help a method or constructor check whether
it was invoked correctly (whether its preconditions have been met). These
methods generally accept a boolean expression which is expected to be true (or
in the case of checkNotNull, an object reference which is expected to be non-
null). When false (or null) is passed instead, the Preconditions method throws
an unchecked exception, which helps the calling method communicate to its
caller that that caller has made a mistake.

>

>
即帮助我们检查方法或者构造函数是否被正确调用，一般接收布尔表达式，期望布尔表达式的值为true；如果布尔表达式的值为false，就会抛出异常，让调用者知道错误的原因。

其部分static方法实现源码如下：

  * 检查参数是否正确–expression就是判断方法的参数的表达式，errorMessage是自定义异常，不允许为空；

    
    
    // Ensures the truth of an expression involving one or more parameters to the calling method.
    public static void checkArgument(boolean expression, @Nullable Object errorMessage) {
        if (!expression) {
            throw new IllegalArgumentException(String.valueOf(errorMessage));
        }
    }
    

  * 检查状态是否正确–expression就是判断状态的参数的表达式，errorMessage是自定义异常，不允许为空；

    
    
    // Ensures the truth of an expression involving the state of the calling instance, but not involving any parameters to the calling method.
    public static void checkState(boolean expression, @Nullable Object errorMessage) {
        if (!expression) {
            throw new IllegalStateException(String.valueOf(errorMessage));
        }
    }
    

  * 检查不允许为空–reference就是待检查参数，errorMessage是自定义异常，不允许为空；

    
    
    // Ensures that an object reference passed as a parameter to the calling method is not null.
    public static <T> T checkNotNull(T reference, @Nullable Object errorMessage) {
        if (reference == null) {
            throw new NullPointerException(String.valueOf(errorMessage));
        }
        return reference;
    }
    

  * 检查下标是否越界–index就是待检查下标参数，size就是集合的size，errorMessage是自定义异常，不允许为空；

    
    
    /**
     * Ensures that {@code index} specifies a valid <i>element</i> in an array, list or string of size
     * {@code size}. An element index may range from zero, inclusive, to {@code size}, exclusive.
     */
    public static int checkElementIndex(
            int index, int size, @Nullable String desc) {
        // Carefully optimized for execution by hotspot (explanatory comment above)
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException(badElementIndex(index, size, desc));
        }
        return index;
    }
    

接下来我们看一下sharding-jdbc源码里张亮大神是如何使用Preconditions的：

  1. **Preconditions.checkArgument()** 的使用  
源码如下：

    
    
    @SuppressWarnings("unchecked")
    private <T extends ShardingStrategy> T buildShardingAlgorithmClassName(final List<String> shardingColumns, ... ...) {
        ... ...
        // 如果是SingleKeyShardingAlgorithm，那么sharding column只能有一个
        if (shardingAlgorithm instanceof SingleKeyShardingAlgorithm) {
            Preconditions.checkArgument(1 == shardingColumns.size(), "Sharding-JDBC: SingleKeyShardingAlgorithm must have only ONE sharding column");
            ... ...
        }
        ... ...
    }
    

  1. **Preconditions.checkState()** 的使用  
源码如下：

    
    
    private Collection<String> routeDataSources(final TableRule tableRule) {
        ... ...
        Collection<String> result = strategy.doStaticSharding(tableRule.getActualDatasourceNames(), shardingValues);
        // result是路由结果，即原生SQL路由后需要在哪些数据库中执行，很明显result肯定不可能为空；
        Preconditions.checkState(!result.isEmpty(), "no database route info");
        return result;
    }
    

  1. **Preconditions.checkElementIndex()** 的使用  
源码如下（不是来自sharding-jdbc源码中，而是笔者写的）：

    
    
    private static String getFromList(int index){
        // 如果从集合中取数据, 首先校验下标
        Preconditions.checkElementIndex(index, list.size(), "index is too big, list size is "+list.size()+". ");
        return list.get(index);
    }
    

> 总结：很明显，借助google_guava的Preconditions能够让我们的代码更优雅，更简洁；

# 2\. 自定义异常

sharding-jdbc自定义了异常处理类`ShardingJdbcException`：

    
    
    public class ShardingJdbcException extends RuntimeException {
    
        // 异常类构造方法：异常信息errorMessage中有多个参数，例如：throw new ShardingJdbcException("Unsupported Date type:%s", convertType);
        public ShardingJdbcException(final String errorMessage, final Object... args) {
            super(String.format(errorMessage, args));
        }
    
        // 把catch的异常转成ShardingJdbcException类型的异常，并重写异常信息
        public ShardingJdbcException(final String message, final Exception cause) {
            super(message, cause);
        }
    
        // 把异常转成ShardingJdbcException类型的异常，不重写异常信息
        public ShardingJdbcException(final Exception cause) {
            super(cause);
        }
    }
    

## sharding-jdbc中抛出自定义日志场景

— 抛出自定义异常并重写有参数的异常信息

    
    
    if (result.isEmpty()) {
        throw new ShardingJdbcException("Cannot find table rule and default data source with logic tables: "%s"", logicTables);
    }
    

  * 将IllegalAccessException或者InvocationTargetException类型的异常转化为ShardingJdbcException异常，并重写异常信息为”Invoke jdbc method exception”

    
    
    try {
        method.invoke(target, arguments);
    } catch (final IllegalAccessException | InvocationTargetException ex) {
        throw new ShardingJdbcException("Invoke jdbc method exception", ex);
    }
    

  * 把异常转成ShardingJdbcException类型的异常，不重写异常信息

    
    
    public static void handleException(final Exception exception) {
        if (isExceptionThrown()) {
            throw new ShardingJdbcException(exception);
        }
        log.error("exception occur: ", exception);
    }
    

# 总结

sharding-jdbc对异常的处理还是很有参考价值的，自定义异常类型封装业务异常，我们一般都会这么做；但是如果能借鉴sharding-
jdbc的源码，再增加对`Preconditions`的使用，很明显能够让代码的逼格提升不少^^；  
“`

