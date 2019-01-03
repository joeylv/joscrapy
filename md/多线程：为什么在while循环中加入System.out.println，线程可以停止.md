在论坛看到这样一个代码：

    
    
    public class StopThread {
    
        private static boolean stopRequested;
    
        public static void main(String[] args) throws InterruptedException {
    
            Thread backgroundThread = new Thread(new Runnable() {
                @Override
                public void run() {
                    int i = 0;
                    while (!stopRequested) {
                        i++;
                    }
                }
            });
    
            backgroundThread.start();
            TimeUnit.SECONDS.sleep(1);
            stopRequested = true;
        }
    }
    

这个我们都知道，由于 stopReqested 的更新值在主内存中，而线程栈中的值不是最新的，所以会一直循环，线程并不能停止。加上 Volatile
关键字后，保证变量的最新值会被更新到主存，线程在读这个变量时候，也会去取最新的，保证数据的可见性。  
但是本文的意思不在此，不对 stopReqested 加同步关键字是否就不能停止了呢？不是的。

如下就能停止线程的运行：

    
    
    public class StopThread {
    
        private static boolean stopRequested;
    
        public static void main(String[] args) throws InterruptedException {
    
            Thread backgroundThread = new Thread(new Runnable() {
    
                @Override
                public void run() {
                    int i = 0;
                    while (!stopRequested) {
                        i++;
                        System.out.println(""+i);
                    }
                }
            });
            backgroundThread.start(); 
            TimeUnit.SECONDS.sleep(1);
            stopRequested = true;
        }
    }
    

如上面所示，加了 `System.out.println`之后，线程能停止了。有的人会说，println 的源码里面有 synchronized
关键字，所以会同步变量 stopRequested 的值。这种是很不正确的理解，同步关键字同步的是同步块里面的变量，stopRequested
在这个同步代码块之外。  
真正的原因是这样的： **JVM 会尽力保证内存的可见性，即便这个变量没有加同步关键字。换句话说，只要 CPU 有时间，JVM
会尽力去保证变量值的更新。这种与 volatile 关键字的不同在于，volatile 关键字会强制的保证线程的可见性。而不加这个关键字，JVM
也会尽力去保证可见性，但是如果 CPU 一直有其他的事情在处理，它也没办法。最开始的代码，一直处于试了循环中，CPU 处于一直被饱受占用的时候，这个时候
CPU 没有时间，JVM 也不能强制要求 CPU 分点时间去取最新的变量值。而加了`System.out.println`
之后，由于内部代码的同步关键字的存在，导致CPU的输出其实是比较耗时的。这个时候CPU就有可能有时间去保证内存的可见性，于是while循环可以被终止** 。

其实，也可以在 while 循环里面加上 sleep ，让 run 方法放弃 cpu ，但是不放弃锁，这个时候由于 CPU 有空闲的时候就去按照 JVM
的要求去保证内存的可见性。如下所示。 run 方法里面休息了 3 秒，cpu 有充足的空闲时间去取变量的最新值，所以循环执行一次就停止了。

    
    
    public class StopThread {
    
        private static boolean stopRequested;
    
        public static void main(String[] args) throws InterruptedException {
    
            Thread backgroundThread = new Thread(new Runnable() {
                @Override
                public void run() {
                    int i = 0;
                    while (!stopRequested) {
                        try {
                            TimeUnit.SECONDS.sleep(3);
                        } catch (InterruptedException e) {
                            // TODO Auto-generated catch block
                            e.printStackTrace();
                        }
                        System.out.println(i);
                    }
                }
            });
            backgroundThread.start();
            TimeUnit.SECONDS.sleep(1);
            stopRequested = true;
        }
    }
    

