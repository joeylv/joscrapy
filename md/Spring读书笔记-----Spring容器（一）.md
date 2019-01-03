Spring有两个核心接口：BeanFactory和ApplicationContext，其中ApplicationContext是BeanFactory的子接口。他们都可代表Spring容器，Spring容器是生成Bean实例的工厂，并且管理容器中的Bean。

Bean是Spring管理的基本单位，在基于Spring的Java
EE应用中，所有的组件都被当成Bean处理，包括数据源、Hibernate的SessionFactory、事务管理器等。在Spring中，Bean的是一个非常广义的概念，任何的Java对象、Java组件都被当成Bean处理。

而且应用中的所有组件，都处于Spring的管理下，都被Spring以Bean的方式管理，Spring负责创建Bean实例，并管理他们的生命周期。Bean在Spring容器中运行，无须感受Spring容器的存在，一样可以接受Spring的依赖注入，包括Bean属性的注入，协作者的注入、依赖关系的注入等。

Spring容器负责创建Bean实例，所以需要知道每个Bean的实现类，Java程序面向接口编程，无须关心Bean实例的实现类；但是Spring容器必须能够精确知道每个Bean实例的实现类，因此Spring配置文件必须精确配置Bean实例的实现类。

一、Spring容器

Spring容器最基本的接口就是BeanFactor。BeanFactory负责配置、创建、管理Bean，他有一个子接口：ApplicationContext，因此也称之为Spring上下文。Spring容器负责管理Bean与Bean之间的依赖关系。

BeanFactory接口包含以下几个基本方法：

Ø Boolean containBean(String name):判断Spring容器是否包含id为name的Bean实例。

Ø <T> getBean(Class<T> requiredTypr):获取Spring容器中属于requiredType类型的唯一的Bean实例。

Ø Object getBean(String name)：返回Sprin容器中id为name的Bean实例。

Ø <T> T getBean(String name,Class
requiredType)：返回容器中id为name,并且类型为requiredType的Bean

Ø Class <?> getType(String name)：返回容器中指定Bean实例的类型。

调用者只需使用getBean()方法即可获得指定Bean的引用，无须关心Bean的实例化过程。即Bean实例的创建过程完全透明。

在使用BeanFactory接口时，我们一般都是使用这个实现类：org.springframework.beans.factory.xml.XmlBeanFactory。然而ApplicationContext作为BeanFactory的子接口，使用它作为Spring容器会更加方便。它的实现类有：FileSystemXmlApplicationContext、ClassPathXmlApplicationContext、AnnotationConfigApplicationContext。

创建Spring容器实例时，必须提供Spring容器管理的Bean的详细配置信息。Spring的配置信息通常采用xml配置文件来设置，因此，创建BeanFactory实例时，应该提供XML配置文件作为参数。

XML配置文件通常使用Resource对象传入。Resource接口是Spring提供的资源访问接口，通过使用该接口，Spring能够以简单、透明的方式访问磁盘、类路径以及网络上的资源。

对于Java
EE应用而言，可在启动Web应用时自动加载ApplicationContext实例，接受Spring管理的Bean无须知道ApplicationContext的存在。一般使用如下方式实例化BeanFactory:

    
    
    1                 //搜索当前文件路径下的bean.xml文件创建Resource对象
    2         InputStreamSource isr = new FileSystemResource("bean.xml");
    3         //以Resource对象作为参数创建BeanFactory实例
    4         XmlBeanFactory factory = new XmlBeanFactory((Resource) isr);
    5 或
    6         ClassPathResource res = new ClassPathResource("bean.xml");
    7         //以Resource对象作为参数创建BeanFactory实例
    8         XmlBeanFactory factory = new XmlBeanFactory(res);
    
    
       但是如果应用里面有多个属性配置文件，则应该采用BeanFactory的子接口ApplicationContext来创建BeanFactory的实例。ApplicationContext通常使用如下两个实现类：

FileSystemXmlApplicationContext：以基于文件系统的XML配置文件创建ApplicationContext实例。

ClassPathXmlApplicationContext：以类加载路径下的XML配置文件创建的ApplicationContext实例。

如果需要同时加载多个XML配置文件，采用如下方式：

    
    
    1         //搜索CLASSPATH路径，以classpath路径下的bean.xml、service.xml文件创建applicationContext
    2         ApplicationContext ctx = new ClassPathXmlApplicationContext(new String[]{"bean.xml","service.xml"});
    3         
    4         //以指定路径下的bean.xml、service.xml文件创建applicationContext
    5         ApplicationContext ctx1 = new FileSystemXmlApplicationContext(new String[]{"bean.xml","service.xml"});

二、让Bean获取Spring容器

在前面简单的介绍了Spring容器。在Spring中我们可以使用Spring容器中getBean()方法来获取Spring容器中的Bean实例。在这样的访问模式下，程序中总是持有Spring容器的引用。但是在实际的应用中，Spring容器通常是采用声明式方式配置产生：记开发者只要在web.xml文件中配置一个Listener，该Listener将会负责初始化Spring容器。在这种情况下，容器中Bean处于容器管理下，无须主动访问容器，只需要接受容器的注入管理即可。同时Bean实例的依赖关系通常也是由容器冬天注入，无须Bean实例主动请求。

在这种情况下，Sprig容器中Bean通常不会需要访问容器中其他的Bean—采用依赖注入，让Spring把被依赖的Bean注入到依赖的Bean中即可。

实现BeanFactoryAware接口的Bean，拥有访问的BeanFactory容器的能力，实现BeanFactoryAware接口的Bean实例将会拥有对容器的访问能力。BeanFactoryAware接口仅有如下一个方法：

SetBeanFactory(BeanFactory
beanFactory)：该方法有一个参数beanFactory，该参数指向创建它的BeanFactory。

该方法将由Spring调动，当Spring调用该方法时会将Spring容器作为参数传入该方法。

    
    
     1 public class Chinese implements ApplicationContextAware{
     2 
     3     //将BeanFactory容器以成员变量保存
     4     private ApplicationContext ctx;
     5     /**
     6      * 实现ApplicationContextAware接口实现的方法
     7      */
     8     public void setApplicationContext(ApplicationContext cyx)
     9             throws BeansException {
    10         this.ctx = ctx;
    11     }
    12     
    13     //获取ApplicationContext的测试方法
    14     public ApplicationContext getContext(){
    15         return ctx;
    16     }
    17 
    18 }

上面的Chinese类实现了ApplicationContext接口，并实现了该接口提供的setApplicationContextAware()方法，这就使得该Bean实例可以直接访问到创建她的Spring容器。

将该Bean部署在Spring容器中。

测试类：

该程序先通过实例化的方法来获取ApplicationContext，然后通过chinese Bean来获得BeanFactory，并将两者进行比较。

    
    
     1 public class ChineseTest {
     2 
     3     public static void main(String[] args) {
     4         ApplicationContext ctx = new ClassPathXmlApplicationContext("bean.xml");
     5         Chinese c = ctx.getBean("chinese",Chinese.class);
     6         System.out.println(c.getContext());
     7         
     8         System.out.println(c.getContext()==ctx);
     9         
    10     }
    11 }

结果如下：

true

上面的代码虽然实现了ApplicationContextAware接口让Bean拥有了访问容器的能力，但是污染了代码，导致代码与Spring接口耦合在一起。所以，如果不是特别需要，一般不建议直接访问容器。

读李刚《轻量级Java EE企业应用实战》

