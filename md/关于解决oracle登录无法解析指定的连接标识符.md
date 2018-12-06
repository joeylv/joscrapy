##关于解决oracle登录无法解析指定的连接标识符

##
## 准备五一开始学习oracle，所以今天就打算把oracle10g安装下。安装完后就来进行测试是否能够正常的工作。

##
## 在安装的过程中，配置的全局数据库为tmt。

##
## 但是使用SQLPlus登陆的时候，用户名：scott，口令为：tiger，主机字符串为：tmt。但是总是登陆不上，报提示ora-12154tns无法解析指定的连接标识符。百度了下，原来是我的TNSNAMES.ORA文件中并没有tmt的相关配置。于是对TNSNAMES.ORA文件增加如下配置：

##
##TMT =  (DESCRIPTION =    (ADDRESS_LIST =      (ADDRESS = (PROTOCOL = TCP)(HOST = YSGH6H9W2BXHOIL)(PORT = 1521))    )    (CONNECT_DATA =      (SERVICE_NAME = tmt)    )  ) 

##
##

##
##

##
## 然后再登陆，就可以登陆成功了。

##
## 当然也可以使用NetManager图形界面来生成该文件。

##
## 如下：

##
##1、

##
##

##
##

##
##2、

##
##

##
##

##
##3、

##
##

##
##

##
##4、

##
##

##
##

##
##5、

##
##

##
##6、

##
##

##
##

##
##这样就可以登录成功了！！！

##
##