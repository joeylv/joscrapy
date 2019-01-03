  * 1 入列
  * 2 出列
  * 3 参考资料

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

在上篇博客[【死磕Java并发】—–J.U.C之AQS：AQS简介](http://cmsblogs.com/?p=2174)中提到了AQS内部维护着一个FIFO队列，该队列就是CLH同步队列。

CLH同步队列是一个FIFO双向队列，AQS依赖它来完成同步状态的管理，当前线程如果获取同步状态失败时，AQS则会将当前线程已经等待状态等信息构造成一个节点（Node）并将其加入到CLH同步队列，同时会阻塞当前线程，当同步状态释放时，会把首节点唤醒（公平锁），使其再次尝试获取同步状态。

在CLH同步队列中，一个节点表示一个线程，它保存着线程的引用（thread）、状态（waitStatus）、前驱节点（prev）、后继节点（next），其定义如下：

    
    
    static final class Node {
        /** 共享 */
        static final Node SHARED = new Node();
    
        /** 独占 */
        static final Node EXCLUSIVE = null;
    
        /**
         * 因为超时或者中断，节点会被设置为取消状态，被取消的节点时不会参与到竞争中的，他会一直保持取消状态不会转变为其他状态；
         */
        static final int CANCELLED =  1;
    
        /**
         * 后继节点的线程处于等待状态，而当前节点的线程如果释放了同步状态或者被取消，将会通知后继节点，使后继节点的线程得以运行
         */
        static final int SIGNAL    = -1;
    
        /**
         * 节点在等待队列中，节点线程等待在Condition上，当其他线程对Condition调用了signal()后，改节点将会从等待队列中转移到同步队列中，加入到同步状态的获取中
         */
        static final int CONDITION = -2;
    
        /**
         * 表示下一次共享式同步状态获取将会无条件地传播下去
         */
        static final int PROPAGATE = -3;
    
        /** 等待状态 */
        volatile int waitStatus;
    
        /** 前驱节点 */
        volatile Node prev;
    
        /** 后继节点 */
        volatile Node next;
    
        /** 获取同步状态的线程 */
        volatile Thread thread;
    
        Node nextWaiter;
    
        final boolean isShared() {
            return nextWaiter == SHARED;
        }
    
        final Node predecessor() throws NullPointerException {
            Node p = prev;
            if (p == null)
                throw new NullPointerException();
            else
                return p;
        }
    
        Node() {
        }
    
        Node(Thread thread, Node mode) {
            this.nextWaiter = mode;
            this.thread = thread;
        }
    
        Node(Thread thread, int waitStatus) {
            this.waitStatus = waitStatus;
            this.thread = thread;
        }
    }
    

CLH同步队列结构图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120810001.png)

### 入列

学了数据结构的我们，CLH队列入列是再简单不过了，无非就是tail指向新节点、新节点的prev指向当前最后的节点，当前最后一个节点的next指向当前节点。代码我们可以看看addWaiter(Node
node)方法：

    
    
        private Node addWaiter(Node mode) {
            //新建Node
            Node node = new Node(Thread.currentThread(), mode);
            //快速尝试添加尾节点
            Node pred = tail;
            if (pred != null) {
                node.prev = pred;
                //CAS设置尾节点
                if (compareAndSetTail(pred, node)) {
                    pred.next = node;
                    return node;
                }
            }
            //多次尝试
            enq(node);
            return node;
        }
    

addWaiter(Node node)先通过快速尝试设置尾节点，如果失败，则调用enq(Node node)方法设置尾节点

    
    
        private Node enq(final Node node) {
            //多次尝试，直到成功为止
            for (;;) {
                Node t = tail;
                //tail不存在，设置为首节点
                if (t == null) {
                    if (compareAndSetHead(new Node()))
                        tail = head;
                } else {
                    //设置为尾节点
                    node.prev = t;
                    if (compareAndSetTail(t, node)) {
                        t.next = node;
                        return t;
                    }
                }
            }
        }
    

在上面代码中，两个方法都是通过一个CAS方法compareAndSetTail(Node expect, Node
update)来设置尾节点，该方法可以确保节点是线程安全添加的。在enq(Node
node)方法中，AQS通过“死循环”的方式来保证节点可以正确添加，只有成功添加后，当前线程才会从该方法返回，否则会一直执行下去。

过程图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120810002.png)

### 出列

CLH同步队列遵循FIFO，首节点的线程释放同步状态后，将会唤醒它的后继节点（next），而后继节点将会在获取同步状态成功时将自己设置为首节点，这个过程非常简单，head执行该节点并断开原首节点的next和当前节点的prev即可，注意在这个过程是不需要使用CAS来保证的，因为只有一个线程能够成功获取到同步状态。过程图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120810003.png)

### 参考资料

Doug Lea：《Java并发编程实战》  
方腾飞：《Java并发编程的艺术》

