  * 1 SynchronousQueue
    * 1.1 TransferQueue
    * 1.2 TransferStack
    * 1.3 公平模式
    * 1.4 非公平模式

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

【注】：SynchronousQueue实现算法看的晕乎乎的，写了好久才写完，如果当中有什么错误之处，忘各位指正

作为BlockingQueue中的一员，SynchronousQueue与其他BlockingQueue有着不同特性：

  1. SynchronousQueue没有容量。与其他BlockingQueue不同，SynchronousQueue是一个不存储元素的BlockingQueue。每一个put操作必须要等待一个take操作，否则不能继续添加元素，反之亦然。
  2. 因为没有容量，所以对应 peek, contains, clear, isEmpty … 等方法其实是无效的。例如clear是不执行任何操作的，contains始终返回false,peek始终返回null。
  3. SynchronousQueue分为公平和非公平，默认情况下采用非公平性访问策略，当然也可以通过构造函数来设置为公平性访问策略（为true即可）。
  4. 若使用 TransferQueue, 则队列中永远会存在一个 dummy node（这点后面详细阐述）。

SynchronousQueue非常适合做交换工作，生产者的线程和消费者的线程同步以传递某些信息、事件或者任务。

# SynchronousQueue

与其他BlockingQueue一样，SynchronousQueue同样继承AbstractQueue和实现BlockingQueue接口：

    
    
    public class SynchronousQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E>, java.io.Serializable
    

SynchronousQueue提供了两个构造函数：

    
    
        public SynchronousQueue() {
            this(false);
        }
    
        public SynchronousQueue(boolean fair) {
            // 通过 fair 值来决定公平性和非公平性
            // 公平性使用TransferQueue，非公平性采用TransferStack
            transferer = fair ? new TransferQueue<E>() : new TransferStack<E>();
        }
    

TransferQueue、TransferStack继承Transferer，Transferer为SynchronousQueue的内部类，它提供了一个方法transfer()，该方法定义了转移数据的规范，如下：

    
    
        abstract static class Transferer<E> {
            abstract E transfer(E e, boolean timed, long nanos);
        }
    

transfer()方法主要用来完成转移数据的，如果e != null，相当于将一个数据交给消费者，如果e ==
null，则相当于从一个生产者接收一个消费者交出的数据。

SynchronousQueue采用队列TransferQueue来实现公平性策略，采用堆栈TransferStack来实现非公平性策略，他们两种都是通过链表实现的，其节点分别为QNode，SNode。TransferQueue和TransferStack在SynchronousQueue中扮演着非常重要的作用，SynchronousQueue的put、take操作都是委托这两个类来实现的。

## TransferQueue

TransferQueue是实现公平性策略的核心类，其节点为QNode，其定义如下：

    
    
        static final class TransferQueue<E> extends Transferer<E> {
            /** 头节点 */
            transient volatile QNode head;
            /** 尾节点 */
            transient volatile QNode tail;
            // 指向一个取消的结点
            //当一个节点中最后一个插入时，它被取消了但是可能还没有离开队列
            transient volatile QNode cleanMe;
    
            /**
             * 省略很多代码O(∩_∩)O
             */
        }
    

在TransferQueue中除了头、尾节点外还存在一个cleanMe节点。该节点主要用于标记，当删除的节点是尾节点时则需要使用该节点。

同时，对于TransferQueue需要注意的是，其队列永远都存在一个dummy node，在构造时创建：

    
    
            TransferQueue() {
                QNode h = new QNode(null, false); // initialize to dummy node.
                head = h;
                tail = h;
            }
    

在TransferQueue中定义了QNode类来表示队列中的节点，QNode节点定义如下：

    
    
        static final class QNode {
            // next 域
            volatile QNode next;
            // item数据项
            volatile Object item;
            //  等待线程，用于park/unpark
            volatile Thread waiter;       // to control park/unpark
            //模式，表示当前是数据还是请求，只有当匹配的模式相匹配时才会交换
            final boolean isData;
    
            QNode(Object item, boolean isData) {
                this.item = item;
                this.isData = isData;
            }
    
            /**
             * CAS next域，在TransferQueue中用于向next推进
             */
            boolean casNext(QNode cmp, QNode val) {
                return next == cmp &&
                        UNSAFE.compareAndSwapObject(this, nextOffset, cmp, val);
            }
    
            /**
             * CAS itme数据项
             */
            boolean casItem(Object cmp, Object val) {
                return item == cmp &&
                        UNSAFE.compareAndSwapObject(this, itemOffset, cmp, val);
            }
    
            /**
             *  取消本结点，将item域设置为自身
             */
            void tryCancel(Object cmp) {
                UNSAFE.compareAndSwapObject(this, itemOffset, cmp, this);
            }
    
            /**
             * 是否被取消
             * 与tryCancel相照应只需要判断item释放等于自身即可
             */
            boolean isCancelled() {
                return item == this;
            }
    
    
            boolean isOffList() {
                return next == this;
            }
    
            private static final sun.misc.Unsafe UNSAFE;
            private static final long itemOffset;
            private static final long nextOffset;
    
            static {
                try {
                    UNSAFE = sun.misc.Unsafe.getUnsafe();
                    Class<?> k = QNode.class;
                    itemOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("item"));
                    nextOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("next"));
                } catch (Exception e) {
                    throw new Error(e);
                }
            }
        }
    

上面代码没啥好看的，需要注意的一点就是isData，该属性在进行数据交换起到关键性作用，两个线程进行数据交换的时候，必须要两者的模式保持一致。

## TransferStack

TransferStack用于实现非公平性，定义如下：

    
    
        static final class TransferStack<E> extends Transferer<E> {
    
            static final int REQUEST    = 0;
    
            static final int DATA       = 1;
    
            static final int FULFILLING = 2;
    
            volatile SNode head;
    
            /**
             * 省略一堆代码  O(∩_∩)O~
             */
    
        }
    

TransferStack中定义了三个状态：REQUEST表示消费数据的消费者，DATA表示生产数据的生产者，FULFILLING，表示匹配另一个生产者或消费者。任何线程对TransferStack的操作都属于上述3种状态中的一种（对应着SNode节点的mode）。同时还包含一个head域，表示头结点。

内部节点SNode定义如下：

    
    
        static final class SNode {
            // next 域
            volatile SNode next;
            // 相匹配的节点
            volatile SNode match;
            // 等待的线程
            volatile Thread waiter;
            // item 域
            Object item;                // data; or null for REQUESTs
    
            // 模型
            int mode;
    
            /**
             * item域和mode域不需要使用volatile修饰，因为它们在volatile/atomic操作之前写，之后读
             */
    
            SNode(Object item) {
                this.item = item;
            }
    
            boolean casNext(SNode cmp, SNode val) {
                return cmp == next &&
                        UNSAFE.compareAndSwapObject(this, nextOffset, cmp, val);
            }
    
            /**
             * 将s结点与本结点进行匹配，匹配成功，则unpark等待线程
             */
            boolean tryMatch(SNode s) {
                if (match == null &&
                        UNSAFE.compareAndSwapObject(this, matchOffset, null, s)) {
                    Thread w = waiter;
                    if (w != null) {    // waiters need at most one unpark
                        waiter = null;
                        LockSupport.unpark(w);
                    }
                    return true;
                }
                return match == s;
            }
    
            void tryCancel() {
                UNSAFE.compareAndSwapObject(this, matchOffset, null, this);
            }
    
            boolean isCancelled() {
                return match == this;
            }
    
            // Unsafe mechanics
            private static final sun.misc.Unsafe UNSAFE;
            private static final long matchOffset;
            private static final long nextOffset;
    
            static {
                try {
                    UNSAFE = sun.misc.Unsafe.getUnsafe();
                    Class<?> k = SNode.class;
                    matchOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("match"));
                    nextOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("next"));
                } catch (Exception e) {
                    throw new Error(e);
                }
            }
        }
    

上面简单介绍了TransferQueue、TransferStack，由于SynchronousQueue的put、take操作都是调用Transfer的transfer()方法，只不过是传递的参数不同而已，put传递的是e参数，所以模式为数据（公平isData
= true，非公平mode= DATA），而take操作传递的是null，所以模式为请求（公平isData = false，非公平mode =
REQUEST），如下：

    
    
        // put操作
        public void put(E e) throws InterruptedException {
            if (e == null) throw new NullPointerException();
            if (transferer.transfer(e, false, 0) == null) {
                Thread.interrupted();
                throw new InterruptedException();
            }
        }
    
        // take操作
        public E take() throws InterruptedException {
            E e = transferer.transfer(null, false, 0);
            if (e != null)
                return e;
            Thread.interrupted();
            throw new InterruptedException();
        }
    

## 公平模式

公平性调用TransferQueue的transfer方法：

    
    
        E transfer(E e, boolean timed, long nanos) {
            QNode s = null;
            // 当前节点模式
            boolean isData = (e != null);
    
            for (;;) {
                QNode t = tail;
                QNode h = head;
                // 头、尾节点 为null，没有初始化
                if (t == null || h == null)
                    continue;
    
                // 头尾节点相等（队列为null） 或者当前节点和队列节点模式一样
                if (h == t || t.isData == isData) {
                    // tn = t.next
                    QNode tn = t.next;
                    // t != tail表示已有其他线程操作了，修改了tail，重新再来
                    if (t != tail)
                        continue;
                    // tn != null，表示已经有其他线程添加了节点，tn 推进，重新处理
                    if (tn != null) {
                        // 当前线程帮忙推进尾节点，就是尝试将tn设置为尾节点
                        advanceTail(t, tn);
                        continue;
                    }
                    //  调用的方法的 wait 类型的, 并且 超时了, 直接返回 null
                    // timed 在take操作阐述
                    if (timed && nanos <= 0)
                        return null;
    
                    // s == null，构建一个新节点Node
                    if (s == null)
                        s = new QNode(e, isData);
    
                    // 将新建的节点加入到队列中，如果不成功，继续处理
                    if (!t.casNext(null, s))
                        continue;
    
                    // 替换尾节点
                    advanceTail(t, s);
    
                    // 调用awaitFulfill, 若节点是 head.next, 则进行自旋
                    // 若不是的话, 直接 block, 直到有其他线程 与之匹配, 或它自己进行线程的中断
                    Object x = awaitFulfill(s, e, timed, nanos);
    
                    // 若返回的x == s表示，当前线程已经超时或者中断，不然的话s == null或者是匹配的节点
                    if (x == s) {
                        // 清理节点S
                        clean(t, s);
                        return null;
                    }
    
                    // isOffList：用于判断节点是否已经从队列中离开了
                    if (!s.isOffList()) {
                        // 尝试将S节点设置为head，移出t
                        advanceHead(t, s);
                        if (x != null)
                            s.item = s;
                        // 释放线程 ref
                        s.waiter = null;
                    }
    
                    // 返回
                    return (x != null) ? (E)x : e;
    
                }
    
                // 这里是从head.next开始，因为TransferQueue总是会存在一个dummy node节点
                else {
                    // 节点
                    QNode m = h.next;
    
                    // 不一致读，重新开始
                    // 有其他线程更改了线程结构
                    if (t != tail || m == null || h != head)
                        continue;
    
                    /**
                     * 生产者producer和消费者consumer匹配操作
                     */
                    Object x = m.item;
                    // isData == (x != null)：判断isData与x的模式是否相同，相同表示已经匹配了
                    // x == m ：m节点被取消了
                    // !m.casItem(x, e)：如果尝试将数据e设置到m上失败
                    if (isData == (x != null) ||  x  == m || !m.casItem(x, e)) {
                        // 将m设置为头结点，h出列，然后重试
                        advanceHead(h, m);
                        continue;
                    }
    
                    // 成功匹配了，m设置为头结点h出列，向前推进
                    advanceHead(h, m);
                    // 唤醒m上的等待线程
                    LockSupport.unpark(m.waiter);
                    return (x != null) ? (E)x : e;
                }
            }
        }
    

整个transfer的算法如下：

  1. 如果队列为null或者尾节点模式与当前节点模式一致，则尝试将节点加入到等待队列中（采用自旋的方式），直到被匹配或、超时或者取消。匹配成功的话要么返回null（producer返回的）要么返回真正传递的值（consumer返回的），如果返回的是node节点本身则表示当前线程超时或者取消了。
  2. 如果队列不为null，且队列的节点是当前节点匹配的节点，则进行数据的传递匹配并返回匹配节点的数据
  3. 在整个过程中都会检测并帮助其他线程推进

当队列为空时，节点入列然后通过调用awaitFulfill()方法自旋，该方法主要用于自旋/阻塞节点，直到节点被匹配返回或者取消、中断。

    
    
        Object awaitFulfill(QNode s, E e, boolean timed, long nanos) {
    
            // 超时控制
            final long deadline = timed ? System.nanoTime() + nanos : 0L;
            Thread w = Thread.currentThread();
            // 自旋次数
            // 如果节点Node恰好是head节点，则自旋一段时间，这里主要是为了效率问题，如果里面阻塞，会存在唤醒、线程上下文切换的问题
            // 如果生产者、消费者者里面到来的话，就避免了这个阻塞的过程
            int spins = ((head.next == s) ?
                    (timed ? maxTimedSpins : maxUntimedSpins) : 0);
            // 自旋
            for (;;) {
                // 线程中断了，剔除当前节点
                if (w.isInterrupted())
                    s.tryCancel(e);
    
                // 如果线程进行了阻塞 -> 唤醒或者中断了，那么x != e 肯定成立，直接返回当前节点即可
                Object x = s.item;
                if (x != e)
                    return x;
                // 超时判断
                if (timed) {
                    nanos = deadline - System.nanoTime();
                    // 如果超时了，取消节点,continue，在if(x != e)肯定会成立，直接返回x
                    if (nanos <= 0L) {
                        s.tryCancel(e);
                        continue;
                    }
                }
    
                // 自旋- 1
                if (spins > 0)
                    --spins;
    
                // 等待线程
                else if (s.waiter == null)
                    s.waiter = w;
    
                // 进行没有超时的 park
                else if (!timed)
                    LockSupport.park(this);
    
                // 自旋次数过了, 直接 + timeout 方式 park
                else if (nanos > spinForTimeoutThreshold)
                    LockSupport.parkNanos(this, nanos);
            }
        }
    

在自旋/阻塞过程中做了一点优化，就是判断当前节点是否为对头元素，如果是的则先自旋，如果自旋次数过了，则才阻塞，这样做的主要目的就在如果生产者、消费者立马来匹配了则不需要阻塞，因为阻塞、唤醒会消耗资源。在整个自旋的过程中会不断判断是否超时或者中断了，如果中断或者超时了则调用tryCancel()取消该节点。

**tryCancel**

    
    
                void tryCancel(Object cmp) {
                    UNSAFE.compareAndSwapObject(this, itemOffset, cmp, this);
                }
    

取消过程就是将节点的item设置为自身（itemOffset是item的偏移量）。所以在调用awaitFulfill()方法时，如果当前线程被取消、中断、超时了那么返回的值肯定时S，否则返回的则是匹配的节点。如果返回值是节点S，那么if(x
== s)必定成立，如下：

    
    
                        Object x = awaitFulfill(s, e, timed, nanos);
                        if (x == s) {                   // wait was cancelled
                            clean(t, s);
                            return null;
                        }
    

如果返回的x == s成立，则调用clean()方法清理节点S：

    
    
        void clean(QNode pred, QNode s) {
            //
            s.waiter = null;
    
            while (pred.next == s) {
                QNode h = head;
                QNode hn = h.next;
                // hn节点被取消了，向前推进
                if (hn != null && hn.isCancelled()) {
                    advanceHead(h, hn);
                    continue;
                }
    
                // 队列为空，直接return null
                QNode t = tail;
                if (t == h)
                    return;
    
                QNode tn = t.next;
                // 不一致，说明有其他线程改变了tail节点，重新开始
                if (t != tail)
                    continue;
    
                // tn != null 推进tail节点，重新开始
                if (tn != null) {
                    advanceTail(t, tn);
                    continue;
                }
    
                // s 不是尾节点 移出
                if (s != t) {
                    QNode sn = s.next;
                    // 如果s已经被移除退出循环，否则尝试断开s
                    if (sn == s || pred.casNext(s, sn))
                        return;
                }
    
                // s是尾节点，则有可能会有其他线程在添加新节点，则cleanMe出场
                QNode dp = cleanMe;
                // 如果dp不为null，说明是前一个被取消节点，将其移除
                if (dp != null) {
                    QNode d = dp.next;
                    QNode dn;
                    if (d == null ||               // 节点d已经删除
                            d == dp ||                 // 原来的节点 cleanMe 已经通过 advanceHead 进行删除
                            !d.isCancelled() ||        // 原来的节点 s已经删除
                            (d != t &&                 // d 不是tail节点
                                    (dn = d.next) != null &&  //
                                    dn != d &&                //   that is on list
                                    dp.casNext(d, dn)))       // d unspliced
                        // 清除 cleanMe 节点, 这里的 dp == pred 若成立, 说明清除节点s，成功, 直接return, 不然的话要再次循环
                        casCleanMe(dp, null);
                    if (dp == pred)
                        return;
                } else if (casCleanMe(null, pred))  // 原来的 cleanMe 是 null, 则将 pred 标记为 cleamMe 为下次 清除 s 节点做标识
                    return;
            }
        }
    

这个clean()方法感觉有点儿难度，我也看得不是很懂。这里是引用<http://www.jianshu.com/p/95cb570c8187>

  1. 删除的节点不是queue尾节点, 这时 直接 pred.casNext(s, s.next) 方式来进行删除(和ConcurrentLikedQueue中差不多)
  2. 删除的节点是队尾节点 
    * 此时 cleanMe == null, 则 前继节点pred标记为 cleanMe, 为下次删除做准备
    * 此时 cleanMe != null, 先删除上次需要删除的节点, 然后将 cleanMe至null, 让后再将 pred 赋值给 cleanMe

## 非公平模式

非公平模式transfer方法如下：

    
    
        E transfer(E e, boolean timed, long nanos) {
            SNode s = null; // constructed/reused as needed
            int mode = (e == null) ? REQUEST : DATA;
    
            for (;;) {
                SNode h = head;
                // 栈为空或者当前节点模式与头节点模式一样，将节点压入栈内，等待匹配
                if (h == null || h.mode == mode) {
                    // 超时
                    if (timed && nanos <= 0) {
                        // 节点被取消了，向前推进
                        if (h != null && h.isCancelled())
                            //  重新设置头结点（弹出之前的头结点）
                            casHead(h, h.next);
                        else
                            return null;
                    }
                    // 不超时
                    // 生成一个SNode节点，并尝试替换掉头节点head (head -> s)
                    else if (casHead(h, s = snode(s, e, h, mode))) {
                        // 自旋，等待线程匹配
                        SNode m = awaitFulfill(s, timed, nanos);
                        // 返回的m == s 表示该节点被取消了或者超时、中断了
                        if (m == s) {
                            // 清理节点S，return null
                            clean(s);
                            return null;
                        }
    
                        // 因为通过前面一步将S替换成了head，如果h.next == s ，则表示有其他节点插入到S前面了,变成了head
                        // 且该节点就是与节点S匹配的节点
                        if ((h = head) != null && h.next == s)
                            // 将s.next节点设置为head，相当于取消节点h、s
                            casHead(h, s.next);
    
                        // 如果是请求则返回匹配的域，否则返回节点S的域
                        return (E) ((mode == REQUEST) ? m.item : s.item);
                    }
                }
    
                // 如果栈不为null，且两者模式不匹配（h != null && h.mode != mode）
                // 说明他们是一队对等匹配的节点，尝试用当前节点s来满足h节点
                else if (!isFulfilling(h.mode)) {
                    // head 节点已经取消了，向前推进
                    if (h.isCancelled())
                        casHead(h, h.next);
    
                    // 尝试将当前节点打上"正在匹配"的标记，并设置为head
                    else if (casHead(h, s=snode(s, e, h, FULFILLING|mode))) {
                        // 循环loop
                        for (;;) {
                            // s为当前节点，m是s的next节点，
                            // m节点是s节点的匹配节点
                            SNode m = s.next;
                            // m == null，其他节点把m节点匹配走了
                            if (m == null) {
                                // 将s弹出
                                casHead(s, null);
                                // 将s置空，下轮循环的时候还会新建
                                s = null;
                                // 退出该循环，继续主循环
                                break;
                            }
                            // 获取m的next节点
                            SNode mn = m.next;
                            // 尝试匹配
                            if (m.tryMatch(s)) {
                                // 匹配成功，将s 、 m弹出
                                casHead(s, mn);     // pop both s and m
                                return (E) ((mode == REQUEST) ? m.item : s.item);
                            } else
                                // 如果没有匹配成功，说明有其他线程已经匹配了，把m移出
                                s.casNext(m, mn);
                        }
                    }
                }
                // 到这最后一步说明节点正在匹配阶段
                else {
                    // head 的next的节点，是正在匹配的节点，m 和 h配对
                    SNode m = h.next;
    
                    // m == null 其他线程把m节点抢走了，弹出h节点
                    if (m == null)
                        casHead(h, null);
                    else {
                        SNode mn = m.next;
                        if (m.tryMatch(h))
                            casHead(h, mn);
                        else
                            h.casNext(m, mn);
                    }
                }
            }
        }
    

整个处理过程分为三种情况，具体如下：

  1. 如果当前栈为空获取节点模式与栈顶模式一样，则尝试将节点加入栈内，同时通过自旋方式等待节点匹配，最后返回匹配的节点或者null（被取消）
  2. 如果栈不为空且节点的模式与首节点模式匹配，则尝试将该节点打上FULFILLING标记，然后加入栈中，与相应的节点匹配，成功后将这两个节点弹出栈并返回匹配节点的数据
  3. 如果有节点在匹配，那么帮助这个节点完成匹配和出栈操作，然后在主循环中继续执行

当节点加入栈内后，通过调用awaitFulfill()方法自旋等待节点匹配：

    
    
        SNode awaitFulfill(SNode s, boolean timed, long nanos) {
            // 超时
            final long deadline = timed ? System.nanoTime() + nanos : 0L;
            // 当前线程
            Thread w = Thread.currentThread();
    
            // 自旋次数
            // shouldSpin 用于检测当前节点是否需要自旋
            // 如果栈为空、该节点是首节点或者该节点是匹配节点，则先采用自旋，否则阻塞
            int spins = (shouldSpin(s) ?
                    (timed ? maxTimedSpins : maxUntimedSpins) : 0);
            for (;;) {
                // 线程中断了，取消该节点
                if (w.isInterrupted())
                    s.tryCancel();
    
                // 匹配节点
                SNode m = s.match;
    
                // 如果匹配节点m不为空，则表示匹配成功，直接返回
                if (m != null)
                    return m;
                // 超时
                if (timed) {
                    nanos = deadline - System.nanoTime();
                    // 节点超时，取消
                    if (nanos <= 0L) {
                        s.tryCancel();
                        continue;
                    }
                }
    
                // 自旋;每次自旋的时候都需要检查自身是否满足自旋条件，满足就 - 1，否则为0
                if (spins > 0)
                    spins = shouldSpin(s) ? (spins-1) : 0;
    
                // 第一次阻塞时，会将当前线程设置到s上
                else if (s.waiter == null)
                    s.waiter = w;
    
                // 阻塞 当前线程
                else if (!timed)
                    LockSupport.park(this);
                // 超时
                else if (nanos > spinForTimeoutThreshold)
                    LockSupport.parkNanos(this, nanos);
            }
        }
    

awaitFulfill()方法会一直自旋/阻塞直到匹配节点。在S节点阻塞之前会先调用shouldSpin()方法判断是否采用自旋方式，为的就是如果有生产者或者消费者马上到来，就不需要阻塞了，在多核条件下这种优化是有必要的。同时在调用park()阻塞之前会将当前线程设置到S节点的waiter上。匹配成功，返回匹配节点m。

shouldSpin()方法如下：

    
    
            boolean shouldSpin(SNode s) {
                SNode h = head;
                return (h == s || h == null || isFulfilling(h.mode));
            }
    

同时在阻塞过程中会一直检测当前线程是否中断了，如果中断了，则调用tryCancel()方法取消该节点，取消过程就是将当前节点的math设置为当前节点。所以如果线程中断了，那么在返回m时一定是S节点自身。

    
    
                void tryCancel() {
                    UNSAFE.compareAndSwapObject(this, matchOffset, null, this);
                }
    

awaitFullfill()方法如果返回的m == s，则表示当前节点已经中断取消了，则需要调用clean()方法，清理节点S：

    
    
        void clean(SNode s) {
    
            // 清理item域
            s.item = null;
            // 清理waiter域
            s.waiter = null;
    
            // past节点
            SNode past = s.next;
            if (past != null && past.isCancelled())
                past = past.next;
    
            // 从栈顶head节点，取消从栈顶head到past节点之间所有已经取消的节点
            // 注意：这里如果遇到一个节点没有取消，则会退出while
            SNode p;
            while ((p = head) != null && p != past && p.isCancelled())
                casHead(p, p.next);     // 如果p节点已经取消了，则剔除该节点
    
            // 如果经历上面while p节点还没有取消，则再次循环取消掉所有p 到past之间的取消节点
            while (p != null && p != past) {
                SNode n = p.next;
                if (n != null && n.isCancelled())
                    p.casNext(n, n.next);
                else
                    p = n;
            }
        }
    

clean()方法就是将head节点到S节点之间所有已经取消的节点全部移出。【不清楚为何要用两个while，一个不行么】

至此，SynchronousQueue的源码分析完成了，说下我个人感觉吧：
**个人感觉SynchronousQueue实现好复杂（可能是自己智商不够吧~~~~(
>_<)~~~~），源码看了好久，这篇博客写了将近一个星期，如果有什么错误之处，烦请各位指正！！**

