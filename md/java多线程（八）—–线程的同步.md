  * 1 一、同步方法
  * 2 二、同步块

## 一、同步方法

线程的同步是保证多线程安全访问竞争资源的一种手段。

线程的同步是Java多线程编程的难点，往往开发者搞不清楚什么是竞争资源、什么时候需要考虑同步，怎么同步等等问题，当然，这些问题没有很明确的答案，但有些原则问题需要考虑，是否有竞争资源被同时改动的问题？

在本文之前，请参阅《[Java线程：线程的同步与锁](http://lavasoft.blog.51cto.com/62575/99155)》，本文是在此基础上所写的。

对于同步，在具体的Java代码中需要完成一下两个操作：

1、把竞争访问的资源标识为private；

2、同步哪些修改变量的代码，使用synchronized关键字同步方法或代码。

当然这不是唯一控制并发安全的途径。

synchronized关键字使用说明：synchronized只能标记非抽象的方法，不能标识成员变量。

为了演示同步方法的使用，构建了一个信用卡账户，起初信用额为100w，然后模拟透支、存款等多个操作。显然银行账户User对象是个竞争资源，而多个并发操作的是账户方法oper(int
x)，当然应该在此方法上加上同步，并将账户的余额设为私有变量，禁止直接访问。

    
    
    public class Test { 
            public static void main(String[] args) { 
                    User u = new User("张三", 100); 
                    MyThread t1 = new MyThread("线程A", u, 20); 
                    MyThread t2 = new MyThread("线程B", u, -60); 
                    MyThread t3 = new MyThread("线程C", u, -80); 
                    MyThread t4 = new MyThread("线程D", u, -30); 
                    MyThread t5 = new MyThread("线程E", u, 32); 
                    MyThread t6 = new MyThread("线程F", u, 21); 
    
                    t1.start(); 
                    t2.start(); 
                    t3.start(); 
                    t4.start(); 
                    t5.start(); 
                    t6.start(); 
            } 
    } 
    
    class MyThread extends Thread { 
            private User u; 
            private int y = 0; 
    
            MyThread(String name, User u, int y) { 
                    super(name); 
                    this.u = u; 
                    this.y = y; 
            } 
    
            public void run() { 
                    u.oper(y); 
            } 
    } 
    
    class User { 
            private String code; 
            private int cash; 
    
            User(String code, int cash) { 
                    this.code = code; 
                    this.cash = cash; 
            } 
    
            public String getCode() { 
                    return code; 
            } 
    
            public void setCode(String code) { 
                    this.code = code; 
            } 
    
            /** 
             * 业务方法 
             * @param x 添加x万元 
             */ 
            public synchronized void oper(int x) { 
                    try { 
                            Thread.sleep(10L); 
                            this.cash += x; 
                            System.out.println(Thread.currentThread().getName() + "运行结束，增加“" + x + "”，当前用户账户余额为：" + cash); 
                            Thread.sleep(10L); 
                    } catch (InterruptedException e) { 
                            e.printStackTrace(); 
                    } 
            } 
    
            @Override 
            public String toString() { 
                    return "User{" + 
                                    "code="" + code + "\"" + 
                                    ", cash=" + cash + 
                                    "}"; 
            } 
    }

输出结果：

    
    
    线程A运行结束，增加“20”，当前用户账户余额为：120 
    线程F运行结束，增加“21”，当前用户账户余额为：141 
    线程E运行结束，增加“32”，当前用户账户余额为：173 
    线程C运行结束，增加“-80”，当前用户账户余额为：93 
    线程B运行结束，增加“-60”，当前用户账户余额为：33 
    线程D运行结束，增加“-30”，当前用户账户余额为：3

反面教材，不同步的情况，也就是去掉oper(int x)方法的synchronized修饰符，然后运行程序，结果如下：

    
    
    线程A运行结束，增加“20”，当前用户账户余额为：61
    线程D运行结束，增加“-30”，当前用户账户余额为：63
    线程B运行结束，增加“-60”，当前用户账户余额为：3
    线程F运行结束，增加“21”，当前用户账户余额为：61
    线程E运行结束，增加“32”，当前用户账户余额为：93
    线程C运行结束，增加“-80”，当前用户账户余额为：61

很显然，上面的结果是错误的，导致错误的原因是多个线程并发访问了竞争资源u，并对u的属性做了改动。

可见同步的重要性。

**注意：
通过前文可知，线程退出同步方法时将释放掉方法所属对象的锁，但还应该注意的是，同步方法中还可以使用特定的方法对线程进行调度。这些方法来自于java.lang.Object类。**

void notify() ：唤醒在此对象监视器上等待的单个线程。  
void notifyAll() ： 唤醒在此对象监视器上等待的所有线程。  
void wait()：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或 notifyAll() 方法。  
void wait(long timeout)：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或 notifyAll()
方法，或者超过指定的时间量。  
void wait(long timeout, int nanos)：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或
notifyAll() 方法，或者其他某个线程中断当前线程，或者已超过某个实际时间量。

结合以上方法，处理多线程同步与互斥问题非常重要，著名的生产者-消费者例子就是一个经典的例子，任何语言多线程必学的例子。

## 二、同步块

对于同步，除了同步方法外，还可以使用同步代码块，有时候同步代码块会带来比同步方法更好的效果。

追其同步的根本的目的，是控制竞争资源的正确的访问，因此只要在访问竞争资源的时候保证同一时刻只能一个线程访问即可，因此Java引入了同步代码快的策略，以提高性能。

在上个例子的基础上，对oper方法做了改动，由同步方法改为同步代码块模式，程序的执行逻辑并没有问题。

    
    
    public class Test { 
            public static void main(String[] args) { 
                    User u = new User("张三", 100); 
                    MyThread t1 = new MyThread("线程A", u, 20); 
                    MyThread t2 = new MyThread("线程B", u, -60); 
                    MyThread t3 = new MyThread("线程C", u, -80); 
                    MyThread t4 = new MyThread("线程D", u, -30); 
                    MyThread t5 = new MyThread("线程E", u, 32); 
                    MyThread t6 = new MyThread("线程F", u, 21); 
    
                    t1.start(); 
                    t2.start(); 
                    t3.start(); 
                    t4.start(); 
                    t5.start(); 
                    t6.start(); 
            } 
    } 
    
    class MyThread extends Thread { 
            private User u; 
            private int y = 0; 
    
            MyThread(String name, User u, int y) { 
                    super(name); 
                    this.u = u; 
                    this.y = y; 
            } 
    
            public void run() { 
                    u.oper(y); 
            } 
    } 
    
    class User { 
            private String code; 
            private int cash; 
    
            User(String code, int cash) { 
                    this.code = code; 
                    this.cash = cash; 
            } 
    
            public String getCode() { 
                    return code; 
            } 
    
            public void setCode(String code) { 
                    this.code = code; 
            } 
    
            /** 
             * 业务方法 
             * 
             * @param x 添加x万元 
             */ 
            public void oper(int x) { 
                    try { 
                            Thread.sleep(10L); 
                            synchronized (this) { 
                                    this.cash += x; 
                                    System.out.println(Thread.currentThread().getName() + "运行结束，增加“" + x + "”，当前用户账户余额为：" + cash); 
                            } 
                            Thread.sleep(10L); 
                    } catch (InterruptedException e) { 
                            e.printStackTrace(); 
                    } 
            } 
    
            @Override 
            public String toString() { 
                    return "User{" + 
                                    "code="" + code + "\"" + 
                                    ", cash=" + cash + 
                                    "}"; 
            } 
    }
    
    
    线程E运行结束，增加“32”，当前用户账户余额为：132 
    线程B运行结束，增加“-60”，当前用户账户余额为：72 
    线程D运行结束，增加“-30”，当前用户账户余额为：42 
    线程F运行结束，增加“21”，当前用户账户余额为：63 
    线程C运行结束，增加“-80”，当前用户账户余额为：-17 
    线程A运行结束，增加“20”，当前用户账户余额为：3

**注意：**

在使用synchronized关键字时候，应该尽可能避免在synchronized方法或synchronized块中使用sleep或者yield方法，因为synchronized程序块占有着对象锁，你休息那么其他的线程只能一边等着你醒来执行完了才能执行。不但严重影响效率，也不合逻辑。

同样，在同步程序块内调用yeild方法让出CPU资源也没有意义，因为你占用着锁，其他互斥线程还是无法访问同步程序块。当然与同步程序块无关的线程可以获得更多的执行时间。

本文出自 “[熔 岩](http://lavasoft.blog.51cto.com/)” 博客。

