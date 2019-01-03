当项目变得比较大的时候，如何还使用hbm.xml文件来配置Hibernate实体就会变得比较复杂。这里Hibernate提供了Annotation注解方式，使得Hibernate的映射文件变得很方便管理了。

这里简单介绍Hibernate的Annotation注解

一、声明实体

@Entity

对实体注释。任何Hibernate映射对象都要有这个注释

@Table

声明此对象映射到数据库的数据表，通过它可以为实体指定表(talbe),目录(Catalog)和schema的名字。该注释不是必须的，如果没有则系统使用默认值(实体的短类名)。

@Version

该注释可用于在实体Bean中添加乐观锁支持。

二、声明主键

@Id

声明此属性为主键。该属性值可以通过应该自身创建，但是Hibernate推荐通过Hibernate生成

@GeneratedValue

指定主键的生成策略。有如下四个值

TABLE：使用表保存id值

IDENTITY：identitycolumn

SEQUENCR ：sequence

AUTO：根据数据库的不同使用上面三个

三、声明普通属性

@Column

声明该属性与数据库字段的映射关系。

    
    
    1 @Column(nam=”category_name” length=20)
    2 Public void getCategoryName(){
    3     Return this.categoryName;
    4 } 

注意：

1、 当POJO有属性不需要映射的时候一定要用@Transitent修饰，该注释表示此属性与表没有映射关系，只是一个暂时的属性。

2、 @Lob注释表示该属性持久化为Blob或者Clob类型，具体取决于属性的类型。

四、声明关联关系

一对多关联关系

@OneToMany(mappedBy=” person”,cascade=CascadeType.ALL,fetch=FetchType.LAZY)

一对多声明

@ManyToOne(cascade=CascadeType.REFRESH,)

@JoinColumn

多对一声明 ,声明为双向关联

一对一关联关系

@OneToOne(optional= true,cascade =CascadeType.ALL, mappedBy = “person”)  
一对一关联声明  
@OneToOne(optional = false, cascade = CascadeType.REFRESH)  
@JoinColumn(name = “Person_ID”, referencedColumnName = “personid”,unique =
true)  
声明为双向关联

多对多关联关系

@ManyToMany(mappedBy= “students”)  
多对多关联声明。  
@ManyToMany(cascade = CascadeType.PERSIST, fetch = FetchType.LAZY)  
@JoinTable(name = “Teacher_Student”,  
joinColumns = {@JoinColumn(name = “Teacher_ID”, referencedColumnName
=“teacherid”)},  
inverseJoinColumns = {@JoinColumn(name = “Student_ID”, referencedColumnName
=“studentid”)})

实例：

有如下两个实体，商品:Goods，分类Category。两者是多对一的关联关系。

使用Hibernate Annotation注解如下

    
    
     1 Goods.java
     2 
     3 @Entity
     4 @Table(name = "goods", catalog = "test")
     5 public class Goods implements java.io.Serializable {
     6 
     7     private static final long serialVersionUID = 1L;
     8     private String goodsId;
     9     private Category category;
    10     private String goodsName;
    11 
    12     public Goods() {
    13     }
    14 
    15     /*
    16      * 主键
    17      * 生成策略为自动增长
    18      * 唯一、长度为20
    19      */
    20     @Id
    21     @GeneratedValue
    22     @Column(name = "goods_id", unique = true, nullable = false, length = 20)
    23     public String getGoodsId() {
    24         return this.goodsId;
    25     }
    26 
    27     public void setGoodsId(String goodsId) {
    28         this.goodsId = goodsId;
    29     }
    30 
    31     /*
    32      * 多对一关联关系
    33      * 延迟加载：fetch = FetchType.LAZY
    34      * 引用外键：category_id
    35      * 
    36      */
    37     @ManyToOne(fetch = FetchType.LAZY,cascade=CascadeType.ALL)
    38     @JoinColumn(name = "category_id")
    39     public Category getCategory() {
    40         return this.category;
    41     }
    42 
    43     public void setCategory(Category category) {
    44         this.category = category;
    45     }
    46 
    47     @Column(name = "goods_name", nullable = false, length = 50)
    48     public String getGoodsName() {
    49         return this.goodsName;
    50     }
    51 
    52     public void setGoodsName(String goodsName) {
    53         this.goodsName = goodsName;
    54     }
    55 
    56 }

Category.java

    
    
     1 @Entity
     2 @Table(name = "category", catalog = "test")
     3 public class Category implements java.io.Serializable {
     4 
     5     private static final long serialVersionUID = -1877960009126534682L;
     6 
     7     private String categoryId;
     8     private String categoryName;
     9     private Set<Goods> goodses = new HashSet<Goods>(0);
    10 
    11     public Category() {
    12     }
    13 
    14     /*
    15      * 主键
    16      * 生成策略为自动增长
    17      * 唯一、长度为20
    18      */
    19     @Id
    20     @GeneratedValue
    21     @Column(name = "category_id", unique = true, length = 10)
    22     public String getCategoryId() {
    23         return this.categoryId;
    24     }
    25 
    26     public void setCategoryId(String categoryId) {
    27         this.categoryId = categoryId;
    28     }
    29 
    30     @Column(name = "category_name", length = 20)
    31     public String getCategoryName() {
    32         return this.categoryName;
    33     }
    34 
    35     public void setCategoryName(String categoryName) {
    36         this.categoryName = categoryName;
    37     }
    38 
    39     /*
    40      * 一对多关联关系
    41      * 级联关系：cascade=CascadeType.ALL
    42      * 延迟加载：fetch = FetchType.LAZY
    43      * 映射：mappedBy = "category"
    44      */
    45     @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY, mappedBy = "category")
    46     public Set<Goods> getGoodses() {
    47         return this.goodses;
    48     }
    49 
    50     public void setGoodses(Set<Goods> goodses) {
    51         this.goodses = goodses;
    52     }
    53 
    54 }

