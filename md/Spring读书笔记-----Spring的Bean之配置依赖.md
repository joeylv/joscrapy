前一篇博客介绍了Spring中的Bean的基本概念和作用域（[Spring读书笔记-----
Spring的Bean之Bean的基本概念](http://www.cnblogs.com/chenssy/archive/2012/11/25/2787710.html)）,现在介绍Spring
Bean的基本配置。

从开始我们知道Java应用中各组件的相互调用的实质可以归纳为依赖关系。根据注入方式的不同，Bean的依赖注入可以分为两种形式：

1、 属性：通过<property …/>元素配置，对应设置注入。

2、 构造器参数：通过<constructor-arg…/>元素配置，对应构造注入。

不管是属性，还是构造器参数，都视为Bean的依赖，接受Spring容器管理，依赖关系的值要么是一个确定的值，要么是Spring容器中的其他Bean的引用。

在一般情况下，我是不应该在配置文件中管理普通属性的引用，通常只是用配置文件管理容器中的Bean实例的依赖关系。

Spring在实例化容器时，会校验BeanFactory中每一个Bean的配置。这些校验包括：

Bean引用的依赖Bean是否指向一个合法的Bean。

Bean的普通属性值是否获得一个有效值。

对于singleton作用域的Bean，如果没有强行取消其预初始化的行为，系统会在创建Spring容器时预初始化所用singleton
Bean，与此同时，该Bean所依赖的Bean也被一起实例化。

BeanFactory与ApplicationContext实例化容器中的Bean的时机也是不同的：BeanFactory等到程序需要Bean实例时才创建Bean，而ApplicationContext是在创建ApplicationContext实例时，会预初始化容器中的全部Bean。同时在创建BeanFactory时不会立即创建Bean实例，所以有可能程序可以正确地创建BeanFactory实例，但是当请求Bean实例时依然抛出一个异常：创建Bean实例或注入它的依赖关系时出现错误。所以当配置错误的延迟出现，会给系统带来一些不安全的因素。而ApplicationContext则是默认预初始化所有singleton作用域的Bean，所以ApplicationContext实例化过程比BeanFactory实例化过程的时间和内存开销大，但是一旦创建成功，应用后面的响应速度会非常快，同时可以检验出配置错误，故一般都是推荐使用ApplicationContext作为Spring容器。

其实我们可以指定lazy-
int=”true”来强制取消singleton作用域的Bean的预初始。这样该Bean就不会随着ApplicationContext启动而预实例化了。

Spring可以为任何java对象注入任何类型的属性，只要改java对象为该属性提供了对应的setter方法即可。

    
    
    1     <bean id="person" class="lee.Person">
    2         <!-- Property配置需要依赖注入的属性 -->
    3         <property name="name" value="chenming" />
    4         <property name="age" value="22" />
    5     </bean>

Spring会为<bean…/>元素创建一个java对象，一个这样的java对象对应一个Bean实例，对于如上代码，Spring会采用如下形式来创建Java实例。

    
    
    1     //获取lee.Person类的Class对象
    2     Class  personClass = Class.forName("lee.Person");
    3     //创建lee.Person类的默认实例
    4     Object personBean = personBean.newInStance();

创建该实例后，Spring就会遍历该<bean../>元素的所有<property…/>子元素。<bean…/>元素每包含一个<property…/>子元素，Spring就会为该Bean实例调用一次setter方法。类似于下面程序：

    
    
    1     //获取name属性的setter方法
    2     String setName = "set"+"Name";
    3     //获取lee.Person类里面的Set()Name方法
    4     java.lang.reflect.Method setMethod = personClass.getMethod(setName, aVal.getClass());
    5     //调用Bean实例的SetName()方法
    6     setMethod.invoke(personBean, aVal);

  
对于使用<constructor-
arg…/>元素来指定构造器注入，Spring不会采用默认的构造器来创建Bean实例，而是使用特定的构造器来创建该Bean实例。

    
    
    1     <bean id="person" class="lee.Person">
    2         <constructor-arg index="0" value="aVal" />
    3         <constructor-arg index="1" value="bVal" />
    4     </bean>

针对上面的代码，Spring会采用类似如下的代码来创建Bean实例：

    
    
    1     //获取lee.Person类的class对象
    2     Class  personClass = Class.forName("lee.Person");
    3     //获取第一个参数是aVal类型，第二个参数是bVal类型的构造器
    4     Constructor personCtr = personClass.getConstructor(aVal.getClass(),bVal.getClass());
    5     //以指定构造器创建Bean实例
    6     Object bean = personCtr.newInstance(aVal,bVal);

  

  
上面的程序只是一个实例，实际上Spring还需要根据<property…/>元素、<contructor-
arg../>元素所使用value属性，ref属性等来判断需要注入的到底是什么数据类型，并要对这些值进行合适的类型转换，所以Spring的实际处理过程会更加复杂。

