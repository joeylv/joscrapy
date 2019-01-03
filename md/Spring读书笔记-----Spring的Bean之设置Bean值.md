Java实例的属性值可以有很多种数据类型、基本类型值、字符串类型、java实例甚至其他的Bean实例、java集合、数组等。所以Spring允许通过如下几个元素为Bean实例的属性指定值：

value

ref

bean

list、set、map、props

一、value：设置普通属性值

<value.../>元素用于指定字符串类型、基本类型的属性值。Spring使用XML解析器来解析出这些数据，然后利用java.beans.PropertyEdior完成类型转换：从java.lang.String类型转换为所需的参数值类型。如果目标类型是基本数据类型，通常都是可以正确转换。

    
    
     1 public class ValueTest {
     2     //定义一个String型属性
     3     private String name;
     4     //定义一个int型属性
     5     private int age;
     6     
     7     public String getName() {
     8         return name;
     9     }
    10     public void setName(String name) {
    11         this.name = name;
    12     }
    13     
    14     public int getAge() {
    15         return age;
    16     }
    17     public void setAge(int age) {
    18         this.age = age;
    19     }
    20 }

上面实例只是演示了注入普通属性值。在Spring配置文件中使用<value.../>元素来为这两个属性指定属性值。

    
    
    1 <bean id="text" class="com.spring.service.impl.ValueTest">
    2         <property name="age" value="1" />
    3         <property name="name" value="chenssy" />
    4     </bean>

通过上面可以知道<value.../>元素主要用于传入字符串、基本类型的属性值。

二、ref:配置合作者

<value.../>主要是配置基本类型的属性值，但是如果我们需要为Bean设置属性值是另一个Bean实例时，这个时候需要使用<ref.../>元素。使用<ref.../>元素可以指定如下两个属性。

bean:引用不在同一份XML配置文件中的其他Bean实例的id属性值。

local：引用同一份XML配置文件中的其他Bean实例的id属性值。

    
    
    1 <bean id="steelAxe" class="com.spring.service.impl.SteelAce"></bean>
    2     <bean id="chinese" class="com.spring.service.impl.Chinese" >
    3         <property name="axe">
    4             <ref local="steelAxe"/>
    5         </property>
    6     </bean>

其实Spring提供了一种更加简洁的写法：

    
    
    1 <bean id="steelAxe" class="com.spring.service.impl.SteelAce"></bean>
    2     <bean id="chinese" class="com.spring.service.impl.Chinese" >
    3         <property name="axe" ref="steelAxe" />
    4     </bean>

通过property增加ref属性，一样可以将另一个Bean的引用设置成axe属性值。这样写的效果和使用<ref.../>属性一样，而且不需要区分是使用bean属性还是local属性，所以推荐这种写法。

2.1、使用自动装配注入合作者bean

Spring支持自动装配Bean与Bean之间的依赖关系，也就是说我们无需显示的指定依赖Bean。由BeanFactory检查XML配置文件内容，根据某种规则，为主调Bean注入依赖关系。

Spring的自动装配机制可以通过<bean.../>元素的default-
autowire属性指定，也可以通过<bean.../>元素的autowire属性指定。

自动装配可以减少配置文件的工作量，但是它降低了依赖关系的透明性和清晰性，所以一般来说在较大部署环境中不推荐使用，显示配置合作者能够得到更加清晰的依赖关系。Spring提供了如下几种规则来实现自动装配。

no:不适用自动装配。Bean依赖必须通过ref元素定义。

byName：根据属性名自动装配。BeanFactory查找容器中的全部Bean，找出其中id属性与属性同名的Bean来完成注入。如果没有找到匹配的Bean实例，则Spring不会进行任何注入。

byType：根据属性类型自动装配。BeanFactory查找容器中的全部Bean，如果正好有一个与依赖属性类型相同的Bean，就自动注入这个属性；但是如果有多个这样的Bean，就会抛出一个异常。如果没有匹配的Bean，则什么都不会发生，属性就不会被设置。如果需要无法自动装配时抛出异常，则设置dependency-
check=”objects”。

constructor:与不Type类似，区别是用于构造注入的参数。

Autodetect:BeanFactory根据Bean内部结构，决定使用constructor或者byType。如果找到一个默认的构造函数，则使用byTe。

byName规则

byTyep规则是指通过名字注入依赖关系，假如Bean
A的实现类里面包含setB()方法，而Spring的配置文件恰好包含一个id为b的Bean，则Spring容器就会将b实例注入Bean
A中。如果容器中没有名字匹配的Bean，Spring则不会做任何事情。

    
    
    1 <bean id="chinese" class="com.spring.service.impl.Chinese" autowire="byName" />
    2     <bean id="gundog" class="com.spring.service.impl.Gundog">
    3         <property name="name" value="wangwang" />
    4     </bean>

上面的配置文件指定了byName规则。则com.app.service.impl.Chinese类中提供如下的依赖注入方法：

    
    
    1 /*
    2      * 依赖关系必须的setter方法，因为需要通过名字自动装配
    3      * 所以setter方法必须提供set+Bean名，Bean名的首字母大写
    4      * @param dog 设置的dog值
    5      */
    6     public void setGundog(Dog dog){
    7         this.dog = dog;
    8     }

byType规则

byType规则是根据类型匹配注入依赖关系。假如A实例有setB(B
b)方法，而Spring配置文件中恰好有一个类型B的Bean实例，容器为A注入类型匹配的Bean实例。如果容器中存在多个B的实例，则会抛出异常，如果没有B实例，则不会发生任何事情。

    
    
    1 <bean id="chinese" class="com.spring.service.impl.Chinese" autowire="byType" />
    2     <bean id="gundog" class="com.spring.service.impl.Gundog">
    3         <property name="name" value="wangwang" />
    4     </bean>

针对上面的配置文件Chinese类有如下方法。

    
    
    1 /**
    2      * 依赖关系必须的setter方法
    3      * 因为使用按类型自动装配，setter方法的参数类型与容器的Bean的类型相同
    4      * 程序中的Gundog实现了Dog接口
    5      * @param dog传入的dog对象
    6      */
    7     public void setDog(Dog dog){
    8         this.dog = dog;
    9     }

当一个Bean即使用自动装配依赖，又使用ref显示依赖时，则显示指定的依赖就会覆盖自动装配。

在默认的情况下，Spring会自动搜索容器中的全部Bean，并对这些Bean进行判断，判断他们是否满足自动装配的条件，如果满足就会将该Bean注入目标Bean实例中。如果我们不想让Spring搜索容器中的全部Bean，也就是说，我们需要Spring来判断哪些Bean需要搜索，哪些Bean不需要搜索，这个时候就需要用到autowire-
candidate属性。通过为<bean.../>元素设置autowire-
candidate=”false”，即可将该Bean限制在自动装配范围之外，容器在查找自动装配对象时将不考虑该Bean。

三、Bean：注入嵌套Bean

如果某个Bean所依赖的Bean不想被Spring容器直接访问，则可以使用嵌套Bean。<bean.../>元素用来定义嵌套Bean，嵌套Bean只对嵌套它的外部Bean有效，Spring容器无法直接访问嵌套Bean，因此在定义嵌套Bean时是无需指定id属性的。

    
    
    1 <bean id="chinese" class="com.spring.service.impl.Chinese" autowire="byName">
    2         <property name="axe">
    3             <!-- 
    4                 属性值为嵌套Bean，嵌套Bean不能由Spring容器直接访问，
    5                 所以嵌套Bean是不需要id属性
    6              -->
    7             <bean class="com.spring.service.impl.SteelAce" />
    8         </property>
    9     </bean>

采用上面的配置可以保证嵌套Bean不能被容器访问，因此不用担心其他程序修改嵌套bean。但是嵌套Bean限制了Bean的访问，提高了程序的内聚性。

四、list、set、map、props

<value.../>元素是注入基本数据类型和String类型的，但是如果某个Bean的属性是集合呢？这个时候我们就需要使用集合元素，<list.../>、<set.../>、<map.../>和<props.../>元素分别用来设置类型list、set、map和Properties的集合属性值。

先看下面java类：

    
    
     1 public class Chinese implements Person{
     2 
     3     //下面是一系列的集合属性
     4     private List<String> schools;
     5     private Map scores;
     6     private Map<String, Axe> phaseAxes;
     7     private Properties health;
     8     private Set axe;
     9     private String[] books;
    10     
    11     public List<String> getSchools() {
    12         return schools;
    13     }
    14 
    15     public void setSchools(List<String> schools) {
    16         this.schools = schools;
    17     }
    18 
    19     public Map getScores() {
    20         return scores;
    21     }
    22 
    23     public void setScores(Map scores) {
    24         this.scores = scores;
    25     }
    26 
    27     public Map<String, String> getPhaseAxes() {
    28         return phaseAxes;
    29     }
    30 
    31     public void setPhaseAxes(Map<String, String> phaseAxes) {
    32         this.phaseAxes = phaseAxes;
    33     }
    34 
    35     public Properties getHealth() {
    36         return health;
    37     }
    38 
    39     public void setHealth(Properties health) {
    40         this.health = health;
    41     }
    42 
    43     public Set getAxe() {
    44         return axe;
    45     }
    46 
    47     public void setAxe(Set axe) {
    48         this.axe = axe;
    49     }
    50 
    51     public String[] getBooks() {
    52         return books;
    53     }
    54 
    55     public void setBooks(String[] books) {
    56         this.books = books;
    57     }
    58 
    59     public void useAxe() {
    60         
    61     }
    62 
    63 }

上面的java代码中有数组、list、set、，map、Properties。下面是针对上面的配置文件。

    
    
     1 <?xml version="1.0" encoding="UTF-8"?>
     2 <beans xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     3     xmlns="http://www.springframework.org/schema/beans"
     4     xsi:schemaLocation="http://www.springframework.org/schema/beans
     5     http://www.springframework.org/schema/beans/spring-beans-3.0.xsd">
     6     <!-- 定义一个普通的Axe Bean -->
     7     <bean id="steelAxe" class="com.spring.service.impl.SteelAxe" />
     8     <bean id="stoneAxe" class="com.spring.service.impl.StoneAxe" />
     9     
    10     <!--定义Chinese Bean -->
    11     <bean id="chinese" class="com.spring.service.impl.Chinese">
    12         <property name="schools">
    13             <list>
    14                 <value>小学</value>
    15                 <value>中学</value>
    16                 <value>大学</value>
    17             </list>
    18         </property>
    19         
    20         <property name="scores">
    21             <map>
    22                 <entry key="语文" value="88" />
    23                 <entry key="数学" value="87" />
    24                 <entry key="外语" value="88" />
    25             </map>
    26         </property>
    27         
    28         <property name="phaseAxes">
    29             <map>
    30                 <entry key="原始社会" value-ref="stoneAxe" />
    31                 <entry key="农业社会" value-ref="steelAxe" />
    32             </map>
    33         </property>
    34         
    35         <property name="health">
    36             <props>
    37                 <prop key="血压">正常</prop>
    38                 <prop key="身高">175</prop>
    39             </props>
    40         </property>
    41         
    42         <property name="axe">
    43             <set>
    44                 <value>普通字符串</value>
    45                 <bean class="com.spring.service.impl.SteelAxe"></bean>
    46                 <ref local="stoneAxe"/>
    47             </set>
    48         </property>
    49         
    50         <property name="books">
    51             <list>
    52                 <value>java 编程思想</value>
    53                 <value>思考致富</value>
    54                 <value>将才</value>
    55             </list>
    56         </property>
    57     </bean>
    58 </beans>

从上面的配置文件中可以看出，Spring对list属性和数组属性的处理是一样的。

当我们使用<list.../>、<set.../>、<map.../>等元素配置集合属性时，我们还需要手动配置集合元素。由于集合元素又可以是基本类型值、引用容器中的其他Bean、嵌套Bean和集合属性等。所以这些元素又可以接受如下子元素：

value:指定集合元素是基本数据类型或者字符类型值。

ref:指定集合元素师容器中另一个Bean实例。

bean:指定集合元素是一个嵌套Bean。

list、set、map、props:指定集合元素值又是集合。

