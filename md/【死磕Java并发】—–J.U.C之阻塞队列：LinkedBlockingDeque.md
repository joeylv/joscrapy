  * 1 LinkedBlockingDeque
    * 1.1 基础方法

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

前面的BlockingQueue都是单向的FIFO队列，而LinkedBlockingDeque则是一个由链表组成的双向阻塞队列，双向队列就意味着可以从对头、对尾两端插入和移除元素，同样意味着LinkedBlockingDeque支持FIFO、FILO两种操作方式。

LinkedBlockingDeque是可选容量的，在初始化时可以设置容量防止其过度膨胀，如果不设置，默认容量大小为Integer.MAX_VALUE。

## LinkedBlockingDeque

LinkedBlockingDeque
继承AbstractQueue，实现接口BlockingDeque，而BlockingDeque又继承接口BlockingQueue，BlockingDeque是支持两个附加操作的
Queue，这两个操作是：获取元素时等待双端队列变为非空；存储元素时等待双端队列中的空间变得可用。这两类操作就为LinkedBlockingDeque
的双向操作Queue提供了可能。BlockingDeque接口提供了一系列的以First和Last结尾的方法，如addFirst、addLast、peekFirst、peekLast。

    
    
    public class LinkedBlockingDeque<E>
        extends AbstractQueue<E>
        implements BlockingDeque<E>, java.io.Serializable {
    
        // 双向链表的表头
        transient Node<E> first;
    
        // 双向链表的表尾
        transient Node<E> last;
    
        // 大小，双向链表中当前节点个数
        private transient int count;
    
        // 容量，在创建LinkedBlockingDeque时指定的
        private final int capacity;
    
        final ReentrantLock lock = new ReentrantLock();
    
        private final Condition notEmpty = lock.newCondition();
    
        private final Condition notFull = lock.newCondition();
    
    }
    

通过上面的Lock可以看出，LinkedBlockingDeque底层实现机制与LinkedBlockingQueue一样，依然是通过互斥锁ReentrantLock
来实现，notEmpty 、notFull 两个Condition做协调生产者、消费者问题。

与其他BlockingQueue一样，节点还是使用内部类Node：

    
    
        static final class Node<E> {
            E item;
    
            Node<E> prev;
    
            Node<E> next;
    
            Node(E x) {
                item = x;
            }
        }
    

双向嘛，节点肯定得要有前驱prev、后继next咯。

### 基础方法

LinkedBlockingDeque
的add、put、offer、take、peek、poll系列方法都是通过调用XXXFirst，XXXLast方法。所以这里就仅以putFirst、putLast、pollFirst、pollLast分析下。

**putFirst**

putFirst(E e) :将指定的元素插入此双端队列的开头，必要时将一直等待可用空间。

    
    
        public void putFirst(E e) throws InterruptedException {
            // check null
            if (e == null) throw new NullPointerException();
            Node<E> node = new Node<E>(e);
            // 获取锁
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                while (!linkFirst(node))
                    // 在notFull条件上等待，直到被唤醒或中断
                    notFull.await();
            } finally {
                // 释放锁
                lock.unlock();
            }
        }
    

先获取锁，然后调用linkFirst方法入列，最后释放锁。如果队列是满的则在notFull上面等待。linkFirst设置Node为对头：

    
    
        private boolean linkFirst(Node<E> node) {
            // 超出容量
            if (count >= capacity)
                return false;
    
            // 首节点
            Node<E> f = first;
            // 新节点的next指向原first
            node.next = f;
            // 设置node为新的first
            first = node;
    
            // 没有尾节点，设置node为尾节点
            if (last == null)
                last = node;
            // 有尾节点，那就将之前first的pre指向新增node
            else
                f.prev = node;
            ++count;
            // 唤醒notEmpty
            notEmpty.signal();
            return true;
        }
    

linkFirst主要是设置node节点队列的列头节点，成功返回true，如果队列满了返回false。整个过程还是比较简单的。

**putLast**

putLast(E e) :将指定的元素插入此双端队列的末尾，必要时将一直等待可用空间。

    
    
        public void putLast(E e) throws InterruptedException {
            if (e == null) throw new NullPointerException();
            Node<E> node = new Node<E>(e);
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                while (!linkLast(node))
                    notFull.await();
            } finally {
                lock.unlock();
            }
        }
    

调用linkLast将节点Node链接到队列尾部：

    
    
        private boolean linkLast(Node<E> node) {
            if (count >= capacity)
                return false;
            // 尾节点
            Node<E> l = last;
    
            // 将Node的前驱指向原本的last
            node.prev = l;
    
            // 将node设置为last
            last = node;
            // 首节点为null，则设置node为first
            if (first == null)
                first = node;
            else
            //非null，说明之前的last有值，就将之前的last的next指向node
                l.next = node;
            ++count;
            notEmpty.signal();
            return true;
        }
    

**pollFirst**

pollFirst()：获取并移除此双端队列的第一个元素；如果此双端队列为空，则返回 null。

    
    
        public E pollFirst() {
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                return unlinkFirst();
            } finally {
                lock.unlock();
            }
        }
    

调用unlinkFirst移除队列首元素：

    
    
        private E unlinkFirst() {
            // 首节点
            Node<E> f = first;
    
            // 空队列，直接返回null
            if (f == null)
                return null;
    
            // first.next
            Node<E> n = f.next;
    
            // 节点item
            E item = f.item;
    
            // 移除掉first ==> first = first.next
            f.item = null;
            f.next = f; // help GC
            first = n;
    
            // 移除后为空队列，仅有一个节点
            if (n == null)
                last = null;
            else
            // n的pre原来指向之前的first，现在n变为first了，pre指向null
                n.prev = null;
            --count;
            notFull.signal();
            return item;
        }
    

**pollLast**

pollLast():获取并移除此双端队列的最后一个元素；如果此双端队列为空，则返回 null。

    
    
        public E pollLast() {
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                return unlinkLast();
            } finally {
                lock.unlock();
            }
        }
    

调用unlinkLast移除尾结点，链表空返回null ：

    
    
        private E unlinkLast() {
            // assert lock.isHeldByCurrentThread();
            Node<E> l = last;
            if (l == null)
                return null;
            Node<E> p = l.prev;
            E item = l.item;
            l.item = null;
            l.prev = l; // help GC
            last = p;
            if (p == null)
                first = null;
            else
                p.next = null;
            --count;
            notFull.signal();
            return item;
        }
    

LinkedBlockingDeque大部分方法都是通过linkFirst、linkLast、unlinkFirst、unlinkLast这四个方法来实现的，因为是双向队列，所以他们都是针对first、last的操作，看懂这个整个LinkedBlockingDeque就不难了。

**掌握了双向队列的插入、删除操作，LinkedBlockingDeque就没有任何难度可言了，数据结构的重要性啊！！！！**

