  * 1 ConcurrentLinkedQueue源码分析
    * 1.1 入列
    * 1.2 出列

> 原文出自:<http://cmsblogs.com>

* * *

> 原文出处<http://cmsblogs.com/> 『 **chenssy** 』

要实现一个线程安全的队列有两种方式：阻塞和非阻塞。阻塞队列无非就是锁的应用，而非阻塞则是CAS算法的应用。下面我们就开始一个非阻塞算法的研究：CoucurrentLinkedQueue。

ConcurrentLinkedQueue是一个基于链接节点的无边界的线程安全队列，它采用FIFO原则对元素进行排序。采用“wait-
free”算法（即CAS算法）来实现的。

CoucurrentLinkedQueue规定了如下几个不变性：

  1. 在入队的最后一个元素的next为null
  2. 队列中所有未删除的节点的item都不能为null且都能从head节点遍历到
  3. 对于要删除的节点，不是直接将其设置为null，而是先将其item域设置为null（迭代器会跳过item为null的节点）
  4. 允许head和tail更新滞后。这是什么意思呢？意思就说是head、tail不总是指向第一个元素和最后一个元素（后面阐述）。

head的不变性和可变性：

  * 不变性 
    1. 所有未删除的节点都可以通过head节点遍历到
    2. head不能为null
    3. head节点的next不能指向自身
  * 可变性 
    1. head的item可能为null，也可能不为null
    2. 允许tail滞后head，也就是说调用succc()方法，从head不可达tail

tail的不变性和可变性

  * 不变性 
    1. tail不能为null
  * 可变性 
    1. tail的item可能为null，也可能不为null
    2. tail节点的next域可以指向自身
    3. 允许tail滞后head，也就是说调用succc()方法，从head不可达tail

这些特性是否已经晕了？没关系，我们看下面的源码分析就可以理解这些特性了。

## ConcurrentLinkedQueue源码分析

CoucurrentLinkedQueue的结构由head节点和tail节点组成，每个节点由节点元素item和指向下一个节点的next引用组成，而节点与节点之间的关系就是通过该next关联起来的，从而组成一张链表的队列。节点Node为ConcurrentLinkedQueue的内部类，定义如下：

    
    
        private static class Node<E> {
            /** 节点元素域 */
            volatile E item;
            volatile Node<E> next;
    
            //初始化,获得item 和 next 的偏移量,为后期的CAS做准备
    
            Node(E item) {
                UNSAFE.putObject(this, itemOffset, item);
            }
    
            boolean casItem(E cmp, E val) {
                return UNSAFE.compareAndSwapObject(this, itemOffset, cmp, val);
            }
    
            void lazySetNext(Node<E> val) {
                UNSAFE.putOrderedObject(this, nextOffset, val);
            }
    
            boolean casNext(Node<E> cmp, Node<E> val) {
                return UNSAFE.compareAndSwapObject(this, nextOffset, cmp, val);
            }
    
            // Unsafe mechanics
    
            private static final sun.misc.Unsafe UNSAFE;
            /** 偏移量 */
            private static final long itemOffset;
            /** 下一个元素的偏移量 */
    
           private static final long nextOffset;
    
            static {
                try {
                    UNSAFE = sun.misc.Unsafe.getUnsafe();
                    Class<?> k = Node.class;
                    itemOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("item"));
                    nextOffset = UNSAFE.objectFieldOffset
                            (k.getDeclaredField("next"));
                } catch (Exception e) {
                    throw new Error(e);
                }
            }
        }
    

### 入列

入列，我们认为是一个非常简单的过程：tail节点的next执行新节点，然后更新tail为新节点即可。从单线程角度我们这么理解应该是没有问题的，但是多线程呢？如果一个线程正在进行插入动作，那么它必须先获取尾节点，然后设置尾节点的下一个节点为当前节点，但是如果已经有一个线程刚刚好完成了插入，那么尾节点是不是发生了变化？对于这种情况ConcurrentLinkedQueue怎么处理呢？我们先看源码：

offer(E e)：将指定元素插入都队列尾部：

    
    
        public boolean offer(E e) {
            //检查节点是否为null
            checkNotNull(e);
            // 创建新节点
            final Node<E> newNode = new Node<E>(e);
    
            //死循环 直到成功为止
            for (Node<E> t = tail, p = t;;) {
                Node<E> q = p.next;
                // q == null 表示 p已经是最后一个节点了，尝试加入到队列尾
                // 如果插入失败，则表示其他线程已经修改了p的指向
                if (q == null) {                                // --- 1
                    // casNext：t节点的next指向当前节点
                    // casTail：设置tail 尾节点
                    if (p.casNext(null, newNode)) {             // --- 2
                        // node 加入节点后会导致tail距离最后一个节点相差大于一个，需要更新tail
                        if (p != t)                             // --- 3
                            casTail(t, newNode);                    // --- 4
                        return true;
                    }
                }
                // p == q 等于自身
                else if (p == q)                                // --- 5
                    // p == q 代表着该节点已经被删除了
                    // 由于多线程的原因，我们offer()的时候也会poll()，如果offer()的时候正好该节点已经poll()了
                    // 那么在poll()方法中的updateHead()方法会将head指向当前的q，而把p.next指向自己，即：p.next == p
                    // 这样就会导致tail节点滞后head（tail位于head的前面），则需要重新设置p
                    p = (t != (t = tail)) ? t : head;           // --- 6
                // tail并没有指向尾节点
                else
                    // tail已经不是最后一个节点，将p指向最后一个节点
                    p = (p != t && t != (t = tail)) ? t : q;    // --- 7
            }
        }
    

光看源码还是有点儿迷糊的，插入节点一次分析就会明朗很多。

**初始化**

ConcurrentLinkedQueue初始化时head、tail存储的元素都为null，且head等于tail：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823001.png)

**添加元素A**

按照程序分析：第一次插入元素A，head = tail = dummyNode，所有q = p.next =
null，直接走步骤2：p.casNext(null, newNode)，由于 p == t成立，所以不会执行步骤3：casTail(t,
newNode)，直接return。插入A节点后如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823002.png)

**添加元素B**

q = p.next = A ,p = tail = dummyNode，所以直接跳到步骤7：p = (p != t && t != (t = tail))
? t : q;。此时p = q，然后进行第二次循环 q = p.next = null，步骤2：p == null成立，将该节点插入，因为p = q，t
= tail，所以步骤3：p != t 成立，执行步骤4：casTail(t, newNode)，然后return。如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823003.png)

**添加节点C**

此时t = tail ,p = t，q = p.next = null，和插入元素A无异，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823004.png)

这里整个offer()过程已经分析完成了，可能p == q 有点儿难理解，p 不是等于q.next么，怎么会有p ==
q呢？这个疑问我们在出列poll()中分析

### 出列

ConcurrentLinkedQueue提供了poll()方法进行出列操作。入列主要是涉及到tail，出列则涉及到head。我们先看源码：

    
    
        public E poll() {
            // 如果出现p被删除的情况需要从head重新开始
            restartFromHead:        // 这是什么语法？真心没有见过
            for (;;) {
                for (Node<E> h = head, p = h, q;;) {
    
                    // 节点 item
                    E item = p.item;
    
                    // item 不为null，则将item 设置为null
                    if (item != null && p.casItem(item, null)) {                    // --- 1
                        // p != head 则更新head
                        if (p != h)                                                 // --- 2
                            // p.next != null，则将head更新为p.next ,否则更新为p
                            updateHead(h, ((q = p.next) != null) ? q : p);          // --- 3
                        return item;
                    }
                    // p.next == null 队列为空
                    else if ((q = p.next) == null) {                                // --- 4
                        updateHead(h, p);
                        return null;
                    }
                    // 当一个线程在poll的时候，另一个线程已经把当前的p从队列中删除——将p.next = p，p已经被移除不能继续，需要重新开始
                    else if (p == q)                                                // --- 5
                        continue restartFromHead;
                    else
                        p = q;                                                      // --- 6
                }
            }
        }
    

这个相对于offer()方法而言会简单些，里面有一个很重要的方法：updateHead()，该方法用于CAS更新head节点，如下：

    
    
        final void updateHead(Node<E> h, Node<E> p) {
            if (h != p && casHead(h, p))
                h.lazySetNext(h);
        }
    

我们先将上面offer()的链表poll()掉，添加A、B、C节点结构如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823005.png)

**poll A**

head = dumy，p = head， item = p.item = null，步骤1不成立，步骤4：(q = p.next) ==
null不成立，p.next = A，跳到步骤6，下一个循环，此时p = A，所以步骤1 item != null，进行p.casItem(item,
null)成功，此时p == A != h，所以执行步骤3：updateHead(h, ((q = p.next) != null) ? q : p)，q
= p.next = B != null，则将head CAS更新成B，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823006.png)

**poll B**

head = B ， p = head = B，item = p.item = B，步骤成立，步骤2：p != h 不成立，直接return，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823007.png)

**poll C**

head = dumy ，p = head = dumy，tiem = p.item = null，步骤1不成立，跳到步骤4：(q = p.next) ==
null，不成立，然后跳到步骤6，此时，p = q = C，item = C(item)，步骤1成立，所以讲C（item）设置为null，步骤2：p !=
h成立，执行步骤3：updateHead(h, ((q = p.next) != null) ? q : p)，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823008.png)

看到这里是不是一目了然了，在这里我们再来分析offer()的步骤5：

    
    
    else if(p == q){
        p = (t != (t = tail))? t : head;
    }
    

ConcurrentLinkedQueue中规定，p ==
q表明，该节点已经被删除了，也就说tail滞后于head，head无法通过succ()方法遍历到tail，怎么做？ (t != (t = tail))? t
: head;（这段代码的可读性实在是太差了，真他妈难理解：不知道是否可以理解为t != tail ? tail :
head）这段代码主要是来判读tail节点是否已经发生了改变，如果发生了改变，则说明tail已经重新定位了，只需要重新找到tail即可，否则就只能指向head了。

就上面那个我们再次插入一个元素D。则p = head，q = p.next = null，执行步骤1： q = null且 p != t
，所以执行步骤4:，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120823009.png)

再插入元素E，q = p.next = null，p == t，所以插入E后如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208230010.png)

到这里ConcurrentLinkedQueue的整个入列、出列都已经分析完毕了，对于ConcurrentLinkedQueue
LZ真心感觉难看懂，看懂之后也感叹设计得太精妙了，利用CAS来完成数据操作，同时允许队列的不一致性，这种弱一致性确实是非常强大。再次感叹Doug
Lea的天才。

