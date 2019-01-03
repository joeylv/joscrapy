  * 1 Lifecycle
    * 1.1 LifecycleState
    * 1.2 LifecycleListener
  * 2 LifecycleBase
    * 2.1 start分析
  * 3 LifecycleMBeanBase

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79051417>

Lifecycle在其他框架中也很常见，比如spring，它常用于具有生命周期的组件，由Lifecycle控制组件的初始化、启动、销毁等动作，方便应用程序获取、释放某些资源，或者是触发某些特定的事件。Tomcat也是如此，在学习整个启动流程之前，我们先行了解下Lifecycle的实现机制，便于理解整个流程。

## Lifecycle

Lifecycle接口是一个公用的接口，定义了组件生命周期的一些方法，用于启动、停止Catalina组件。它是一个非常重要的接口，组件的生命周期包括：init、start、stop、destory，以及各种事件的常量、操作LifecycleListener的API，典型的观察者模式

    
    
    public interface Lifecycle {
    
        // ----------------------- 定义各种EVENT事件 -----------------------
    
        public static final String BEFORE_INIT_EVENT = "before_init";
        public static final String AFTER_INIT_EVENT = "after_init";
        public static final String START_EVENT = "start";
    
        // 省略事件常量定义……
    
        /**
         * 注册一个LifecycleListener
         */
        public void addLifecycleListener(LifecycleListener listener);
    
        /**
         * 获取所有注册的LifecycleListener
         */
        public LifecycleListener[] findLifecycleListeners();
    
        /**
         * 移除指定的LifecycleListener
         */
        public void removeLifecycleListener(LifecycleListener listener);
    
        /**
         * 组件被实例化之后，调用该方法完成初始化工作，发会出以下事件
         * <ol>
         *   <li>INIT_EVENT: On the successful completion of component initialization.</li>
         * </ol>
         * @exception LifecycleException if this component detects a fatal error
         *  that prevents this component from being used
         */
        public void init() throws LifecycleException;
    
        /**
         * 在组件投入使用之前调用该方法，先后会发出以下事件：BEFORE_START_EVENT、START_EVENT、AFTER_START_EVENT
         * @exception LifecycleException if this component detects a fatal error
         *  that prevents this component from being used
         */
        public void start() throws LifecycleException;
    
        /**
         * 使组件停止工作
         */
        public void stop() throws LifecycleException;
    
        /**
         * 销毁组件时被调用
         */
        public void destroy() throws LifecycleException;
    
        /**
         * Obtain the current state of the source component.
         */
        public LifecycleState getState();
    
        /**
         * 获取state的文字说明
         */
        public String getStateName();
    
        /**
         * Marker interface used to indicate that the instance should only be used
         * once. Calling {@link #stop()} on an instance that supports this interface
         * will automatically call {@link #destroy()} after {@link #stop()}
         * completes.
         */
        public interface SingleUse {
        }
    }
    

各大组件均实现了Lifecycle接口，类图如下所示：

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180108002044571.png)

  * LifecycleBase：它实现了Lifecycle的init、start、stop等主要逻辑，向注册在LifecycleBase内部的LifecycleListener发出对应的事件，并且预留了initInternal、startInternal、stopInternal等模板方法，便于子类完成自己的逻辑
  * MBeanRegistration：JmxEnabled 的父类， jmx框架提供的注册MBean的接口，引入此接口是为了便于使用JMX提供的管理功能
  * LifecycleMBeanBase：JmxEnabled的子类，通过重写initInternal、destroyInternal方法，统一向jmx中注册/取消注册当前实例，方便利用jmx对实例对象进行管理，代码上特别强调要求子类先行调用super.initInternal
  * ContainerBase、StandardServer、StandardService、WebappLoader、Connector、StandardContext、StandardEngine、StandardHost、StandardWrapper等容器都继承了LifecycleMBeanBase，因此这些容器都具有了同样的生命周期并可以通过JMX进行管理

tomcat允许我们使用jmx对tomcat进行监控、管理，可以使用jconsole工具，准备后续写一篇博客分析tomcat jmx

    
    
    public abstract class LifecycleMBeanBase extends LifecycleBase
            implements JmxEnabled {
    
        /**
         * Sub-classes wishing to perform additional initialization should override
         * this method, ensuring that super.initInternal() is the first call in the
         * overriding method.
         */
        protected void initInternal() throws LifecycleException {
            if (oname == null) {
                mserver = Registry.getRegistry(null, null).getMBeanServer();
                oname = register(this, getObjectNameKeyProperties());
            }
        }
    }
    
    public class Connector extends LifecycleMBeanBase  {
        protected void initInternal() throws LifecycleException {
            super.initInternal();
            adapter = new CoyoteAdapter(this);
            protocolHandler.setAdapter(adapter);
            // other code......
        }
    }
    

### LifecycleState

LifecycleState是枚举类，定义了各种状态

    
    
    public enum LifecycleState {
    
        // LifecycleBase实例化完成时的状态
        NEW(false, null),   
    
        // 容器正在初始化的状态，在INITIALIZED之前
        INITIALIZING(false, Lifecycle.BEFORE_INIT_EVENT),
    
        // 初始化完成的状态
        INITIALIZED(false, Lifecycle.AFTER_INIT_EVENT),
    
        // 启动前
        STARTING_PREP(false, Lifecycle.BEFORE_START_EVENT),
    
        // 启动过程中的状态
        STARTING(true, Lifecycle.START_EVENT),
    
        // 启动完成
        STARTED(true, Lifecycle.AFTER_START_EVENT),
    
        // 停止前的状态
        STOPPING_PREP(true, Lifecycle.BEFORE_STOP_EVENT),
    
        // 停止过程中
        STOPPING(false, Lifecycle.STOP_EVENT),
    
        // 停止完成
        STOPPED(false, Lifecycle.AFTER_STOP_EVENT),
    
        // 销毁中
        DESTROYING(false, Lifecycle.BEFORE_DESTROY_EVENT),
    
        // 完成销毁
        DESTROYED(false, Lifecycle.AFTER_DESTROY_EVENT),
    
        // 启动、停止过程中出现异常
        FAILED(false, null);
    
        private final boolean available;
        private final String lifecycleEvent;
    
        private LifecycleState(boolean available, String lifecycleEvent) {
            this.available = available;
            this.lifecycleEvent = lifecycleEvent;
        }
    
        public boolean isAvailable() {
            return available;
        }
    
        public String getLifecycleEvent() {
            return lifecycleEvent;
        }
    
    }
    

### LifecycleListener

要订阅事件的实体类需要实现LifecycleListener

    
    
    public interface LifecycleListener {
        public void lifecycleEvent(LifecycleEvent event);
    }
    

默认情况下，tomcat会内置一些LifecycleListener，配置在server.xml中，除了xml中的LifecycleListener，还有org.apache.catalina.core.NamingContextListener，而这个LifecycleListener是在StandardServer的构造器中添加的，各个LifecycleListener的作用在此不再细说。如果我们在tomcat启动、停止的时候增加额外的逻辑，比如发送邮件通知，则可以从这个地方入手

    
    
    <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
    <!--APR library loader. Documentation at /docs/apr.html -->
    <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
    <!-- Prevent memory leaks due to use of particular java/javax APIs-->
    <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
    <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
    <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />
    
    
    
    
    public StandardServer() {
        // 忽略部分代码
        if (isUseNaming()) {
            namingContextListener = new NamingContextListener();
            addLifecycleListener(namingContextListener);
        } else {
            namingContextListener = null;
        }
    }
    

## LifecycleBase

LifecycleBase实现了Lifecycle接口，完成了核心逻辑

  * StringManager：用来做日志信息参数化输出的，支持国际化 
  * 内部使用CopyOnWriteArrayList维护所有的LifecycleListener，因为在各个生命周期，内部的LifecycleListener是会变化的，并且存在并发操作问题，因此使用了并发的List。注意，不同的LifecycleBase子类，其内部的lifecycleListeners存放不同的LifecyListener，比如Server和Service，它们是不同的Lifecycle实例，内部的lifecycleListeners也是不同 
  * LifecycleBase的state初始值是LifecycleState.NEW，也存在并发修改的问题，用了volatile修饰 
  * addLifecycleListener、removeLifecycleListener允许添加、删除LifecycleListener，告诉LifecycleBase有哪些监听者需要进行事件通知 
  * fireLifecycleEvent：向内部注册的LifecycleListener发出事件通知，它是protected的方法，所以LifecycleBase的子类可以在适当的时机调用该方法发出事件通知。事件通知由LifecycleListener实现类决定要不要对特定的事件进行处理 
  * setState：更新state值，并发出对应的事件通知，同样是调用fireLifecycleEvent

    
    
    public abstract class LifecycleBase implements Lifecycle {
    
        // 日志国际化输出使用
        private static final StringManager sm = StringManager.getManager(LifecycleBase.class);
    
        // 维护LifecycleListener
        private final List<LifecycleListener> lifecycleListeners = new CopyOnWriteArrayList<>();
    
        // 初始状态是NEW
        private volatile LifecycleState state = LifecycleState.NEW;
    
        /**
         * 注册LifecycleListener
         */
        @Override
        public void addLifecycleListener(LifecycleListener listener) {
            lifecycleListeners.add(listener);
        }
    
        @Override
        public LifecycleListener[] findLifecycleListeners() {
            return lifecycleListeners.toArray(new LifecycleListener[0]);
        }
    
        /**
         * 移除LifecycleListener
         */
        @Override
        public void removeLifecycleListener(LifecycleListener listener) {
            lifecycleListeners.remove(listener);
        }
    
        /**
         * 发出事件通知，遍历内部所有的LifecycleListener，并调用其lifecycleEvent
         */
        protected void fireLifecycleEvent(String type, Object data) {
            LifecycleEvent event = new LifecycleEvent(this, type, data);
            for (LifecycleListener listener : lifecycleListeners) {
                listener.lifecycleEvent(event);
            }
        }
    
        @Override
        public LifecycleState getState() {
            return state;
        }
    
        @Override
        public String getStateName() {
            return getState().toString();
        }
    
        protected synchronized void setState(LifecycleState state)
                throws LifecycleException {
            setStateInternal(state, null, true);
        }
    
        protected synchronized void setState(LifecycleState state, Object data)
                throws LifecycleException {
            setStateInternal(state, data, true);
        }
    
        /**
         * 设置state值，并发出事件通知
         */
        private synchronized void setStateInternal(LifecycleState state,
                Object data, boolean check) throws LifecycleException {
    
            // 校验state的正确性
            if (check) {
                if (state == null) {
                    invalidTransition("null");
                    return;
                }
    
                // Any method can transition to failed
                // startInternal() permits STARTING_PREP to STARTING
                // stopInternal() permits STOPPING_PREP to STOPPING and FAILED to
                // STOPPING
                if (!(state == LifecycleState.FAILED ||
                        (this.state == LifecycleState.STARTING_PREP &&
                                state == LifecycleState.STARTING) ||
                        (this.state == LifecycleState.STOPPING_PREP &&
                                state == LifecycleState.STOPPING) ||
                        (this.state == LifecycleState.FAILED &&
                                state == LifecycleState.STOPPING))) {
                    // No other transition permitted
                    invalidTransition(state.name());
                }
            }
    
            this.state = state;
            String lifecycleEvent = state.getLifecycleEvent();
            if (lifecycleEvent != null) {
                fireLifecycleEvent(lifecycleEvent, data);
            }
        }
    
        // 省略其它代码......
    }
    

Lifecycle组件的init、start、stop、destory的套路基本上一样，先由LifecycleBase完成前期的校验、事件通知动作，再调用子类的方法完成自己的逻辑

    
    
    graph LR
    校验state-->发出事件通知
    发出事件通知-->子类doInternal</code>
    

### start分析

start过程会触发LifecycleState的STARTING_PREP、STARTED事件，如果出现启动失败还会触发FAILED事件，并且调用stop。因为会涉及多线程操作，因此对方法加了锁。如果start期间出现了异常，则会调用stop停止tomcat，或者state状态有误也会抛出异常

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180108220951024.png)

state状态变更时调用setStateInternal方法，遍历内部所有的LifecycleListener，并向其发起对应的事件通知，由LifecycleListener去完成某些动作。其子类可以直接调用fireLifecycleEvent，比如在StandardServer中，start过程会发出CONFIGURE_START_EVENT事件。注：所有事件的命名均定义在Lifecycle接口中

    
    
    public abstract class LifecycleBase implements Lifecycle {
        @Override
        public final synchronized void start() throws LifecycleException {
    
            // 如果是start前、进行中、start完成，则直接return
            if (LifecycleState.STARTING_PREP.equals(state) || LifecycleState.STARTING.equals(state) ||
                    LifecycleState.STARTED.equals(state)) {
                // 忽略logger日志
                return;
            }
    
            // 完成init初始化
            if (state.equals(LifecycleState.NEW)) {
                init();
            } else if (state.equals(LifecycleState.FAILED)) {
                stop();
            } else if (!state.equals(LifecycleState.INITIALIZED) &&
                    !state.equals(LifecycleState.STOPPED)) {
                invalidTransition(Lifecycle.BEFORE_START_EVENT);
            }
    
            try {
                // 发出STARTING_PREP事件
                setStateInternal(LifecycleState.STARTING_PREP, null, false);
    
                // 由子类实现
                startInternal();
    
                // 如果启动失败直接调用stop
                if (state.equals(LifecycleState.FAILED)) {
                    stop();
                }
                // 说明状态有误
                else if (!state.equals(LifecycleState.STARTING)) {
                    invalidTransition(Lifecycle.AFTER_START_EVENT);
                }
                // 成功完成start，发出STARTED事件
                else {
                    setStateInternal(LifecycleState.STARTED, null, false);
                }
            } catch (Throwable t) {
                ExceptionUtils.handleThrowable(t);
                setStateInternal(LifecycleState.FAILED, null, false);
                throw new LifecycleException(sm.getString("lifecycleBase.startFail", toString()), t);
            }
        }
    
        /**
         * 由子类实现
         */
        protected abstract void startInternal() throws LifecycleException;
    
    }
    

## LifecycleMBeanBase

由前面的类图可知，LifecycleMBeanBase是LifecycleBase的直接子类，并且实现了JmxEnabled接口，很多组件都是直接继承它

LifecycleMBeanBase完成了jmx注册的主要逻辑，重写了LifecycleBase的initInternal、destroyInternal方法，用于完成jmx的注册、注销动作，这两个模板方法中特别说明：

> Sub-classes wishing to perform additional initialization should override
this method,  
>  ensuring that super.initInternal() is the first call in the overriding
method.

为了保证jmx的正常注册和注销，要求子类在重写initInternal、destroyInternal方法时，必须先调用super.initInternal()。例如Connector：

    
    
    public class Connector extends LifecycleMBeanBase  {
        @Override
        protected void initInternal() throws LifecycleException {
    
            // 先行调用LifecycleMBeanBase的initInternal
            super.initInternal();
    
            // Initialize adapter
            adapter = new CoyoteAdapter(this);
            protocolHandler.setAdapter(adapter);
    
            // other code......
        }
    
        // other code......
    }
    

我们再来看看LifecycleMBeanBase的内部实现，在initInternal阶段初始化MBeanServer实例，并且把当前实例注册到jmx中；而destroyInternal阶段则是根据ObjectName注销MBean

    
    
    public abstract class LifecycleMBeanBase extends LifecycleBase
            implements JmxEnabled {
    
        /**
         * jmx的域，默认使用Service的name，即"Catalina"
         */
        private String domain = null;
    
        /**
         * 用于标识一个MBean的对象名称，也可以根据这个name来查找MBean
         */
        private ObjectName oname = null;
    
        /**
         * jmx的核心组件，提供代理端操作MBean的接口，提供了创建、注册、删除MBean的接口，它由MBeanServerFactory创建
         */
        protected MBeanServer mserver = null;
    
        @Override
        protected void initInternal() throws LifecycleException {
            if (oname == null) {
                mserver = Registry.getRegistry(null, null).getMBeanServer();
                oname = register(this, getObjectNameKeyProperties());
            }
        }
    
        @Override
        protected void destroyInternal() throws LifecycleException {
            unregister(oname);
        }
    
        protected final void unregister(ObjectName on) {
            if (on == null) {
                return;
            }
            if (mserver == null) {
                log.warn(sm.getString("lifecycleMBeanBase.unregisterNoServer", on));
                return;
            }
            try {
                mserver.unregisterMBean(on);
            } catch (MBeanRegistrationException e) {
                log.warn(sm.getString("lifecycleMBeanBase.unregisterFail", on), e);
            } catch (InstanceNotFoundException e) {
                log.warn(sm.getString("lifecycleMBeanBase.unregisterFail", on), e);
            }
    
        }
    }
    

