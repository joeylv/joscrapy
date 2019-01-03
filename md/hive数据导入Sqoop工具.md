下载Sqoop ，直接解压缩;然后导入2个环境变量

![](../md/img/ggzhangxiaochao/1298744-20180624165425810-1508448804.png)

1、导入oracle数据库中表emp的数据到hive表中

![](../md/img/ggzhangxiaochao/1298744-20180624165635983-1668932031.png)

![](../md/img/ggzhangxiaochao/1298744-20180624165819562-252082003.png)

1、导入到HDFS中

![](../md/img/ggzhangxiaochao/1298744-20180624165942599-437932563.png)

    
    
    $ sqoop import --connect jdbc:mysql://database.example.com/employees \
        --username aaron --password 12345  
    --connect用来链接数据库，--table选择一个表，--colums选择列，-m选择mapreduce任务数量，--target-dir选择导入到HDFS的路径  
    2、导入Hive数据仓库中

![](../md/img/ggzhangxiaochao/1298744-20180624170710164-2085797477.png)

3、制定表的名字，导入到hive中指定的表中

![](../md/img/ggzhangxiaochao/1298744-20180624170844888-948362812.png)

4、制定条件

![](../md/img/ggzhangxiaochao/1298744-20180624170946688-193700598.png)

\--hive-table导入到hive"中制定的emp2表中，若不存在，则创建，--where指明条件

5、查询语句 query

![](../md/img/ggzhangxiaochao/1298744-20180624171309838-1503914718.png)

6、导出数据

![](../md/img/ggzhangxiaochao/1298744-20180624171521440-491622420.png)

![](../md/img/ggzhangxiaochao/1298744-20180624171632153-334895815.png)

