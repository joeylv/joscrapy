  * 1 Context 容器
    * 1.1 触发 CONFIGURE_START_EVENT 事件
    * 1.2 启动 Wrapper 容器
    * 1.3 调用 ServletContainerInitializer
    * 1.4 启动 Servlet 相关的 Listener
  * 2 初始化 Filter
  * 3 处理 Wrapper 容器
  * 4 、Wrapper 容器
    * 4.1 启动 Wrapper 容器
    * 4.2 加载 Wrapper
  * 5 总结

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79328151>

上一篇文章中我们分析了 Service、Engine、Host、Pipeline、Valve 组件的启动逻辑，在 HostConfig 中会实例化
StandardContext，并启动 Context 容器，完成 webapp
应用程序的启动，这一块是最贴近我们开发的应用程序。在这一篇文章中，我们将要分析 tomcat 是如何解析并初始化应用程序定义的
Servlet、Filter、Listener 等

首先我们思考几个问题：

1 . tomcat 如何支持 servlet3.0 的注解编程，比如对 javax.servlet.annotation.WebListener
注解的支持？

> 如果 tomcat 利用 ClassLoader 加载 webapp 下面所有的 class，从而分析 Class
对象的注解，这样子肯定会导致很多问题，比如 MetaSpace 出现内存溢出，而且加载了很多不想干的类，我们知道 jvm 卸载 class
的条件非常苛刻，这显然是不可取的。因此，tomcat 开发了字节码解析的工具类，位于 `org.apache.tomcat.util.bcel`，bcel
即 ：Byte Code Engineering Library，专门用于解析 class 字节码，而不是像我们前面猜测的那样，把类加载到 jvm 中

  1. 假如 webapp 目录有多个应用，使用的开源框架的 jar 版本不尽一致，tomcat 是怎样避免出现类冲突？

> 不同的 webapp 使用不同的 ClassLoader 实例加载 class，因此 webapp 内部加载的 class
是不同的，自然不会出现类冲突，当然这里要排除 ClassLoader 的 parent 能够加载的 class。关于 ClassLoader
这一块，后续会专门写一篇博客进行分析

## Context 容器

首先，我们来看下StandardContext重要的几个属性，包括了我们熟悉的 ServletContext、servlet容器相关的Listener(比如
SessionListener 和 ContextListener)、FilterConfig

    
    
    protected ApplicationContext context：即ServletContext上下文
    
    private InstanceManager instanceManager：根据 class 实例化对象，比如 Listener、Filter、Servlet 实例对象
    
    private List<Object> applicationEventListenersList：SessionListener、ContextListner 等集合
    
    private HashMap<String, ApplicationFilterConfig> filterConfigs：filer 名字与 FilterConfig 的映射关系
    
    private Loader loader：用于加载class等资源
    
    private final ReadWriteLock loaderLock：用于对loader的读写操作
    
    protected Manager manager：Session管理器
    
    private final ReadWriteLock managerLock：用于对manager的读写操作
    
    private HashMap<String, String> servletMappings：url与Servlet名字的映射关系
    
    private HashMap<Integer, ErrorPage> statusPages：错误码与错误页的映射
    
    private JarScanner jarScanner：用于扫描jar包资源
    
    private CookieProcessor cookieProcessor：cookies处理器，默认使用Rfc6265CookieProcessor
    
    

StandardContext 和其他 Container 一样，也是重写了 startInternal 方法。由于涉及到 webapp
的启动流程，需要很多准备工作，比如使用 WebResourceRoot 加载资源文件、利用 Loader 加载 class、使用 JarScanner 扫描
jar 包，等等。因此StandardContext 的启动逻辑比较复杂，这里描述下几个重要的步骤：  
  
1\. 创建工作目录，比如$CATALINA_HOME\work\Catalina\localhost\examples；实例化
ContextServlet，应用程序拿到的是 ApplicationContext的外观模式  
2\. 实例化 WebResourceRoot，默认实现类是 StandardRoot，用于读取 webapp 的文件资源  
3\. 实例化 Loader 对象，Loader 是 tomcat 对于 ClassLoader 的封装，用于支持在运行期间热加载 class  
4\. 发出 CONFIGURE_START_EVENT 事件，ContextConfig 会处理该事件，主要目的是从 webapp 中读取 servlet
相关的 Listener、Servlet、Filter 等  
5\. 实例化 Sesssion 管理器，默认使用 StandardManager  
6\. 调用 listenerStart，实例化 servlet 相关的各种 Listener，并且调用  
ServletContextListener  
7\. 处理 Filter  
8\. 加载 Servlet

下面，将分析下几个重要的步骤

### 触发 CONFIGURE_START_EVENT 事件

ContextConfig 它是一个 LifycycleListener，它在 Context
启动过程中是承担了一个非常重要的角色。StandardContext 会发出 CONFIGURE_START_EVENT 事件，而
ContextConfig 会处理该事件，主要目的是通过 web.xml 或者 Servlet3.0 的注解配置，读取 Servlet 相关的配置信息，比如
Filter、Servlet、Listener 等，其核心逻辑在 `ContextConfig#webConfig()` 方法中实现。下面，我们对
ContextConfig 进行详细分析

  1. 首先，是通过 WebXmlParser 对 web.xml 进行解析，如果存在 web.xml 文件，则会把文件中定义的 Servlet、Filter、Listener 注册到 WebXml 实例中

    
    
    WebXmlParser webXmlParser = new WebXmlParser(context.getXmlNamespaceAware(),
                context.getXmlValidation(), context.getXmlBlockExternal());
    Set<WebXml> defaults = new HashSet<>();
    defaults.add(getDefaultWebXmlFragment(webXmlParser));
    
    // 创建 WebXml实例，并解析 web.xml 文件
    WebXml webXml = createWebXml();
    InputSource contextWebXml = getContextWebXmlSource();
    if (!webXmlParser.parseWebXml(contextWebXml, webXml, false)) {
        ok = false;
    }
    

1、 接下来，会处理 javax.servlet.ServletContainerInitializer，把对象实例保存到 ContextConfig 的
Map 中，待 Wrapper 子容器添加到 StandardContext 子容器中之后，再把 ServletContainerInitializer
加入 ServletContext 中。ServletContainerInitializer 是 servlet3.0 提供的一个 SPI，可以通过
HandlesTypes 筛选出相关的 servlet 类，并可以对 ServletContext 进行额外处理，下面是一个自定义的
ServletContainerInitializer，实现了 ServletContainerInitializer 接口，和 jdk 提供的其它 SPI
一样，需要在 META-INF/services/javax.servlet.ServletContainerInitializer 文件中指定该类名
`net.dwade.tomcat.CustomServletContainerInitializer`

    
    
    @HandlesTypes( Filter.class )
    public class CustomServletContainerInitializer implements ServletContainerInitializer {
        @Override
        public void onStartup(Set<Class<?>> c, ServletContext ctx) throws ServletException {
            for ( Class<?> type : c ) {
                System.out.println( type.getName() );
            }
        }
    }
    

2、如果没有 web.xml 文件，tomcat 会先扫描 WEB-INF/classes 目录下面的 class 文件，然后扫描 WEB-INF/lib
目录下面的 jar 包，解析字节码读取 servlet 相关的注解配置类，这里不得不吐槽下 serlvet3.0 注解，对 servlet
注解的处理相当重量级。tomcat 不会预先把该 class 加载到 jvm
中，而是通过解析字节码文件，获取对应类的一些信息，比如注解、实现的接口等，核心代码如下所示：

    
    
    protected void processAnnotationsStream(InputStream is, WebXml fragment,
                boolean handlesTypesOnly, Map<String,JavaClassCacheEntry> javaClassCache)
                throws ClassFormatException, IOException {
        // is 即 class 字节码文件的 IO 流
        ClassParser parser = new ClassParser(is);
    
        // 使用 JavaClass 封装 class 相关的信息
        JavaClass clazz = parser.parse();
        checkHandlesTypes(clazz, javaClassCache);
    
        if (handlesTypesOnly) {
            return;
        }
    
        AnnotationEntry[] annotationsEntries = clazz.getAnnotationEntries();
        if (annotationsEntries != null) {
            String className = clazz.getClassName();
            for (AnnotationEntry ae : annotationsEntries) {
                String type = ae.getAnnotationType();
                if ("Ljavax/servlet/annotation/WebServlet;".equals(type)) {
                    processAnnotationWebServlet(className, ae, fragment);
                }else if ("Ljavax/servlet/annotation/WebFilter;".equals(type)) {
                    processAnnotationWebFilter(className, ae, fragment);
                }else if ("Ljavax/servlet/annotation/WebListener;".equals(type)) {
                    fragment.addListener(className);
                } else {
                    // Unknown annotation - ignore
                }
            }
        }
    }
    

tomcat 使用自己的工具类 ClassParser 通过对字节码文件进行解析，获取其注解，并把
WebServlet、WebFilter、WebListener 注解的类添加到 WebXml 实例中，统一由它对 ServletContext
进行参数配置。tomcat 对字节码的处理是由  
`org.apache.tomcat.util.bcel` 包完成的，bcel 即 Byte Code Engineering
Library，其实现比较繁锁，需要对字节码结构有一定的了解，感兴趣的童鞋可以研究下底层实现。

3、配置信息读取完毕之后，会把 WebXml 装载的配置赋值给 ServletContext，在这个时候，ContextConfig 会往
StardardContext 容器中添加子容器（即 Wrapper 容器），部分代码如下所示：

    
    
    private void configureContext(WebXml webxml) {
        // 设置 Filter 定义
        for (FilterDef filter : webxml.getFilters().values()) {
            if (filter.getAsyncSupported() == null) {
                filter.setAsyncSupported("false");
            }
            context.addFilterDef(filter);
        }
    
        // 设置 FilterMapping，即 Filter 的 URL 映射
        for (FilterMap filterMap : webxml.getFilterMappings()) {
            context.addFilterMap(filterMap);
        }
    
        // 往 Context 中添加子容器 Wrapper，即 Servlet
        for (ServletDef servlet : webxml.getServlets().values()) {
            Wrapper wrapper = context.createWrapper();
            // 省略若干代码。。。
            wrapper.setOverridable(servlet.isOverridable());
            context.addChild(wrapper);
        }
    }
    

4、 tomcat 还会加载 WEB-INF/classes/META-INF/resources/、WEB-INF/lib/xxx.jar/META-
INF/resources/ 的静态资源，这一块的作用暂时不清楚，关键代码如下所示：

    
    
    // fragments 包括了 WEB-INF/classes、WEB-INF/lib/xxx.jar
    protected void processResourceJARs(Set<WebXml> fragments) {
        for (WebXml fragment : fragments) {
            URL url = fragment.getURL();
            if ("jar".equals(url.getProtocol()) || url.toString().endsWith(".jar")) {
                try (Jar jar = JarFactory.newInstance(url)) {
                    jar.nextEntry();
                    String entryName = jar.getEntryName();
                    while (entryName != null) {
                        if (entryName.startsWith("META-INF/resources/")) {
                            context.getResources().createWebResourceSet(
                                    WebResourceRoot.ResourceSetType.RESOURCE_JAR,
                                    "/", url, "/META-INF/resources");
                            break;
                        }
                        jar.nextEntry();
                        entryName = jar.getEntryName();
                    }
                }
            } else if ("file".equals(url.getProtocol())) {
                File file = new File(url.toURI());
                File resources = new File(file, "META-INF/resources/");
                if (resources.isDirectory()) {
                    context.getResources().createWebResourceSet(
                            WebResourceRoot.ResourceSetType.RESOURCE_JAR,
                            "/", resources.getAbsolutePath(), null, "/");
                }
            }
        }
    }
    

### 启动 Wrapper 容器

ContextConfig 把 Wrapper 子容器添加到 StandardContext 容器中之后，便会挨个启动 Wrapper
子容器。但是实际上，由于 StandardContext 至 ContainerBase，在添加子容器的时候，便会调用 start 方法启动
Wrapper，关于 Wrapper 的启动在下文进行详细分析

    
    
    for (Container child : findChildren()) {
        if (!child.getState().isAvailable()) {
            child.start();
        }
    }
    

### 调用 ServletContainerInitializer

在初始化 Servlet、Listener 之前，便会先调用
ServletContainerInitializer，进行额外的初始化处理。注意：ServletContainerInitializer 需要的是
Class 对象，而不是具体的实例对象，这个时候 servlet 相关的 Listener 并没有被实例化，因此不会产生矛盾

    
    
    // 指定 ServletContext 的相关参数
    mergeParameters();
    
    // 调用 ServletContainerInitializer#onStartup()
    for (Map.Entry<ServletContainerInitializer, Set<Class<?>>> entry :
        initializers.entrySet()) {
        try {
            entry.getKey().onStartup(entry.getValue(),
                    getServletContext());
        } catch (ServletException e) {
            log.error(sm.getString("standardContext.sciFail"), e);
            ok = false;
            break;
        }
    }
    

### 启动 Servlet 相关的 Listener

WebConfig 加载 Listener 时，只是保存了 className，实例化动作由 StandardContext 触发。前面在介绍
StandardContext 的时候提到了 InstanceManager，创建实例的逻辑由 InstanceManager 完成。

Listener 监听器分为 Event、Lifecycle 监听器，WebConfig 在加载 Listener
的时候是不会区分的，实例化之后才会分开存储。在完成 Listener 实例化之后，tomcat 容器便启动 OK 了。此时，tomcat
需要通知应用程序定义的 ServletContextListener，方便应用程序完成自己的初始化逻辑，它会遍历
ServletContextListener 实例，并调用其 contextInitialized 方法，比如 spring 的
ContextLoaderListener

有以下 Event 监听器，主要是针对事件通知：

  * ServletContextAttributeListener 
  * ServletRequestAttributeListener 
  * ServletRequestListener 
  * HttpSessionIdListener 
  * HttpSessionAttributeListener

有以下两种 Lifecycle 监听器，主要是针对 ServletContext、HttpSession 的生命周期管理，比如创建、销毁等

  * ServletContextListener 
  * HttpSessionListener

## 初始化 Filter

ContextConfig 在处理 CONFIGURE_START_EVENT 事件的时候，会使用 FilterDef 保存 Filter 信息。而
StandardContext 会把 FilterDef 转化成 ApplicationFilterConfig，在
ApplicationFilterConfig 构造方法中完成 Filter 的实例化，并且调用 Filter 接口的 init 方法，完成 Filter
的初始化。ApplicationFilterConfig 是 `javax.servlet.FilterConfig`  
接口的实现类。

    
    
    public boolean filterStart() {
        boolean ok = true;
        synchronized (filterConfigs) {
            filterConfigs.clear();
            for (Entry<String,FilterDef> entry : filterDefs.entrySet()) {
                String name = entry.getKey();
                try {
                    // 在构造方法中完成 Filter 的实例化，并且调用 Filter 接口的 init 方法，完成 Filter 的初始化
                    ApplicationFilterConfig filterConfig =
                            new ApplicationFilterConfig(this, entry.getValue());
                    filterConfigs.put(name, filterConfig);
                } catch (Throwable t) {
                    // 省略 logger 处理
                    ok = false;
                }
            }
        }
        return ok;
    }
    

## 处理 Wrapper 容器

Servlet 对应 tomcat 的 Wrapper 容器，完成 Filter 初始化之后便会对 Wrapper 容器进行处理，如果 Servlet 的
loadOnStartup >= 0，便会在这一阶段完成 Servlet 的加载，并且值越小越先被加载，否则在接受到请求的时候才会加载 Servlet。

加载过程，主要是完成 Servlet 的实例化，并且调用 Servlet 接口的 init 方法，具体的逻辑将在下文进行详细分析

    
    
    // StandardWrapper 实例化并且启动 Servlet，由于 Servlet 存在 loadOnStartup 属性
    // 因此使用了 TreeMap，根据 loadOnStartup 值 对 Wrapper 容器进行排序，然后依次启动 Servlet
    if (ok) {
        if (!loadOnStartup(findChildren())){
            log.error(sm.getString("standardContext.servletFail"));
            ok = false;
        }
    }
    

loadOnStartup 方法使用 TreeMap 对 Wrapper 进行排序，loadOnStartup 值越小越靠前，值相同的 Wrapper
放在同一个 List 中，代码如下所示：

    
    
    public boolean loadOnStartup(Container children[]) {
    
        // 使用 TreeMap 对 Wrapper 进行排序，loadOnStartup 值越小越靠前，值相同的 Wrapper 放在同一个 List 中
        TreeMap<Integer, ArrayList<Wrapper>> map = new TreeMap<>();
        for (int i = 0; i < children.length; i++) {
            Wrapper wrapper = (Wrapper) children[i];
            int loadOnStartup = wrapper.getLoadOnStartup();
            if (loadOnStartup < 0)
                continue;
            Integer key = Integer.valueOf(loadOnStartup);
            ArrayList<Wrapper> list = map.get(key);
            if (list == null) {
                list = new ArrayList<>();
                map.put(key, list);
            }
            list.add(wrapper);
        }
    
        // 根据 loadOnStartup 值有序加载 Wrapper 容器
        for (ArrayList<Wrapper> list : map.values()) {
            for (Wrapper wrapper : list) {
                try {
                    wrapper.load();
                } catch (ServletException e) {
                    if(getComputedFailCtxIfServletStartFails()) {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    

## 、Wrapper 容器

Wrapper 容器是 tomcat 所有容器中最底层子容器，它没有子容器，并且父容器是
Context，对这一块不了解的童鞋请移步前面的博客[《tomcat框架设计》](https://blog.csdn.net/dwade_mia/article/details/tomcat%E6%A1%86%E6%9E%B6%E8%AE%BE%E8%AE%A1)。默认实现是
StandardWrapper，我们先来看看类定义，它继承至 ContainBase，实现了 servlet 的 ServletConfig 接口，以及
tomcat 的 Wrapper 接口，说明 StandardWrapper 不仅仅是一个 Wrapper 容器实现，还是 ServletConfig
实现，部分代码如下所示：

    
    
    public class StandardWrapper extends ContainerBase
        implements ServletConfig, Wrapper, NotificationEmitter {
    
        // Wrapper 的门面模式，调用 Servlet 的 init 方法传入的是该对象
        protected final StandardWrapperFacade facade = new StandardWrapperFacade(this);    
        protected volatile Servlet instance = null; // Servlet 实例对象
        protected int loadOnStartup = -1;   // 默认值为 -1，不立即启动 Servlet
        protected String servletClass = null;
    
        public StandardWrapper() {
            super();
            swValve=new StandardWrapperValve();
            pipeline.setBasic(swValve);
            broadcaster = new NotificationBroadcasterSupport();
        }
    }
    

由前面对 [Context
的分析可知](https://blog.csdn.net/dwade_mia/article/details/79328151#add-
wrapper)，StandardContext 在启动的时候会发出 CONFIGURE_START_EVENT 事件，ContextConfig
会处理该事件，通过解析 web.xml 或者读取注解信息获取 Wrapper 子容器，并且会添加到 Context 容器中。由于
StandardContext 继承至 ContainerBase，在调用 addChild 的时候默认会启动 child 容器(即
Wrapper)，我们来看看 StandardWrapper 的启动逻辑

### 启动 Wrapper 容器

StandardWrapper 没有子容器，启动逻辑相对比较简单清晰，它重写了 startInternal 方法，主要是完成了 jmx 的事件通知，先后向
jmx 发出 starting、running 事件，代码如下所示：

    
    
    protected synchronized void startInternal() throws LifecycleException {
        // 发出 j2ee.state.starting 事件通知
        if (this.getObjectName() != null) {
            Notification notification =
                new Notification("j2ee.state.starting", this.getObjectName(), sequenceNumber++);
            broadcaster.sendNotification(notification);
        }
    
        // ConainerBase 的启动逻辑
        super.startInternal();
        setAvailable(0L);
    
        // 发出 j2ee.state.running 事件通知
        if (this.getObjectName() != null) {
            Notification notification =
                new Notification("j2ee.state.running", this.getObjectName(), sequenceNumber++);
            broadcaster.sendNotification(notification);
        }
    }
    

### 加载 Wrapper

由前面对 [Context
容器的分析可知](https://blog.csdn.net/dwade_mia/article/details/79328151#load-on-
startup)，Context 完成 Filter 初始化之后，如果 loadOnStartup >= 0 便会调用 load 方法加载 Wrapper
容器。StandardWrapper 使用 InstanceManager 实例化 Servlet，并且调用 Servlet 的 init
方法进行初始化，传入的 ServletConfig 是 StandardWrapperFacade 对象

    
    
    public synchronized void load() throws ServletException {
    
        // 实例化 Servlet，并且调用 init 方法完成初始化
        instance = loadServlet();
    
        if (!instanceInitialized) {
            initServlet(instance);
        }
    
        if (isJspServlet) {
            // 处理 jsp Servlet
        }
    }
    

## 总结

tomcat 实现了 `javax.servlet.ServletContext`  
接口，在 Context 启动的时候会实例化该对象。由 Context 容器通过 web.xml 或者 扫描 class 字节码读取 servlet3.0
的注解配置，从而加载 webapp 定义的 Listener、Servlet、Filter 等 servlet
组件，但是并不会立即实例化对象。全部加载完毕之后，依次对 Listener、Filter、Servlet 进行实例化、并且调用其初始化方法，比如  
`ServletContextListener#contextInitialized()`、`Flter#init()`  
等。

