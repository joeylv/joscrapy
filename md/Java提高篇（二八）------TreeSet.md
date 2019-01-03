与HashSet是基于HashMap实现一样，TreeSet同样是基于TreeMap实现的。在《Java提高篇（二七）-----TreeMap》中LZ详细讲解了TreeMap实现机制，如果客官详情看了这篇博文或者多TreeMap有比较详细的了解，那么TreeSet的实现对您是喝口水那么简单。

## 一、TreeSet定义

我们知道TreeMap是一个有序的二叉树，那么同理TreeSet同样也是一个有序的，它的作用是提供有序的Set集合。通过源码我们知道TreeSet基础AbstractSet，实现NavigableSet、Cloneable、Serializable接口。其中AbstractSet提供
`Set` 接口的骨干实现，从而最大限度地减少了实现此接口所需的工作。NavigableSet是扩展的
`SortedSet`，具有了为给定搜索目标报告最接近匹配项的导航方法，这就意味着它支持一系列的导航方法。比如查找与指定目标最匹配项。Cloneable支持克隆，Serializable支持序列化。

    
    
    public class TreeSet<E> extends AbstractSet<E>
        implements NavigableSet<E>, Cloneable, java.io.Serializable

同时在TreeSet中定义了如下几个变量。

    
    
    private transient NavigableMap<E,Object> m;
            
    //PRESENT会被当做Map的value与key构建成键值对
     private static final Object PRESENT = new Object();

其构造方法：

    
    
    //默认构造方法，根据其元素的自然顺序进行排序
        public TreeSet() {
            this(new TreeMap<E,Object>());
        }
        
        //构造一个包含指定 collection 元素的新 TreeSet，它按照其元素的自然顺序进行排序。
        public TreeSet(Comparator<? super E> comparator) {
                this(new TreeMap<>(comparator));
        }
        
        //构造一个新的空 TreeSet，它根据指定比较器进行排序。
        public TreeSet(Collection<? extends E> c) {
            this();
            addAll(c);
        }
        
        //构造一个与指定有序 set 具有相同映射关系和相同排序的新 TreeSet。
        public TreeSet(SortedSet<E> s) {
            this(s.comparator());
            addAll(s);
        }
        
        TreeSet(NavigableMap<E,Object> m) {
            this.m = m;
        }

## 二、TreeSet主要方法

**1、** add：将指定的元素添加到此 set（如果该元素尚未存在于 set 中）。

    
    
    public boolean add(E e) {
            return m.put(e, PRESENT)==null;
        }

**2、** addAll：将指定 collection 中的所有元素添加到此 set 中。

    
    
    public  boolean addAll(Collection<? extends E> c) {
            // Use linear-time version if applicable
            if (m.size()==0 && c.size() > 0 &&
                c instanceof SortedSet &&
                m instanceof TreeMap) {
                SortedSet<? extends E> set = (SortedSet<? extends E>) c;
                TreeMap<E,Object> map = (TreeMap<E, Object>) m;
                Comparator<? super E> cc = (Comparator<? super E>) set.comparator();
                Comparator<? super E> mc = map.comparator();
                if (cc==mc || (cc != null && cc.equals(mc))) {
                    map.addAllForTreeSet(set, PRESENT);
                    return true;
                }
            }
            return super.addAll(c);
        }

**3、** ceiling：返回此 set 中大于等于给定元素的最小元素；如果不存在这样的元素，则返回 null。

    
    
    public E ceiling(E e) {
            return m.ceilingKey(e);
        }

**4、** clear：移除此 set 中的所有元素。

    
    
    public void clear() {
            m.clear();
        }

5、clone：返回 TreeSet 实例的浅表副本。属于浅拷贝。

    
    
    public Object clone() {
            TreeSet<E> clone = null;
            try {
                clone = (TreeSet<E>) super.clone();
            } catch (CloneNotSupportedException e) {
                throw new InternalError();
            }
    
            clone.m = new TreeMap<>(m);
            return clone;
        }

6、comparator：返回对此 set 中的元素进行排序的比较器；如果此 set
使用其元素的[自然顺序](mk:@MSITStore:G:%5CmyYunFile%5C????????????%5Cjdk6.ZH_cn.chm::/j2se6/api/java/lang/Comparable.html)，则返回
null。

    
    
    public Comparator<? super E> comparator() {
            return m.comparator();
        }

7、contains：如果此 set 包含指定的元素，则返回 true。

    
    
    public boolean contains(Object o) {
            return m.containsKey(o);
        }

8、descendingIterator：返回在此 set 元素上按降序进行迭代的迭代器。

    
    
    public Iterator<E> descendingIterator() {
            return m.descendingKeySet().iterator();
        }

9、descendingSet：返回此 set 中所包含元素的逆序视图。

    
    
    public NavigableSet<E> descendingSet() {
            return new TreeSet<>(m.descendingMap());
        }

10、first：返回此 set 中当前第一个（最低）元素。

    
    
    public E first() {
            return m.firstKey();
        }

11、floor：返回此 set 中小于等于给定元素的最大元素；如果不存在这样的元素，则返回 null。

    
    
    public E floor(E e) {
            return m.floorKey(e);
        }

12、headSet：返回此 set 的部分视图，其元素严格小于 toElement。

    
    
    public SortedSet<E> headSet(E toElement) {
            return headSet(toElement, false);
        }

13、higher：返回此 set 中严格大于给定元素的最小元素；如果不存在这样的元素，则返回 null。

    
    
    public E higher(E e) {
            return m.higherKey(e);
        }

14、isEmpty：如果此 set 不包含任何元素，则返回 true。

    
    
    public boolean isEmpty() {
            return m.isEmpty();
        }

15、iterator：返回在此 set 中的元素上按升序进行迭代的迭代器。

    
    
    public Iterator<E> iterator() {
            return m.navigableKeySet().iterator();
        }

16、last：返回此 set 中当前最后一个（最高）元素。

    
    
    public E last() {
            return m.lastKey();
        }

17、lower：返回此 set 中严格小于给定元素的最大元素；如果不存在这样的元素，则返回 null。

    
    
    public E lower(E e) {
            return m.lowerKey(e);
        }

18、pollFirst：获取并移除第一个（最低）元素；如果此 set 为空，则返回 null。

    
    
    public E pollFirst() {
            Map.Entry<E,?> e = m.pollFirstEntry();
            return (e == null) ? null : e.getKey();
        }

19、pollLast：获取并移除最后一个（最高）元素；如果此 set 为空，则返回 null。

    
    
    public E pollLast() {
            Map.Entry<E,?> e = m.pollLastEntry();
            return (e == null) ? null : e.getKey();
        }

20、remove：将指定的元素从 set 中移除（如果该元素存在于此 set 中）。

    
    
    public boolean remove(Object o) {
            return m.remove(o)==PRESENT;
        }

21、size：返回 set 中的元素数（set 的容量）。

    
    
    public int size() {
            return m.size();
        }

22、subSet：返回此 set 的部分视图

    
    
    /**
         * 返回此 set 的部分视图，其元素范围从 fromElement 到 toElement。
         */
         public NavigableSet<E> subSet(E fromElement, boolean fromInclusive,
                 E toElement,   boolean toInclusive) {
                 return new TreeSet<>(m.subMap(fromElement, fromInclusive,
                      toElement,   toInclusive));
         }
         
         /**
          * 返回此 set 的部分视图，其元素从 fromElement（包括）到 toElement（不包括）。
          */
         public SortedSet<E> subSet(E fromElement, E toElement) {
             return subSet(fromElement, true, toElement, false);
         }

23、tailSet：返回此 set 的部分视图

    
    
    /**
         * 返回此 set 的部分视图，其元素大于（或等于，如果 inclusive 为 true）fromElement。
         */
        public NavigableSet<E> tailSet(E fromElement, boolean inclusive) {
            return new TreeSet<>(m.tailMap(fromElement, inclusive));
        }
        
        /**
         * 返回此 set 的部分视图，其元素大于等于 fromElement。
         */
        public SortedSet<E> tailSet(E fromElement) {
            return tailSet(fromElement, true);
        }

## 三、最后

由于TreeSet是基于TreeMap实现的，所以如果我们对treeMap有了一定的了解，对TreeSet那是小菜一碟，我们从TreeSet中的源码可以看出，其实现过程非常简单，几乎所有的方法实现全部都是基于TreeMap的。

