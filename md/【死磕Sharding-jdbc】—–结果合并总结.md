  * 1 分页性能分析
    * 1.1 性能瓶颈
    * 1.2 Sharding-JDBC的优化
    * 1.3 更好的分页解决方案
    * 1.4 是否需要这种分页

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/a1403e8566ac>

* * *

# 分页性能分析

## 性能瓶颈

查询偏移量过大的分页会导致数据库获取数据性能低下，以MySQL为例：

    
    
    SELECT * FROM t_order ORDER BY id LIMIT 1000000, 10
    

这句SQL会使得MySQL在无法利用索引的情况下跳过1000000条记录后，再获取10条记录，其性能可想而知。而在分库分表的情况下（假设分为2个库），为了保证数据的正确性，SQL会改写为：

    
    
    SELECT * FROM t_order ORDER BY id LIMIT 0, 1000010
    

即将偏移量前的记录全部取出，并仅获取排序后的最后10条记录。这会在数据库本身就执行很慢的情况下，进一步加剧性能瓶颈。因为原SQL仅需要传输10条记录至客户端，而改写之后的SQL则会传输1000010*2的记录至客户端。

## Sharding-JDBC的优化

Sharding-JDBC进行了2个方面的优化。

首先，Sharding-JDBC采用流式处理 + 归并排序的方式来避免内存的过量占用。Sharding-
JDBC的SQL改写，不可避免的占用了额外的带宽，但并不会导致内存暴涨。  
与直觉不同，大多数人认为Sharding-JDBC会将1000010*2记录全部加载至内存，进而占用大量内存而导致内存溢出。  
但由于每个结果集的记录是有序的，因此Sharding-
JDBC每次比较仅获取各个分片的当前结果集记录，驻留在内存中的记录仅为当前路由到的分片的结果集的当前游标指向而已。  
对于本身即有序的待排序对象，归并排序的时间复杂度仅为O(n)，性能损耗很小。

其次，Sharding-
JDBC对仅落至单分片的查询进行进一步优化。落至单分片查询的请求并不需要改写SQL也可以保证记录的正确性，因此在此种情况下，Sharding-
JDBC并未进行SQL改写，从而达到节省带宽的目的。

## 更好的分页解决方案

由于LIMIT并不能通过索引查询数据，因此如果可以保证ID的连续性，通过ID进行分页是比较好的解决方案：

    
    
    SELECT * FROM t_order WHERE id > 100000 AND id <= 100010 ORDER BY id
    

或通过记录上次查询结果的最后一条记录的ID进行下一页的查询：

    
    
    SELECT * FROM t_order WHERE id > 100000 LIMIT 10
    

摘自：[sharding-
jdbc使用指南☞分页及子查询](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2F1.x%2Fdocs%2F02-guide%2Fsubquery%2F)

## 是否需要这种分页

无论是`SELECT * FROM t_order ORDER BY id LIMIT 0, 100010`或者`SELECT * FROM t_order
WHERE id &gt; 100000 LIMIT 10`，性能都一般般，后者只是稍微好点而已，但是由于LIMIT的存在，mysql都需要排序；

是否能从产品角度或者用户习惯等方面解决或者避免这个问题？

  * 用户习惯结合产品需求解决方案：

> 比如我们以前有个 **每日TOP榜单** 需求，分析用户行为一般不会无限制往下滑，即使有这种用户，也是极少数，可以忽略。这样的话，可以通过SQL`***
LIMIT 300`只查询10页总计300个TOP应用，然后把这些数据以list结构保存到redis中。这样的话，用户查看 **每日TOP榜单**
只需通过`LRANGE key start stop`从redis缓存中取数据即可，且限制查询的offset不允许超过300；

