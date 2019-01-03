故障一：某个datanode节点无法启动

我是以用户名centos安装和搭建了一个测试用的hadoop集群环境，也配置好了有关的权限，所有者、所属组都配成centos:centos

【故障现象】

名称节点的3个进程都起来了，但是其中一个数据节点的DataNode进程没启动，就是说在该数据节点上通过jps没查到有关进程。

【排查过程】

登录此故障节点（主机名为s203）的日志存放目录$ cd $HADOOP_HOME/logs/

查看日志hadoop-centos-datanode-s203.log，发现有一行FATAL级别的错误：

FATAL org.apache.hadoop.hdfs.server.datanode.DataNode: Initialization failed
for Block pool <registering> (Datanode Uuid unassigned)

还有一行：

java.io.IOException: Incompatible clusterIDs in /tmp/hadoop-centos/dfs/data:
namenode clusterID = CID-8ba03cf7-a71d-4439-8818-c0a65f47e7aa; datanode
clusterID = CID-7d9b5e26-d96e-4596-b42e-5810aaacedf8

从字面上来看，报错信息大意是datanode所属的集群ID和namenodeID不一致,。这就导致了该data
node无法加入到同一个集群里面去(每个hadoop集群的ID不能有两个)，所以此数据节点启动失败。

【解决办法】

有两个，一个是删除集群所有主机信息后，格式化名称节点后再启动集群。这个办法会丢失我之前已有的数据，这不是我想要的。

所以我这里采用第二种办法：把无法启动的数据节点所属的clusterID和集群的cluesterID配成一样的。

那么先找到名称节点的集群ID，即clusterID，clusterID存在于VERSION文件中，而VERSION文件默认的话在HADOOP_FILE_SYSTEM/namenode/current/目录下

1，找到VERSION文件后找到clusterID的值，拷贝下来。

2，然后登入故障节点、找到主机里的VERSION文件，编辑该文件，用刚才的名称节点的clusterID值替换掉此data
node的clusterID值，保存退出。

3，在此数据节点执行命令 sh $HADOOP_HOME/sbin/hadoop-daemon.sh start datanode

4，在本机查看jps后就发现DataNode进程启动了。退出此节点后，打开浏览器输入 IP:50070
即可看到Datanodes页面出现了刚才启动的数据节点。

故障二：在集群上运行M-R作业后，没有输出想要的结果

[centos@s201 ~]$ hadoop jar TONY-1.0-SNAPSHOT.jar pckmar11.WCapp
/user/centos/input /user/centos/output

[centos@s201 ~]$ hadoop fs -ls -R / | grep -v tmp

drwxr-xr-x - centos supergroup 0 2017-02-28 21:40 /user

drwxr-xr-x - centos supergroup 0 2017-02-28 21:41 /user/centos

drwxr-xr-x - centos supergroup 0 2017-02-28 21:45 /user/centos/input

-rw-r--r-- 3 centos supergroup 112 2017-02-28 21:45 /user/centos/input/mar11.txt

在user/centos下没有生成out目录。于是通过浏览器检查作业日志。

浏览器输入[http://clusterIP:8088](http://clusterip:8088/)可以在页面看到All Applications

在Scheduler
Metrics的FinalStatus中，可以看到FAILED的作业ID，点进此ID后，查看到Diagnostics诊断信息，摘出来如下：

ERROR
org.apache.hadoop.yarn.server.nodemanager.containermanager.ContainerManagerImpl:
Unauthorized request to start container.

This token is expired. current time is 1489186612865 found 1488290898107

Note: System times on machines may be out of sync. Check system time and time
zones.

可以推断出，是因为节点的时间不一致导致的任务调度失败。所以解决办法是把各个计算节点(也就是datanode)和namenode节点的系统时间同步。

同步系统时间的方法有两种：第一种方式，同时批量修改各个节点的时间，可以尝试shell脚本自动运行命令：

date -s “yyyymmdd HH:SS”但是要有执行此命令的权限；

第二种方式，使用ntpdate指定提供时间同步的服务器，我这里使用的北京邮电大学的：

sudo ntpdate [s2c.time.edu.cn](http://s2c.time.edu.cn/)

执行完后，确认一下每个节点的时间是一致的。

重新执行M-R作业，成功：

[centos@s201 ~]$ hadoop fs -ls -R / | grep -v tmp

drwxr-xr-x - centos supergroup 0 2017-02-28 21:40 /user  
drwxr-xr-x - centos supergroup 0 2017-03-11 18:47 /user/centos  
drwxr-xr-x - centos supergroup 0 2017-02-28 21:45 /user/centos/input  
-rw-r--r-- 3 centos supergroup 112 2017-02-28 21:45 /user/centos/input/mar11.txt  
drwxr-xr-x - centos supergroup 0 2017-03-11 18:47 /user/centos/output  
-rw-r--r-- 3 centos supergroup 0 2017-03-11 18:47 /user/centos/output/_SUCCESS  
-rw-r--r-- 3 centos supergroup 64 2017-03-11 18:47 /user/centos/output/part-r-00000

故障三：配置YARN集群HA后，查看状态失败

故障现象：

在执行完start-
dfs.sh、在rm1主机上启动第一个ResourceManager进程，查看ResourceManager服务在rm1和rm2各自的状态，报错：

[centos@h201 hadoop]$ yarn-daemon.sh start resourcemanager  
starting resourcemanager, logging to /soft/hadoop-2.7.3/logs/yarn-centos-
resourcemanager-h201.out  
[centos@h201 hadoop]$ jps  
9057 NameNode  
9897 ResourceManager  
9932 Jps  
[centos@h201 hadoop]$ ssh h205 yarn-daemon.sh start resourcemanager  
bash: yarn-daemon.sh: command not found  
[centos@h201 hadoop]$ ssh h205 # ResourceManager不会自动启动，须登入第二台RM服务器启动该进程  
Last login: Thu Apr 6 23:06:28 2017 from h201  
[centos@h205 ~]$ yarn-daemon.sh start resourcemanager  
starting resourcemanager, logging to /soft/hadoop-2.7.3/logs/yarn-centos-
resourcemanager-h205.out  
[centos@h205 ~]$ jps  
4736 NameNode  
5095 ResourceManager  
5132 Jps  
[centos@h205 ~]$ yarn rmadmin -getServiceState rm2  
17/04/08 13:59:45 INFO ipc.Client: Retrying connect to server:
h205/172.16.112.205:8033. Already tried 0 time(s); retry policy is
RetryUpToMaximumCountWithFixedSleep(maxRetries=1, sleepTime=1000 MILLISECONDS)  
Operation failed: Call From h205/172.16.112.205 to h205:8033 failed on
connection exception: java.net.ConnectException: Connection refused; For more
details see: http://wiki.apache.org/hadoop/ConnectionRefused  
[centos@h205 ~]$ exit  
logout  
Connection to h205 closed.  
[centos@h201 hadoop]$ yarn rmadmin -getServiceState rm1 # 也是和上面同样的报错

排查过程：

1) RM节点的yarn-site.xml配置文件检查无误，各个节点的yarn-
stie.xml配置文件也是和RM节点同步的，网络通信也没问题。查看h205(RM节点rm2)的ResourceManager进程，没启动，于是启动它。

2) 再查看yarn rmadmin -getServiceState rm1仍然报同样的错误。

3) 检查zookeeper集群的3个zone服务器上各自的QuorumPeerMain进程未启动，分别使用zkServer.sh
start启动后，再查看RM的2个节点状态，修好了：

[centos@h201 hadoop]$ yarn rmadmin -getServiceState rm1  
active  
[centos@h201 hadoop]$ yarn rmadmin -getServiceState rm2  
standby

然后到yarn框架的web页面http://h205:8088/cluster/ 点击About栏目就能看到其中一个RM节点的状态

ResourceManager HA state: standby

在另一个RM节点http://h201:8088/cluster/ 点击About栏目就能看到ResourceManager HA state:
active

所以说有了zookeeper的自动容灾，大数据平台高可用配置就很方便！

故障四：hive2.1启动hive命令行报错

错误信息：java.net.URISyntaxException: Relative path in absolute URI

解决方法：

1\. 打开hive-site.xml配置文件，找到配置值含有 system:java.io.tmpdir 的<name>

2\. 把第一个system:java.io.tmpdir配置项改成

<property>

<name>hive.querylog.location</name>

<value>/home/centos/hivequerylog</value>

<description>Location of Hive run time structured log file</description>

</property>

第二个system:java.io.tmpdir配置项改成：

<property>

<name>hive.server2.logging.operation.log.location</name>

<value>/home/centos/hiveserver2log</value>

<description>Top level directory where operation logs are stored if logging
functionality is enabled</description>

对应的<value>改成指定的目录，可以不存在，他会自动建

3.改好后把这个配置文件同步到其他装有hive的主机

4\. 再启动hive，就成功了

