三、1—N

对于1-N而言，它的持久化类发生了一点改变，持久化类里需要使用集合属性。因为1的一端需要访问N的一端，而N的一端将以集合(Set)形式表现。

1、单向1-N关联

对于单向的1-N关联关系，只需要在1的一端增加Set类型的属性，该属性记录当前实体的关联实体。

同样以员工-部门为例(Employee-->Department)。两个持久化类如下：

Department

    
    
     1 public class Department {
     2     private Integer id;
     3     private String name;
     4     private Set<Employee> employees;          //关联关系
     5 
     6     public Integer getId() {
     7         return id;
     8     }
     9 
    10     public void setId(Integer id) {
    11         this.id = id;
    12     }
    13 
    14     public String getName() {
    15         return name;
    16     }
    17 
    18     public void setName(String name) {
    19         this.name = name;
    20     }
    21 
    22     public Set<Employee> getEmployees() {
    23         return employees;
    24     }
    25 
    26     public void setEmployees(Set<Employee> employees) {
    27         this.employees = employees;
    28     }
    29 
    30 }
    31  

Employee

    
    
     1 public class Employee {
     2     private Integer id;
     3     private String name;
     4 
     5     public Integer getId() {
     6         return id;
     7     }
     8 
     9     public void setId(Integer id) {
    10         this.id = id;
    11     }
    12 
    13     public String getName() {
    14         return name;
    15     }
    16 
    17     public void setName(String name) {
    18         this.name = name;
    19     }
    20 
    21 }

  

1.1基于无连接表的单向1-N关联

对于1-N的单向关联，需要在1的一端增加对应的集合映射元素，如<set.../>、<bag.../>。在集合元素中需要增加<key.../>子元素，该子元素用来映射外键。同时集合元素中需要使用<one-
to-many.../>元素来映射1-N关联关系。

下面是Department的映射文件Department.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain" >
     2     <class name="Department" table="department">
     3         <id name="id" column="departmentID">
     4             <generator class="native" />
     5         </id>
     6         
     7         <property name="name" column="departmentName" />
     8         
     9         <!-- 映射集合属合 -->
    10         <set name="employees" inverse="true" >
    11             <!-- 指定关联的外键列 -->
    12             <key column="departmentID" />
    13             <!-- 用以映射到关联类属性 -->
    14             <one-to-many class="Employee"/>
    15         </set>    
    16     </class>
    17 </hibernate-mapping>

  
对于上面的映射文件，映射<set.../>元素时并没有指定cascade属性，在默认的情况下，对主表实体的持久化操作不会级联到从表实体。

Employee.hbm.xml

    
    
    1 <hibernate-mapping package="com.hibernate.domain">
    2     <class name="Employee" table="employee">
    3         <id name="id" column="employeeID">
    4             <generator class="native" />
    5         </id>
    6         <property name="name" column="employeeName" />    
    7     </class>
    8 </hibernate-mapping>

  
使用下面代码来操作Department和Employee实体：保存一个Department实体和两个Employee实体

    
    
     1 static void add(){
     2         Session session = HibernateUtil.getSession();
     3         Transaction tx = session.beginTransaction();
     4         
     5         Department department = new Department();
     6         department.setName("国防部");
     7         
     8         //建立两个对象
     9         Employee employee1 = new Employee();
    10         employee1.setName("chentmt1");
    11         
    12         Employee employee2 = new Employee();
    13         employee2.setName("chentmt2");
    14 
    15         Set<Employee> emps = new HashSet<Employee>();
    16         emps.add(employee1);
    17         emps.add(employee2);
    18         
    19         //设置Department和Employee之间的关联关系
    20         department.setEmployees(emps);       
    21     
    22         session.save(department);          //....1
    23         session.save(employee2);
    24         session.save(employee1);
    25         tx.commit();
    26         session.close();
    27     }

  
分析上面代码段：

当程序运行到....1的时候，系统会持久化该对象：Department，而且这个对象已经关联了两个Employee对象。在这个时候Hibernate需要完成两件事：

1、执行insert语句想department表中插入一条记录

2、Hibernate试图执行update语句，将当前的department表记录关联的employee表记录的外键departmentID修改为该department记录的主键的值。

下面为上面代码段的sql语句：

    
    
    1 Hibernate: insert into department (departmentName) values (?)
    2 
    3 Hibernate: insert into employee (employeeName) values (?)
    4 
    5 Hibernate: insert into employee (employeeName) values (?)
    6 
    7 Hibernate: update employee set departmentID=? where employeeID=?
    8 
    9 Hibernate: update employee set departmentID=? where employeeID=?

从上面的sql语句中我们可以看到虽然程序仅仅需要为Department实体增加一个关联Employee实体，但是Hibernate会采用两条SQL语句来完成：一条inset语句插入一个条外键为null的employee记录，一条update语句修改插入的employee记录。造成这个问题的根本原因就在于：从Department到Employee的关联并没有被当中为Department对象状态的一部分（程序是通过吧Employee实体添加到Department实体的集合属性中，而Employee实体并不知道她所关联的Department实体），因而Hibernate无法在执行insert语句为该外键指定值。

为了解决这个问题，程序必须在持久化Employee实体之前，让Employee实体能够知道它所关联的Department实体，也就是通过employee.setDepartment(department);方法建立关联关系，但是这个时候就已经变成了1-N的双向关联。所以，尽量少用1-N的单向关联，而改用1-N的双向关联。

1.2基于有连接表的单向1-N关联

对于有连接表的1-N关联映射，映射文件不再使用<one-to-many..../>元素映射关联实体，而是使用<many-to-
many.../>元素，但是为了保证当前实体是1的一端，我们需要增加一个属性：unique="true"。

所以Department.hbm.xml配置文件如下：

    
    
     1 <hibernate-mapping package="com.hibernate.domain" >
     2     <class name="Department" table="department">
     3         <id name="id" column="departmentID">
     4             <generator class="native" />
     5         </id>
     6         <property name="name" column="departmentName" />
     7         
     8         <set name="employees" inverse="true" table="department_employee">
     9             <!-- 指定关联的外键列 -->
    10             <key column="departmentID" />
    11             <!-- 用以映射到关联类属性 -->
    12             <many-to-many class="Employee" column="employeeID" unique="true"/>
    13         </set>
    14     </class>
    15 </hibernate-mapping> 

Employee.hbm.xml配置文件保持不变

如果我们依然通过使用操作方法：保存一个Department、两个Employee，这个时候，系统应该是产生5条sql语句。其中两条是用于向连接表中插入记录，从而建立Department和Employee之间的关联关系。

2、双向1-N关联

对于1-N关联，Hibernate推荐使用双向关联，而且不要让1端控制关联关系，而使用N的一端控制关联关系。

双向的1-N关联，两端都需要增加对关联属性的访问，N的一端增加引用到关联实体的属性，1的一端增加集合属性，集合元素为关联实体。

两个持久化类和上面差不多，只需要在Employee中增加对Department的引用属性即可。

2.1无连接表的双向1-N关联

对于无连接表的双向1-N关联。N的一端需要增加<many-to-
one.../>元素来映射关联属性，而1的一端需要使用<set.../>或者<bag.../>元素来映射关联属性。同时<set.../>或者<bag../>元素需要增加<key.../>子元素映射外键列，并且使用<one-
to-many.../>子元素映射关联属性。

在前面已经提到对于1-N关联映射，通常不提倡1的一端控制关联关系，而应该由N的一端来控制关联关系。此时我们可以再<set.../>元素中指定inverse="true"，用于指定1的一端不控制关联关系

Department映射文件:Department.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain" >
     2     <class name="Department" table="department">
     3         <id name="id" column="departmentID">
     4              <generator class="native" />
     5         </id>
     6         <property name="name" column="departmentName" />
     7         <!-- 映射集合属合 -->
     8         <set name="employees" inverse="true" >
     9             <!-- 指定关联的外键列 -->
    10             <key column="departmentID" />
    11             <!-- 用以映射到关联类属性 -->
    12             <one-to-many class="Employee"/>
    13         </set>    
    14     </class>
    15 </hibernate-mapping>

  
Employee映射文件：Employee.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Employee" table="employee">
     3         <id name="id" column="employeeID">
     4             <generator class="native" />
     5         </id>
     6         <property name="name" column="employeeName" />
     7         <!-- 用于映射N-1关联实体，指定关联实体类为 :Department,指定外键为：departmentID-->
     8         <many-to-one name="department" column="departmentID" />    
     9     </class>
    10 </hibernate-mapping>

  
下面的程序段用于保存一个Department对象和两个Employee对象

    
    
     1     static void add(){
     2         Session session = HibernateUtil.getSession();
     3         Transaction tx = session.beginTransaction();
     4         
     5         Department department = new Department();
     6         department.setName("国防部");
     7         
     8         //建立两个对象
     9         Employee employee1 = new Employee();
    10         employee1.setName("chentmt1");
    11         employee1.setDepartment(department);      //建立两个对象的关联关系
    12         
    13         Employee employee2 = new Employee();
    14         employee2.setName("chentmt2");
    15         employee2.setDepartment(department);      //建立两个对象的关联关系
    16       
    17         session.save(department);          //....1
    18         session.save(employee2);
    19         session.save(employee1);
    20         tx.commit();
    21         session.close();
    22     }

  
SQL语句：

    
    
    1 Hibernate: insert into department (departmentName) values (?)
    2 
    3 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)
    4 
    5 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)

  
通过上面的SQL语句可以看出，Hibernate并不是采用哪种先insert后update的方式来插入employee记录的。而是通过一条insert
SQL语句来执行的。为什么？因为程序持久化Employee实体之前，Employee已经知道它所关联Department实体（employee2.setDepartment(department);）。
所以为了保证比较好的性能，需要注意以下两个问题：

1、应该先持久化主表对象：Department。因为我们希望程序在持久化从表：Employee对象时，Hibernate可以为他的外键属性值分配值。

2、先设置两个持久化类（Department和Employee）的关系，再保存持久化从表对象（Employee）。如果顺序反过来，程序持久化Employee对象时，该对象还没有关联实体，所以Hibernate不能为对应记录的外键列指定值，等到设置关联关系时，Hibernate只能再次使用update语句来修改了。

2.2有连接表的双向1-N关联

有连接表的双向1-N关联。1的一端使用集合元素映射，然后在集合元素中增加<many-to-
many../>子元素，该子元素映射到关联类。为保证该实体是1的一端，需要增加unique="true"属性。N的一端则使用<join.../>元素来强制使用连接表。

在N的一端使用<join../>元素强制使用连接表，因此将使用<key.../>子元素来映射连接表中外键列，器且使用<many-to-
one../>来映射连接表中关联实体的外键列；反过来，1的一端也将在<set.../>元素中使用<key.../>和<many-to-
many.../>两个子元素，他们也映射到连接表的两列。为了保证得到正确的映射关系，应该满足如下关系：<join.../>里<key.../>子元素的column属性和<set.../>里<man-
to-many.../>元素的column属性相同；<join.../>里<many-to-
many.../>子元素的column属性和<set../>元素的<key../>子元素的column属性应该相等。

下面就是Department和Employee两个持久化类的映射文件：

Department.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain" >
     2     <class name="Department" table="department">
     3         <id name="id" column="departmentID">
     4             <generator class="native" />
     5         </id>
     6         <property name="name" column="departmentName" />
     7         <set name="employees" inverse="true" table="department_employee">
     8             <!-- 指定关联的外键列 -->
     9             <key column="departmentID" />
    10             <!-- 用以映射到关联类属性 -->
    11             <many-to-many class="Employee" column="employeeID" unique="true"/>
    12         </set>
    13         
    14     </class>
    15 </hibernate-mapping>

Employee.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Employee" table="employee">
     3         <id name="id" column="employeeID">
     4             <generator class="native" />
     5         </id>
     6         <property name="name" column="employeeName" />
     7         
     8         <!-- 使用join元素强制使用连接表 -->
     9         <join table="department_employee">
    10             <!-- key映射外键列 -->
    11             <key column="employeeID" />
    12             <!-- 映射关联实体 -->
    13             <many-to-one name="department" column="departmentID" />
    14         </join>  
    15     </class>
    16 </hibernate-mapping>

