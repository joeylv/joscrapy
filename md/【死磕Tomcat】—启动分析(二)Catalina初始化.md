  * 1 main方法
    * 1.1 init
    * 1.2 load & start
  * 2 Catalina
    * 2.1 load(init)
    * 2.2 Server初始化
    * 2.3 Service初始化
    * 2.4 Engine初始化
    * 2.5 Connector初始化
    * 2.6 ProtocolHandler初始化
  * 3 总结

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79051444>

Tomcat运行是通过Bootstrap的main方法，在开发工具中，我们只需要运行Bootstrap的main方法，便可以启动tomcat进行代码调试和分析。Bootstrap是tomcat的入口，它会完成初始化ClassLoader，实例化Catalina以及load、start动作。在这一篇文章中，我们将会对tomcat初始化过程进行分析。

## main方法

首先实例化Bootstrap，并调用init方法对其初始化

    
    
    Bootstrap bootstrap = new Bootstrap();
    bootstrap.init();
    

### init

首先初始化commonLoader、catalinaLoader、sharedLoader，默认情况下这三个是相同的实例，用于加载不同的资源。然后，使用反射实例化Catalina，设置其parentClassLoader为sharedLoader

    
    
    public void init() throws Exception {
    
        // 初始化commonLoader、catalinaLoader、sharedLoader，关于ClassLoader的后面再单独分析
        initClassLoaders();
    
        Thread.currentThread().setContextClassLoader(catalinaLoader);
        SecurityClassLoad.securityClassLoad(catalinaLoader);
    
        // 反射方法实例化Catalina，后面初始化Catalina也用了很多反射，不知道意图是什么
        Class<?> startupClass = catalinaLoader.loadClass("org.apache.catalina.startup.Catalina");
        Object startupInstance = startupClass.getConstructor().newInstance();
    
        // 反射调用setParentClassLoader方法，设置其parentClassLoader为sharedLoader
        String methodName = "setParentClassLoader";
        Class<?> paramTypes[] = new Class[1];
        paramTypes[0] = Class.forName("java.lang.ClassLoader");
        Object paramValues[] = new Object[1];
        paramValues[0] = sharedLoader;
        Method method =
            startupInstance.getClass().getMethod(methodName, paramTypes);
        method.invoke(startupInstance, paramValues);
    
        // 引用Catalina实例
        catalinaDaemon = startupInstance;
    }
    

### load & start

初始化Bootstrap之后，接下来就是加载配置，启动容器。而load、start实际上是由Bootstrap反射调用Catalina的load、start，这一部分代码将在下面的Catalina部分进行分析

  * 启动时，Catalina.setAwait(true)，其目的是为了让tomcat在关闭端口阻塞监听关闭命令，参考Catalina.await()方法
  * deamon.load(args)，实际上会去调用Catalina#load(args)方法，会去初始化一些资源，优先加载conf/server.xml，找不到再去加载server-embed.xml；此外，load方法还会初始化Server
  * daemon.start()，实例上是调用Catalina.start()

    
    
    // daemon即Bootstrap实例
    daemon.setAwait(true);
    daemon.load(args);
    daemon.start();</code>
    

## Catalina

由前面的分析，可知Bootstrap中的load逻辑实际上是交给Catalina去处理的，下面我们对Catalina的初始化过程进行分析

### load(init)

load阶段主要是通过读取conf/server.xml或者server-
embed.xml，实例化Server、Service、Connector、Engine、Host等组件，并调用Lifecycle#init()完成初始化动作，以及发出INITIALIZING、INITIALIZED事件

  1. 首先初始化jmx的环境变量
  2. 定义解析server.xml的配置，告诉Digester哪个xml标签应该解析成什么类，如果我们要改变server.xml的某个属性值(比如优化tomcat线程池)，直接查看对应实现类的setXXX方法即可
  3. 解析conf/server.xml或者server-embed.xml，并且实例化对应的组件并且赋值操作，比如Server、Container、Connector等等
  4. 为Server设置catalina信息，指定Catalina实例，设置catalina的home、base路径
  5. 调用StarndServer#init()方法，完成各个组件的初始化，并且由parent组件初始化child组件，一层套一层，这个设计真心牛逼！

    
    
    public void load() {
    
        initDirs();
    
        // 初始化jmx的环境变量
        initNaming();
    
        // Create and execute our Digester
        // 定义解析server.xml的配置，告诉Digester哪个xml标签应该解析成什么类
        Digester digester = createStartDigester();
    
        InputSource inputSource = null;
        InputStream inputStream = null;
        File file = null;
        try {
    
          // 首先尝试加载conf/server.xml，省略部分代码......
          // 如果不存在conf/server.xml，则加载server-embed.xml(该xml在catalina.jar中)，省略部分代码......
          // 如果还是加载不到xml，则直接return，省略部分代码......
    
          try {
              inputSource.setByteStream(inputStream);
    
              // 把Catalina作为一个顶级实例
              digester.push(this);
    
              // 解析过程会实例化各个组件，比如Server、Container、Connector等
              digester.parse(inputSource);
          } catch (SAXParseException spe) {
              // 处理异常......
          }
        } finally {
            // 关闭IO流......
        }
    
        // 给Server设置catalina信息
        getServer().setCatalina(this);
        getServer().setCatalinaHome(Bootstrap.getCatalinaHomeFile());
        getServer().setCatalinaBase(Bootstrap.getCatalinaBaseFile());
    
        // Stream redirection
        initStreams();
    
        // 调用Lifecycle的init阶段
        try {
            getServer().init();
        } catch (LifecycleException e) {
            // ......
        }
    
        // ......
    
    }
    

load时序图如下所示([查看原图](https://img-
blog.csdn.net/20180110010608836?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvRHdhZGVfbWlh/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast))：

![init时序图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180110010608836.jpg)

  * Digester利用jdk提供的sax解析功能，将server.xml的配置解析成对应的Bean，并完成注入，比如往Server中注入Service
  * EngineConfig，它是一个LifecycleListener实现，用于配置Engine，但是只会处理START_EVENT和STOP_EVENT事件
  * Connector默认会有两种：HTTP/1.1、AJP，不同的Connector内部持有不同的CoyoteAdapter和ProtocolHandler，在Connector初始化的时候，也会对ProtocolHandler进行初始化，完成端口的监听
  * ProtocolHandler常用的实现有Http11NioProtocol、AjpNioProtocol，还有apr系列的Http11AprProtocol、AjpAprProtocol，apr系列只有在使用apr包的时候才会使用到
  * 在ProtocolHandler调用init初始化的时候，还会去执行AbstractEndpoint的init方法，完成请求端口绑定、初始化NIO等操作，在tomcat7中使用JIoEndpoint阻塞IO，而tomcat8中直接移除了JIoEndpoint，具体信息请查看org.apache.tomcat.util.net这个包

Catalina在load结束之前，会调用Server的init()完成各个组件的初始化，下面我们来分析下各个组件在init初始化过程中都做了哪些操作

### Server初始化

StandardServer是由Catalina进行init初始化的，调用的是LifecycleBase父类的init方法，而StandardServer继承至LifecycleMBeanBase，重写了initInternal方法。关于这块的知识，请参考上一篇Lifecycle的博客

StandardServer初始化的时序图如下所示，为了表述清楚，我这里把LifecycleBase、LifecycleMBeanBase拆开了，实际上是同一个StandardServer实例对象，存在继承关系  
  
![StandardServer时序图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180110233231370.jpg)

由上图可以很清晰地看到，StandardServer的初始化过程，先由父类LifecycleBase改变当前的state值并发出事件通知，
**那么这个时候StandardServer的子容器StandardService内部的state是否会发生改变呢，是否会发出事件通知呢？**
当然是不会的，因为这个state值不是LifecycleBase的静态成员变量，StandardServer只能改变自己的值，而StandardService只有在被StandardServer调用init初始化的时候才会改变，二者拥有独立的状态。考虑到有其它线程可能会改变StandardServer的state值，比如利用jmx执行init操作，因此要考虑并发问题，所以LifecycleBase#init()使用了synchronized锁，并且state是volatile修饰的。

LifecycleBase改变state、发出事件通知之后，便会执行StandardServer自身的initInternal，我们来看看这个里面都干嘛了

    
    
    protected void initInternal() throws LifecycleException {
    
        super.initInternal();
    
        // 往jmx中注册全局的String cache，尽管这个cache是全局听，但是如果在同一个jvm中存在多个Server，
        // 那么则会注册多个不同名字的StringCache，这种情况在内嵌的tomcat中可能会出现
        onameStringCache = register(new StringCache(), "type=StringCache");
    
        // 注册MBeanFactory，用来管理Server
        MBeanFactory factory = new MBeanFactory();
        factory.setContainer(this);
        onameMBeanFactory = register(factory, "type=MBeanFactory");
    
        // 往jmx中注册全局的NamingResources
        globalNamingResources.init();
    
        // Populate the extension validator with JARs from common and shared class loaders
        if (getCatalina() != null) {
            // 忽略ClassLoader操作
        }
    
        // 初始化内部的Service
        for (int i = 0; i < services.length; i++) {
            services[i].init();
        }
    }
    

  1. 先是调用super.initInternal()，把自己注册到jmx
  2. 然后注册StringCache和MBeanFactory
  3. 初始化NamingResources，就是server.xml中指定的GlobalNamingResources
  4. 调用Service子容器的init方法，让Service组件完成初始化，注意：在同一个Server下面，可能存在多个Service组件

### Service初始化

StandardService和StandardServer都是继承至LifecycleMBeanBase，因此公共的初始化逻辑都是一样的，这里不做过多介绍，我们直接看下initInternal

    
    
    protected void initInternal() throws LifecycleException {
    
        // 往jmx中注册自己
        super.initInternal();
    
        // 初始化Engine
        if (engine != null) {
            engine.init();
        }
    
        // 存在Executor线程池，则进行初始化，默认是没有的
        for (Executor executor : findExecutors()) {
            if (executor instanceof JmxEnabled) {
                ((JmxEnabled) executor).setDomain(getDomain());
            }
            executor.init();
        }
    
        // 暂时不知道这个MapperListener的作用
        mapperListener.init();
    
        // 初始化Connector，而Connector又会对ProtocolHandler进行初始化，开启应用端口的监听
        synchronized (connectorsLock) {
            for (Connector connector : connectors) {
                try {
                    connector.init();
                } catch (Exception e) {
                    // 省略部分代码，logger and throw exception
                }
            }
        }
    }
    

  1. 首先，往jmx中注册StandardService
  2. 初始化Engine，而Engine初始化过程中会去初始化Realm(权限相关的组件)
  3. 如果存在Executor线程池，还会进行init操作，这个Excecutor是tomcat的接口，继承至java.util.concurrent.Executor、org.apache.catalina.Lifecycle
  4. 初始化Connector连接器，默认有http1.1、ajp连接器，而这个Connector初始化过程，又会对ProtocolHandler进行初始化，开启应用端口的监听，后面会详细分析

### Engine初始化

StandardEngine在init阶段，需要获取Realm，这个Realm是干嘛用的？

> Realm(域)是用于对单个用户进行身份验证的底层安全领域的只读外观，并标识与这些用户相关联的安全角色。  
>  域可以在任何容器级别上附加，但是通常只附加到Context，或者更高级别的容器。

StandardEngine初始化的代码如下：

    
    
    @Override
    protected void initInternal() throws LifecycleException {
        getRealm();
        super.initInternal();
    }
    
    public Realm getRealm() {
        Realm configured = super.getRealm();
        if (configured == null) {
            configured = new NullRealm();
            this.setRealm(configured);
        }
        return configured;
    }
    

由前面的类图可知，StandardEngine继承至ContainerBase，而ContainerBase重写了initInternal()方法，用于初始化start、stop线程池，这个线程池有以下特点：  
  
1\. core线程和max是相等的，默认为1  
2\. 允许core线程在超时未获取到任务时退出线程  
3\. 线程获取任务的超时时间是10s，也就是说所有的线程(包括core线程)，超过10s未获取到任务，那么这个线程就会被销毁

这么做的初衷是什么呢？因为这个线程池只需要在容器启动和停止的时候发挥作用，没必要时时刻刻处理任务队列

ContainerBase的代码如下所示：

    
    
    // 默认是1个线程
    private int startStopThreads = 1;
    protected ThreadPoolExecutor startStopExecutor;
    
    @Override
    protected void initInternal() throws LifecycleException {
        BlockingQueue<Runnable> startStopQueue = new LinkedBlockingQueue<>();
        startStopExecutor = new ThreadPoolExecutor(
                getStartStopThreadsInternal(),
                getStartStopThreadsInternal(), 10, TimeUnit.SECONDS,
                startStopQueue,
                new StartStopThreadFactory(getName() + "-startStop-"));
        // 允许core线程超时未获取任务时退出
        startStopExecutor.allowCoreThreadTimeOut(true);
        super.initInternal();
    }
    
    private int getStartStopThreadsInternal() {
        int result = getStartStopThreads();
    
        if (result > 0) {
            return result;
        }
        result = Runtime.getRuntime().availableProcessors() + result;
        if (result < 1) {
            result = 1;
        }
        return result;
    }
    

这个startStopExecutor线程池有什么用呢？

  1. 在start的时候，如果发现有子容器，则会把子容器的start操作放在线程池中进行处理
  2. 在stop的时候，也会把stop操作放在线程池中处理

在前面的文章中我们介绍了Container组件，StandardEngine作为顶层容器，它的直接子容器是StardandHost，但是对StandardEngine的代码分析，我们并没有发现它会对子容器StardandHost进行初始化操作，StandardEngine不按照套路出牌，而是把初始化过程放在start阶段。个人认为Host、Context、Wrapper这些容器和具体的webapp应用相关联了，初始化过程会更加耗时，因此在start阶段用多线程完成初始化以及start生命周期，否则，像顶层的Server、Service等组件需要等待Host、Context、Wrapper完成初始化才能结束初始化流程，整个初始化过程是具有传递性的

### Connector初始化

Connector也是继承至LifecycleMBeanBase，公共的初始化逻辑都是一样的。我们先来看下Connector的默认配置，大部分属性配置都可以在Connector类中找到，tomcat默认开启了HTTP/1.1、AJP/1.3，其实AJP的用处不大，可以去掉

    
    
    <Connector port="8080" protocol="HTTP/1.1"
                   connectionTimeout="20000"
                   redirectPort="8443" />
    
    <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
    

Connector定义了很多属性，比如port、redirectPort、maxCookieCount、maxPostSize等等，比较有意思的是竟然找不到connectionTimeout的定义，全文搜索后发现使用了属性名映射，估计是为了兼容以前的版本

    
    
    protected static final HashMap<String,String> replacements = new HashMap<>();
    static {
        replacements.put("acceptCount", "backlog");
        replacements.put("connectionLinger", "soLinger");
        replacements.put("connectionTimeout", "soTimeout");
        replacements.put("rootFile", "rootfile");
    }
    
    public Object getProperty(String name) {
        String repl = name;
        if (replacements.get(name) != null) {
            repl = replacements.get(name);
        }
        return IntrospectionUtils.getProperty(protocolHandler, repl);
    }
    
    public boolean setProperty(String name, String value) {
        String repl = name;
        if (replacements.get(name) != null) {
            repl = replacements.get(name);
        }
        return IntrospectionUtils.setProperty(protocolHandler, repl, value);
    }
    

initInternal过程如下所示：

  1. 实例化Coyote适配器，这个适配器是用于Coyote的Request、Response与HttpServlet的Request、Response适配的，后续的博客会进行深入分析 
  2. 为ProtocolHander指定CoyoteAdapter用于处理请求 
  3. 初始化ProtocolHander，这一部分放在Connector后面进行分析

    
    
    protected void initInternal() throws LifecycleException {
    
        // 注册jmx
        super.initInternal();
    
        // 初始化Coyote适配器，这个适配器是用于Coyote的Request、Response与HttpServlet的Request、Response适配的
        adapter = new CoyoteAdapter(this);
    
        // protocolHandler需要指定Adapter用于处理请求
        protocolHandler.setAdapter(adapter);
    
        // Make sure parseBodyMethodsSet has a default
        if (null == parseBodyMethodsSet) {
            setParseBodyMethods(getParseBodyMethods());
        }
    
        // apr支持，忽略部分代码......
    
        // 初始化ProtocolHandler，这个init不是Lifecycle定义的init，而是ProtocolHandler接口的init
        try {
            protocolHandler.init();
        } catch (Exception e) {
            throw new LifecycleException(
                    sm.getString("coyoteConnector.protocolHandlerInitializationFailed"), e);
        }
    }
    

### ProtocolHandler初始化

接下来，我们分析下HTTP/1.1的ProtocolHandler的初始化过程。首先，我们来认识下ProtocolHandler，它是一个抽象的协议实现，它不同于JNI这样的Jk协议，它是单线程、基于流的协议。ProtocolHandler是一个Cycote连接器实现的主要接口，而Adapter适配器是由一个Coyote
Servlet容器实现的主要接口，定义了处理请求的抽象接口。

    
    
    public interface ProtocolHandler {
    
        public void setAdapter(Adapter adapter);
        public Adapter getAdapter();
        public Executor getExecutor();
    
        public void init() throws Exception;
        public void start() throws Exception;
        public void pause() throws Exception;
        public void resume() throws Exception;
        public void stop() throws Exception;
        public void destroy() throws Exception;
    
        // other code......
    }
    
    public interface Adapter {
    
        public void service(Request req, Response res) throws Exception;
    
        public boolean prepare(Request req, Response res) throws Exception;
    
        public boolean asyncDispatch(Request req,Response res, SocketEvent status) throws Exception;
    
        public void log(Request req, Response res, long time);
    
        public void checkRecycled(Request req, Response res);
    
        public String getDomain();
    }
    

ProtocolHandler的子类如下所示，AbstractProtocol是基本的实现，而NIO默认使用的是Http11NioProtocol

![ProtocolHandler继承关系](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180111020650138.png)

调用ProtocolHandler的init进行初始化是调用的AbstractProtocol，首先完成jmx的注册，然后对NioEndpoint进行初始化

    
    
    public abstract class AbstractProtocol<S> implements ProtocolHandler,
            MBeanRegistration {
        public void init() throws Exception {
            // 完成jmx注册
            if (oname == null) {
                oname = createObjectName();
                if (oname != null) {
                    Registry.getRegistry(null, null).registerComponent(this, oname, null);
                }
            }
            if (this.domain != null) {
                rgOname = new ObjectName(domain + ":type=GlobalRequestProcessor,name=" + getName());
                Registry.getRegistry(null, null).registerComponent(
                        getHandler().getGlobal(), rgOname, null);
            }
    
            String endpointName = getName();
            endpoint.setName(endpointName.substring(1, endpointName.length()-1));
            endpoint.setDomain(domain);
    
            // 初始化endpoint
            endpoint.init();
        }
    }
    

NioEndpoint初始化过程，最重要的是完成端口和地址的绑定监听工作，关于网络通信这块的内容将在后面着重介绍

    
    
    public class NioEndpoint extends AbstractJsseEndpoint<NioChannel> {
        public void bind() throws Exception {
    
            // 实例化ServerSocketChannel，并且绑定端口和地址
            serverSock = ServerSocketChannel.open();
            socketProperties.setProperties(serverSock.socket());
            InetSocketAddress addr = (getAddress()!=null?new InetSocketAddress(getAddress(),getPort()):new InetSocketAddress(getPort()));
    
            // 设置最大连接数，原来是在这里设置的
            serverSock.socket().bind(addr,getAcceptCount());
            serverSock.configureBlocking(true); //mimic APR behavior
    
            // 初始化acceptor、poller线程的数量
            // Initialize thread count defaults for acceptor, poller
            if (acceptorThreadCount == 0) {
                // FIXME: Doesn"t seem to work that well with multiple accept threads
                acceptorThreadCount = 1;
            }
            if (pollerThreadCount <= 0) {
                pollerThreadCount = 1;
            }
            setStopLatch(new CountDownLatch(pollerThreadCount));
    
            // 如果有必要的话初始化ssl
            initialiseSsl();
    
            // 初始化selector
            selectorPool.open();
        }
    }
    

## 总结

至此，整个初始化过程便告一段落。整个初始化过程，由parent组件控制child组件的初始化，一层层往下传递，直到最后全部初始化OK。下图描述了整体的传递流程

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180113142248714.png)

默认情况下，Server只有一个Service组件，Service组件先后对Engine、Connector进行初始化。而Engine组件并不会在初始化阶段对子容器进行初始化，Host、Context、Wrapper容器的初始化是在start阶段完成的。tomcat默认会启用HTTP1.1和AJP的Connector连接器，这两种协议默认使用Http11NioProtocol、AJPNioProtocol进行处理

