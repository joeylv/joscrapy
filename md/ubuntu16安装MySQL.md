MySQL 是一种开源数据库管理系统，通常作为流行的LAMP（Linux，Apache，MySQL，PHP / Python /
Perl）堆栈的一部分安装。它使用关系数据库和SQL（结构化查询语言）来管理其数据。

安装的方式很简单：更新软件包索引，安装mysql-server软件包，然后运行附带的安全脚本即可。

    
    
    sudo apt-get update
    sudo apt-get install mysql-server 
    sudo mysql_secure_installation
    

本教程将介绍如何在 [Ubuntu](https://www.linuxidc.com/topicnews.aspx?tid=2 "Ubuntu")
16.04 服务器上安装 MySQL 5.7 版本。但是，如果要将现有的 MySQL 安装更新为 5.7 版，可以阅读此 MySQL 5.7 更新指南。

### 步骤1 – 安装MySQL

在 Ubuntu 16.04 中，默认情况下，只有最新版本的 MySQL 包含在 APT 软件包存储库中。在撰写本文时，那是 MySQL 5.7

要安装它，只需更新服务器上的包索引并安装默认包 apt-get。

    
    
    sudo apt-get update
    sudo apt-get install mysql-server
    

系统将提示您在安装过程中创建 root 密码。选择一个安全的密码，并确保你记住它，因为你以后需要它。接下来，我们将完成 MySQL 的配置。

### 步骤2 – 配置MySQL

因为是全新安装，您需要运行附带的安全脚本。这会更改一些不太安全的默认选项，例如远程 root 登录和示例用户。在旧版本的 MySQL
上，您需要手动初始化数据目录，但 Mysql 5.7 已经自动完成了。

运行安全脚本。

    
    
    sudo mysql_secure_installation
    

这将提示您输入您在步骤1中创建的 root 密码。您可以按 Y，然后 ENTER 接受所有后续问题的默认值，但是要询问您是否要更改 root
密码。您只需在步骤 1 中进行设置即可，因此无需现在更改。

最后，我们来测试MySQL安装。

### 步骤3 – 测试MySQL

按上边方式安装完成后，MySQL应该已经开始自动运行了。要测试它，请检查其状态。

    
    
    systemctl status mysql.service
    

您将看到类似于以下内容的输出：

    
    
    mysql.service - MySQL Community Server
    Loaded: loaded (/lib/systemd/system/mysql.service; enabled; vendor preset: en Active: active (running) since Wed 2016-11-23 21:21:25 UTC; 30min ago Main PID: 3754 (mysqld) Tasks: 28 Memory: 142.3M CPU: 1.994s CGroup: /system.slice/mysql.service └─3754 /usr/sbin/mysqld
    

如果MySQL没有运行，您可以启动它：

    
    
    sudo systemctl mysql start
    

如果额外的检查，您可以尝试使用该 mysqladmin 工具连接到数据库，该工具是允许您运行管理命令的客户端。例如，该命令表示以 root（-u
root）方式连接到 MySQL ，提示输入密码（-p）并返回版本。

    
    
    mysqladmin -p -u root version
    

你应该看到类似的输出：

    
    
    mysqladmin  Ver 8.42 Distrib 5.7.16, for Linux on x86_64
    Copyright (c) 2000, 2016, [Oracle](https://www.linuxidc.com/topicnews.aspx?tid=12 "Oracle") and/or its affiliates. All rights reserved.
    Oracle is a registered trademark of Oracle Corporation and/or its affiliates. Other names may be trademarks of their respective owners.
    Server version 5.7.16-0ubuntu0.16.04.1 Protocol version 10 Connection Localhost via UNIX socket UNIX socket /var/run/mysqld/mysqld.sock Uptime: 30 min 54 sec
    Threads: 1 Questions: 12 Slow queries: 0 Opens: 115 Flush tables: 1 Open tables: 34 Queries per second avg: 0.006
    

这意味着MySQL正在运行。

