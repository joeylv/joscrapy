> 作者:liuinsect  
>  原文出处:<http://www.liuinsect.com/?p=69>

* * *

在java.util.concurrent包中，有两个很特殊的工具类，Condition和ReentrantLock，使用过的人都知道，ReentrantLock（重入锁）是jdk的concurrent包提供的一种独占锁的实现。它继承自Dong
Lea的
AbstractQueuedSynchronizer（同步器），确切的说是ReentrantLock的一个内部类继承了AbstractQueuedSynchronizer，ReentrantLock只不过是代理了该类的一些方法，可能有人会问为什么要使用内部类在包装一层？
我想是安全的关系，因为AbstractQueuedSynchronizer中有很多方法，还实现了共享锁，Condition(稍候再细说)等功能，如果直接使ReentrantLock继承它，则很容易出现AbstractQueuedSynchronizer中的API被无用的情况。

言归正传，今天，我们讨论下Condition工具类的实现。

ReentrantLock和Condition的使用方式通常是这样的：

    
    
    public static void main(String[] args) {
        final ReentrantLock reentrantLock = new ReentrantLock();
        final Condition condition = reentrantLock.newCondition();
    
        Thread thread = new Thread((Runnable) () -> {
                try {
                    reentrantLock.lock();
                    System.out.println("我要等一个新信号" + this);
                    condition.wait();
                }
                catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("拿到一个信号！！" + this);
                reentrantLock.unlock();
        }, "waitThread1");
    
        thread.start();
    
        Thread thread1 = new Thread((Runnable) () -> {
                reentrantLock.lock();
                System.out.println("我拿到锁了");
                try {
                    Thread.sleep(3000);
                }
                catch (InterruptedException e) {
                    e.printStackTrace();
                }
                condition.signalAll();
                System.out.println("我发了一个信号！！");
                reentrantLock.unlock();
        }, "signalThread");
    
        thread1.start();
    }
    

运行后，结果如下：

    
    
    我要等一个新信号lock.ReentrantLockTest$1@a62fc3
    我拿到锁了
    我发了一个信号！！
    拿到一个信号！！
    

可以看到，

Condition的执行方式，是当在线程1中调用await方法后，线程1将释放锁，并且将自己沉睡，等待唤醒，

线程2获取到锁后，开始做事，完毕后，调用Condition的signal方法，唤醒线程1，线程1恢复执行。

以上说明Condition是一个多线程间协调通信的工具类，使得某个，或者某些线程一起等待某个条件（Condition）,只有当该条件具备( signal
或者 signalAll方法被带调用)时 ，这些等待线程才会被唤醒，从而重新争夺锁。

那，它是怎么实现的呢？

首先还是要明白，reentrantLock.newCondition()
返回的是Condition的一个实现，该类在AbstractQueuedSynchronizer中被实现，叫做newCondition()

    
    
    public Condition newCondition()   {
      return sync.newCondition();
    }
    

它可以访问AbstractQueuedSynchronizer中的方法和其余内部类（AbstractQueuedSynchronizer是个抽象类，至于他怎么能访问，这里有个很奇妙的点，后面我专门用demo说明
）

现在，我们一起来看下Condition类的实现，还是从上面的demo入手，

为了方便书写，我将AbstractQueuedSynchronizer缩写为AQS

当await被调用时，代码如下：

    
    
    public final void await() throws InterruptedException {
        if (Thread.interrupted())
            throw new InterruptedException();
        Node node = addConditionWaiter(); // 将当前线程包装下后，
                                          // 添加到Condition自己维护的一个链表中。
        int savedState = fullyRelease(node);// 释放当前线程占有的锁，从demo中看到，
                                            // 调用await前，当前线程是占有锁的
    
        int interruptMode = 0;
        while (!isOnSyncQueue(node)) {// 释放完毕后，遍历AQS的队列，看当前节点是否在队列中，
            // 不在 说明它还没有竞争锁的资格，所以继续将自己沉睡。
            // 直到它被加入到队列中，聪明的你可能猜到了，
            // 没有错，在singal的时候加入不就可以了？
            LockSupport.park(this);
            if ((interruptMode = checkInterruptWhileWaiting(node)) != 0)
                break;
        }
        // 被唤醒后，重新开始正式竞争锁，同样，如果竞争不到还是会将自己沉睡，等待唤醒重新开始竞争。
        if (acquireQueued(node, savedState) && interruptMode != THROW_IE)
            interruptMode = REINTERRUPT;
        if (node.nextWaiter != null)
            unlinkCancelledWaiters();
        if (interruptMode != 0)
            reportInterruptAfterWait(interruptMode);
    }
    

回到上面的demo，锁被释放后，线程1开始沉睡，这个时候线程因为线程1沉睡时，会唤醒AQS队列中的头结点，所所以线程2会开始竞争锁，并获取到，等待3秒后，线程2会调用signal方法，“发出”signal信号，signal方法如下：

    
    
    public final void signal() {
        if (!isHeldExclusively())
            throw new IllegalMonitorStateException();
        Node first = firstWaiter; // firstWaiter为condition自己维护的一个链表的头结点，
                                  // 取出第一个节点后开始唤醒操作
        if (first != null)
            doSignal(first);
    }
    

说明下，其实Condition内部维护了等待队列的头结点和尾节点，该队列的作用是存放等待signal信号的线程，该线程被封装为Node节点后存放于此。

    
    
    public class ConditionObject implements Condition, java.io.Serializable {
        private static final long serialVersionUID = 1173984872572414699L;
        /** First node of condition queue. */
        private transient Node firstWaiter;
        /** Last node of condition queue. */
        private transient Node lastWaiter;
    

关键的就在于此，我们知道AQS自己维护的队列是当前等待资源的队列，AQS会在资源被释放后，依次唤醒队列中从前到后的所有节点，使他们对应的线程恢复执行。直到队列为空。

而Condition自己也维护了一个队列，该队列的作用是维护一个等待signal信号的队列，两个队列的作用是不同，事实上，每个线程也仅仅会同时存在以上两个队列中的一个，流程是这样的：

  * 线程1调用reentrantLock.lock时，线程被加入到AQS的等待队列中。
  * 线程1调用await方法被调用时，该线程从AQS中移除，对应操作是锁的释放。
  * 接着马上被加入到Condition的等待队列中，以为着该线程需要signal信号。
  * 线程2，因为线程1释放锁的关系，被唤醒，并判断可以获取锁，于是线程2获取锁，并被加入到AQS的等待队列中。
  * 线程2调用signal方法，这个时候Condition的等待队列中只有线程1一个节点，于是它被取出来，并被加入到AQS的等待队列中。 注意，这个时候，线程1 并没有被唤醒。
  * signal方法执行完毕，线程2调用reentrantLock.unLock()方法，释放锁。这个时候因为AQS中只有线程1，于是，AQS释放锁后按从头到尾的顺序唤醒线程时，线程1被唤醒，于是线程1回复执行。
  * 直到释放所整个过程执行完毕。

可以看到，整个协作过程是靠结点在AQS的等待队列和Condition的等待队列中来回移动实现的，Condition作为一个条件类，很好的自己维护了一个等待信号的队列，并在适时的时候将结点加入到AQS的等待队列中来实现的唤醒操作。

看到这里，signal方法的代码应该不难理解了。

取出头结点，然后doSignal

    
    
    public final void signal() {
        if (!isHeldExclusively()) {
            throw new IllegalMonitorStateException();
        }
        Node first = firstWaiter;
        if (first != null) {
            doSignal(first);
        }
    }
    
    private void doSignal(Node first) {
        do {
            if ((firstWaiter = first.nextWaiter) == null) // 修改头结点，完成旧头结点的移出工作
                lastWaiter = null;
            first.nextWaiter = null;
        } while (!transferForSignal(first) && // 将老的头结点，加入到AQS的等待队列中
                 (first = firstWaiter) != null);
    }
    
    final boolean transferForSignal(Node node) {
        /*
         * If cannot change waitStatus, the node has been cancelled.
         */
        if (!compareAndSetWaitStatus(node, Node.CONDITION, 0))
            return false;
    
        /*
         * Splice onto queue and try to set waitStatus of predecessor to
         * indicate that thread is (probably) waiting. If cancelled or attempt
         * to set waitStatus fails, wake up to resync (in which case the
         * waitStatus can be transiently and harmlessly wrong).
         */
        Node p = enq(node);
        int ws = p.waitStatus;
        // 如果该结点的状态为cancel 或者修改waitStatus失败，则直接唤醒。
        if (ws > 0 || !compareAndSetWaitStatus(p, ws, Node.SIGNAL))
            LockSupport.unpark(node.thread);
        return true;
    }
    

可以看到，正常情况 ws > 0 || !compareAndSetWaitStatus(p, ws,
Node.SIGNAL)这个判断是不会为true的，所以，不会在这个时候唤醒该线程。

只有到发送signal信号的线程调用reentrantLock.unlock()后因为它已经被加到AQS的等待队列中，所以才会被唤醒。

**总结：**

本文从代码的角度说明了Condition的实现方式，其中，涉及到了AQS的很多操作，比如AQS的等待队列实现独占锁功能，不过，这不是本文讨论的重点，等有机会再将AQS的实现单独分享出来。

