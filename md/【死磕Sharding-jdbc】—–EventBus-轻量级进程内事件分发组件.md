  * 1 使用参考
    * 1.1 核心方法
  * 2 源码分析
    * 2.1 发布源码分析
    * 2.2 订阅源码分析

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/891fa8cb1540>

* * *

**EventBus** 来自于 **google-guava** 包中。源码注释如下：

> Dispatches events to listeners, and provides ways for listeners to register
themselves.  
>  The EventBus allows publish-subscribe-style communication between
components  
>  without requiring the components to explicitly register with one another
(and thus be  
>  aware of each other). It is designed exclusively to replace traditional
Java in-process  
>  event distribution using explicit registration. It is not a general-purpose
publish-subscribe  
>  system, nor is it intended for interprocess communication.

翻译：将事件分派给监听器，并为监听器提供注册自己的方法。 **EventBus** 允许组件之间的发布 –
订阅式通信，而不需要组件彼此明确注册（并且因此彼此意识到）。 它专门用于使用显式注册替换传统的Java进程内事件分发。 它不是一个通用的发布 –
订阅系统，也不是用于进程间通信。

# 使用参考

关于EventBus的用例代码提取自sharding-jdbc源码，并结合lombok最大限度的简化：

  * EventBusInstance–用于获取EventBus实例（饿汉式单例模式）

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class EventBusInstance {
    
        private static final EventBus INSTANCE = new EventBus();
    
        public static EventBus getInstance() {
            return INSTANCE;
        }
    }
    

  * DMLExecutionEvent–发布订阅事件模型

    
    
    @Getter
    @Setter
    public class DMLExecutionEvent {
        private String id;
        private String dataSource;
        private Date sendTime;
    }
    

  * DMLExecutionEventListener–事件监听器

    
    
    public final class DMLExecutionEventListener {
    
        @Subscribe
        @AllowConcurrentEvents
        public void listener(final DMLExecutionEvent event) {
            System.out.println("监听的DML执行事件: " + JSON.toJSONString(event));
            // do something
        }
    }
    

— Main–主方法：注册订阅者监听事件，以及发布事件。

    
    
    /**
     * @author wangzhenfei9
     * @version 1.0.0
     * @since 2018年04月24日
     */
    public class Main {
    
        static{
            System.out.println("register listener...");
            EventBusInstance.getInstance().register(new DMLExecutionEventListener());
        }
    
        public static void main(String[] args) throws InterruptedException {
    
            for (int i=0; i<10; i++) {
                pub();
                Thread.sleep(3000);
            }
        }
    
        private static void pub(){
            DMLExecutionEvent event = new DMLExecutionEvent();
            event.setId(String.valueOf(new Random().nextInt(1000)));
            event.setDataSource("sj_db_1");
            event.setSendTime(new Date());
            System.out.println("发布的DML执行事件: " + JSON.toJSONString(event));
            EventBusInstance.getInstance().post(event);
        }
    }
    

## 核心方法

EventBus一些重要方法解释如下：

  * **post(Object)** ：Posts an event to all registered subscribers. This method will return successfully after the event has been posted to all subscribers, and regardless of any exceptions thrown by subscribers.
  * **register(Object)** : Registers all subscriber methods on object to receive events.Subscriber methods are selected and classified using this EventBus’s SubscriberFindingStrategy; the default strategy is the AnnotatedSubscriberFinder.
  * **unregister(Object)** ：Unregisters all subscriber methods on a registered object.

# 源码分析

主要分析发布事件以及订阅的核心源码；

## 发布源码分析

    
    
    public void post(Object event) {
        // 得到所有该类已经它的所有父类（因为有些注册监听器是监听其父类）
        Set<Class<?>> dispatchTypes = flattenHierarchy(event.getClass());
    
        boolean dispatched = false;
        // 遍历类本身以及所有父类
        for (Class<?> eventType : dispatchTypes) {
            // 重入读锁先锁住
            subscribersByTypeLock.readLock().lock();
            try {
                // 得到类的所有订阅者，例如DMLExecutionEvent的订阅者就是DMLExecutionEventListener（EventSubscriber有两个属性：重要的属性target和method，target就是监听器即DMLExecutionEventListener，method就是监听器方法即listener；从而知道DMLExecutionEvent这个事件由哪个类的哪个方法监听处理）
                Set<EventSubscriber> wrappers = subscribersByType.get(eventType);
    
                if (!wrappers.isEmpty()) {
                    // 如果有时间订阅者，那么dispatched = true，表示该事件可以分发
                    dispatched = true;
                    // 遍历所有的时间订阅者，每个订阅者的队列都增加该事件
                    for (EventSubscriber wrapper : wrappers) {
                        enqueueEvent(event, wrapper);
                    }
                }
            } finally {
                subscribersByTypeLock.readLock().unlock();
            }
        }
    
        if (!dispatched && !(event instanceof DeadEvent)) {
            post(new DeadEvent(this, event));
        }
    
        // 分发进入队列的事件
        dispatchQueuedEvents();
    }
    
    /** 
     * queues of events for the current thread to dispatch;
     * 核心数据结构为LinkedList，保存的是EventBus.EventWithSubscriber类型数据
     */
    private final ThreadLocal<Queue<EventBus.EventWithSubscriber>> eventsToDispatch =
            new ThreadLocal<Queue<EventBus.EventWithSubscriber>>() {
                @Override protected Queue<EventBus.EventWithSubscriber> initialValue() {
                    return new LinkedList<EventBus.EventWithSubscriber>();
                }
            };
    
    void enqueueEvent(Object event, EventSubscriber subscriber) {
        // 数据结构为new LinkedList<EventWithSubscriber>()，EventWithSubscriber就是对event和subscriber的封装，LinkedList数据结构保证进入队列和消费队列顺序一致
        eventsToDispatch.get().offer(new EventBus.EventWithSubscriber(event, subscriber));
    }
    
    /**
     * Drain the queue of events to be dispatched. As the queue is being drained,
     * new events may be posted to the end of the queue. 
     * 排干要被分发的事件队列，正在排干的过程中，可能有新的事件被追加到队列尾部
     */
    void dispatchQueuedEvents() {
        // don"t dispatch if we"re already dispatching, that would allow reentrancy
        // and out-of-order events. Instead, leave the events to be dispatched
        // after the in-progress dispatch is complete.
        // 如果正在排干队列，则不分发
        if (isDispatching.get()) {
            return;
        }
    
        // ThreadLocal设置正在分发即isDispatching为true
        isDispatching.set(true);
        try {
            Queue<EventBus.EventWithSubscriber> events = eventsToDispatch.get();
            EventBus.EventWithSubscriber eventWithSubscriber;
            while ((eventWithSubscriber = events.poll()) != null) {
                // 调用订阅者处理事件（method.invoke(target, new Object[] { event });，method和target来自订阅者）
                dispatch(eventWithSubscriber.event, eventWithSubscriber.subscriber);
            }
        } finally {
            // ThreadLocal可能内存泄漏，用完需要remove
            isDispatching.remove();
            // 队列中的事件任务处理完，清空队列，即所谓的排干（Drain）
            eventsToDispatch.remove();
        }
    }
    

## 订阅源码分析

“`  
/**  
* Registers all subscriber methods on {@code object} to receive events.  
* 注册object上所有订阅方法，用来接收事件，上面的使用参考，DMLExecutionEventListener就是这里的object  
*/  
public void register(Object object) {  
// Multimap是guava自定义数据结构，类似Map<K,
Collection>，key就是事件类型，例如DMLExecutionEvent，value就是EventSubscriber即事件订阅者集合（说明，这个的订阅者集合是指object里符合订阅者的所有方法，例如DMLExecutionEventListener.listener()，DMLExecutionEventListener中可以有多个订阅者，注解@Subscribe即可），  
Multimap<Class, EventSubscriber> methodsInListener =  
finder.findAllSubscribers(object);  
// 重入写锁保证线程安全  
subscribersByTypeLock.writeLock().lock();  
try {  
// 把订阅者信息放到map中缓存起来（发布事件post()时就会用到）  
subscribersByType.putAll(methodsInListener);  
} finally {  
subscribersByTypeLock.writeLock().unlock();  
}  
}  
“

