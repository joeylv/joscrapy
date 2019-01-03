在我们的实际应用当中可能经常会遇到这样一个场景：多个线程读或者、写相同的数据，访问相同的文件等等。对于这种情况如果我们不加以控制，是非常容易导致错误的。在java中，为了解决这个问题，引入临界区概念。所谓
**临界区是指一个访问共用资源的程序片段，而这些共用资源又无法同时被多个线程访问。**

在java中为了实现临界区提供了同步机制。当一个线程试图访问一个临界区时，他将使用一种同步机制来查看是不是已经有其他线程进入临界区。如果没有则他就可以进入临界区，否则他就会被同步机制挂起，指定进入的线程离开这个临界区。

临界区规定：每次只准许一个进程进入临界区，进入后不允许其他进程进入。调度法则为（百度百科）：

1、如果有若干进程要求进入空闲的临界区，一次仅允许一个进程进入。

2、任何时候，处于临界区内的进程不可多于一个。如已有进程进入自己的临界区，则其它所有试图进入临界区的进程必须等待。

3、进入临界区的进程要在有限时间内退出，以便其它进程能及时进入自己的临界区。

4、如果进程不能进入自己的临界区，则应让出CPU，避免进程出现“忙等”现象。

下面介绍使用synchronized关键字来实现同步机制。

# 一、synchronized关键字

## 1.1、简介

synchronized，我们谓之锁，主要用来给方法、代码块加锁。当某个方法或者代码块使用synchronized时，那么在同一时刻至多仅有有一个线程在执行该段代码。当有多个线程访问同一对象的加锁方法/代码块时，同一时间只有一个线程在执行，其余线程必须要等待当前线程执行完之后才能执行该代码段。但是，其余线程是可以访问该对象中的非加锁代码块的。

synchronized主要包括两种方法：synchronized 方法、synchronized 块。

## 1.2、synchronized 方法

通过在方法声明中加入 synchronized关键字来声明 synchronized 方法。如：

    
    
    public synchronized void getResult();

synchronized方法控制对类成员变量的访问。它是如何来避免类成员变量的访问控制呢？我们知道方法使用了synchronized关键字表明该方法已加锁，在任一线程在访问改方法时都必须要判断该方法是否有其他线程在“独占”。每个类实例对应一个把锁，每个synchronized方法都必须调用该方法的类实例的锁方能执行，否则所属线程阻塞，方法一旦执行，就独占该锁，直到从该方法返回时才将锁释放，被阻塞的线程方能获得该锁。

其实synchronized方法是存在缺陷的，如果我们将一个很大的方法声明为synchronized将会大大影响效率的。如果多个线程在访问一个synchronized方法，那么同一时刻只有一个线程在执行该方法，而其他线程都必须等待，但是如果该方法没有使用synchronized，则所有线程可以在同一时刻执行它，减少了执行的总时间。所以如果我们知道一个方法不会被多个线程执行到或者说不存在资源共享的问题，则不需要使用synchronized关键字。但是如果一定要使用synchronized关键字，那么我们可以synchronized代码块来替换synchronized方法。

## 1.3、synchronized 块

synchronized代码块所起到的作用和synchronized方法一样，只不过它使临界区变的尽可能短了，换句话说：它只把需要的共享数据保护起来，其余的长代码块留出此操作。语法如下：

    
    
    synchronized(object) {  
        //允许访问控制的代码  
    }

如果我们需要以这种方式来使用synchronized关键字,那么必须要通过一个对象引用来作为参数,通常这个参数我们常使用为this.

    
    
    synchronized (this) {
        //允许访问控制的代码 
    }

对于synchronized(this)有如下理解：

1、当两个并发线程访问同一个对象object中的这个synchronized(this)同步代码块时，一个时间内只能有一个线程得到执行。另一个线程必须等待当前线程执行完这个代码块以后才能执行该代码块。

2、然而，当一个线程访问object的一个synchronized(this)同步代码块时，另一个线程仍然可以访问object中的非synchronized(this)同步代码块。

3、尤其关键的是，当一个线程访问object的一个synchronized(this)同步代码块时，其他线程对object中所有其他synchronized(this)同步代码块得访问将被阻塞。

4、第三个例子同样适用其他同步代码块。也就是说，当一个线程访问object的一个synchronized(this)同步代码块时，它就获得了这个object的对象锁。结果，其他线程对该object对象所有同步代码部分的访问都将被暂时阻塞。

5、以上规则对其他对象锁同样适用

<http://freewxy.iteye.com/blog/978159>，这篇博客使用实例对上面四点进行了较为详细的说明，这里就不多阐述了。

<http://www.cnblogs.com/GnagWang/archive/2011/02/27/1966606.html>这篇博客对synchronized的使用举了一个很不错的例子（拿钥匙进房间）。这里由于篇幅问题LZ就不多阐述了，下面我们来刨刨synchronized稍微高级点的东西。

## 1.4、进阶

在java多线程中存在一个“先来后到”的原则，也就是说谁先抢到钥匙，谁先用。我们知道为避免资源竞争产生问题，java使用同步机制来避免，而同步机制是使用锁概念来控制的。那么在Java程序当中，锁是如何体现的呢？这里我们需要弄清楚两个概念：

### 什么是锁？

什么是锁？在日常生活中，它就是一个加在门、箱子、抽屉等物体上的封缄器，防止别人偷窥或者偷盗，起到一个保护的作用。在java中同样如此，锁对对象起到一个保护的作用，一个线程如果独占了某个资源，那么其他的线程别想用，想用？等我用完再说吧！

在java程序运行环境中，JVM需要对两类线程共享的数据进行协调：

1、保存在堆中的实例变量

2、保存在方法区中的类变量。

在java虚拟机中，每个对象和类在逻辑上都是和一个监视器相关联的。对于对象来说，相关联的监视器保护对象的实例变量。
对于类来说，监视器保护类的类变量。如果一个对象没有实例变量，或者说一个类没有变量，相关联的监视器就什么也不监视。

为了实现监视器的排他性监视能力，java虚拟机为每一个对象和类都关联一个锁。代表任何时候只允许一个线程拥有的特权。线程访问实例变量或者类变量不需锁。
如果某个线程获取了锁，那么在它释放该锁之前其他线程是不可能获取同样锁的。一个线程可以多次对同一个对象上锁。对于每一个对象，java虚拟机维护一个加锁计数器，线程每获得一次该对象，计数器就加1，每释放一次，计数器就减
1，当计数器值为0时，锁就被完全释放了。  
java编程人员不需要自己动手加锁，对象锁是java虚拟机内部使用的。在java程序中，只需要使用synchronized块或者synchronized方法就可以标志一个监视区域。当每次进入一个监视区域时，java
虚拟机都会自动锁上对象或者类。（摘自[java的锁机制](http://blog.csdn.net/yangzhijun_cau/article/details/6432216)）。

### 锁的是什么？

在这个问题之前我们必须要明确一点：无论synchronized关键字加在方法上还是对象上，它取得的锁都是对象。在java中每一个对象都可以作为锁，它主要体现在下面三个方面：

* 对于同步方法，锁是当前实例对象。 
* 对于同步方法块，锁是Synchonized括号里配置的对象。
* 对于静态同步方法，锁是当前对象的Class对象。 

首先我们先看下面例子：

    
    
    public class ThreadTest_01 implements Runnable{
    
        @Override
        public synchronized void run() {
            for(int i = 0 ; i < 3 ; i++){
                System.out.println(Thread.currentThread().getName() + "run......");
            }
        }
        
        public static void main(String[] args) {
            for(int i = 0 ; i < 5 ; i++){
                new Thread(new ThreadTest_01(),"Thread_" + i).start();
            }
        }
    }

部分运行结果：

    
    
    Thread_2run......
    Thread_2run......
    Thread_4run......
    Thread_4run......
    Thread_3run......
    Thread_3run......
    Thread_3run......
    Thread_2run......
    Thread_4run......

这个结果与我们预期的结果有点不同（这些线程在这里乱跑），照理来说，run方法加上synchronized关键字后，会产生同步效果，这些线程应该是一个接着一个执行run方法的。在上面LZ提到，一个成员方法加上synchronized关键字后，实际上就是给这个成员方法加上锁，具体点就是以这个成员方法所在的对象本身作为对象锁。但是在这个实例当中我们一共new了10个ThreadTest对象，那个每个线程都会持有自己线程对象的对象锁，这必定不能产生同步的效果。所以：
**如果要对这些线程进行同步，那么这些线程所持有的对象锁应当是共享且唯一的！**

_这个时候synchronized锁住的是那个对象？它锁住的就是调用这个同步方法对象。就是说threadTest这个对象在不同线程中执行同步方法，就会形成互斥。达到同步的效果。_
所以将上面的new Thread(new ThreadTest_01(),"Thread_" + i).start(); 修改为new
Thread(threadTest,"Thread_" + i).start();就可以了。

对于同步方法，锁是当前实例对象。

上面实例是使用synchronized方法，我们在看看synchronized代码块：

    
    
    public class ThreadTest_02 extends Thread{
    
        private String lock ;
        private String name;
        
        public ThreadTest_02(String name,String lock){
            this.name = name;
            this.lock = lock;
        }
        
        @Override
        public void run() {
            synchronized (lock) {
                for(int i = 0 ; i < 3 ; i++){
                    System.out.println(name + " run......");
                }
            }
        }
        
        public static void main(String[] args) {
            String lock  = new String("test");
            for(int i = 0 ; i < 5 ; i++){
                new ThreadTest_02("ThreadTest_" + i,lock).start();
            }
        }
    }

运行结果：

    
    
    ThreadTest_0 run......
    ThreadTest_0 run......
    ThreadTest_0 run......
    ThreadTest_1 run......
    ThreadTest_1 run......
    ThreadTest_1 run......
    ThreadTest_4 run......
    ThreadTest_4 run......
    ThreadTest_4 run......
    ThreadTest_3 run......
    ThreadTest_3 run......
    ThreadTest_3 run......
    ThreadTest_2 run......
    ThreadTest_2 run......
    ThreadTest_2 run......

在main方法中我们创建了一个String对象lock，并将这个对象赋予每一个ThreadTest2线程对象的私有变量lock。我们知道java中存在一个字符串池，那么这些线程的lock私有变量实际上指向的是堆内存中的同一个区域，即存放main函数中的lock变量的区域，所以对象锁是唯一且共享的。线程同步！！

在这里synchronized锁住的就是lock这个String对象。

对于同步方法块，锁是Synchonized括号里配置的对象。

    
    
    public class ThreadTest_03 extends Thread{
    
        public synchronized static void test(){
            for(int i = 0 ; i < 3 ; i++){
                System.out.println(Thread.currentThread().getName() + " run......");
            }
        }
        
        @Override
        public void run() {
            test();
        }
    
        public static void main(String[] args) {
            for(int i = 0 ; i < 5 ; i++){
                new ThreadTest_03().start();
            }
        }
    }

运行结果：

    
    
    Thread-0 run......
    Thread-0 run......
    Thread-0 run......
    Thread-4 run......
    Thread-4 run......
    Thread-4 run......
    Thread-1 run......
    Thread-1 run......
    Thread-1 run......
    Thread-2 run......
    Thread-2 run......
    Thread-2 run......
    Thread-3 run......
    Thread-3 run......
    Thread-3 run......

在这个实例中，run方法使用的是一个同步方法，而且是static的同步方法，那么这里synchronized锁的又是什么呢？我们知道static超脱于对象之外，它属于类级别的。所以，对象锁就是该静态放发所在的类的Class实例。由于在JVM中，所有被加载的类都有唯一的类对象，在该实例当中就是唯一的
ThreadTest_03.class对象。不管我们创建了该类的多少实例，但是它的类实例仍然是一个！所以对象锁是唯一且共享的。线程同步！！

对于静态同步方法，锁是当前对象的Class对象。

**_如果一个类中定义了一个synchronized的static函数A，也定义了一个synchronized的instance函数B，那么这个类的同一对象Obj,在多线程中分别访问A和B两个方法时，不会构成同步，因为它们的锁都不一样。A方法的锁是Obj这个对象，而B的锁是Obj所属的那个Class。_**

### 锁的升级

java中锁一共有四种状态，无锁状态，偏向锁状态，轻量级锁状态和重量级锁状态，它会随着竞争情况逐渐升级。锁可以升级但不能降级，意味着偏向锁升级成轻量级锁后不能降级成偏向锁。这种锁升级却不能降级的策略，目的是为了提高获得锁和释放锁的效率。下面主要部分主要是对博客：[聊聊并发（二）Java
SE1.6中的Synchronized](http://ifeve.com/java-synchronized/)的总结。

**锁自旋**

我们知道在当某个线程在进入同步方法/代码块时若发现该同步方法/代码块被其他现在所占，则它就要等待，进入阻塞状态，这个过程性能是低下的。

在遇到锁的争用或许等待事，线程可以不那么着急进入阻塞状态，而是等一等，看看锁是不是马上就释放了，这就是锁自旋。锁自旋在一定程度上可以对线程进行优化处理。

**偏向锁**

**偏向锁主要为了解决在没有竞争情况下锁的性能问题。**
在大多数情况下锁锁不仅不存在多线程竞争，而且总是由同一线程多次获得，为了让线程获得锁的代价更低而引入了偏向锁。当某个线程获得锁的情况，该线程是可以多次锁住该对象，但是每次执行这样的操作都会因为CAS（CPU的Compare-
And-
Swap指令）操作而造成一些开销消耗性能，为了减少这种开销，这个锁会偏向于第一个获得它的线程，如果在接下来的执行过程中，该锁没有被其他的线程获取，则持有偏向锁的线程将永远不需要再进行同步。

当有其他线程在尝试着竞争偏向锁时，持有偏向锁的线程就会释放锁。

**锁膨胀**

多个或多次调用粒度太小的锁，进行加锁解锁的消耗，反而还不如一次大粒度的锁调用来得高效。

**轻量级锁**

轻量级锁能提升程序同步性能的依据是“对于绝大部分的锁，在整个同步周期内都是不存在竞争的”，这是一个经验数据。轻量级锁在当前线程的栈帧中建立一个名为锁记录的空间，用于存储锁对象目前的指向和状态。如果没有竞争，轻量级锁使用CAS操作避免了使用互斥量的开销，但如果存在锁竞争，除了互斥量的开销外，还额外发生了CAS操作，因此在有竞争的情况下，轻量级锁会比传统的重量级锁更慢。

## 1.5参考资料

1、《Java 7 并发编程实战手册》

2、[java
synchronized详解](http://www.cnblogs.com/GnagWang/archive/2011/02/27/1966606.html)

3、[聊聊并发（二）Java SE1.6中的Synchronized](http://ifeve.com/java-synchronized/)

4、[java的锁机制](http://blog.csdn.net/yangzhijun_cau/article/details/6432216)

[5、Java的无锁编程和锁优化](http://blog.csdn.net/raychase/article/details/6667141)

