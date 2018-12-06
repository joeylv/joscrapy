##oracle------http://localhost:5560/isqlplus 打不开的解决方案

##
## 今天打算复习下oracle，本来oracle是以前安装的，重新安装了系统，大概重新装了系统对其有影响吧，在服务表中发现没有了lister该项。于是为了保险起见重新安装了oracle。配置什么都是正确的，但是通过http://localhost:5560/isqlplus时，突然发现http://localhost:5560/isqlplus打不开了。

##
## 解决方案：

##
## 首先进入CMD

##
## 1.用命令：netstat -an 查看端口5560是否打开

##
## 2.用isqlplusctl start 启动

##
## 3.打开IE 输入http://localhost:5560/isqlplus就可以打开了！

##
##