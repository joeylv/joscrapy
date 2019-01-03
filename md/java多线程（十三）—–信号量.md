Java的信号量实际上是一个功能完毕的计数器，对控制一定资源的消费与回收有着很重要的意义，信号量常常用于多线程的代码中，并能监控有多少数目的线程等待获取资源，并且通过信号量可以得知可用资源的数目等等，这里总是在强调“数目”二字，但不能指出来有哪些在等待，哪些资源可用。

因此，本人认为，这个信号量类如果能返回数目，还能知道哪些对象在等待，哪些资源可使用，就非常完美了，仅仅拿到这些概括性的数字，对精确控制意义不是很大。目前还没想到更好的用法。

下面是一个简单例子：

    
    
    public class Test { 
            public static void main(String[] args) { 
                    MyPool myPool = new MyPool(20); 
                    //创建线程池 
                    ExecutorService threadPool = Executors.newFixedThreadPool(2); 
                    MyThread t1 = new MyThread("任务A", myPool, 3); 
                    MyThread t2 = new MyThread("任务B", myPool, 12); 
                    MyThread t3 = new MyThread("任务C", myPool, 7); 
                    //在线程池中执行任务 
                    threadPool.execute(t1); 
                    threadPool.execute(t2); 
                    threadPool.execute(t3); 
                    //关闭池 
                    threadPool.shutdown(); 
            } 
    } 
    
    /** 
    * 一个池 
    */ 
    class MyPool { 
            private Semaphore sp;     //池相关的信号量 
    
            /** 
             * 池的大小，这个大小会传递给信号量 
             * 
             * @param size 池的大小 
             */ 
            MyPool(int size) { 
                    this.sp = new Semaphore(size); 
            } 
    
            public Semaphore getSp() { 
                    return sp; 
            } 
    
            public void setSp(Semaphore sp) { 
                    this.sp = sp; 
            } 
    } 
    
    class MyThread extends Thread { 
            private String threadname;            //线程的名称 
            private MyPool pool;                        //自定义池 
            private int x;                                    //申请信号量的大小 
    
            MyThread(String threadname, MyPool pool, int x) { 
                    this.threadname = threadname; 
                    this.pool = pool; 
                    this.x = x; 
            } 
    
            public void run() { 
                    try { 
                            //从此信号量获取给定数目的许可 
                            pool.getSp().acquire(x); 
                            //todo：也许这里可以做更复杂的业务 
                            System.out.println(threadname + "成功获取了" + x + "个许可！"); 
                    } catch (InterruptedException e) { 
                            e.printStackTrace(); 
                    } finally { 
                            //释放给定数目的许可，将其返回到信号量。 
                            pool.getSp().release(x); 
                            System.out.println(threadname + "释放了" + x + "个许可！"); 
                    } 
            } 
    }
    
    
    任务B成功获取了12个许可！ 
    任务B释放了12个许可！ 
    任务A成功获取了3个许可！ 
    任务C成功获取了7个许可！ 
    任务C释放了7个许可！ 
    任务A释放了3个许可！

从结果可以看出，信号量仅仅是对池资源进行监控，但不保证线程的安全，因此，在使用时候，应该自己控制线程的安全访问池资源。

**本文出自 “**[ **熔 岩**](http://lavasoft.blog.51cto.com/) **” 博客，请务必保留此出处**[
**http://lavasoft.blog.51cto.com/62575/222469**](http://lavasoft.blog.51cto.com/62575/222469)

