  * 1 ArrayList的源码解析
  * 2 LinkedList源码分析

> 作者：大菜鸟  
>  出处：<https://mp.weixin.qq.com/s/_tH2PZOA00hl0vgPpB7Bgw>

* * *

在面试中经常碰到：ArrayList和LinkedList的特点和区别？

个人认为这个问题的回答应该分成这几部分：

  1. **介绍ArrayList底层实现**
  2. **介绍LinkedList底层实现**
  3. **两者个适用于哪些场合**

本文也是按照上面这几部分组织的。

## ArrayList的源码解析

**成员属性源码解析**

    
    
    public class ArrayList<E> 
        extends AbstractList<E>
        implements List<E>, RandomAccess
        ,Cloneable, java.io.Serializable {
        private static final long 
           serialVersionUID 
           = 8683452581122892189L;
    
        //默认容量是10
        private static final int 
                 DEFAULT_CAPACITY = 10;
    
        //当传入ArrayList构造器的容量为0时
        //用这个数组表示：容器的容量为0
        private static final Object[] 
               EMPTY_ELEMENTDATA = {};
    

**接上面**

    
    
    /*
    主要作为一个标识位，在扩容时区分：
    默认大小和容量为0，使用默认容量时采取的
    是“懒加载”:即等到add元素的时候才进行实际
    容量的分配，后面扩容函数讲解还会提到这点
    */
    private static final Object[] 
    DEFAULTCAPACITY_EMPTY_ELEMENTDATA={};
    
    //ArrayList底层使用Object数组保存的元素
    transient Object[] elementData; 
    
    //记录当前容器中有多少元素
    private int size;
    

**构造器源码解析**

    
    
    /*
    最常用的构造器之一，实际上就是创建了一个
    指定大小的Object数组来保存之后add的元素
    */
    public ArrayList(int initialCapacity){
        if (initialCapacity > 0) {
           //初始化保存数据的Object数组
            this.elementData
            =new Object[initialCapacity];
        } else if(initialCapacity==0) {
          //标识容量为0：EMPTY_ELEMENTDATA
            this.elementData 
                      = EMPTY_ELEMENTDATA;
        } else {
            throw new 
            IllegalArgumentException(
            "Illegal Capacity: "+
                    initialCapacity);
        }
    }
    
    /*
    无参构造器，指向的是默认容量大小的Object
    数组，注意使用无参构造函数的时候并没有
    直接创建容量 为10(默认容量是10)的Object
    数组,而是采取懒加载的策略：使用
    DEFAULTCAPACITY_EMPTY_ELEMENTDATA,
    这个默认数组的容量是0,所以得区分是
    默认容量，还是你传给构造器的容量参数大小
    本身就是0。在真正执行add操作时才会创建
    Object数组，即在扩容函数中有处理默认容量
    的逻辑，后面会有详细分析。
    */
        public ArrayList() {
            //这个赋值操作仅仅是标识作用
           this.elementData = 
         DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
        }
    
       //省略一部分不常用代码函数
    

**add方法源码解析**

    
    
    /*
    add是ArrayList最常用的接口，逻辑很简单
    */
    public boolean add(E e) {
     /*
     主要用于标识线程安全，即ArrayList只能
    在单线程环境下使用，在多线程环境下会出现并发
    安全问题，modCount主要用于记录对ArrayList的
    修改次数，如果一个线程操作ArrayList期间
    modCount发生了变化即，有多个线程同时修改当前
    这个ArrayList，此时会抛出
    “ConcurrentModificationException”异常，
    这又被称为“failFast机制”，在很多非线程安全的
    类中都有failFast机制：HashMap、 LinkedList
    等。这个机制主要用于迭代器、加强for循环等相关
    功能，也就是一个线程在迭代一个有failfast机制
    容器的时候，如果其他线程改变了容器内的元素，
    迭代的这个线程会抛 
    出“ConcurrentModificationException”异常
    */
        modCount++;
    
    /*
    add操作的核心函数，当使用无参构造器时并没有
    直接分配大小为10的Object数组，这里面有对应 的处理逻辑。
    */  
       //进入该函数
        add(e, elementData, size);
        return true;
    }
    
    private void add(E e,Object[] elementData
                    , int s) {
        /*
        如果使用无参构造器：开始时length为0，
        s也为0.grow()核心函数,扩容/初始化操作
        */
        if (s == elementData.length)
            elementData = grow();
        elementData[s] = e;
        size = s + 1;
    }
    

**grow相关方法源码解析**

    
    
    private Object[] grow() {
        //继续追踪
        return grow(size + 1);
    }
    
    private Object[] grow(int minCapacity){
        /*
      使用数组复制的方式，扩容：将elementData
      所有元素复制到一个新数组中，这个新数组的
      长度是newCapacity()函数的返回值，之后再
      把这个新数组赋值给elementData，完成扩容
      操作
        */
        //进入newCapacity()函数
        return elementData = 
        Arrays.copyOf(elementData,
              newCapacity(minCapacity));
    }
    
    //返回的是扩容后数组的长度
    private int newCapacity(int minCapacity){
        int oldCapacity=elementData.length;
        //扩容后的容量为原来容量的1.5倍
        int newCapacity = oldCapacity 
                + (oldCapacity >> 1);
        if (newCapacity-minCapacity <=0){
            if (elementData ==
            DEFAULTCAPACITY_EMPTY_ELEMENTDATA)
                 //默认容量的处理
                 return Math.max(
               DEFAULT_CAPACITY, minCapacity);
    
          /*
        minCapacity是int类型，有溢出的可能，也就
        是ArrayList最大大小是Integer.MAX_VALUE
          */
            if (minCapacity<0) //overflow
               throw new OutOfMemoryError();
    
            //返回新容量
            return minCapacity;
        }
    
      /*
      MAX_ARRAY_SIZE=Integer.MAX_VALUE-8,
      当扩容后大于MAX_ARRAY_SIZE ，返回 
     hugeCapacity(minCapacity),
      其实就是Integer.MAX_VALUE
        */
        return (newCapacity-MAX_ARRAY_SIZE
             <= 0)? newCapacity
            : hugeCapacity(minCapacity);
    }
    
    private static int hugeCapacity
                    (int minCapacity){
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError();
        return (minCapacity>MAX_ARRAY_SIZE)
            ? Integer.MAX_VALUE
            : MAX_ARRAY_SIZE;
    }
    

**ArrayList的failfast机制**

    
    
    //最后看下ArrayList的failFast机制
    private class Itr implements 
                    Iterator<E>{
        //index of next element to return
        int cursor;      
        // index of last element returned;  
        int lastRet = -1; -1 if no such
        /*
        在迭代之前先保存modCount的值，
        modCount在改变容器元素、容器
        大小时会自增加1
        */
        int expectedModCount=modCount;
    
        // prevent creating a synthetic
        // constructor
        Itr() {}
    
        public boolean hasNext() {
            return cursor != size;
        }
    
        @SuppressWarnings("unchecked")
        public E next() {
           /*
           使用迭代器遍历元素的时候先检查
           modCount的值是否等于预期的值，
           进入该函数
           */
            checkForComodification();
            int i = cursor;
            if (i >= size)
                throw new 
                NoSuchElementException();
            Object[] elementData =
              ArrayList.this.elementData;
            if (i >= elementData.length)
                throw new 
              ConcurrentModificationException();
            cursor = i + 1;
            return (E)elementData[lastRet=i];
        }
    
      /*
        可以发现：在迭代期间如果有线程改变了
        容器，此时会抛出
        “ConcurrentModificationException”
        */
       final void checkForComodification(){
            if (modCount!=expectedModCount)
                throw new 
              ConcurrentModificationException();
        }
    

ArrayList的其他操作，比如：get、remove、indexOf其实就很简单了，都是对Object数组的操作：获取数组某个索引位置的元素，删除数组中某个元素，查找数组中某个元素的位置……所以说理解原理很重要。

上面注释的部分就是ArrayList的考点，主要有：**初始容量、最大容量、使用Object数组保存元素（数组与链表的异同）、扩容机制（1.5倍）、failFast机制等。

## LinkedList源码分析

**成员属性源码分析**

    
    
    public class LinkedList<E>
        extends AbstractSequentialList<E>
        implements List<E>, Deque<E>
        ,Cloneable, java.io.Serializable {
      MAX_ARRAY_SIZE=Integer.MAX_VALUE-8,
        /*
        LinkedList的size是int类型，但是后面
        会看到LinkedList大小实际只受内存大小
        的限制也就是LinkedList的size大小可能
        发生溢出，返回负数
        */
        transient int size = 0;
    
        //LinkedList底层使用双向链表实现，
        //并保留了头尾两个节点的引用
        transient Node<E> first;//头节点
    
        transient Node<E> last;//尾节点
        //省略一部分无关代码
    
        //下面分析LinkedList内部类Node
    

**内部类Node源码分析**

    
    
    private static class Node<E> {
            E item;//元素值
            Node<E> next;//后继节点
    
            //前驱节点,即Node是双向链表
            Node<E> prev;
    
            Node(Node<E> prev, E element
            , Node<E> next) {//Node的构造器
                this.item = element;
                this.next = next;
                this.prev = prev;
            }
        }
    

**构造器源码分析**

    
    
    //LinkedList无参构造器：什么都没做
    public LinkedList() {}
    

**其他核心辅助接口方法源码分析**

    
    
    /*
    LinkedList的大部分接口都是基于
                    这几个接口实现的：
    1.往链表头部插入元素
    2.往链表尾部插入元素
    3.在指定节点的前面插入一个节点
    4.删除链表的头结点
    5.删除除链表的尾节点
    6.删除除链表中的指定节点
    */
    //1.往链表头部插入元素
    private void linkFirst(E e) {
        final Node<E> f = first;
        final Node<E> newNode = 
                new Node<>(null, e, f);
        first = newNode;
        if (f == null)
            last = newNode;
        else
            f.prev = newNode;
        size++;
        modCount++;//failFast机制
    }
    
      //2.往链表尾部插入元素
    void linkLast(E e) {
        final Node<E> l = last;
        final Node<E> newNode = 
            new Node<>(l, e, null);
        last = newNode;
        if (l == null)
            first = newNode;
        else
            l.next = newNode;
        size++;
        modCount++;//failFast机制
    }
    
    //3.在指定节点(succ)的前面插入一个节点
    void linkBefore(E e, Node<E> succ) {
        // assert succ != null;
        final Node<E> pred = succ.prev;
        final Node<E> newNode 
            = new Node<>(pred, e, succ);
        succ.prev = newNode;
        if (pred == null)
            first = newNode;
        else
            pred.next = newNode;
        size++;
        modCount++;//failFast机制
    }
    
    //4.删除链表的头结点
    private E unlinkFirst(Node<E> f){
        //assert f==first && f!=null;
        final E element = f.item;
        final Node<E> next = f.next;
        f.item = null;
        f.next = null; //help GC
        first = next;
        if (next == null)
            last = null;
        else
            next.prev = null;
        size--;
        modCount++;//failFast机制
        return element;
    }
    
    //5.删除除链表的尾节点
    private E unlinkLast(Node<E> l) {
        //assert l==last && l!=null;
        final E element = l.item;
        final Node<E> prev = l.prev;
        l.item = null;
        l.prev = null; // help GC
        last = prev;
        if (prev == null)
            first = null;
        else
            prev.next = null;
        size--;
        modCount++;//failFast机制
        return element;
    }
    
    //6.删除除链表中的指定节点
    E unlink(Node<E> x) {
        // assert x != null;
        final E element = x.item;
        final Node<E> next = x.next;
        final Node<E> prev = x.prev;
    
        if (prev == null) {
            first = next;
        } else {
            prev.next = next;
            x.prev = null;
        }
    
        if (next == null) {
            last = prev;
        } else {
            next.prev = prev;
            x.next = null;
        }
    
        x.item = null;
        size--;
        modCount++;//failFast机制
            return element;
        }
    

**常用API源码分析**

    
    
    //LinkedList常用接口的实现 public E removeFirst() {
        final Node<E> f = first;
        if (f == null)
            throw 
            new NoSuchElementException();
        //调用 4.删除链表的头结点 实现
            return unlinkFirst(f);
      }
    
    public E removeLast() {
        final Node<E> l = last;
        if (l == null)
            throw 
            new NoSuchElementException();
         //调用 5.删除除链表的尾节点 实现
             return unlinkLast(l);
        }
    
       public void addFirst(E e) {
           //调用 1.往链表头部插入元素 实现
           linkFirst(e);
        }
    
       public void addLast(E e) {
           //调用 2.往链表尾部插入元素 实现
           linkLast(e);
    }
    
    public boolean add(E e) {
        //调用 2.往链表尾部插入元素 实现
        linkLast(e);
        return true;
        }
    
    public boolean remove(Object o) {
        if (o == null) {
            for (Node<E> x = first;
             x != null; x = x.next) {
                if (x.item == null) {
             //调用 6.删除除链表中的
             //指定节点 实现
                    unlink(x);
                    return true;
                }
            }
        } else {
            for (Node<E> x = first
            ; x != null; x = x.next) {
                if (o.equals(x.item)) {
                    //调用 6.删除除链表中的
                    //指定节点 实现
                    unlink(x);
                    return true;
                }
            }
        }
        return false;
        }
    
    //省略其他无关函数
    

**failfast机制**

    
    
    //迭代器中的failFast机制 private class ListItr 
    implements ListIterator<E> {
        private Node<E> lastReturned;
        private Node<E> next;
        private int nextIndex;
    
        /*
        在迭代之前先保存modCount的值，
        modCount在改变容器元素、容器大小时
        会自增加1
        */
        private int expectedModCount
                     = modCount;
    
        ListItr(int index) {
            next = (index == size) 
                ? null : node(index);
            nextIndex = index;
        }
    
        public boolean hasNext() {
            return nextIndex < size;
        }
    
        public E next() {
            /*
            使用迭代器遍历元素的时候先检查
            modCount的值是否等于预期的值，
            进入该函数
            */
            checkForComodification();
            if (!hasNext())
                throw 
                new NoSuchElementException();
    
            lastReturned = next;
            next = next.next;
            nextIndex++;
            return lastReturned.item;
        }
    
         /*
        可以发现：在迭代期间如果有线程改变了容器，
        此时会抛出
        “ConcurrentModificationException”
        */
         final void checkForComodification(){
              if (modCount!=expectedModCount)
                  throw new 
               ConcurrentModificationException();
            }
    

LinkedList的实现较为简单： **底层使用双向链表实现、保留了头尾两个指针**
、LinkedList的其他操作基本都是基于上面那六个函数实现的，另外LinkedList也有 **failFast** 机制，这个机制主要在迭代器中使用。

**数组和链表各自的特性**

数组和链表的特性差异，本质是： **连续空间存储和非连续空间存储的差异。** 主要有下面两点：

  1. **ArrayList** ：底层是Object数组实现的：由于数组的地址是连续的，数组支持O(1)随机访问；数组在初始化时需要指定容量；数组不支持动态扩容，像ArrayList、Vector和Stack使用的时候看似不用考虑容量问题（因为可以一直往里面存放数据）；但是它们的底层实际做了扩容；数组扩容代价比较大，需要开辟一个新数组将数据拷贝进去，数组扩容效率低；适合读数据较多的场合。
  2. **LinkedList** ：底层使用一个Node数据结构，有前后两个指针，双向链表实现的。相对数组，链表插入效率较高，只需要更改前后两个指针即可；另外链表不存在扩容问题，因为链表不要求存储空间连续，每次插入数据都只是改变last指针；另外，链表所需要的内存比数组要多，因为他要维护前后两个指针；它适合删除，插入较多的场景LinkedList还实现了Deque接口。

