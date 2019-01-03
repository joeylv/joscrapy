![](../md/img/ggzhangxiaochao/1298744-20180624163918789-654935520.png)

![](../md/img/ggzhangxiaochao/1298744-20180624164044730-1596187258.png)

LOCAL 指的是操作系统的文件路径，否则默认为HDFS的文件路径

1、向t2和t3的数据表中导入数据

![](../md/img/ggzhangxiaochao/1298744-20180624164259182-932205859.png)

2、导入操作系统的一下三个文件

![](../md/img/ggzhangxiaochao/1298744-20180624164345452-1131321437.png)

执行导入命令

![](../md/img/ggzhangxiaochao/1298744-20180624164432856-683670742.png)

![](../md/img/ggzhangxiaochao/1298744-20180624164545284-1334156018.png)

![](../md/img/ggzhangxiaochao/1298744-20180624164633939-10294608.png)

3、将HDFS文件中的数据导入到t3中

![](../md/img/ggzhangxiaochao/1298744-20180624164731241-250624960.png)

4、导入到分区表中

指明2个文件

![](../md/img/ggzhangxiaochao/1298744-20180624164900323-1506698838.png)

导入分区表中的命令

![](../md/img/ggzhangxiaochao/1298744-20180624164946150-1412363197.png)

