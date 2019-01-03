为更好了解各种故障，可以修改数据块的大小和提升NameNode的日志级别

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>dfs.block.size</name>
  3. <value>4194304</value>
  4. </property>
  5. <property>
  6. <name>dfs.namenode.logging.level</name>
  7. <value>all</value>
  8. </property>

dfsadmin命令可查看集群的整体状态，包括容量、每个节点的数据块数量、活跃节点数及最后通信时间等

under replicated blocks：表示副本数量小于复制因子的数据块个数。

### DataNode故障

当NameNode进程明确了副本数过低的数据块后，会让其他DataNode从现有副本驻留主机复制这些数据块。需要注意的是，如果出现故障的节点重新恢复正常运行，该节点存储的数据块在集群中的副本数可能超过所需数量，这时候，NameNode随机选择要删除的副本并发出指令让相应主机删除。

DataNode被认定为dead的准确时间间隔并不是HDFS的一个可配置属性，它是由其他几个属性计算得出的，起关键作用的是心跳间隔时间。要重启所有主机中的死亡节点，使用start-
all.sh，它并不会影响活跃节点。

### TaskTracker故障

TaskTracker进程频繁向JobTracker发送心跳信息，心跳信息包含任务进度及可用空间。每个节点都有一个配置的map和reduce
slot（默认值是2）。用户可通过修改mapred-
site.xml的mapred.tasktracker.expiry.interval属性配置TaskTracker进程的超时时间。个别TaskTracker发生故障只会减少集群可并发运行的任务数，除此之外不会产生其他直接影响。即使所有TaskTracker都发生故障，也不会影响到HDFS的功能。

若物理主机发生了致命故障导致死亡节点无法重启，这时应该把该主机从slaves文件删掉，Hadoop就不再启动那台主机上的DataNode或TaskTracker。用户只需在运行这些命令（start/stop和slaves.sh）的主机上更新slaves文件，而无需在每个节点都进行同样操作。

### JobTracker故障

因为运行作业的主机上的客户端要通过与JobTracker的通信完成作业调度的初始化工作。若JobTracker已经停止运行，通信过程无法完成，作业以失败告终。但是运行异常的MapReduce集群不会对HDFS造成直接影响。JobTracker挂掉时，MapReduce框架没有保存任何正在执行的作业的状态信息，所有未完成作业都需重启。而许多作业会往HDFS写入一些临时数据，并会在作业运行结束时删掉这些数据。所以失败的作业可能会留下一些这种文件，用户需要手动清理这些数据。

在新主机上运行JobTracker，需要对所有节点上的mapred-site.xml文件进行修改，更新该文件中的主节点地址，并重启集群。

### NameNode维护的信息

用户要访问的是文件系统中某个位置的特定文件，不会关注数据块。NameNode要维护的信息如下：

  * 所有文件的实际内容、文件名及它们所在目录
  * 文件的元数据（文件大小，所有者，复制因子）
  * 文件与数据块的映射关系
  * 节点与数据块的映射关系

前三项信息是永久数据，保存在fsimage中，必须在NameNode启动过程中拿到这些数据，并维持在内存中。NameNode进程在硬盘上保存有两个文件，一个是fsimage，另一个为edit
log（记录了对fsimage文件的所有改动）。启动之时会搜寻edit
log文件，并所它的内容更新到fsimage文件中，再把fsimage读入内存。SecondaryNameNode并不是运行在另一台主机上的NameNode副本，它的作用在于周期性地读取
fsimage和edit log，并把edit
log中记录的改动应用到fsimage文件中，输出一个经过更新的fsimage文件。因此，它可以帮助NameNode快速启动。

NameNode发生致命故障时的主要防范措施就是配置NameNode，让它把fsimage和edit
log输出到多个不同位置。通常，我们可以添加一个NFS作为fsimage的输出位置。Hadoop
2.0最终目标是实现一种全自动的NameNode故障恢复机制。

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>dfs.namenode.name.dir</name>
  3. <value>${hadoop.tmp.dir}/dfs/name,/share/backup/namenode</value>
  4. </property>

如上配置，NameNode同时输出fsimage文件到两个位置，后面那个位置应当是远程文件系统（如NFS），启动集群之前，要确保存在新路径且该路径下没有数据。迁移到新的NameNode主机时，先登录到承载新NameNode进程的主机，修改/share/backup里面的相关配置文件，使其指向新NameNode主机。而后拷贝*site.xml和slaves文件到hadoop/conf。接着把更新过的配置文件拷贝到DataNode节点。

如果用户拥有多个指向文件系统不同位置的物理硬盘或其他存储设备时，dfs.data.dir属性非常有用，它允许使用多个数据存储位置，将这引动路径当做可并行使用的独立位置。Hadoop会智能调度这些设备，读写操作均匀分配到这些设备上，使存储量和吞吐量最大化，但却以健壮性为代价。

### 任务引发的故障

可设置任务的超时阈值，如果任务在这段时间里处于静默休眠状态，那Hadoop会强制结束该任务。

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>mapred.task.timeout</name>
  3. <value>30000</value>
  4. </property>

默认情况下，Hadoop将提交的后续作业放入一个FIFO，任何时候集群资源专用于处理正在运行的单个作业，因此还需要另外的作业调度器：计算能力调度器（capacityScheduler）和公平调度器（fairScheduler）。为了启用这些调度器，在yarn-
site.xml设置属性

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>yarn.resourcemanager.scheduler.class</name>
  3. <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler</value>
  4. </property>

CapacityScheduler采用多个作业队列，每个队列都会获得一部分集群资源（可不均等）。FairScheduler把整个集群分割成若干个资源池（默认情况下，份额相等，也可修改资源分配比例），在各资源池中，默认是所有提交到池中的作业都共享其资源，用户可限制资源池中并行作业的总数。两种调度器都会在某个队列（资源池）无作业时，将该队列（资源池）的资源分配给忙队列，又有作业被提交至空队列时，会再次获得其原有容量。两者的容器都支持作业优先级。

实现作业管理的主要工具是mapred job。提交作业：

$ mapred job -submit <job-file>

列出正在运行的作业：

$ mapred job -list

检查某个作业的状态

$ mapred job -status <job-id>

修改作业优先级

$ mapred job -set-priority <job-id> VERY_HIGH | HIGH | NORMAL | LOW | VERY_LOW

强制结束作业

$ mapred job -kill <job-id>

对运行缓慢的任务，会根据输出结果、向计数器写数值和明确地报告进度（Context类已实现Progressable接口，所以任意mapper/reducer都可以调用context.progress()报告作业执行的进度）这些线索来源确定任务处于空闲状态、静默状态或卡住状态的时间。

运行失败的任务可能以暂停运行、明确地抛出异常、中止运行或其他有声方式停止运行的形式存在。失败应对措施的设置如下：

mapreduce.map.maxattempts：任务最大重试次数

mapreduce.reduce.maxattempts

mapreduce.map.failures.maxpercent：更灵活的单个Job最多允许x%个map task失败

mapreduce.reduce.failures.maxpercent

mapreduce.job.maxtaskfailures.per.tracker：如果失败的任务数超过该值，整个作业失败

另外，可以使用skip模式处理异常数据。任务失败时，会在相同数据块上重试，直到跳过的记录数小于设置的最大值。具体是通过二分查找方法确定要跳过哪些范围内的数据。在mapred-
site.xml文件添加下列属性

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>mapreduce.map.skip.maxrecords</name>
  3. <value>5</value>
  4. </property>

### 主节点的扩容方案

可逐步提升主节点的性能，首先在一台专用主机上运行NameNode、JobTracker和SecondaryNameNode（hadoop2.0把secondaryNameNode分为Backup
NameNode和Checkpoint
NameNode）。随着集群规模增长，把NameNode迁移到新增的一台主机，让JobTracker和SecondaryNameNode运行在同一台主机上。集群规模进一步增长，有必要再把JobTracker和SecondaryNameNode分开，分别在单独的主机上运行。

### 网络配置与数据块的放置

在大多数集群中，各种主机（包括网络设备）都被放置在标准标准尺寸的机柜上，垂直地一层一层地堆叠起来。每个机柜通常都有一个供电装置，还有一个网络交换器用于将机柜上的主机接入到更广泛的网络。默认情况下，Hadoop认为每个节点都在同一个物理机柜上。若采用多个机柜放置主机，需要用到脚本让NameNode知道每台主机所在的机柜ID。此脚本只能位于NameNode主机，由用户设置core-
site.xml，如果没有指定执行脚本的位置，所有节点都报告它们位于同一个默认机柜。

**[html]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. <property>
  2. <name>net.topology.script.file.name</name>
  3. <value>/home/hadoop/rack-script.sh</value>
  4. </property 

脚本实现节点IP地址到所在机柜名的映射，由NameNode向该脚本传入要调查节点的IP地址。示例rack-script.sh为

**[plain]** [view
plain](https://blog.csdn.net/u012135300/article/details/51198732# "view
plain") [copy](https://blog.csdn.net/u012135300/article/details/51198732#
"copy")

  1. if [ $1 = "10.0.0.101" ]; then 
  2. echo -n "/rack1 " 
  3. else 
  4. echo -n "/default-rack " 
  5. fi 

$ chmod +x rack-script.sh

$ hdfs fsck -rack

hdfs fsck工具用于检测并修复文件系统问题，报告内部构件信息。hdfs fsck -rack可查看到机柜配置结果  
  

### 集群访问控制

hadoop使用执行HDFS命令的用户的Unix
ID作为HDFS上的用户身份。任何人只要在可以连接到集群的任意一台主机上创建一个与现有hadoop用户同名的用户，即可访问集群。并且Hadoop把启动集群的用户ID视为超级用户，可以拥有读写HDFS上作何用户的任意文件的权限。为支持更细粒度、更强的安全模型，需要从其他地方获悉用户身份信息，Kerberos就被采用了。

若安全性是一个最好具备而非具备的功能，可将整个集群部署在有着严格访问控制策略的防火墙之后，且只允许集群中的一台主机访问NameNode和JobTracker服务，所有用户都要连到该主机。

