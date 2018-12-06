##java提高篇(二二)---LinkedList
##一、概述

##
## LinkedList与ArrayList一样实现List接口，只是ArrayList是List接口的大小可变数组的实现，LinkedList是List接口链表的实现。基于链表实现的方式使得LinkedList在插入和删除时更优于ArrayList，而随机访问则比ArrayList逊色些。

##
## LinkedList实现所有可选的列表操作，并允许所有的元素包括null。

##
## 除了实现 List 接口外，LinkedList 类还为在列表的开头及结尾 get、remove 和 insert 元素提供了统一的命名方法。这些操作允许将链接列表用作堆栈、队列或双端队列。

##
## 此类实现 Deque 接口，为 add、poll 提供先进先出队列操作，以及其他堆栈和双端队列操作。 

##
## 所有操作都是按照双重链接列表的需要执行的。在列表中编索引的操作将从开头或结尾遍历列表（从靠近指定索引的一端）。

##
## 同时，与ArrayList一样此实现不是同步的。

##
## （以上摘自JDK 6.0 API）。
##二、源码分析 2.1、定义

##
## 首先我们先看LinkedList的定义：	public class LinkedList<E>    extends AbstractSequentialList<E>    implements List<E>, Deque<E>, Cloneable, java.io.Serializable

##
## 从这段代码中我们可以清晰地看出LinkedList继承AbstractSequentialList，实现List、Deque、Cloneable、Serializable。其中AbstractSequentialList提供了 List 接口的骨干实现，从而最大限度地减少了实现受“连续访问”数据存储（如链接列表）支持的此接口所需的工作,从而以减少实现List接口的复杂度。Deque一个线性 collection，支持在两端插入和移除元素，定义了双端队列的操作。2.2、属性

##
## 在LinkedList中提供了两个基本属性size、header。	private transient Entry<E> header = new Entry<E>(null, null, null);private transient int size = 0;

##
## 其中size表示的LinkedList的大小，header表示链表的表头，Entry为节点对象。	private static class Entry<E> {        E element;        //元素节点        Entry<E> next;    //下一个元素        Entry<E> previous;  //上一个元素        Entry(E element, Entry<E> next, Entry<E> previous) {            this.element = element;            this.next = next;            this.previous = previous;        	}    	}

##
## 上面为Entry对象的源代码，Entry为LinkedList的内部类，它定义了存储的元素。该元素的前一个元素、后一个元素，这是典型的双向链表定义方式。2.3、构造方法

##
## LinkedList提高了两个构造方法：LinkedLis()和LinkedList(Collection<? extends E> c)。	/**     *  构造一个空列表。     */    public LinkedList() {        header.next = header.previous = header;    	}        /**     *  构造一个包含指定 collection 中的元素的列表，这些元素按其 collection 的迭代器返回的顺序排列。     */    public LinkedList(Collection<? extends E> c) {        this();        addAll(c);    	}

##
## LinkedList()构造一个空列表。里面没有任何元素，仅仅只是将header节点的前一个元素、后一个元素都指向自身。

##
## LinkedList(Collection<? extends E> c)： 构造一个包含指定 collection 中的元素的列表，这些元素按其 collection 的迭代器返回的顺序排列。该构造函数首先会调用LinkedList()，构造一个空列表，然后调用了addAll()方法将Collection中的所有元素添加到列表中。以下是addAll()的源代码：	/**     *  添加指定 collection 中的所有元素到此列表的结尾，顺序是指定 collection 的迭代器返回这些元素的顺序。     */    public boolean addAll(Collection<? extends E> c) {        return addAll(size, c);    	}        /**     * 将指定 collection 中的所有元素从指定位置开始插入此列表。其中index表示在其中插入指定collection中第一个元素的索引     */    public boolean addAll(int index, Collection<? extends E> c) {        //若插入的位置小于0或者大于链表长度，则抛出IndexOutOfBoundsException异常        if (index < 0 || index > size)            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);        Object[] a = c.toArray();        int numNew = a.length;    //插入元素的个数        //若插入的元素为空，则返回false        if (numNew == 0)            return false;        //modCount:在AbstractList中定义的，表示从结构上修改列表的次数        modCount++;        //获取插入位置的节点，若插入的位置在size处，则是头节点，否则获取index位置处的节点        Entry<E> successor = (index == size ? header : entry(index));        //插入位置的前一个节点，在插入过程中需要修改该节点的next引用：指向插入的节点元素        Entry<E> predecessor = successor.previous;        //执行插入动作        for (int i = 0; i < numNew; i++) {            //构造一个节点e，这里已经执行了插入节点动作同时修改了相邻节点的指向引用            //            Entry<E> e = new Entry<E>((E) a[i], successor, predecessor);            //将插入位置前一个节点的下一个元素引用指向当前元素            predecessor.next = e;            //修改插入位置的前一个节点，这样做的目的是将插入位置右移一位，保证后续的元素是插在该元素的后面，确保这些元素的顺序            predecessor = e;        	}        successor.previous = predecessor;        //修改容量大小        size += numNew;        return true;    	}

##
## 在addAll()方法中，涉及到了两个方法，一个是entry(int index)，该方法为LinkedList的私有方法，主要是用来查找index位置的节点元素。	/**     * 返回指定位置(若存在)的节点元素     */    private Entry<E> entry(int index) {        if (index < 0 || index >= size)            throw new IndexOutOfBoundsException("Index: " + index + ", Size: "                    + size);        //头部节点        Entry<E> e = header;        //判断遍历的方向        if (index < (size >> 1)) {            for (int i = 0; i <= index; i++)                e = e.next;        	} else {            for (int i = size; i > index; i--)                e = e.previous;        	}        return e;    	}

##
## 从该方法有两个遍历方向中我们也可以看出LinkedList是双向链表，这也是在构造方法中为什么需要将header的前、后节点均指向自己。

##
## 如果对数据结构有点了解，对上面所涉及的内容应该问题，我们只需要清楚一点：LinkedList是双向链表，其余都迎刃而解。

##
## 由于篇幅有限，下面将就LinkedList中几个常用的方法进行源码分析。2.4、增加方法

##
## add(E e): 将指定元素添加到此列表的结尾。	public boolean add(E e) {    addBefore(e, header);        return true;    	}

##
## 该方法调用addBefore方法，然后直接返回true，对于addBefore()而已，它为LinkedList的私有方法。	private Entry<E> addBefore(E e, Entry<E> entry) {        //利用Entry构造函数构建一个新节点 newEntry，        Entry<E> newEntry = new Entry<E>(e, entry, entry.previous);        //修改newEntry的前后节点的引用，确保其链表的引用关系是正确的        newEntry.previous.next = newEntry;        newEntry.next.previous = newEntry;        //容量+1        size++;        //修改次数+1        modCount++;        return newEntry;    	}

##
## 在addBefore方法中无非就是做了这件事：构建一个新节点newEntry，然后修改其前后的引用。

##
## LinkedList还提供了其他的增加方法：

##
## add(int index, E element)：在此列表中指定的位置插入指定的元素。

##
## addAll(Collection<? extends E> c)：添加指定 collection 中的所有元素到此列表的结尾，顺序是指定 collection 的迭代器返回这些元素的顺序。

##
## addAll(int index, Collection<? extends E> c)：将指定 collection 中的所有元素从指定位置开始插入此列表。

##
## AddFirst(E e): 将指定元素插入此列表的开头。

##
## addLast(E e): 将指定元素添加到此列表的结尾。2.5、移除方法

##
## remove(Object o)：从此列表中移除首次出现的指定元素（如果存在）。该方法的源代码如下：	public boolean remove(Object o) {        if (o==null) {            for (Entry<E> e = header.next; e != header; e = e.next) {                if (e.element==null) {                    remove(e);                    return true;                	}            	}        	} else {            for (Entry<E> e = header.next; e != header; e = e.next) {                if (o.equals(e.element)) {                    remove(e);                    return true;                	}            	}        	}        return false;    	}

##
## 该方法首先会判断移除的元素是否为null，然后迭代这个链表找到该元素节点，最后调用remove(Entry<E> e)，remove(Entry<E> e)为私有方法，是LinkedList中所有移除方法的基础方法，如下：	private E remove(Entry<E> e) {        if (e == header)            throw new NoSuchElementException();        //保留被移除的元素：要返回        E result = e.element;                //将该节点的前一节点的next指向该节点后节点        e.previous.next = e.next;        //将该节点的后一节点的previous指向该节点的前节点        //这两步就可以将该节点从链表从除去：在该链表中是无法遍历到该节点的        e.next.previous = e.previous;        //将该节点归空        e.next = e.previous = null;        e.element = null;        size--;        modCount++;        return result;    	}

##
## 其他的移除方法：

##
## clear()： 从此列表中移除所有元素。

##
## remove()：获取并移除此列表的头（第一个元素）。

##
## remove(int index)：移除此列表中指定位置处的元素。

##
## remove(Objec o)：从此列表中移除首次出现的指定元素（如果存在）。

##
## removeFirst()：移除并返回此列表的第一个元素。

##
## removeFirstOccurrence(Object o)：从此列表中移除第一次出现的指定元素（从头部到尾部遍历列表时）。

##
## removeLast()：移除并返回此列表的最后一个元素。

##
## removeLastOccurrence(Object o)：从此列表中移除最后一次出现的指定元素（从头部到尾部遍历列表时）。2.5、查找方法

##
## 对于查找方法的源码就没有什么好介绍了，无非就是迭代，比对，然后就是返回当前值。

##
## get(int index)：返回此列表中指定位置处的元素。

##
## getFirst()：返回此列表的第一个元素。

##
## getLast()：返回此列表的最后一个元素。

##
## indexOf(Object o)：返回此列表中首次出现的指定元素的索引，如果此列表中不包含该元素，则返回 -1。

##
## lastIndexOf(Object o)：返回此列表中最后出现的指定元素的索引，如果此列表中不包含该元素，则返回 -1。

##
##

##
## >>>>>>欢迎各位关注我的个人站点：http://cmsblogs.com/