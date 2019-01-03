> 原文出处<http://cmsblogs.com/> 『 **chenssy** 』

* * *

昨天有位小伙伴问我一个 ArrayBlockingQueue 中的一个构造函数为何需要加锁，其实这个问题我还真没有注意过。主要是在看
ArrayBlockingQueue 源码时，觉得它很简单，不就是通过加锁的方式来操作一个数组 items
么，有什么难的，所以就没有关注这个问题，所以它一问我懵逼了。回家细想了下，所以产生这篇博客。我们先看构造方法：

    
    
        public ArrayBlockingQueue(int capacity, boolean fair, Collection<? extends E> c) {
            this(capacity, fair);
    
            final ReentrantLock lock = this.lock;
            lock.lock(); // Lock only for visibility, not mutual exclusion    //----(1)
            try {
                int i = 0;
                try {
                    for (E e : c) {
                        checkNotNull(e);
                        items[i++] = e;
                    }
                } catch (ArrayIndexOutOfBoundsException ex) {
                    throw new IllegalArgumentException();
                }
                count = i;
                putIndex = (i == capacity) ? 0 : i;
            } finally {
                lock.unlock();
            }
        }
    

第五行代码获取互斥锁，解释为 **锁的目的不是为了互斥，而是为了保证可见性** 。保证可见性？保证哪个可见性？我们知道 ArrayBlockingQueue
操作的其实就是一个 items 数组，这个数组是不具备线程安全的，所以保证可见性就是保证 items 的可见性。如果不加锁为什么就没法保证 items
的可见性呢？这其实是指令重排序的问题。

什么是指令重排序？编译器或运行时环境为了优化程序性能而采取的对指令进行重新排序执行的一种手段。也就是说程序运行的顺序与我们所想的顺序是不一致的。虽然它遵循
as-if-serial
语义，但是还是无法保证多线程环境下的数据安全。更多请参考博客[【死磕Java并发】—–Java内存模型之重排序](http://cmsblogs.com/?p=2116)。

为什么说指令重排序会影响 items 的可见性呢？创建一个对象要分为三个步骤：

  1. 分配内存空间
  2. 初始化对象
  3. 将内存空间的地址赋值给对应的引用

但是由于指令重排序的问题，步骤 2 和步骤 3 是可能发生重排序的，如下：

  1. 分配内存空间
  2. 将内存空间的地址赋值给对应的引用
  3. 初始化对象

这个过程就会对上面产生影响。假如我们两个线程：线程 A，负责 ArrayBlockingQueue 的实例化工作，线程 B，负责入队、出队操作。线程 A
优先执行。当它执行第 2 行代码，也就是 `this(capacity, fair);`，如下：

    
    
        public ArrayBlockingQueue(int capacity, boolean fair) {
            if (capacity <= 0)
                throw new IllegalArgumentException();
            this.items = new Object[capacity];
            lock = new ReentrantLock(fair);
            notEmpty = lock.newCondition();
            notFull =  lock.newCondition();
        }
    

这个时候 items 是已经完成了初始化工作的，也就是说我们可以对其进行操作了。如果在线程 A 实例化对象过程中，步骤 2 和步骤 3
重排序了，那么对于线程 B 而言，ArrayBlockingQueue 是已经完成初始化工作了也就是可以使用了。其实线程 A
可能还正在执行构造函数中的某一个行代码。两个线程在不加锁的情况对一个不具备线程安全的数组同时操作，很有可能会引发线程安全问题。

还有一种解释：缓存一致性。为了解决CPU处理速度以及读写主存速度不一致的问题，引入了 CPU
高速缓存。虽然解决了速度问题，但是也带来了缓存一致性的问题。在不加锁的前提下，线程 A 在构造函数中 items 进行操作，线程 B 通过入队、出队的方式对
items 进行操作，这个过程对 items 的操作结果有可能只存在各自线程的缓存中，并没有写入主存，这样肯定会造成数据不一致的情况。

推荐阅读：

  * [【死磕Java并发】—–Java内存模型之重排序](http://cmsblogs.com/?p=2116)
  * [【死磕Java并发】—–Java内存模型之从JMM角度分析DCL](http://cmsblogs.com/?p=2161)
  * [【死磕Java并发】—–深入分析volatile的实现原理](http://cmsblogs.com/?p=2092)
  * [【死磕Java并发】—–J.U.C之阻塞队列：ArrayBlockingQueue](http://cmsblogs.com/?p=2381)

