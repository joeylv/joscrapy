## 前言

开心一刻

朋友喜欢去按摩，第一次推门进来的是一个学生美眉，感觉还不错；后来经常去，有时是护士，有时是空姐，有时候是教师。昨天晚上推门进去的是一个女警察，长得贼好看，身材也很好，朋友嗷的一声就扑上去了。然后他就被抓起来了，罪名是：嫖娼、袭警、强奸未遂。

路漫漫其修远兮，吾将上下而求索！

github：[https://github.com/youzhibing](https://github.com/youzhibing)

码云(gitee)：[https://gitee.com/youzhibing](https://gitee.com/youzhibing)

## 前情回顾

[springboot2.3源码篇之SpringApplication的构造方法](https://www.cnblogs.com/youzhibing/p/9550343.html)

主要做了两件事：

1、推测应用类型

根据类路径下是否存在指定类型的类来断定应用类型；

应用类型有三种：NONE、SERVLET、REACTIVE，NONO表示普通的java应用，SERVLET表示基于servlet
的web工程，REACTIVE表示 reactive web application（还没去了解，囧...）

2、获取ApplicationContextInitializer、ApplicationListener实例

查找类路径下全部的META-
INF/spring.factories的URL（spring.factories文件的路径），并加载所有spring.factories中的内容（包括各种Initializer、ApplicationListener、AutoConfigure、Failure
analyzers等）到SpringFactoriesLoader的cache中；

然后从缓存中获取ApplicationContextInitializer、ApplicationListener类型的类并进行实例化，然后将得到的实例化集合分别赋值给SpringApplication的initializers和listeners

[springboot2.3源码篇之run方法（一）：SpringApplicationRunListener](https://www.cnblogs.com/youzhibing/p/9603119.html)

主要做了两件事：

1、准备好运行时监听器：EventPublishingRunListener，并过滤出于与ApplicationStartingEvent匹配的监听器

2、广播ApplicationStartingEvent事件，触发对应的事件监听器

LoggingApplicationListener

检测正在使用的日志系统

BackgroundPreinitializer

另起一个后台线程执行耗时的初始化

[springboot2.3源码篇之run方法（二）：prepareEnvironment方法](https://www.cnblogs.com/youzhibing/p/9622441.html)

1、获取或创建环境

根据SpringApplication构造方法中推断出的应用类型创建对应的环境，一般而言是web环境：StandardServletEnvironment

2、广播ApplicationEnvironmentPreparedEvent事件，触发相应的监听器

ConfigFileApplicationListener

添加名叫random的RandomValuePropertySource到environment

添加名叫applicationConfig:[classpath:/application.yml]的OriginTrackedMapPropertySource到environment

LoggingApplicationListener

初始化日志系统

3、加载外部化配置的资源到environment

包括命令行参数、servletConfigInitParams、servletContextInitParams、systemProperties、sytemEnvironment、random、application.yml(.yaml/.xml/.properties)等

[springboot2.3源码篇之run方法（三）：createApplicationContext方法](https://www.cnblogs.com/youzhibing/p/9686969.html)

1、实例化应用上下文

应用类型有三种，对应的上下文也有三种，NONE -> AnnotationConfigApplicationContext，SERVLET ->
AnnotationConfigServletWebServerApplicationContext，REACTIVE ->
AnnotationConfigReactiveWebServerApplicationContext；一般而言，创建的是AnnotationConfigServletWebServerApplicationContext。

2、实例化AnnotatedBeanDefinitionReader、ClassPathBeanDefinitionScanner和DefaultListableBeanFactory

AnnotatedBeanDefinitionReader是注解bean定义读取器，用于编程式注解bean的注册；ClassPathBeanDefinitionScanner是类路径bean定义扫描器，用于检测类路径上的bean候选者。

AnnotatedBeanDefinitionReade用来加载class类型的配置，在它初始化的时候，会预先注册一些BeanPostProcessor和BeanFactoryPostProcessor，这些处理器会在接下来的spring初始化流程中被调用。ClassPathBeanDefinitionScanner是一个扫描指定类路径中注解Bean定义的扫描器，在它初始化的时候，会初始化一些需要被扫描的注解。

DefaultListableBeanFactory，也就是我们所说的beanFactory，用来注册所有bean定义（bean
definitions），也可以用来作为单例bean工厂。

[springboot2.3源码篇之run方法（四）：prepareContext方法](https://www.cnblogs.com/youzhibing/p/9697825.html)

1、将SpringApplication中的部分属性应用到上下文中

SpringApplication中的environment、initializers、listeners应用到spring上下文中

2、广播ApplicationPreparedEvent事件，触发对应的事件监听器

向context的beanFactoryPostProcessors中注册了一个PropertySourceOrderingPostProcessor实例  
向beanFactory中注册了一个名叫springBootLoggingSystem的单例bean，也就是我们的日志系统bean

3、加载资源

支持4种方式：Class、Resource、Package和CharSequence。

Class：注解形式的Bean定义；AnnotatedBeanDefinitionReader负责处理。

Resource：一般而言指的是xml
bean配置文件，也就是我们在spring中常用的xml配置。说的简单点就是：将xml的bean定义封装成BeanDefinition并注册到beanFactory的BeanDefinitionMap中；XmlBeanDefinitionReader负责处理。

Package：以扫包的方式扫描bean定义； ClassPathBeanDefinitionScanner负责处理。

CharSequence：以先后顺序进行匹配Class、Resource或Package进行加载，谁匹配上了就用谁的处理方式处理。

springboot鼓励用java类实现java bean定义，所以springboot应用中，我们一般只需要关注Class方式、Package方式即可。

context中主要是三个属性增加了内容：beanFactory、beanFactoryPostProcessors和applicationListeners

## 三个事件

ApplicationStartingEvent

在监听器注册完、SpringApplication构造完后，以及其他的任何处理之前被广播，触发对应的事件监听器

ApplicationEnvironmentPreparedEvent

environment创建后，context创建之前被广播，触发对应的事件监听器  
ApplicationPreparedEvent

bean定义加载后，上下文refresh之前被广播，触发对应的事件监听器

后续还会涉及到ApplicationReadyEvent、ApplicationFailedEvent事件，后续再详解

关于事件机制，可到[此处](https://www.cnblogs.com/youzhibing/p/9593788.html)查看更多详情

## 三个核心

[SpringApplication](https://docs.spring.io/spring-
boot/docs/2.1.0.RELEASE/reference/htmlsingle/#boot-features)

springboot的特性之一，内容如下

23\. SpringApplication  
23.1. Startup Failure  
23.2. Customizing the Banner  
23.3. Customizing SpringApplication  
23.4. Fluent Builder API  
23.5. Application Events and Listeners  
23.6. Web Environment  
23.7. Accessing Application Arguments  
23.8. Using the ApplicationRunner or CommandLineRunner  
23.9. Application Exit  
23.10. Admin Features

也是springboot中比较重要的特性之一，用于从java
main方法引导和启动Spring应用程序。其实给我印象最深的还是从spring.factories加载一系列的类，包括Initializer、ApplicationListener、AutoConfigure、Failure
analyzers等等，springboot的自动配置，从此时已经开始了，一系列的AutoConfigure都是从spring.factories获取的。  
environment：StandardServletEnvironment

表示当前应用程序所处的环境，主要包括两方面：profiles和properties；例如我们经常说的本地、运测、预发布、生产环境，就可以通过environment进行配置，以及是否是web环境。

一般而言，我们的环境是StandardServletEnvironment，标准的servlet环境，也就是我们经常说的web环境

ApplicationContext：AnnotationConfigServletWebServerApplicationContext

应用上下文，用于为应用程序提供配置的中央接口，提供如下内容：

1、访问应用程序组件的Bean工厂方法

2、加载文件资源的能力

3、发布事件到已注册的事件监听器的能力

4、解析消息，支持国际化的能力

等等一系列的功能

AnnotationConfigServletWebServerApplicationContext是springboot对spring应用上下文的拓展，引入了一些springboot的内容。

