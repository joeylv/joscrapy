二、1—1

无论是单向1-1映射关联，还是双休1-1映射关联，都有三种映射策略：基于主键、基于外键、采用连接表。

1、单向1-1映射关联

1.1、基于主键的单向1-1映射关联

对于基于主键的单向1-1关联，基于主键关联的持久化类不能拥有自己的主键生成器策略，它的主键由关联实体来负责生成。

是根据他自己的person属性来获得的。即他通过自身的一个getPerson()方法来获得Person对象。然后通过Person对象中的getID()方法获得id，然后赋值给自身id。这样就可以不需要自己来生成id。

采用基于主键的1-1关联时，应使用<one-to-one.../>元素来映射关联实体，配置<one-to-one.../>元素时需要指定一个name属性。

实例(Person<\--IDCard)

Person

    
    
     1 public class Person {
     2     private Integer id;
     3     private String name;
     4     private IDCard idCard;
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
    22     public IDCard getIdCard() {
    23         return idCard;
    24     }
    25 
    26     public void setIdCard(IDCard idCard) {
    27         this.idCard = idCard;
    28     }
    29 
    30 }    

IDCard：

    
    
     1 public class IDCard {
     2     private Integer id;
     3     private String useLife;
     4     public String getUseLife() {
     5         return useLife;
     6     }
     7 
     8     public void setUseLife(String useLife) {
     9         this.useLife = useLife;
    10     }
    11 
    12     private Person person;
    13 
    14     public Integer getId() {
    15         return id;
    16     }
    17 
    18     public void setId(Integer id) {
    19         this.id = id;
    20     }
    21 
    22     public Person getPerson() {
    23         return person;
    24     }
    25 
    26     public void setPerson(Person person) {
    27         this.person = person;
    28     }
    29 
    30 }

映射文件：

Person.hbm.xml

    
    
    1 <hibernate-mapping package="com.hibernate.domain">
    2     <class name="Person" table="person">
    3         <id name="id" column="personID">
    4             <generator class="native" />
    5         </id>
    6         
    7         <property name="name" column="personName" />    
    8     </class>
    9 </hibernate-mapping>

IDCard.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4             <!-- 基于主键关联时,主键生成策略是foreign，表明根据关联类的主键来生成该实体的主键 -->
     5             <generator class="foreign">
     6                 <!-- 指定引用关联实体的属性名  -->
     7                 <param name="property">person</param>
     8             </generator>
     9         </id>
    10         
    11         <property name="useLife" column="useLife" />
    12         <one-to-one name="person" constrained="true" />     
    13     </class>
    14 </hibernate-mapping>

在上面的映射文件中，采用这种关联映射策略是，idCard表作为从表，此时idCard表的主键将没有自己的主键生成策略。他是根据person表中的主键来生成的。同时从表(idCard)里记录的主键将会与主表（person）里的记录保存一致。

IDCard中的id既是主键也是外键。那么idCard表如何通过person表来生成主键的呢？

foreign生成器中有一个元素：property。这个元素代表了该表的外键是从哪一个属性中获得的。通过上面的配置可以发现idCard表的外键是从person属性中获得的。它的外键就是通过person属性中的getId获得id，然后将该id直接赋给id。

使用constrained="true"表明该类对应表和被关联的对象所对应的数据库表之间通过一个外键引用对主键进行约束。

通过上面的配置后，就可以对两个实体进行操作了：

    
    
     1     static void add(){
     2         Session  session = null;
     3         Transaction tx = null;
     4         try{
     5             session = HibernateUtil.getSession();
     6             tx = session.beginTransaction();
     7             IDCard idCard = new IDCard();
     8             idCard.setUseLife("10年");
     9             
    10             Person person = new Person();
    11             person.setName("chentmt");
    12             
    13             idCard.setPerson(person); 
    14             session.save(person);
    15             session.save(idCard);
    16             tx.commit();
    17             
    18         }finally{
    19             if(session!=null)
    20                 session.close();
    21         }
    22     }

1.2、基于外键的单向1-1映射关联

基于外键的关联映射与一般的N-1关联映射没有多大区别，只需要将<many-to-one.../>元素中增加unique="true"属性即可。如下：

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4             <generator class="native" />    
     5         </id>
     6         
     7         <property name="useLife" column="useLife" />
     8         
     9         <many-to-one name="person" column="personID" unique="true"/>
    10     </class>
    11 </hibernate-mapping>

unique="true"代表了idCard表的personid外键列上增加了唯一约束\--这样就完成基于外键的单向1-1映射了。

其他的配置文件和持久化类都不需要做修改。

1.3、有连接表的单向1-1映射关联

和上面差不多，只需要在有连接表的N-1关联映射中的<many-to-one.../>元素增加一个unique="true"即可。如下：

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4             <generator class="native" />    
     5         </id>
     6         
     7         <property name="useLife" column="useLife" />
     8         <!-- 使用join元素强制使用连接表 -->
     9         <join table="person_idCard">
    10              <key column="idCardID"/>
    11              <many-to-one name="person" column="personID" unique="true"/>
    12          </join>    
    13     </class>
    14 </hibernate-mapping>

2、双向1-1关联映射

对于双向的1-1关联需要让两个持久化列都增加引用关联实体的属性，并为该属性提供setter和getter方法。持久化类：如上。

2.1基于主键的双向1-1关联映射

基于主键的双向1-1关联映射同样需要在一端的主键生成器策略使用foreign策略，表明将根据对方的主键来生成自己的主键，本实体不能拥有自己的主键生成策略。另一端需要使用<one-
to-one.../>元素用来映射关联实体，否则就变成了单向的。映射文件如下：

Person.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Person" table="person">
     3         <id name="id" column="personID">
     4             <generator class="native" />
     5         </id>
     6         
     7         <property name="name" column="personName" />
     8         <!-- 映射关联实体 -->    
     9         <one-to-one name="idCard" />
    10     </class>
    11 </hibernate-mapping>

IDCard.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4         <!-- 基于主键关联时,主键生成策略是foreign，表明根据关联类的主键来生成该实体的主键 -->
     5             <generator class="foreign">
     6                 <!-- 指定引用关联实体的属性名  -->
     7                 <param name="property">person</param>
     8             </generator>
     9         </id>
    10         
    11         <property name="useLife" column="useLife" />
    12         <one-to-one name="person" constrained="true" />
    13     </class>
    14 </hibernate-mapping>

对于操作这个两个实体增加同时。因为可以通过两边来访问，所以这里就演示查询

这里查询分为两种：基于主表查询和基于从表查询

基于主表查询（通过主表查询从表记录）

    
    
     1     static void query(int personid){
     2         Session  session = null;
     3         try{
     4             session = HibernateUtil.getSession();
     5             
     6             Person person = (Person) session.get(Person.class, personid);
     7             System.out.println("useLife="+person.getIdCard().getUseLife());    
     8         }finally{
     9             if(session!=null)
    10                 session.close();
    11         }
    12     }

我们知道对于N-1关联查询的时候，系统会产生两条sql查询语句来检索从表对象：一条先查询主表，然后根据外键从从表中获取相对应的记录。但是对于1-1关联时，它并不是产生两条sql语句来查询。而是一条sql语句，通过外连接来连接两张表的。如下

    
    
    1 Hibernate: select person0_.personID as personID1_1_, 
    2 person0_.personName as personName1_1_, idcard1_.idCardID as idCardID2_0_, 
    3 idcard1_.useLife as useLife2_0_ 
    4 from person person0_ 
    5 left outer join idCard idcard1_ 
    6 on person0_.personID=idcard1_.idCardID 
    7 where person0_.personID=?

基于从表查询（通过从表查询主表）

    
    
     1     static void query(int personid){
     2         Session  session = null;
     3         try{
     4             session = HibernateUtil.getSession();
     5             
     6             IDCard idCard = (IDCard) session.get(IDCard.class, 1);
     7             System.out.println(idCard.getPerson().getName());
     8         }finally{
     9             if(session!=null)
    10                 session.close();
    11         }
    12     }

通过从表查询主表与通过主表查询从表又有点不同了。在这里它不再是产生一条sql语句，而是两条。如下：

    
    
    1 Hibernate: select idcard0_.idCardID as idCardID2_0_, idcard0_.useLife as useLife2_0_ from idCard idcard0_ where idcard0_.idCardID=?
    2 
    3 Hibernate: select person0_.personID as personID1_1_, person0_.personName as personName1_1_, idcard1_.idCardID as idCardID2_0_, idcard1_.useLife as useLife2_0_ from person person0_ left outer join idCard idcard1_ on person0_.personID=idcard1_.idCardID where person0_.personID=?

它会先查询从表，获取记录，然后再通过外连接方式连接两张表根据personID获取记录。

2.2基于外键的双向1-1关联映射

对于基于外键的双向1-1关联映射。外键可以存放任意一边。需要存放外键的一端，需要增加<many-to-
one../>元素。同时也需要添加unique="true"属性。

对于双向单位1-1关联映射，两个实体原本是处于平等状态的。但是当我们选择一个表来增加外键后，该表就变成了从表，另一个表变成主表。

另一端需要使用<one-to-one../>元素，该元素需要使用name属性指定关联属性名，同时也需要使用property-
ref属性来指定引用关联类的属性。property-ref的值是从表中的引用属性。

映射文件如下：

Person.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Person" table="person">
     3         <id name="id" column="personID">
     4             <generator class="native" />
     5         </id>
     6         
     7         <property name="name" column="personName" />
     8         <!-- 映射关联实体 -->    
     9         <one-to-one name="idCard"     property-ref="person"/>
    10     </class>
    11 </hibernate-mapping>

IDCard.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4             <generator class="native" />    
     5         
     6         </id>
     7         
     8         <property name="useLife" column="useLife" />
     9         <many-to-one name="person" column="personID" unique="true" />
    10     </class>
    11 </hibernate-mapping>

2.3有连接表的双向1-1关联映射

采用这个方式是非常少的，因为这中情况映射相当复杂，数据模型繁琐，一般不推荐采用这种策略。

双向1-1关联两端都需要使用<join.../>元素指定连接表，<join../>元素的table属性用于指定连接表的表名，所有两端的table属性值应该是一致的。同时两个也需要增加key元素映射连接表的外键列，还需要增加<many-
to-one../.>元素映射关联属性，两个<many-to-
one.../>元素都需要增加unique="true"属性。注意这里两端的key元素和<many-to-one../>中column的属性值应该是相反的。

同时为了让hibernate在连接表的两个数据列上增加唯一约束，映射文件应该为两个<key.../>元素指定unique="true"。

当使用连接表来建立1-1关联关系时，两个实体应该是绝对的平等，不存在任何的主从约束关系，hibernate映射他们的连接表时，将会选择某一个外键作为连接表的主键\--因此两个持久化类的映射文件依然不是完全相同的。映射文件必须在一端的<join.../>元素中指定inverse="true"，而另一端则指定option="true"。下面是两个映射文件

Person.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="Person" table="person">
     3         <id name="id" column="personID">
     4             <generator class="native" />
     5         </id>
     6         
     7         <property name="name" column="personName" />
     8         
     9         <join table="person_idCard" inverse="true">
    10             <key column="personID" unique="true" />
    11             <many-to-one name="idCard" column="idCardID" unique="true" />
    12         </join> 
    13     </class>
    14 </hibernate-mapping>

IDCard.hbm.xml

    
    
     1 <hibernate-mapping package="com.hibernate.domain">
     2     <class name="IDCard" table="idCard">
     3         <id name="id" column="idCardID">
     4             <generator class="native" />    
     5         </id>
     6         
     7         <property name="useLife" column="useLife" />
     8         <join table="person_idCard" optional="true">
     9             <key column="idCardID" unique="true" />
    10             <many-to-one name="person" column="personID" unique="true"></many-to-one>
    11         </join>
    12     </class>
    13 </hibernate-mapping>

  

