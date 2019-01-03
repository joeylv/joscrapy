  * 1 卸载类
  * 2 热加载问题
    * 2.1 文件锁
    * 2.2 类加载器泄露
    * 2.3 ThreadLocal 对象泄露

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/80512916>

在前面的文章中，我们分析了 tomcat 类加载器的相关源码，也了解了 tomcat 支持类的热加载，意味着 tomcat
要涉及类的重复卸装/装载过程，这个过程是很敏感的，一旦处理不当，可能会引起内存泄露

## 卸载类

我们知道，class 信息存放在元数据区（1.7是 Perm
区），这一块的内存相比堆而言，只占据非常小的空间，但是如果处理不当，还是有可能会导致内存溢出。这让我回想起几年前的一个故障，线上环境启用了 tomcat
的自动 reload 功能，出现过 `java.lang.OutOfMemoryError: PermGen space` 问题，排查的结果是因为
tomcat 在自动重载应用的时候，没有正常卸载类，导致 Perm 区内存没能被释放而发生溢出。tomcat
会尽量避免这类问题的发生，但是不能百分之百保证不会出现，所以还是建议不要随意开启 `reloadable` 功能

卸载类的条件很苛刻，必须同时满足以下3点：  
1\. 该类所有的实例已经被回收  
2\. 加载该类的 `ClassLoder` 已经被回收  
3\. 该类对应的 `java.lang.Class` 对象没有任何地方被引用

针对第1点，保证所有的实例被回收，这点不难，tomcat 在 Context 组件中实例化这些对象，持有直接或间接的引用，所以在热部署的时候，只要回收
Context 组件即可保证实例对象被回收。

在前面的文章中我们分析了 tomcat 类加载器，tomcat 使用 `ParallelWebappClassLoader` 加载
Class，在热部署的时候自然也会回收该类加载器。但是要注意的是，`ParallelWebappClassLoader`
会作为线程上下文的类加载器，因此要避免该类加载器对象在其他地方被引用。其实，这个问题是最隐晦的，jdk
中有些类会持有线程上下文的类加载器，作为一个优秀的开源产品，tomcat 为我们解决了很多诸如此类的问题

此外，还要保证类对应的 `java.lang.Class` 对象没有任何地方引用，只要 Class 对象作用域限制在 `Context`
组件的作用范围便不会发生泄露，tomcat 也是这么做了，使用 `Context` 实现了隔离机制

## 热加载问题

热加载会面临很多问题，有很多坑，需要非常丰富的经验。下面针对 tomcat
中涉及的类加载器泄露、对象泄露、文件锁等这几类常见的问题加以分析讨论。如果您对热加载感兴趣的话，可以研究下阿里开源的
[jarlinks](https://github.com/alibaba/jarslink)

### 文件锁

在 Windows 系统下使用 `URLConnection` 读取本地 jar 包的资源时，它会将资源缓存起来，会导致该 jar
包资源被锁。如果这个时候使用 war 包进行重新部署，需要解压 war 包再把原来目录下面的 jar 包删除，由于 jar
包资源被锁，导致删除失败，重新部署自然也会失败。我们先来看一段代码，这段代码会抛出异常，`java.nio.file.FileSystemException:
E:\spring-boot-2.0.1.RELEASE.jar: 另一个程序正在使用此文件，进程无法访问`，说明该 jar 包被锁了

    
    
    String path = "E://spring-boot-2.0.1.RELEASE.jar";
    File file = new File( path );
    URL url = file.toURI().toURL();
    
    URLConnection uConn = url.openConnection();
    uConn.getLastModified();    // 读取jar包信息
    
    Files.delete( FileSystems.getDefault().getPath( path ) );
    

为了解决文件锁的问题，tomcat 禁用了 `URLConnection` 的缓存，是在 `JreMemoryLeakPreventionListener`
中完成的，关键代码如下所示：

    
    
    // dummy.jar 不存在也没有关系
    URL url = new URL("jar:file://dummy.jar!/");
    URLConnection uConn = url.openConnection();
    uConn.setDefaultUseCaches(false);
    

可能有些童鞋会有疑问，tomcat 只是针对该 `URLConnection` 对象禁用了缓存，而其它的 `URLConnection`
资源缓存未必被禁用啊。答案是肯定的，因为 `URLConnection` 的 `defaultUseCaches` 属性是静态变量

### 类加载器泄露

其中一种 JRE 内存泄露是因为上下文类加载器导致的内存泄露。某些 JRE 库以单例的形式存在，它的生命周期很长甚至会贯穿于整个 java
程序，它们会使用上下文类加载器加载类，并且保留了类加载器的引用，所以会导致被引用的类加载器无法被回收，而 tomcat 重加载 webapp
是创建一个新的类加载器来实现的，旧的类加载器无法被 gc 回收，致使其加载的 Class 也无法被回收，导致内存泄露。

`DriverManager` 就是典型的例子，它利用 jdk 提供的 SPI 机制加载 `java.sql.Driver` 驱动，而 jdk 提供的
SPI 机制便是使用上下文类加载器加载 Class 的，如果这类 jdbc 驱动由 `ParallelWebappClassLoader`
类加载器加载的话，就会导致该 `ClassLoder` 无法被回收，自然会出现内存泄露

我们来看看 tomcat 是怎么解决的？tomcat 是利用 `LifecycleListener` 处理 `before_init`
事件，将上下文类加载器置为系统类加载器，并且完成驱动的加载过程，最后，为了不影响其它的类加载，再将上下文类加载器重置为
`ParallelWebappClassLoader`

另外一种 JRE
内存泄露是因为当前线程会启动另外一个线程，这个时候新线程会引用当前线程的上下文类加载器，如果新线程无止尽地运行，那么上下文类加载器就会一直被引用，而无法被回收，导致内存泄露。`sun.awt.AppContext.getAppContext()`
便是典型的例子，它会在内部开启一个 `AWT-AppKit` 线程，直到图形化环境准备就绪，例如
`ImageIO.getCacheDirectory()`、`java.awt.Toolkit.getDefaultToolkit()`

![image](https://gitee.com/chenssy/blog-home/raw/master/image/201809/jre-
memory-leak-thread.png)

针对这种情况，解决思路也是一样的，只需要将当前上下文类加载器指定为系统类加载器即可，关键代码如下所示：

    
    
    JreMemoryLeakPreventionListener.java
    
    @Override
    public void lifecycleEvent(LifecycleEvent event) {
        if (Lifecycle.BEFORE_INIT_EVENT.equals(event.getType())) {
            ClassLoader loader = Thread.currentThread().getContextClassLoader();
            try {
                // 当线程上下文类加载器指定为系统类加载器
                Thread.currentThread().setContextClassLoader(ClassLoader.getSystemClassLoader());
                if (driverManagerProtection) {
                    DriverManager.getDrivers();
                }
                // 避免开启的子线程持有 ParallelWebappClassLoader 引用
                if (appContextProtection && !JreCompat.isJre8Available()) {
                    ImageIO.getCacheDirectory();
                }
                if (awtThreadProtection && !JreCompat.isJre9Available()) {
                    java.awt.Toolkit.getDefaultToolkit();
                }
                // 避免持有 ParallelWebappClassLoader 引用
                if (tokenPollerProtection && !JreCompat.isJre9Available()) {
                    java.security.Security.getProviders();
                }
                // 忽略若干代码......
            } finally {
                // 再重置为 ParallelWebappClassLoader，避免影响其它的类的加载
                Thread.currentThread().setContextClassLoader(loader);
            }
        }
    }
    

### ThreadLocal 对象泄露

还有一种内存泄露是由于 `ThreadLocal` 引起的，假如我们在 `ThreadLocal` 中保存了对象A，而且对象A由
`ParallelWebappClassLoader` 加载，那么就可以看成线程引用了对象A。由于 tomcat
中处理请求的是线程池，意味着该线程会存活很长一段时间。webapp 热加载时，会重新实例化一个 `ParallelWebappClassLoader`
对象，如果线程未销毁，那么旧的 `ParallelWebappClassLoader` 也无法被回收，导致内存泄露。

解决 `ThreadLocal`
内存泄露最好的办法，自然是把线程池中的所有的线程销毁并重新创建。这个过程分为两步，第一步是将任务队列堵住，不让新的任务进来，第二步是将线程池中所有线程停止。

tomcat 解决该 ThreadLocal 对象泄露问题，也是借助了 `Lifecycle` 完成的，具体的实现类是
`ThreadLocalLeakPreventionListener`，它会处理 `Lifecycle.AFTER_STOP_EVENT`
事件，并且销毁线程池内的空闲线程，关键代码如下所示：

    
    
    ThreadLocalLeakPreventionListener.java
    
    @Override
    public void lifecycleEvent(LifecycleEvent event) {
        Lifecycle lifecycle = event.getLifecycle();
        if (Lifecycle.AFTER_STOP_EVENT.equals(event.getType()) &&
                lifecycle instanceof Context) {
            stopIdleThreads((Context) lifecycle);
        }
    }
    
    private void stopIdleThreads(Context context) {
        Engine engine = (Engine) context.getParent().getParent();
        Service service = engine.getService();
        Connector[] connectors = service.findConnectors();
        if (connectors != null) {
            for (Connector connector : connectors) {
                ProtocolHandler handler = connector.getProtocolHandler();
                Executor executor = null;
                if (handler != null) {
                    executor = handler.getExecutor();
                }
                // 销毁线程池 ThreadPoolExecutor，首先将任务队列设为 0，再设置coreSize为0（会触发线程池内线程的interrupt），从而销毁空闲的线程
                if (executor instanceof ThreadPoolExecutor) {
                    ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) executor;
                    threadPoolExecutor.contextStopping();
                } else if (executor instanceof StandardThreadExecutor) {
                    StandardThreadExecutor stdThreadExecutor = (StandardThreadExecutor) executor;
                    stdThreadExecutor.contextStopping();
                }
            }
        }
    }
    

