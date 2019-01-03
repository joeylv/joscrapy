对于面向对象的程序设计语言，继承、多态是两个最基本的概念。Hibernate的继承映射可以理解两个持久化类之间的继承关系。

Hibernate支持几种继承映射策略，不管哪种继承映射策略，Hibernate的多态查询都可以很好的运行。

假设有四个对象：Department、Employee、Skiller、Sales。他们四个对象存在如下关系：

![](http://my.csdn.net/uploads/201207/06/1341544346_8129.jpg)

从上面的关系可知：Employee与Department之间存在N-1的关联关系。Skiller和Sales都是Employee的子类。下面是这四个类的代码：

Department

    
    
    1 public class Department {
    2     private Integer id;
    3     private String name;
    4     private Set<Employee> employees;          //关联关系
    5     
    6     //省略setter和getter方法
    7 }

Employee

    
    
    1 public class Employee {
    2     private Integer id;
    3     private String name;
    4     private Department department;
    5     //省略setter和getter方法
    6 }

Skiller

    
    
    public class Skiller extends Employee {
        private String skiller;
        //省略setter和getter方法
    }

Sales

    
    
    1 public class Sales extends Employee {
    2     private int sell;
    3     //省略setter和getter方法
    4 }

一、采用subclass元素的继承映射

在这种继承映射策略下，整个继承树的所有实例都将保存在同一张表中。因为是将父类、子类的实例全部保存在同一张表中，所以需要在该表中添加列，通过该列可以区分每行记录到底是属于哪个类的实例\---这个列被称之为辨别者。

在这种继承映射策略下，我们需要使用<subclass.../>元素来映射子类的持久化类，使用<discrimainator.../>元素来映射辨别者，同时还需要给<subclass.../>元素增加discriminator-
value属性来指定每个类的辨别者的值。

映射文件如下：

    
    
    <
    
    
     1 hibernate-mapping package="com.hibernate.domain">
     2     <class name="Employee" table="employee">
     3         <id name="id" column="employeeID">
     4             <generator class="hilo" />
     5         </id>
     6          <!-- 映射辨别者 -->
     7         <discriminator column="type" type="string" />
     8         
     9         <property name="name" column="employeeName" />
    10         <!-- 用于映射N-1关联实体，指定关联实体类为 :Department,指定外键为：departmentID-->
    11         <many-to-one name="department" column="departmentID" />  
    12         
    13         <!-- 使用subclass元素映射Employee的子类Skiller --> 
    14         <subclass name="Skiller" discriminator-value="skiller">
    15             <property name="skiller" />
    16         </subclass>
    17         
    18         <!-- 使用subclass元素映射Employee的子类Sales --> 
    19         <subclass name="Sales" discriminator-value="sales">
    20             <property name="sell" />
    21         </subclass>
    22     </class>
    23 </hibernate-mapping>
    
    
             在这里我们只需要给父类进行映射就可以了。在这个配置文件中，指定了一个辨别者列：type，该列其本省是没有任何意义的，只是起到一个区分每条记录时对应哪个持久化类的作用。其中Skiller类的辨别者列type的值为skiller，Sales类的辨别者列type的值为sales。通过下面的程序段来进行操作。
    
    
     1     static void add(){
     2         Session session = HibernateUtil.getSession();
     3         Transaction tx = session.beginTransaction();
     4         
     5         Department department = new Department();
     6         department.setName("department name1");
     7         
     8         Employee emp1 = new Employee();
     9         emp1.setName("employy name1");
    10         emp1.setId(1);
    11         
    12         Skiller emp2 = new Skiller();
    13         emp2.setSkiller("电工");
    14         emp2.setName("employee name2");
    15         emp2.setDepartment(department);        //建立对象之间的关联关系
    16         
    17         Sales emp3= new Sales();
    18         emp3.setSell(50);
    19         emp3.setName("employee name3");
    20         emp3.setDepartment(department);        //建立对象之间的关联关系
    21         
    22         session.save(department);
    23         session.save(emp1);
    24         session.save(emp2);
    25         session.save(emp3);
    26         
    27         tx.commit();
    28         session.close();
    29         
    30     }

上面的程序段，hibernate将会产生如下的几条SQL语句：

    
    
    1 Hibernate: insert into department (departmentName) values (?)
    2 
    3 Hibernate: insert into employee (employeeName, departmentID, type) values (?, ?, "com.hibernate.domain.Employee")
    4 
    5 Hibernate: insert into employee (employeeName, departmentID, skiller, type) values (?, ?, ?, "skiller")
    6 
    7 Hibernate: insert into employee (employeeName, departmentID, sell, type) values (?, ?, ?, "sales")

  
在第二条sql语句，type的值为com.hibernate.domain.Employee。对于这个值可以理解为空。在第三条sql语句中，type的值为skiller，第四天sql语句中type值为sales。同时要注意第三条sql语句中的sell列是没有值的，第四条的skiller列同样也没有值。所以在这里一定要注意：使用subclass继承映射策略时，其子类中增加的属性映射的字段是一定不能有非空约束的。

表结构如下：

![](http://my.csdn.net/uploads/201207/06/1341545320_9237.jpg)

通过下面的程序段，来进行查询操作：

    
    
    1  static void query(int empid){
    2   Session session = HibernateUtil.getSession();
    3   Employee emp = (Employee) session.get(Employee.class, empid);
    4  }

得到如下SQL语句：

    
    
    1 Hibernate: select employee0_.employeeID as employeeID2_0_, employee0_.employeeName as employee3_2_0_, employee0_.departmentID as departme4_2_0_, employee0_.skiller as skiller2_0_, employee0_.sell as sell2_0_, employee0_.type as type2_0_ 
    2 
    3 from employee employee0_ where employee0_.employeeID=?

  
从上面的sql语句可以看到它是从一张表中获取所有的记录。这正是这种继承策略的一个非常大的好处：在这种映射策略下，整棵继承树的所有数据都保存在一张表中，因此不管进行怎样的查询，不管查询继承树中的那一层的实体，底层数据库都只需要在一张表中查询即可，非常方便、高效。

我们在这里给上面的查询代码增加一句：System.out.println(emp.getClass());

依次给empid赋值为：1、2得到的结果如下：

1、class com.hibernate.domain.Employee

2、class com.hibernate.domain.Skiller

有上面的输出结果可知：hibernate能够非常好处理多态查询。

一、采用joined-subclass元素的继承映射

采用这种策略时，父类实例保存在父类表里，而子类实例则有父类表和子类表共同存储。在这种策略下，是将父类与子类共有的属性保存在父类表中，而子类特有的属性，则保存在子类表中，就是说，父类一张表，子类一张表，同时子类表中需要增加父类表的外键。

采用joined-subclass来映射这种策略，并且需要为每个子类使用<key.../>元素映射共有主键\--这个主键类还将参照父表的主键列。

映射文件如下：

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Employee" table="employee">
     3         <id name="id" column="employeeID">
     4             <generator class="hilo" />
     5         </id>
     6 
     7         <property name="name" column="employeeName" />
     8         <!-- 用于映射N-1关联实体，指定关联实体类为 :Department,指定外键为：departmentID-->
     9         <many-to-one name="department" column="departmentID" />  
    10 
    11         <!-- 使用join-class元素映射Employee类的Skill而子类 -->
    12         <joined-subclass name="Skiller">
    13             <!-- 必须使用key元素映射父子类的共有主键 -->
    14             <key column="employee_id" />
    15             <property name="skiller" />
    16         </joined-subclass>
    17         
    18         <!-- 使用join-class元素映射Employee类的Sales而子类 -->
    19         <joined-subclass name="Sales">
    20             <!-- 必须使用key元素映射父子类的共有主键 -->
    21             <key column="employee_id" />
    22             <property name="sell" />
    23         </joined-subclass>
    24     </class>
    25 </hibernate-mapping>

  
通过上面的增加代码，执行添加操作。得到如下结果：

![](http://my.csdn.net/uploads/201207/06/1341545610_2850.jpg)
![](http://my.csdn.net/uploads/201207/06/1341545624_6058.jpg)

SQL语句如下：

    
    
     1 Hibernate: insert into department (departmentName) values (?)
     2 
     3 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)
     4 
     5 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)
     6 
     7 Hibernate: insert into Skiller (skiller, employee_id) values (?, ?)
     8 
     9 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)
    10 
    11 Hibernate: insert into Sales (sell, employee_id) values (?, ?)

  
从上面的SQL语句中也可以看出hibernate对与这种继承映射策略的处理。父类一张表，子类一张表同时子类引用父类外键建立关联关系。

对与这样继承映射策略的查询，hibernate采用表连接方式来获取子类表的信息：

    
    
     1 Hibernate: select employee0_.employeeID as employeeID2_0_, employee0_.employeeName as employee2_2_0_, employee0_.departmentID as departme3_2_0_, employee0_1_.skiller as skiller3_0_, employee0_2_.sell as sell4_0_, case 
     2 
     3 when employee0_1_.employee_id is not null then 1 
     4 
     5 when employee0_2_.employee_id is not null then 2 
     6 
     7 when employee0_.employeeID is not null then 0 end as clazz_0_ 
     8 
     9 from employee employee0_ left 
    10 
    11 outer join Skiller employee0_1_ 
    12 
    13 on employee0_.employeeID=employee0_1_.employee_id 
    14 
    15 left outer join Sales employee0_2_ 
    16 
    17 on employee0_.employeeID=employee0_2_.employee_id 
    18 
    19 where employee0_.employeeID=?

  
所以当使用joined-
subclass继承映射策略，当程序查询子类实例时，需要跨越多个字表查询，其复杂度取决于该子类有多少层父类。这样势必会对查询的性能有些影响。

一、采用union-subclass元素的继承映射

采用这样继承映射策略，父类实例的数据保存在父表中，子类实例的数据仅仅只保存在字表中，没有在附表中有任何记录。在这种继承映射策略下，子表的字段会比父表的字段多。

同时在这种映射策略，既不需要使用辨别者，也不需要使用<key.../>元素来映射共有主键。

映射文件如下：

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Employee" table="employee">
     3         <id name="id" column="employeeID">
     4             <generator class="hilo" />
     5         </id>
     6 
     7         <property name="name" column="employeeName" />
     8         <!-- 用于映射N-1关联实体，指定关联实体类为 :Department,指定外键为：departmentID-->
     9         <many-to-one name="department" column="departmentID" />  
    10 
    11         <!-- 使用union-subclass元素映射Employee类的子类：Skiller -->
    12         <union-subclass name="Skiller" table="skiller">
    13             <property name="skiller" />
    14         </union-subclass>
    15         
    16         <!-- 使用union-subclass元素映射Employee类的子类：Sales -->
    17         <union-subclass name="Sales" table="sales">
    18             <property name="sell" />
    19         </union-subclass>
    20     </class>
    21 </hibernate-mapping>

  
注：在这种映射策略下，映射持久化类是不能使用identity主键生成策略。

通过添加操作得到如下的两个子类表：

![](http://my.csdn.net/uploads/201207/06/1341545778_9375.jpg)

![](http://my.csdn.net/uploads/201207/06/1341545791_1260.jpg)

采用这中映射策略，底层数据库的数据看起来更加符合正常情况下的数据库设计，不同实体保存在不同的数据表中。

  

