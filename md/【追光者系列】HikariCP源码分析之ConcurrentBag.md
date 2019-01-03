  * 1 ConcurrentBag的定义
  * 2 ConcurrentBag源码解析
  * 3 SynchronousQueue
    * 3.1 公平模式
    * 3.2 非公平模式
  * 4 CopyOnWriteArrayList
  * 5 参考资料

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

* * *

# ConcurrentBag的定义

HikariCP contains a custom lock-free collection called a ConcurrentBag. The
idea was borrowed from the C# .NET ConcurrentBag class, but the internal
implementation quite different. The ConcurrentBag provides…

  * A lock-free design
  * ThreadLocal caching
  * Queue-stealing
  * Direct hand-off optimizations

…resulting in a high degree of concurrency, extremely low latency, and
minimized occurrences of false-sharing.

<https://en.wikipedia.org/wiki/False_sharing>

  * CopyOnWriteArrayList：负责存放ConcurrentBag中全部用于出借的资源
  * ThreadLocal：用于加速线程本地化资源访问
  * SynchronousQueue：用于存在资源等待线程时的第一手资源交接

ConcurrentBag取名来源于C# .NET的同名类，但是实现却不一样。它是一个lock-
free集合，在连接池（多线程数据交互）的实现上具有比LinkedBlockingQueue和LinkedTransferQueue更优越的并发读写性能。

# ConcurrentBag源码解析

ConcurrentBag内部同时使用了ThreadLocal和CopyOnWriteArrayList来存储元素，其中CopyOnWriteArrayList是线程共享的。ConcurrentBag采用了queue-
stealing的机制获取元素：首先尝试从ThreadLocal中获取属于当前线程的元素来避免锁竞争，如果没有可用元素则扫描公共集合、再次从共享的CopyOnWriteArrayList中获取。（ThreadLocal列表中没有被使用的items在借用线程没有属于自己的时候，是可以被“窃取”的）

ThreadLocal和CopyOnWriteArrayList在ConcurrentBag中都是成员变量，线程间不共享，避免了伪共享(false
sharing)的发生。  
其使用专门的AbstractQueuedLongSynchronizer来管理跨线程信号，这是一个”lock-less“的实现。

这里要特别注意的是，ConcurrentBag中通过borrow方法进行数据资源借用，通过requite方法进行资源回收，注意其中borrow方法只提供对象引用，不移除对象。所以从bag中“借用”的items实际上并没有从任何集合中删除，因此即使引用废弃了，垃圾收集也不会发生。因此使用时
**通过borrow取出的对象必须通过requite方法进行放回，否则会导致内存泄露** ，只有”remove”方法才能完全从bag中删除一个对象。

好了，我们一起看一下ConcurrentBag源码概览：

![201805031001](http://cmsblogs.qiniudn.com/201805031001.jpeg)

上节提过，CopyOnWriteArrayList负责存放ConcurrentBag中全部用于出借的资源，就是private final
CopyOnWriteArrayList sharedList; 如下图所示，sharedList中的资源通过add方法添加，remove方法出借

![201805031002](http://cmsblogs.qiniudn.com/201805031002.jpeg)

add方法向bag中添加bagEntry对象，让别人可以借用

    
    
      /**
        * Add a new object to the bag for others to borrow.
        *
        * @param bagEntry an object to add to the bag
        */
       public void add(final T bagEntry) {
          if (closed) {
             LOGGER.info("ConcurrentBag has been closed, ignoring add()");
             throw new IllegalStateException("ConcurrentBag has been closed, ignoring add()");
          }
          sharedList.add(bagEntry);//新添加的资源优先放入CopyOnWriteArrayList
          // spin until a thread takes it or none are waiting
          // 当有等待资源的线程时，将资源交到某个等待线程后才返回（SynchronousQueue）
          while (waiters.get() > 0 && !handoffQueue.offer(bagEntry)) {
             yield();
          }
       }
    

remove方法用来从bag中删除一个bageEntry，该方法只能在borrow(long, TimeUnit)和reserve(T)时被使用

    
    
    /**
        * Remove a value from the bag.  This method should only be called
        * with objects obtained by <code>borrow(long, TimeUnit)</code> or <code>reserve(T)</code>
        *
        * @param bagEntry the value to remove
        * @return true if the entry was removed, false otherwise
        * @throws IllegalStateException if an attempt is made to remove an object
        *         from the bag that was not borrowed or reserved first
        */
       public boolean remove(final T bagEntry) {
       // 如果资源正在使用且无法进行状态切换，则返回失败
          if (!bagEntry.compareAndSet(STATE_IN_USE, STATE_REMOVED) && !bagEntry.compareAndSet(STATE_RESERVED, STATE_REMOVED) && !closed) {
             LOGGER.warn("Attempt to remove an object from the bag that was not borrowed or reserved: {}", bagEntry);
             return false;
          }
          final boolean removed = sharedList.remove(bagEntry);// 从CopyOnWriteArrayList中移出
          if (!removed && !closed) {
             LOGGER.warn("Attempt to remove an object from the bag that does not exist: {}", bagEntry);
          }
          return removed;
       }
    

ConcurrentBag中通过borrow方法进行数据资源借用

    
    
      /**
        * The method will borrow a BagEntry from the bag, blocking for the
        * specified timeout if none are available.
        *
        * @param timeout how long to wait before giving up, in units of unit
        * @param timeUnit a <code>TimeUnit</code> determining how to interpret the timeout parameter
        * @return a borrowed instance from the bag or null if a timeout occurs
        * @throws InterruptedException if interrupted while waiting
        */
       public T borrow(long timeout, final TimeUnit timeUnit) throws InterruptedException
       {
          // Try the thread-local list first
          // 优先查看有没有可用的本地化的资源
          final List<Object> list = threadList.get();
          for (int i = list.size() - 1; i >= 0; i--) {
             final Object entry = list.remove(i);
             @SuppressWarnings("unchecked")
             final T bagEntry = weakThreadLocals ? ((WeakReference<T>) entry).get() : (T) entry;
             if (bagEntry != null && bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                return bagEntry;
             }
          }
          // Otherwise, scan the shared list ... then poll the handoff queue
          final int waiting = waiters.incrementAndGet();
          try {
          // 当无可用本地化资源时，遍历全部资源，查看是否存在可用资源
          // 因此被一个线程本地化的资源也可能被另一个线程“抢走”
             for (T bagEntry : sharedList) {
                if (bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                   // If we may have stolen another waiter"s connection, request another bag add.
                   if (waiting > 1) {
                   // 因为可能“抢走”了其他线程的资源，因此提醒包裹进行资源添加
                      listener.addBagItem(waiting - 1);
                   }
                   return bagEntry;
                }
             }
             listener.addBagItem(waiting);
             timeout = timeUnit.toNanos(timeout);
             do {
                final long start = currentTime();
                // 当现有全部资源全部在使用中，等待一个被释放的资源或者一个新资源
                final T bagEntry = handoffQueue.poll(timeout, NANOSECONDS);
                if (bagEntry == null || bagEntry.compareAndSet(STATE_NOT_IN_USE, STATE_IN_USE)) {
                   return bagEntry;
                }
                timeout -= elapsedNanos(start);
             } while (timeout > 10_000);
             return null;
          }
          finally {
             waiters.decrementAndGet();
          }
       }
    
    
    
      /**
        * This method will return a borrowed object to the bag.  Objects
        * that are borrowed from the bag but never "requited" will result
        * in a memory leak.
        *
        * @param bagEntry the value to return to the bag
        * @throws NullPointerException if value is null
        * @throws IllegalStateException if the bagEntry was not borrowed from the bag
        */
       public void requite(final T bagEntry) {
       // 将状态转为未在使用
          bagEntry.setState(STATE_NOT_IN_USE);
    // 判断是否存在等待线程，若存在，则直接转手资源
          for (int i = 0; waiters.get() > 0; i++) {
             if (bagEntry.getState() != STATE_NOT_IN_USE || handoffQueue.offer(bagEntry)) {
                return;
             }
             else if ((i & 0xff) == 0xff) {
                parkNanos(MICROSECONDS.toNanos(10));
             }
             else {
                yield();
             }
          }
     // 否则，进行资源本地化
          final List<Object> threadLocalList = threadList.get();
          threadLocalList.add(weakThreadLocals ? new WeakReference<>(bagEntry) : bagEntry);
       }
    

上述代码中的 weakThreadLocals 是用来判断是否使用弱引用，通过下述方法初始化：

    
    
      /**
        * Determine whether to use WeakReferences based on whether there is a
        * custom ClassLoader implementation sitting between this class and the
        * System ClassLoader.
        *
        * @return true if we should use WeakReferences in our ThreadLocals, false otherwise
        */
       private boolean useWeakThreadLocals()
       {
          try {
          // 人工指定是否使用弱引用，但是官方不推荐进行自主设置。
             if (System.getProperty("com.zaxxer.hikari.useWeakReferences") != null) {   // undocumented manual override of WeakReference behavior
                return Boolean.getBoolean("com.zaxxer.hikari.useWeakReferences");
             }
    // 默认通过判断初始化的ClassLoader是否是系统的ClassLoader来确定
             return getClass().getClassLoader() != ClassLoader.getSystemClassLoader();
          }
          catch (SecurityException se) {
             return true;
          }
       }
    

# SynchronousQueue

SynchronousQueue主要用于存在资源等待线程时的第一手资源交接，如下图所示：

![201805031003](http://cmsblogs.qiniudn.com/201805031003.jpeg)

在hikariCP中，选择的是公平模式 this.handoffQueue = new SynchronousQueue(true);

公平模式总结下来就是：队尾匹配队头出队，先进先出，体现公平原则。

SynchronousQueue是一个无存储空间的阻塞队列(是实现newFixedThreadPool的核心)，非常适合做交换工作，生产者的线程和消费者的线程同步以传递某些信息、事件或者任务。

因为是无存储空间的，所以与其他阻塞队列实现不同的是，这个阻塞peek方法直接返回null，无任何其他操作，其他的方法与阻塞队列的其他方法一致。这个队列的特点是，必须先调用take或者poll方法，才能使用off，add方法。

作为BlockingQueue中的一员，SynchronousQueue与其他BlockingQueue有着不同特性（
**来自明姐http://cmsblogs.com/?p=2418** ）：

  * SynchronousQueue没有容量。与其他BlockingQueue不同，SynchronousQueue是一个不存储元素的BlockingQueue。每一个put操作必须要等待一个take操作，否则不能继续添加元素，反之亦然。
  * 因为没有容量，所以对应 peek, contains, clear, isEmpty … 等方法其实是无效的。例如clear是不执行任何操作的，contains始终返回false,peek始终返回null。
  * SynchronousQueue分为公平和非公平，默认情况下采用非公平性访问策略，当然也可以通过构造函数来设置为公平性访问策略（为true即可）。
  * 若使用 TransferQueue, 则队列中永远会存在一个 dummy node。

SynchronousQueue提供了两个构造函数：

    
    
    public SynchronousQueue() {
            this(false);
        }
        public SynchronousQueue(boolean fair) {
            // 通过 fair 值来决定公平性和非公平性
            // 公平性使用TransferQueue，非公平性采用TransferStack
            transferer = fair ? new TransferQueue<E>() : new TransferStack<E>();
        }
    

TransferQueue、TransferStack继承Transferer，Transferer为SynchronousQueue的内部类，它提供了一个方法transfer()，该方法定义了转移数据的规范

    
    
    abstract static class Transferer<E> {
            abstract E transfer(E e, boolean timed, long nanos);
        }
    

transfer()方法主要用来完成转移数据的，如果e != null，相当于将一个数据交给消费者，如果e ==
null，则相当于从一个生产者接收一个消费者交出的数据。

SynchronousQueue采用队列TransferQueue来实现公平性策略，采用堆栈TransferStack来实现非公平性策略，他们两种都是通过链表实现的，其节点分别为QNode，SNode。TransferQueue和TransferStack在SynchronousQueue中扮演着非常重要的作用，SynchronousQueue的put、take操作都是委托这两个类来实现的。

## 公平模式

公平模式底层使用的TransferQueue内部队列，一个head和tail指针，用于指向当前正在等待匹配的线程节点。 （
**来自https://blog.csdn.net/yanyan19880509/article/details/52562039** ）  
初始化时，TransferQueue的状态如下：

![201805031004](http://cmsblogs.qiniudn.com/201805031004.png)

接着我们进行一些操作：

1、线程put1执行 put(1)操作，由于当前没有配对的消费线程，所以put1线程入队列，自旋一小会后睡眠等待，这时队列状态如下：

![201805031004](http://cmsblogs.qiniudn.com/201805031005.png)

2、接着，线程put2执行了put(2)操作，跟前面一样，put2线程入队列，自旋一小会后睡眠等待，这时队列状态如下：

![201805031006](http://cmsblogs.qiniudn.com/201805031006.png)

3、这时候，来了一个线程take1，执行了
take操作，由于tail指向put2线程，put2线程跟take1线程配对了(一put一take)，这时take1线程不需要入队，但是请注意了，这时候，要唤醒的线程并不是put2，而是put1。为何？
大家应该知道我们现在讲的是公平策略，所谓公平就是谁先入队了，谁就优先被唤醒，我们的例子明显是put1应该优先被唤醒。至于读者可能会有一个疑问，明明是take1线程跟put2线程匹配上了，结果是put1线程被唤醒消费，怎么确保take1线程一定可以和次首节点(head.next)也是匹配的呢？其实大家可以拿个纸画一画，就会发现真的就是这样的。  
公平策略总结下来就是：队尾匹配队头出队。  
执行后put1线程被唤醒，take1线程的 take()方法返回了1(put1线程的数据)，这样就实现了线程间的一对一通信，这时候内部状态如下：

![201805031007](http://cmsblogs.qiniudn.com/201805031007.png)

4、最后，再来一个线程take2，执行take操作，这时候只有put2线程在等候，而且两个线程匹配上了，线程put2被唤醒，  
take2线程take操作返回了2(线程put2的数据)，这时候队列又回到了起点，如下所示：

![201805031008](http://cmsblogs.qiniudn.com/201805031008.png)

以上便是公平模式下，SynchronousQueue的实现模型。总结下来就是：队尾匹配队头出队，先进先出，体现公平原则。

## 非公平模式

还是使用跟公平模式下一样的操作流程，对比两种策略下有何不同。非公平模式底层的实现使用的是TransferStack，  
一个栈，实现中用head指针指向栈顶，接着我们看看它的实现模型:

1、线程put1执行 put(1)操作，由于当前没有配对的消费线程，所以put1线程入栈，自旋一小会后睡眠等待，这时栈状态如下：

![201805031009](http://cmsblogs.qiniudn.com/201805031009.png)

2、接着，线程put2再次执行了put(2)操作，跟前面一样，put2线程入栈，自旋一小会后睡眠等待，这时栈状态如下：

![201805031010](http://cmsblogs.qiniudn.com/201805031010.png)

3、这时候，来了一个线程take1，执行了take操作，这时候发现栈顶为put2线程，匹配成功，但是实现会先把take1线程入栈，然后take1线程循环执行匹配put2线程逻辑，一旦发现没有并发冲突，就会把栈顶指针直接指向
put1线程

![201805031011](http://cmsblogs.qiniudn.com/201805031011.png)

4、最后，再来一个线程take2，执行take操作，这跟步骤3的逻辑基本是一致的，take2线程入栈，然后在循环中匹配put1线程，最终全部匹配完毕，栈变为空，恢复初始状态，如下图所示：

![201805031012](http://cmsblogs.qiniudn.com/201805031012.png)

从上面流程看出，虽然put1线程先入栈了，但是却是后匹配，这就是非公平的由来。

# CopyOnWriteArrayList

CopyOnWriteArrayList负责存放ConcurrentBag中全部用于出借的资源。(
**引自http://www.importnew.com/25034.html** )

CopyOnWriteArrayList，顾名思义，Write的时候总是要Copy，也就是说对于任何可变的操作（add、set、remove）都是伴随复制这个动作的，是ArrayList
的一个线程安全的变体。

> A thread-safe variant of ArrayList in which all mutative operations (add,
set, and so on) are implemented by making a fresh copy of the underlying
array.This is ordinarily too costly, but may be more efficient than
alternatives when traversal operations vastly outnumber mutations, and is
useful when you cannot or don’t want to synchronize traversals, yet need to
preclude interference among concurrent threads. The “snapshot” style iterator
method uses a reference to the state of the array at the point that the
iterator was created. This array never changes during the lifetime of the
iterator, so interference is impossible and the iterator is guaranteed not to
throw ConcurrentModificationException. The iterator will not reflect
additions, removals, or changes to the list since the iterator was created.
Element-changing operations on iterators themselves (remove, set, and add) are
not supported. These methods throw UnsupportedOperationException. All elements
are permitted, including null.

![2018050310013](http://cmsblogs.qiniudn.com/2018050310013.jpg)

CopyOnWriteArrayList的add操作的源代码如下：

    
    
    public boolean add(E e) {
        //1、先加锁
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();
            int len = elements.length;
            //2、拷贝数组
            Object[] newElements = Arrays.copyOf(elements, len + 1);
            //3、将元素加入到新数组中
            newElements[len] = e;
            //4、将array引用指向到新数组
            setArray(newElements);
            return true;
        } finally {
           //5、解锁
            lock.unlock();
        }
    }
    

一次add大致经历了几个步骤：

  1. 加锁
  2. 拿到原数组，得到新数组的大小（原数组大小+1），实例化出一个新的数组来
  3. 把原数组的元素复制到新数组中去
  4. 新数组最后一个位置设置为待添加的元素（因为新数组的大小是按照原数组大小+1来的）
  5. 把Object array引用指向新数组
  6. 解锁

插入、删除、修改操作也都是一样，每一次的操作都是以对Object[] array进行一次复制为基础的

由于所有的写操作都是在新数组进行的，这个时候如果有线程并发的写，则通过锁来控制，如果有线程并发的读，则分几种情况：  
– 如果写操作未完成，那么直接读取原数组的数据；  
– 如果写操作完成，但是引用还未指向新数组，那么也是读取原数组数据；  
– 如果写操作完成，并且引用已经指向了新的数组，那么直接从新数组中读取数据。

可见，CopyOnWriteArrayList的读操作是可以不用加锁的。

**常用的List有ArrayList、LinkedList、Vector，其中前两个是线程非安全的，最后一个是线程安全的。Vector虽然是线程安全的，但是只是一种相对的线程安全而不是绝对的线程安全，它只能够保证增、删、改、查的单个操作一定是原子的，不会被打断，但是如果组合起来用，并不能保证线程安全性。比如就像上面的线程1在遍历一个Vector中的元素、线程2在删除一个Vector中的元素一样，势必产生并发修改异常，也就是fail-
fast。**

所以这就是选择CopyOnWriteArrayList这个并发组件的原因，CopyOnWriteArrayList如何做到线程安全的呢？

CopyOnWriteArrayList使用了一种叫 **写时复制**
的方法，当有新元素添加到CopyOnWriteArrayList时，先从原有的数组中拷贝一份出来，然后在新的数组做写操作，写完之后，再将原来的数组引用指向到新数组。

当有新元素加入的时候，如下图，创建新数组，并往新数组中加入一个新元素,这个时候，array这个引用仍然是指向原数组的。

![201805031014](http://cmsblogs.qiniudn.com/201805031014.png)

当元素在新数组添加成功后，将array这个引用指向新数组。

![201805031015](http://cmsblogs.qiniudn.com/201805031015.png)

CopyOnWriteArrayList的整个add操作都是在锁的保护下进行的。  
这样做是为了避免在多线程并发add的时候，复制出多个副本出来,把数据搞乱了，导致最终的数组数据不是我们期望的。

CopyOnWriteArrayList反映的是三个十分重要的分布式理念：

1)读写分离  
我们读取CopyOnWriteArrayList的时候读取的是CopyOnWriteArrayList中的Object[]
array，但是修改的时候，操作的是一个新的Object[]
array，读和写操作的不是同一个对象，这就是读写分离。这种技术数据库用的非常多，在高并发下为了缓解数据库的压力，即使做了缓存也要对数据库做读写分离，读的时候使用读库，写的时候使用写库，然后读库、写库之间进行一定的同步，这样就避免同一个库上读、写的IO操作太多

2)最终一致  
对CopyOnWriteArrayList来说，线程1读取集合里面的数据，未必是最新的数据。因为线程2、线程3、线程4四个线程都修改了CopyOnWriteArrayList里面的数据，但是线程1拿到的还是最老的那个Object[]
array，新添加进去的数据并没有，所以线程1读取的内容未必准确。不过这些数据虽然对于线程1是不一致的，但是对于之后的线程一定是一致的，它们拿到的Object[]
array一定是三个线程都操作完毕之后的Object
array[]，这就是最终一致。最终一致对于分布式系统也非常重要，它通过容忍一定时间的数据不一致，提升整个分布式系统的可用性与分区容错性。当然，最终一致并不是任何场景都适用的，像火车站售票这种系统用户对于数据的实时性要求非常非常高，就必须做成强一致性的。

3）使用另外开辟空间的思路，来解决并发冲突

缺点：

  1. 因为CopyOnWrite的写时复制机制，所以在进行写操作的时候，内存里会同时驻扎两个对象的内存，旧的对象和新写入的对象（注意:在复制的时候只是复制容器里的引用，只是在写的时候会创建新对象添加到新容器里，而旧容器的对象还在使用，所以有两份对象内存）。如果这些对象占用的内存比较大，比如说200M左右，那么再写入100M数据进去，内存就会占用300M，那么这个时候很有可能造成频繁的Yong GC和Full GC。之前某系统中使用了一个服务由于每晚使用CopyOnWrite机制更新大对象，造成了每晚15秒的Full GC，应用响应时间也随之变长。针对内存占用问题，可以通过压缩容器中的元素的方法来减少大对象的内存消耗，比如，如果元素全是10进制的数字，可以考虑把它压缩成36进制或64进制。或者不使用CopyOnWrite容器，而使用其他的并发容器，如ConcurrentHashMap。
  2. 不能用于实时读的场景，像拷贝数组、新增元素都需要时间，所以调用一个set操作后，读取到数据可能还是旧的,虽CopyOnWriteArrayList 能做到最终一致性,但是还是没法满足实时性要求；
  3. 数据一致性问题。CopyOnWrite容器只能保证数据的最终一致性，不能保证数据的实时一致性。所以如果你希望写入的的数据，马上能读到，请不要使用CopyOnWrite容器。关于C++的STL中，曾经也有过Copy-On-Write的玩法，参见陈皓的《C++ STL String类中的Copy-On-Write》，后来，因为有很多线程安全上的事，就被去掉了。https://blog.csdn.net/haoel/article/details/24058

随着CopyOnWriteArrayList中元素的增加，CopyOnWriteArrayList的修改代价将越来越昂贵，因此，CopyOnWriteArrayList
合适读多写少的场景，不过这类慎用

因为谁也没法保证CopyOnWriteArrayList
到底要放置多少数据，万一数据稍微有点多，每次add/set都要重新复制数组，这个代价实在太高昂了。在高性能的互联网应用中，这种操作分分钟引起故障。
**CopyOnWriteArrayList适用于读操作远多于修改操作的并发场景中。** 而HikariCP就是这种场景。

还有比如白名单，黑名单，商品类目的访问和更新场景，假如我们有一个搜索网站，用户在这个网站的搜索框中，输入关键字搜索内容，但是某些关键字不允许被搜索。这些不能被搜索的关键字会被放在一个黑名单当中，黑名单每天晚上更新一次。当用户搜索时，会检查当前关键字在不在黑名单当中，如果在，则提示不能搜索。

但是使用CopyOnWriteMap需要注意两件事情：

  1. 减少扩容开销。根据实际需要，初始化CopyOnWriteMap的大小，避免写时CopyOnWriteMap扩容的开销。

  2. 使用批量添加。因为每次添加，容器每次都会进行复制，所以减少添加次数，可以减少容器的复制次数。

# 参考资料

  * <http://www.cnblogs.com/taisenki/p/7699667.html>
  * <http://cmsblogs.com/?p=2418>
  * <https://blog.csdn.net/yanyan19880509/article/details/52562039>
  * <http://www.importnew.com/25034.html>
  * <https://blog.csdn.net/linsongbin1/article/details/54581787>

