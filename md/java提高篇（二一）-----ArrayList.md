## 一、ArrayList概述

ArrayList是实现List接口的动态数组，所谓动态就是它的大小是可变的。实现了所有可选列表操作，并允许包括 null 在内的所有元素。除了实现
List 接口外，此类还提供一些方法来操作内部用来存储列表的数组的大小。

每个ArrayList实例都有一个容量，该容量是指用来存储列表元素的数组的大小。默认初始容量为10。随着ArrayList中元素的增加，它的容量也会不断的自动增长。在每次添加新的元素时，ArrayList都会检查是否需要进行扩容操作，扩容操作带来数据向新数组的重新拷贝，所以如果我们知道具体业务数据量，在构造ArrayList时可以给ArrayList指定一个初始容量，这样就会减少扩容时数据的拷贝问题。当然在添加大量元素前，应用程序也可以使用ensureCapacity操作来增加ArrayList实例的容量，这可以减少递增式再分配的数量。

**** **注意，ArrayList实现不是同步的**
。如果多个线程同时访问一个ArrayList实例，而其中至少一个线程从结构上修改了列表，那么它必须保持外部同步。所以为了保证同步，最好的办法是在创建时完成，以防止意外对列表进行不同步的访问：

    
    
            List list = Collections.synchronizedList(new ArrayList(...)); 

## 二、ArrayList源码分析

ArrayList我们使用的实在是太多了，非常熟悉，所以在这里将不介绍它的使用方法。ArrayList是实现List接口的，底层采用数组实现，所以它的操作基本上都是基于对数组的操作。

**2.1、底层使用数组**

    
    
     private transient Object[] elementData;

transient？？为java关键字，为变量修饰符，如果用transient声明一个实例变量，当对象存储时，它的值不需要维持。Java的serialization提供了一种持久化对象实例的机制。当持久化对象时，可能有一个特殊的对象数据成员，我们不想用serialization机制来保存它。为了在一个特定对象的一个域上关闭serialization，可以在这个域前加上关键字transient。当一个对象被序列化的时候，transient型变量的值不包括在序列化的表示中，然而非transient型的变量是被包括进去的。

这里Object[] elementData，就是我们的ArrayList容器，下面介绍的基本操作都是基于该elementData变量来进行操作的。

**2.2、构造函数**

ArrayList提供了三个构造函数：

ArrayList()：默认构造函数，提供初始容量为10的空列表。

ArrayList(int initialCapacity)：构造一个具有指定初始容量的空列表。

ArrayList(Collection <? extends
[E](mk:@MSITStore:G:%5C????????????%5Cjdk6.ZH_cn.chm::/j2se6/api/java/util/ArrayList.html)>
c)：构造一个包含指定 collection 的元素的列表，这些元素是按照该 collection 的迭代器返回它们的顺序排列的。

    
    
    /**
         * 构造一个初始容量为 10 的空列表
         */
        public ArrayList() {
            this(10);
        }
        
        /**
         * 构造一个具有指定初始容量的空列表。
         */
        public ArrayList(int initialCapacity) {
            super();
            if (initialCapacity < 0)
                throw new IllegalArgumentException("Illegal Capacity: "
                        + initialCapacity);
            this.elementData = new Object[initialCapacity];
        }
    
        /**
         *  构造一个包含指定 collection 的元素的列表，这些元素是按照该 collection 的迭代器返回它们的顺序排列的。
         */
        public ArrayList(Collection<? extends E> c) {
            elementData = c.toArray();
            size = elementData.length;
            // c.toArray might (incorrectly) not return Object[] (see 6260652)
            if (elementData.getClass() != Object[].class)
                elementData = Arrays.copyOf(elementData, size, Object[].class);
        }

**2.3、新增**

ArrayList提供了add(E e)、add(int index, E element)、addAll(Collection <? extends E>
c)、addAll(int index, Collection<? extends E> c)、set(int index, E
element)这个五个方法来实现ArrayList增加。

add(E e)：将指定的元素添加到此列表的尾部。

    
    
    public boolean add(E e) {
        ensureCapacity(size + 1);  // Increments modCount!!
        elementData[size++] = e;
        return true;
        }

这里ensureCapacity()方法是对ArrayList集合进行扩容操作，elementData(size++) = e，将列表末尾元素指向e。

add(int index, E element)：将指定的元素插入此列表中的指定位置。

    
    
    public void add(int index, E element) {
            //判断索引位置是否正确
            if (index > size || index < 0)
                throw new IndexOutOfBoundsException(
                "Index: "+index+", Size: "+size);
            //扩容检测
            ensureCapacity(size+1);  
            /*
             * 对源数组进行复制处理（位移），从index + 1到size-index。
             * 主要目的就是空出index位置供数据插入，
             * 即向右移动当前位于该位置的元素以及所有后续元素。 
             */
            System.arraycopy(elementData, index, elementData, index + 1,
                     size - index);
            //在指定位置赋值
            elementData[index] = element;
            size++;
            }

在这个方法中最根本的方法就是System.arraycopy()方法，该方法的根本目的就是将index位置空出来以供新数据插入，这里需要进行数组数据的右移，这是非常麻烦和耗时的，所以如果指定的数据集合需要进行大量插入（中间插入）操作，推荐使用LinkedList。

addAll(Collection<? extends E> c)：按照指定 collection 的迭代器所返回的元素顺序，将该 collection
中的所有元素添加到此列表的尾部。

    
    
    public boolean addAll(Collection<? extends E> c) {
            // 将集合C转换成数组
            Object[] a = c.toArray();
            int numNew = a.length;
            // 扩容处理，大小为size + numNew
            ensureCapacity(size + numNew); // Increments modCount
            System.arraycopy(a, 0, elementData, size, numNew);
            size += numNew;
            return numNew != 0;
        }

这个方法无非就是使用System.arraycopy()方法将C集合(先准换为数组)里面的数据复制到elementData数组中。这里就稍微介绍下System.arraycopy()，因为下面还将大量用到该方法。该方法的原型为：public
static void **arraycopy** (Object src, int srcPos, Object dest, int destPos,
int
length)。它的根本目的就是进行数组元素的复制。即从指定源数组中复制一个数组，复制从指定的位置开始，到目标数组的指定位置结束。将源数组src从srcPos位置开始复制到dest数组中，复制长度为length，数据从dest的destPos位置开始粘贴。

addAll(int index, Collection<? extends E> c)：从指定的位置开始，将指定 collection
中的所有元素插入到此列表中。

    
    
    public boolean addAll(int index, Collection<? extends E> c) {
            //判断位置是否正确
            if (index > size || index < 0)
                throw new IndexOutOfBoundsException("Index: " + index + ", Size: "
                        + size);
            //转换成数组
            Object[] a = c.toArray();
            int numNew = a.length;
            //ArrayList容器扩容处理
            ensureCapacity(size + numNew); // Increments modCount
            //ArrayList容器数组向右移动的位置
            int numMoved = size - index;
            //如果移动位置大于0，则将ArrayList容器的数据向右移动numMoved个位置，确保增加的数据能够增加
            if (numMoved > 0)
                System.arraycopy(elementData, index, elementData, index + numNew,
                        numMoved);
            //添加数组
            System.arraycopy(a, 0, elementData, index, numNew);
            //容器容量变大
            size += numNew;   
            return numNew != 0;
        }

set(int index, E element)：用指定的元素替代此列表中指定位置上的元素。

    
    
    public E set(int index, E element) {
            //检测插入的位置是否越界
            RangeCheck(index);
    
            E oldValue = (E) elementData[index];
            //替代
            elementData[index] = element;
            return oldValue;
        }

**2.4、删除**

ArrayList提供了remove(int index)、remove(Object o)、removeRange(int fromIndex, int
toIndex)、removeAll()四个方法进行元素的删除。

remove(int index)：移除此列表中指定位置上的元素。

    
    
    public E remove(int index) {
            //位置验证
            RangeCheck(index);
    
            modCount++;
            //需要删除的元素
            E oldValue = (E) elementData[index];   
            //向左移的位数
            int numMoved = size - index - 1;
            //若需要移动，则想左移动numMoved位
            if (numMoved > 0)
                System.arraycopy(elementData, index + 1, elementData, index,
                        numMoved);
            //置空最后一个元素
            elementData[--size] = null; // Let gc do its work
    
            return oldValue;
        }

remove(Object o)：移除此列表中首次出现的指定元素（如果存在）。

    
    
    public boolean remove(Object o) {
            //因为ArrayList中允许存在null，所以需要进行null判断
            if (o == null) {
                for (int index = 0; index < size; index++)
                    if (elementData[index] == null) {
                        //移除这个位置的元素
                        fastRemove(index);
                        return true;
                    }
            } else {
                for (int index = 0; index < size; index++)
                    if (o.equals(elementData[index])) {
                        fastRemove(index);
                        return true;
                    }
            }
            return false;
        }

其中fastRemove()方法用于移除指定位置的元素。如下

    
    
    private void fastRemove(int index) {
            modCount++;
            int numMoved = size - index - 1;
            if (numMoved > 0)
                System.arraycopy(elementData, index+1, elementData, index,
                                 numMoved);
            elementData[--size] = null; // Let gc do its work
        }

removeRange(int fromIndex, int toIndex)：移除列表中索引在 `fromIndex`（包括）和
`toIndex`（不包括）之间的所有元素。

    
    
    protected void removeRange(int fromIndex, int toIndex) {
            modCount++;
            int numMoved = size - toIndex;
            System
                    .arraycopy(elementData, toIndex, elementData, fromIndex,
                            numMoved);
    
            // Let gc do its work
            int newSize = size - (toIndex - fromIndex);
            while (size != newSize)
                elementData[--size] = null;
        }

removeAll()：是继承自AbstractCollection的方法，ArrayList本身并没有提供实现。

    
    
    public boolean removeAll(Collection<?> c) {
            boolean modified = false;
            Iterator<?> e = iterator();
            while (e.hasNext()) {
                if (c.contains(e.next())) {
                    e.remove();
                    modified = true;
                }
            }
            return modified;
        }

**2.5、查找**

**** ArrayList提供了get(int
index)用读取ArrayList中的元素。由于ArrayList是动态数组，所以我们完全可以根据下标来获取ArrayList中的元素，而且速度还比较快，故ArrayList长于随机访问。

    
    
     public E get(int index) {
            RangeCheck(index);
    
            return (E) elementData[index];
        }

**2.6、扩容**

在上面的新增方法的源码中我们发现每个方法中都存在这个方法：ensureCapacity()，该方法就是ArrayList的扩容方法。在前面就提过ArrayList每次新增元素时都会需要进行容量检测判断，若新增元素后元素的个数会超过ArrayList的容量，就会进行扩容操作来满足新增元素的需求。所以当我们清楚知道业务数据量或者需要插入大量元素前，我可以使用ensureCapacity来手动增加ArrayList实例的容量，以减少递增式再分配的数量。

    
    
     public void ensureCapacity(int minCapacity) {
            //修改计时器
            modCount++;
            //ArrayList容量大小
            int oldCapacity = elementData.length;
            /*
             * 若当前需要的长度大于当前数组的长度时，进行扩容操作
             */
            if (minCapacity > oldCapacity) {
                Object oldData[] = elementData;
                //计算新的容量大小，为当前容量的1.5倍
                int newCapacity = (oldCapacity * 3) / 2 + 1;
                if (newCapacity < minCapacity)
                    newCapacity = minCapacity;
                //数组拷贝，生成新的数组
                elementData = Arrays.copyOf(elementData, newCapacity);
            }
        }

在这里有一个疑问，为什么每次扩容处理会是1.5倍，而不是2.5、3、4倍呢？通过google查找，发现1.5倍的扩容是最好的倍数。因为一次性扩容太大(例如2.5倍)可能会浪费更多的内存(1.5倍最多浪费33%，而2.5被最多会浪费60%，3.5倍则会浪费71%……)。但是一次性扩容太小，需要多次对数组重新分配内存，对性能消耗比较严重。所以1.5倍刚刚好，既能满足性能需求，也不会造成很大的内存消耗。

处理这个ensureCapacity()这个扩容数组外，ArrayList还给我们提供了将底层数组的容量调整为当前列表保存的实际元素的大小的功能。它可以通过trimToSize()方法来实现。该方法可以最小化ArrayList实例的存储量。

    
    
    public void trimToSize() {
            modCount++;
            int oldCapacity = elementData.length;
            if (size < oldCapacity) {
                elementData = Arrays.copyOf(elementData, size);
            }
        }

**关注我的新站：**[ **CMSBLOGS.com**](http://chenssy.gotoip55.com/)

