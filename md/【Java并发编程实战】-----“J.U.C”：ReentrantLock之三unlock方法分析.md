前篇博客LZ已经分析了ReentrantLock的lock()实现过程，我们了解到lock实现机制有公平锁和非公平锁，两者的主要区别在于公平锁要按照CLH队列等待获取锁，而非公平锁无视CLH队列直接获取锁。但是对于unlock()而已，它是不分为公平锁和非公平锁的。

    
    
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

release(1)，尝试在当前锁的锁定计数（state）值上减1。成功返回true，否则返回false。当然在release()方法中不仅仅只是将state
- 1这么简单，- 1之后还需要进行一番处理，如果-1之后的新state = 0
，则表示当前锁已经被线程释放了，同时会唤醒线程等待队列中的下一个线程，当然该锁不一定就一定会把所有权交给下一个线程，能不能成功就看它是不是亲爹生的了（看运气）。

    
    
    protected final boolean tryRelease(int releases) {
            int c = getState() - releases;   //state - 1
            //判断是否为当前线程在调用，不是抛出IllegalMonitorStateException异常
            if (Thread.currentThread() != getExclusiveOwnerThread())   
                throw new IllegalMonitorStateException();
            boolean free = false;
            //c == 0,释放该锁，同时将当前所持有线程设置为null
            if (c == 0) {
                free = true;
                setExclusiveOwnerThread(null);
            }
            //设置state
            setState(c);
            return free;
        }

在release代码中有一段代码很重要：

    
    
    Node h = head;
                if (h != null && h.waitStatus != 0)
                    unparkSuccessor(h);
                return true;

对于这个LZ在前篇博客已经较为详细的阐述了。不懂或者忘记请再次翻阅：【Java并发编程实战】-----“J.U.C”：ReentrantLock之二lock方法分析

waitStatus!=0表明或者处于CANCEL状态，或者是置SIGNAL表示下一个线程在等待其唤醒。也就是说waitStatus不为零表示它的后继在等待唤醒。

unparkSuccessor()方法：

    
    
    private void unparkSuccessor(Node node) {
            int ws = node.waitStatus;
            //如果waitStatus < 0 则将当前节点清零
            if (ws < 0)
                compareAndSetWaitStatus(node, ws, 0);
    
            //若后续节点为空或已被cancel，则从尾部开始找到队列中第一个waitStatus<=0，即未被cancel的节点
            Node s = node.next;
            if (s == null || s.waitStatus > 0) {
                s = null;
                for (Node t = tail; t != null && t != node; t = t.prev)
                    if (t.waitStatus <= 0)
                        s = t;
            }
            if (s != null)
                LockSupport.unpark(s.thread);
        }

**注：unlock最好放在finally中！！！！！！unlock最好放在finally中！！！！！！ unlock最好放在finally中！！！！！！
（重要的事说三遍）**

参考文献：

1、[Java多线程系列--“JUC锁”04之
公平锁(二)](http://www.cnblogs.com/skywang12345/p/3496609.html)

