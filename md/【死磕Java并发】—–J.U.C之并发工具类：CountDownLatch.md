  * 1 实现分析
    * 1.1 await()
    * 1.2 countDown()
    * 1.3 总结
  * 2 应用示例

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

> 此篇博客所有源码均来自JDK 1.8

在上篇博客中介绍了Java四大并发工具一直的CyclicBarrier，今天要介绍的CountDownLatch与CyclicBarrier有点儿相似。

CyclicBarrier所描述的是“允许一组线程互相等待，直到到达某个公共屏障点，才会进行后续任务”，而CountDownLatch所描述的是”在完成一组正在其他线程中执行的操作之前，它允许一个或多个线程一直等待“。在API中是这样描述的：

> 用给定的计数 初始化 CountDownLatch。由于调用了 countDown() 方法，所以在当前计数到达零之前，await
方法会一直受阻塞。之后，会释放所有等待的线程，await 的所有后续调用都将立即返回。这种现象只出现一次——计数无法被重置。如果需要重置计数，请考虑使用
CyclicBarrier。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120818001.png)

CountDownLatch是通过一个计数器来实现的，当我们在new
一个CountDownLatch对象的时候需要带入该计数器值，该值就表示了线程的数量。每当一个线程完成自己的任务后，计数器的值就会减1。当计数器的值变为0时，就表示所有的线程均已经完成了任务，然后就可以恢复等待的线程继续执行了。

虽然，CountDownlatch与CyclicBarrier有那么点相似，但是他们还是存在一些区别的：

  1. CountDownLatch的作用是允许1或N个线程等待其他线程完成执行；而CyclicBarrier则是允许N个线程相互等待
  2. CountDownLatch的计数器无法被重置；CyclicBarrier的计数器可以被重置后使用，因此它被称为是循环的barrier

## 实现分析

CountDownLatch结构如下

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120818002.png)

通过上面的结构图我们可以看到，CountDownLatch内部依赖Sync实现，而Sync继承AQS。CountDownLatch仅提供了一个构造方法：

CountDownLatch(int count) ： 构造一个用给定计数初始化的 CountDownLatch

    
    
        public CountDownLatch(int count) {
            if (count < 0) throw new IllegalArgumentException("count < 0");
            this.sync = new Sync(count);
        }
    

sync为CountDownLatch的一个内部类，其定义如下：

    
    
        private static final class Sync extends AbstractQueuedSynchronizer {
            private static final long serialVersionUID = 4982264981922014374L;
    
            Sync(int count) {
                setState(count);
            }
    
            //获取同步状态
            int getCount() {
                return getState();
            }
    
            //获取同步状态
            protected int tryAcquireShared(int acquires) {
                return (getState() == 0) ? 1 : -1;
            }
    
            //释放同步状态
            protected boolean tryReleaseShared(int releases) {
                for (;;) {
                    int c = getState();
                    if (c == 0)
                        return false;
                    int nextc = c-1;
                    if (compareAndSetState(c, nextc))
                        return nextc == 0;
                }
            }
        }
    

通过这个内部类Sync我们可以清楚地看到CountDownLatch是采用共享锁来实现的。

### await()

CountDownLatch提供await()方法来使当前线程在锁存器倒计数至零之前一直等待，除非线程被中断，定义如下：

    
    
        public void await() throws InterruptedException {
            sync.acquireSharedInterruptibly(1);
        }
    

await其内部使用AQS的acquireSharedInterruptibly(int arg)：

    
    
        public final void acquireSharedInterruptibly(int arg)
                throws InterruptedException {
            if (Thread.interrupted())
                throw new InterruptedException();
            if (tryAcquireShared(arg) < 0)
                doAcquireSharedInterruptibly(arg);
        }
    

在内部类Sync中重写了tryAcquireShared(int arg)方法：

    
    
            protected int tryAcquireShared(int acquires) {
                return (getState() == 0) ? 1 : -1;
            }
    

getState()获取同步状态，其值等于计数器的值，从这里我们可以看到如果计数器值不等于0，则会调用doAcquireSharedInterruptibly(int
arg)，该方法为一个自旋方法会尝试一直去获取同步状态：

    
    
        private void doAcquireSharedInterruptibly(int arg)
                throws InterruptedException {
            final Node node = addWaiter(Node.SHARED);
            boolean failed = true;
            try {
                for (;;) {
                    final Node p = node.predecessor();
                    if (p == head) {
                        /**
                         * 对于CountDownLatch而言，如果计数器值不等于0，那么r 会一直小于0
                         */
                        int r = tryAcquireShared(arg);
                        if (r >= 0) {
                            setHeadAndPropagate(node, r);
                            p.next = null; // help GC
                            failed = false;
                            return;
                        }
                    }
                    //等待
                    if (shouldParkAfterFailedAcquire(p, node) &&
                            parkAndCheckInterrupt())
                        throw new InterruptedException();
                }
            } finally {
                if (failed)
                    cancelAcquire(node);
            }
        }
    

### countDown()

CountDownLatch提供countDown() 方法递减锁存器的计数，如果计数到达零，则释放所有等待的线程。

    
    
        public void countDown() {
            sync.releaseShared(1);
        }
    

内部调用AQS的releaseShared(int arg)方法来释放共享锁同步状态：

    
    
        public final boolean releaseShared(int arg) {
            if (tryReleaseShared(arg)) {
                doReleaseShared();
                return true;
            }
            return false;
        }
    

tryReleaseShared(int arg)方法被CountDownLatch的内部类Sync重写：

    
    
        protected boolean tryReleaseShared(int releases) {
            for (;;) {
                //获取锁状态
                int c = getState();
                //c == 0 直接返回，释放锁成功
                if (c == 0)
                    return false;
                //计算新“锁计数器”
                int nextc = c-1;
                //更新锁状态（计数器）
                if (compareAndSetState(c, nextc))
                    return nextc == 0;
            }
        }
    

### 总结

CountDownLatch内部通过共享锁实现。在创建CountDownLatch实例时，需要传递一个int型的参数：count，该参数为计数器的初始值，也可以理解为该共享锁可以获取的总次数。当某个线程调用await()方法，程序首先判断count的值是否为0，如果不会0的话则会一直等待直到为0为止。当其他线程调用countDown()方法时，则执行释放共享锁状态，使count值
–
1。当在创建CountDownLatch时初始化的count参数，必须要有count线程调用countDown方法才会使计数器count等于0，锁才会释放，前面等待的线程才会继续运行。注意CountDownLatch不能回滚重置。

关于共享锁的请参考：[【死磕Java并发】—–J.U.C之AQS：同步状态的获取与释放]()

## 应用示例

示例仍然使用开会案例。老板进入会议室等待5个人全部到达会议室才会开会。所以这里有两个线程老板等待开会线程、员工到达会议室：

    
    
    public class CountDownLatchTest {
        private static CountDownLatch countDownLatch = new CountDownLatch(5);
    
        /**
         * Boss线程，等待员工到达开会
         */
        static class BossThread extends Thread{
            @Override
            public void run() {
                System.out.println("Boss在会议室等待，总共有" + countDownLatch.getCount() + "个人开会...");
                try {
                    //Boss等待
                    countDownLatch.await();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
    
                System.out.println("所有人都已经到齐了，开会吧...");
            }
        }
    
        //员工到达会议室
        static class EmpleoyeeThread  extends Thread{
            @Override
            public void run() {
                System.out.println(Thread.currentThread().getName() + "，到达会议室....");
                //员工到达会议室 count - 1
                countDownLatch.countDown();
            }
        }
    
        public static void main(String[] args){
            //Boss线程启动
            new BossThread().start();
    
            for(int i = 0 ; i < countDownLatch.getCount() ; i++){
                new EmpleoyeeThread().start();
            }
        }
    }
    

运行结果：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120818003.png)

