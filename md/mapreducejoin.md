# MapReduce Join

对两份数据data1和data2进行关键词连接是一个很通用的问题，如果数据量比较小，可以在内存中完成连接。

如果数据量比较大，在内存进行连接操会发生OOM。mapreduce join可以用来解决大数据的连接。

## 1 思路

### 1.1 reduce join

在map阶段,
把关键字作为key输出，并在value中标记出数据是来自data1还是data2。因为在shuffle阶段已经自然按key分组，reduce阶段，判断每一个value是来自data1还是data2,在内部分成2组，做集合的乘积。

这种方法有2个问题：

> 1, map阶段没有对数据瘦身，shuffle的网络传输和排序性能很低。

>

> 2, reduce端对2个集合做乘积计算，很耗内存，容易导致OOM。

### 1.2 map join

两份数据中，如果有一份数据比较小，小数据全部加载到内存，按关键字建立索引。大数据文件作为map的输入文件，对map()函数每一对输入，都能够方便地和已加载到内存的小数据进行连接。把连接结果按key输出，经过shuffle阶段，reduce端得到的就是已经按key分组的，并且连接好了的数据。

这种方法，要使用hadoop中的DistributedCache把小数据分布到各个计算节点，每个map节点都要把小数据库加载到内存，按关键字建立索引。

> 这种方法有明显的局限性：有一份数据比较小，在map端，能够把它加载到内存，并进行join操作。

### 1.3 使用内存服务器，扩大节点的内存空间

针对map join，可以把一份数据存放到专门的内存服务器，在map()方法中，对每一个<key,value style="margin: 0px;
padding: 0px;">的输入对，根据key到内存服务器中取出数据，进行连接

### 1.4 使用BloomFilter过滤空连接的数据

对其中一份数据在内存中建立BloomFilter，另外一份数据在连接之前，用BloomFilter判断它的key是否存在，如果不存在，那这个记录是空连接，可以忽略。

### 1.5 使用mapreduce专为join设计的包

在mapreduce包里看到有专门为join设计的包，对这些包还没有学习，不知道怎么使用，只是在这里记录下来，作个提醒。

> jar： mapreduce-client-core.jar

>

> package： org.apache.hadoop.mapreduce.lib.join

# 2 实现map join

相对而言，map join更加普遍，下面的代码使用DistributedCache实现map join

## 2.1 背景

有客户数据customer和订单数据orders。

**customer**  
  
<table>  
<tr>  
<th>

客户编号

</th>  
<th>

姓名

</th>  
<th>

地址

</th>  
<th>

电话

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr> </table>

** order**  
  
<table>  
<tr>  
<th>

订单编号

</th>  
<th>

客户编号

</th>  
<th>

其它字段被忽略

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

1

</td>  
<td>

50

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

1

</td>  
<td>

200

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

3

</td>  
<td>

15

</td> </tr>  
<tr>  
<td>

4

</td>  
<td>

3

</td>  
<td>

350

</td> </tr>  
<tr>  
<td>

5

</td>  
<td>

3

</td>  
<td>

58

</td> </tr>  
<tr>  
<td>

6

</td>  
<td>

1

</td>  
<td>

42

</td> </tr>  
<tr>  
<td>

7

</td>  
<td>

1

</td>  
<td>

352

</td> </tr>  
<tr>  
<td>

8

</td>  
<td>

2

</td>  
<td>

1135

</td> </tr>  
<tr>  
<td>

9

</td>  
<td>

2

</td>  
<td>

400

</td> </tr>  
<tr>  
<td>

10

</td>  
<td>

2

</td>  
<td>

2000

</td> </tr>  
<tr>  
<td>

11

</td>  
<td>

2

</td>  
<td>

300

</td> </tr> </table>

要求对customer和orders按照客户编号进行连接，结果要求对客户编号分组，对订单编号排序，对其它字段不作要求  
  
<table>  
<tr>  
<th>

客户编号

</th>  
<th>

订单编号

</th>  
<th>

订单金额

</th>  
<th>

姓名

</th>  
<th>

地址

</th>  
<th>

电话

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

1

</td>  
<td>

50

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

2

</td>  
<td>

200

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

6

</td>  
<td>

42

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

7

</td>  
<td>

352

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

8

</td>  
<td>

1135

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

9

</td>  
<td>

400

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

10

</td>  
<td>

2000

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

11

</td>  
<td>

300

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

3

</td>  
<td>

15

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

4

</td>  
<td>

350

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

5

</td>  
<td>

58

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr> </table>

  1. 在提交job的时候，把小数据通过DistributedCache分发到各个节点。
  2. map端使用DistributedCache读到数据，在内存中构建映射关系--如果使用专门的内存服务器，就把数据加载到内存服务器，map()节点可以只保留一份小缓存；如果使用BloomFilter来加速，在这里就可以构建；
  3. map()函数中，对每一对<key,value style="margin: 0px; padding: 0px;">，根据key到第2)步构建的映射里面中找出数据，进行连接，输出。

### 2\. 常见的join方法介绍

假设要进行join的数据分别来自File1和File2.

#### 2.1 reduce side join

reduce side join是一种最简单的join方式，其主要思想如下：  
在map阶段，map函数同时读取两个文件File1和File2，为了区分两种来源的key/value数据对，对每条数据打一个标签（tag）,比如：tag=0表示来自文件File1，tag=2表示来自文件File2。即：map阶段的主要任务是对不同文件中的数据打标签。  
在reduce阶段，reduce函数获取key相同的来自File1和File2文件的value list，
然后对于同一个key，对File1和File2中的数据进行join（笛卡尔乘积）。即：reduce阶段进行实际的连接操作。

#### 2.2 map side join

之所以存在reduce side join，是因为在map阶段不能获取所有需要的join字段，即：同一个key对应的字段可能位于不同map中。Reduce
side join是非常低效的，因为shuffle阶段要进行大量的数据传输。  
Map side
join是针对以下场景进行的优化：两个待连接表中，有一个表非常大，而另一个表非常小，以至于小表可以直接存放到内存中。这样，我们可以将小表复制多份，让每个map
task内存中存在一份（比如存放到hash table中），然后只扫描大表：对于大表中的每一条记录key/value，在hash
table中查找是否有相同的key的记录，如果有，则连接后输出即可。  
为了支持文件的复制，Hadoop提供了一个类DistributedCache，使用该类的方法如下：  
（1）用户使用静态方法DistributedCache.addCacheFile()指定要复制的文件，它的参数是文件的URI（如果是HDFS上的文件，可以这样：hdfs://namenode:9000/home/XXX/file，其中9000是自己配置的NameNode端口号）。JobTracker在作业启动之前会获取这个URI列表，并将相应的文件拷贝到各个TaskTracker的本地磁盘上。（2）用户使用DistributedCache.getLocalCacheFiles()方法获取文件目录，并使用标准的文件读写API读取相应的文件。

#### 2.3 SemiJoin

SemiJoin，也叫半连接，是从分布式数据库中借鉴过来的方法。它的产生动机是：对于reduce side
join，跨机器的数据传输量非常大，这成了join操作的一个瓶颈，如果能够在map端过滤掉不会参加join操作的数据，则可以大大节省网络IO。  
实现方法很简单：选取一个小表，假设是File1，将其参与join的key抽取出来，保存到文件File3中，File3文件一般很小，可以放到内存中。在map阶段，使用DistributedCache将File3复制到各个TaskTracker上，然后将File2中不在File3中的key对应的记录过滤掉，剩下的reduce阶段的工作与reduce
side join相同。  
更多关于半连接的介绍，可参考：半连接介绍：http://wenku.baidu.com/view/ae7442db7f1922791688e877.html

#### 2.4 reduce side join + BloomFilter

在某些情况下，SemiJoin抽取出来的小表的key集合在内存中仍然存放不下，这时候可以使用BloomFiler以节省空间。  
BloomFilter最常见的作用是：判断某个元素是否在一个集合里面。它最重要的两个方法是：add()
和contains()。最大的特点是不会存在false
negative，即：如果contains()返回false，则该元素一定不在集合中，但会存在一定的true
negative，即：如果contains()返回true，则该元素可能在集合中。  
因而可将小表中的key保存到BloomFilter中，在map阶段过滤大表，可能有一些不在小表中的记录没有过滤掉（但是在小表中的记录一定不会过滤掉），这没关系，只不过增加了少量的网络IO而已。  
更多关于BloomFilter的介绍，可参考：http://blog.csdn.net/jiaomeng/article/details/1495500

### 3\. 二次排序

在Hadoop中，默认情况下是按照key进行排序，如果要按照value进行排序怎么办？即：对于同一个key，reduce函数接收到的value
list是按照value排序的。这种应用需求在join操作中很常见，比如，希望相同的key中，小表对应的value排在前面。  
有两种方法进行二次排序，分别为：buffer and in memory sort和 value-to-key conversion。  
对于buffer and in memory sort，主要思想是：在reduce()函数中，将某个key对应的所有value保存下来，然后进行排序。
这种方法最大的缺点是：可能会造成out of memory。  
对于value-to-key
conversion，主要思想是：将key和部分value拼接成一个组合key（实现WritableComparable接口或者调用setSortComparatorClass函数），这样reduce获取的结果便是先按key排序，后按value排序的结果，需要注意的是，用户需要自己实现Paritioner，以便只按照key进行数据划分。Hadoop显式的支持二次排序，在Configuration类中有个setGroupingComparatorClass()方法，可用于设置排序group的key值

# MapReduce Join

对两份数据data1和data2进行关键词连接是一个很通用的问题，如果数据量比较小，可以在内存中完成连接。

如果数据量比较大，在内存进行连接操会发生OOM。mapreduce join可以用来解决大数据的连接。

## 1 思路

### 1.1 reduce join

在map阶段,
把关键字作为key输出，并在value中标记出数据是来自data1还是data2。因为在shuffle阶段已经自然按key分组，reduce阶段，判断每一个value是来自data1还是data2,在内部分成2组，做集合的乘积。

这种方法有2个问题：

> 1, map阶段没有对数据瘦身，shuffle的网络传输和排序性能很低。

>

> 2, reduce端对2个集合做乘积计算，很耗内存，容易导致OOM。

### 1.2 map join

两份数据中，如果有一份数据比较小，小数据全部加载到内存，按关键字建立索引。大数据文件作为map的输入文件，对map()函数每一对输入，都能够方便地和已加载到内存的小数据进行连接。把连接结果按key输出，经过shuffle阶段，reduce端得到的就是已经按key分组的，并且连接好了的数据。

这种方法，要使用hadoop中的DistributedCache把小数据分布到各个计算节点，每个map节点都要把小数据库加载到内存，按关键字建立索引。

> 这种方法有明显的局限性：有一份数据比较小，在map端，能够把它加载到内存，并进行join操作。

### 1.3 使用内存服务器，扩大节点的内存空间

针对map join，可以把一份数据存放到专门的内存服务器，在map()方法中，对每一个<key,value style="margin: 0px;
padding: 0px;">的输入对，根据key到内存服务器中取出数据，进行连接

### 1.4 使用BloomFilter过滤空连接的数据

对其中一份数据在内存中建立BloomFilter，另外一份数据在连接之前，用BloomFilter判断它的key是否存在，如果不存在，那这个记录是空连接，可以忽略。

### 1.5 使用mapreduce专为join设计的包

在mapreduce包里看到有专门为join设计的包，对这些包还没有学习，不知道怎么使用，只是在这里记录下来，作个提醒。

> jar： mapreduce-client-core.jar

>

> package： org.apache.hadoop.mapreduce.lib.join

# 2 实现map join

相对而言，map join更加普遍，下面的代码使用DistributedCache实现map join

## 2.1 背景

有客户数据customer和订单数据orders。

**customer**  
  
<table>  
<tr>  
<th>

客户编号

</th>  
<th>

姓名

</th>  
<th>

地址

</th>  
<th>

电话

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr> </table>

** order**  
  
<table>  
<tr>  
<th>

订单编号

</th>  
<th>

客户编号

</th>  
<th>

其它字段被忽略

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

1

</td>  
<td>

50

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

1

</td>  
<td>

200

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

3

</td>  
<td>

15

</td> </tr>  
<tr>  
<td>

4

</td>  
<td>

3

</td>  
<td>

350

</td> </tr>  
<tr>  
<td>

5

</td>  
<td>

3

</td>  
<td>

58

</td> </tr>  
<tr>  
<td>

6

</td>  
<td>

1

</td>  
<td>

42

</td> </tr>  
<tr>  
<td>

7

</td>  
<td>

1

</td>  
<td>

352

</td> </tr>  
<tr>  
<td>

8

</td>  
<td>

2

</td>  
<td>

1135

</td> </tr>  
<tr>  
<td>

9

</td>  
<td>

2

</td>  
<td>

400

</td> </tr>  
<tr>  
<td>

10

</td>  
<td>

2

</td>  
<td>

2000

</td> </tr>  
<tr>  
<td>

11

</td>  
<td>

2

</td>  
<td>

300

</td> </tr> </table>

要求对customer和orders按照客户编号进行连接，结果要求对客户编号分组，对订单编号排序，对其它字段不作要求  
  
<table>  
<tr>  
<th>

客户编号

</th>  
<th>

订单编号

</th>  
<th>

订单金额

</th>  
<th>

姓名

</th>  
<th>

地址

</th>  
<th>

电话

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

1

</td>  
<td>

50

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

2

</td>  
<td>

200

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

6

</td>  
<td>

42

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

7

</td>  
<td>

352

</td>  
<td>

hanmeimei

</td>  
<td>

ShangHai

</td>  
<td>

110

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

8

</td>  
<td>

1135

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

9

</td>  
<td>

400

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

10

</td>  
<td>

2000

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

11

</td>  
<td>

300

</td>  
<td>

leilei

</td>  
<td>

BeiJing

</td>  
<td>

112

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

3

</td>  
<td>

15

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

4

</td>  
<td>

350

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

5

</td>  
<td>

58

</td>  
<td>

lucy

</td>  
<td>

GuangZhou

</td>  
<td>

119

</td> </tr> </table>

  1. 在提交job的时候，把小数据通过DistributedCache分发到各个节点。
  2. map端使用DistributedCache读到数据，在内存中构建映射关系--如果使用专门的内存服务器，就把数据加载到内存服务器，map()节点可以只保留一份小缓存；如果使用BloomFilter来加速，在这里就可以构建；
  3. map()函数中，对每一对<key,value style="margin: 0px; padding: 0px;">，根据key到第2)步构建的映射里面中找出数据，进行连接，输出。

