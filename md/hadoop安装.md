下载https://archive.cloudera.com/cdh5/cdh/5/hadoop-2.6.0-cdh5.9.3.tar.gz

1、配置环境变量 vim /etc/proflie

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64  
export JRE_HOME=${JAVA_HOME}/jre  
export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib  
export PATH=${JAVA_HOME}/bin:$PATH

export HADOOP_HOME=$HOME/Programs/Hadoop/hadoop-2.2.0  
export HADOOP_MAPRED_HOME=$HOME/Programs/Hadoop/hadoop-2.2.0  
export HADOOP_COMMON_HOME=$HOME/Programs/Hadoop/hadoop-2.2.0  
export HADOOP_HDFS_HOME=$HOME/Programs/Hadoop/hadoop-2.2.0  
export YARN_HOME=$HOME/Programs/Hadoop/hadoop-2.2.0  
export HADOOP_CONF_DIR=$HOME/Programs/Hadoop/hadoop-2.2.0/etc/hadoop  
export PATH=${HADOOP_HOME}/bin:$PATH

2、simon@simon-Lenovo-G400: source /etc/profile

3、hadoop-env.sh

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

4、core-site.xml

<configuration>  
<property>  
<name>fs.defaultFS</name>  
<value>hdfs://localhost:9000</value>  
</property>  
<property>  
<name>hadoop.tmp.dir</name>  
<value>file:/home/simon/hadWorkspace/tmp</value>  
<description>Abase for other temporary directories.</description>  
</property>  
</configuration>

5、hdfs-site.xml

<configuration>  
<property>  
<name>dfs.namenode.secondary.http-address</name>  
<value>localhost:50090</value>  
</property>  
<property>  
<name>dfs.replication</name>  
<value>1</value>  
</property>  
<property>  
<name>dfs.namenode.name.dir</name>  
<value>file:/home/simon/hadWorkspace/namenode</value>  
</property>  
<property>  
<name>dfs.datanode.data.dir</name>  
<value>file:/home/simon/hadWorkspace/datanode</value>  
</property>  
</configuration>

6、mapred-site.xml

<configuration>  
<property>  
<name>mapreduce.framework.name</name>  
<value>yarn</value>  
</property>  
<property>  
<name>mapreduce.jobhistory.address</name>  
<value>localhost:10020</value>  
</property>  
<property>  
<name>mapreduce.jobhistory.webapp.address</name>  
<value>localhost:19888</value>  
</property>  
</configuration>

7、yarn-site.xml

<configuration>  
<property>  
<name>yarn.resourcemanager.hostname</name>  
<value>localhost</value>  
</property>  
<property>  
<name>yarn.nodemanager.aux-services</name>  
<value>mapreduce_shuffle</value>  
</property>  
</configuration>

8、配置ssh

sudo apt-get install ssh  
sudo apt-get install rsync  
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa  
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys  
chmod 0600 ~/.ssh/authorized_keys  
ssh localhost

9、运行

simon@simon-Lenovo-G400:~$ cd /home/simon/software/hadoop/bin  
simon@simon-Lenovo-G400:~/software/hadoop/bin$ hadoop namenode -format  
simon@simon-Lenovo-G400:~$ cd /home/simon/software/hadoop/sbin  
simon@simon-Lenovo-G400:~/software/hadoop/sbin$ ./start-all.sh  
simon@simon-Lenovo-G400:~/software/hadoop/sbin$ jps  
10564 NodeManager  
10692 Jps  
10329 SecondaryNameNode  
10140 DataNode  
9996 NameNode  
9534 ResourceManager

