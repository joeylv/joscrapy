Hibernate3 提供了一种创新的方式来处理具有“显性(visibility)”规则的数据，那就是使用Hibernate filter。
Hibernate filter是全局有效的、具有名字、可以带参数的过滤器， 对于某个特定的Hibernate
session您可以选择是否启用（或禁用）某个过滤器。

一旦启用了数据过滤器，则不管是数据查询，还是数据加载，该过滤器将自动作用于所有数据，只有满足过滤条件的记录才会被选出来。

过滤器条件相当于定义一个 非常类似于类和各种集合上的“where”属性的约束子句，但是过滤器条件可以带参数。
应用程序可以在运行时决定是否启用给定的过滤器，以及使用什么样的参数值。 过滤器的用法很像数据库视图，只不过是在应用程序中确定使用什么样的参数的。

过滤器分以下几步：

1、定义过滤器。

要使用过滤器，必须首先在相应的映射节点中定义。而定义一个过滤器，要用到位于<hibernate-mapping/> 节点之内的<filter-
def/>节点：

    
    
    1 <filter-def name="myFilter">
    2 
    3     <filter-param name="myFilterParam" type="string"/>
    4 
    5 </filter-def>

2、使用过滤器。

定义好之后，就可以在某个类中使用这个过滤器。通过<filter.../>元素将指定的过滤器应用到指定的持久化类

    
    
    1 <class name="myClass" ...>
    2 
    3     ...
    4 
    5     <filter name="myFilter" condition=":myFilterParam = MY_FILTERED_COLUMN"/>
    6 
    7 </class>

Condition属性值是一个SQL风格的where子句，因此condition属性所指定的过滤条件应该根据表明、列名进行过滤。

也可以在某个集合使用它：

    
    
    1 <set ...>
    2 
    3     <filter name="myFilter" condition=":myFilterParam = MY_FILTERED_COLUMN"/>
    4 
    5 </set>

可以在多个类或集合中使用某个过滤器；某个类或者集合中也可以使用多个过滤器。

3、在程序中通过Session启用过滤器。

Session对象中会用到的方法有：enableFilter(String filterName), getEnabledFilter(String
filterName), 和 disableFilter(String filterName).
Session中默认是不启用过滤器的，必须通过Session.enabledFilter()方法显式的启用。
该方法返回被启用的Filter的实例。以上文定义的过滤器为例：

session.enableFilter("myFilter").setParameter("myFilterParam", "some-value");

下面是一个完整的实例

过滤器的配置文件

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <!-- 映射Person持久化类 -->
     3     <class name="Person" table="person">
     4         <!-- 映射标识属性 -->
     5         <id name="id" column="person_id">
     6             <!-- 指定identity的主键生成策略 -->
     7             <generator class="identity"/>
     8         </id>
     9         <!-- 映射普通属性 -->
    10         <property name="name" type="string"/>
    11         <property name="age" type="int"/>
    12         
    13         <!-- 使用数据过滤 -->
    14         <filter name="myFilter" condition=":filterparam = age" />
    15         </class>
    16         
    17         <!--定义Filter -->
    18         <filter-def name="myFilter">
    19             <filter-param name="filterparam" type="int"/>
    20         </filter-def>
    21 </hibernate-mapping>

  
示例程序：

    
    
     1 public class PersonManager {
     2     public static void main(String[] args) {
     3         Session  session = HibernateUtil.getSession();
     4         Transaction tx = session.beginTransaction();
     5         
     6         //启动myFilter过滤器，并且设置参数
     7         
     8         session.enableFilter("myFilter").setParameter("filterparam", 30);
     9         //查询person实体，不加任何筛选条件
    10         List list = session.createQuery("from Person as p").list();
    11         for (Iterator iterator=list.iterator();iterator.hasNext();) {
    12             Person person = (Person) iterator.next();
    13             System.out.println(person.getName());
    14         }    
    15     }
    16 }

一般来说如果某个筛选条件使用的很频繁，那么我们可以将该筛选条件设置为过滤器；如果是临时的数据筛选，还是使用常规的查询比较好。

