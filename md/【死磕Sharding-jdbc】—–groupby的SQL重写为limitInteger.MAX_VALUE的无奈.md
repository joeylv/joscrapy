  * 1 构造数据
  * 2 执行SQL
  * 3 分析
  * 4 延伸

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/e541ac380e18>

* * *

这篇文章源于[sharding-
jdbc源码分析之重写](https://www.jianshu.com/p/c7854327634f)的遗留问题，相关sharding-jdbc源码如下：

    
    
    private void appendLimitRowCount(final SQLBuilder sqlBuilder, final RowCountToken rowCountToken, final int count, final List<SQLToken> sqlTokens, final boolean isRewrite) {
        SelectStatement selectStatement = (SelectStatement) sqlStatement;
        Limit limit = selectStatement.getLimit();
        if (!isRewrite) {
            ... ...
        } else if ((!selectStatement.getGroupByItems().isEmpty() || !selectStatement.getAggregationSelectItems().isEmpty()) && !selectStatement.isSameGroupByAndOrderByItems()) {
            // 如果要重写sql中的limit的话，且sql中有group by或者有group by & order by，例如"select user_id, sum(score) from t_order group by user_id order by sum(score) desc limit 5"，那么limit 5需要重写为limit Integer.MAX_VALUE，原因接下来分析
            sqlBuilder.appendLiterals(String.valueOf(Integer.MAX_VALUE));
        } else {
            ... ...
        }
        ... ...
    }
    

# 构造数据

为了解释为什么limit rowCount中的rowCount需要重写为Integer.MAX_VALUE，需要先构造一些数据，如下图所示：

![2018050510021](http://cmsblogs.qiniudn.com/2018050510021.png)

如果不分库分表的话，数据如下图所示：

![2018050510022](http://cmsblogs.qiniudn.com/2018050510022.png)

# 执行SQL

假定执行如下SQL：

    
    
    select user_id, sum(score) from t_order group by user_id order by sum(score) desc limit 5;
    

结果如下所示：

![2018050510023](http://cmsblogs.qiniudn.com/2018050510023.png)

假定`select user_id, sum(score) from t_order group by user_id order by
sum(score) desc limit 5;`这个SQL不重写为`limit 0,
Integer.MAX_VALUE`，那么`t_order_0`和`t_order_1`的结果分别如下；  
`t_order_0`的结果：

![2018050510024](http://cmsblogs.qiniudn.com/2018050510024.png)

`t_order_1`的结果：

![2018050510025](http://cmsblogs.qiniudn.com/2018050510025.png)

路由到两个表的执行结果归并后的结果如下：

![2018050510026](http://cmsblogs.qiniudn.com/2018050510026.png)

# 分析

根据执行结果可知，主要差异在于，真实结果有user_id为20，21的数据。我们在看一下`t_order_0`和`t_order_1`两个分表中这两个user_id的数据有什么特殊之处：

![2018050510027](http://cmsblogs.qiniudn.com/2018050510027.png)

在`t_order_1`这个分表中，由于user_id为20，21的score值在TOP
5以外。但是合并`t_order_0`和`t_order_1`两个分表的结果，user_id为20的sum(score)能够排在第一（18+18=36）；所以，
**如果group by这类的SQL不重写为`limit 0, Integer.MAX_VALUE`的话，会导致结果有误** 。所以sharding-
jdbc的源码必须要这样重写，没有其他办法！

# 延伸

事实上不只是sharding-jdbc，任何有sharding概念的中间件例如es，都要这么处理，因为sharding后数据处理的流程几乎都要经过
**解析- >重写->路由->执行->结果归并**这几个阶段；

