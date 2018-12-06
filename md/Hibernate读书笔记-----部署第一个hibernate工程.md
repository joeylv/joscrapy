##Hibernate读书笔记-----部署第一个hibernate工程

##
## 在介绍hibernate之前我们有必要的简单了解一下ORM

##
## 目前的主流数据库依然是关系型数据库，但是java则是面向对象的编程语言，当把两者结合在一起使用时非常麻烦。这时便催生了ORM框架的产生。

##
##ORM，全称为Object/RelationMapping，即对象/关系数据库映射，我们可以把他理解成一种规范。它完成面向对象的编程语言到关系数据库的映射。因此，我们可以把ORM框架作为面向对象编程语言到数据库之间的桥梁。

##
##

##
##当我们采用ORM框架之后，应用程序不再直接访问数据库，而是以面向对象的方式来操作持久化对象，而ORM框架则将这些面向对象的操作转化为底层的SQL操作。所以我们可以把ORM的作用理解为:把持久化对象的保存、删除、修改等操作，转换成对数据库的操作。所以我们在编程的过程中，只需要以面向对象的方式来操作持久化对象，而不需要理会相对应的SQL操作，ORM框架会自动的负责转换成对应的SQL操作。

##
##

##
##Hibernate就是ORM框架中的一种。Hibernate是一个面向对象java环境的对象/关系数据库映射工具，用来把对象模型表示的对象映射到基于SQL的关系模型数据结构中去。

##
##

##
##在详细介绍hibernate之前，先部署一个简单的hibernate应用。

##
##

##
##步骤如下:

##
##一、将必要的jar包添加到WEB-INF/lib中去。

##
##

##
##先下载一个hibernate的压缩包。将包下的hibernate3.jar和lib路径下的required、jpa子目录下所有JAR包添加到应用程序的WEB-INF/lib路径下。注意由于hibernate是基于JDBC的，因此还需要添加一个相应数据库的JDBC驱动。

##
##

##
## 二、编写POJO类

##
## PO,持久化对象。持久化对象的作用是完成持久化操作，简单的说就是通过该对象可对数据执行增、删、改操作---以面向对象的方式操作数据库。

##
##

##
##Hibernate是低侵入式的设计，完全采用用普通的java对象作为持久对象使用。我们在编写PO持久对象时无需理会数据库方面的，因为这一切对于应用程序是完全透明的，应用程序只需创建、删除、修改持久化对象即可。	 1 public class News { 2     private Integer id; 3     private String title; 4     private String content; 5  6     public Integer getId() { 7         return id; 8     	} 9 10     public void setId(Integer id) {11         this.id = id;12     	}13 14     public String getTitle() {15         return title;16     	}17 18     public void setTitle(String title) {19         this.title = title;20     	}21 22     public String getContent() {23         return content;24     	}25 26     public void setContent(String content) {27         this.content = content;28     	}29 30 	}

##
##

##
##三、xml文件映射

##
## 为了使PO持久化对象具有操作的能力，我们还应该提供hibernate的xml映射文件

##
## 如下：（News.hbm.xml）

##
##	 1 <?xml version="1.0" encoding="gb2312"?> 2 <!DOCTYPE hibernate-mapping PUBLIC  3     "-//Hibernate/Hibernate Mapping DTD 3.0//EN" 4     "http://www.hibernate.org/dtd/hibernate-mapping-3.0.dtd"> 5 <!--hibernate-mapping是映射文件的根元素 --> 6 <hibernate-mapping> 7     <!-- 为每个class元素对应一个持久对象 --> 8     <class name="com.app.domain.News" table="news"> 9         <id name="id">10             <!-- 指定主键生成策略 -->11             <generator class="identity" />12         </id>13         <!-- property元素定义常规属性 -->14         <property name="title"></property>15         <property name="content"></property>16     </class>17 </hibernate-mapping>

##
##

##
##

##
## 对于以上的配置，以后介绍。

##
##

##
## 通过上面的映射文件，hibernate可以理解持久化类和数据库之间的对应关系，也可以理解持久化类属性和数据表列之间的对应关系。但是无法确认要连接到那个数据库，以及连接的相关配置。这些信息对于所有的持久化类都是通用的，我们把这些通用的信息称为hibernate配置信息

##
##

##
## 我们一般都是采用xml文件作为hibernate配置文件

##
##

##
## 四、hibernate配置文件的配置	 1 <!DOCTYPE hibernate-configuration PUBLIC  2 "-//Hibernate/Hibernate Configuration DTD 3.0//EN"  3 "http://hibernate.sourceforge.net/hibernate-configuration-3.0.dtd"> 4  5 <hibernate-configuration> 6     <session-factory> 7         <!-- 指定连接数据库所用的驱动 --> 8         <property name="connection.driver_class">com.microsoft.sqlserver.jdbc.SQLServerDriver</property> 9         <!-- 指定连接数据的url -->10         <property name="connection.url">jdbc:sqlserver://localhost:1433;databaseName=test</property>11         <!-- 指定连接数据库的用户名 -->12         <property name="connection.username">sa</property>13         <!-- 指定数据库的密码-->14         <property name="connection.password">SQL2005</property>15         <!-- 指定连接池里最大的连接数 -->16         <property name="hibernate.c3p0.max_size">200</property>17         <!-- 指定连接池里最小的连接数 -->18         <property name="hibernate.c3p0.min_size">1</property>19         <!-- 指定连接池里连接的超时时长 -->20         <property name="hibernate.c3p0.timeout">5000</property>21         <!-- 指定连接池里最大缓存多少个Statement对象 -->22         <property name="hibernate.c3p0.max_statements">100</property>23         <property name="hibernate.c3p0.idle_test_period">3000</property>24         <property name="hibernate.c3p0.acquire_increment">2</property>25         26         <!-- 指定数据库方言 -->27         <property name="dialect">org.hibernate.dialect.SQLServerDialect</property>28         <!-- 根据需要自动创建数据表 -->29         <property name="hbm2ddl.auto">update</property>30         <!-- 映射文件 -->31         <mapping resource="com/app/domain/News.hbm.xml" />32     </session-factory>33 </hibernate-configuration>

##
##

##
##

##
## 通过上面的一些配置后，我们就可以实现hibernate的功能了。

##
## 下面的代码是向数据库中插入一条记录	 1 public class NewsManager { 2  3     public static void main(String[] args) { 4         //实例化Congiguration,默认加载hibernate.cfg.xml文件 5         Configuration conf = new Configuration().configure(); 6         //以Configuration创建Sessionfactory 7         SessionFactory sf = conf.buildSessionFactory(); 8         //创建session 9         Session session = sf.openSession();10         Transaction tx = session.beginTransaction();11         //创建消息实例12         News n = new News();13         n.setTitle("疯狂java联盟成立了");14         n.setContent("疯狂java联盟成立了,网站地址http://www.crazyit.org");15         //保存消息16         session.save(n);17         //提交事务18         tx.commit();19         //关闭session20         session.close();21         sf.close();22     	}23 	}

##
##