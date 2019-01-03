  * 1 tomcat 类加载器
  * 2 WebappClassLoader
    * 2.1 WebappLoader
    * 2.2 Hotswap
  * 3 类卸载

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/80140585>

在分析 tomcat 类加载之前，我们简单的回顾下 java 体系的类加载器

  * 启动类加载器（Bootstrap ClassLoader)：加载对象是java的核心类库，把一些的 java 类加载到 jvm 中，它并不是我们熟悉的 `ClassLoader`，而是 jvm 层面由 C/C++ 实现的类加载器，负责加载 $JAVA_HOME/jre/lib 目录下 jvm 指定的类库，它是无法被 java 应用程序直接使用的
  * 扩展类加载器（Extension Classloader）：它是一个 ClassLoader 实例，父加载器是启动类加载器，它负责加载 $JAVA_HOME/jre/lib/ext 目录的类库
  * 应用类加载器（Application ClassLoader）：又叫做系统类加载器(System ClassLoader)，负责加载用户类路径（-cp参数）指定的类库，可以通过 `ClassLoader.getSystemClassLoader()` 获取，它也是由启动类加载器加载的
  * 自定义类加载器：应用程序根据自己的需求开发的类加载器，可以继承 `ClassLoader`，当然也可以不继承

下图描述了类加载器的关系图，其中自定义类加载器有N多个

![类加载器](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/classloader.png)

我们知道 `java.lang.ClassLoader` 有双亲委派机制（准确的说是单亲，因为只有一个parent），这只是 java
建议的规范，我们也可以不遵循这条规则，但是建议遵循该规则。此外，有一点需要注意的是，类加载器不局限于
`ClassLoader`，我们也可以自己实现一个类加载器，只要你加载出来的 Class 符合 jvm 规范即可

我们在日常开发工作中，经常会遇到类冲突的情况，明明 classpath
下面的类有这个方法，但是一旦跑线上环境就出错，比如`NoSuchMethodError`、`NoClassDefFoundError`、`NoClassDefFoundError`
等。我们可以使用 jvm 参数 `-verbose:class`
方便地定位该问题，使用该参数可以快速地定位某个类是从哪个jar包加载的，而不是一味地埋头苦干，求百度，找Google。下面是使用
`-verbose:class` jvm 参数的部分日志输出

    
    
    [Loaded org.springframework.context.annotation.CommonAnnotationBeanPostProcessor from file:/D:/tomcat/webapps/touch/WEB-INF/lib/spring-context-4.3.7.RELEASE.jar]
    [Loaded com.alibaba.dubbo.rpc.InvokerListener from file:/D:/tomcat/webapps/touch/WEB-INF/lib/dubbo-2.5.3.jar]
    [Loaded com.alibaba.dubbo.common.bytecode.Wrapper from file:/D:/tomcat/webapps/touch/WEB-INF/lib/dubbo-2.5.3.jar]
    

我们有必要了解下关于类加载有几个重要的知识点：

  * 在 Java 中我们用完全类名来标识一个类，而在 JVM 层面，使用完全类名 + CloassLoader 对象实例 ID 作为唯一标识，因此使用不同实例的类加载器，加载的两个同名的类，他们的类实例是不同的，并且不能强制转换
  * 在双亲委派机制中，类加载器查找类时，是一层层往父类加载器查找的，最后才查看自己，如果都找不到则会抛出异常，而不是一层层往下找的
  * 每个运行中的线程都有一个 `CloassLoader`，并且会从父线程中继承（默认是应用类加载器），在没有显式声明由哪个类加载器加载类时（比如 new 关键字），将默认由当前线程的类加载器加载该类

由于篇幅有限，关于类加载的过程这里不再展开了，可以参考厮大的博客

  * Java虚拟机类加载机制：<https://blog.csdn.net/u013256816/article/details/50829596>

## tomcat 类加载器

根据实际的应用场景，我们来分析下 tomcat 类加载器需要解决的几个问题

  * 为了避免类冲突，每个 webapp 项目中各自使用的类库要有隔离机制
  * 不同 webapp 项目支持共享某些类库
  * 类加载器应该支持热插拔功能，比如对 jsp 的支持、webapp 的 reload 操作

为了解决以上问题，tomcat设计了一套类加载器，如下图所示。在 Tomcat 里面最重要的是 Common
类加载器，它的父加载器是应用程序类加载器，负责加载 `${catalina.base}/lib`、`${catalina.home}/lib`
目录下面所有的 .jar 文件和 .class 文件。下图的虚线部分，有 catalina 类加载器、share 类加载器，并且它们的 parent 是
common 类加载器，默认情况下被赋值为 Common 类加载器实例，即 Common 类加载器、catalina 类加载器、 share
类加载器都属于同一个实例。当然，如果我们通过修改 `catalina.properties` 文件的 `server.loader` 和
`shared.loader` 配置，从而指定其创建不同的类加载器

![tomcat类加载器](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/tomcat-classloader.png)

我们先从 `Bootstrap` 这个入口说起，在执行 `init` 的时候会实例化类加载器，在初始化类加载器之后立即设置线程上下文类加载器（Thread
Context ClassLoader）为 catalina 类加载器，接下来是为 `Catalina`
组件指定父类加载器。为什么要设置线程上下文的类加载器呢？一方面，很多诸如 `ClassUtils` 之类的编码，他们在获取 `ClassLoader`
的时候，都是先尝试从 Thread 上下文中获取 `ClassLoader`，例如：`ClassLoader cl =
Thread.currentThread().getContextClassLoader();`另一方面，在没有显式指定类加载器的情况下，默认使用线程的上下文类加载器加载类，由于
tomcat 的大部分 jar 包都在 `${catalina.hom}/lib` 目录，因此需要将线程类加载器指定为 catalina
类加载器，否则加载不了相关的类。

双亲委派模型存在设计上的缺陷，在某些应用场景下，例如加载 SPI
实现（JNDI、JDBC等），如果我们严格遵循双亲委派的一般性原则，使用应用程序类加载器，由于这些 SPI 实现在厂商的 jar
包中，所以应用程序类加载器不可能认识这些代码啊，怎么办？为了解决这个问题，Java 设计团队引入了一个不太优雅的设计：`Thread Context
ClassLoader`，有了这个线程上下文类加载器，我们便可以做一些“舞弊”的事情了，JNDI 服务可以使用这个类加载器加载 SPI
需要的代码，JDBC、JAXB 也是如此。这样，双亲委派模型便被破坏了。

    
    
    Bootstrap.java
    public void init() throws Exception {
        // 初始化commonLoader、catalinaLoader、sharedLoader，关于ClassLoader的后面再看
        initClassLoaders();
    
        // 设置上下文类加载器为 catalinaLoader
        Thread.currentThread().setContextClassLoader(catalinaLoader);
        SecurityClassLoad.securityClassLoad(catalinaLoader);
    
        // 反射方法实例化Catalina，后面初始化Catalina用了很多反射，不知道意图是什么
        Class<?> startupClass = catalinaLoader.loadClass("org.apache.catalina.startup.Catalina");
        Object startupInstance = startupClass.getConstructor().newInstance();
    
        //TODO 为Catalina对象设置其父加载器为shared类加载器，默认情况下就是catalina类加载器
    
        // 引用Catalina实例
        catalinaDaemon = startupInstance;
    }
    

catalina.properties 文件的相关配置如下所示

    
    
    common.loader=${catalina.base}/lib,${catalina.base}/lib/*.jar,${catalina.home}/lib,${catalina.home}/lib/*.jar
    server.loader=
    shared.loader=
    

我们再来看下创建类加载器的代码，首先是创建 common 类加载器，从 `catalina.properties` 中读取 `common.loader`
配置作为 common 类加载器的路径。我们注意到 `common.loader` 中存在
`${catalina.base}`、`${catalina.home}` 这样的占位符，在读取配置之后，tomcat 会进行替换处理，同理
`server.loader`、`shared.loader` 也可以使用这样的占位符，或者系统变量作为占位符，有兴趣的童鞋可以参考下
`Bootstrap.replace(String str)` 源码，如果在项目中有相同的场景的话，可以直接 copy 该代码。

    
    
    Bootstrap.java
    
    private void initClassLoaders() {
        try {
            // 从catalina.properties中读取common.loader配置作为common类加载的路径
            commonLoader = createClassLoader("common", null);
            if( commonLoader == null ) {
                commonLoader=this.getClass().getClassLoader();
            }
            // 如果未指定server.loader和shared.loader配置，则catalina和shared类加载器都是common类加载器
            catalinaLoader = createClassLoader("server", commonLoader);
            sharedLoader = createClassLoader("shared", commonLoader);
        } catch (Throwable t) {
            handleThrowable(t);
            log.error("Class loader creation threw exception", t);
            System.exit(1);
        }
    }
    

接下来，我们再来看下 tomcat 是如何创建 common 类加载器的。关键代码如下所示，在创建类加载器时，会读取相关的路径配置，并把路径封装成
`Repository` 对象，然后交给 `ClassLoaderFactory` 创建类加载器。

    
    
    Bootstrap.java
    private ClassLoader createClassLoader(String name, ClassLoader parent)
            throws Exception {
    
        // 从catalina.propeties中读取配置，并替换 catalina.home、或者catalina.base，或者环境变量
        String value = CatalinaProperties.getProperty(name + ".loader");
        value = replace(value);
    
        // 遍历目录，并对路径进行处理
        List<Repository> repositories = new ArrayList<>();
        String[] repositoryPaths = getPaths(value);
        for (String repository : repositoryPaths) {
            //TODO 将路径封装成 Repository 对象
        }
        return ClassLoaderFactory.createClassLoader(repositories, parent);
    }
    

我们再进一步对 `ClassLoaderFactory` 进行分析，都是细节上的处理，比如利用文件路径构造带有明显协议的 URL 对象，例如本地文件的标准
URL 是 `file:/D:/app.jar`。另外，在创建 `URLClassLoader` 的时候还需要考虑 jdk 对权限控制的影响，因此
tomcat 利用 `AccessController` 创建 `URLClassLoader`，由此可见 tomcat
编码的严谨性。而我们在实际的开发过程中，有时候需要自定义类加载器，但往往不会考虑权限控制这块，所以在对类加载器进行编码时需要注意一下

    
    
    ClassLoaderFactory.java
    public static ClassLoader createClassLoader(List<Repository> repositories, final ClassLoader parent)
            throws Exception {
        Set<URL> set = new LinkedHashSet<>();
        if (repositories != null) {
            for (Repository repository : repositories)  {
                // 对不同类型的 Repository 对象进行处理，将路径转换为URL类型
                // 因为 URL 类型带有明显的协议，比如jar:xxx、file:xxx
            }
        }
        // 将对应的路径组装成 URL
        final URL[] array = set.toArray(new URL[set.size()]);
        // 在创建 URLClassLoader 需要考虑到 AccessController 的影响
        return AccessController.doPrivileged(
            new PrivilegedAction<URLClassLoader>() {
                public URLClassLoader run() {
                    if (parent == null)
                        return new URLClassLoader(array);
                    else
                        return new URLClassLoader(array, parent);
                }
            });
    }
    
    private static URL buildClassLoaderUrl(File file) throws MalformedURLException {
        String fileUrlString = file.toURI().toString();
        fileUrlString = fileUrlString.replaceAll("!/", "%21/"); // 转换成URL编码
        return new URL(fileUrlString);
    }
    

OK，前面介绍了 tomcat 创建类加载器的过程，接下来我们看下 tomcat 类加载器的具体应用场景

## WebappClassLoader

在前面，我们介绍了 tomcat 类加载器的设计，每个 webapp 使用单独的类加载器完成我们开发的 webapp 应用程序的类加载，而每一个
webapp 对应一个 `WebappClassLoader`。tomcat7 默认使用 `WebappClassLoader` 类加载器，而
tomcat8 默认使用 `ParallelWebappClassLoader`，支持并行加载类的特性，这也算是 tomcat8
做的一些优化吧，而实际上也是利用 jdk 的功能，需要同时满足以下两点才支持并行加载类，并且一旦注册了并行加载的能力，就不能回退了

  1. 没有创建调用者的实例
  2. 调用者的所有超类（除了类对象）都是并行注册的

基于上面两点，因此，`ParallelWebappClassLoader` 在 static 代码块中注册并行加载机制，而它的父类
`URLClassLoader` 父类也是具有并行能力的，关键代码如下所示：

    
    
    public class ParallelWebappClassLoader extends WebappClassLoaderBase {
        static {
            boolean result = ClassLoader.registerAsParallelCapable();
            if (!result) {
                log.warn(sm.getString("webappClassLoaderParallel.registrationFailed"));
            }
        }
        // 省略无关代码...
    }
    

`WebappClassLoader` 的类图如下所示，其中 `WebappClassLoaderBase` 实现了主要的逻辑，并且继承了
`Lifecycle`，在 tomcat 组件启动、关闭时会完成资源的加载、卸载操作，例如在 `start` 过程会读取我们熟悉的 `/WEB-
INF/classes`、`/WEB-INF/lib` 资源，并且记录每个 jar 包的时间戳方便重载 jar 包；而在组件 `stop`
的时候，会清理已经加载的资源；`destory` 时会显式地触发 `URLClassLoader.close()`。这个 `Lifecycle`
真是无处不在啊

![WebappClassLoader类图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/webappclassloader-class-diagram.png)

单独的类加载器是无法获取 webapp 的资源信息的，因此 tomcat 引入了 `WebappLoader`，便于访问 `Context`
组件的信息，同时为 `Context` 提供类加载的能力支持，下面我们分析下 `WebappLoader` 的底层实现

### WebappLoader

我们先来看看 `WebappLoader` 几个重要的属性，内部持有 `Context` 组件，并且有个我们熟悉的 `reloadable` 参数，如果设为
true，则会开启类的热加载机制

    
    
    public class WebappLoader extends LifecycleMBeanBase
        implements Loader, PropertyChangeListener {
        private WebappClassLoaderBase classLoader = null;   // 默认使用ParallelWebappClassLoader
        private Context context = null;
        private String loaderClass = ParallelWebappClassLoader.class.getName();
        private ClassLoader parentClassLoader = null;       // 父加载器，默认为 catalina 类加载器
        private boolean reloadable = false;                 // 是否支持热加载类
        private String classpath = null;
    }
    

在 tomcat 中，每个 webapp 对应一个 `StandardContext`，在 `start` 过程便会实例化
`WebappLoader`，并且调用其 `start` 方法完成初始化，包括创建 `ParallelWebappClassLoader`
实例，然后，还会启动 `Context` 的子容器。注意，这两个过程，都会将线程上下文类加载器指定为 `ParallelWebappClassLoader`
类加载器，在完成 webapp 相关的类加载之后，又将线程上下文类加载器设置为 catalina 类加载器。`Context`
容器的启动过程，这里便不再重复了，感兴趣的童鞋请查看前面的博文
[webapp源码分析](https://blog.csdn.net/dwade_mia/article/details/79328151)

    
    
    StandardContext.java
    
    protected synchronized void startInternal() throws LifecycleException {
        // 实例化 Loader 实例，它是 tomcat 对于 ClassLoader 的封装，用于支持在运行期间热加载 class
        if (getLoader() == null) {
            WebappLoader webappLoader = new WebappLoader(getParentClassLoader());
            webappLoader.setDelegate(getDelegate());
            setLoader(webappLoader);    // 使用了读写锁控制并发问题
        }
    
        // 将 Loader 中的 ParallelWebappClassLoader 绑定到当前线程中，并返回 catalian 类加载器
        ClassLoader oldCCL = bindThread();
    
        try {
            if (ok) {
                // 如果 Loader 是 Lifecycle 实现类，则启动该 Loader
                Loader loader = getLoader();
                if (loader instanceof Lifecycle) {
                    ((Lifecycle) loader).start();
                }
    
                // 设置 ClassLoader 的各种属性
                setClassLoaderProperty("clearReferencesRmiTargets", getClearReferencesRmiTargets());
    
                // 省略……
                // 解除线程上下文类加载器绑定
                unbindThread(oldCCL);
                oldCCL = bindThread();
    
                // 发出 CONFIGURE_START_EVENT 事件，ContextConfig 会处理该事件，主要目的是加载 Context 的子容器
                fireLifecycleEvent(Lifecycle.CONFIGURE_START_EVENT, null);
    
                // 启动子容器
                for (Container child : findChildren()) {
                    if (!child.getState().isAvailable()) {
                        child.start();
                    }
                }
            }
        } finally {
            // Unbinding thread
            unbindThread(oldCCL);
        }
    }
    

而 `WebappLoader` 在 `stop` 的时候，会销毁 `WebappClassLoader`，并且进行回收，促使 jvm 卸载已加载的类

    
    
    WebappLoader.java
    
    @Override
    protected void stopInternal() throws LifecycleException {
        // 省略不相关代码...
        if (classLoader != null) {
            try {
                classLoader.stop();
            } finally {
                classLoader.destroy();
            }
        }
        classLoader = null; // help gc
    }
    

### Hotswap

我们可以为 `Context` 组件指定 `reloadable` 属性，如果设为 `true`，tomcat便会启用
Hotswap，定期扫描类文件的变动，如果有变动，则重启 webapp 从而达到 `Hotswap` 的目的。

这个参数由 `Context` 指定的，但是会通过 `WebappLoader#setContext(Context context)`
方法调用，从而传递给 `WebappLoader`

    
    
    <Context path="examples" docBase="F:/tomcat/webapps/examples" reloadable="true" />
    

`WebappLoader` 提供了后台定时任务的方法，`Context` 容器会间隔性地进行调用，它用于监听 `class`、`jar`
等文件的变更，一旦有变动，便会对 `Context` 容器进行 `reload` 操作

    
    
    WebappLoader.java
    
    @Override
    public void backgroundProcess() {
        if (reloadable && modified()) {
            try {
                // 变更线程上下文类加载器为 webapp 类加载器
                Thread.currentThread().setContextClassLoader(WebappLoader.class.getClassLoader());
                if (context != null) {
                    context.reload();   // 重载 webapp
                }
            } finally {
                if (context != null && context.getLoader() != null) {
                    Thread.currentThread().setContextClassLoader(context.getLoader().getClassLoader());
                }
            }
        }
    }
    

## 类卸载

tomcat 既然支持类的热加载，那么肯定要考虑类的卸载因素，如果处理不当可能会造成内存泄露，tomcat
对这一块的处理也是相当谨慎，我们将在下一博文中针对这一话题进行讨论分析

