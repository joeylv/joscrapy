  * 1 一、线程交互的基础知识
  * 2 二、多个线程在等待一个对象锁时候使用notifyAll()

线程交互是比较复杂的问题，SCJP要求不很基础：给定一个场景，编写代码来恰当使用等待、通知和通知所有线程。

## 一、线程交互的基础知识

SCJP所要求的线程交互知识点需要从java.lang.Object的类的三个方法来学习：

void notify()：唤醒在此对象监视器上等待的单个线程。  
void notifyAll()：唤醒在此对象监视器上等待的所有线程。  
void wait()：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或 notifyAll() 方法。

当然，wait()还有另外两个重载方法：

void wait(long timeout)：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或 notifyAll()
方法，或者超过指定的时间量。  
void wait(long timeout, int nanos)：导致当前的线程等待，直到其他线程调用此对象的 notify() 方法或
notifyAll() 方法，或者其他某个线程中断当前线程，或者已超过某个实际时间量。

以上这些方法是帮助线程传递线程关心的时间状态。

关于等待/通知，要记住的关键点是：
**必须从同步环境内调用wait()、notify()、notifyAll()方法。线程不能调用对象上等待或通知的方法，除非它拥有那个对象的锁。**

wait()、notify()、notifyAll()都是Object的实例方法。与每个对象具有锁一样，每个对象可以有一个线程列表，他们等待来自该信号（通知）。线程通过执行对象上的wait()方法获得这个等待列表。从那时候起，它不再执行任何其他指令，直到调用对象的notify()方法为止。如果多个线程在同一个对象上等待，则将只选择一个线程（不保证以何种顺序）继续执行。如果没有线程等待，则不采取任何特殊操作。

下面看个例子就明白了：

    
    
    /** 
    * 计算输出其他线程锁计算的数据 
    */ 
    public class ThreadA { 
        public static void main(String[] args) { 
            ThreadB b = new ThreadB(); 
            //启动计算线程 
            b.start(); 
            //线程A拥有b对象上的锁。线程为了调用wait()或notify()方法，该线程必须是那个对象锁的拥有者 
            synchronized (b) { 
                try { 
                    System.out.println("等待对象b完成计算。。。"); 
                    //当前线程A等待 
                    b.wait(); 
                } catch (InterruptedException e) { 
                    e.printStackTrace(); 
                } 
                System.out.println("b对象计算的总和是：" + b.total); 
            } 
        } 
    }
    
    
    /** 
    * 计算1+2+3 ... +100的和 
    */ 
    public class ThreadB extends Thread { 
        int total; 
    
        public void run() { 
            synchronized (this) { 
                for (int i = 0; i < 101; i++) { 
                    total += i; 
                } 
                //（完成计算了）唤醒在此对象监视器上等待的单个线程，在本例中线程A被唤醒 
                notify(); 
            } 
        } 
    }
    
    
    等待对象b完成计算。。。 
    b对象计算的总和是：5050 
    
    Process finished with exit code 0

**千万注意：
当在对象上调用wait()方法时，执行该代码的线程立即放弃它在对象上的锁。然而调用notify()时，并不意味着这时线程会放弃其锁。如果线程荣然在完成同步代码，则线程在移出之前不会放弃锁。因此，只要调用notify()并不意味着这时该锁变得可用。**

## 二、多个线程在等待一个对象锁时候使用notifyAll()

在多数情况下，最好通知等待某个对象的所有线程。如果这样做，可以在对象上使用notifyAll()让所有在此对象上等待的线程冲出等待区，返回到可运行状态。

下面给个例子：

    
    
    /** 
    * 计算线程 
    */ 
    public class Calculator extends Thread { 
            int total; 
    
            public void run() { 
                    synchronized (this) { 
                            for (int i = 0; i < 101; i++) { 
                                    total += i; 
                            } 
                    } 
                    //通知所有在此对象上等待的线程 
                    notifyAll(); 
            } 
    }
    
    
    /** 
    * 获取计算结果并输出 
    * 
    * @author leizhimin 2008-9-20 11:15:22 
    */ 
    public class ReaderResult extends Thread { 
            Calculator c; 
    
            public ReaderResult(Calculator c) { 
                    this.c = c; 
            } 
    
            public void run() { 
                    synchronized (c) { 
                            try { 
                                    System.out.println(Thread.currentThread() + "等待计算结果。。。"); 
                                    c.wait(); 
                            } catch (InterruptedException e) { 
                                    e.printStackTrace(); 
                            } 
                            System.out.println(Thread.currentThread() + "计算结果为：" + c.total); 
                    } 
            } 
    
            public static void main(String[] args) { 
                    Calculator calculator = new Calculator(); 
    
                    //启动三个线程，分别获取计算结果 
                    new ReaderResult(calculator).start(); 
                    new ReaderResult(calculator).start(); 
                    new ReaderResult(calculator).start(); 
                    //启动计算线程 
                    calculator.start(); 
            } 
    }

运行结果：

    
    
    Thread[Thread-1,5,main]等待计算结果。。。
    Thread[Thread-2,5,main]等待计算结果。。。
    Thread[Thread-3,5,main]等待计算结果。。。
    Exception in thread "Thread-0" java.lang.IllegalMonitorStateException: current thread not owner
      at java.lang.Object.notifyAll(Native Method)
      at threadtest.Calculator.run(Calculator.java:18)
    Thread[Thread-1,5,main]计算结果为：5050
    Thread[Thread-2,5,main]计算结果为：5050
    Thread[Thread-3,5,main]计算结果为：5050
    Process finished with exit code 0

运行结果表明，程序中有异常，并且多次运行结果可能有多种输出结果。这就是说明，这个多线程的交互程序还存在问题。究竟是出了什么问题，需要深入的分析和思考，下面将做具体分析。

实际上，上面这个代码中，我们期望的是读取结果的线程在计算线程调用notifyAll()之前等待即可。
但是，如果计算线程先执行，并在读取结果线程等待之前调用了notify()方法，那么又会发生什么呢？这种情况是可能发生的。因为无法保证线程的不同部分将按照什么顺序来执行。幸运的是当读取线程运行时，它只能马上进入等待状态—-它没有做任何事情来检查等待的事件是否已经发生。
—-因此，如果计算线程已经调用了notifyAll()方法，那么它就不会再次调用notifyAll()，—-并且等待的读取线程将永远保持等待。这当然是开发者所不愿意看到的问题。

因此，当等待的事件发生时，需要能够检查notifyAll()通知事件是否已经发生。

**本文出自 “**[ **熔 岩**](http://lavasoft.blog.51cto.com/) **” 博客，转载：**[
**http://lavasoft.blog.51cto.com/62575/99157**](http://lavasoft.blog.51cto.com/62575/99157
"http://lavasoft.blog.51cto.com/62575/99157")

