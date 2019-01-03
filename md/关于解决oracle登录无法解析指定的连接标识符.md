准备五一开始学习oracle，所以今天就打算把oracle 10g安装下。安装完后就来进行测试是否能够正常的工作。

在安装的过程中，配置的全局数据库为tmt。

但是使用SQL Plus登陆的时候，用户名：scott，口令为：tiger，主机字符串为：tmt。但是总是登陆不上，报提示
ora-12154tns无法解析指定的连接标识符。百度了下，原来是我的TNSNAMES.ORA文件中并没有tmt的相关配置。于是对TNSNAMES.ORA文件增加如下配置：

    
    
    TMT =
      (DESCRIPTION =
        (ADDRESS_LIST =
          (ADDRESS = (PROTOCOL = TCP)(HOST = YSGH6H9W2BXHOIL)(PORT = 1521))
        )
        (CONNECT_DATA =
          (SERVICE_NAME = tmt)
        )
      ) 
    
    

然后再登陆，就可以登陆成功了。

当然也可以使用Net Manager图形界面来生成该文件。

如下：

1、

![](http://my.csdn.net/uploads/201204/28/1335607917_3989.jpg)

2、

![](http://my.csdn.net/uploads/201204/28/1335607946_1415.jpg)

3、

![](http://my.csdn.net/uploads/201204/28/1335607974_5873.jpg)

4、

![](http://my.csdn.net/uploads/201204/28/1335607997_1997.jpg)

5、

![](http://my.csdn.net/uploads/201204/28/1335608035_6642.jpg)

6、

![](http://my.csdn.net/uploads/201204/28/1335608018_1396.jpg)

这样就可以登录成功了！！！

