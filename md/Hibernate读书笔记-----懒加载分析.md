懒加载是指程序推迟访问数据库，这样做可以保证有时候不必要的访问数据库，因为访问一次数据库是比较耗时的。  

一、load方法的懒加载

先看如下代码段

    
    
     1 public class UserManager {
     2 
     3     public static void main(String[] args) {
     4         Users user = new Users();
     5         user.setBirthday(new Date());
     6         
     7         Name name = new Name();
     8         name.setFirstName("guo");
     9         name.setLastName("zhao");
    10         
    11         user.setName(name);
    12         addUser(user);
    13         
    14         Users users = getUser(user.getId());
    15         System.out.println(users.getName());
    16         
    17     }
    18     
    19     
    20     static Users getUser(int id){
    21         Session session = HibernateUtil.getSession();
    22         try {
    23             Users users = (Users) session.load(Users.class, id);
    24             return users;
    25         } finally{
    26             session.close();
    27         }
    28     }
    29     
    30     static void addUser(Users users){
    31         Session session = null;
    32         Transaction tx = null;
    33         
    34         try {
    35             session = HibernateUtil.getSession();
    36             tx = session.beginTransaction();
    37 
    38             session.save(users);
    39             tx.commit();
    40         } catch (HibernateException e) {
    41             if (tx!=null) {
    42                 tx.rollback();
    43             }
    44             throw e;
    45         }finally{
    46             if(session!=null){
    47                 session.close();
    48             }
    49         }
    50     }
    51 }

  
上面代码是先增加一个用户、然后再查询这个用户的name组合属性。运行上面的时候，该程序会抛出这样一个异常：

Exception in thread "main" org.hibernate.LazyInitializationException: could
not initialize proxy - no Session这就是懒加载不能初始化异常。其原因就在于no
session。在前面个持久化对象中已经说明：使用load方法时，该方法将具有延迟加载的功能，load方法并不会立即去访问数据库，它会返回一个代理对象，只有当你真正去访问这个对象的时候，它才会去访问数据库。

![](http://my.csdn.net/uploads/201207/10/1341888773_2703.jpg)
通过上面的图，我们看出，hibernate根本就没有select语句，也就是说hibernate没有去访问数据库，所以这个时候你去访问它肯定是没有的。但为什么没有抛出空指针异常？没有抛出空指针异常，也就是说明User对象是存在的，那它是什么呢？通过输出user.getClass()可以看出是这样一个东西：

class com.hibernate.domain.Users_$$_javassist_5。

这个user就是load返回的代理对象。但是这个对象并不是我们所要的。我们所要的是一个User实例对象。

那么怎么解决这个问题呢？

第一种方法：在关闭session之前访问该对象

    
    
     1     static Users getUser(int id){
     2         Session session = HibernateUtil.getSession();
     3         try {
     4             Users users = (Users) session.load(Users.class, id);
     5             users.getName();
     6             return users;
     7         } finally{
     8             session.close();
     9         }
    10     }

不过这句话看起来会很奇怪。我们通常会采用如下的方式

    
    
     1     static Users getUser(int id){
     2         Session session = HibernateUtil.getSession();
     3         try {
     4             Users users = (Users) session.load(Users.class, id);
     5             Hibernate.initialize(users);
     6             return users;
     7         } finally{
     8             session.close();
     9         }
    10     }

利用hibernate的initialize()方法将这个代理对象给初始化。

注：在使用代理对象的getId()方法和getClass()方法的时候，并不会抛出不能初始化异常，因为这两个属性并不用查询数据库。

二、在缺省的情况下，hibernate对于关联关系会采用懒加载的方式。也就是说1-1、1-N、N-1、N-N都存在懒加载的问题。

2.1、one-to-one懒加载

一对一的懒加载并不常用，因为懒加载的目的是为了减少与数据库的交互，从而提高执行效率，而在一对一关系中，主表中的每一条数据只对应从表的一条数据库，就算都查询也不会增加多少交互的成本，而且主表不能有contrained=true，所以主表是不能懒加载的。但是从表可以有。

实现此种懒加载必须在从对象这边同时满足三个条件：  
1、lazy！=false（lazy的属性有三个选项分别为：no-proxy、false和proxy）  
2、Constrained = true ；  
3、fetch=select。  
注：当fetch设置为[join](http://www.linuxso.com/command/join.html)时，懒加载就会失效。因为fetch的作用是抓取方式，他有两个值分别问select和join，默认值为select。即在设为join时，他会直接将从表信息以join方式查询到而不是再次使用select查询，这样导致了懒加载的失效。

2.2、one-to-many懒加载

与one-to-one关联不同，对one-to-
many而言，主表的每一条属性都会对应从表的多条数据，这个时候懒加载就显得非常有效了。比如一个部门里面有多个员工，如果没有懒加载，每查询这个部门的时候都会查询出多个员工，这会大大增加与数据库交互的成本。所以Hbernate默认的是加入懒加载的。这就是查询集合属性的时候返回的是一个PersistentIndexed*类型对象的原因。该对象其实就是一个代理对象。当然，可以在映射文件中通过将lazy属性设为假来禁用。

Hibernate默认对one-to-many就是使用的懒加载，但用户也可以取消懒加载操作：  
一：设置lazy=”false”;  
二：设置fetch=”join”.  
实现此种懒加载必须在从对象这边同时满足两个个条件：  
1、lazy！=false（lazy的属性有三个选项分别为：no-proxy、false和proxy）  
2、fetch=select。

2.3、mang-to-one懒加载

此关联关系的懒加载和one-to-
one的懒加载一样都是可要可不要的，因为对执行效率的提高都不是非常明显。虽然多对一与一对一关系方式相同，但是在Hibernate中多对一时，默认是进行懒加载的。另外有一点需要注意的是懒加载并不会区分集合属性里面是否有值，即使是没有值，他依然会使用懒加载。

实现此种懒加载必须在从对象这边同时满足两个个条件：  
1、lazy！=false（lazy的属性有三个选项分别为：no-proxy、false和proxy）  
2、fetch=select

2.4、many-to-many懒加载

此关联关系的懒加载和one-to-many的懒加载一样对程序的执行效率的提高都是非常明显的。  
实现此种懒加载必须在从对象这边同时满足两个个条件：  
1、lazy！=false（lazy的属性有三个选项分别为：no-proxy、false和proxy）  
2、fetch=select

能够懒加载的对象都是被改过的代理对象，当相应的对象没有关闭时，访问这些懒加载对象的属性（getId和getClass除外）hibernate会初始化这些代理，或用hibernate.initalize(proxy)来初始化代理对象；当关闭session后在访问懒加载的对象就会出现异常

