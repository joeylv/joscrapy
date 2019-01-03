# hadoop 管理命令dfsadmin

dfsadmin 命令用于管理HDFS集群，这些命令常用于管理员。

  

1\. （Safemode）安全模式  
  
<table>  
<tr>  
<td>

动作

</td>  
<td>

命令

</td> </tr>  
<tr>  
<td>

把集群切换到安全模式

</td>  
<td>

bin/hdfs dfsadmin -safemode [enter/get/leave]

</td> </tr>  
<tr>  
<td>

数据节点状态列表

</td>  
<td>

bin/hadoop dfsadmin -report

</td> </tr>  
<tr>  
<td>

添加或删除数据节点

</td>  
<td>

bin/hadoop dfsadmin -refreshNodes

</td> </tr>  
<tr>  
<td>

打印网络拓扑

</td>  
<td>

bin/hadoop dfsadmin -printTopology

</td> </tr>  
<tr>  
<td>

官当网站

</td>  
<td>

<http://hadoop.apache.org/docs/r2.8.3/hadoop-project-dist/hadoop-
hdfs/HDFSCommands.html#dfsadmin>

</td> </tr> </table>

  1. [hadoop@master bin]$ ./hdfs dfsadmin -safemode enter #进入安全模式

  2. Safe mode is ON

  3.   4. [hadoop@master bin]$ ./hdfs dfsadmin -safemode get #获取当前状态

  5. Safe mode is ON

  6.   7. [hadoop@master bin]$ ./hdfs dfsadmin -safemode leave #离开safemode状态

  8. Safe mode is OFF

  9. [hadoop@master bin]$ 

  10.   11. 
安全模式：On startup, the NameNode enters a special state called Safemode.
Replication of data blocks does not occur when the NameNode is in the Safemode
state. The NameNode receives Heartbeat and Blockreport messages from the
DataNodes. A Blockreport contains the list of data blocks that a DataNode is
hosting. Each block has a specified minimum number of replicas. A block is
considered safely replicated when the minimum number of replicas of that data
block has checked in with the NameNode. After a configurable percentage of
safely replicated data blocks checks in with the NameNode (plus an additional
30 seconds), the NameNode exits the Safemode state. It then determines the
list of data blocks (if any) that still have fewer than the specified number
of replicas. The NameNode then replicates these blocks to other DataNodes.

hadoop启动时，会处于一种特殊的状态称做安全模式，这种模式下，数据块的复制是不能发生的，主节点会收到各数据节点的心跳(Heartbeat）和块报告（Blockreport）信息。块报告信息包含该数据节点包含的块信息，每一个数据块都有一个最小被副本数，当一个块最小副本数与NN记录的相符合时就被认为是安全的复制，在配置一个安全副本百分数与NN相符后（再加30s）（意思就是副本数*N%后与NN记录的相符就认为是安全，N可配置），NN就退出Safemode状态。之后（safemode
时是不能发生数据复制的）如果列表中仍然有少数的副本数比已备份少，NN将会把这些块复制到其他数据节点。

根据上面说明：

1.Safemode 主要是校验数据节点的块信息。

2.safemode 不能发生块复制（Replication ）。

3.hadoop 的维护工作是在模式下进行的。

Safemode状态时创建目录报错：

    
    
    Cannot create directory /hxw. Name node is in safe mode. It was turned on manually. Use "hdfs dfsadmin -safemode leave" to turn safe mode off.

  
  
2.集群信息状态报告

以及集群资源占用情况，以及各数据节点信息。

  1. [hadoop@master logs]$ hadoop dfsadmin -report

  2. DEPRECATED: Use of this script to execute hdfs command is deprecated.

  3. Instead use the hdfs command for it.

  4.   5.   6. Configured Capacity: 37492883456 (34.92 GB)

  7. Present Capacity: 22908968960 (21.34 GB)

  8. DFS Remaining: 21126250496 (19.68 GB)

  9. DFS Used: 1782718464 (1.66 GB)

  10. DFS Used%: 7.78%

  11. Under replicated blocks: 18

  12. Blocks with corrupt replicas: 0

  13. Missing blocks: 0

  14. Missing blocks (with replication factor 1): 0

  15. Pending deletion blocks: 0

  16.   17.   18. \-------------------------------------------------

  19. Live datanodes (2):

  20.   21.   22. Name: 10.0.1.226:50010 (slave-2)

  23. Hostname: slave-2

  24. Decommission Status : Normal

  25. Configured Capacity: 18746441728 (17.46 GB)

  26. DFS Used: 891359232 (850.07 MB)

  27. Non DFS Used: 7806763008 (7.27 GB)

  28. DFS Remaining: 10048319488 (9.36 GB)

  29. DFS Used%: 4.75%

  30. DFS Remaining%: 53.60%

  31. Configured Cache Capacity: 0 (0 B)

  32. Cache Used: 0 (0 B)

  33. Cache Remaining: 0 (0 B)

  34. Cache Used%: 100.00%

  35. Cache Remaining%: 0.00%

  36. Xceivers: 1

  37. Last contact: Wed Jan 17 17:09:23 CST 2018

  38.   39.   40.   41.   42. Name: 10.0.1.227:50010 (slave-1)

  43. Hostname: slave-1

  44. Decommission Status : Normal

  45. Configured Capacity: 18746441728 (17.46 GB)

  46. DFS Used: 891359232 (850.07 MB)

  47. Non DFS Used: 6777151488 (6.31 GB)

  48. DFS Remaining: 11077931008 (10.32 GB)

  49. DFS Used%: 4.75%

  50. DFS Remaining%: 59.09%

  51. Configured Cache Capacity: 0 (0 B)

  52. Cache Used: 0 (0 B)

  53. Cache Remaining: 0 (0 B)

  54. Cache Used%: 100.00%

  55. Cache Remaining%: 0.00%

  56. Xceivers: 1

  57. Last contact: Wed Jan 17 17:09:24 CST 2018

  
3.节点刷新

当集群有新增或删除节点时使用。

  1. [hadoop@master bin]$ ./hdfs dfsadmin -refreshNodes

  2. Refresh nodes successful

  3.   4. [hadoop@slave-1 sbin]$ ./hadoop-daemon.sh stop datanode

  5. stopping datanode

  6.   7. [hadoop@master bin]$ hadoop dfsadmin -report

  8. DEPRECATED: Use of this script to execute hdfs command is deprecated.

  9. Instead use the hdfs command for it.

  10.   11.   12. Configured Capacity: 37492883456 (34.92 GB)

  13. Present Capacity: 22914383872 (21.34 GB)

  14. DFS Remaining: 21131665408 (19.68 GB)

  15. DFS Used: 1782718464 (1.66 GB)

  16. DFS Used%: 7.78%

  17. Under replicated blocks: 18

  18. Blocks with corrupt replicas: 0

  19. Missing blocks: 0

  20. Missing blocks (with replication factor 1): 0

  21. Pending deletion blocks: 0

  22.   23.   24. \-------------------------------------------------

  25. Live datanodes (2):

  26.   27.   28. Name: 10.0.1.226:50010 (slave-2)

  29. Hostname: slave-2

  30. Decommission Status : Normal

  31. Configured Capacity: 18746441728 (17.46 GB)

  32. DFS Used: 891359232 (850.07 MB)

  33. Non DFS Used: 7801290752 (7.27 GB)

  34. DFS Remaining: 10053791744 (9.36 GB)

  35. DFS Used%: 4.75%

  36. DFS Remaining%: 53.63%

  37. Configured Cache Capacity: 0 (0 B)

  38. Cache Used: 0 (0 B)

  39. Cache Remaining: 0 (0 B)

  40. Cache Used%: 100.00%

  41. Cache Remaining%: 0.00%

  42. Xceivers: 1

  43. Last contact: Wed Jan 17 18:16:06 CST 2018

  44.   45.   46.   47.   48. Name: 10.0.1.227:50010 (slave-1)

  49. Hostname: slave-1

  50. Decommission Status : Normal

  51. Configured Capacity: 18746441728 (17.46 GB)

  52. DFS Used: 891359232 (850.07 MB)

  53. Non DFS Used: 6777208832 (6.31 GB)

  54. DFS Remaining: 11077873664 (10.32 GB)

  55. DFS Used%: 4.75%

  56. DFS Remaining%: 59.09%

  57. Configured Cache Capacity: 0 (0 B)

  58. Cache Used: 0 (0 B)

  59. Cache Remaining: 0 (0 B)

  60. Cache Used%: 100.00%

  61. Cache Remaining%: 0.00%

  62. Xceivers: 1

  63. Last contact: Wed Jan 17 18:13:43 CST 2018

  64.   65. [hadoop@master bin]$ ./hdfs dfsadmin -refreshNodes

  66. Refresh nodes successful

  67.   68.   69. [hadoop@master bin]$ ./hdfs dfsadmin -refreshNodes

  70. Refresh nodes successful

  71. [hadoop@master bin]$ hadoop dfsadmin -report 

  72. DEPRECATED: Use of this script to execute hdfs command is deprecated.

  73. Instead use the hdfs command for it.

  74.   75.   76. Configured Capacity: 37492883456 (34.92 GB)

  77. Present Capacity: 22914379776 (21.34 GB)

  78. DFS Remaining: 21131661312 (19.68 GB)

  79. DFS Used: 1782718464 (1.66 GB)

  80. DFS Used%: 7.78%

  81. Under replicated blocks: 18

  82. Blocks with corrupt replicas: 0

  83. Missing blocks: 0

  84. Missing blocks (with replication factor 1): 0

  85. Pending deletion blocks: 0

  86.   87.   88. \-------------------------------------------------

  89. Live datanodes (2):

  90.   91.   92. Name: 10.0.1.226:50010 (slave-2)

  93. Hostname: slave-2

  94. Decommission Status : Normal

  95. Configured Capacity: 18746441728 (17.46 GB)

  96. DFS Used: 891359232 (850.07 MB)

  97. Non DFS Used: 7801294848 (7.27 GB)

  98. DFS Remaining: 10053787648 (9.36 GB)

  99. DFS Used%: 4.75%

  100. DFS Remaining%: 53.63%

  101. Configured Cache Capacity: 0 (0 B)

  102. Cache Used: 0 (0 B)

  103. Cache Remaining: 0 (0 B)

  104. Cache Used%: 100.00%

  105. Cache Remaining%: 0.00%

  106. Xceivers: 1

  107. Last contact: Wed Jan 17 18:18:54 CST 2018

  108.   109.   110.   111.   112. Name: 10.0.1.227:50010 (slave-1)

  113. Hostname: slave-1

  114. Decommission Status : Normal

  115. Configured Capacity: 18746441728 (17.46 GB)

  116. DFS Used: 891359232 (850.07 MB)

  117. Non DFS Used: 6777208832 (6.31 GB)

  118. DFS Remaining: 11077873664 (10.32 GB)

  119. DFS Used%: 4.75%

  120. DFS Remaining%: 59.09%

  121. Configured Cache Capacity: 0 (0 B)

  122. Cache Used: 0 (0 B)

  123. Cache Remaining: 0 (0 B)

  124. Cache Used%: 100.00%

  125. Cache Remaining%: 0.00%

  126. Xceivers: 1

  127. Last contact: Wed Jan 17 18:13:43 CST 2018

说明：在停止某个数据节点后，刷新节点信息仍然能看到该节点信息，状态noraml 状态，界面上看到last contact 时间是560+s。

在Namenode 的配置文件slaves 中删除该节点，然后重新刷新节点信息，则后台显示：

  1. [hadoop@master bin]$ ./hdfs dfsadmin -refreshNodes

  2. Refresh nodes successful

  3. [hadoop@master bin]$ hadoop dfsadmin -report 

  4. DEPRECATED: Use of this script to execute hdfs command is deprecated.

  5. Instead use the hdfs command for it.

  6.   7. Configured Capacity: 18746441728 (17.46 GB)

  8. Present Capacity: 10945093632 (10.19 GB)

  9. DFS Remaining: 10053734400 (9.36 GB)

  10. DFS Used: 891359232 (850.07 MB)

  11. DFS Used%: 8.14%

  12. Under replicated blocks: 161

  13. Blocks with corrupt replicas: 0

  14. Missing blocks: 0

  15. Missing blocks (with replication factor 1): 0

  16. Pending deletion blocks: 0

  17.   18. \-------------------------------------------------

  19. Live datanodes (1):

  20.   21. Name: 10.0.1.226:50010 (slave-2)

  22. Hostname: slave-2

  23. Decommission Status : Normal

  24. Configured Capacity: 18746441728 (17.46 GB)

  25. DFS Used: 891359232 (850.07 MB)

  26. Non DFS Used: 7801348096 (7.27 GB)

  27. DFS Remaining: 10053734400 (9.36 GB)

  28. DFS Used%: 4.75%

  29. DFS Remaining%: 53.63%

  30. Configured Cache Capacity: 0 (0 B)

  31. Cache Used: 0 (0 B)

  32. Cache Remaining: 0 (0 B)

  33. Cache Used%: 100.00%

  34. Cache Remaining%: 0.00%

  35. Xceivers: 1

  36. Last contact: Wed Jan 17 18:26:36 CST 2018

  37.   38.   39. Dead datanodes (1):

  40.   41. Name: 10.0.1.227:50010 (slave-1)

  42. Hostname: slave-1

  43. Decommission Status : Normal

  44. Configured Capacity: 0 (0 B)

  45. DFS Used: 0 (0 B)

  46. Non DFS Used: 6777208832 (6.31 GB)

  47. DFS Remaining: 0 (0 B)

  48. DFS Used%: 100.00%

  49. DFS Remaining%: 0.00%

  50. Configured Cache Capacity: 0 (0 B)

  51. Cache Used: 0 (0 B)

  52. Cache Remaining: 0 (0 B)

  53. Cache Used%: 100.00%

  54. Cache Remaining%: 0.00%

  55. Xceivers: 0

  56. Last contact: Wed Jan 17 18:13:43 CST 2018

  57. 
  
![](https://img-
blog.csdn.net/20180117182809374?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvampzaG91amk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)  

4.网络拓扑

  1. [hadoop@master ~]$ hadoop dfsadmin -printTopology 

  2. DEPRECATED: Use of this script to execute hdfs command is deprecated.

  3. Instead use the hdfs command for it.

  4.   5. Rack: /default-rack

  6. 10.0.1.226:50010 (slave-2)

  7. 10.0.1.227:50010 (slave-1)

  

总结：

  1. [hadoop@master bin]$ ./hdfs dfsadmin -safemode enter #进入Safemode模式

  2. [hadoop@master bin]$ ./hdfs dfsadmin -safemode get #获取当前运行模式

  3. [hadoop@master bin]$ ./hdfs dfsadmin -safemode leave #退出Safemode模式

  4. [hadoop@master bin]$ hadoop dfsadmin -report #当前hadoop集群状态信息

  5. [hadoop@master bin]$ ./hdfs dfsadmin -refreshNodes #新增删除节点更新集群信息

  6. [hadoop@master sbin]$ ./hadoop-daemon.sh stop datanode #停止单个数据节点

  7. [hadoop@master ~]$ hadoop dfsadmin -printTopology #打印集群网络拓扑

  8. 

