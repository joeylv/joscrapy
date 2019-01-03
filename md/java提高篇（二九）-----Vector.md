在[java提高篇（二一）—–ArrayList](http://www.cnblogs.com/chenssy/p/3498468.html)、[java提高篇（二二）—LinkedList](http://www.cnblogs.com/chenssy/p/3514524.html)，详细讲解了ArrayList、linkedList的原理和实现过程，对于List接口这里还介绍一个它的实现类Vector，Vector
类可以实现可增长的对象数组。

## 一、Vector简介

Vector可以实现可增长的对象数组。与数组一样，它包含可以使用整数索引进行访问的组件。不过，Vector的大小是可以增加或者减小的，以便适应创建Vector后进行添加或者删除操作。

Vector实现List接口，继承AbstractList类，所以我们可以将其看做队列，支持相关的添加、删除、修改、遍历等功能。

Vector实现RandmoAccess接口，即提供了随机访问功能，提供提供快速访问功能。在Vector我们可以直接访问元素。

Vector 实现了Cloneable接口，支持clone()方法，可以被克隆。

    
    
    public class Vector<E>
        extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable

Vector提供了四个构造函数：

    
    
    /**
         * 构造一个空向量，使其内部数据数组的大小为 10，其标准容量增量为零。
         */
         public Vector() {
                this(10);
         }
        
        /**
         * 构造一个包含指定 collection 中的元素的向量，这些元素按其 collection 的迭代器返回元素的顺序排列。
         */
        public Vector(Collection<? extends E> c) {
            elementData = c.toArray();
            elementCount = elementData.length;
            // c.toArray might (incorrectly) not return Object[] (see 6260652)
            if (elementData.getClass() != Object[].class)
                elementData = Arrays.copyOf(elementData, elementCount,
                        Object[].class);
        }
        
        /**
         * 使用指定的初始容量和等于零的容量增量构造一个空向量。
         */
        public Vector(int initialCapacity) {
            this(initialCapacity, 0);
        }
        
        /**
         *  使用指定的初始容量和容量增量构造一个空的向量。
         */
        public Vector(int initialCapacity, int capacityIncrement) {
            super();
            if (initialCapacity < 0)
                throw new IllegalArgumentException("Illegal Capacity: "+
                                                   initialCapacity);
            this.elementData = new Object[initialCapacity];
            this.capacityIncrement = capacityIncrement;
        }

在成员变量方面，Vector提供了elementData , elementCount， capacityIncrement三个成员变量。其中

elementData
："Object[]类型的数组"，它保存了Vector中的元素。按照Vector的设计elementData为一个动态数组，可以随着元素的增加而动态的增长，其具体的增加方式后面提到（ensureCapacity方法）。如果在初始化Vector时没有指定容器大小，则使用默认大小为10.

elementCount：`Vector` 对象中的有效组件数。

capacityIncrement：向量的大小大于其容量时，容量自动增加的量。如果在创建Vector时，指定了capacityIncrement的大小；则，每次当Vector中动态数组容量增加时>，增加的大小都是capacityIncrement。如果容量的增量小于等于零，则每次需要增大容量时，向量的容量将增大一倍。

同时Vector是线程安全的！

## 二、源码解析

对于源码的解析，LZ在这里只就增加（add）删除（remove）两个方法进行讲解。

### 2.1增加：add(E e)

add(E e)：将指定元素添加到此向量的末尾。

    
    
    public synchronized boolean add(E e) {
            modCount++;     
            ensureCapacityHelper(elementCount + 1);    //确认容器大小，如果操作容量则扩容操作
            elementData[elementCount++] = e;   //将e元素添加至末尾
            return true;
        }

这个方法相对而言比较简单，具体过程就是先确认容器的大小，看是否需要进行扩容操作，然后将E元素添加到此向量的末尾。

    
    
    private void ensureCapacityHelper(int minCapacity) {
            //如果
            if (minCapacity - elementData.length > 0)
                grow(minCapacity);
        }
        
        /**
         * 进行扩容操作
         * 如果此向量的当前容量小于minCapacity，则通过将其内部数组替换为一个较大的数组俩增加其容量。
         * 新数据数组的大小姜维原来的大小 + capacityIncrement，
         * 除非 capacityIncrement 的值小于等于零，在后一种情况下，新的容量将为原来容量的两倍，不过，如果此大小仍然小于 minCapacity，则新容量将为 minCapacity。
         */
        private void grow(int minCapacity) {
            int oldCapacity = elementData.length;     //当前容器大小
            /*
             * 新容器大小
             * 若容量增量系数(capacityIncrement) > 0，则将容器大小增加到capacityIncrement
             * 否则将容量增加一倍
             */
            int newCapacity = oldCapacity + ((capacityIncrement > 0) ?
                                             capacityIncrement : oldCapacity);
            
            if (newCapacity - minCapacity < 0)
                newCapacity = minCapacity;
            
            if (newCapacity - MAX_ARRAY_SIZE > 0)
                newCapacity = hugeCapacity(minCapacity);
            
            elementData = Arrays.copyOf(elementData, newCapacity);
        }
        
        /**
         * 判断是否超出最大范围
         * MAX_ARRAY_SIZE：private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
         */
        private static int hugeCapacity(int minCapacity) {
            if (minCapacity < 0)
                throw new OutOfMemoryError();
            return (minCapacity > MAX_ARRAY_SIZE) ? Integer.MAX_VALUE : MAX_ARRAY_SIZE;
        }

对于Vector整个的扩容过程，就是根据capacityIncrement确认扩容大小的，若capacityIncrement <= 0
则扩大一倍，否则扩大至capacityIncrement 。当然这个容量的最大范围为Integer.MAX_VALUE即，2^32 -
1，所以Vector并不是可以无限扩充的。

### 2.2、remove(Object o)

    
    
    /**
         * 从Vector容器中移除指定元素E
         */
        public boolean remove(Object o) {
            return removeElement(o);
        }
    
        public synchronized boolean removeElement(Object obj) {
            modCount++;
            int i = indexOf(obj);   //计算obj在Vector容器中位置
            if (i >= 0) {
                removeElementAt(i);   //移除
                return true;
            }
            return false;
        }
        
        public synchronized void removeElementAt(int index) {
            modCount++;     //修改次数+1
            if (index >= elementCount) {   //删除位置大于容器有效大小
                throw new ArrayIndexOutOfBoundsException(index + " >= " + elementCount);
            }
            else if (index < 0) {    //位置小于 < 0
                throw new ArrayIndexOutOfBoundsException(index);
            }
            int j = elementCount - index - 1;
            if (j > 0) {   
                //从指定源数组中复制一个数组，复制从指定的位置开始，到目标数组的指定位置结束。
                //也就是数组元素从j位置往前移
                System.arraycopy(elementData, index + 1, elementData, index, j);
            }
            elementCount--;   //容器中有效组件个数 - 1
            elementData[elementCount] = null;    //将向量的末尾位置设置为null
        }

因为Vector底层是使用数组实现的，所以它的操作都是对数组进行操作，只不过其是可以随着元素的增加而动态的改变容量大小，其实现方法是是使用Arrays.copyOf方法将旧数据拷贝到一个新的大容量数组中。Vector的整个内部实现都比较简单，这里就不在重述了。

## 三、Vector遍历

Vector支持4种遍历方式。

### 3.1、 **随机访问**

因为Vector实现了RandmoAccess接口，可以通过下标来进行随机访问。

    
    
    for(int i = 0 ; i < vec.size() ; i++){
            value = vec.get(i);
        }

### 3.2、迭代器

    
    
    Iterator it = vec.iterator();
        while(it.hasNext()){
            value = it.next();
            //do something
        }

### 3.2、for循环

    
    
    for(Integer value:vec){
            //do something
        }

### 3.4、 **Enumeration循环**

    
    
    Vector vec =  new Vector<>();
        Enumeration enu = vec.elements();
        while (enu.hasMoreElements()) {
            value = (Integer)enu.nextElement();
        }

