前面介绍了三个同步辅助类：CyclicBarrier、Barrier、Phaser，这篇博客介绍最后一个：Exchanger。JDK
API是这样介绍的：可以在对中对元素进行配对和交换的线程的同步点。每个线程将条目上的某个方法呈现给 exchange
方法，与伙伴线程进行匹配，并且在返回时接收其伙伴的对象。Exchanger 可能被视为 SynchronousQueue 的双向形式。Exchanger
可能在应用程序（比如遗传算法和管道设计）中很有用。

Exchanger，它允许在并发任务之间交换数据。具体来说，Exchanger类允许在两个线程之间定义同步点。当两个线程都到达同步点时，他们交换数据结构，因此第一个线程的数据结构进入到第二个线程中，第二个线程的数据结构进入到第一个线程中。

在官方API对Exchanger定义是相当简洁的，一个无参构造函数，两个方法：

**构造函数：**

Exchanger()创建一个新的 Exchanger。

**方法：**

exchange(V x):等待另一个线程到达此交换点（除非当前线程被中断），然后将给定的对象传送给该线程，并接收该线程的对象。  
exchange(V x, long timeout, TimeUnit
unit):等待另一个线程到达此交换点（除非当前线程被中断，或者超出了指定的等待时间），然后将给定的对象传送给该线程，同时接收该线程的对象。

Exchanger在生产-消费者问题情境中非常有用。在生产者-消费者情境模式中它包含了一个数缓冲区（仓库），一个或者多个生产者，一个或者多个消费中。

下面是生产者-消费者的实例（实例来自《java 7 并发编程实战手册》）

    
    
    public class Producer implements Runnable{
        
        /**
         * 生产者和消费者进行交换的数据结构
         */
        private List<String> buffer;
        
        /**
         * 同步生产者和消费者的交换对象
         */
        private final Exchanger<List<String>> exchanger;
        
        Producer(List<String> buffer,Exchanger<List<String>> exchanger){
            this.buffer = buffer;
            this.exchanger = exchanger;
        }
        
        @Override
        public void run() {
            int cycle = 1;
            for(int i = 0 ; i < 10 ; i++){
                System.out.println("Producer : Cycle :" + cycle);
                for(int j = 0 ; j < 10 ; j++){
                    String message = "Event " + ((i * 10 ) + j);
                    System.out.println("Producer : " + message);
                    buffer.add(message);
                }
                
                //调用exchange()与消费者进行数据交换
                try {
                    buffer = exchanger.exchange(buffer);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("Producer :" + buffer.size());
                cycle++ ;
            }
        }
    }

Consumer:

    
    
    public class Consumer implements Runnable{
        private List<String> buffer;
        
        private final Exchanger<List<String>> exchanger;
        
        public Consumer(List<String> buffer,Exchanger<List<String>> exchanger){
            this.buffer = buffer;
            this.exchanger = exchanger;
        }
        
        @Override
        public void run() {
            int cycle = 1;
            for(int i = 0 ; i < 10 ; i++){
                System.out.println("Consumer : Cycle :" + cycle);
    
                //调用exchange()与消费者进行数据交换
                try {
                    buffer = exchanger.exchange(buffer);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("Consumer :" + buffer.size());
                for(int j = 0 ; j < 10 ; j++){
                    System.out.println("Consumer : " + buffer.get(0));
                    buffer.remove(0);
                }
                cycle++ ;
            }
        }
    }

Test:

    
    
    public class Test {
        public static void main(String[] args) {
            List<String> buffer1 = new ArrayList<>();
            List<String> buffer2 = new ArrayList<>();
            
            Exchanger<List<String>> exchanger = new Exchanger<>();
            
            Producer producer = new Producer(buffer1, exchanger);
            Consumer consumer = new Consumer(buffer2, exchanger);
            
            Thread thread1 = new Thread(producer);
            Thread thread2 = new Thread(consumer);
            
            thread1.start();
            thread2.start();
        }
    }

运行结果（部分）：

    
    
    Producer : Cycle :1
    Producer : Event 0
    Producer : Event 1
    Producer : Event 2
    Producer : Event 3
    Producer : Event 4
    Producer : Event 5
    Producer : Event 6
    Producer : Event 7
    Consumer : Cycle :1
    Producer : Event 8
    Producer : Event 9
    Producer :0
    Producer : Cycle :2
    Producer : Event 10
    Producer : Event 11
    Producer : Event 12
    Producer : Event 13
    Consumer :10
    Consumer : Event 0
    Consumer : Event 1
    Consumer : Event 2
    Consumer : Event 3
    Consumer : Event 4
    Consumer : Event 5
    Consumer : Event 6
    Consumer : Event 7
    Consumer : Event 8
    Consumer : Event 9
    Consumer : Cycle :2
    Producer : Event 14
    Producer : Event 15
    Producer : Event 16
    Producer : Event 17
    Producer : Event 18
    Producer : Event 19

首先生产者Producer、消费中Consumer首先都创建一个缓存列表，通过Exchanger来同步交换数据。消费中通过调用Exchanger与生产者进行同步来获取数据，而生产者则通过for循环向缓存队列存储数据并使用exchanger对象消费者同步。到消费者从exchanger哪里得到数据后，他的缓冲列表中有10个数据，而生产者得到的则是一个空的列表。上面的例子充分展示了消费者-
生产者是如何利用Exchanger来完成数据交换的。

在Exchanger中，如果一个线程已经到达了exchanger节点时，对于它的伙伴节点的情况有三种：

1、如果它的伙伴节点在该线程到达之间已经调用了exchanger方法，则它会唤醒它的伙伴然后进行数据交换，得到各自数据返回。

2、如果它的伙伴节点还没有到达交换点，则该线程将会被挂起，等待它的伙伴节点到达被唤醒，完成数据交换。

3、如果当前线程被中断了则抛出异常，或者等待超时了，则抛出超时异常。

**参考资料：**

**1、《java 7 并发编程实战手册》**

