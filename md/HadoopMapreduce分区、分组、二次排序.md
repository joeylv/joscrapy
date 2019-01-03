1、MapReduce中数据流动  
（1）最简单的过程： map - reduce  
（2）定制了partitioner以将map的结果送往指定reducer的过程： map - partition - reduce  
（3）增加了在本地先进性一次reduce（优化）过程： map - combin(本地reduce) - partition -reduce  
2、Mapreduce中Partition的概念以及使用。  
（1）Partition的原理和作用  
得到map给的记录后，他们该分配给哪些reducer来处理呢？hadoop采用的默认的派发方式是根据散列值来派发的，但是实际中，这并不能很高效或者按照我们要求的去执行任务。例如，经过partition处理后，一个节点的reducer分配到了20条记录，另一个却分配道了10W万条，试想，这种情况效率如何。又或者，我们想要处理后得到的文件按照一定的规律进行输出，假设有两个reducer，我们想要最终结果中part-00000中存储的是"h"开头的记录的结果,part-00001中存储其他开头的结果，这些默认的partitioner是做不到的。所以需要我们自己定制partition来根据自己的要求，选择记录的reducer。自定义partitioner很简单，只要自定义一个类，并且继承Partitioner类，重写其getPartition方法就好了，在使用的时候通过调用Job的setPartitionerClass指定一下即可  
  
Map的结果，会通过partition分发到Reducer上。Mapper的结果，可能送到Combiner做合并，Combiner在系统中并没有自己的基类，而是用Reducer作为Combiner的基类，他们对外的功能是一样的，只是使用的位置和使用时的上下文不太一样而已。Mapper最终处理的键值对<key,
value>，是需要送到Reducer去合并的，合并的时候，有相同key的键/值对会送到同一个Reducer那。哪个key到哪个Reducer的分配过程，是由Partitioner规定的。它只有一个方法，  
  
getPartition(Text key, Text value, int numPartitions)  
  
输入是Map的结果对<key,
value>和Reducer的数目，输出则是分配的Reducer（整数编号）。就是指定Mappr输出的键值对到哪一个reducer上去。系统缺省的Partitioner是HashPartitioner，它以key的Hash值对Reducer的数目取模，得到对应的Reducer。这样保证如果有相同的key值，肯定被分配到同一个reducre上。如果有N个reducer，编号就为0,1,2,3……(N-1)。  
  
（2）Partition的使用  
分区出现的必要性，如何使用Hadoop产生一个全局排序的文件？最简单的方法就是使用一个分区，但是该方法在处理大型文件时效率极低，因为一台机器必须处理所有输出文件，从而完全丧失了MapReduce所提供的并行架构的优势。事实上我们可以这样做，首先创建一系列排好序的文件；其次，串联这些文件（类似于归并排序）；最后得到一个全局有序的文件。主要的思路是使用一个partitioner来描述全局排序的输出。比方说我们有1000个1-10000的数据，跑10个ruduce任务，
如果我们运行进行partition的时候，能够将在1-1000中数据的分配到第一个reduce中，1001-2000的数据分配到第二个reduce中，以此类推。即第n个reduce所分配到的数据全部大于第n-1个reduce中的数据。这样，每个reduce出来之后都是有序的了，我们只要cat所有的输出文件，变成一个大的文件，就都是有序的了  
  
基本思路就是这样，但是现在有一个问题，就是数据的区间如何划分，在数据量大，还有我们并不清楚数据分布的情况下。一个比较简单的方法就是采样，假如有一亿的数据，我们可以对数据进行采样，如取10000个数据采样，然后对采样数据分区间。在Hadoop中，patition我们可以用TotalOrderPartitioner替换默认的分区。然后将采样的结果传给他，就可以实现我们想要的分区。在采样时，我们可以使用hadoop的几种采样工具，RandomSampler,InputSampler,IntervalSampler。  
  
这样，我们就可以对利用分布式文件系统进行大数据量的排序了，我们也可以重写Partitioner类中的compare函数，来定义比较的规则，从而可以实现字符串或其他非数字类型的排序，也可以实现二次排序乃至多次排序。  
  
2、MapReduce中分组的概念和使用  
分区的目的是根据Key值决定Mapper的输出记录被送到哪一个Reducer上去处理。而分组的就比较好理解了。笔者认为，分组就是与记录的Key相关。在同一个分区里面，具有相同Key值的记录是属于同一个分组的。  
  
3、MapReduce中Combiner的使用  
很多MapReduce程序受限于集群上可用的带宽，所以它会尽力最小化需要在map和reduce任务之间传输的中间数据。Hadoop允许用户声明一个combiner
function来处理map的输出，同时把自己对map的处理结果作为reduce的输入。因为combiner
function本身只是一种优化，hadoop并不保证对于某个map输出，这个方法会被调用多少次。换句话说，不管combiner
function被调用多少次，对应的reduce输出结果都应该是一样的。  
  
下面我们以《权威指南》的例子来加以说明，假设1950年的天气数据读取是由两个map完成的，其中第一个map的输出如下：  
(1950, 0)  
(1950, 20)  
(1950, 10)  
  
第二个map的输出为：  
(1950, 25)  
(1950, 15)  
  
而reduce得到的输入为：(1950, [0, 20, 10, 25, 15])， 输出为：(1950, 25)  
  
由于25是集合中的最大值，我们可以使用一个类似于reduce function的combiner
function来找出每个map输出中的最大值，这样的话，reduce的输入就变成了：  
(1950, [20, 25])  
  
各个funciton 对温度值的处理过程可以表示如下：max(0, 20, 10, 25, 15) =max(max(0, 20, 10), max(25,
15)) = max(20, 25) = 25  
  
注意：并不是所有的函数都拥有这个属性的（有这个属性的函数我们称之为commutative和associative），例如，如果我们要计算平均温度，就不能这样使用combiner
function，因为mean(0, 20, 10, 25, 15) =14，而mean(mean(0, 20, 10),mean(25, 15)) =
mean(10, 20) = 15  
  
combiner function并不能取代reduce function（因为仍然需要reduce
function处理来自不同map的带有相同key的记录）。但是他可以帮助减少需要在map和reduce之间传输的数据，就为这一点combiner
function就值得考虑使用。  
  
4、Shuffle阶段排序流程详解  
我们首先看一下MapReduce中的排序的总体流程。  
  
MapReduce框架会确保每一个Reducer的输入都是按Key进行排序的。一般，将排序以及Map的输出传输到Reduce的过程称为混洗（shuffle)。每一个Map都包含一个环形的缓存，默认100M，Map首先将输出写到缓存当中。当缓存的内容达到“阈值”时（阈值默认的大小是缓存的80%），一个后台线程负责将结果写到硬盘，这个过程称为“spill”。Spill过程中，Map仍可以向缓存写入结果，如果缓存已经写满，那么Map进行等待。  
  
Spill的具体过程如下：首先，后台线程根据Reducer的个数将输出结果进行分组，每一个分组对应一个Reducer。其次，对于每一个分组后台线程对输出结果的Key进行排序。在排序过程中，如果有Combiner函数，则对排序结果进行Combiner函数进行调用。每一次spill都会在硬盘产生一个spill文件。因此，一个Map
task有可能会产生多个spill文件，当Map写出最后一个输出时，会将所有的spill文件进行合并与排序，输出最终的结果文件。在这个过程中Combiner函数仍然会被调用。从整个过程来看，Combiner函数的调用次数是不确定的。下面我们重点分析下Shuffle阶段的排序过程：  
  
Shuffle阶段的排序可以理解成两部分，一个是对spill进行分区时，由于一个分区包含多个key值，所以要对分区内的<key,value>按照key进行排序，即key值相同的一串<key,value>存放在一起，这样一个partition内按照key值整体有序了。  
  
第二部分并不是排序，而是进行merge，merge有两次，一次是map端将多个spill
按照分区和分区内的key进行merge，形成一个大的文件。第二次merge是在reduce端，进入同一个reduce的多个map的输出
merge在一起，该merge理解起来有点复杂，最终不是形成一个大文件，而且期间数据在内存和磁盘上都有。所以shuffle阶段的merge并不是严格的排序意义，只是将多个整体有序的文件merge成一个大的文件，由于不同的task执行map的输出会有所不同，所以merge后的结果不是每次都相同，不过还是严格要求按照分区划分，同时每个分区内的具有相同key的<key,value>对挨在一起。  
  
Shuffle排序综述：如果只定义了map函数，没有定义reduce函数，那么输入数据经过shuffle的排序后，结果为key值相同的输出挨在一起，且key值小的一定在前面，这样整体来看key值有序（宏观意义的，不一定是按从大到小，因为如果采用默认的HashPartitioner，则key
的hash值相等的在一个分区，如果key为IntWritable的话，每个分区内的key会排序好的），而每个key对应的value不是有序的。  
  
5、MapReduce中辅助排序的原理与实现  
（1）任务  
我们需要把内容如下的sample.txt文件处理为下面文件：  
  
源文件：Sample.txt  
  
bbb 654  
  
ccc 534  
  
ddd 423  
  
aaa 754  
  
bbb 842  
  
ccc 120  
  
ddd 219  
  
aaa 344  
  
bbb 214  
  
ccc 547  
  
ddd 654  
  
aaa 122  
  
bbb 102  
  
ccc 479  
  
ddd 742  
  
aaa 146  
  
目标：part-r-00000  
  
aaa 122  
  
bbb 102  
  
ccc 120  
  
ddd 219  
  
（2）工作原理  
过程导引：  
1、定义包含记录值和自然值的组合键，本例中为MyPariWritable.  
  
2、自定义键的比较器（comparator）来根据组合键对记录进行排序，即同时利用自然键和自然值进行排序。（aaa 122组合为一个键）。  
  
3、针对组合键的Partitioner（本示例使用默认的hashPartitioner）和分组comparator在进行分区和分组时均只考虑自然键。  
  
详细过程：  
首先在map阶段，使用job.setInputFormatClass定义的InputFormat将输入的数据集分割成小数据块splites，同时InputFormat提供一个RecordReder的实现。本例子中使用的是TextInputFormat，他提供的RecordReder会将文本的一行的行号作为key，这一行的文本作为value。这就是自定义Map的输入是<LongWritable,
Text>的原因。然后调用自定义Map的map方法，将一个个<LongWritable,
Text>对输入给Map的map方法。注意输出应该符合自定义Map中定义的输出< MyPariWritable,
NullWritable>。最终是生成一个List< MyPariWritable,
NullWritable>。在map阶段的最后，会先调用job.setPartitionerClass对这个List进行分区，每个分区映射到一个reducer。每个分区内又调用job.setSortComparatorClass设置的key比较函数类排序。可以看到，这本身就是一个二次排序。在reduce阶段，reducer接收到所有映射到这个reducer的map输出后，也是会调用job.setSortComparatorClass设置的key比较函数类对所有数据对排序。然后开始构造一个key对应的value迭代器。这时就要用到分组，使用jobjob.setGroupingComparatorClass设置的分组函数类。只要这个比较器比较的两个key相同，他们就属于同一个组（本例中由于要求得每一个分区内的最小值，因此比较MyPariWritable类型的Key时，只需要比较自然键，这样就能保证只要两个MyPariWritable的自然键相同，则它们被送到Reduce端时候的Key就认为在相同的分组，由于该分组的Key只取分组中的第一个，而这些数据已经按照自定义MyPariWritable比较器排好序，则第一个Key正好包含了每一个自然键对应的最小值），它们的value放在一个value迭代器，而这个迭代器的key使用属于同一个组的所有key的第一个key。最后就是进入Reducer的reduce方法，reduce方法的输入是所有的key和它的value迭代器。同样注意输入与输出的类型必须与自定义的Reducer中声明的一致。

