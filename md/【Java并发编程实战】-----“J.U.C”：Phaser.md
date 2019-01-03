Phaser由java7中推出，是Java SE
7中新增的一个使用同步工具，在功能上面它与[CyclicBarrier](http://cmsblogs.com/?p=1684)、[CountDownLatch](http://cmsblogs.com/?p=1691)有些重叠，但是它提供了更加灵活、强大的用法。

CyclicBarrier，允许一组线程互相等待，直到到达某个公共屏障点。它提供的await()可以实现让所有参与者在临界点到来之前一直处于等待状态。

CountDownLatch，在完成一组正在其他线程中执行的操作之前，它允许一个或多个线程一直等待。它提供了await()、countDown()两个方法来进行操作。

在Phaser中，它把多个线程协作执行的任务划分为多个阶段，编程时需要明确各个阶段的任务，每个阶段都可以有任意个参与者，线程都可以随时注册并参与到某个阶段。

**构造**

Phaser创建后，初始阶段编号为0，构造函数中指定初始参与个数。

**注册：Registration**

Phaser支持通过register()和bulkRegister(int parties)方法来动态调整注册任务的数量。

**Arrival**

每个Phaser实例都会维护一个phase number，初始值为0。每当所有注册的任务都到达Phaser时，phase
number累加，并在超过Integer.MAX_VALUE后清零。arrive()和arriveAndDeregister()方法用于记录到达；其中arrive()，某个参与者完成任务后调用；arriveAndDeregister()，任务完成，取消自己的注册。arriveAndAwaitAdvance()，自己完成等待其他参与者完成，进入阻塞，直到Phaser成功进入下个阶段。

### example 1

    
    
    public class PhaserTest_1 {
        public static void main(String[] args) {
            Phaser phaser = new Phaser(5);
            
            for(int i = 0 ; i < 5 ; i++){
                Task_01 task_01 = new Task_01(phaser);
                Thread thread = new Thread(task_01, "PhaseTest_" + i);
                thread.start();
            }
        }
        
        static class Task_01 implements Runnable{
            private final Phaser phaser;
            
            public Task_01(Phaser phaser){
                this.phaser = phaser;
            }
            
            @Override
            public void run() {
                System.out.println(Thread.currentThread().getName() + "执行任务完成，等待其他任务执行......");
                //等待其他任务执行完成
                phaser.arriveAndAwaitAdvance();
                System.out.println(Thread.currentThread().getName() + "继续执行任务...");
            }
        }
    }

运行结果：

    
    
    PhaseTest_0执行任务完成，等待其他任务执行......
    PhaseTest_1执行任务完成，等待其他任务执行......
    PhaseTest_3执行任务完成，等待其他任务执行......
    PhaseTest_2执行任务完成，等待其他任务执行......
    PhaseTest_4执行任务完成，等待其他任务执行......
    PhaseTest_4继续执行任务...
    PhaseTest_1继续执行任务...
    PhaseTest_0继续执行任务...
    PhaseTest_2继续执行任务...
    PhaseTest_3继续执行任务...

在该实例中我们可以确认，所有子线程的****+”继续执行任务…”，都是在线程调用arriveAndAwaitAdvance()方法之后执行的。

### example 2

前面提到过，Phaser提供了比CountDownLatch、CyclicBarrier更加强大、灵活的功能，从某种程度上来说，Phaser可以替换他们：

    
    
    public class PhaserTest_5 {
        public static void main(String[] args) {
            Phaser phaser = new Phaser(1);        //相当于CountDownLatch(1) 
            
            //五个子任务
            for(int i = 0 ; i < 3 ; i++){
                Task_05 task = new Task_05(phaser);
                Thread thread = new Thread(task,"PhaseTest_" + i);
                thread.start();
            }
            
            try {
                //等待3秒
                Thread.sleep(3000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            phaser.arrive();        //countDownLatch.countDown()
        }
        
        static class Task_05 implements Runnable{
            private final Phaser phaser;
            
            Task_05(Phaser phaser){
                this.phaser = phaser;
            }
            
            @Override
            public void run() {
                phaser.awaitAdvance(phaser.getPhase());        //countDownLatch.await()
                System.out.println(Thread.currentThread().getName() + "执行任务...");
            }
        }
    }

在这里，任务一开始并没有真正执行，而是等待三秒后执行。

对于CyclicBarrier就更加简单了，直接arriveAndAwaitAdvance()方法替换，如example 1。

### example 3

在CyclicBarrier中当任务执行完之后可以执行一个action，在Phaser中同样有一个对应的action，只不过Phaser需要重写onAdvance()方法：

    
    
    public class PhaserTest_3 {
        public static void main(String[] args) {
            Phaser phaser = new Phaser(3){
                /**
                 * registeredParties:线程注册的数量
                 * phase:进入该方法的线程数，
                 */
                 protected boolean onAdvance(int phase, int registeredParties) { 
                     System.out.println("执行onAdvance方法.....;phase:" + phase + "registeredParties=" + registeredParties);
                     return phase == 3; 
                 }
            };
            
            for(int i = 0 ; i < 3 ; i++){
                Task_03 task = new Task_03(phaser);
                Thread thread = new Thread(task,"task_" + i);
                thread.start();
            }
            while(!phaser.isTerminated()){
                phaser.arriveAndAwaitAdvance();    //主线程一直等待
            }
            System.out.println("主线程任务已经结束....");
        }
        
        static class Task_03 implements Runnable{
            private final Phaser phaser;
            
            public Task_03(Phaser phaser){
                this.phaser = phaser;
            }
            
            @Override
            public void run() {
                do{
                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    System.out.println(Thread.currentThread().getName() + "开始执行任务...");
                    phaser.arriveAndAwaitAdvance();
                }while(!phaser.isTerminated());
            }
        }
    }

运行结果：

    
    
    task_0开始执行任务...
    task_1开始执行任务...
    task_1执行onAdvance方法.....;phase:0registeredParties=3
    task_2开始执行任务...
    task_0开始执行任务...
    task_1开始执行任务...
    task_0执行onAdvance方法.....;phase:1registeredParties=3
    task_2开始执行任务...
    task_2执行onAdvance方法.....;phase:2registeredParties=3
    主线程任务已经结束....
    task_0开始执行任务...

参考博文：

1、[What"s New on Java 7 Phaser](http://whitesock.iteye.com/blog/1135457)

2、<http://blog.csdn.net/andycpp/article/details/8838820>

