**一、前言**

在完成Map下的并发集合后，现在来分析ArrayBlockingQueue，ArrayBlockingQueue可以用作一个阻塞型队列，支持多任务并发操作，有了之前看源码的积累，再看ArrayBlockingQueue源码会很容易，下面开始正文。

**二、ArrayBlockingQueue数据结构**

通过源码分析，并且可以对比ArrayList可知，ArrayBlockingQueue的底层数据结构是数组，数据结构如下

![](data:image/png;base64,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)
说明：ArrayBlockingQueue底层采用数据才存放数据，对数组的访问添加了锁的机制，使其能够支持多线程并发。

**三、ArrayBlockingQueue源码分析**

3.1 类的继承关系

    
    
     public class ArrayBlockingQueue<E> extends AbstractQueue<E>
            implements BlockingQueue<E>, java.io.Serializable {}

说明：可以看到ArrayBlockingQueue继承了AbstractQueue抽象类，AbstractQueue定义了对队列的基本操作；同时实现了BlockingQueue接口，BlockingQueue表示阻塞型的队列，其对队列的操作可能会抛出异常；同时也实现了Searializable接口，表示可以被序列化。

3.2 类的属性

![]()![]()

    
    
    public class ArrayBlockingQueue<E> extends AbstractQueue<E>
            implements BlockingQueue<E>, java.io.Serializable {
        // 版本序列号
        private static final long serialVersionUID = -817911632652898426L;
        // 存放实际元素的数组
        final Object[] items;
        // 取元素索引
        int takeIndex;
        // 获取元素索引
        int putIndex;
        // 队列中的项
        int count;
        // 可重入锁
        final ReentrantLock lock;
        // 等待获取条件
        private final Condition notEmpty;
        // 等待存放条件
        private final Condition notFull;
        // 迭代器
        transient Itrs itrs = null;
    }

View Code

说明：从类的属性中可以清楚的看到其底层的结构是Object类型的数组，取元素和存元素有不同的索引，有一个可重入锁ReentrantLock，两个条件Condition。对ReentrantLock和Condition不太熟悉的读者可以参考笔者的这篇博客，[【JUC】JDK1.8源码分析之ReentrantLock（三）](http://www.cnblogs.com/leesf456/p/5383609.html)。

3.3 类的构造函数

1\. ArrayBlockingQueue(int)型构造函数

![]()![]()

    
    
        public ArrayBlockingQueue(int capacity) {
            // 调用两个参数的构造函数
            this(capacity, false);
        }

View Code

说明：该构造函数用于创建一个带有给定的（固定）容量和默认访问策略的 ArrayBlockingQueue。

2\. ArrayBlockingQueue(int, boolean)型构造函数

![]()![]()

    
    
        public ArrayBlockingQueue(int capacity, boolean fair) {
            // 初始容量必须大于0
            if (capacity <= 0)
                throw new IllegalArgumentException();
            // 初始化数组
            this.items = new Object[capacity];
            // 初始化可重入锁
            lock = new ReentrantLock(fair);
            // 初始化等待条件
            notEmpty = lock.newCondition();
            notFull =  lock.newCondition();
        }

View Code

说明：该构造函数用于创建一个具有给定的（固定）容量和指定访问策略的 ArrayBlockingQueue。

3\. ArrayBlockingQueue(int, boolean, Collection<? extends E>)型构造函数

![]()![]()

    
    
        public ArrayBlockingQueue(int capacity, boolean fair,
                                  Collection<? extends E> c) {
            // 调用两个参数的构造函数
            this(capacity, fair);
            // 可重入锁
            final ReentrantLock lock = this.lock;
            // 上锁
            lock.lock(); // Lock only for visibility, not mutual exclusion
            try {
                int i = 0;
                try {
                    for (E e : c) { // 遍历集合
                        // 检查元素是否为空
                        checkNotNull(e);
                        // 存入ArrayBlockingQueue中
                        items[i++] = e;
                    }
                } catch (ArrayIndexOutOfBoundsException ex) { // 当初始化容量小于传入集合的大小时，会抛出异常
                    throw new IllegalArgumentException();
                }
                // 元素数量
                count = i;
                // 初始化存元素的索引
                putIndex = (i == capacity) ? 0 : i;
            } finally {
                // 释放锁
                lock.unlock();
            }
        }

View Code

说明：该构造函数用于创建一个具有给定的（固定）容量和指定访问策略的 ArrayBlockingQueue，它最初包含给定 collection 的元素，并以
collection 迭代器的遍历顺序添加元素。

3.4 核心函数分析

1\. put函数

![]()![]()

    
    
        public void put(E e) throws InterruptedException {
            checkNotNull(e);
            // 获取可重入锁
            final ReentrantLock lock = this.lock;
            // 如果当前线程未被中断，则获取锁
            lock.lockInterruptibly();
            try {
                while (count == items.length) // 判断元素是否已满
                    // 若满，则等待
                    notFull.await();
                // 入队列
                enqueue(e);
            } finally {
                // 释放锁
                lock.unlock();
            }
        }

View Code

说明：put函数用于存放元素，在当前线程被中断时会抛出异常，并且当队列已经满时，会阻塞一直等待。其中，put会调用enqueue函数，enqueue函数源码如下

![]()![]()

    
    
        private void enqueue(E x) {
            // assert lock.getHoldCount() == 1;
            // assert items[putIndex] == null;
            // 获取数组
            final Object[] items = this.items;
            // 将元素放入
            items[putIndex] = x;
            if (++putIndex == items.length) // 放入后存元素的索引等于数组长度（表示已满）
                // 重置存索引为0
                putIndex = 0;
            // 元素数量加1
            count++;
            // 唤醒在notEmpty条件上等待的线程
            notEmpty.signal();
        }

View Code

说明：enqueue函数用于将元素存入底层Object数组中，并且会唤醒等待notEmpty条件的线程。

2\. offer函数

![]()![]()

    
    
        public boolean offer(E e) {
            // 检查元素不能为空
            checkNotNull(e);
            // 可重入锁
            final ReentrantLock lock = this.lock;
            // 获取锁
            lock.lock();
            try {
                if (count == items.length) // 元素个数等于数组长度，则返回
                    return false; 
                else { // 添加进数组
                    enqueue(e);
                    return true;
                }
            } finally {
                // 释放数组
                lock.unlock();
            }
        }

View Code

说明：offer函数也用于存放元素，在调用ArrayBlockingQueue的add方法时，会间接的调用到offer函数，offer函数添加元素不会抛出异常，当底层Object数组已满时，则返回false，否则，会调用enqueue函数，将元素存入底层Object数组。并唤醒等待notEmpty条件的线程。

3\. take函数

![]()![]()

    
    
        public E take() throws InterruptedException {
            // 可重入锁
            final ReentrantLock lock = this.lock;
            // 如果当前线程未被中断，则获取锁，中断会抛出异常
            lock.lockInterruptibly();
            try {
                while (count == 0) // 元素数量为0，即Object数组为空
                    // 则等待notEmpty条件
                    notEmpty.await();
                // 出队列
                return dequeue();
            } finally {
                // 释放锁
                lock.unlock();
            }
        }

View Code

说明：take函数用于从ArrayBlockingQueue中获取一个元素，其与put函数相对应，在当前线程被中断时会抛出异常，并且当队列为空时，会阻塞一直等待。其中，take会调用dequeue函数，dequeue函数源码如下

![]()![]()

    
    
        private E dequeue() {
            // assert lock.getHoldCount() == 1;
            // assert items[takeIndex] != null;
            final Object[] items = this.items;
            @SuppressWarnings("unchecked")
            // 取元素
            E x = (E) items[takeIndex];
            // 该索引的值赋值为null
            items[takeIndex] = null;
            // 取值索引等于数组长度
            if (++takeIndex == items.length)
                // 重新赋值取值索引
                takeIndex = 0;
            // 元素个数减1
            count--;
            if (itrs != null) 
                itrs.elementDequeued();
            // 唤醒在notFull条件上等待的线程
            notFull.signal();
            return x;
        }

View Code

说明：dequeue函数用于将取元素，并且会唤醒等待notFull条件的线程。

4\. poll函数

![]()![]()

    
    
        public E poll() {
            // 重入锁
            final ReentrantLock lock = this.lock;
            // 获取锁
            lock.lock();
            try {
                // 若元素个数为0则返回null，否则，调用dequeue，出队列
                return (count == 0) ? null : dequeue();
            } finally {
                // 释放锁
                lock.unlock();
            }
        }

View Code

说明：poll函数用于获取元素，其与offer函数相对应，不会抛出异常，当元素个数为0是，返回null，否则，调用dequeue函数，并唤醒等待notFull条件的线程。并返回。

5\. clear函数

![]()![]()

    
    
        public void clear() {
            // 数组
            final Object[] items = this.items;
            // 可重入锁
            final ReentrantLock lock = this.lock;
            // 获取锁
            lock.lock();
            try {
                // 保存元素个数
                int k = count;
                if (k > 0) { // 元素个数大于0
                    // 存数元素索引
                    final int putIndex = this.putIndex;
                    // 取元素索引
                    int i = takeIndex;
                    do {
                        // 赋值为null
                        items[i] = null;
                        if (++i == items.length) // 重新赋值i
                            i = 0;
                    } while (i != putIndex);
                    // 重新赋值取元素索引
                    takeIndex = putIndex;
                    // 元素个数为0
                    count = 0;
                    if (itrs != null)
                        itrs.queueIsEmpty();
                    for (; k > 0 && lock.hasWaiters(notFull); k--) // 若有等待notFull条件的线程，则逐一唤醒
                        notFull.signal();
                }
            } finally {
                // 释放锁
                lock.unlock();
            }
        }

View Code

说明：clear函数用于清空ArrayBlockingQueue，并且会释放所有等待notFull条件的线程（存放元素的线程）。

**四、示例**

下面给出一个具体的示例来演示ArrayBlockingQueue的使用

![]()![]()

    
    
     package com.hust.grid.leesf.collections;
    
    import java.util.concurrent.ArrayBlockingQueue;
    
    class PutThread extends Thread {
        private ArrayBlockingQueue<Integer> abq;
        public PutThread(ArrayBlockingQueue<Integer> abq) {
            this.abq = abq;
        }
        
        public void run() {
            for (int i = 0; i < 10; i++) {
                try {
                    System.out.println("put " + i);
                    abq.put(i);
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    class GetThread extends Thread {
        private ArrayBlockingQueue<Integer> abq;
        public GetThread(ArrayBlockingQueue<Integer> abq) {
            this.abq = abq;
        }
        
        public void run() {
            for (int i = 0; i < 10; i++) {
                try {
                    System.out.println("take " + abq.take());
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    public class ArrayBlockingQueueDemo {
        public static void main(String[] args) {
            ArrayBlockingQueue<Integer> abq = new ArrayBlockingQueue<Integer>(10);
            PutThread p1 = new PutThread(abq);
            GetThread g1 = new GetThread(abq);
            
            p1.start();
            g1.start();
        }
    }

View Code

运行结果：

![]()![]()

    
    
    put 0
    take 0
    put 1
    take 1
    put 2
    take 2
    put 3
    take 3
    put 4
    take 4
    put 5
    take 5
    put 6
    take 6
    put 7
    take 7
    put 8
    take 8
    put 9
    take 9

View Code

说明：示例中使用了两个线程，一个用于存元素，一个用于读元素，存和读各10次，每个线程存一个元素或者读一个元素后都会休眠100ms，可以看到结果是交替打印，并且首先打印的肯定是put线程语句（因为若取线程先取元素，此时队列并没有元素，其会阻塞，等待存线程存入元素），并且最终程序可以正常结束。

① 若修改取元素线程，将存的元素的次数修改为15次（for循环的结束条件改为15即可），运行结果如下：

![]()![]()

    
    
    put 0
    take 0
    put 1
    take 1
    put 2
    take 2
    put 3
    take 3
    put 4
    take 4
    put 5
    take 5
    put 6
    take 6
    put 7
    take 7
    put 8
    take 8
    put 9
    take 9

View Code

说明：运行结果与上面的运行结果相同，但是，此时程序无法正常结束，因为take方法被阻塞了，等待被唤醒。

**五、总结**

总的来说，有了前面分析的基础，分析ArrayBlockingQueue就会非常的简单，ArrayBlockingQueue是通过ReentrantLock和Condition条件来保证多线程的正确访问的。ArrayBockingQueue的分析就到这里，欢迎交流，谢谢各位园友的观看~

