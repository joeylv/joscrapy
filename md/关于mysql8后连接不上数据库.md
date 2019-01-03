将本地 MySQL 数据库升级版本后（升级到 8.0.11） ，发现原来的代码连接不上数据库了。检查了很多遍配置都没有发现问题。想到 MySQL 8
后发生了很多改变，所以才想可能是因为 mysql8.0 java 驱动的问题，搜索发现 8.0.11 版本的 mysql
的驱动连接方式不一样，之前我们这边用的是 com.mysql.jdbc.Driver ，而 8.0.11 要用
com.mysql.cj.jdbc.Driver ，此外 mysql8.0 是不需要建立 ssl 连接的，所以需要关闭掉，最后需要设置 CST 。

使用 mysql8.0.11 版本的话，需要做以下修改。

驱动修改成 8.0.11 的

    
    
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.11</version>
    </dependency>
    

再修改 连接配置

    
    
    jdbc.url=jdbc:mysql://localhost:3306/xxadmin?useSSL=false&serverTimezone=UTC&characterEncoding=utf8&allowMultiQueries=true
    

这样就可以连接数据库了。

