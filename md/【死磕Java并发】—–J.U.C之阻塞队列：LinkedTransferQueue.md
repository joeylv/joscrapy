  * 1 LinkedTransferQueue
    * 1.1 结构
    * 1.2 Node节点
    * 1.3 put操作
    * 1.4 take操作
    * 1.5 tranfer操作
    * 1.6 xfer()
    * 1.7 实例

> 原文出处<http://cmsblogs.com/> 『 **chenssy** 』

前面提到的各种BlockingQueue对读或者写都是锁上整个队列，在并发量大的时候，各种锁是比较耗资源和耗时间的，而前面的SynchronousQueue虽然不会锁住整个队列，但它是一个没有容量的“队列”，那么有没有这样一种队列，它即可以像其他的BlockingQueue一样有容量又可以像SynchronousQueue一样不会锁住整个队列呢？有！答案就是LinkedTransferQueue。

LinkedTransferQueue是基于链表的FIFO无界阻塞队列，它出现在JDK7中。Doug Lea 大神说
**LinkedTransferQueue是一个聪明的队列**
。它是[ConcurrentLinkedQueue](http://cmsblogs.com/?p=2353)、[SynchronousQueue](http://cmsblogs.com/?p=2418)
(公平模式下)、无界的[LinkedBlockingQueues](http://cmsblogs.com/?p=2381)等的超集。既然这么牛逼，那势必要弄清楚其中的原理了。

## LinkedTransferQueue

看源码之前我们先稍微了解下它的原理，这样看源码就会有迹可循了。

LinkedTransferQueue采用一种 **预占模式**
。什么意思呢？有就直接拿走，没有就占着这个位置直到拿到或者超时或者中断。即消费者线程到队列中取元素时，如果发现队列为空，则会生成一个null节点，然后park住等待生产者。后面如果生产者线程入队时发现有一个null元素节点，这时生产者就不会入列了，直接将元素填充到该节点上，唤醒该节点的线程，被唤醒的消费者线程拿东西走人。是不是有点儿[SynchronousQueue](http://cmsblogs.com/?p=2418)的味道？

### 结构

LinkedTransferQueue与其他的BlockingQueue一样，同样继承AbstractQueue类，但是它实现了TransferQueue，TransferQueue接口继承BlockingQueue，所以TransferQueue算是对BlockingQueue一种扩充，该接口提供了一整套的transfer接口：

    
    
        public interface TransferQueue<E> extends BlockingQueue<E> {
    
            /**
             * 若当前存在一个正在等待获取的消费者线程（使用take()或者poll()函数），使用该方法会即刻转移/传输对象元素e；
             * 若不存在，则返回false，并且不进入队列。这是一个不阻塞的操作
             */
            boolean tryTransfer(E e);
    
            /**
             * 若当前存在一个正在等待获取的消费者线程，即立刻移交之；
             * 否则，会插入当前元素e到队列尾部，并且等待进入阻塞状态，到有消费者线程取走该元素
             */
            void transfer(E e) throws InterruptedException;
    
            /**
             * 若当前存在一个正在等待获取的消费者线程，会立即传输给它;否则将插入元素e到队列尾部，并且等待被消费者线程获取消费掉；
             * 若在指定的时间内元素e无法被消费者线程获取，则返回false，同时该元素被移除。
             */
            boolean tryTransfer(E e, long timeout, TimeUnit unit)
                    throws InterruptedException;
    
            /**
             * 判断是否存在消费者线程
             */
            boolean hasWaitingConsumer();
    
            /**
             * 获取所有等待获取元素的消费线程数量
             */
            int getWaitingConsumerCount();
        }
    

相对于其他的BlockingQueue，LinkedTransferQueue就多了上面几个方法。这几个方法在LinkedTransferQueue中起到了核心作用。

LinkedTransferQueue定义的变量如下：

    
    
        // 判断是否为多核
        private static final boolean MP =
                Runtime.getRuntime().availableProcessors() > 1;
    
        // 自旋次数
        private static final int FRONT_SPINS   = 1 << 7;
    
        // 前驱节点正在处理，当前节点需要自旋的次数
        private static final int CHAINED_SPINS = FRONT_SPINS >>> 1;
    
        static final int SWEEP_THRESHOLD = 32;
    
        // 头节点
        transient volatile Node head;
    
        // 尾节点
        private transient volatile Node tail;
    
        // 删除节点失败的次数
        private transient volatile int sweepVotes;
    
        /*
         * 调用xfer()方法时需要传入,区分不同处理
         * xfer()方法是LinkedTransferQueue的最核心的方法
         */
        private static final int NOW   = 0; // for untimed poll, tryTransfer
        private static final int ASYNC = 1; // for offer, put, add
        private static final int SYNC  = 2; // for transfer, take
        private static final int TIMED = 3; // for timed poll, tryTransfer
    

### Node节点

Node节点由四个部分构成：

  * isData：表示该节点是存放数据还是获取数据
  * item：存放数据，isData为false时，该节点为null，为true时，匹配后，该节点会置为null
  * next：指向下一个节点
  * waiter：park住消费者线程，线程就放在这里

结构如下：

![这里写图片描述](http://img.blog.csdn.net/20170924210642971?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnNzeQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)  
源码如下：

    
    
        static final class Node {
            // 表示该节点是存放数据还是获取数据
            final boolean isData;
            // 存放数据，isData为false时，该节点为null，为true时，匹配后，该节点会置为null
            volatile Object item;
            //指向下一个节点
            volatile Node next;
    
            // park住消费者线程，线程就放在这里
            volatile Thread waiter; // null until waiting
    
            /**
             * CAS Next域
             */
            final boolean casNext(Node cmp, Node val) {
                return UNSAFE.compareAndSwapObject(this, nextOffset, cmp, val);
            }
    
            /**
             * CAS itme域
             */
            final boolean casItem(Object cmp, Object val) {
                return UNSAFE.compareAndSwapObject(this, itemOffset, cmp, val);
            }
    
            /**
             * 构造函数
             */
            Node(Object item, boolean isData) {
                UNSAFE.putObject(this, itemOffset, item); // relaxed write
                this.isData = isData;
            }
    
            /**
             * 将next域指向自身，其实就是剔除节点
             */
            final void forgetNext() {
                UNSAFE.putObject(this, nextOffset, this);
            }
    
            /**
             *  匹配过或节点被取消的时候会调用
             */
            final void forgetContents() {
                UNSAFE.putObject(this, itemOffset, this);
                UNSAFE.putObject(this, waiterOffset, null);
            }
    
            /**
             * 校验节点是否匹配过，如果匹配做取消了，item则会发生变化
             */
            final boolean isMatched() {
                Object x = item;
                return (x == this) || ((x == null) == isData);
            }
    
            /**
             * 是否是一个未匹配的请求节点
             * 如果是的话isData应为false，item == null，因位如果匹配了，item则会有值
             */
            final boolean isUnmatchedRequest() {
                return !isData && item == null;
            }
    
            /**
             * 如给定节点类型不能挂在当前节点后返回true
             */
            final boolean cannotPrecede(boolean haveData) {
                boolean d = isData;
                Object x;
                return d != haveData && (x = item) != this && (x != null) == d;
            }
    
            /**
             * 匹配一个数据节点
             */
            final boolean tryMatchData() {
                // assert isData;
                Object x = item;
                if (x != null && x != this && casItem(x, null)) {
                    LockSupport.unpark(waiter);
                    return true;
                }
                return false;
            }
    
            private static final long serialVersionUID = -3375979862319811754L;
    
            // Unsafe mechanics
            private static final sun.misc.Unsafe UNSAFE;
            private static final long itemOffset;
            private static final long nextOffset;
            private static final long waiterOffset;
            static {
                try {
                    UNSAFE = sun.misc.Unsafe.getUnsafe();
                    Class<?> k = Node.class;
                    itemOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("item"));
                    nextOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("next"));
                    waiterOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("waiter"));
                } catch (Exception e) {
                    throw new Error(e);
                }
            }
        }
    

节点Node为LinkedTransferQueue的内部类，其内部结构和公平方式的SynchronousQueue差不多，里面也同样提供了一些很重要的方法。

### put操作

LinkedTransferQueue提供了add、put、offer三类方法，用于将元素插入队列中，如下：

    
    
        public void put(E e) {
            xfer(e, true, ASYNC, 0);
        }
    
        public boolean offer(E e, long timeout, TimeUnit unit) {
            xfer(e, true, ASYNC, 0);
            return true;
        }
    
        public boolean offer(E e) {
            xfer(e, true, ASYNC, 0);
            return true;
        }
    
        public boolean add(E e) {
            xfer(e, true, ASYNC, 0);
            return true;
        }
    

由于LinkedTransferQueue是无界的，不会阻塞，所以在调用xfer方法是传入的是ASYNC，同时直接返回true.

### take操作

LinkedTransferQueue提供了poll、take方法用于出列元素：

    
    
        public E take() throws InterruptedException {
            E e = xfer(null, false, SYNC, 0);
            if (e != null)
                return e;
            Thread.interrupted();
            throw new InterruptedException();
        }
    
        public E poll() {
            return xfer(null, false, NOW, 0);
        }
    
        public E poll(long timeout, TimeUnit unit) throws InterruptedException {
            E e = xfer(null, false, TIMED, unit.toNanos(timeout));
            if (e != null || !Thread.interrupted())
                return e;
            throw new InterruptedException();
        }
    

这里和put操作有点不一样，take()方法传入的是SYNC，阻塞。poll()传入的是NOW，poll(long timeout, TimeUnit
unit)则是传入TIMED。

### tranfer操作

实现TransferQueue接口，就要实现它的方法：

    
    
    public boolean tryTransfer(E e, long timeout, TimeUnit unit)
        throws InterruptedException {
        if (xfer(e, true, TIMED, unit.toNanos(timeout)) == null)
            return true;
        if (!Thread.interrupted())
            return false;
        throw new InterruptedException();
    }
    
    public void transfer(E e) throws InterruptedException {
        if (xfer(e, true, SYNC, 0) != null) {
            Thread.interrupted(); // failure possible only due to interrupt
            throw new InterruptedException();
        }
    }
    
    public boolean tryTransfer(E e) {
        return xfer(e, true, NOW, 0) == null;
    }
    

### xfer()

通过上面几个核心方法的源码我们清楚可以看到，最终都是调用xfer()方法，该方法接受四个参数，item或者null的E，put操作为true、take操作为false的havaData，how（有四个值NOW,
ASYNC, SYNC, or TIMED，分别表示不同的操作），超时nanos。

    
    
        private E xfer(E e, boolean haveData, int how, long nanos) {
    
            // havaData为true，但是e == null 抛出空指针
            if (haveData && (e == null))
                throw new NullPointerException();
            Node s = null;                        // the node to append, if needed
    
            retry:
            for (;;) {
    
                // 从首节点开始匹配
                // p == null 队列为空
                for (Node h = head, p = h; p != null;) {
    
                    // 模型，request or data
                    boolean isData = p.isData;
                    // item域
                    Object item = p.item;
    
                    // 找到一个没有匹配的节点
                    // item != p 也就是自身，则表示没有匹配过
                    // (item != null) == isData，表示模型符合
                    if (item != p && (item != null) == isData) {
    
                        // 节点类型和待处理类型一致，这样肯定是不能匹配的
                        if (isData == haveData)   // can"t match
                            break;
                        // 匹配，将E加入到item域中
                        // 如果p 的item为data，那么e为null,如果p的item为null，那么e为data
                        if (p.casItem(item, e)) { // match
                            //
                            for (Node q = p; q != h;) {
                                Node n = q.next;  // update by 2 unless singleton
                                if (head == h && casHead(h, n == null ? q : n)) {
                                    h.forgetNext();
                                    break;
                                }                 // advance and retry
                                if ((h = head)   == null ||
                                        (q = h.next) == null || !q.isMatched())
                                    break;        // unless slack < 2
                            }
    
                            // 匹配后唤醒p的waiter线程;reservation则叫人收货，data则叫null收货
                            LockSupport.unpark(p.waiter);
                            return LinkedTransferQueue.<E>cast(item);
                        }
                    }
                    // 如果已经匹配了则向前推进
                    Node n = p.next;
                    // 如果p的next指向p本身，说明p节点已经有其他线程处理过了，只能从head重新开始
                    p = (p != n) ? n : (h = head); // Use head if p offlist
                }
    
                // 如果没有找到匹配的节点，则进行处理
                // NOW为untimed poll, tryTransfer，不需要入队
                if (how != NOW) {                 // No matches available
                    // s == null，新建一个节点
                    if (s == null)
                        s = new Node(e, haveData);
                    // 入队，返回前驱节点
                    Node pred = tryAppend(s, haveData);
                    // 返回的前驱节点为null，那就是有race，被其他的抢了，那就continue 整个for
                    if (pred == null)
                        continue retry;
    
                    // ASYNC不需要阻塞等待
                    if (how != ASYNC)
                        return awaitMatch(s, pred, e, (how == TIMED), nanos);
                }
                return e;
            }
        }
    

整个算法的核心就是寻找匹配节点找到了就返回，否则就入队（NOW直接返回）：

  * matched。判断匹配条件（isData不一样，本身没有匹配），匹配后就casItem，然后unpark匹配节点的waiter线程，如果是reservation则叫人收货，data则叫null收货。
  * unmatched。如果没有找到匹配节点，则根据传入的how来处理，NOW直接返回，其余三种先入对，入队后如果是ASYNC则返回，SYNC和TIMED则会阻塞等待匹配。

其实相当于SynchronousQueue来说，这个处理逻辑还是比较简单的。

如果没有找到匹配节点，且how != NOW会入队，入队则是调用tryAppend方法：

    
    
        private Node tryAppend(Node s, boolean haveData) {
            // 从尾节点tail开始
            for (Node t = tail, p = t;;) {
                Node n, u;
    
                // 队列为空则将节点S设置为head
                if (p == null && (p = head) == null) {
                    if (casHead(null, s))
                        return s;
                }
    
                // 如果为data
                else if (p.cannotPrecede(haveData))
                    return null;
    
                // 不是最后一个节点
                else if ((n = p.next) != null)
                    p = p != t && t != (u = tail) ? (t = u) : (p != n) ? n : null;
                // CAS失败，一般来说失败的原因在于p.next != null，可能有其他增加了tail，向前推荐
                else if (!p.casNext(null, s))
                    p = p.next;                   // re-read on CAS failure
                else {
                    if (p != t) {                 // update if slack now >= 2
                        while ((tail != t || !casTail(t, s)) &&
                                (t = tail)   != null &&
                                (s = t.next) != null && // advance and retry
                                (s = s.next) != null && s != t);
                    }
                    return p;
                }
            }
        }
    

tryAppend方法是将S节点添加到tail上，然后返回其前驱节点。好吧，我承认这段代码我看的有点儿晕！！！

加入队列后，如果how还不是ASYNC则调用awaitMatch()方法阻塞等待：

    
    
        private E awaitMatch(Node s, Node pred, E e, boolean timed, long nanos) {
            // 超时控制
            final long deadline = timed ? System.nanoTime() + nanos : 0L;
    
            // 当前线程
            Thread w = Thread.currentThread();
    
            // 自旋次数
            int spins = -1; // initialized after first item and cancel checks
    
            // 随机数
            ThreadLocalRandom randomYields = null; // bound if needed
    
            for (;;) {
                Object item = s.item;
                //匹配了，可能有其他线程匹配了线程
                if (item != e) {
                    // 撤销该节点
                    s.forgetContents();
                    return LinkedTransferQueue.<E>cast(item);
                }
    
                // 线程中断或者超时了。则调用将s节点item设置为e，等待取消
                if ((w.isInterrupted() || (timed && nanos <= 0)) && s.casItem(e, s)) {        // cancel
                    // 断开节点
                    unsplice(pred, s);
                    return e;
                }
    
                // 自旋
                if (spins < 0) {
                    // 计算自旋次数
                    if ((spins = spinsFor(pred, s.isData)) > 0)
                        randomYields = ThreadLocalRandom.current();
                }
    
                // 自旋
                else if (spins > 0) {
                    --spins;
                    // 生成的随机数 == 0 ，停止线程？不是很明白....
                    if (randomYields.nextInt(CHAINED_SPINS) == 0)
                        Thread.yield();
                }
    
                // 将当前线程设置到节点的waiter域
                // 一开始s.waiter == null 肯定是会成立的，
                else if (s.waiter == null) {
                    s.waiter = w;                 // request unpark then recheck
                }
    
                // 超时阻塞
                else if (timed) {
                    nanos = deadline - System.nanoTime();
                    if (nanos > 0L)
                        LockSupport.parkNanos(this, nanos);
                }
                else {
                    // 不是超时阻塞
                    LockSupport.park(this);
                }
            }
        }
    

整个awaitMatch过程和SynchronousQueue的awaitFulfill没有很大区别，不过在自旋过程会调用Thread.yield();这是干嘛？

在awaitMatch过程中，如果线程中断了，或者超时了则会调用unsplice()方法去除该节点：

    
    
        final void unsplice(Node pred, Node s) {
            s.forgetContents(); // forget unneeded fields
    
            if (pred != null && pred != s && pred.next == s) {
                Node n = s.next;
                if (n == null ||
                        (n != s && pred.casNext(s, n) && pred.isMatched())) {
    
                    for (;;) {               // check if at, or could be, head
                        Node h = head;
                        if (h == pred || h == s || h == null)
                            return;          // at head or list empty
                        if (!h.isMatched())
                            break;
                        Node hn = h.next;
                        if (hn == null)
                            return;          // now empty
                        if (hn != h && casHead(h, hn))
                            h.forgetNext();  // advance head
                    }
                    if (pred.next != pred && s.next != s) { // recheck if offlist
                        for (;;) {           // sweep now if enough votes
                            int v = sweepVotes;
                            if (v < SWEEP_THRESHOLD) {
                                if (casSweepVotes(v, v + 1))
                                    break;
                            }
                            else if (casSweepVotes(v, 0)) {
                                sweep();
                                break;
                            }
                        }
                    }
                }
            }
        }
    

主体流程已经完成，这里总结下：

  1. 无论是入对、出对，还是交换，最终都会跑到xfer(E e, boolean haveData, int how, long nanos)方法中，只不过传入的how不同而已
  2. 如果队列不为空，则尝试在队列中寻找是否存在与该节点相匹配的节点，如果找到则将匹配节点的item设置e，然后唤醒匹配节点的waiter线程。如果是reservation则叫人收货，data则叫null收货
  3. 如果队列为空，或者没有找到匹配的节点且how ！= NOW，则调用tryAppend()方法将节点添加到队列的tail，然后返回其前驱节点
  4. 如果节点的how != NOW && how != ASYNC，则调用awaitMatch()方法阻塞等待，在阻塞等待过程中和SynchronousQuque的awaitFulfill()逻辑差不多，都是先自旋，然后判断是否需要自旋，如果中断或者超时了则将该节点从队列中移出

### 实例

这段摘自[JAVA
1.7并发之LinkedTransferQueue原理理解](http://www.cnblogs.com/rockman12352/p/3790245.html)。感觉看完上面的源码后，在结合这个例子会有更好的了解，掌握。

1：Head->Data Input->Data  
Match: 根据他们的属性 发现 cannot match ，因为是同类的  
处理节点: 所以把新的data放在原来的data后面，然后head往后移一位，Reservation同理  
HEAD=DATA->DATA

2：Head->Data Input->Reservation （取数据）  
Match: 成功match，就把Data的item变为reservation的值（null,有主了），并且返回数据。  
处理节点： 没动，head还在原地  
HEAD=DATA（用过）

3：Head->Reservation Input->Data（放数据）  
Match: 成功match，就把Reservation的item变为Data的值（有主了），并且叫waiter来取  
处理节点： 没动  
HEAD=RESERVATION(用过)

