    * 0.1 tomcat session 设计分析
  * 1 创建Session
    * 1.1 Session清理
      * 1.1.1 Background 线程
      * 1.1.2 Session 检查
      * 1.1.3 清理过期 Session
    * 1.2 HttpSessionListener
      * 1.2.1 创建通知
      * 1.2.2 销毁通知

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79328151>

在 web 开发中，我们经常会用到 Session 来保存会话信息，包括用户信息、权限信息，等等。在这篇文章中，我们将分析 tomcat 容器是如何创建
session、销毁 session，又是如何对 HttpSessionListener 进行事件通知

## tomcat session 设计分析

tomcat session 组件图如下所示，其中 `Context` 对应一个 webapp 应用，每个 webapp 有多个
`HttpSessionListener`， 并且每个应用的 session 是独立管理的，而 session 的创建、销毁由 `Manager`
组件完成，它内部维护了 N 个 `Session` 实例对象。在前面的文章中，我们分析了 `Context` 组件，它的默认实现是
`StandardContext`，它与 `Manager` 是一对一的关系，`Manager` 创建、销毁会话时，需要借助
`StandardContext` 获取 `HttpSessionListener` 列表并进行事件通知，而 `StandardContext`
的后台线程会对 `Manager` 进行过期 Session 的清理工作

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180327173127949.png)

`org.apache.catalina.Manager` 接口的主要方法如下所示，它提供了
`Context`、`org.apache.catalina.SessionIdGenerator`的 getter/setter
接口，以及创建、添加、移除、查找、遍历 `Session` 的 API 接口，此外还提供了 `Session` 持久化的接口（load/unload）
用于加载/卸载会话信息，当然持久化要看不同的实现类

    
    
    public interface Manager {
        public Context getContext();
        public void setContext(Context context);
        public SessionIdGenerator getSessionIdGenerator();
        public void setSessionIdGenerator(SessionIdGenerator sessionIdGenerator);
        public void add(Session session);
        public void addPropertyChangeListener(PropertyChangeListener listener);
        public void changeSessionId(Session session);
        public void changeSessionId(Session session, String newId);
        public Session createEmptySession();
        public Session createSession(String sessionId);
        public Session findSession(String id) throws IOException;
        public Session[] findSessions();
        public void remove(Session session);
        public void remove(Session session, boolean update);
        public void removePropertyChangeListener(PropertyChangeListener listener);
        public void unload() throws IOException;
        public void backgroundProcess();
        public boolean willAttributeDistribute(String name, Object value);
    }
    

tomcat8.5 提供了 4 种实现，默认使用 `StandardManager`，tomcat
还提供了集群会话的解决方案，但是在实际项目中很少运用，关于 `Manager` 的详细配置信息请参考 [tomcat
官方文档](http://tomcat.apache.org/tomcat-8.5-doc/config/manager.html)

  * StandardManager：Manager 默认实现，在内存中管理 session，宕机将导致 session 丢失；但是当调用 Lifecycle 的 start/stop 接口时，将采用 jdk 序列化保存 Session 信息，因此当 tomcat 发现某个应用的文件有变更进行 reload 操作时，这种情况下不会丢失 Session 信息
  * DeltaManager：增量 Session 管理器，用于Tomcat集群的会话管理器，某个节点变更 Session 信息都会同步到集群中的所有节点，这样可以保证 Session 信息的实时性，但是这样会带来较大的网络开销
  * BackupManager：用于 Tomcat 集群的会话管理器，与DeltaManager不同的是，某个节点变更 Session 信息的改变只会同步给集群中的另一个 backup 节点
  * PersistentManager：当会话长时间空闲时，将会把 Session 信息写入磁盘，从而限制内存中的活动会话数量；此外，它还支持容错，会定期将内存中的 Session 信息备份到磁盘

Session 相关的类图如下所示，`StandardSession` 同时实现了
`javax.servlet.http.HttpSession`、`org.apache.catalina.Session` 接口，并且对外提供的是
`StandardSessionFacade` 外观类，保证了 `StandardSession` 的安全，避免开发人员调用其内部方法进行不当操作。而
`org.apache.catalina.connector.Request` 实现了
`javax.servlet.http.HttpServletRequest` 接口，它持有 `StandardSession` 的引用，对外也是暴露
`RequestFacade` 外观类。而 `StandardManager` 内部维护了其创建的
`StandardSession`，是一对多的关系，并且持有 `StandardContext` 的引用，而 `StandardContext` 内部注册了
webapp 所有的 `HttpSessionListener` 实例。

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180329001709330.png)

# 创建Session

我们以 `HttpServletRequest#getSession()` 作为切入点，对 Session 的创建过程进行分析

    
    
    public class SessionExample extends HttpServlet {
        public void doGet(HttpServletRequest request, HttpServletResponse response)
            throws IOException, ServletException  {
            HttpSession session = request.getSession();
            // other code......
        }
    }
    

整个流程图如下图所示([查看原图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180327220204647))：

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180327220204647.png)

tomcat 创建 session 的流程如上图所示，我们的应用程序拿到的 `HttpServletRequest` 是
`org.apache.catalina.connector.RequestFacade`(除非某些 Filter 进行了特殊处理)，它是
`org.apache.catalina.connector.Request` 的门面模式。首先，会判断 `Request` 对象中是否存在
`Session`，如果存在并且未失效则直接返回，因为在 tomcat 中 `Request`
对象是被重复利用的，只会替换部分组件，所以会进行这步判断。此时，如果不存在 `Session`，则尝试根据 `requestedSessionId` 查找
`Session`，而该 `requestedSessionId` 会在 HTTP Connector 中进行赋值（如果存在的话），如果存在
`Session` 的话则直接返回，如果不存在的话，则创建新的 `Session`，并且把 `sessionId` 添加到 `Cookie`
中，后续的请求便会携带该 `Cookie`，这样便可以根据 `Cookie` 中的`sessionId` 找到原来创建的 `Session` 了

在上面的过程中，`Session` 的查找、创建都是由 `Manager` 完成的，下面我们分析下 `StandardManager` 创建
`Session` 的具体逻辑。首先，我们来看下 `StandardManager` 的类图，它也是个 `Lifecycle` 组件，并且
`ManagerBase` 实现了主要的逻辑。

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180328001557765.png)

整个创建 `Session` 的过程比较简单，就是实例化 `StandardSession` 对象并设置其基本属性，以及生成唯一的
`sessionId`，其次就是记录创建时间，关键代码如下所示：

    
    
    public Session createSession(String sessionId) {
    
        // 限制 session 数量，默认不做限制，maxActiveSessions = -1
        if ((maxActiveSessions >= 0) &&
                (getActiveSessions() >= maxActiveSessions)) {
            rejectedSessions++;
            throw new TooManyActiveSessionsException(sm.getString("managerBase.createSession.ise"), maxActiveSessions);
        }
    
        // 创建 StandardSession 实例，子类可以重写该方法
        Session session = createEmptySession();
    
        // 设置属性，包括创建时间，最大失效时间
        session.setNew(true);
        session.setValid(true);
        session.setCreationTime(System.currentTimeMillis());
    
        // 设置最大不活跃时间(单位s)，如果超过这个时间，仍然没有请求的话该Session将会失效
        session.setMaxInactiveInterval(getContext().getSessionTimeout() * 60);
        String id = sessionId;
        if (id == null) {
            id = generateSessionId();
        }
        session.setId(id);
        sessionCounter++;   // 这个地方不是线程安全的，可能当时开发人员认为计数器不要求那么准确
    
        // 将创建时间添加到LinkedList中，并且把最先添加的时间移除，主要还是方便清理过期session
        SessionTiming timing = new SessionTiming(session.getCreationTime(), 0);
        synchronized (sessionCreationTiming) {
            sessionCreationTiming.add(timing);
            sessionCreationTiming.poll();
        }
        return (session);
    }
    

在 tomcat 中是可以限制 session 数量的，如果需要限制，请指定 `Manager` 的 `maxActiveSessions`
参数，默认不做限制，不建议进行设置，但是如果存在恶意攻击，每次请求不携带 `Cookie` 就有可能会频繁创建 `Session`，导致 `Session`
对象爆满最终出现 OOM。另外 `sessionId` 采用随机算法生成，并且每次生成都会判断当前是否已经存在该 id，从而避免 `sessionId`
重复。而 `StandardManager` 是使用 `ConcurrentHashMap` 存储 session 对象的，`sessionId` 作为
key，`org.apache.catalina.Session` 作为 value。此外，值得注意的是 `StandardManager` 创建的是
tomcat 的 `org.apache.catalina.session.StandardSession`，同时他也实现了 servlet 的
`HttpSession`，但是为了安全起见，tomcat 并不会把这个 `StandardSession` 直接交给应用程序，因此需要调用
`org.apache.catalina.Session#getSession()` 获取 `HttpSession`。

我们再来看看 `StandardSession` 的内部结构

  * attributes：使用 ConcurrentHashMap 解决多线程读写的并发问题
  * creationTime：Session 的创建时间
  * expiring：用于标识 Session 是否过期
  * expiring：用于标识 Session 是否过期
  * lastAccessedTime：上一次访问的时间，用于计算 Session 的过期时间
  * maxInactiveInterval：Session 的最大存活时间，如果超过这个时间没有请求，Session 就会被清理、
  * listeners：这是 tomcat 的 SessionListener，并不是 servlet 的 HttpSessionListener
  * facade：HttpSession 的外观模式，应用程序拿到的是该对象

    
    
    public class StandardSession implements HttpSession, Session, Serializable {
        protected ConcurrentMap<String, Object> attributes = new ConcurrentHashMap<>();
        protected long creationTime = 0L;
        protected transient volatile boolean expiring = false;
        protected transient StandardSessionFacade facade = null;
        protected String id = null;
        protected volatile long lastAccessedTime = creationTime;
        protected transient ArrayList<SessionListener> listeners = new ArrayList<>();
        protected transient Manager manager = null;
        protected volatile int maxInactiveInterval = -1;
        protected volatile boolean isNew = false;
        protected volatile boolean isValid = false;
        protected transient Map<String, Object> notes = new Hashtable<>();
        protected transient Principal principal = null;
    }
    

## Session清理

### Background 线程

前面我们分析了 Session 的创建过程，而 Session 会话是有时效性的，下面我们来看下 tomcat
是如何进行失效检查的。在分析之前，我们先回顾下 `Container` 容器的 Background 线程。

tomcat 所有容器组件，都是继承至 `ContainerBase` 的，包括
`StandardEngine`、`StandardHost`、`StandardContext`、`StandardWrapper`，而
`ContainerBase` 在启动的时候，如果 `backgroundProcessorDelay` 参数大于 0 则会开启
`ContainerBackgroundProcessor` 后台线程，调用自己以及子容器的 `backgroundProcess`
进行一些后台逻辑的处理，和 `Lifecycle`
一样，这个动作是具有传递性的，也就是说子容器还会把这个动作传递给自己的子容器，如下图所示，其中父容器会遍历所有的子容器并调用其
`backgroundProcess` 方法，而 `StandardContext` 重写了该方法，它会调用
`StandardManager#backgroundProcess()` 进而完成 Session 的清理工作。看到这里，不得不感慨 tomcat 的责任

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180328132003352.png)

关键代码如下所示：

    
    
    ContainerBase.java(省略了异常处理代码)
    
    protected synchronized void startInternal() throws LifecycleException {
        // other code......
        // 开启ContainerBackgroundProcessor线程用于处理子容器，默认情况下backgroundProcessorDelay=-1，不会启用该线程
        threadStart();
    }
    
    protected class ContainerBackgroundProcessor implements Runnable {
        public void run() {
            // threadDone 是 volatile 变量，由外面的容器控制
            while (!threadDone) {
                try {
                    Thread.sleep(backgroundProcessorDelay * 1000L);
                } catch (InterruptedException e) {
                    // Ignore
                }
                if (!threadDone) {
                    processChildren(ContainerBase.this);
                }
            }
        }
    
        protected void processChildren(Container container) {
            container.backgroundProcess();
            Container[] children = container.findChildren();
            for (int i = 0; i < children.length; i++) {
                // 如果子容器的 backgroundProcessorDelay 参数小于0，则递归处理子容器
                // 因为如果该值大于0，说明子容器自己开启了线程处理，因此父容器不需要再做处理
                if (children[i].getBackgroundProcessorDelay() <= 0) {
                    processChildren(children[i]);
                }
            }
        }
    }
    

### Session 检查

`backgroundProcessorDelay` 参数默认值为 `-1`，单位为秒，即默认不启用后台线程，而 tomcat 的 Container
容器需要开启线程处理一些后台任务，比如监听 jsp 变更、tomcat 配置变动、Session 过期等等，因此 `StandardEngine`
在构造方法中便将 `backgroundProcessorDelay` 参数设为 10（当然可以在 `server.xml` 中指定该参数），即每隔 10s
执行一次。那么这个线程怎么控制生命周期呢？我们注意到 `ContainerBase` 有个 `threadDone` 变量，用 `volatile`
修饰，如果调用 Container 容器的 stop 方法该值便会赋值为
false，那么该后台线程也会退出循环，从而结束生命周期。另外，有个地方需要注意下，父容器在处理子容器的后台任务时，需要判断子容器的
`backgroundProcessorDelay` 值，只有当其小于等于 0
才进行处理，因为如果该值大于0，子容器自己会开启线程自行处理，这时候父容器就不需要再做处理了

前面分析了容器的后台线程是如何调度的，下面我们重点来看看 webapp 这一层，以及 `StandardManager`
是如何清理过期会话的。`StandardContext` 重写了 `backgroundProcess`
方法，除了对子容器进行处理之外，还会对一些缓存信息进行清理，关键代码如下所示：

    
    
    StandardContext.java
    
    @Override
    public void backgroundProcess() {
        if (!getState().isAvailable())
            return;
        // 热加载 class，或者 jsp
        Loader loader = getLoader();
        if (loader != null) {
            loader.backgroundProcess();
        }
        // 清理过期Session
        Manager manager = getManager();
        if (manager != null) {
            manager.backgroundProcess();
        }
        // 清理资源文件的缓存
        WebResourceRoot resources = getResources();
        if (resources != null) {
            resources.backgroundProcess();
        }
        // 清理对象或class信息缓存
        InstanceManager instanceManager = getInstanceManager();
        if (instanceManager instanceof DefaultInstanceManager) {
            ((DefaultInstanceManager)instanceManager).backgroundProcess();
        }
        // 调用子容器的 backgroundProcess 任务
        super.backgroundProcess();
    }
    

`StandardContext` 重写了 `backgroundProcess` 方法，在调用子容器的后台任务之前，还会调用
`Loader`、`Manager`、`WebResourceRoot`、`InstanceManager` 的后台任务，这里我们只关心 `Manager`
的后台任务。弄清楚了 `StandardManager` 的来龙去脉之后，我们接下来分析下具体的逻辑。

`StandardManager` 继承至 `ManagerBase`，它实现了主要的逻辑，关于 Session
清理的代码如下所示。backgroundProcess 默认是每隔10s调用一次，但是在 `ManagerBase` 做了取模处理，默认情况下是 60s
进行一次 Session 清理。tomcat 对 Session 的清理并没有引入时间轮，因为对 Session 的时效性要求没有那么精确，而且除了通知
`SessionListener`。

    
    
    ManagerBase.java
    
    public void backgroundProcess() {
        // processExpiresFrequency 默认值为 6，而backgroundProcess默认每隔10s调用一次，也就是说除了任务执行的耗时，每隔 60s 执行一次
        count = (count + 1) % processExpiresFrequency;
        if (count == 0) // 默认每隔 60s 执行一次 Session 清理
            processExpires();
    }
    
    /**
     * 单线程处理，不存在线程安全问题
     */
    public void processExpires() {
        long timeNow = System.currentTimeMillis();
        Session sessions[] = findSessions();    // 获取所有的 Session
        int expireHere = 0 ;
        for (int i = 0; i < sessions.length; i++) {
            // Session 的过期是在 isValid() 里面处理的
            if (sessions[i]!=null && !sessions[i].isValid()) {
                expireHere++;
            }
        }
        long timeEnd = System.currentTimeMillis();
        // 记录下处理时间
        processingTime += ( timeEnd - timeNow );
    }
    

### 清理过期 Session

在上面的代码，我们并没有看到太多的过期处理，只是调用了 `sessions[i].isValid()`，原来清理动作都在这个方法里面处理的，相当的隐晦。在
`StandardSession#isValid()` 方法中，如果 `now - thisAccessedTime >=
maxInactiveInterval`则判定当前 Session 过期了，而这个 `thisAccessedTime` 参数在每次访问都会进行更新

    
    
    public boolean isValid() {
        // other code......
        // 如果指定了最大不活跃时间，才会进行清理，这个时间是 Context.getSessionTimeout()，默认是30分钟
        if (maxInactiveInterval > 0) {
            int timeIdle = (int) (getIdleTimeInternal() / 1000L);
            if (timeIdle >= maxInactiveInterval) {
                expire(true);
            }
        }
        return this.isValid;
    }
    

而 `expire` 方法处理的逻辑较繁锁，下面我用伪代码简单地描述下核心的逻辑，由于这个步骤可能会有多线程进行操作，因此使用 `synchronized`
对当前 Session 对象加锁，还做了双重校验，避免重复处理过期 Session。它还会向 Container 容器发出事件通知，还会调用
`HttpSessionListener` 进行事件通知，这个也就是我们 web 应用开发的 `HttpSessionListener` 了。由于
`Manager` 中维护了 `Session` 对象，因此还要将其从 `Manager` 移除。Session
最重要的功能就是存储数据了，可能存在强引用，而导致 Session 无法被 gc 回收，因此还要移除内部的 key/value 数据。由此可见，tomcat
编码的严谨性了，稍有不慎将可能出现并发问题，以及出现内存泄露

    
    
    public void expire(boolean notify) {
        1、校验 isValid 值，如果为 false 直接返回，说明已经被销毁了
        synchronized (this) {   // 加锁
            2、双重校验 isValid 值，避免并发问题
            Context context = manager.getContext();
            if (notify) {   
                Object listeners[] = context.getApplicationLifecycleListeners();
                HttpSessionEvent event = new HttpSessionEvent(getSession());
                for (int i = 0; i < listeners.length; i++) {
                3、判断是否为 HttpSessionListener，不是则继续循环
                4、向容器发出Destory事件，并调用 HttpSessionListener.sessionDestroyed() 进行通知
                context.fireContainerEvent("beforeSessionDestroyed", listener);
                listener.sessionDestroyed(event);
                context.fireContainerEvent("afterSessionDestroyed", listener);
            }
            5、从 manager 中移除该  session
            6、向 tomcat 的 SessionListener 发出事件通知，非 HttpSessionListener
            7、清除内部的 key/value，避免因为强引用而导致无法回收 Session 对象
        }
    }
    

由前面的分析可知，tomcat 会根据时间戳清理过期 Session，那么 tomcat 又是如何更新这个时间戳呢？我们在
`StandardSession#thisAccessedTime` 的属性上面打个断点，看下调用栈。原来 tomcat 在处理完请求之后，会对
`Request` 对象进行回收，并且会对 Session 信息进行清理，而这个时候会更新
`thisAccessedTime`、`lastAccessedTime` 时间戳。此外，我们通过调用 `request.getSession()` 这个
API 时，在返回 Session 时会调用 `Session#access()` 方法，也会更新 `thisAccessedTime`
时间戳。这样一来，每次请求都会更新时间戳，可以保证 Session 的鲜活时间

方法调用栈如下所示：

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180328200150936.png)

关键代码如下所示：

    
    
    org.apache.catalina.connector.Request.java
    
    protected void recycleSessionInfo() {
        if (session != null) {  
            session.endAccess();    // 更新时间戳
        }
        // 回收 Request 对象的内部信息
        session = null;
        requestedSessionCookie = false;
        requestedSessionId = null;
        requestedSessionURL = false;
        requestedSessionSSL = false;
    }
    

org.apache.catalina.session.StandardSession.java

    
    
    public void endAccess() {
        isNew = false;
        if (LAST_ACCESS_AT_START) {     // 可以通过系统参数改变该值，默认为false
            this.lastAccessedTime = this.thisAccessedTime;
            this.thisAccessedTime = System.currentTimeMillis();
        } else {
            this.thisAccessedTime = System.currentTimeMillis();
            this.lastAccessedTime = this.thisAccessedTime;
        }
    }
    
    public void access() {
        this.thisAccessedTime = System.currentTimeMillis();
    }
    

## HttpSessionListener

### 创建通知

前面我们分析了 `Session` 的创建过程，但是在整个创建流程中，似乎没有看到关于 `HttpSessionListener` 的创建通知。原来，在给
Session 设置 id 的时候会进行事件通知，和 Session 的销毁一样，也是非常的隐晦，个人感觉这一块设计得不是很合理。

创建通知这块的逻辑很简单，首先创建 `HttpSessionEvent` 对象，然后遍历 Context 内部的
LifecycleListener，并且判断是否为 `HttpSessionListener` 实例，如果是的话则调用
`HttpSessionListener#sessionCreated()` 方法进行事件通知。

    
    
    public void setId(String id, boolean notify) {
        // 省略部分代码
        if (notify) {
            tellNew();
        }
    }
    
    public void tellNew() {
    
        // 通知 org.apache.catalina.SessionListener
        fireSessionEvent(Session.SESSION_CREATED_EVENT, null);
    
        // 获取 Context 内部的 LifecycleListener，并判断是否为 HttpSessionListener
        Context context = manager.getContext();
        Object listeners[] = context.getApplicationLifecycleListeners();
        if (listeners != null && listeners.length > 0) {
            HttpSessionEvent event = new HttpSessionEvent(getSession());
            for (int i = 0; i < listeners.length; i++) {
                if (!(listeners[i] instanceof HttpSessionListener))
                    continue;
                HttpSessionListener listener = (HttpSessionListener) listeners[i];
                context.fireContainerEvent("beforeSessionCreated", listener);   // 通知 Container 容器
                listener.sessionCreated(event);
                context.fireContainerEvent("afterSessionCreated", listener);
            }
        }
    }
    

### 销毁通知

我们在前面分析[清理过期
Session](https://blog.csdn.net/dwade_mia/article/details/79736427#session-
expire)时大致分析了 Session 销毁时会触发 `HttpSessionListener` 的销毁通知，这里不再重复了。

