##Hibernate读书笔记-----Hibernate的关联映射之N-1关联映射

##
## 我们所生活的世界很少有事物是孤立存在的，每个事物必然会存在着与它相关联的事物。在面向对象设计当中，关联关系是非常重要的。关联关系一般可以分为以下两种：

##
## 单向关系：只需单向访问关联端

##
## 双向关系：关联的两端都可以互相访问

##
## 单向关系可分为：1—N、1—1、N—1、N—N

##
## 双向关系可分为：1—1、1—N、N—N

##
## 下面就上面的每种关联映射分别讲解：

##
##一、N—1关联映射

##
##1、单向N—1关联

##
## 1.1、无连接表的N-1关联（基于外键的N-1关联）

##
## 对于单向的N—1关联而言只需要从N的一端可以访问1的一端。为了让这个两个持久化类支持这种关联映射，程序应该在N的一端的持久化类中增加一个熟悉，该属性引用1一端的关联实体。

##
## 两个关联属性如下（以员工和部门之间的关系为例）：

##
##Employee：

##
##	 1 public class Employee { 2     private Integer id; 3     private String name; 4     private Department department;    //关联属性 5  6     public Integer getId() { 7         return id; 8     	} 9 10     public void setId(Integer id) {11         this.id = id;12     	}13 14     public String getName() {15         return name;16     	}17 18     public void setName(String name) {19         this.name = name;20     	}21 22     public Department getDepartment() {23         return department;24     	}25 26     public void setDepartment(Department department) {27         this.department = department;28     	}29 30 	}

##
##

##
##

##
##Department：

##
##	 1 public class Department { 2     private Integer id; 3     private String name; 4     private Set<Employee> employees; 5  6     public Integer getId() { 7         return id; 8     	} 9 10     public void setId(Integer id) {11         this.id = id;12     	}13 14     public String getName() {15         return name;16     	}17 18     public void setName(String name) {19         this.name = name;20     	}21 22     public Set<Employee> getEmployees() {23         return employees;24     	}25 26     public void setEmployees(Set<Employee> employees) {27         this.employees = employees;28     	}29 30 	}

##
##

##
##

##
##Employee端增加了Department属性，该属性并不是一个普通的组件属性，而是引用另一个持久化类的类。Hibernate使用<many-to-one.../>元素映射N—1的关联实体，直接采用<many-to-one.../>元素来映射关联实体将会在N的一端的数据表中增加一个外键，用于参照主表记录。

##
##下面为两个实体的映射文件：

##
##Employee.hbm.xml

##
##在这个映射文件中需要用<many-to-one../>来完成关联映射

##
##	 1 <hibernate-mapping package="com.hibernate.domain"> 2     <class name="Employee" table="employee"> 3         <id name="id" column="employeeID"> 4             <generator class="native" /> 5         </id> 6          7         <property name="name" column="employeeName" /> 8         <!-- 用于映射N-1关联实体，指定关联实体类为 :Department,指定外键为：departmentID--> 9         <many-to-one class="Department" name="department" column="departmentID" not-null="true"    cascade="all"/>    10     </class>11 </hibernate-mapping>

##
##

##
##

##
##Department.hbm.xml	1 <hibernate-mapping package="com.hibernate.domain" >2     <class name="Department" table="department">3         <id name="id" column="departmentID">4             <generator class="native" />5         </id>6         7         <property name="name" column="departmentName" />8     </class>9 </hibernate-mapping>

##
##

##
## 通过上面的映射后，就可以使用如下代码来保存Employee和Department实体了。	 1 //增加 2     static void add() { 3         Session s = null; 4         Transaction tx = null; 5         try { 6             s = HibernateUtil.getSession(); 7             tx = s.beginTransaction(); 8              9             Department depart = new Department();           //....110             depart.setName("组织部");11 12             Employee emp = new Employee();13             //对象模型：建立两个对象的关联关系14             emp.setDepartment(depart);                     //...2 15             emp.setName("汤妹彤");16             17             s.save(depart);                               //...318             s.save(emp);                                  //...419     20             tx.commit();21         	} finally {22             if (s != null)23                 s.close();24         	}25     	}

##
##代码分析：

##
## 当代码运行到...1的时候会创建一个瞬态的Department对象。当程序运行到...3和...4的时候，系统就会分别保存Department对象和Employee对象。会产生如下两条SQL语句：	1 Hibernate: insert into department (departmentName) values (?)2 3 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)

##
##

##
##...2这条语句非常重要，因为它是建立Department和Employee两个对象的关联关系。没有这条语句是无法建立两个对象的关系。

##
##在这里我们将...3语句和...4两条语句交换位置。这时运行就会产生三条SQL语句。当...3的时候，departmentID插入的时候为空，只有当持久化Department对象后，系统就会将departmentID修改为相对应的值。如下：	1 Hibernate: insert into employee (employeeName, departmentID) values (?, ?)2 3 Hibernate: insert into department (departmentName) values (?)4 5 Hibernate: update employee set employeeName=?, departmentID=? where employeeID=?

##
## 如果我们在Employee.hbm.xml映射文件中，给外键添加一个非空约束，即：	1 <many-to-one class="Department" name="department" column="departmentID" not-null="true"/>

##
##

##
## 上面的代码就会报空异常：org.hibernate.PropertyValueException:not-nullpropertyreferencesanullortransientvalue。

##
## 如果我们不想改变上面代码，又要能够执行。即先持久化从表。对于这种情况我们可以设置级联：cascade="all".即

##
##	1 <many-to-one class="Department" name="department" column="departmentID" not-null="true" cascade="all"/>。

##
##

##
##

##
## 通过指定了cascade="all"。这就意味着系统将先自动级联插入主表记录。

##
##所以在所有基于外键约束的关联关系中，我们必须牢记：要么总是先持久化主表对应的实体，要么设置级联操作。否则当Hibernate试图插入从表记录时，如果发现该从表参照的主表记录不存在，一定会抛出异常。

##
##

##
##2、有连接表的N-1关联

##
##对于绝大部分的单向N-1关联而言，使用基于外键的关联映射就可以了。但是如果需要使用连接表来映射单向N-1关联，则需要使用<join.../>元素，该元素用于强制将一个类的属性映射到多张表中。

##
##使用<join.../>元素映射到连接表时，需要外键关联，应在配置文件中增加<key.../>子元素来映射外键，并为<join.../>元素增加<many-to-one.../>子元素来映射N-1的关联实体。如下:

##
##	 1 <hibernate-mapping package="com.hibernate.domain"> 2     <class name="Employee" table="employee"> 3         <id name="id" column="employeeID"> 4             <generator class="native" /> 5         </id> 6          7         <property name="name" column="employeeName" /> 8         <!-- 使用join元素强制使用连接表 --> 9         <join table="employee_department">10             <!-- 映射连接表中参照本表主键的外键列 -->11             <key column="employeeID" />12             <!-- 映射连接表参照关联实体的外键列 -->13             <many-to-one name="department" class="Department" column="departmentID" />14         </join>    15     </class>16 </hibernate-mapping>

##
##

##
##

##
##