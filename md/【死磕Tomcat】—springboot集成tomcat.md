  * 1 SPI
  * 2 @ Spring Boot for Tomcat
  * 3 tomcat 外部配置
  * 4 总结

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79328151>

spring boot 支持目前主流的 servlet 容器，包括 tomcat、jetty、undertow，可以在我们的项目中方便地集成这些
servlet 容器，减少了开发、运维的工作量。而传统的应用开发，需要经过繁锁的操作步骤：安装 tomcat –> 修改 tomcat 配置 –> 部署
war 包 –> 启动 tomcat –> 运维……，这个工作量不小，尤其是集群部署、应用迁移的时候。而采用 spring boot
之后，一切变得如此简单，打包 –> java -jar –> 运维，只需要一个 jar 包便可以随意部署安装。这篇文章，将对 spring boot 集成
tomcat 的源码进行分析，探索其内部的原理

## SPI

在分析源码前，我们先来了解下 spring 的 SPI 机制。我们知道，jdk 为了方便应用程序进行扩展，提供了默认的 SPI
实现（ServiceLoader），dubbo 也有自己的 SPI。spring 也是如此，他为我们提供了
`SpringFactoriesLoader`，允许开发人员通过 `META-INF/spring.factories`
文件进行扩展，下面举一个例子方便理解

假如，我想要往 spring 容器中添加一个 `ApplicationContextInitializer` 做一些初始化工作，我们可以借助 spring
提供的这个 SPI 功能完成这个需求。

首先，在项目中创建 `META-INF/spring.factories` 文件，文件内容如下所示：

    
    
    org.springframework.context.ApplicationContextInitializer=\
    net.dwade.spring.boot.demo.DubboApplicationContextInitializer
    

我们再写个 test case，便可以通过 SPI 的方式获取我们定义的
`ApplicationContextInitializer`。看似很简单的一个功能，但是 spring boot 正是利用这个强大的扩展点，在
spring framework 的基础上为我们集成了常用的开源框架

    
    
    @Test
    public void testSpringSpi() {
        List<ApplicationListener> listeners = SpringFactoriesLoader.loadFactories( ApplicationListener.class,
                ClassUtils.getDefaultClassLoader() );
        System.out.println( listeners );
    }
    

我们再来看看这个 `SpringFactoriesLoader`，关键代码如下所示，它通过读取 `META-INF/spring.factories`
文件，并且查找方法参数指定的 class，然后创建对应的实例对象，并且返回。此外，还支持排序，可以使用以下几种方式进行排序

  * org.springframework.core.Ordered：实现该接口
  * org.springframework.core.annotation.Order：注解
  * javax.annotation.Priority：注解

    
    
    public static <T> List<T> loadFactories(Class<T> factoryClass, ClassLoader classLoader) {
        List<String> factoryNames = loadFactoryNames(factoryClass, classLoaderToUse);
        List<T> result = new ArrayList<T>(factoryNames.size());
        for (String factoryName : factoryNames) {
            result.add(instantiateFactory(factoryName, factoryClass, classLoaderToUse));
        }
        AnnotationAwareOrderComparator.sort(result);
        return result;
    }
    

接下来，我们来分析下 spring boot 是如何利用 SPI 机制集成 tomcat

## @ Spring Boot for Tomcat

在分析 tomcat 集成的源码之前，我们先来了解下 EmbeddedServletContainer

> EmbeddedServletContainer：  
>  spring 用 `EmbeddedServletContainer` 封装了内嵌的 servlet 容器，提供了`start`、`stop`
等接口用于控制容器的生命周期，并且 spring 内置了 tomcat、jetty、undertow 容器的实现，类图所下所示

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180321125111921.png)

我们再来看看 spring boot 中最常用的 `SpringBootApplication` 注解，原来是多个注解的综合体，而这个
`EnableAutoConfiguration` 便是 spring boot 用做自动化配置的注解

    
    
    @SpringBootConfiguration
    @EnableAutoConfiguration
    @ComponentScan(excludeFilters = {
            @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
            @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
    public @interface SpringBootApplication {
        // code......
    }
    

我们在 `spring-boot-autoconfigure` 模块可以看到大量的 SPI 配置，部分如下所示

    
    
    # Auto Configure
    org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
    org.springframework.boot.autoconfigure.web.EmbeddedServletContainerAutoConfiguration,\
    org.springframework.boot.autoconfigure.web.ErrorMvcAutoConfiguration
    

原来 `EnableAutoConfiguration` 注解引入了
`EmbeddedServletContainerAutoConfiguration`，而这个便是内嵌 servlet
容器的配置类，tomcat、jetty、undertow 都在这个类上面，通过 `@ConditionalOnClass` 注解加载不同的 servlet
容器。但是，这个类仅仅是注册了 `TomcatEmbeddedServletContainerFactory`
，不足以帮助我们解除所有的困惑。不要急，我们先来看看 `TomcatEmbeddedServletContainerFactory` 的类图。

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180321002235248.png)

由上面的类图可知，它实现了以下接口：

  * EmbeddedServletContainerFactory：它是一个工厂模式，用于创建 `EmbeddedServletContainer`，即用于创建一个内嵌的 Servlet 容器，这个接口里面只有一个 `getEmbeddedServletContainer` 方法
  * ConfigurableEmbeddedServletContainer：用于配置 `EmbeddedServletContainer`，比如说端口、上下文路径等

分析了上面两个接口，原来创建 servlet 容器的工作是由 `EmbeddedServletContainerFactory` 完成的，看下
`getEmbeddedServletContainer` 方法的调用栈。在 `EmbeddedWebApplicationContext` 中重写了
`GenericWebApplicationContext#onRefresh()` 方法，并且调用
`getEmbeddedServletContainer` 方法创建 servlet 容器，我们接下来分析这个创建过程。

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180321104100735)

关键代码如下（省略异常处理）：

    
    
    EmbeddedWebApplicationContext.java
    
    @Override
    protected void onRefresh() {
        super.onRefresh();
        createEmbeddedServletContainer();
    }
    
    private void createEmbeddedServletContainer() {
        EmbeddedServletContainer localContainer = this.embeddedServletContainer;
        ServletContext localServletContext = getServletContext();
        if (localContainer == null && localServletContext == null) {
            // 从容器中获取bean，如果使用tomcat则返回TomcatEmbeddedServletContainerFactory
            EmbeddedServletContainerFactory containerFactory = getEmbeddedServletContainerFactory();
            this.embeddedServletContainer = containerFactory.getEmbeddedServletContainer(getSelfInitializer());
        }
        else if (localServletContext != null) {
            getSelfInitializer().onStartup(localServletContext);
        }
        initPropertySources();
    }
    

我们先画出主要的流程图([查看原图](http://img-blog.csdn.net/2018032111572262))

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/2018032111572262.png)

由上图可知，`EmbeddedWebApplicationContext` 在执行 `onRefresh` 方法的时候，首先调用父类的
`onRefresh`，然后从容器中获取 `EmbeddedServletContainerFactory` 的实现类。由于我们在 classpath
下面可以获取 tomcat 的 jar 包，因此 `EmbeddedServletContainerAutoConfiguration` 会在 spring
容器中注册 `TomcatEmbeddedServletContainerFactory` 这个 bean。然后，由它创建
`TomcatEmbeddedServletContainer`，我们来看看具体的创建过程，代码如下所示：

    
    
    TomcatEmbeddedServletContainerFactory.java
    
    @Override
    public EmbeddedServletContainer getEmbeddedServletContainer(
            ServletContextInitializer... initializers) {
        Tomcat tomcat = new Tomcat();   // 实例化 apache Tomcat
        File baseDir = (this.baseDirectory != null ? this.baseDirectory
                : createTempDir("tomcat"));
        tomcat.setBaseDir(baseDir.getAbsolutePath());
    
        // 创建 Connector 组件，默认使用org.apache.coyote.http11.Http11NioProtocol
        Connector connector = new Connector(this.protocol);
        tomcat.getService().addConnector(connector);
    
        // 支持对 Connector 进行自定义设置，比如设置线程池、最大连接数等
        customizeConnector(connector);
        tomcat.setConnector(connector);
        tomcat.getHost().setAutoDeploy(false);
    
        configureEngine(tomcat.getEngine());
        for (Connector additionalConnector : this.additionalTomcatConnectors) {
            tomcat.getService().addConnector(additionalConnector);
        }
    
        prepareContext(tomcat.getHost(), initializers);
        return getTomcatEmbeddedServletContainer(tomcat);
    }
    

首先是实例化 `Tomcat` 对象，然后创建 `Connector` 组件，并且对 `Connector` 进行相关的参数设置，同时也允许我们通过
`TomcatConnectorCustomizer` 接口进行自定义的设置。OK，创建了 `Tomcat` 实例之后，需要创建
`TomcatEmbeddedServletContainer`，它依赖 `Tomcat` 对象，在构造方法中便会启动 Tomcat
容器，从而完成各个组件的启动流程

    
    
    public TomcatEmbeddedServletContainer(Tomcat tomcat, boolean autoStart) {
        Assert.notNull(tomcat, "Tomcat Server must not be null");
        this.tomcat = tomcat;
        this.autoStart = autoStart;
        initialize();
    }
    
    private void initialize() throws EmbeddedServletContainerException {
        synchronized (this.monitor) {
            addInstanceIdToEngineName();
            // Remove service connectors to that protocol binding doesn"t happen yet
            removeServiceConnectors();
    
            // Start the server to trigger initialization listeners
            this.tomcat.start();
    
            // We can re-throw failure exception directly in the main thread
            rethrowDeferredStartupExceptions();
    
            Context context = findContext();
            ContextBindings.bindClassLoader(context, getNamingToken(context),
                        getClass().getClassLoader());
            // Unlike Jetty, all Tomcat threads are daemon threads. We create a
            // blocking non-daemon to stop immediate shutdown
            startDaemonAwaitThread();
        }
    }
    

`Tomcat` 实例的 `start` 方法如下所示，这便回到了 tomcat 的启动流程了，这里不再哆嗦了，感兴趣的童鞋可以查看我的博文

    
    
    Tomcat.java
    
    public void start() throws LifecycleException {
        getServer();
        getConnector();
        server.start();
    }
    

  * [Tomcat8源码分析系列-启动分析(一) Lifecycle](http://blog.csdn.net/dwade_mia/article/details/79051417)
  * [Tomcat8源码分析系列-启动分析(二) Catalina初始化](http://blog.csdn.net/dwade_mia/article/details/79051444)
  * [Tomcat8源码分析系列-启动分析(三) Catalina启动](http://blog.csdn.net/dwade_mia/article/details/79244157)
  * [Tomcat8源码分析系列-启动分析(四) webapp](http://blog.csdn.net/dwade_mia/article/details/79328151)

## tomcat 外部配置

前面我们分析了 spring boot 与 tomcat 的集成，我们再来看看 spring boot 是如何为 serlvet
容器设置参数的。首先，来看一下常用的配置，内嵌容器的配置以 `server` 开头，下面的示例采用 yml 格式，properties
文件只是格式略有不同而已

application.yml

    
    
    server:
      port: 8080
      context-path: /driver
      tomcat:
        max-threads: 500
        max-connections: 20000 # 最大允许的连接数，nio默认10000
        accept-count: 100   # 达到 max-connections 之后，允许等待的连接数量
    

spring boot 关于内嵌 servlet 容器主要依赖 `ServerProperties` 完成，下面的代码列举了常用的配置，注意：代码里面的
`Tomcat`、`Jetty` 是内部类，用于进行参数配置的，并不是对应的 servlet 容器。比如我们要设置 tomcat 的参数，使用
`server.tomcat` 前缀即可，jetty 对应就是 `server.jetty`

    
    
    @ConfigurationProperties(prefix = "server", ignoreUnknownFields = true)
    public class ServerProperties
            implements EmbeddedServletContainerCustomizer, EnvironmentAware, Ordered {
    
        private Integer port;
        private String contextPath;
        private String servletPath = "/";
    
        private final Tomcat tomcat = new Tomcat();
        private final Jetty jetty = new Jetty();
        private final Undertow undertow = new Undertow();
    
        public static class Tomcat {
            private final Accesslog accesslog = new Accesslog();
            private int maxThreads = 0; // Number of threads in protocol handler
            private int maxConnections = 0;
            private int acceptCount = 0;
        }
    
        public static class Jetty { //...... }
    
        public static class Undertow {  //...... }
    
        //......
    }
    

spring boot 是如何为 servlet 容器设置这些参数的呢？我们注意到 `ServerProperties` 实现了
`EmbeddedServletContainerCustomizer`
接口，通过这个接口便可以进行参数设置，下面列出了部分代码。首先，对通用参数进行设置，比如 `端口`、`上下文路径`、`session 超时时间`
等等，然后判断 `ConfigurableEmbeddedServletContainer` 的具体实现类，分别对具体的 servlet
容器进行配置，因为不同 servlet 容器的参数是不一样的，所以需要特殊处理。如果我们需要对 tomcat 容器进行额外的设置，可以实现
`EmbeddedServletContainerCustomizer` 接口，然后把这个 bean 注册到 spring 容器中即可

    
    
    @Override
    public void customize(ConfigurableEmbeddedServletContainer container) {
        if (getPort() != null) {
            container.setPort(getPort());
        }
        // other code......
    
        // 根据具体的实现类，分别对具体的 servlet 容器进行配置
        if (container instanceof TomcatEmbeddedServletContainerFactory) {
            // 即 private final Tomcat tomcat = new Tomcat();
            getTomcat().customizeTomcat(this,
                    (TomcatEmbeddedServletContainerFactory) container);
        }
        if (container instanceof JettyEmbeddedServletContainerFactory) {
            getJetty().customizeJetty(this,
                    (JettyEmbeddedServletContainerFactory) container);
        }
    
        if (container instanceof UndertowEmbeddedServletContainerFactory) {
            getUndertow().customizeUndertow(this,
                    (UndertowEmbeddedServletContainerFactory) container);
        }
        container.addInitializers(new SessionConfiguringInitializer(this.session));
        container.addInitializers(new InitParameterConfiguringServletContextInitializer(
                getContextParameters()));
    }
    

`EmbeddedServletContainerCustomizer` 又是何时被调用的呢？它是通过 `BeanPostProcessor`
进行扩展实现的，从 spring 容器中获取 `ConfigurableEmbeddedServletContainer` 对象时，便会执行该
`BeanPostProcessor`，这里再次感受到 `BeanPostProcessor` 的强大之处。

    
    
    public class EmbeddedServletContainerCustomizerBeanPostProcessor
            implements BeanPostProcessor, BeanFactoryAware {
    
        @Override
        public Object postProcessBeforeInitialization(Object bean, String beanName)
                throws BeansException {
            if (bean instanceof ConfigurableEmbeddedServletContainer) {
                postProcessBeforeInitialization((ConfigurableEmbeddedServletContainer) bean);
            }
            return bean;
        }
    
        private void postProcessBeforeInitialization(ConfigurableEmbeddedServletContainer bean) {
            for (EmbeddedServletContainerCustomizer customizer : getCustomizers()) {
                customizer.customize(bean);
            }
        }
    }
    

## 总结

在此，spring boot 集成 tomcat 的代码分析便告一段落，最后，我们用一张图总结下整个逻辑([查看原图](http://img-
blog.csdn.net/20180321195638167))

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180321195638167.png)

  * spring boot 利用 spring 的 SPI 的机制加载 EmbeddedServletContainerAutoConfiguration 该配置类，将 TomcatEmbeddedServletContainerFactory 加载到 spring 容器中
  * 对 tomcat 容器进行配置的动作，由 BeanFactoryPostProcessor 完成，spring boot 内置了多种 EmbeddedServletContainerCustomizer，由 ServerConfig 完成对 servlet 容器的配置
  * 利用工厂模式创建 TomcatEmbeddedServletContainer，并且调用 `org.apache.catalina.startup.Tomcat#start()` 启动 tomcat 容器

