  * 1 红黑树
    * 1.1 旋转
    * 1.2 红黑树插入节点
    * 1.3 ConcurrentHashMap 的treeifyBin过程

> 原文出自:<http://cmsblogs.com>

* * *

> 原文出处<http://cmsblogs.com/> 『 **chenssy** 』

在[【死磕Java并发】—–J.U.C之Java并发容器：ConcurrentHashMap](http://cmsblogs.com/?p=2283)一文中详细阐述了ConcurrentHashMap的实现过程，其中有提到在put操作时，如果发现链表结构中的元素超过了TREEIFY_THRESHOLD（默认为8），则会把链表转换为红黑树，已便于提高查询效率。代码如下：

    
    
    if (binCount >= TREEIFY_THRESHOLD)
        treeifyBin(tab, i);
    

下面博主将详细分析整个过程，并用一个链表转换为红黑树的过程为案例来分析。博文从如下几个方法进行分析阐述：

  1. 红黑树
  2. ConcurrentHashMap链表转红黑树源码分析
  3. 链表转红黑树案例

## 红黑树

先看红黑树的基本概念：红黑树是一课特殊的平衡二叉树，主要用它存储有序的数据，提供高效的数据检索，时间复杂度为O(lgn)。红黑树每个节点都有一个标识位表示颜色，红色或黑色，具备五种特性：

  1. 每个节点非红即黑
  2. 根节点为黑色
  3. 每个叶子节点为黑色。叶子节点为NIL节点，即空节点
  4. 如果一个节点为红色，那么它的子节点一定是黑色
  5. 从一个节点到该节点的子孙节点的所有路径包含相同个数的黑色节点

**请牢记这五个特性，它在维护红黑树时选的格外重要**

红黑树结构图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822001.png)

对于红黑树而言，它主要包括三个步骤：左旋、右旋、着色。所有不符合上面五个特性的“红黑树”都可以通过这三个步骤调整为正规的红黑树。

### 旋转

当对红黑树进行插入和删除操作时可能会破坏红黑树的特性。为了继续保持红黑树的性质，则需要通过对红黑树进行旋转和重新着色处理，其中旋转包括左旋、右旋。

**左旋**

左旋示意图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822002.gif)

左旋处理过程比较简单，将E的右孩子S调整为E的父节点、S节点的左孩子作为调整后E节点的右孩子。

**右旋**

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822003.gif)

###  红黑树插入节点

由于链表转换为红黑树只有添加操作，加上篇幅有限所以这里就只介绍红黑树的插入操作，关于红黑树的详细情况，烦请各位Google。

在分析过程中，我们已下面一颗简单的树为案例，根节点G、有两个子节点P、U，我们新增的节点为N

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822004.png)

红黑树默认插入的节点为红色，因为如果为黑色，则一定会破坏红黑树的规则5（从一个节点到该节点的子孙节点的所有路径包含相同个数的黑色节点）。尽管默认的节点为红色，插入之后也会导致红黑树失衡。红黑树插入操作导致其失衡的主要原因在于插入的当前节点与其父节点的颜色冲突导致（红红，违背规则4：如果一个节点为红色，那么它的子节点一定是黑色）。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822005.png)

要解决这类冲突就靠上面三个操作：左旋、右旋、重新着色。由于是红红冲突，那么其祖父节点一定存在且为黑色，但是叔父节点U颜色不确定，根据叔父节点的颜色则可以做相应的调整。

**1 叔父U节点是红色**

如果叔父节点为红色，那么处理过程则变得比较简单了：更换G与P、U节点的颜色，下图（一）。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822006.png)

当然这样变色可能会导致另外一个问题了，就是父节点G与其父节点GG颜色冲突（上图二），那么这里需要将G节点当做新增节点进行递归处理。

**2 叔父U节点为黑叔**

如果当前节点的叔父节点U为黑色，则需要根据当前节点N与其父节点P的位置决定，分为四种情况：

  1. N是P的右子节点、P是G的右子节点
  2. N是P的左子节点，P是G的左子节点
  3. N是P的左子节点，P是G的右子节点
  4. N是P的右子节点，P是G的左子节点

情况1、2称之为外侧插入、情况3、4是内侧插入，之所以这样区分是因为他们的处理方式是相对的。

**2.1 外侧插入**

以N是P的右子节点、P是G的右子节点为例，这种情况的处理方式为：以P为支点进行左旋，然后交换P和G的颜色（P设置为黑色，G设置为红色），如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822007.png)

左外侧的情况（N是P的左子节点，P是G的左子节点）和上面的处理方式一样，先右旋，然后重新着色。

**2.2 内侧插入**

以N是P的左子节点，P是G的右子节点情况为例。内侧插入的情况稍微复杂些，经过一次旋转、着色是无法调整为红黑树的，处理方法如下：先进行一次右旋，再进行一次左旋，然后重新着色，即可完成调整。注意这里两次右旋都是以新增节点N为支点不是P。这里将N节点的两个NIL节点命名为X、L。如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822008.png)

至于左内侧则处理逻辑如下：先进行右旋，然后左旋，最后着色。

### ConcurrentHashMap 的treeifyBin过程

ConcurrentHashMap的链表转换为红黑树过程就是一个红黑树增加节点的过程。在put过程中，如果发现链表结构中的元素超过了TREEIFY_THRESHOLD（默认为8），则会把链表转换为红黑树：

    
    
    if (binCount >= TREEIFY_THRESHOLD)
        treeifyBin(tab, i);
    

treeifyBin主要的功能就是把链表所有的节点Node转换为TreeNode节点，如下：

    
    
        private final void treeifyBin(Node<K,V>[] tab, int index) {
            Node<K,V> b; int n, sc;
            if (tab != null) {
                if ((n = tab.length) < MIN_TREEIFY_CAPACITY)
                    tryPresize(n << 1);
                else if ((b = tabAt(tab, index)) != null && b.hash >= 0) {
                    synchronized (b) {
                        if (tabAt(tab, index) == b) {
                            TreeNode<K,V> hd = null, tl = null;
                            for (Node<K,V> e = b; e != null; e = e.next) {
                                TreeNode<K,V> p =
                                    new TreeNode<K,V>(e.hash, e.key, e.val,
                                                      null, null);
                                if ((p.prev = tl) == null)
                                    hd = p;
                                else
                                    tl.next = p;
                                tl = p;
                            }
                            setTabAt(tab, index, new TreeBin<K,V>(hd));
                        }
                    }
                }
            }
        }
    

先判断当前Node的数组长度是否小于MIN_TREEIFY_CAPACITY（64），如果小于则调用tryPresize扩容处理以缓解单个链表元素过大的性能问题。否则则将Node节点的链表转换为TreeNode的节点链表，构建完成之后调用setTabAt()构建红黑树。TreeNode继承Node，如下：

    
    
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
            ......
        }
    

我们以下面一个链表作为案例，结合源代码来分析ConcurrentHashMap创建红黑树的过程：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120822009.png)

**12**

12作为跟节点，直接为将红编程黑即可，对应源码：

    
    
                    next = (TreeNode<K,V>)x.next;
                    x.left = x.right = null;
                    if (r == null) {
                        x.parent = null;
                        x.red = false;
                        r = x;
                    }
    

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220010.png)

( **【注】：为了方便起见，这里省略NIL节点，后面也一样** )

**1**

此时根节点root不为空，则插入节点时需要找到合适的插入位置，源码如下：

    
    
                        K k = x.key;
                        int h = x.hash;
                        Class<?> kc = null;
                        for (TreeNode<K,V> p = r;;) {
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
                                TreeNode<K,V> xp = p;
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
    

从上面可以看到起处理逻辑如下：

  1. 计算节点的hash值 p。dir 表示为往左移还是往右移。x 表示要插入的节点，p 表示带比较的节点。
  2. 从根节点出发，计算比较节点p的的hash值 ph ，若ph > h ,则dir = -1 ,表示左移，取p = p.left。若p == null则插入，若 p != null，则继续比较，直到直到一个合适的位置，最后调用balanceInsertion()方法调整红黑树结构。ph < h，右移。
  3. 如果ph = h，则表示节点“冲突”（和HashMap冲突一致），那怎么处理呢？首先调用comparableClassFor()方法判断节点的key是否实现了Comparable接口，如果kc ！= null ，则通过compareComparables()方法通过compareTo()比较带下，如果还是返回 0，即dir == 0，则调用tieBreakOrder()方法来比较了。tieBreakOrder如下：

    
    
            static int tieBreakOrder(Object a, Object b) {
                int d;
                if (a == null || b == null ||
                    (d = a.getClass().getName().
                     compareTo(b.getClass().getName())) == 0)
                    d = (System.identityHashCode(a) <= System.identityHashCode(b) ?
                         -1 : 1);
                return d;
            }
    

tieBreakOrder()方法最终还是通过调用System.identityHashCode()方法来比较。

确定插入位置后，插入，由于插入的节点有可能会打破红黑树的结构，所以插入后调用balanceInsertion()方法来调整红黑树结构。

    
    
        static <K,V> TreeNode<K,V> balanceInsertion(TreeNode<K,V> root,
                                                    TreeNode<K,V> x) {
            x.red = true;       // 所有节点默认插入为红
            for (TreeNode<K,V> xp, xpp, xppl, xppr;;) {
    
                // x.parent == null，为跟节点，置黑即可
                if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                }
                // x 父节点为黑色，或者x 的祖父节点为空，直接插入返回
                else if (!xp.red || (xpp = xp.parent) == null)
                    return root;
    
                /*
                 * x 的 父节点为红色
                 * ---------------------
                 * x 的 父节点 为 其祖父节点的左子节点
                 */
                if (xp == (xppl = xpp.left)) {
                    /*
                     * x的叔父节点存在，且为红色，颜色交换即可
                     * x的父节点、叔父节点变为黑色，祖父节点变为红色
                     */
                    if ((xppr = xpp.right) != null && xppr.red) {
                        xppr.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    }
                    else {
                        /*
                         * x 为 其父节点的右子节点，则为内侧插入
                         * 则先左旋，然后右旋
                         */
                        if (x == xp.right) {
                            // 左旋
                            root = rotateLeft(root, x = xp);
                            // 左旋之后x则会变成xp的父节点
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
    
                        /**
                         * 这里有两部分。
                         * 第一部分：x 原本就是其父节点的左子节点，则为外侧插入，右旋即可
                         * 第二部分：内侧插入后，先进行左旋，然后右旋
                         */
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateRight(root, xpp);
                            }
                        }
                    }
                }
    
                /**
                 * 与上相对应
                 */
                else {
                    if (xppl != null && xppl.red) {
                        xppl.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    }
                    else {
                        if (x == xp.left) {
                            root = rotateRight(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateLeft(root, xpp);
                            }
                        }
                    }
                }
            }
        }
    

回到节点1，其父节点为黑色，即：

    
    
                else if (!xp.red || (xpp = xp.parent) == null)
                    return root;
    

直接插入：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220011.png)

**9**

9作为1的右子节点插入，但是存在红红冲突，此时9的并没有叔父节点。9的父节点1为12的左子节点，9为其父节点1的右子节点，所以处理逻辑是先左旋，然后右旋，对应代码如下：

    
    
                            if (x == xp.right) {
                                root = rotateLeft(root, x = xp);
                                xpp = (xp = x.parent) == null ? null : xp.parent;
                            }
                            if (xp != null) {
                                xp.red = false;
                                if (xpp != null) {
                                    xpp.red = true;
                                    root = rotateRight(root, xpp);
                                }
                            }
    

图例变化如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220012.png)

**2**

节点2 作为1 的右子节点插入，红红冲突，切其叔父节点为红色，直接变色即可，：

    
    
                        if ((xppr = xpp.right) != null && xppr.red) {
                            xppr.red = false;
                            xp.red = false;
                            xpp.red = true;
                            x = xpp;
                        }
    

对应图例为：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220013.png)

**0**

节点0作为1的左子节点插入，由于其父节点为黑色，不会插入后不会打破红黑树结构，直接插入即可：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220014.png)

**11**

节点11作为12的左子节点，其父节点12为黑色，和0一样道理，直接插入：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220015.png)

**7**

节点7作为2右子节点插入，红红冲突，其叔父节点0为红色，变色即可：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220016.png)

**19**

节点19作为节点12的右子节点，直接插入：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220017.png)

至此，整个过程已经完成了，最终结果如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/20181208220018.png)

