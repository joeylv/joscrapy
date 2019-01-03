# Hadoop2.0 Namenode HA实现方案介绍及汇总

基于社区最新release的Hadoop2.2.0版本，调研了hadoop
HA方面的内容。hadoop2.0主要的新特性([Hadoop2.0稳定版2.2.0新特性剖析](http://dongxicheng.org/mapreduce-
nextgen/hadoop-2-2-0/))：

  1. hdfs snapshots: [apache官方对hdfs snapshots说明](http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsSnapshots.html)
  2. namenode federation: namenode在集群规模大了之后会成为性能瓶颈，尤其是内存使用量急剧增大，同时hdfs所有元数据信息的读取和操作都要与namenode通信。而联邦模式解决的就是namenode的可扩展性问题。更多内容可以参看[hadoop 2.0 namenode HA实战和federation实践](http://www.sizeofvoid.net/hadoop-2-0-namenode-ha-federation-practice-zh/) 下图是我画的HA和Federation部署图。每个namesevice映射了HDFS中部分实际路径，可以单独给Client提供服务，也可以由Client通过Client Mount Table来访问若干NS。图中每个NS里有一个active NN和一个standby NN，这部分HA会在下面介绍。每个NS对应了一个Pool，Pool对应的DN是该NS可以访问的DN id的集合。这样做到可扩展，带来的好处有很多，比如后续添加的NS不会影响之前的NS等。联邦部署适合大规模集群，一般规模不大的情况下不需要使用。下面主要介绍HA的内容。![](https://img-blog.csdn.net/20131105142938000?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvcGVsaWNr/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)
  3. namenode单点故障解决方案。NN现在的HA解决方案主要思路是提供一个保存元数据信息的地方，保证editlog不会丢失。董的这篇[HA单点故障解决方案总结](http://dongxicheng.org/mapreduce-nextgen/hadoop-2-0-ha/)中介绍了从解决MRv1的Jobtracker HA，到HDFS HA，再到还未正式发布的YARN RM HA解决方案的异同，各自采用的共享存储系统有所不同，主要原因是HA的解决方案难度取决于Master自身记录信息的多少和信息可重构性。共享存储系统主要有NFS，ZK，BookKeeper，QJM。其中已经发行版本里默认使用的QJM(Quaro Journal Manager)。QJM是Cloudera公司提出的，在QJM出现前，如果在主从切换的这段时间内出现脑裂，破坏HDFS元数据的时候，常见方式是去掉activeNN的写权限来保证最多只有一个active NN。QJM本质上是Paxos算法的实现，通过启动2N+1个JournalNode来写editlog，当其中大于N个Node写成功时候认为本次写成功，且允许容忍N以下个Node挂掉。QJM实现及源码分析可以参考[基于QJM的HDFS HA原理及代码分析](http://yanbohappy.sinaapp.com/?p=205)。QJM和BKJM(借助BookKeeper实现的JM)都是将editlog信息写在磁盘上，这点也是与NFS方案的区别，且NFS相对而言其实更重量级，本身是一个需要独立维护的东西，而QJM是已经实现的默认方案，配置方法在官方里也可以找到，很详细。BKJM正在实现中且长期看好。关于BookKeeper相关的JIRA进展可以参考[ BookKeeper Option For NN HA](https://issues.apache.org/jira/browse/HDFS-3399)。所以总结来说推荐使用QJM和BKJM，且他们的原理比较相似。再给出HDFS JIRA上一份cloudera员工给的Quorum-Journal Design设计文档，地址为<https://issues.apache.org/jira/secure/attachment/12547598/qjournal-design.pdf>
  4. hdfs symbo links将在2.3.0里发布。类似linux文件系统的软链接。相关资料可以参考[理解 Linux 的硬链接与软链接](http://www.ibm.com/developerworks/cn/linux/l-cn-hardandsymb-links/) [硬连接和软连接的原理](http://roclinux.cn/?p=754)

其实现在的HA方案，很大程度上参考的是Facebook的AvatarNode的NN
HA方案，只是他是手动的。Facebook的AvatarNode是业界较早的Namenode HA方案，它是基于HDFS 0.20实现的，如下图所示。

![](https://img-
blog.csdn.net/20131105155541375?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvcGVsaWNr/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

由于采用的是人工切换，所以实现相对简单。AvatarNode对Namenode进行了封装，处于工作状态的叫Primary
Avatar，处于热备状态的叫Standby
Avatar(封装了Namenode和SecondaryNameNode)，两者通过NFS共享EditLog所在目录。在工作状态下，Primary
Avatar中的Namenode实例接收Client的请求并进行处理，Datanode会向Primary和Standby两个同时发送blockReport和心跳，Standby
Avatar不断地从共享的EditLog中持续写入的新事务，并推送给它的Namenode实例，此时Standby
Avatar内部的Namenode处于安全模式状态，不对外提供服务，但是状态与Primary
Avatar中的保持一致。一旦Primary发生故障，管理员进行Failover切换：首先将原来的Primary进程杀死(避免了“Split
Brain”和“IO
Fencing”问题)，然后将原来的Standby设置为Primary，新的Primary会保证回放完成所有的EditLog事务，然后退出安全模式，对外接收服务请求。为了实现对客户端透明，AvatarNode主从采用相同的虚拟IP，切换时将新的Primary设置为该虚拟IP即可。整个流程可在秒~分钟级别完成。可以参考FaceBook
2011年的论文[ Apache Hadoop Goes Realtime at
Facebook](http://borthakur.com/ftp/RealtimeHadoopSigmod2011.pdf) 里面专门有一节讲到HA
AvatarNode的设计。

