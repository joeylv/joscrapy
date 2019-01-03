  * 1 写锁
    * 1.1 写锁的获取
    * 1.2 写锁的释放
  * 2 读锁
    * 2.1 读锁的获取
    * 2.2 读锁的释放
    * 2.3 HoldCounter
  * 3 锁降级
  * 4 推荐阅读
  * 5 参考资料

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

> 此篇博客所有源码均来自JDK 1.8

重入锁ReentrantLock是排他锁，排他锁在同一时刻仅有一个线程可以进行访问，但是在大多数场景下，大部分时间都是提供读服务，而写服务占有的时间较少。然而读服务不存在数据竞争问题，如果一个线程在读时禁止其他线程读势必会导致性能降低。所以就提供了读写锁。

读写锁维护着一对锁，一个读锁和一个写锁。通过分离读锁和写锁，使得并发性比一般的排他锁有了较大的提升：在同一时间可以允许多个读线程同时访问，但是在写线程访问时，所有读线程和写线程都会被阻塞。

读写锁的主要特性：

  1. 公平性：支持公平性和非公平性。
  2. 重入性：支持重入。读写锁最多支持65535个递归写入锁和65535个递归读取锁。
  3. 锁降级：遵循获取写锁、获取读锁在释放写锁的次序，写锁能够降级成为读锁

读写锁ReentrantReadWriteLock实现接口ReadWriteLock，该接口维护了一对相关的锁，一个用于只读操作，另一个用于写入操作。只要没有
writer，读取锁可以由多个 reader 线程同时保持。写入锁是独占的。

    
    
    public interface ReadWriteLock {
        Lock readLock();
        Lock writeLock();
    }
    

ReadWriteLock定义了两个方法。readLock()返回用于读操作的锁，writeLock()返回用于写操作的锁。ReentrantReadWriteLock定义如下：

    
    
        /** 内部类  读锁 */
        private final ReentrantReadWriteLock.ReadLock readerLock;
        /** 内部类  写锁 */
        private final ReentrantReadWriteLock.WriteLock writerLock;
    
        final Sync sync;
    
        /** 使用默认（非公平）的排序属性创建一个新的 ReentrantReadWriteLock */
        public ReentrantReadWriteLock() {
            this(false);
        }
    
        /** 使用给定的公平策略创建一个新的 ReentrantReadWriteLock */
        public ReentrantReadWriteLock(boolean fair) {
            sync = fair ? new FairSync() : new NonfairSync();
            readerLock = new ReadLock(this);
            writerLock = new WriteLock(this);
        }
    
        /** 返回用于写入操作的锁 */
        public ReentrantReadWriteLock.WriteLock writeLock() { return writerLock; }
        /** 返回用于读取操作的锁 */
        public ReentrantReadWriteLock.ReadLock  readLock()  { return readerLock; }
    
        abstract static class Sync extends AbstractQueuedSynchronizer {
            /**
             * 省略其余源代码
             */
        }
        public static class WriteLock implements Lock, java.io.Serializable{
            /**
             * 省略其余源代码
             */
        }
    
        public static class ReadLock implements Lock, java.io.Serializable {
            /**
             * 省略其余源代码
             */
        }
    

ReentrantReadWriteLock与ReentrantLock一样，其锁主体依然是Sync，它的读锁、写锁都是依靠Sync来实现的。所以ReentrantReadWriteLock实际上只有一个锁，只是在获取读取锁和写入锁的方式上不一样而已，它的读写锁其实就是两个类：ReadLock、writeLock，这两个类都是lock实现。

在ReentrantLock中使用一个int类型的state来表示同步状态，该值表示锁被一个线程重复获取的次数。但是读写锁ReentrantReadWriteLock内部维护着两个一对锁，需要用一个变量维护多种状态。所以读写锁采用“按位切割使用”的方式来维护这个变量，将其切分为两部分，高16为表示读，低16为表示写。分割之后，读写锁是如何迅速确定读锁和写锁的状态呢？通过为运算。假如当前同步状态为S，那么写状态等于
S & 0x0000FFFF（将高16位全部抹去），读状态等于S >>> 16(无符号补0右移16位)。代码如下：

    
    
            static final int SHARED_SHIFT   = 16;
            static final int SHARED_UNIT    = (1 << SHARED_SHIFT);
            static final int MAX_COUNT      = (1 << SHARED_SHIFT) - 1;
            static final int EXCLUSIVE_MASK = (1 << SHARED_SHIFT) - 1;
    
            static int sharedCount(int c)    { return c >>> SHARED_SHIFT; }
            static int exclusiveCount(int c) { return c & EXCLUSIVE_MASK; }
    

## 写锁

写锁就是一个支持可重入的排他锁。

### 写锁的获取

写锁的获取最终会调用tryAcquire(int arg)，该方法在内部类Sync中实现：

    
    
        protected final boolean tryAcquire(int acquires) {
            Thread current = Thread.currentThread();
            //当前锁个数
            int c = getState();
            //写锁
            int w = exclusiveCount(c);
            if (c != 0) {
                //c != 0 && w == 0 表示存在读锁
                //当前线程不是已经获取写锁的线程
                if (w == 0 || current != getExclusiveOwnerThread())
                    return false;
                //超出最大范围
                if (w + exclusiveCount(acquires) > MAX_COUNT)
                    throw new Error("Maximum lock count exceeded");
                setState(c + acquires);
                return true;
            }
            //是否需要阻塞
            if (writerShouldBlock() ||
                    !compareAndSetState(c, c + acquires))
                return false;
            //设置获取锁的线程为当前线程
            setExclusiveOwnerThread(current);
            return true;
        }
    

该方法和ReentrantLock的tryAcquire(int
arg)大致一样，在判断重入时增加了一项条件：读锁是否存在。因为要确保写锁的操作对读锁是可见的，如果在存在读锁的情况下允许获取写锁，那么那些已经获取读锁的其他线程可能就无法感知当前写线程的操作。因此只有等读锁完全释放后，写锁才能够被当前线程所获取，一旦写锁获取了，所有其他读、写线程均会被阻塞。

### 写锁的释放

获取了写锁用完了则需要释放，WriteLock提供了unlock()方法释放写锁：

    
    
        public void unlock() {
            sync.release(1);
        }
    
        public final boolean release(int arg) {
            if (tryRelease(arg)) {
                Node h = head;
                if (h != null && h.waitStatus != 0)
                    unparkSuccessor(h);
                return true;
            }
            return false;
        }
    

写锁的释放最终还是会调用AQS的模板方法release(int arg)方法，该方法首先调用tryRelease(int
arg)方法尝试释放锁，tryRelease(int arg)方法为读写锁内部类Sync中定义了，如下：

    
    
        protected final boolean tryRelease(int releases) {
            //释放的线程不为锁的持有者
            if (!isHeldExclusively())
                throw new IllegalMonitorStateException();
            int nextc = getState() - releases;
            //若写锁的新线程数为0，则将锁的持有者设置为null
            boolean free = exclusiveCount(nextc) == 0;
            if (free)
                setExclusiveOwnerThread(null);
            setState(nextc);
            return free;
        }
    

写锁释放锁的整个过程和独占锁ReentrantLock相似，每次释放均是减少写状态，当写状态为0时表示
写锁已经完全释放了，从而等待的其他线程可以继续访问读写锁，获取同步状态，同时此次写线程的修改对后续的线程可见。

## 读锁

读锁为一个可重入的共享锁，它能够被多个线程同时持有，在没有其他写线程访问时，读锁总是或获取成功。

### 读锁的获取

读锁的获取可以通过ReadLock的lock()方法：

    
    
            public void lock() {
                sync.acquireShared(1);
            }
    

Sync的acquireShared(int arg)定义在AQS中：

    
    
        public final void acquireShared(int arg) {
            if (tryAcquireShared(arg) < 0)
                doAcquireShared(arg);
        }
    

tryAcqurireShared(int arg)尝试获取读同步状态，该方法主要用于获取共享式同步状态，获取成功返回 >= 0的返回结果，否则返回 < 0
的返回结果。

    
    
        protected final int tryAcquireShared(int unused) {
            //当前线程
            Thread current = Thread.currentThread();
            int c = getState();
            //exclusiveCount(c)计算写锁
            //如果存在写锁，且锁的持有者不是当前线程，直接返回-1
            //存在锁降级问题，后续阐述
            if (exclusiveCount(c) != 0 &&
                    getExclusiveOwnerThread() != current)
                return -1;
            //读锁
            int r = sharedCount(c);
    
            /*
             * readerShouldBlock():读锁是否需要等待（公平锁原则）
             * r < MAX_COUNT：持有线程小于最大数（65535）
             * compareAndSetState(c, c + SHARED_UNIT)：设置读取锁状态
             */
            if (!readerShouldBlock() &&
                    r < MAX_COUNT &&
                    compareAndSetState(c, c + SHARED_UNIT)) {
                /*
                 * holdCount部分后面讲解
                 */
                if (r == 0) {
                    firstReader = current;
                    firstReaderHoldCount = 1;
                } else if (firstReader == current) {
                    firstReaderHoldCount++;
                } else {
                    HoldCounter rh = cachedHoldCounter;
                    if (rh == null || rh.tid != getThreadId(current))
                        cachedHoldCounter = rh = readHolds.get();
                    else if (rh.count == 0)
                        readHolds.set(rh);
                    rh.count++;
                }
                return 1;
            }
            return fullTryAcquireShared(current);
        }
    

读锁获取的过程相对于独占锁而言会稍微复杂下，整个过程如下：

  1. 因为存在锁降级情况，如果存在写锁且锁的持有者不是当前线程则直接返回失败，否则继续
  2. 依据公平性原则，判断读锁是否需要阻塞，读锁持有线程数小于最大值（65535），且设置锁状态成功，执行以下代码（对于HoldCounter下面再阐述），并返回1。如果不满足改条件，执行fullTryAcquireShared()。

    
    
        final int fullTryAcquireShared(Thread current) {
            HoldCounter rh = null;
            for (;;) {
                int c = getState();
                //锁降级
                if (exclusiveCount(c) != 0) {
                    if (getExclusiveOwnerThread() != current)
                        return -1;
                }
                //读锁需要阻塞
                else if (readerShouldBlock()) {
                    //列头为当前线程
                    if (firstReader == current) {
                    }
                    //HoldCounter后面讲解
                    else {
                        if (rh == null) {
                            rh = cachedHoldCounter;
                            if (rh == null || rh.tid != getThreadId(current)) {
                                rh = readHolds.get();
                                if (rh.count == 0)
                                    readHolds.remove();
                            }
                        }
                        if (rh.count == 0)
                            return -1;
                    }
                }
                //读锁超出最大范围
                if (sharedCount(c) == MAX_COUNT)
                    throw new Error("Maximum lock count exceeded");
                //CAS设置读锁成功
                if (compareAndSetState(c, c + SHARED_UNIT)) {
                    //如果是第1次获取“读取锁”，则更新firstReader和firstReaderHoldCount
                    if (sharedCount(c) == 0) {
                        firstReader = current;
                        firstReaderHoldCount = 1;
                    }
                    //如果想要获取锁的线程(current)是第1个获取锁(firstReader)的线程,则将firstReaderHoldCount+1
                    else if (firstReader == current) {
                        firstReaderHoldCount++;
                    } else {
                        if (rh == null)
                            rh = cachedHoldCounter;
                        if (rh == null || rh.tid != getThreadId(current))
                            rh = readHolds.get();
                        else if (rh.count == 0)
                            readHolds.set(rh);
                        //更新线程的获取“读取锁”的共享计数
                        rh.count++;
                        cachedHoldCounter = rh; // cache for release
                    }
                    return 1;
                }
            }
        }
    

fullTryAcquireShared(Thread
current)会根据“是否需要阻塞等待”，“读取锁的共享计数是否超过限制”等等进行处理。如果不需要阻塞等待，并且锁的共享计数没有超过限制，则通过CAS尝试获取锁，并返回1

### 读锁的释放

与写锁相同，读锁也提供了unlock()释放读锁：

    
    
            public void unlock() {
                sync.releaseShared(1);
            }
    

unlcok()方法内部使用Sync的releaseShared(int arg)方法，该方法定义在AQS中：

    
    
        public final boolean releaseShared(int arg) {
            if (tryReleaseShared(arg)) {
                doReleaseShared();
                return true;
            }
            return false;
        }
    

调用tryReleaseShared(int arg)尝试释放读锁，该方法定义在读写锁的Sync内部类中：

    
    
        protected final boolean tryReleaseShared(int unused) {
            Thread current = Thread.currentThread();
            //如果想要释放锁的线程为第一个获取锁的线程
            if (firstReader == current) {
                //仅获取了一次，则需要将firstReader 设置null，否则 firstReaderHoldCount - 1
                if (firstReaderHoldCount == 1)
                    firstReader = null;
                else
                    firstReaderHoldCount--;
            }
            //获取rh对象，并更新“当前线程获取锁的信息”
            else {
                HoldCounter rh = cachedHoldCounter;
                if (rh == null || rh.tid != getThreadId(current))
                    rh = readHolds.get();
                int count = rh.count;
                if (count <= 1) {
                    readHolds.remove();
                    if (count <= 0)
                        throw unmatchedUnlockException();
                }
                --rh.count;
            }
            //CAS更新同步状态
            for (;;) {
                int c = getState();
                int nextc = c - SHARED_UNIT;
                if (compareAndSetState(c, nextc))
                    return nextc == 0;
            }
        }
    

### HoldCounter

在读锁获取锁和释放锁的过程中，我们一直都可以看到一个变量rh （HoldCounter ），该变量在读锁中扮演着非常重要的作用。

我们了解读锁的内在机制其实就是一个共享锁，为了更好理解HoldCounter
，我们暂且认为它不是一个锁的概率，而相当于一个计数器。一次共享锁的操作就相当于在该计数器的操作。获取共享锁，则该计数器 + 1，释放共享锁，该计数器 –
1。只有当线程获取共享锁后才能对共享锁进行释放、重入操作。所以HoldCounter的作用就是当前线程持有共享锁的数量，这个数量必须要与线程绑定在一起，否则操作其他线程锁就会抛出异常。我们先看HoldCounter的定义：

    
    
            static final class HoldCounter {
                int count = 0;
                final long tid = getThreadId(Thread.currentThread());
            }
    

HoldCounter 定义非常简单，就是一个计数器count 和线程 id tid 两个变量。按照这个意思我们看到HoldCounter
是需要和某给线程进行绑定了，我们知道如果要将一个对象和线程绑定仅仅有tid是不够的，而且从上面的代码我们可以看到HoldCounter
仅仅只是记录了tid，根本起不到绑定线程的作用。那么怎么实现呢？答案是ThreadLocal，定义如下：

    
    
            static final class ThreadLocalHoldCounter
                extends ThreadLocal<HoldCounter> {
                public HoldCounter initialValue() {
                    return new HoldCounter();
                }
            }
    

通过上面代码HoldCounter就可以与线程进行绑定了。故而，HoldCounter应该就是绑定线程上的一个计数器，而ThradLocalHoldCounter则是线程绑定的ThreadLocal。从上面我们可以看到ThreadLocal将HoldCounter绑定到当前线程上，同时HoldCounter也持有线程Id，这样在释放锁的时候才能知道ReadWriteLock里面缓存的上一个读取线程（cachedHoldCounter）是否是当前线程。这样做的好处是可以减少ThreadLocal.get()的次数，因为这也是一个耗时操作。需要说明的是这样HoldCounter绑定线程id而不绑定线程对象的原因是避免HoldCounter和ThreadLocal互相绑定而GC难以释放它们（尽管GC能够智能的发现这种引用而回收它们，但是这需要一定的代价），所以其实这样做只是为了帮助GC快速回收对象而已。

看到这里我们明白了HoldCounter作用了，我们在看一个获取读锁的代码段：

    
    
                    else if (firstReader == current) {
                        firstReaderHoldCount++;
                    } else {
                        if (rh == null)
                            rh = cachedHoldCounter;
                        if (rh == null || rh.tid != getThreadId(current))
                            rh = readHolds.get();
                        else if (rh.count == 0)
                            readHolds.set(rh);
                        rh.count++;
                        cachedHoldCounter = rh; // cache for release
                    }
    

这段代码涉及了几个变量：firstReader 、firstReaderHoldCount、cachedHoldCounter 。我们先理清楚这几个变量：

    
    
    private transient Thread firstReader = null;
    private transient int firstReaderHoldCount;
    private transient HoldCounter cachedHoldCounter;
    

firstReader
看名字就明白了为第一个获取读锁的线程，firstReaderHoldCount为第一个获取读锁的重入数，cachedHoldCounter为HoldCounter的缓存。

理清楚上面所有的变量了，HoldCounter也明白了，我们就来给上面那段代码标明注释，如下：

    
    
        //如果获取读锁的线程为第一次获取读锁的线程，则firstReaderHoldCount重入数 + 1
        else if (firstReader == current) {
            firstReaderHoldCount++;
        } else {
            //非firstReader计数
            if (rh == null)
                rh = cachedHoldCounter;
            //rh == null 或者 rh.tid != current.getId()，需要获取rh
            if (rh == null || rh.tid != getThreadId(current))
                rh = readHolds.get();
                //加入到readHolds中
            else if (rh.count == 0)
                readHolds.set(rh);
            //计数+1
            rh.count++;
            cachedHoldCounter = rh; // cache for release
        }
    

这里解释下为何要引入firstRead、firstReaderHoldCount。这是为了一个效率问题，firstReader是不会放入到readHolds中的，如果读锁仅有一个的情况下就会避免查找readHolds。

## 锁降级

上开篇是LZ就阐述了读写锁有一个特性就是锁降级，锁降级就意味着写锁是可以降级为读锁的，但是需要遵循先获取写锁、获取读锁在释放写锁的次序。注意如果当前线程先获取写锁，然后释放写锁，再获取读锁这个过程不能称之为锁降级，锁降级一定要遵循那个次序。

在获取读锁的方法tryAcquireShared(int unused)中，有一段代码就是来判读锁降级的：

    
    
            int c = getState();
            //exclusiveCount(c)计算写锁
            //如果存在写锁，且锁的持有者不是当前线程，直接返回-1
            //存在锁降级问题，后续阐述
            if (exclusiveCount(c) != 0 &&
                    getExclusiveOwnerThread() != current)
                return -1;
            //读锁
            int r = sharedCount(c);
    

锁降级中读锁的获取释放为必要？肯定是必要的。试想，假如当前线程A不获取读锁而是直接释放了写锁，这个时候另外一个线程B获取了写锁，那么这个线程B对数据的修改是不会对当前线程A可见的。如果获取了读锁，则线程B在获取写锁过程中判断如果有读锁还没有释放则会被阻塞，只有当前线程A释放读锁后，线程B才会获取写锁成功。

## 推荐阅读

因为里面很多地方涉及到了AQS部分，推荐阅读如下部分：

  1. [【死磕Java并发】—–J.U.C之AQS：AQS简介](http://cmsblogs.com/?p=2174)
  2. [【死磕Java并发】—–J.U.C之AQS：CLH同步队列](http://cmsblogs.com/?p=2188)
  3. [【死磕Java并发】—–J.U.C之AQS：同步状态的获取与释放](http://cmsblogs.com/?p=2197)
  4. [【死磕Java并发】—–J.U.C之AQS：阻塞和唤醒线程](http://cmsblogs.com/?p=2205)

## 参考资料

  1. Doug Lea：《Java并发编程实战》
  2. 方腾飞：《Java并发编程的艺术》
  3. [【Java并发编程实战】—–“J.U.C”：ReentrantReadWriteLock](http://cmsblogs.com/?p=1679)
  4. [Java多线程（十）之ReentrantReadWriteLock深入分析](https://my.oschina.net/adan1/blog/158107)

