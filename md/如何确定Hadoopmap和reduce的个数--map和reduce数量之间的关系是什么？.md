1.map和reduce的数量过多会导致什么情况？  
2.Reduce可以通过什么设置来增加任务个数？  
3.一个task的map数量由谁来决定？  
4.一个task的reduce数量由谁来决定？  
  
  
一般情况下，在输入源是文件的时候，一个task的map数量由splitSize来决定的，那么splitSize是由以下几个来决定的  
goalSize = totalSize / mapred.map.tasks  
inSize = max {mapred.min.split.size, minSplitSize}  
splitSize = max (minSize, min(goalSize, dfs.block.size))  
一个task的reduce数量，由partition决定。  
在输入源是数据库的情况下，比如mysql，对于map的数量需要用户自己指定，比如  
jobconf.set(“mapred.map.tasks.nums”,20)；  
如果数据源是HBase的话，map的数量就是该表对应的region数量。  
map和reduce是hadoop的核心功能，hadoop正是通过多个map和reduce的并行运行来实现任务的分布式并行计算，从这个观点来看，如果将map和reduce的数量设置为1，那么用户的任务就没有并行执行，但是map和reduce的数量也不能过多，数量过多虽然可以提高任务并行度，但是太多的map和reduce也会导致整个hadoop框架因为过度的系统资源开销而使任务失败。所以用户在提交map/reduce作业时应该在一个合理的范围内，这样既可以增强系统负载匀衡，也可以降低任务失败的开销。  
  
  
1 map的数量  
map的数量通常是由hadoop集群的DFS块大小确定的，也就是输入文件的总块数，正常的map数量的并行规模大致是每一个Node是10~100个，对于CPU消耗较小的作业可以设置Map数量为300个左右，但是由于hadoop的每一个任务在初始化时需要一定的时间，因此比较合理的情况是每个map执行的时间至少超过1分钟。具体的数据分片是这样的，InputFormat在默认情况下会根据hadoop集群的DFS块大小进行分片，每一个分片会由一个map任务来进行处理，当然用户还是可以通过参数mapred.min.split.size参数在作业提交客户端进行自定义设置。还有一个重要参数就是mapred.map.tasks，这个参数设置的map数量仅仅是一个提示，只有当InputFormat
决定了map任务的个数比mapred.map.tasks值小时才起作用。同样，Map任务的个数也能通过使用JobConf
的conf.setNumMapTasks(int
num)方法来手动地设置。这个方法能够用来增加map任务的个数，但是不能设定任务的个数小于Hadoop系统通过分割输入数据得到的值。当然为了提高集群的并发效率，可以设置一个默认的map数量，当用户的map数量较小或者比本身自动分割的值还小时可以使用一个相对交大的默认值，从而提高整体hadoop集群的效率。  
  
  
2 reduece的数量  
reduce在运行时往往需要从相关map端复制数据到reduce节点来处理，因此相比于map任务。reduce节点资源是相对比较缺少的，同时相对运行较慢，正确的reduce任务的个数应该是0.95或者1.75
*（节点数 ×mapred.tasktracker.tasks.maximum参数值）。如果任务数是节点个数的0.95倍，那么所有的reduce任务能够在
map任务的输出传输结束后同时开始运行。如果任务数是节点个数的1.75倍，那么高速的节点会在完成他们第一批reduce任务计算之后开始计算第二批
reduce任务，这样的情况更有利于负载均衡。同时需要注意增加reduce的数量虽然会增加系统的资源开销，但是可以改善负载匀衡，降低任务失败带来的负面影响。同样，Reduce任务也能够与
map任务一样，通过设定JobConf 的conf.setNumReduceTasks(int num)方法来增加任务个数。  
  
  
3 reduce数量为0  
有些作业不需要进行归约进行处理，那么就可以设置reduce的数量为0来进行处理，这种情况下用户的作业运行速度相对较高，map的输出会直接写入到
SetOutputPath(path)设置的输出目录，而不是作为中间结果写到本地。同时Hadoop框架在写入文件系统前并不对之进行排序。

一 如何控制Map任务数量

既然要讨论如何控制map任务数量，那么我们就得知道有哪些因素会影响map任务的数量。

我们知道，map任务的数量是由在提交job的时候，进行文件切片的时候，文件的切片数决定的。

在这个时候，无论你是否在配置文件设置mapreduce.job.maps参数，都将会重新设置这个值为文件的切片数。

而这个文件切片数又是由splitSize决定的。如果一个splitSize=20M，那么100M的文件就会生成5个切片。

那么splitSize又是由什么决定的呢？

intsplitSize = computeSplitSize():

具体逻辑就是：

maxSize:mapreduce.input.fileinputformat.split.maxsize,默认值是Integer.MAX_VALUE

minSize:mapreduce.input.fileinputformat.split.minsize,默认值是1

如果min(maxSize,blockSize)取其中最小的，假设结果为result

然后在max(minSize,result)取中较大者。

所以默认情况下，splitSize就是blockSize=128M

策略如下：

#如果希望调小maptask, 那么你需要调大minSize,至少保证minSize> blockSize(128M)

#如果希望调大maptask，那么你需要调小maxSize，至少保证maxSize< blockSize(128M)

#如果有很多小文件，你又想减少map任务，这时候我觉得你可以使用CombineInputFormat将多个文件组装成一个CombineInputSplit。

二 调整reduce数量

Reduce的数量是由mapreduce.job.reduces这个参数决定的，你也可以在job. setNumReduceTasks

