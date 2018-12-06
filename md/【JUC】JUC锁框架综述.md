##【JUC】JUC锁框架综述

##
##一、前言

##
##　　在分析完了集合框架后，很有必要接着分析java并发包下面的源码，JUC（java.util.concurrent）源码也是我们学习Java迈进一步的重要过程。我们分为几个模块进行分析，首先是对锁模块的分析。

##
##二、锁框架图

##
##　　在Java并发中，锁是最重要的一个工具，因为锁，才能实现正确的并发访问，所以，先从锁入手一步步进行分析，锁的框架图如下。

##
## ![Alt text](../md/img/616953-20160421215519273-1874262315.png)　　说明：在锁结构框架中乃至并发框架中，AbstractQueuedSynchronizer都占有举足轻重的地位，同时LockSupport也是非常重要的类。

##
##三、具体说明

##
##　　3.1 Condition

##
##　　Condition为接口类型，它将 Object 监视器方法（wait、notify 和 notifyAll）分解成截然不同的对象，以便通过将这些对象与任意 Lock 实现组合使用，为每个对象提供多个等待 set （wait-set）。其中，Lock 替代了 synchronized 方法和语句的使用，Condition 替代了 Object 监视器方法的使用。可以通过await(),signal()来休眠/唤醒线程。

##
##　　3.2 Lock

##
##　　Lock为接口类型，Lock实现提供了比使用synchronized方法和语句可获得的更广泛的锁定操作。此实现允许更灵活的结构，可以具有差别很大的属性，可以支持多个相关的Condition对象。

##
##　　3.3 ReadWriteLock

##
##

##
##　　ReadWriteLock为接口类型， 维护了一对相关的锁，一个用于只读操作，另一个用于写入操作。只要没有 writer，读取锁可以由多个 reader 线程同时保持。写入锁是独占的。

##
##　　3.4 AbstractOwnableSynchonizer

##
##　　AbstractOwnableSynchonizer为抽象类，可以由线程以独占方式拥有的同步器。此类为创建锁和相关同步器（伴随着所有权的概念）提供了基础。AbstractOwnableSynchronizer 类本身不管理或使用此信息。但是，子类和工具可以使用适当维护的值帮助控制和监视访问以及提供诊断。

##
##　　3.5 AbstractQueuedLongSynchronizer

##
##　　AbstractQueuedLongSynchronizer为抽象类，以 long 形式维护同步状态的一个 AbstractQueuedSynchronizer 版本。此类具有的结构、属性和方法与 AbstractQueuedSynchronizer 完全相同，但所有与状态相关的参数和结果都定义为 long 而不是 int。当创建需要 64 位状态的多级别锁和屏障等同步器时，此类很有用。

##
##　　3.6 AbstractQueuedSynchonizer

##
##　　AbstractQueuedSynchonizer为抽象类，其为实现依赖于先进先出 (FIFO) 等待队列的阻塞锁和相关同步器（信号量、事件，等等）提供一个框架。此类的设计目标是成为依靠单个原子 int 值来表示状态的大多数同步器的一个有用基础。 

##
##　　3.7 LockSupport

##
##　　LockSupport为常用类，用来创建锁和其他同步类的基本线程阻塞原语。LockSupport的功能和"Thread中的 Thread.suspend()和Thread.resume()有点类似"，LockSupport中的park() 和 unpark() 的作用分别是阻塞线程和解除阻塞线程。但是park()和unpark()不会遇到“Thread.suspend 和 Thread.resume所可能引发的死锁”问题。

##
##　　3.8 CountDownLatch

##
##　　CountDownLatch为常用类，它是一个同步辅助类，在完成一组正在其他线程中执行的操作之前，它允许一个或多个线程一直等待。

##
##　　3.9 Semaphore

##
##　　Semaphore为常用类，其是一个计数信号量，从概念上讲，信号量维护了一个许可集。如有必要，在许可可用前会阻塞每一个 acquire()，然后再获取该许可。每个 release() 添加一个许可，从而可能释放一个正在阻塞的获取者。但是，不使用实际的许可对象，Semaphore 只对可用许可的号码进行计数，并采取相应的行动。通常用于限制可以访问某些资源（物理或逻辑的）的线程数目。

##
##　　3.10 CyclicBarrier

##
##　　CyclicBarrier为常用类，其是一个同步辅助类，它允许一组线程互相等待，直到到达某个公共屏障点 (common barrier point)。在涉及一组固定大小的线程的程序中，这些线程必须不时地互相等待，此时 CyclicBarrier 很有用。因为该 barrier 在释放等待线程后可以重用，所以称它为循环 的 barrier。 

##
##　　3.11 ReentrantLock

##
##　　ReentrantLock为常用类，它是一个可重入的互斥锁 Lock，它具有与使用 synchronized 方法和语句所访问的隐式监视器锁相同的一些基本行为和语义，但功能更强大。

##
##　　3.12 ReentrantReadWriteLock

##
##　　ReentrantReadWriteLock是读写锁接口ReadWriteLock的实现类，它包括Lock子类ReadLock和WriteLock。ReadLock是共享锁，WriteLock是独占锁。

##
##四、总结

##
##　　JUC中锁框架就介绍到这里，之后会进一步结合源码和示例进行分析，谢谢各位园友的观看~