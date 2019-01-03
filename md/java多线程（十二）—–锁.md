  * 1 一、锁（上）
  * 2 二、锁（下）

## 一、锁（上）

在Java5中，专门提供了锁对象，利用锁可以方便的实现资源的封锁，用来控制对竞争资源并发访问的控制，这些内容主要集中在java.util.concurrent.locks
包下面，里面有三个重要的接口Condition、Lock、ReadWriteLock。

**Condition**` ：Condition` 将 `Object` 监视器方法（`wait`、`notify` 和
`notifyAll`）分解成截然不同的对象，以便通过将这些对象与任意
[`Lock`](mk:@MSITStore:F:%5CCHM%5Cjdk150.ZH_cn.chm::/jdk150/api/java/util/concurrent/locks/Lock.html)
实现组合使用，为每个对象提供多个等待 set （wait-set）。

**Lock**` ：Lock` 实现提供了比使用 `synchronized` 方法和语句可获得的更广泛的锁定操作。

**ReadWriteLock**` ：ReadWriteLock`
维护了一对相关的[`锁定`](mk:@MSITStore:F:%5CCHM%5Cjdk150.ZH_cn.chm::/jdk150/api/java/util/concurrent/locks/Lock.html)，一个用于只读操作，另一个用于写入操作。

有关锁的介绍,API文档解说很多，看得很烦，还是看个例子再看文档比较容易理解。

    
    
    public class Test { 
            public static void main(String[] args) { 
                    //创建并发访问的账户 
                    MyCount myCount = new MyCount("95599200901215522", 10000); 
                    //创建一个锁对象 
                    Lock lock = new ReentrantLock(); 
                    //创建一个线程池 
                    ExecutorService pool = Executors.newCachedThreadPool(); 
                    //创建一些并发访问用户，一个信用卡，存的存，取的取，好热闹啊 
                    User u1 = new User("张三", myCount, -4000, lock); 
                    User u2 = new User("张三他爹", myCount, 6000, lock); 
                    User u3 = new User("张三他弟", myCount, -8000, lock); 
                    User u4 = new User("张三", myCount, 800, lock); 
                    //在线程池中执行各个用户的操作 
                    pool.execute(u1); 
                    pool.execute(u2); 
                    pool.execute(u3); 
                    pool.execute(u4); 
                    //关闭线程池 
                    pool.shutdown(); 
            } 
    } 
    
    /** 
    * 信用卡的用户 
    */ 
    class User implements Runnable { 
            private String name;                //用户名 
            private MyCount myCount;        //所要操作的账户 
            private int iocash;                 //操作的金额，当然有正负之分了 
            private Lock myLock;                //执行操作所需的锁对象 
    
            User(String name, MyCount myCount, int iocash, Lock myLock) { 
                    this.name = name; 
                    this.myCount = myCount; 
                    this.iocash = iocash; 
                    this.myLock = myLock; 
            } 
    
            public void run() { 
                    //获取锁 
                    myLock.lock(); 
                    //执行现金业务 
                    System.out.println(name + "正在操作" + myCount + "账户，金额为" + iocash + "，当前金额为" + myCount.getCash()); 
                    myCount.setCash(myCount.getCash() + iocash); 
                    System.out.println(name + "操作" + myCount + "账户成功，金额为" + iocash + "，当前金额为" + myCount.getCash()); 
                    //释放锁，否则别的线程没有机会执行了 
                    myLock.unlock(); 
            } 
    } 
    
    /** 
    * 信用卡账户，可随意透支 
    */ 
    class MyCount { 
            private String oid;         //账号 
            private int cash;             //账户余额 
    
            MyCount(String oid, int cash) { 
                    this.oid = oid; 
                    this.cash = cash; 
            } 
    
            public String getOid() { 
                    return oid; 
            } 
    
            public void setOid(String oid) { 
                    this.oid = oid; 
            } 
    
            public int getCash() { 
                    return cash; 
            } 
    
            public void setCash(int cash) { 
                    this.cash = cash; 
            } 
    
            @Override 
            public String toString() { 
                    return "MyCount{" + 
                                    "oid="" + oid + "\"" + 
                                    ", cash=" + cash + 
                                    "}"; 
            } 
    }
    
    
    张三正在操作MyCount{oid="95599200901215522", cash=10000}账户，金额为-4000，当前金额为10000 
    张三操作MyCount{oid="95599200901215522", cash=6000}账户成功，金额为-4000，当前金额为6000 
    张三他爹正在操作MyCount{oid="95599200901215522", cash=6000}账户，金额为6000，当前金额为6000 
    张三他爹操作MyCount{oid="95599200901215522", cash=12000}账户成功，金额为6000，当前金额为12000 
    张三他弟正在操作MyCount{oid="95599200901215522", cash=12000}账户，金额为-8000，当前金额为12000 
    张三他弟操作MyCount{oid="95599200901215522", cash=4000}账户成功，金额为-8000，当前金额为4000 
    张三正在操作MyCount{oid="95599200901215522", cash=4000}账户，金额为800，当前金额为4000 
    张三操作MyCount{oid="95599200901215522", cash=4800}账户成功，金额为800，当前金额为4800

从上面的输出可以看到，利用锁对象太方便了，比直接在某个不知情的对象上用锁清晰多了。

但一定要注意的是，在获取了锁对象后，用完后应该尽快释放锁，以便别的等待该锁的线程有机会去执行。

## 二、锁（下）

在上文中提到了Lock接口以及对象，使用它，很优雅的控制了竞争资源的安全访问，但是这种锁不区分读写，称这种锁为普通锁。为了提高性能，Java提供了读写锁，在读的地方使用读锁，在写的地方使用写锁，灵活控制，在一定程度上提高了程序的执行效率。

Java中读写锁有个接口java.util.concurrent.locks.ReadWriteLock，也有具体的实现ReentrantReadWriteLock，详细的API可以查看JavaAPI文档。

下面这个例子是在文例子的基础上，将普通锁改为读写锁，并添加账户余额查询的功能，代码如下：

    
    
    public class Test { 
            public static void main(String[] args) { 
                    //创建并发访问的账户 
                    MyCount myCount = new MyCount("95599200901215522", 10000); 
                    //创建一个锁对象 
                    ReadWriteLock lock = new ReentrantReadWriteLock(false); 
                    //创建一个线程池 
                    ExecutorService pool = Executors.newFixedThreadPool(2); 
                    //创建一些并发访问用户，一个信用卡，存的存，取的取，好热闹啊 
                    User u1 = new User("张三", myCount, -4000, lock, false); 
                    User u2 = new User("张三他爹", myCount, 6000, lock, false); 
                    User u3 = new User("张三他弟", myCount, -8000, lock, false); 
                    User u4 = new User("张三", myCount, 800, lock, false); 
                    User u5 = new User("张三他爹", myCount, 0, lock, true); 
                    //在线程池中执行各个用户的操作 
                    pool.execute(u1); 
                    pool.execute(u2); 
                    pool.execute(u3); 
                    pool.execute(u4); 
                    pool.execute(u5); 
                    //关闭线程池 
                    pool.shutdown(); 
            } 
    } 
    
    /** 
    * 信用卡的用户 
    */ 
    class User implements Runnable { 
            private String name;                //用户名 
            private MyCount myCount;        //所要操作的账户 
            private int iocash;                 //操作的金额，当然有正负之分了 
            private ReadWriteLock myLock;                //执行操作所需的锁对象 
            private boolean ischeck;        //是否查询 
    
            User(String name, MyCount myCount, int iocash, ReadWriteLock myLock, boolean ischeck) { 
                    this.name = name; 
                    this.myCount = myCount; 
                    this.iocash = iocash; 
                    this.myLock = myLock; 
                    this.ischeck = ischeck; 
            } 
    
            public void run() { 
                    if (ischeck) { 
                            //获取读锁 
                            myLock.readLock().lock(); 
                            System.out.println("读：" + name + "正在查询" + myCount + "账户，当前金额为" + myCount.getCash()); 
                            //释放读锁 
                            myLock.readLock().unlock(); 
                    } else { 
                            //获取写锁 
                            myLock.writeLock().lock(); 
                            //执行现金业务 
                            System.out.println("写：" + name + "正在操作" + myCount + "账户，金额为" + iocash + "，当前金额为" + myCount.getCash()); 
                            myCount.setCash(myCount.getCash() + iocash); 
                            System.out.println("写：" + name + "操作" + myCount + "账户成功，金额为" + iocash + "，当前金额为" + myCount.getCash()); 
                            //释放写锁 
                            myLock.writeLock().unlock(); 
                    } 
            } 
    } 
    
    /** 
    * 信用卡账户，可随意透支 
    */ 
    class MyCount { 
            private String oid;         //账号 
            private int cash;             //账户余额 
    
            MyCount(String oid, int cash) { 
                    this.oid = oid; 
                    this.cash = cash; 
            } 
    
            public String getOid() { 
                    return oid; 
            } 
    
            public void setOid(String oid) { 
                    this.oid = oid; 
            } 
    
            public int getCash() { 
                    return cash; 
            } 
    
            public void setCash(int cash) { 
                    this.cash = cash; 
            } 
    
            @Override 
            public String toString() { 
                    return "MyCount{" + 
                                    "oid="" + oid + "\"" + 
                                    ", cash=" + cash + 
                                    "}"; 
            } 
    }
    
    
    写：张三正在操作MyCount{oid="95599200901215522", cash=10000}账户，金额为-4000，当前金额为10000 
    写：张三操作MyCount{oid="95599200901215522", cash=6000}账户成功，金额为-4000，当前金额为6000 
    写：张三他弟正在操作MyCount{oid="95599200901215522", cash=6000}账户，金额为-8000，当前金额为6000 
    写：张三他弟操作MyCount{oid="95599200901215522", cash=-2000}账户成功，金额为-8000，当前金额为-2000 
    写：张三正在操作MyCount{oid="95599200901215522", cash=-2000}账户，金额为800，当前金额为-2000 
    写：张三操作MyCount{oid="95599200901215522", cash=-1200}账户成功，金额为800，当前金额为-1200 
    读：张三他爹正在查询MyCount{oid="95599200901215522", cash=-1200}账户，当前金额为-1200 
    写：张三他爹正在操作MyCount{oid="95599200901215522", cash=-1200}账户，金额为6000，当前金额为-1200 
    写：张三他爹操作MyCount{oid="95599200901215522", cash=4800}账户成功，金额为6000，当前金额为4800

在实际开发中，最好在能用读写锁的情况下使用读写锁，而不要用普通锁，以求更好的性能。

**本文出自 “**[ **熔 岩**](http://lavasoft.blog.51cto.com/) **” 博客，请务必保留此出处**

