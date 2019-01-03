  * 1 二叉堆
    * 1.1 添加元素
    * 1.2 删除元素
  * 2 PriorityBlockingQueue
    * 2.1 入列
    * 2.2 出列

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

我们知道线程Thread可以调用setPriority(int
newPriority)来设置优先级的，线程优先级高的线程先执行，优先级低的后执行。而前面介绍的ArrayBlockingQueue、LinkedBlockingQueue都是采用FIFO原则来确定线程执行的先后顺序，那么有没有一个队列可以支持优先级呢？
PriorityBlockingQueue 。

PriorityBlockingQueue是一个支持优先级的无界阻塞队列。默认情况下元素采用自然顺序升序排序，当然我们也可以通过构造函数来指定Comparator来对元素进行排序。需要注意的是PriorityBlockingQueue不能保证同优先级元素的顺序。

## 二叉堆

由于PriorityBlockingQueue底层采用二叉堆来实现的，所以有必要先介绍下二叉堆。

二叉堆是一种特殊的堆，就结构性而言就是完全二叉树或者是近似完全二叉树，满足树结构性和堆序性。树机构特性就是完全二叉树应该有的结构，堆序性则是：父节点的键值总是保持固定的序关系于任何一个子节点的键值，且每个节点的左子树和右子树都是一个二叉堆。它有两种表现形式：最大堆、最小堆。

最大堆：父节点的键值总是大于或等于任何一个子节点的键值（下右图）

最小堆：父节点的键值总是小于或等于任何一个子节点的键值（下走图）

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827001.png)

二叉堆一般用数组表示，如果父节点的节点位置在n处，那么其左孩子节点为：2 * n + 1 ，其右孩子节点为2 * (n + 1)，其父节点为（n – 1）
/ 2 处。上左图的数组表现形式为：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827002.png)

二叉堆的基本结构了解了，下面来看看二叉堆的添加和删除节点。二叉堆的添加和删除相对于二叉树来说会简单很多。

### 添加元素

首先将要添加的元素N插添加到堆的末尾位置（在二叉堆中我们称之为空穴）。如果元素N放入空穴中而不破坏堆的序（其值大于跟父节点值（最大堆是小于父节点）），那么插入完成。否则，我们则将该元素N的节点与其父节点进行交换，然后与其新父节点进行比较直到它的父节点不在比它小（最大堆是大）或者到达根节点。

假如有如下一个二叉堆

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827003.png)

这是一个最小堆，其父节点总是小于等于任一一个子节点。现在我们添加一个元素2。

第一步：在末尾添加一个元素2，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827004.png)

第二步：元素2比其父节点6小，进行替换，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827005.png)

第三步：继续与其父节点5比较，小于，替换：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827006.png)

第四步：继续比较其跟节点1，发现跟节点比自己小，则完成，到这里元素2插入完毕。所以整个添加元素过程可以概括为：在元素末尾插入元素，然后不断比较替换直到不能移动为止。

复杂度：Ο(logn)

### 删除元素

删除元素与增加元素一样，需要维护整个二叉堆的序。删除位置1的元素（数组下标0），则把最后一个元素空出来移到最前边，然后和它的两个子节点比较，如果两个子节点中较小的节点小于该节点，就将他们交换，知道两个子节点都比该元素大为止。

就上面二叉堆而言，删除的元素为元素1。

第一步：删掉元素1，元素6空出来，如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827007.png)

第二步：与其两个子节点（元素2、元素3）比较，都小，将其中较小的元素（元素2）放入到该空穴中:

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827008.png)

第三步：继续比较两个子节点（元素5、元素7），还是都小，则将较小的元素（元素5）放入到该空穴中：!

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120827009.png)

第四步：比较其子节点（元素8），比该节点小，则元素6放入该空穴位置不会影响二叉堆的树结构，放入：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208270010.png)

到这里整个删除操作就已经完成了。

二叉堆的添加、删除操作还是比较简单的，很容易就理解了。下面我们就参考该内容来开启PriorityBlockingQueue的源代码研究。

## PriorityBlockingQueue

PriorityBlockingQueue继承AbstractQueue，实现BlockingQueue接口。

    
    
    public class PriorityBlockingQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E>, java.io.Serializable
    

定义了一些属性：

    
    
        // 默认容量
        private static final int DEFAULT_INITIAL_CAPACITY = 11;
    
        // 最大容量
        private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
    
        // 二叉堆数组
        private transient Object[] queue;
    
        // 队列元素的个数
        private transient int size;
    
        // 比较器，如果为空，则为自然顺序
        private transient Comparator<? super E> comparator;
    
        // 内部锁
        private final ReentrantLock lock;
    
        private final Condition notEmpty;
    
        //
        private transient volatile int allocationSpinLock;
    
        // 优先队列：主要用于序列化，这是为了兼容之前的版本。只有在序列化和反序列化才非空
        private PriorityQueue<E> q;
    

内部仍然采用可重入锁ReentrantLock来实现同步机制，但是这里只有一个notEmpty的Condition，了解了ArrayBlockingQueue我们知道它定义了两个Condition，之类为何只有一个呢？原因就在于PriorityBlockingQueue是一个无界队列，插入总是会成功，除非消耗尽了资源导致服务器挂。

### 入列

PriorityBlockingQueue提供put()、add()、offer()方法向队列中加入元素。我们这里从put()入手：put(E e)
：将指定元素插入此优先级队列。

    
    
        public void put(E e) {
            offer(e); // never need to block
        }
    

PriorityBlockingQueue是无界的，所以不可能会阻塞。内部调用offer(E e)：

    
    
        public boolean offer(E e) {
            // 不能为null
            if (e == null)
                throw new NullPointerException();
            // 获取锁
            final ReentrantLock lock = this.lock;
            lock.lock();
            int n, cap;
            Object[] array;
            // 扩容
            while ((n = size) >= (cap = (array = queue).length))
                tryGrow(array, cap);
            try {
                Comparator<? super E> cmp = comparator;
                // 根据比较器是否为null，做不同的处理
                if (cmp == null)
                    siftUpComparable(n, e, array);
                else
                    siftUpUsingComparator(n, e, array, cmp);
                size = n + 1;
                // 唤醒正在等待的消费者线程
                notEmpty.signal();
            } finally {
                lock.unlock();
            }
            return true;
        }
    

**siftUpComparable**

当比较器comparator为null时，采用自然排序，调用siftUpComparable方法：

    
    
        private static <T> void siftUpComparable(int k, T x, Object[] array) {
            Comparable<? super T> key = (Comparable<? super T>) x;
            // “上冒”过程
            while (k > 0) {
                // 父级节点 （n - ） / 2
                int parent = (k - 1) >>> 1;
                Object e = array[parent];
    
                // key >= parent 完成（最大堆）
                if (key.compareTo((T) e) >= 0)
                    break;
                // key < parant 替换
                array[k] = e;
                k = parent;
            }
            array[k] = key;
        }
    

这段代码所表示的意思：将元素X插入到数组中，然后进行调整以保持二叉堆的特性。

**siftUpUsingComparator**

当比较器不为null时，采用所指定的比较器，调用siftUpUsingComparator方法：

    
    
        private static <T> void siftUpUsingComparator(int k, T x, Object[] array,
                                           Comparator<? super T> cmp) {
            while (k > 0) {
                int parent = (k - 1) >>> 1;
                Object e = array[parent];
                if (cmp.compare(x, (T) e) >= 0)
                    break;
                array[k] = e;
                k = parent;
            }
            array[k] = x;
        }
    

**扩容：tryGrow**

    
    
        private void tryGrow(Object[] array, int oldCap) {
            lock.unlock();      // 扩容操作使用自旋，不需要锁主锁，释放
            Object[] newArray = null;
            // CAS 占用
            if (allocationSpinLock == 0 && UNSAFE.compareAndSwapInt(this, allocationSpinLockOffset, 0, 1)) {
                try {
    
                    // 新容量  最小翻倍
                    int newCap = oldCap + ((oldCap < 64) ? (oldCap + 2) :  (oldCap >> 1));
    
                    // 超过
                    if (newCap - MAX_ARRAY_SIZE > 0) {    // possible overflow
                        int minCap = oldCap + 1;
                        if (minCap < 0 || minCap > MAX_ARRAY_SIZE)
                            throw new OutOfMemoryError();
                        newCap = MAX_ARRAY_SIZE;        // 最大容量
                    }
                    if (newCap > oldCap && queue == array)
                        newArray = new Object[newCap];
                } finally {
                    allocationSpinLock = 0;     // 扩容后allocationSpinLock = 0 代表释放了自旋锁
                }
            }
            // 到这里如果是本线程扩容newArray肯定是不为null，为null就是其他线程在处理扩容，那就让给别的线程处理
            if (newArray == null)
                Thread.yield();
            // 主锁获取锁
            lock.lock();
            // 数组复制
            if (newArray != null && queue == array) {
                queue = newArray;
                System.arraycopy(array, 0, newArray, 0, oldCap);
            }
        }
    

整个添加元素的过程和上面二叉堆一模一样：先将元素添加到数组末尾，然后采用“上冒”的方式将该元素尽量往上冒。

### 出列

PriorityBlockingQueue提供poll()、remove()方法来执行出对操作。出对的永远都是第一个元素：array[0]。

    
    
       public E poll() {
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                return dequeue();
            } finally {
                lock.unlock();
            }
        }
    

先获取锁，然后调用dequeue()方法：

    
    
        private E dequeue() {
            // 没有元素 返回null
            int n = size - 1;
            if (n < 0)
                return null;
            else {
                Object[] array = queue;
                // 出对元素
                E result = (E) array[0];
                // 最后一个元素（也就是插入到空穴中的元素）
                E x = (E) array[n];
                array[n] = null;
                // 根据比较器释放为null，来执行不同的处理
                Comparator<? super E> cmp = comparator;
                if (cmp == null)
                    siftDownComparable(0, x, array, n);
                else
                    siftDownUsingComparator(0, x, array, n, cmp);
                size = n;
                return result;
            }
        }
    

**siftDownComparable**

如果比较器为null，则调用siftDownComparable来进行自然排序处理：

    
    
        private static <T> void siftDownComparable(int k, T x, Object[] array,
                                                   int n) {
            if (n > 0) {
                Comparable<? super T> key = (Comparable<? super T>)x;
                // 最后一个叶子节点的父节点位置
                int half = n >>> 1;
                while (k < half) {
                    int child = (k << 1) + 1;       // 待调整位置左节点位置
                    Object c = array[child];        //左节点
                    int right = child + 1;          //右节点
    
                    //左右节点比较，取较小的
                    if (right < n &&
                            ((Comparable<? super T>) c).compareTo((T) array[right]) > 0)
                        c = array[child = right];
    
                    //如果待调整key最小，那就退出，直接赋值
                    if (key.compareTo((T) c) <= 0)
                        break;
                    //如果key不是最小，那就取左右节点小的那个放到调整位置，然后小的那个节点位置开始再继续调整
                    array[k] = c;
                    k = child;
                }
                array[k] = key;
            }
        }
    

处理思路和二叉堆删除节点的逻辑一样：就第一个元素定义为空穴，然后把最后一个元素取出来，尝试插入到空穴位置，并与两个子节点值进行比较，如果不符合，则与其中较小的子节点进行替换，然后继续比较调整。

**siftDownUsingComparator**

如果指定了比较器，则采用比较器来进行调整：

    
    
        private static <T> void siftDownUsingComparator(int k, T x, Object[] array,
                                                        int n,
                                                        Comparator<? super T> cmp) {
            if (n > 0) {
                int half = n >>> 1;
                while (k < half) {
                    int child = (k << 1) + 1;
                    Object c = array[child];
                    int right = child + 1;
                    if (right < n && cmp.compare((T) c, (T) array[right]) > 0)
                        c = array[child = right];
                    if (cmp.compare(x, (T) c) <= 0)
                        break;
                    array[k] = c;
                    k = child;
                }
                array[k] = x;
            }
        }
    

PriorityBlockingQueue采用二叉堆来维护，所以整个处理过程不是很复杂，添加操作则是不断“上冒”，而删除操作则是不断“下掉”。掌握二叉堆就掌握了PriorityBlockingQueue，无论怎么变还是。对于PriorityBlockingQueue需要注意的是他是一个无界队列，所以添加操作是不会失败的，除非资源耗尽。

