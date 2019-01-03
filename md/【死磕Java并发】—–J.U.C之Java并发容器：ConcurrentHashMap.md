  * 1 ConcurrentHashMap的实现
  * 2 重要概念
  * 3 重要内部类
    * 3.1 Node
    * 3.2 TreeNode
    * 3.3 TreeBin
    * 3.4 ForwardingNode
  * 4 构造函数
  * 5 初始化： initTable()
  * 6 put操作
  * 7 get操作
  * 8 size 操作
  * 9 扩容操作
  * 10 转换红黑树

> 原文出自:<http://cmsblogs.com>

* * *

> 此篇博客所有源码均来自JDK 1.8

HashMap是我们用得非常频繁的一个集合，但是由于它是非线程安全的，在多线程环境下，put操作是有可能产生死循环的，导致CPU利用率接近100%。为了解决该问题，提供了Hashtable和Collections.synchronizedMap(hashMap)两种解决方案，但是这两种方案都是对读写加锁，独占式，一个线程在读时其他线程必须等待，吞吐量较低，性能较为低下。故而Doug
Lea大神给我们提供了高性能的线程安全HashMap：ConcurrentHashMap。

## ConcurrentHashMap的实现

ConcurrentHashMap作为Concurrent一族，其有着高效地并发操作，相比Hashtable的笨重，ConcurrentHashMap则更胜一筹了。

在1.8版本以前，ConcurrentHashMap采用分段锁的概念，使锁更加细化，但是1.8已经改变了这种思路，而是利用CAS+Synchronized来保证并发更新的安全，当然底层采用数组+链表+红黑树的存储结构。

关于1.7和1.8的区别请参考占小狼博客：谈谈ConcurrentHashMap1.7和1.8的不同实现:<http://www.jianshu.com/p/e694f1e868ec>

我们从如下几个部分全面了解ConcurrentHashMap在1.8中是如何实现的：

  1. 重要概念
  2. 重要内部类
  3. ConcurrentHashMap的初始化
  4. put操作
  5. get操作
  6. size操作
  7. 扩容
  8. 红黑树转换

## 重要概念

ConcurrentHashMap定义了如下几个常量：

    
    
    // 最大容量：2^30=1073741824
    private static final int MAXIMUM_CAPACITY = 1 << 30;
    
    // 默认初始值，必须是2的幕数
    private static final int DEFAULT_CAPACITY = 16;
    
    //
    static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
    
    //
    private static final int DEFAULT_CONCURRENCY_LEVEL = 16;
    
    //
    private static final float LOAD_FACTOR = 0.75f;
    
    // 链表转红黑树阀值,> 8 链表转换为红黑树
    static final int TREEIFY_THRESHOLD = 8;
    
    //树转链表阀值，小于等于6（tranfer时，lc、hc=0两个计数器分别++记录原bin、新binTreeNode数量，<=UNTREEIFY_THRESHOLD 则untreeify(lo)）
    static final int UNTREEIFY_THRESHOLD = 6;
    
    //
    static final int MIN_TREEIFY_CAPACITY = 64;
    
    //
    private static final int MIN_TRANSFER_STRIDE = 16;
    
    //
    private static int RESIZE_STAMP_BITS = 16;
    
    // 2^15-1，help resize的最大线程数
    private static final int MAX_RESIZERS = (1 << (32 - RESIZE_STAMP_BITS)) - 1;
    
    // 32-16=16，sizeCtl中记录size大小的偏移量
    private static final int RESIZE_STAMP_SHIFT = 32 - RESIZE_STAMP_BITS;
    
    // forwarding nodes的hash值
    static final int MOVED     = -1;
    
    // 树根节点的hash值
    static final int TREEBIN   = -2;
    
    // ReservationNode的hash值
    static final int RESERVED  = -3;
    
    // 可用处理器数量
    static final int NCPU = Runtime.getRuntime().availableProcessors();
    

上面是ConcurrentHashMap定义的常量，简单易懂，就不多阐述了。下面介绍ConcurrentHashMap几个很重要的概念。

  1. **table** ：用来存放Node节点数据的，默认为null，默认大小为16的数组，每次扩容时大小总是2的幂次方；
  2. **nextTable** ：扩容时新生成的数据，数组为table的两倍；
  3. **Node** ：节点，保存key-value的数据结构；
  4. **ForwardingNode** ：一个特殊的Node节点，hash值为-1，其中存储nextTable的引用。只有table发生扩容的时候，ForwardingNode才会发挥作用，作为一个占位符放在table中表示当前节点为null或则已经被移动
  5. **sizeCtl** ：控制标识符，用来控制table初始化和扩容操作的，在不同的地方有不同的用途，其值也不同，所代表的含义也不同 
    * 负数代表正在进行初始化或扩容操作
    * -1代表正在初始化
    * -N 表示有N-1个线程正在进行扩容操作
    * 正数或0代表hash表还没有被初始化，这个数值表示初始化或下一次进行扩容的大小

## 重要内部类

为了实现ConcurrentHashMap，Doug
Lea提供了许多内部类来进行辅助实现，如Node，TreeNode,TreeBin等等。下面我们就一起来看看ConcurrentHashMap几个重要的内部类。

### Node

作为ConcurrentHashMap中最核心、最重要的内部类，Node担负着重要角色：key-
value键值对。所有插入ConCurrentHashMap的中数据都将会包装在Node中。定义如下：

    
    
        static class Node<K,V> implements Map.Entry<K,V> {
            final int hash;
            final K key;
            volatile V val;             //带有volatile，保证可见性
            volatile Node<K,V> next;    //下一个节点的指针
    
            Node(int hash, K key, V val, Node<K,V> next) {
                this.hash = hash;
                this.key = key;
                this.val = val;
                this.next = next;
            }
    
            public final K getKey()       { return key; }
            public final V getValue()     { return val; }
            public final int hashCode()   { return key.hashCode() ^ val.hashCode(); }
            public final String toString(){ return key + "=" + val; }
            /** 不允许修改value的值 */
            public final V setValue(V value) {
                throw new UnsupportedOperationException();
            }
    
            public final boolean equals(Object o) {
                Object k, v, u; Map.Entry<?,?> e;
                return ((o instanceof Map.Entry) &&
                        (k = (e = (Map.Entry<?,?>)o).getKey()) != null &&
                        (v = e.getValue()) != null &&
                        (k == key || k.equals(key)) &&
                        (v == (u = val) || v.equals(u)));
            }
    
            /**  赋值get()方法 */
            Node<K,V> find(int h, Object k) {
                Node<K,V> e = this;
                if (k != null) {
                    do {
                        K ek;
                        if (e.hash == h &&
                                ((ek = e.key) == k || (ek != null && k.equals(ek))))
                            return e;
                    } while ((e = e.next) != null);
                }
                return null;
            }
        }
    

在Node内部类中，其属性value、next都是带有volatile的。同时其对value的setter方法进行了特殊处理，不允许直接调用其setter方法来修改value的值。最后Node还提供了find方法来赋值map.get()。

### TreeNode

我们在学习HashMap的时候就知道，HashMap的核心数据结构就是链表。在ConcurrentHashMap中就不一样了，如果链表的数据过长是会转换为红黑树来处理。当它并不是直接转换，而是将这些链表的节点包装成TreeNode放在TreeBin对象中，然后由TreeBin完成红黑树的转换。所以TreeNode也必须是ConcurrentHashMap的一个核心类，其为树节点类，定义如下：

    
    
        static final class TreeNode<K,V> extends Node<K,V> {
            TreeNode<K,V> parent;  // red-black tree links
            TreeNode<K,V> left;
            TreeNode<K,V> right;
            TreeNode<K,V> prev;    // needed to unlink next upon deletion
            boolean red;
    
            TreeNode(int hash, K key, V val, Node<K,V> next,
                     TreeNode<K,V> parent) {
                super(hash, key, val, next);
                this.parent = parent;
            }
    
    
            Node<K,V> find(int h, Object k) {
                return findTreeNode(h, k, null);
            }
    
            //查找hash为h，key为k的节点
            final TreeNode<K,V> findTreeNode(int h, Object k, Class<?> kc) {
                if (k != null) {
                    TreeNode<K,V> p = this;
                    do  {
                        int ph, dir; K pk; TreeNode<K,V> q;
                        TreeNode<K,V> pl = p.left, pr = p.right;
                        if ((ph = p.hash) > h)
                            p = pl;
                        else if (ph < h)
                            p = pr;
                        else if ((pk = p.key) == k || (pk != null && k.equals(pk)))
                            return p;
                        else if (pl == null)
                            p = pr;
                        else if (pr == null)
                            p = pl;
                        else if ((kc != null ||
                                (kc = comparableClassFor(k)) != null) &&
                                (dir = compareComparables(kc, k, pk)) != 0)
                            p = (dir < 0) ? pl : pr;
                        else if ((q = pr.findTreeNode(h, k, kc)) != null)
                            return q;
                        else
                            p = pl;
                    } while (p != null);
                }
                return null;
            }
        }
    

源码展示TreeNode继承Node，且提供了findTreeNode用来查找查找hash为h，key为k的节点。

### TreeBin

该类并不负责key-
value的键值对包装，它用于在链表转换为红黑树时包装TreeNode节点，也就是说ConcurrentHashMap红黑树存放是TreeBin，不是TreeNode。该类封装了一系列的方法，包括putTreeVal、lookRoot、UNlookRoot、remove、balanceInsetion、balanceDeletion。由于TreeBin的代码太长我们这里只展示构造方法（构造方法就是构造红黑树的过程）：

    
    
        static final class TreeBin<K,V> extends Node<K,V> {
            TreeNode<K, V> root;
            volatile TreeNode<K, V> first;
            volatile Thread waiter;
            volatile int lockState;
            static final int WRITER = 1; // set while holding write lock
            static final int WAITER = 2; // set when waiting for write lock
            static final int READER = 4; // increment value for setting read lock
    
            TreeBin(TreeNode<K, V> b) {
                super(TREEBIN, null, null, null);
                this.first = b;
                TreeNode<K, V> r = null;
                for (TreeNode<K, V> x = b, next; x != null; x = next) {
                    next = (TreeNode<K, V>) x.next;
                    x.left = x.right = null;
                    if (r == null) {
                        x.parent = null;
                        x.red = false;
                        r = x;
                    } else {
                        K k = x.key;
                        int h = x.hash;
                        Class<?> kc = null;
                        for (TreeNode<K, V> p = r; ; ) {
                            int dir, ph;
                            K pk = p.key;
                            if ((ph = p.hash) > h)
                                dir = -1;
                            else if (ph < h)
                                dir = 1;
                            else if ((kc == null &&
                                    (kc = comparableClassFor(k)) == null) ||
                                    (dir = compareComparables(kc, k, pk)) == 0)
                                dir = tieBreakOrder(k, pk);
                            TreeNode<K, V> xp = p;
                            if ((p = (dir <= 0) ? p.left : p.right) == null) {
                                x.parent = xp;
                                if (dir <= 0)
                                    xp.left = x;
                                else
                                    xp.right = x;
                                r = balanceInsertion(r, x);
                                break;
                            }
                        }
                    }
                }
                this.root = r;
                assert checkInvariants(root);
            }
    
            /** 省略很多代码 */
        }
    

通过构造方法是不是发现了部分端倪，构造方法就是在构造一个红黑树的过程。

### ForwardingNode

这是一个真正的辅助类，该类仅仅只存活在ConcurrentHashMap扩容操作时。只是一个标志节点，并且指向nextTable，它提供find方法而已。该类也是集成Node节点，其hash为-1，key、value、next均为null。如下：

    
    
        static final class ForwardingNode<K,V> extends Node<K,V> {
            final Node<K,V>[] nextTable;
            ForwardingNode(Node<K,V>[] tab) {
                super(MOVED, null, null, null);
                this.nextTable = tab;
            }
    
            Node<K,V> find(int h, Object k) {
                // loop to avoid arbitrarily deep recursion on forwarding nodes
                outer: for (Node<K,V>[] tab = nextTable;;) {
                    Node<K,V> e; int n;
                    if (k == null || tab == null || (n = tab.length) == 0 ||
                            (e = tabAt(tab, (n - 1) & h)) == null)
                        return null;
                    for (;;) {
                        int eh; K ek;
                        if ((eh = e.hash) == h &&
                                ((ek = e.key) == k || (ek != null && k.equals(ek))))
                            return e;
                        if (eh < 0) {
                            if (e instanceof ForwardingNode) {
                                tab = ((ForwardingNode<K,V>)e).nextTable;
                                continue outer;
                            }
                            else
                                return e.find(h, k);
                        }
                        if ((e = e.next) == null)
                            return null;
                    }
                }
            }
        }
    

## 构造函数

ConcurrentHashMap提供了一系列的构造函数用于创建ConcurrentHashMap对象：

    
    
        public ConcurrentHashMap() {
        }
    
        public ConcurrentHashMap(int initialCapacity) {
            if (initialCapacity < 0)
                throw new IllegalArgumentException();
            int cap = ((initialCapacity >= (MAXIMUM_CAPACITY >>> 1)) ?
                       MAXIMUM_CAPACITY :
                       tableSizeFor(initialCapacity + (initialCapacity >>> 1) + 1));
            this.sizeCtl = cap;
        }
    
        public ConcurrentHashMap(Map<? extends K, ? extends V> m) {
            this.sizeCtl = DEFAULT_CAPACITY;
            putAll(m);
        }
    
        public ConcurrentHashMap(int initialCapacity, float loadFactor) {
            this(initialCapacity, loadFactor, 1);
        }
    
        public ConcurrentHashMap(int initialCapacity,
                                 float loadFactor, int concurrencyLevel) {
            if (!(loadFactor > 0.0f) || initialCapacity < 0 || concurrencyLevel <= 0)
                throw new IllegalArgumentException();
            if (initialCapacity < concurrencyLevel)   // Use at least as many bins
                initialCapacity = concurrencyLevel;   // as estimated threads
            long size = (long)(1.0 + (long)initialCapacity / loadFactor);
            int cap = (size >= (long)MAXIMUM_CAPACITY) ?
                MAXIMUM_CAPACITY : tableSizeFor((int)size);
            this.sizeCtl = cap;
        }
    

## 初始化： initTable()

ConcurrentHashMap的初始化主要由initTable()方法实现，在上面的构造函数中我们可以看到，其实ConcurrentHashMap在构造函数中并没有做什么事，仅仅只是设置了一些参数而已。其真正的初始化是发生在插入的时候，例如put、merge、compute、computeIfAbsent、computeIfPresent操作时。其方法定义如下：

    
    
        private final Node<K,V>[] initTable() {
            Node<K,V>[] tab; int sc;
            while ((tab = table) == null || tab.length == 0) {
                //sizeCtl < 0 表示有其他线程在初始化，该线程必须挂起
                if ((sc = sizeCtl) < 0)
                    Thread.yield();
                // 如果该线程获取了初始化的权利，则用CAS将sizeCtl设置为-1，表示本线程正在初始化
                else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
                        // 进行初始化
                    try {
                        if ((tab = table) == null || tab.length == 0) {
                            int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
                            @SuppressWarnings("unchecked")
                            Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];
                            table = tab = nt;
                            // 下次扩容的大小
                            sc = n - (n >>> 2); ///相当于0.75*n 设置一个扩容的阈值  
                        }
                    } finally {
                        sizeCtl = sc;
                    }
                    break;
                }
            }
            return tab;
        }
    

初始化方法initTable()的关键就在于sizeCtl，该值默认为0，如果在构造函数时有参数传入该值则为2的幂次方。该值如果 <
0，表示有其他线程正在初始化，则必须暂停该线程。如果线程获得了初始化的权限则先将sizeCtl设置为-1，防止有其他线程进入，最后将sizeCtl设置0.75
* n，表示扩容的阈值。

## put操作

ConcurrentHashMap最常用的put、get操作，ConcurrentHashMap的put操作与HashMap并没有多大区别，其核心思想依然是根据hash值计算节点插入在table的位置，如果该位置为空，则直接插入，否则插入到链表或者树中。但是ConcurrentHashMap会涉及到多线程情况就会复杂很多。我们先看源代码，然后根据源代码一步一步分析：

    
    
        public V put(K key, V value) {
            return putVal(key, value, false);
        }
    
        final V putVal(K key, V value, boolean onlyIfAbsent) {
            //key、value均不能为null
            if (key == null || value == null) throw new NullPointerException();
            //计算hash值
            int hash = spread(key.hashCode());
            int binCount = 0;
            for (Node<K,V>[] tab = table;;) {
                Node<K,V> f; int n, i, fh;
                // table为null，进行初始化工作
                if (tab == null || (n = tab.length) == 0)
                    tab = initTable();
                //如果i位置没有节点，则直接插入，不需要加锁
                else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
                    if (casTabAt(tab, i, null,
                            new Node<K,V>(hash, key, value, null)))
                        break;                   // no lock when adding to empty bin
                }
                // 有线程正在进行扩容操作，则先帮助扩容
                else if ((fh = f.hash) == MOVED)
                    tab = helpTransfer(tab, f);
                else {
                    V oldVal = null;
                    //对该节点进行加锁处理（hash值相同的链表的头节点），对性能有点儿影响
                    synchronized (f) {
                        if (tabAt(tab, i) == f) {
                            //fh > 0 表示为链表，将该节点插入到链表尾部
                            if (fh >= 0) {
                                binCount = 1;
                                for (Node<K,V> e = f;; ++binCount) {
                                    K ek;
                                    //hash 和 key 都一样，替换value
                                    if (e.hash == hash &&
                                            ((ek = e.key) == key ||
                                                    (ek != null && key.equals(ek)))) {
                                        oldVal = e.val;
                                        //putIfAbsent()
                                        if (!onlyIfAbsent)
                                            e.val = value;
                                        break;
                                    }
                                    Node<K,V> pred = e;
                                    //链表尾部  直接插入
                                    if ((e = e.next) == null) {
                                        pred.next = new Node<K,V>(hash, key,
                                                value, null);
                                        break;
                                    }
                                }
                            }
                            //树节点，按照树的插入操作进行插入
                            else if (f instanceof TreeBin) {
                                Node<K,V> p;
                                binCount = 2;
                                if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key,
                                        value)) != null) {
                                    oldVal = p.val;
                                    if (!onlyIfAbsent)
                                        p.val = value;
                                }
                            }
                        }
                    }
                    if (binCount != 0) {
                        // 如果链表长度已经达到临界值8 就需要把链表转换为树结构
                        if (binCount >= TREEIFY_THRESHOLD)
                            treeifyBin(tab, i);
                        if (oldVal != null)
                            return oldVal;
                        break;
                    }
                }
            }
    
            //size + 1  
            addCount(1L, binCount);
            return null;
        }
    

按照上面的源码，我们可以确定put整个流程如下：

  * 判空；ConcurrentHashMap的key、value都不允许为null
  * 计算hash。利用方法计算hash值。

    
    
        static final int spread(int h) {
            return (h ^ (h >>> 16)) & HASH_BITS;
        }
    

  * 遍历table，进行节点插入操作，过程如下： 
    * 如果table为空，则表示ConcurrentHashMap还没有初始化，则进行初始化操作：initTable()
    * 根据hash值获取节点的位置i，若该位置为空，则直接插入，这个过程是不需要加锁的。计算f位置：i=(n – 1) & hash
    * 如果检测到fh = f.hash == -1，则f是ForwardingNode节点，表示有其他线程正在进行扩容操作，则帮助线程一起进行扩容操作
    * 如果f.hash >= 0 表示是链表结构，则遍历链表，如果存在当前key节点则替换value，否则插入到链表尾部。如果f是TreeBin类型节点，则按照红黑树的方法更新或者增加节点
    * 若链表长度 > TREEIFY_THRESHOLD(默认是8)，则将链表转换为红黑树结构
  * 调用addCount方法，ConcurrentHashMap的size + 1

这里整个put操作已经完成。

## get操作

ConcurrentHashMap的get操作还是挺简单的，无非就是通过hash来找key相同的节点而已，当然需要区分链表和树形两种情况。

    
    
        public V get(Object key) {
            Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
            // 计算hash
            int h = spread(key.hashCode());
            if ((tab = table) != null && (n = tab.length) > 0 &&
                    (e = tabAt(tab, (n - 1) & h)) != null) {
                // 搜索到的节点key与传入的key相同且不为null,直接返回这个节点
                if ((eh = e.hash) == h) {
                    if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                        return e.val;
                }
                // 树
                else if (eh < 0)
                    return (p = e.find(h, key)) != null ? p.val : null;
                // 链表，遍历
                while ((e = e.next) != null) {
                    if (e.hash == h &&
                            ((ek = e.key) == key || (ek != null && key.equals(ek))))
                        return e.val;
                }
            }
            return null;
        }
    

get操作的整个逻辑非常清楚：

  * 计算hash值
  * 判断table是否为空，如果为空，直接返回null
  * 根据hash值获取table中的Node节点（tabAt(tab, (n – 1) & h)），然后根据链表或者树形方式找到相对应的节点，返回其value值。

## size 操作

ConcurrentHashMap的size()方法我们虽然用得不是很多，但是我们还是很有必要去了解的。ConcurrentHashMap的size()方法返回的是一个不精确的值，因为在进行统计的时候有其他线程正在进行插入和删除操作。当然为了这个不精确的值，ConcurrentHashMap也是操碎了心。

为了更好地统计size，ConcurrentHashMap提供了baseCount、counterCells两个辅助变量和一个CounterCell辅助内部类。

    
    
        @sun.misc.Contended static final class CounterCell {
            volatile long value;
            CounterCell(long x) { value = x; }
        }
    
        //ConcurrentHashMap中元素个数,但返回的不一定是当前Map的真实元素个数。基于CAS无锁更新
        private transient volatile long baseCount;
    
        private transient volatile CounterCell[] counterCells;
    

这里我们需要清楚CounterCell 的定义

size()方法定义如下：

    
    
        public int size() {
            long n = sumCount();
            return ((n < 0L) ? 0 :
                    (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE :
                    (int)n);
        }
    

内部调用sunmCount()：

    
    
        final long sumCount() {
            CounterCell[] as = counterCells; CounterCell a;
            long sum = baseCount;
            if (as != null) {
                for (int i = 0; i < as.length; ++i) {
                    //遍历，所有counter求和
                    if ((a = as[i]) != null)
                        sum += a.value;     
                }
            }
            return sum;
        }
    

sumCount()就是迭代counterCells来统计sum的过程。我们知道put操作时，肯定会影响size()，我们就来看看CouncurrentHashMap是如何为了这个不和谐的size()操碎了心。

在put()方法最后会调用addCount()方法，该方法主要做两件事，一件更新baseCount的值，第二件检测是否进行扩容，我们只看更新baseCount部分：

    
    
        private final void addCount(long x, int check) {
            CounterCell[] as; long b, s;
            // s = b + x，完成baseCount++操作；
            if ((as = counterCells) != null ||
                !U.compareAndSwapLong(this, BASECOUNT, b = baseCount, s = b + x)) {
                CounterCell a; long v; int m;
                boolean uncontended = true;
                if (as == null || (m = as.length - 1) < 0 ||
                    (a = as[ThreadLocalRandom.getProbe() & m]) == null ||
                    !(uncontended =
                      U.compareAndSwapLong(a, CELLVALUE, v = a.value, v + x))) {
                    //  多线程CAS发生失败时执行
                    fullAddCount(x, uncontended);
                    return;
                }
                if (check <= 1)
                    return;
                s = sumCount();
            }
    
            // 检查是否进行扩容
        }
    

x == 1，如果counterCells == null，则U.compareAndSwapLong(this, BASECOUNT, b =
baseCount, s = b +
x)，如果并发竞争比较大可能会导致改过程失败，如果失败则最终会调用fullAddCount()方法。其实为了提高高并发的时候baseCount可见性的失败问题，又避免一直重试，JDK
8
引入了类Striped64,其中LongAdder和DoubleAdder都是基于该类实现的，而CounterCell也是基于Striped64实现的。如果counterCells
！= null，且uncontended = U.compareAndSwapLong(a, CELLVALUE, v = a.value, v +
x)也失败了，同样会调用fullAddCount()方法，最后调用sumCount()计算s。

其实在1.8中，它不推荐size()方法，而是推崇mappingCount()方法，该方法的定义和size()方法基本一致：

    
    
        public long mappingCount() {
            long n = sumCount();
            return (n < 0L) ? 0L : n; // ignore transient negative values
        }
    

## 扩容操作

当ConcurrentHashMap中table元素个数达到了容量阈值（sizeCtl）时，则需要进行扩容操作。在put操作时最后一个会调用addCount(long
x, int check)，该方法主要做两个工作：1.更新baseCount；2.检测是否需要扩容操作。如下：

    
    
        private final void addCount(long x, int check) {
            CounterCell[] as; long b, s;
            // 更新baseCount
    
            //check >= 0 :则需要进行扩容操作
            if (check >= 0) {
                Node<K,V>[] tab, nt; int n, sc;
                while (s >= (long)(sc = sizeCtl) && (tab = table) != null &&
                        (n = tab.length) < MAXIMUM_CAPACITY) {
                    int rs = resizeStamp(n);
                    if (sc < 0) {
                        if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 ||
                                sc == rs + MAX_RESIZERS || (nt = nextTable) == null ||
                                transferIndex <= 0)
                            break;
                        if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1))
                            transfer(tab, nt);
                    }
    
                    //当前线程是唯一的或是第一个发起扩容的线程  此时nextTable=null
                    else if (U.compareAndSwapInt(this, SIZECTL, sc,
                            (rs << RESIZE_STAMP_SHIFT) + 2))
                        transfer(tab, null);
                    s = sumCount();
                }
            }
        }
    

transfer()方法为ConcurrentHashMap扩容操作的核心方法。由于ConcurrentHashMap支持多线程扩容，而且也没有进行加锁，所以实现会变得有点儿复杂。整个扩容操作分为两步：

  1. 构建一个nextTable，其大小为原来大小的两倍，这个步骤是在单线程环境下完成的
  2. 将原来table里面的内容复制到nextTable中，这个步骤是允许多线程操作的，所以性能得到提升，减少了扩容的时间消耗

我们先来看看源代码，然后再一步一步分析：

    
    
        private final void transfer(Node<K,V>[] tab, Node<K,V>[] nextTab) {
            int n = tab.length, stride;
            // 每核处理的量小于16，则强制赋值16
            if ((stride = (NCPU > 1) ? (n >>> 3) / NCPU : n) < MIN_TRANSFER_STRIDE)
                stride = MIN_TRANSFER_STRIDE; // subdivide range
            if (nextTab == null) {            // initiating
                try {
                    @SuppressWarnings("unchecked")
                    Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n << 1];        //构建一个nextTable对象，其容量为原来容量的两倍
                    nextTab = nt;
                } catch (Throwable ex) {      // try to cope with OOME
                    sizeCtl = Integer.MAX_VALUE;
                    return;
                }
                nextTable = nextTab;
                transferIndex = n;
            }
            int nextn = nextTab.length;
            // 连接点指针，用于标志位（fwd的hash值为-1，fwd.nextTable=nextTab）
            ForwardingNode<K,V> fwd = new ForwardingNode<K,V>(nextTab);
            // 当advance == true时，表明该节点已经处理过了
            boolean advance = true;
            boolean finishing = false; // to ensure sweep before committing nextTab
            for (int i = 0, bound = 0;;) {
                Node<K,V> f; int fh;
                // 控制 --i ,遍历原hash表中的节点
                while (advance) {
                    int nextIndex, nextBound;
                    if (--i >= bound || finishing)
                        advance = false;
                    else if ((nextIndex = transferIndex) <= 0) {
                        i = -1;
                        advance = false;
                    }
                    // 用CAS计算得到的transferIndex
                    else if (U.compareAndSwapInt
                            (this, TRANSFERINDEX, nextIndex,
                                    nextBound = (nextIndex > stride ?
                                            nextIndex - stride : 0))) {
                        bound = nextBound;
                        i = nextIndex - 1;
                        advance = false;
                    }
                }
                if (i < 0 || i >= n || i + n >= nextn) {
                    int sc;
                    // 已经完成所有节点复制了
                    if (finishing) {
                        nextTable = null;
                        table = nextTab;        // table 指向nextTable
                        sizeCtl = (n << 1) - (n >>> 1);     // sizeCtl阈值为原来的1.5倍
                        return;     // 跳出死循环，
                    }
                    // CAS 更扩容阈值，在这里面sizectl值减一，说明新加入一个线程参与到扩容操作
                    if (U.compareAndSwapInt(this, SIZECTL, sc = sizeCtl, sc - 1)) {
                        if ((sc - 2) != resizeStamp(n) << RESIZE_STAMP_SHIFT)
                            return;
                        finishing = advance = true;
                        i = n; // recheck before commit
                    }
                }
                // 遍历的节点为null，则放入到ForwardingNode 指针节点
                else if ((f = tabAt(tab, i)) == null)
                    advance = casTabAt(tab, i, null, fwd);
                // f.hash == -1 表示遍历到了ForwardingNode节点，意味着该节点已经处理过了
                // 这里是控制并发扩容的核心
                else if ((fh = f.hash) == MOVED)
                    advance = true; // already processed
                else {
                    // 节点加锁
                    synchronized (f) {
                        // 节点复制工作
                        if (tabAt(tab, i) == f) {
                            Node<K,V> ln, hn;
                            // fh >= 0 ,表示为链表节点
                            if (fh >= 0) {
                                // 构造两个链表  一个是原链表  另一个是原链表的反序排列
                                int runBit = fh & n;
                                Node<K,V> lastRun = f;
                                for (Node<K,V> p = f.next; p != null; p = p.next) {
                                    int b = p.hash & n;
                                    if (b != runBit) {
                                        runBit = b;
                                        lastRun = p;
                                    }
                                }
                                if (runBit == 0) {
                                    ln = lastRun;
                                    hn = null;
                                }
                                else {
                                    hn = lastRun;
                                    ln = null;
                                }
                                for (Node<K,V> p = f; p != lastRun; p = p.next) {
                                    int ph = p.hash; K pk = p.key; V pv = p.val;
                                    if ((ph & n) == 0)
                                        ln = new Node<K,V>(ph, pk, pv, ln);
                                    else
                                        hn = new Node<K,V>(ph, pk, pv, hn);
                                }
                                // 在nextTable i 位置处插上链表
                                setTabAt(nextTab, i, ln);
                                // 在nextTable i + n 位置处插上链表
                                setTabAt(nextTab, i + n, hn);
                                // 在table i 位置处插上ForwardingNode 表示该节点已经处理过了
                                setTabAt(tab, i, fwd);
                                // advance = true 可以执行--i动作，遍历节点
                                advance = true;
                            }
                            // 如果是TreeBin，则按照红黑树进行处理，处理逻辑与上面一致
                            else if (f instanceof TreeBin) {
                                TreeBin<K,V> t = (TreeBin<K,V>)f;
                                TreeNode<K,V> lo = null, loTail = null;
                                TreeNode<K,V> hi = null, hiTail = null;
                                int lc = 0, hc = 0;
                                for (Node<K,V> e = t.first; e != null; e = e.next) {
                                    int h = e.hash;
                                    TreeNode<K,V> p = new TreeNode<K,V>
                                            (h, e.key, e.val, null, null);
                                    if ((h & n) == 0) {
                                        if ((p.prev = loTail) == null)
                                            lo = p;
                                        else
                                            loTail.next = p;
                                        loTail = p;
                                        ++lc;
                                    }
                                    else {
                                        if ((p.prev = hiTail) == null)
                                            hi = p;
                                        else
                                            hiTail.next = p;
                                        hiTail = p;
                                        ++hc;
                                    }
                                }
    
                                // 扩容后树节点个数若<=6，将树转链表
                                ln = (lc <= UNTREEIFY_THRESHOLD) ? untreeify(lo) :
                                        (hc != 0) ? new TreeBin<K,V>(lo) : t;
                                hn = (hc <= UNTREEIFY_THRESHOLD) ? untreeify(hi) :
                                        (lc != 0) ? new TreeBin<K,V>(hi) : t;
                                setTabAt(nextTab, i, ln);
                                setTabAt(nextTab, i + n, hn);
                                setTabAt(tab, i, fwd);
                                advance = true;
                            }
                        }
                    }
                }
            }
        }
    

上面的源码有点儿长，稍微复杂了一些，在这里我们抛弃它多线程环境，我们从单线程角度来看：

  1. 为每个内核分任务，并保证其不小于16
  2. 检查nextTable是否为null，如果是，则初始化nextTable，使其容量为table的两倍
  3. 死循环遍历节点，知道finished：节点从table复制到nextTable中，支持并发，请思路如下： 
    * 如果节点 f 为null，则插入ForwardingNode（采用Unsafe.compareAndSwapObjectf方法实现），这个是触发并发扩容的关键
    * 如果f为链表的头节点（fh >= 0）,则先构造一个反序链表，然后把他们分别放在nextTable的i和i + n位置，并将ForwardingNode 插入原节点位置，代表已经处理过了
    * 如果f为TreeBin节点，同样也是构造一个反序 ，同时需要判断是否需要进行unTreeify()操作，并把处理的结果分别插入到nextTable的i 和i+nw位置，并插入ForwardingNode 节点
  4. 所有节点复制完成后，则将table指向nextTable，同时更新sizeCtl = nextTable的0.75倍，完成扩容过程

在多线程环境下，ConcurrentHashMap用两点来保证正确性：ForwardingNode和synchronized。当一个线程遍历到的节点如果是ForwardingNode，则继续往后遍历，如果不是，则将该节点加锁，防止其他线程进入，完成后设置ForwardingNode节点，以便要其他线程可以看到该节点已经处理过了，如此交叉进行，高效而又安全。

下图是扩容的过程（来自：http://blog.csdn.net/u010723709/article/details/48007881）：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120821001.png)

在put操作时如果发现fh.hash = -1，则表示正在进行扩容操作，则当前线程会协助进行扩容操作。

    
    
                else if ((fh = f.hash) == MOVED)
                    tab = helpTransfer(tab, f);
    

helpTransfer()方法为协助扩容方法，当调用该方法的时候，nextTable一定已经创建了，所以该方法主要则是进行复制工作。如下：

    
    
        final Node<K,V>[] helpTransfer(Node<K,V>[] tab, Node<K,V> f) {
            Node<K,V>[] nextTab; int sc;
            if (tab != null && (f instanceof ForwardingNode) &&
                    (nextTab = ((ForwardingNode<K,V>)f).nextTable) != null) {
                int rs = resizeStamp(tab.length);
                while (nextTab == nextTable && table == tab &&
                        (sc = sizeCtl) < 0) {
                    if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 ||
                            sc == rs + MAX_RESIZERS || transferIndex <= 0)
                        break;
                    if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1)) {
                        transfer(tab, nextTab);
                        break;
                    }
                }
                return nextTab;
            }
            return table;
        }
    

## 转换红黑树

在put操作是，如果发现链表结构中的元素超过了TREEIFY_THRESHOLD（默认为8），则会把链表转换为红黑树，已便于提高查询效率。如下：

    
    
    if (binCount >= TREEIFY_THRESHOLD)
        treeifyBin(tab, i);
    

调用treeifyBin方法用与将链表转换为红黑树。

    
    
    private final void treeifyBin(Node<K,V>[] tab, int index) {
            Node<K,V> b; int n, sc;
            if (tab != null) {
                if ((n = tab.length) < MIN_TREEIFY_CAPACITY)//如果table.length<64 就扩大一倍 返回
                    tryPresize(n << 1);
                else if ((b = tabAt(tab, index)) != null && b.hash >= 0) {
                    synchronized (b) {
                        if (tabAt(tab, index) == b) {
                            TreeNode<K,V> hd = null, tl = null;
                            //构造了一个TreeBin对象 把所有Node节点包装成TreeNode放进去
                            for (Node<K,V> e = b; e != null; e = e.next) {
                                TreeNode<K,V> p =
                                    new TreeNode<K,V>(e.hash, e.key, e.val,
                                                      null, null);//这里只是利用了TreeNode封装 而没有利用TreeNode的next域和parent域
                                if ((p.prev = tl) == null)
                                    hd = p;
                                else
                                    tl.next = p;
                                tl = p;
                            }
                            //在原来index的位置 用TreeBin替换掉原来的Node对象
                            setTabAt(tab, index, new TreeBin<K,V>(hd));
                        }
                    }
                }
            }
        }
    

从上面源码可以看出，构建红黑树的过程是同步的，进入同步后过程如下：

  1. 根据table中index位置Node链表，重新生成一个hd为头结点的TreeNode
  2. 根据hd头结点，生成TreeBin树结构，并用TreeBin替换掉原来的Node对象。

整个红黑树的构建过程有点儿复杂，关于ConcurrentHashMap 红黑树的构建过程，我们后续分析。

**【注】：ConcurrentHashMap的扩容和链表转红黑树稍微复杂点，后续另起博文分析**

