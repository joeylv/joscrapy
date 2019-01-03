四、N—N关联关系

1.1单向N-N的关联

单向的N-N关联和1-N关联的持久化类完全一样，控制关系的一端需要增加一个set集合属性，被关联的持久化实例以集合的形式存在。

N-N关联必须使用连接表，N-N关联与有连接表的1-N关联非常相似，只需要去掉<many-to-
many.../>元素的unique="true"即可。其他的配置和1-N关联一样。

由于与1-N关联非常相似，这里就不演示了。

1.2双向N-N的关联

对于双向的N-N关联，我们只需要转换为两个1-N关联模型即可。双向N-N关联两端都需要使用set集合属性，两端都增加对集合属性的访问。双向N-
N同样必须使用连接表来建立两个实体之间的关联关系。

以学生、老师为例:下面为两个实体的持久化类：

Student

    
    
     1 public class Student {
     2     private Integer id;
     3     private String name;
     4     private Set<Teacher> teachers;
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
    22     public Set<Teacher> getTeachers() {
    23         return teachers;
    24     }
    25 
    26     public void setTeachers(Set<Teacher> teachers) {
    27         this.teachers = teachers;
    28     }
    29 }

Teacher

    
    
     1 public class Teacher {
     2     private Integer id;
     3     private String name;
     4     private Set<Student> students;
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
    22     public Set<Student> getStudents() {
    23         return students;
    24     }
    25 
    26     public void setStudents(Set<Student> students) {
    27         this.students = students;
    28     }
    29 
    30 }

双向N-
N关联的映射文件需要使用<set.../>元素，用以映射集合属性。<set.../>属性还需要增加<key.../>子元素来映射外键列，同时还应该增加<many-
to-many.../>子元素来映射关联实体类。两个映射文件如下：

Student.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Student" table="student">
     3         <id name="id" column="student_id">
     4             <generator class="native" />
     5         </id>
     6         
     7         <property name="name" column="student_name" />
     8         
     9         <!-- 映射N-N关联实体，两边的table应该以样 -->
    10         <set name="teachers" table="student_teacher">
    11             <!-- 映射关联的外键 列-->
    12             <key column="student_id" />
    13             <!-- 映射关联类属性 -->
    14             <many-to-many class="Teacher" column="teacher_id" />
    15         </set>
    16     </class>
    17 </hibernate-mapping>

Teacher.hbm.xml

    
    
    <hibernate-mapping package="com.hibernate.domain">
        <class name="Teacher" table="teacher">
            <id name="id" column="teacher_id">
                <generator class="native" />
            </id>
            
            <property name="name" column="teacher_name" />
            
            <!-- 映射N-N关联实体，两边的table应该以样 -->
            <set name="students" table="student_teacher">
                <!-- 映射关联的外键 列-->
                <key column="teacher_id" />
                <!-- 映射关联类属性 -->
                <many-to-many class="Student" column="student_id"></many-to-many>
            </set>
        </class>
    </hibernate-mapping>
    
    
              双向N-N关联的双边都需要指定连接表的表名，外键列的列名，所以两个<set.../>元素的table属性的值必须指定且一样。<set.../>元素的两个子元素:<key../>、<many-to-many.../>都必须指定column属性。<key.../>和<many-to-many.../>分别是指定本持久化类、关联类在连接表中的外键列。因此两边的<key.../>和<many-to-many.../>的column属性的值应该是交叉相等。

通过下面的操作类来添加两个Student对象和两个Teacher对象

    
    
     1     static void add(){
     2         Session session = HibernateUtil.getSession();
     3         Transaction tx = session.beginTransaction();
     4         
     5         Teacher teacher1 = new Teacher();
     6         teacher1.setName("teacher1");
     7         
     8         Teacher teacher2 = new Teacher();
     9         teacher2.setName("teacher2");
    10         
    11         Student student1 = new Student();
    12         student1.setName("student1");
    13         
    14         Student student2 = new Student();
    15         student2.setName("student2");
    16         
    17         //建立两者之间的关系
    18         Set<Student> ss = new HashSet<Student>();
    19         ss.add(student1);
    20         ss.add(student2);
    21         
    22         teacher1.setStudents(ss);
    23         teacher2.setStudents(ss);
    24         
    25         session.save(teacher1);
    26         session.save(teacher2);
    27         session.save(student1);
    28         session.save(student2);
    29         
    30         tx.commit();
    31         session.close();
    32     }

  
注意：这里只能由一边建立关联关系，就是说只能由Student对象建立与Teacher对象的关联或者由Teachert对象建立与Student对象的关联。否则将会出现主键重复错误

