先看User持久化类：

    
    
     1 public class Users {
     2     private int id;
     3     private Date birthday;
     4     private Name name;
     5 
     6     public int getId() {
     7         return id;
     8     }
     9 
    10     public void setId(int id) {
    11         this.id = id;
    12     }
    13 
    14     public Date getBirthday() {
    15         return birthday;
    16     }
    17 
    18     public void setBirthday(Date birhday) {
    19         this.birthday = birhday;
    20     }
    21 
    22     public Name getName() {
    23         return name;
    24     }
    25 
    26     public void setName(Name name) {
    27         this.name = name;
    28     }
    29 
    30 }

  
从User持久化类中可以看到name不再是一个简单的String，而是一个类。在这里name就是一个组件属性，在name类中可以包含基本数据类型、字符型、日期型甚至是组件和关联实体。从User持久化类中我们看不出name是关联实体还是普通的组件属性。但是如果我们将Name映射成持久化实体，那么Name就是关联实体，如果不映射成持久化类，那么就是组件属性。这里我们不将Name映射成持久化类。

Name类如下：

    
    
     1 public class Name {
     2     private String firstName;
     3     private String lastName;
     4 
     5     public String getFirstName() {
     6         return firstName;
     7     }
     8 
     9     public void setFirstName(String firstName) {
    10         this.firstName = firstName;
    11     }
    12 
    13     public String getLastName() {
    14         return lastName;
    15     }
    16 
    17     public void setLastName(String lastName) {
    18         this.lastName = lastName;
    19     }
    20 
    21 }

为了映射User类中的Name组件，映射文件中使用<component.../>元素来映射该主键元素。映射文件如下：

User.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Users">
     3         <id name="id">
     4             <generator class="native" />
     5         </id>
     6 
     7         <property name="birthday" />
     8         
     9         <!-- 映射组件元素 -->
    10         <component name="name">
    11             <!-- 映射组件的name属性指向包含实体 -->
    12             <property name="firstName" column="first_name"/>
    13             <property name="lastName" column="last_name"/>
    14         </component>
    15     </class>
    16 </hibernate-mapping>

操作类如下：

    
    
     1 public class UserManager {
     2 
     3     public static void main(String[] args) {
     4         Session session = HibernateUtil.getSession();
     5         Transaction tx = session.beginTransaction();
     6         
     7         Users users = new Users();
     8         users.setBirthday(new Date());
     9         Name name = new Name();
    10         
    11         name.setFirstName("first name");
    12         name.setLastName("last name");
    13         users.setName(name);
    14         
    15         session.save(users);
    16         tx.commit();
    17         session.close();
    18     }
    19 
    20 }

