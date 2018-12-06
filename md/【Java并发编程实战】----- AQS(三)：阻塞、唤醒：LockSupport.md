##【Java并发编程实战】----- AQS(三)：阻塞、唤醒：LockSupport

##
##在上篇博客（【Java并发编程实战】----- AQS(二)：获取锁、释放锁）中提到，当一个线程加入到CLH队列中时，如果不是头节点是需要判断该节点是否需要挂起；在释放锁后，需要唤醒该线程的继任节点  

##
##lock方法，在调用acquireQueued()：     	if (shouldParkAfterFailedAcquire(p, node) &amp;&amp;                    parkAndCheckInterrupt())                    interrupted = true;

##
##在acquireQueued()中调用parkAndCheckInterrupt()来挂起当前线程：  	private final boolean parkAndCheckInterrupt() {        LockSupport.park(this);        return Thread.interrupted();    	}

##
##调用LockSupport.park()方法。对于park()：为了线程调度，在许可可用之前禁用当前线程。

##
##释放锁后，需要唤醒该线程继任节点：  	public final boolean release(int arg) {        if (tryRelease(arg)) {            Node h = head;            if (h != null &amp;&amp; h.waitStatus != 0)                unparkSuccessor(h);            return true;        	}        return false;    	}

##
##在release方法中调用unparkSuccessor()来唤醒该线程的继任节点。在unparkSuccessor()方法中通过LockSupport.unpark()来唤醒。unpark():如果给定线程的许可尚不可用，则使其可用。LockSupport

##
##LockSupport是用来创建锁和其他同步类的基本线程阻塞原语。每个使用LockSupport的线程都会与一个许可关联，如果该许可可用，并且可在进程中使用，则调用park()将会立即返回，否则可能阻塞。如果许可尚不可用，则可以调用 unpark 使其可用。但是注意许可不可重入，也就是说只能调用一次park()方法，否则会一直阻塞。

##
##LockSupport.park()、LockSupport.unpark()的作用分别是阻塞线程和解除阻塞线程，且park()和unpark()不会遇到“Thread.suspend ()和 Thread.resume所可能引发的死锁”问题。当然park()、unpark()是成对使用。

##
##park()：如果许可可用，则使用该许可，并且该调用立即返回；否则，为线程调度禁用当前线程，并在发生以下三种情况之一以前，使其处于休眠状态： 其他某个线程将当前线程作为目标调用 unpark；或者 其他某个线程中断当前线程；或者 该调用不合逻辑地（即毫无理由地）返回。   

##
##其源码实现如下：      	public static void park() {        unsafe.park(false, 0L);    	}    

##
##unpark:如果给定线程的许可尚不可用，则使其可用。如果线程在 park 上受阻塞，则它将解除其阻塞状态。否则，保证下一次调用 park 不会受阻塞。如果给定线程尚未启动，则无法保证此操作有任何效果。  

##
##其源代码如下：      	public static void unpark(Thread thread) {        if (thread != null) {             Object lock = unsafe.getObject(thread, lockOffset);            synchronized (lock) {                 if (thread.isAlive()) {                     unsafe.unpark(thread);                 	}             	}         	}     	}    

##
##  

##
##一般来说park()、unpark()是成对出现的，同时unpark必须要在park执行之后执行，当然并不是说没有不调用unpark线程就会一直阻塞，park有一个方法，它带了时间戳（parkNanos(long nanos)：为了线程调度禁用当前线程，最多等待指定的等待时间，除非许可可用。）  

##
##  

##
##参考资料  

##
##1、LockSupport的park和unpark的基本使用,以及对线程中断的响应性  