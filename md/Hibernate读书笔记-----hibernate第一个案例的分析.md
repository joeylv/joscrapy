##Hibernate读书笔记-----hibernate第一个案例的分析

##
## 上一篇波博客我部署的第一个hibernate工程，现在就这个工程里面的细节来分析下。

##
##

##
## 一、POJO类

##
## POJO类即持久化对象。他是完成hibernate持久化操作。说本质点就是简单的java类。但是并不是所有的java类都可以是POJO的。对于这个java类它是有如下几个限制：

##
##1、它必须存在默认的构造方法

##
## 如果存在带参数的构造方法，那么hibernate就不能管理这个pojo了。

##
##2、有无意义的标示符id

##
## 这个是可选的。这个id和表里面的主键是相对应的。一般来说hibernate是建议有这个属性id的。因为这样hibernate操作就会更加方便和高效率。

##
##3、这个类应该是非final的

##
## 如果某个类是final的话，这个类就不能被继承了。那么这样就可能对懒加载有些影响。

##
##4、为每个属性提供setter和getter方法

##
## Hibernate默认采用属性方式来访问持久化类的属性。

##
##

##
##二、映射文件

##
##对于以下映射文件：

##
##	 1 <?xml version="1.0" encoding="gb2312"?> 2 <!DOCTYPE hibernate-mapping PUBLIC  3     "-//Hibernate/Hibernate Mapping DTD 3.0//EN" 4     "http://www.hibernate.org/dtd/hibernate-mapping-3.0.dtd"> 5 <!--hibernate-mapping是映射文件的根元素 --> 6 <hibernate-mapping> 7     <!-- 为每个class元素对应一个持久对象 --> 8     <class name="com.app.domain.News" table="news"> 9         <id name="id">10             <!-- 指定主键生成策略 -->11             <generator class="identity" />12         </id>13         <!-- property元素定义常规属性 -->14         <property name="title"></property>15         <property name="content"></property>16     </class>17     </hibernate-mapping>

##
##

##
##

##
##这里只简单的介绍下：

##
##首先来看class。对于<class.../>元素。每个<class.../>元素都是对应一个持久化类的映射。它代表了一个类。在<hibernate-mapping...>元素中可以包含多个<class../>元素，也就是说一个映射文件可以定义多个持久化类。但是建议一般不要这么做。最好的方法是一个映射文件对应一个持久化类。

##
##name属性：用来指定该持久化映射的持久化类的类名。我这里采用的是全限局的类名。如果不使用全限局的类名，就必须在<hibernate-mapping.../>元素里指定package属性。name属性的作用是hibernate可以通过这个属性或者package属性来唯一确定相应的持久化对象。

##
##table属性：这个属性对应着数据库里的表。通过这个属性，hibernate就可以确定数据库里的那个表和那个持久化对象相关联。如果缺省这个属性，就代表了数据库里的表名和java类的类名是一样的。

##
##<id.../>标签：该标签是用来映射主键的。其中的name属性用来指定持久化类标识属性名。<generator.../>用来定义主键生成策略。

##
##<property.../>：标签：该标签用来映射普通属性。

##
##

##
##以下会对hibernate的映射文件做详细的介绍。。。