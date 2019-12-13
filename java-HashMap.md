1\. Java7中的HashMap（key，value均可以为空）：

大方向上HashMap是一个数组，每个数组元素是一个单向链表。

![Image_Here](https://img2018.cnblogs.com/blog/1702473/201906/1702473-20190627205131223-287617809.png)

上图中每个绿色的实体是嵌套类Entry的实例，Entry包含4个属性：key，value，hash，和单链表的next。

capacity：数组的容量，始终保持在2^n，每次扩容后大小为扩容前的2倍。

loadfactor：扩容因子，始终保持在0.75。

threshold：扩容的阈值，大小为：capacity*loadfactor。



1.1put方法的过程：

总结：

当第一次插入时需要初始化数组的大小（threshold）；

判断如果key为空就将这个Entry放入到table[ 0 ]中；

否则计算key的hash值，遍历单链表，若该位置已有元素，就进行覆盖，并返回旧值；

若不存在重复的值，就将该Entry放入到链表中。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V put(K key, V value) {
     2     // 当插入第一个元素的时候，需要先初始化数组大小
     3     if (table == EMPTY_TABLE) {
     4         inflateTable(threshold);
     5     }
     6     // 如果 key 为 null，感兴趣的可以往里看，最终会将这个 entry 放到 table[0] 中
     7     if (key == null)
     8         return putForNullKey(value);
     9     // 1. 求 key 的 hash 值
    10     int hash = hash(key);
    11     // 2. 找到对应的数组下标
    12     int i = indexFor(hash, table.length);
    13     // 3. 遍历一下对应下标处的链表，看是否有重复的 key 已经存在，
    14     //    如果有，直接覆盖，put 方法返回旧值就结束了
    15     for (Entry<K,V> e = table[i]; e != null; e = e.next) {
    16         Object k;
    17         if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
    18             V oldValue = e.value;
    19             e.value = value;
    20             e.recordAccess(this);
    21             return oldValue;
    22         }
    23     }
    24 
    25     modCount++;
    26     // 4. 不存在重复的 key，将此 entry 添加到链表中，细节后面说
    27     addEntry(hash, key, value, i);
    28     return null;
    29 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

1.2数组（大小）的初始化：

当第一个数组元素放入HashMap时，就进行一次数组的初始化，就是先计算数组的大小，再计算阈值（threshold），并始终将数组内元素的数量保持在2^n个。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 private void inflateTable(int toSize) {
     2     // 保证数组大小一定是 2 的 n 次方。
     3     // 比如这样初始化：new HashMap(20)，那么处理成初始数组大小是 32
     4     int capacity = roundUpToPowerOf2(toSize);
     5     // 计算扩容阈值：capacity * loadFactor
     6     threshold = (int) Math.min(capacity * loadFactor, MAXIMUM_CAPACITY + 1);
     7     // 算是初始化数组吧
     8     table = new Entry[capacity];
     9     initHashSeedAsNeeded(capacity); //ignore
    10 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

1.3计算数组的位置：

根据key的Hash值，来对数组长度进行取模。eg：当数组长度为32时，可以取key的hash值的后5位，来进行计算相应数组中位置。

1.4添加结点到链表中：

找到数组下标后，进行key判重，若没有重复，就将该元素放到链表的表头位置。

以下方法首先判断是否需要扩容，如果扩容后，就将元素放到相应数组位置上链表的表头处。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 void addEntry(int hash, K key, V value, int bucketIndex) {
     2     // 如果当前 HashMap 大小已经达到了阈值，并且新值要插入的数组位置已经有元素了，那么要扩容
     3     if ((size >= threshold) && (null != table[bucketIndex])) {
     4         // 扩容，后面会介绍一下
     5         resize(2 * table.length);
     6         // 扩容以后，重新计算 hash 值
     7         hash = (null != key) ? hash(key) : 0;
     8         // 重新计算扩容后的新的下标
     9         bucketIndex = indexFor(hash, table.length);
    10     }
    11     // 往下看
    12     createEntry(hash, key, value, bucketIndex);
    13 }
    14 // 这个很简单，其实就是将新值放到链表的表头，然后 size++
    15 void createEntry(int hash, K key, V value, int bucketIndex) {
    16     Entry<K,V> e = table[bucketIndex];
    17     table[bucketIndex] = new Entry<>(hash, key, value, e);
    18     size++;
    19 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

1.5数组的扩容：

扩容就是将小数组扩大成大数组再将元素转移到大数组中。双倍扩容：比如原数组（每个数组中放的其实是一个链表）中old [ i]的元素，会放到新数组的new [
i] ,和new [ i+oldlength]的位置上。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 void resize(int newCapacity) {
     2     Entry[] oldTable = table;
     3     int oldCapacity = oldTable.length;
     4     if (oldCapacity == MAXIMUM_CAPACITY) {
     5         threshold = Integer.MAX_VALUE;
     6         return;
     7     }
     8     // 新的数组
     9     Entry[] newTable = new Entry[newCapacity];
    10     // 将原来数组中的值迁移到新的更大的数组中
    11     transfer(newTable, initHashSeedAsNeeded(newCapacity));
    12     table = newTable;
    13     threshold = (int)Math.min(newCapacity * loadFactor, MAXIMUM_CAPACITY + 1);
    14 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

1.6 get过程的分析:

 首先根据key计算hash值；

找到相应的数组下标 hash&（length-1）；

遍历数组该位置的链表，直到找到相等（==或者equals）的key。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
    1 public V get(Object key) {
    2     // 之前说过，key 为 null 的话，会被放到 table[0]，所以只要遍历下 table[0] 处的链表就可以了
    3     if (key == null)
    4         return getForNullKey();
    5     // 
    6     Entry<K,V> entry = getEntry(key);
    7 
    8     return null == entry ? null : entry.getValue();
    9 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

getEntry（key）：  

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
    final Entry<K,V> getEntry(Object key) {
        if (size == 0) {
            //如果数组为空返回null
            return null;
        }
         //根据key计算hash值，通过hash值来判断数组中的下标位置
        int hash = (key == null) ? 0 : hash(key);
        //确定数组下标后，遍历该条链表直到找到（== / equals）为止
        for (Entry<K,V> e = table[indexFor(hash, table.length)];
             e != null;
             e = e.next) {
            Object k;
            if (e.hash == hash &&
                ((k = e.key) == key || (key != null && key.equals(k))))
                return e;
        }
        return null;
    }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

2.Java7的concurrentHashMap（value不能为空）：

concurrentHashMap支持并发操作，所以比HashMap复杂一点。concurrentHashMap采用分段锁机制实现线程的同步，concurrentHasMap是由一个个个段组成。

如下图所示：一个concurrentHashMap是由segment数组构成的，segment继承了ReentrantLock来实现线程安全，所以只要保证了每个segment的安全性就实现了concurrentHashMap的线程安全。

![Image_Here](https://img2018.cnblogs.com/blog/1702473/201906/1702473-20190628090220676-850761388.png)



 2.1初始化：

initialCapacity：初始容量，是ConcurrentHashMap的（"HashMap的数量"），会平均分给segment；

loadfactor：加载因子，ConcurrentHashMap不可扩容，所以加载因子是给每个segment用的；

concurrenceLevel：可以理解为：并发级别，并发数，segment数，默认值是16，表示一个concurrentHashMap有16个segment，即就是可以允许16个线程来同时写，concurrenceLevel在初始化时可以指定大小，一旦初始化后不可扩容。（每个segment结构上很像HashMap）；



初始化完成后（调用new ConcurrentHashMap）：

segment数组的默认打小为16；

segment [ i ]的大小为2，加载因子是0.75，所以阈值为1.5，也就是说，当插入第一个元素时，不会扩容，第二个元素时segment[ i ]
会扩容;

并且初始了segment[ 0 ]，其他的位置还是null;



[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public ConcurrentHashMap(int initialCapacity,
     2                          float loadFactor, int concurrencyLevel) {
     3     if (!(loadFactor > 0) || initialCapacity < 0 || concurrencyLevel <= 0)
     4         throw new IllegalArgumentException();
     5     if (concurrencyLevel > MAX_SEGMENTS)
     6         concurrencyLevel = MAX_SEGMENTS;
     7     // Find power-of-two sizes best matching arguments
     8     int sshift = 0;
     9     int ssize = 1;
    10     // 计算并行级别 ssize，因为要保持并行级别是 2 的 n 次方
    11     while (ssize < concurrencyLevel) {
    12         ++sshift;
    13         ssize <<= 1;
    14     }
    15     // 我们这里先不要那么烧脑，用默认值，concurrencyLevel 为 16，sshift 为 4
    16     // 那么计算出 segmentShift 为 28，segmentMask 为 15，后面会用到这两个值
    17     this.segmentShift = 32 - sshift;
    18     this.segmentMask = ssize - 1;
    19 
    20     if (initialCapacity > MAXIMUM_CAPACITY)
    21         initialCapacity = MAXIMUM_CAPACITY;
    22 
    23     // initialCapacity 是设置整个 map 初始的大小，
    24     // 这里根据 initialCapacity 计算 Segment 数组中每个位置可以分到的大小
    25     // 如 initialCapacity 为 64，那么每个 Segment 或称之为"槽"可以分到 4 个
    26     int c = initialCapacity / ssize;
    27     if (c * ssize < initialCapacity)
    28         ++c;
    29     // 默认 MIN_SEGMENT_TABLE_CAPACITY 是 2，这个值也是有讲究的，因为这样的话，对于具体的槽上，
    30     // 插入一个元素不至于扩容，插入第二个的时候才会扩容
    31     int cap = MIN_SEGMENT_TABLE_CAPACITY; 
    32     while (cap < c)
    33         cap <<= 1;
    34 
    35     // 创建 Segment 数组，
    36     // 并创建数组的第一个元素 segment[0]
    37     Segment<K,V> s0 =
    38         new Segment<K,V>(loadFactor, (int)(cap * loadFactor),
    39                          (HashEntry<K,V>[])new HashEntry[cap]);
    40     Segment<K,V>[] ss = (Segment<K,V>[])new Segment[ssize];
    41     // 往数组写入 segment[0]
    42     UNSAFE.putOrderedObject(ss, SBASE, s0); // ordered write of segments[0]
    43     this.segments = ss;
    44 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

2.2put的过程分析：

主流程：

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
    public V put(K key, V value) {
        Segment<K,V> s;
        if (value == null)
            throw new NullPointerException();
        // 1. 计算 key 的 hash 值
        int hash = hash(key);
        // 2. 根据 hash 值找到 Segment 数组中的位置 j
        //    hash 是 32 位，无符号右移 segmentShift(28) 位，剩下高 4 位，
        //    然后和 segmentMask(15) 做一次与操作，也就是说 j 是 hash 值的高 4 位，也就是槽的数组下标
        int j = (hash >>> segmentShift) & segmentMask;
        // 刚刚说了，初始化的时候初始化了 segment[0]，但是其他位置还是 null，
        // ensureSegment(j) 对 segment[j] 进行初始化
        if ((s = (Segment<K,V>)UNSAFE.getObject          // nonvolatile; recheck
             (segments, (j << SSHIFT) + SBASE)) == null) //  in ensureSegment
            s = ensureSegment(j);
        // 3. 插入新值到 槽 s 中
        return s.put(key, hash, value, false);
    }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")



根据key来计算hash的值，对应到segment数组的位置，再对segment[ i ]内部进行put操作，segment[ i
]的内部是一个数组+链表的形式。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 final V put(K key, int hash, V value, boolean onlyIfAbsent) {
     2     // 在往该 segment 写入前，需要先获取该 segment 的独占锁
     3     //    先看主流程，后面还会具体介绍这部分内容
     4     HashEntry<K,V> node = tryLock() ? null :
     5         scanAndLockForPut(key, hash, value);
     6     V oldValue;
     7     try {
     8         // 这个是 segment 内部的数组
     9         HashEntry<K,V>[] tab = table;
    10         // 再利用 hash 值，求应该放置的数组下标
    11         int index = (tab.length - 1) & hash;
    12         // first 是数组该位置处的链表的表头
    13         HashEntry<K,V> first = entryAt(tab, index);
    14 
    15         // 下面这串 for 循环虽然很长，不过也很好理解，想想该位置没有任何元素和已经存在一个链表这两种情况
    16         for (HashEntry<K,V> e = first;;) {
    17             if (e != null) {
    18                 K k;
    19                 if ((k = e.key) == key ||
    20                     (e.hash == hash && key.equals(k))) {
    21                     oldValue = e.value;
    22                     if (!onlyIfAbsent) {
    23                         // 覆盖旧值
    24                         e.value = value;
    25                         ++modCount;
    26                     }
    27                     break;
    28                 }
    29                 // 继续顺着链表走
    30                 e = e.next;
    31             }
    32             else {
    33                 // node 到底是不是 null，这个要看获取锁的过程，不过和这里都没有关系。
    34                 // 如果不为 null，那就直接将它设置为链表表头；如果是null，初始化并设置为链表表头。
    35                 if (node != null)
    36                     node.setNext(first);
    37                 else
    38                     node = new HashEntry<K,V>(hash, key, value, first);
    39 
    40                 int c = count + 1;
    41                 // 如果超过了该 segment 的阈值，这个 segment 需要扩容
    42                 if (c > threshold && tab.length < MAXIMUM_CAPACITY)
    43                     rehash(node); // 扩容后面也会具体分析
    44                 else
    45                     // 没有达到阈值，将 node 放到数组 tab 的 index 位置，
    46                     // 其实就是将新的节点设置成原链表的表头
    47                     setEntryAt(tab, index, node);
    48                 ++modCount;
    49                 count = c;
    50                 oldValue = null;
    51                 break;
    52             }
    53         }
    54     } finally {
    55         // 解锁
    56         unlock();
    57     }
    58     return oldValue;
    59 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

put操作中的关键几步：

初始化段 （ensuresegment）：

ConcurrentHashMap初始化时只初始化了第一个segment[ 0 ]，其他的segment[ j
]，在放第一个元素时进行初始化；当有多个线程进来初始化同一个segment[ i
]时，只会有一个初始化成功（对于并发操作采用CAS算法进行控制该初始化操作）。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 private Segment<K,V> ensureSegment(int k) {
     2     final Segment<K,V>[] ss = this.segments;
     3     long u = (k << SSHIFT) + SBASE; // raw offset
     4     Segment<K,V> seg;
     5     if ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u)) == null) {
     6         // 这里看到为什么之前要初始化 segment[0] 了，
     7         // 使用当前 segment[0] 处的数组长度和负载因子来初始化 segment[k]
     8         // 为什么要用“当前”，因为 segment[0] 可能早就扩容过了
     9         Segment<K,V> proto = ss[0];
    10         int cap = proto.table.length;
    11         float lf = proto.loadFactor;
    12         int threshold = (int)(cap * lf);
    13 
    14         // 初始化 segment[k] 内部的数组
    15         HashEntry<K,V>[] tab = (HashEntry<K,V>[])new HashEntry[cap];
    16         if ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u))
    17             == null) { // 再次检查一遍该槽是否被其他线程初始化了。
    18 
    19             Segment<K,V> s = new Segment<K,V>(lf, threshold, tab);
    20             // 使用 while 循环，内部用 CAS，当前线程成功设值或其他线程成功设值后，退出
    21             while ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u))
    22                    == null) {
    23                 if (UNSAFE.compareAndSwapObject(ss, u, null, seg = s))
    24                     break;
    25             }
    26         }
    27     }
    28     return seg;
    29 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

获取写入锁（scanAndlockForPut）：

在每次写入到segment前会调用：node = tyrLock（）？null
：scanAndLockForput（key，value，hash），即首先会进行tryLock（）来获取segment的独占锁，若获取失败就调用scanAndLockforput（key，value，hash）来获取锁。

scanAndLockForPut（key，value，hash）实现控制加锁：

此方法有两个出口：

一个是tryLock（）成功了退出循环，否则当循环超过一定次数，就会调用lock（）--->进入到阻塞等待，直到tryLock（）成功！

该方法主要是获取segment的独占锁。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 private HashEntry<K,V> scanAndLockForPut(K key, int hash, V value) {
     2     HashEntry<K,V> first = entryForHash(this, hash);
     3     HashEntry<K,V> e = first;
     4     HashEntry<K,V> node = null;
     5     int retries = -1; // negative while locating node
     6 
     7     // 循环获取锁
     8     while (!tryLock()) {
     9         HashEntry<K,V> f; // to recheck first below
    10         if (retries < 0) {
    11             if (e == null) {
    12                 if (node == null) // speculatively create node
    13                     // 进到这里说明数组该位置的链表是空的，没有任何元素
    14                     // 当然，进到这里的另一个原因是 tryLock() 失败，所以该槽存在并发，不一定是该位置
    15                     node = new HashEntry<K,V>(hash, key, value, null);
    16                 retries = 0;
    17             }
    18             else if (key.equals(e.key))
    19                 retries = 0;
    20             else
    21                 // 顺着链表往下走
    22                 e = e.next;
    23         }
    24         // 重试次数如果超过 MAX_SCAN_RETRIES（单核1多核64），那么不抢了，进入到阻塞队列等待锁
    25         //    lock() 是阻塞方法，直到获取锁后返回
    26         else if (++retries > MAX_SCAN_RETRIES) {
    27             lock();
    28             break;
    29         }
    30         else if ((retries & 1) == 0 &&
    31                  // 这个时候是有大问题了，那就是有新的元素进到了链表，成为了新的表头
    32                  //     所以这边的策略是，相当于重新走一遍这个 scanAndLockForPut 方法
    33                  (f = entryForHash(this, hash)) != first) {
    34             e = first = f; // re-traverse if entry changed
    35             retries = -1;
    36         }
    37     }
    38     return node;
    39 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

扩容：rehash

需要注意：segment数组不会扩容，只是对segment数组某一位置上的内部数组（HashEntry <key，value> [
]）进行扩容操作，扩容后的容量为原容量的2倍。在put前会判断该元素的插入会导致数组元素超过阈值？ 如果是，就先扩容(2倍大小)再插入。

以下的方法不需要考虑并发，因为此时还持有segment的独占锁。

（也是会将old[ i ]位置上的元素放到new[ i ]和new[ i+old.length]）

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 // 方法参数上的 node 是这次扩容后，需要添加到新的数组中的数据。
     2 private void rehash(HashEntry<K,V> node) {
     3     HashEntry<K,V>[] oldTable = table;
     4     int oldCapacity = oldTable.length;
     5     // 2 倍
     6     int newCapacity = oldCapacity << 1;
     7     threshold = (int)(newCapacity * loadFactor);
     8     // 创建新数组
     9     HashEntry<K,V>[] newTable =
    10         (HashEntry<K,V>[]) new HashEntry[newCapacity];
    11     // 新的掩码，如从 16 扩容到 32，那么 sizeMask 为 31，对应二进制 ‘000...00011111’
    12     int sizeMask = newCapacity - 1;
    13 
    14     // 遍历原数组，老套路，将原数组位置 i 处的链表拆分到 新数组位置 i 和 i+oldCap 两个位置
    15     for (int i = 0; i < oldCapacity ; i++) {
    16         // e 是链表的第一个元素
    17         HashEntry<K,V> e = oldTable[i];
    18         if (e != null) {
    19             HashEntry<K,V> next = e.next;
    20             // 计算应该放置在新数组中的位置，
    21             // 假设原数组长度为 16，e 在 oldTable[3] 处，那么 idx 只可能是 3 或者是 3 + 16 = 19
    22             int idx = e.hash & sizeMask;
    23             if (next == null)   // 该位置处只有一个元素，那比较好办
    24                 newTable[idx] = e;
    25             else { // Reuse consecutive sequence at same slot
    26                 // e 是链表表头
    27                 HashEntry<K,V> lastRun = e;
    28                 // idx 是当前链表的头结点 e 的新位置
    29                 int lastIdx = idx;
    30 
    31                 // 下面这个 for 循环会找到一个 lastRun 节点，这个节点之后的所有元素是将要放到一起的
    32                 for (HashEntry<K,V> last = next;
    33                      last != null;
    34                      last = last.next) {
    35                     int k = last.hash & sizeMask;
    36                     if (k != lastIdx) {
    37                         lastIdx = k;
    38                         lastRun = last;
    39                     }
    40                 }
    41                 // 将 lastRun 及其之后的所有节点组成的这个链表放到 lastIdx 这个位置
    42                 newTable[lastIdx] = lastRun;
    43                 // 下面的操作是处理 lastRun 之前的节点，
    44                 //    这些节点可能分配在另一个链表中，也可能分配到上面的那个链表中
    45                 for (HashEntry<K,V> p = e; p != lastRun; p = p.next) {
    46                     V v = p.value;
    47                     int h = p.hash;
    48                     int k = h & sizeMask;
    49                     HashEntry<K,V> n = newTable[k];
    50                     newTable[k] = new HashEntry<K,V>(h, p.key, v, n);
    51                 }
    52             }
    53         }
    54     }
    55     // 将新来的 node 放到新数组中刚刚的 两个链表之一 的 头部
    56     int nodeIndex = node.hash & sizeMask; // add the new node
    57     node.setNext(newTable[nodeIndex]);
    58     newTable[nodeIndex] = node;
    59     table = newTable;
    60 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

2.3get的过程分析：

根据key计算Hash值；

依据Hash值定位到segment[ i ];

依据Hash值定位到segment[ i ]的内部数组（HashEntry<k,v>[ ]）中的某一位置处;

遍历该数组处的链表。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V get(Object key) {
     2     Segment<K,V> s; // manually integrate access methods to reduce overhead
     3     HashEntry<K,V>[] tab;
     4     // 1. hash 值
     5     int h = hash(key);
     6     long u = (((h >>> segmentShift) & segmentMask) << SSHIFT) + SBASE;
     7     // 2. 根据 hash 找到对应的 segment
     8     if ((s = (Segment<K,V>)UNSAFE.getObjectVolatile(segments, u)) != null &&
     9         (tab = s.table) != null) {
    10         // 3. 找到segment 内部数组相应位置的链表，遍历
    11         for (HashEntry<K,V> e = (HashEntry<K,V>) UNSAFE.getObjectVolatile
    12                  (tab, ((long)(((tab.length - 1) & h)) << TSHIFT) + TBASE);
    13              e != null; e = e.next) {
    14             K k;
    15             if ((k = e.key) == key || (e.hash == h && key.equals(k)))
    16                 return e.value;
    17         }
    18     }
    19     return null;
    20 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

2.x并发问题的分析：

get操作是没有进行加锁的，添加元素put和删除元素remove都需要获取segment的独占锁，

这里需要考虑的是在get的过程中遇到put和remove时：

put操作的线程安全性：

初始化段：segment的初始化采用了CAS算法来实现并发控制；

添加结点到链表操作是添加到链表表头的；

 3.Java8的HashMap：

Java8对HashMap做了一些修改，最大的不同就是使用了红黑树，所以是由（数组，链表，红黑树）组成的。

在Java7中，当在链表中查找目标元素时，时间复杂度是由链表长度决定的，为O (n)，为了减少这部分的开销，

zaiJava8中，当链表长度达到8时，就将链表转化成红黑树的结构，可以降低时间复杂度为O(logN)。

![Image_Here](https://img2018.cnblogs.com/blog/1702473/201906/1702473-20190628103609828-1939344377.png)

在Java7中使用Entry来存储HashMap的元素，Java8中采用Node，不过Entry和Node都包含了key，value，hash，next这几个属性，Node是适用于链表的，TreeNode是红黑树。

所以我们可以根据Node和TreeNode来判断是链表还是红黑树。

3.1put过程分析：

第一次进行put操作时，会调用resize（），类似于Java7的初始化数组的大小，即从null初始化到16或者指定的大小；

根据key的Hash值来定位到数组的某一位置Node[ i ] ，

若数组该位置没有元素时就初始化Node，将Node放到链表头部（通过key计算的hash值相同时会将value放到数组的同一位置处，形成链表）；

若数组的该位置已有元素就比较key的equals()，若equals为true，则进行覆盖，否则就将该Node放到链表的后面，若是树结构，就调用树的put；

当插入的元素是链表的第八个元素时，就将链表转换成红黑树。



与Java7的不同：

在扩容时：先插入，再扩容；

当链表长度达到8时，就转为红黑树。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V put(K key, V value) {
     2     return putVal(hash(key), key, value, false, true);
     3 }
     4 
     5 // 第三个参数 onlyIfAbsent 如果是 true，那么只有在不存在该 key 时才会进行 put 操作
     6 // 第四个参数 evict 我们这里不关心
     7 final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
     8                boolean evict) {
     9     Node<K,V>[] tab; Node<K,V> p; int n, i;
    10     // 第一次 put 值的时候，会触发下面的 resize()，类似 java7 的第一次 put 也要初始化数组长度
    11     // 第一次 resize 和后续的扩容有些不一样，因为这次是数组从 null 初始化到默认的 16 或自定义的初始容量
    12     if ((tab = table) == null || (n = tab.length) == 0)
    13         n = (tab = resize()).length;
    14     // 找到具体的数组下标，如果此位置没有值，那么直接初始化一下 Node 并放置在这个位置就可以了
    15     if ((p = tab[i = (n - 1) & hash]) == null)
    16         tab[i] = newNode(hash, key, value, null);
    17 
    18     else {// 数组该位置有数据
    19         Node<K,V> e; K k;
    20         // 首先，判断该位置的第一个数据和我们要插入的数据，key 是不是"相等"，如果是，取出这个节点
    21         if (p.hash == hash &&
    22             ((k = p.key) == key || (key != null && key.equals(k))))
    23             e = p;
    24         // 如果该节点是代表红黑树的节点，调用红黑树的插值方法，本文不展开说红黑树
    25         else if (p instanceof TreeNode)
    26             e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
    27         else {
    28             // 到这里，说明数组该位置上是一个链表
    29             for (int binCount = 0; ; ++binCount) {
    30                 // 插入到链表的最后面(Java7 是插入到链表的最前面)
    31                 if ((e = p.next) == null) {
    32                     p.next = newNode(hash, key, value, null);
    33                     // TREEIFY_THRESHOLD 为 8，所以，如果新插入的值是链表中的第 8 个
    34                     // 会触发下面的 treeifyBin，也就是将链表转换为红黑树
    35                     if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
    36                         treeifyBin(tab, hash);
    37                     break;
    38                 }
    39                 // 如果在该链表中找到了"相等"的 key(== 或 equals)
    40                 if (e.hash == hash &&
    41                     ((k = e.key) == key || (key != null && key.equals(k))))
    42                     // 此时 break，那么 e 为链表中[与要插入的新值的 key "相等"]的 node
    43                     break;
    44                 p = e;
    45             }
    46         }
    47         // e!=null 说明存在旧值的key与要插入的key"相等"
    48         // 对于我们分析的put操作，下面这个 if 其实就是进行 "值覆盖"，然后返回旧值
    49         if (e != null) {
    50             V oldValue = e.value;
    51             if (!onlyIfAbsent || oldValue == null)
    52                 e.value = value;
    53             afterNodeAccess(e);
    54             return oldValue;
    55         }
    56     }
    57     ++modCount;
    58     // 如果 HashMap 由于新插入这个值导致 size 已经超过了阈值，需要进行扩容
    59     if (++size > threshold)
    60         resize();
    61     afterNodeInsertion(evict);
    62     return null;
    63 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

3.2数组扩容：

resize（）用来进行数组的初始化，或者扩容，每次扩容后大小为原来的2倍，并进行数据的转移。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 final Node<K,V>[] resize() {
     2     Node<K,V>[] oldTab = table;
     3     int oldCap = (oldTab == null) ? 0 : oldTab.length;
     4     int oldThr = threshold;
     5     int newCap, newThr = 0;
     6     if (oldCap > 0) { // 对应数组扩容
     7         if (oldCap >= MAXIMUM_CAPACITY) {
     8             threshold = Integer.MAX_VALUE;
     9             return oldTab;
    10         }
    11         // 将数组大小扩大一倍
    12         else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
    13                  oldCap >= DEFAULT_INITIAL_CAPACITY)
    14             // 将阈值扩大一倍
    15             newThr = oldThr << 1; // double threshold
    16     }
    17     else if (oldThr > 0) // 对应使用 new HashMap(int initialCapacity) 初始化后，第一次 put 的时候
    18         newCap = oldThr;
    19     else {// 对应使用 new HashMap() 初始化后，第一次 put 的时候
    20         newCap = DEFAULT_INITIAL_CAPACITY;
    21         newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
    22     }
    23 
    24     if (newThr == 0) {
    25         float ft = (float)newCap * loadFactor;
    26         newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
    27                   (int)ft : Integer.MAX_VALUE);
    28     }
    29     threshold = newThr;
    30 
    31     // 用新的数组大小初始化新的数组
    32     Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    33     table = newTab; // 如果是初始化数组，到这里就结束了，返回 newTab 即可
    34 
    35     if (oldTab != null) {
    36         // 开始遍历原数组，进行数据迁移。
    37         for (int j = 0; j < oldCap; ++j) {
    38             Node<K,V> e;
    39             if ((e = oldTab[j]) != null) {
    40                 oldTab[j] = null;
    41                 // 如果该数组位置上只有单个元素，那就简单了，简单迁移这个元素就可以了
    42                 if (e.next == null)
    43                     newTab[e.hash & (newCap - 1)] = e;
    44                 // 如果是红黑树，具体我们就不展开了
    45                 else if (e instanceof TreeNode)
    46                     ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
    47                 else { 
    48                     // 这块是处理链表的情况，
    49                     // 需要将此链表拆成两个链表，放到新的数组中，并且保留原来的先后顺序
    50                     // loHead、loTail 对应一条链表，hiHead、hiTail 对应另一条链表，代码还是比较简单的
    51                     Node<K,V> loHead = null, loTail = null;
    52                     Node<K,V> hiHead = null, hiTail = null;
    53                     Node<K,V> next;
    54                     do {
    55                         next = e.next;
    56                         if ((e.hash & oldCap) == 0) {
    57                             if (loTail == null)
    58                                 loHead = e;
    59                             else
    60                                 loTail.next = e;
    61                             loTail = e;
    62                         }
    63                         else {
    64                             if (hiTail == null)
    65                                 hiHead = e;
    66                             else
    67                                 hiTail.next = e;
    68                             hiTail = e;
    69                         }
    70                     } while ((e = next) != null);
    71                     if (loTail != null) {
    72                         loTail.next = null;
    73                         // 第一条链表
    74                         newTab[j] = loHead;
    75                     }
    76                     if (hiTail != null) {
    77                         hiTail.next = null;
    78                         // 第二条链表的新的位置是 j + oldCap，这个很好理解
    79                         newTab[j + oldCap] = hiHead;
    80                     }
    81                 }
    82             }
    83         }
    84     }
    85     return newTab;
    86 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

 3.3get过程解析：

首先根据key计算hash值，定位到数组的某一位置；

检查数组该位置处的第一个元素是不是需要get的，不是就进行下一步；

若数组下是红黑树结构，就调用树的方法来取元素；

否则就进行遍历链表，直到找到key的相等（==或者equals（））；

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V get(Object key) {
     2     Node<K,V> e;
     3     return (e = getNode(hash(key), key)) == null ? null : e.value;
     4 }  
      
    
     5 final Node<K,V> getNode(int hash, Object key) {
     6     Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
     7     if ((tab = table) != null && (n = tab.length) > 0 &&
     8         (first = tab[(n - 1) & hash]) != null) {
     9         // 判断第一个节点是不是就是需要的
    10         if (first.hash == hash && // always check first node
    11             ((k = first.key) == key || (key != null && key.equals(k))))
    12             return first;
    13         if ((e = first.next) != null) {
    14             // 判断是否是红黑树
    15             if (first instanceof TreeNode)
    16                 return ((TreeNode<K,V>)first).getTreeNode(hash, key);
    17 
    18             // 链表遍历
    19             do {
    20                 if (e.hash == hash &&
    21                     ((k = e.key) == key || (key != null && key.equals(k))))
    22                     return e;
    23             } while ((e = e.next) != null);
    24         }
    25     }
    26     return null;
    27 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

4.Java8的ConcurrentHashMap：

![Image_Here](https://img2018.cnblogs.com/blog/1702473/201906/1702473-20190628144421823-1999460254.png)

4.1初始化：

无参构造方法：

    
    
    // 这构造函数里，什么都不干
    public ConcurrentHashMap() {
    }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
    public ConcurrentHashMap(int initialCapacity) {
        if (initialCapacity < 0)
            throw new IllegalArgumentException();
        int cap = ((initialCapacity >= (MAXIMUM_CAPACITY >>> 1)) ?
                   MAXIMUM_CAPACITY :
                   tableSizeFor(initialCapacity + (initialCapacity >>> 1) + 1));
        this.sizeCtl = cap;
    }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

通过提供的初始容量，计算sizeCtl=(【1.1*initialCapacity+1】，再向上取最近的2^n)。

4.2put的过程分析：

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V put(K key, V value) {
     2     return putVal(key, value, false);
     3 }  
      
      
    
     4 final V putVal(K key, V value, boolean onlyIfAbsent) {
     5     if (key == null || value == null) throw new NullPointerException();
     6     // 得到 hash 值
     7     int hash = spread(key.hashCode());
     8     // 用于记录相应链表的长度
     9     int binCount = 0;
    10     for (Node<K,V>[] tab = table;;) {
    11         Node<K,V> f; int n, i, fh;
    12         // 如果数组"空"，进行数组初始化
    13         if (tab == null || (n = tab.length) == 0)
    14             // 初始化数组，后面会详细介绍
    15             tab = initTable();
    16 
    17         // 找该 hash 值对应的数组下标，得到第一个节点 f
    18         else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
    19             // 如果数组该位置为空，
    20             //    用一次 CAS 操作将这个新值放入其中即可，这个 put 操作差不多就结束了，可以拉到最后面了
    21             //          如果 CAS 失败，那就是有并发操作，进到下一个循环就好了
    22             if (casTabAt(tab, i, null,
    23                          new Node<K,V>(hash, key, value, null)))
    24                 break;                   // no lock when adding to empty bin
    25         }
    26         // hash 居然可以等于 MOVED，这个需要到后面才能看明白，不过从名字上也能猜到，肯定是因为在扩容
    27         else if ((fh = f.hash) == MOVED)
    28             // 帮助数据迁移，这个等到看完数据迁移部分的介绍后，再理解这个就很简单了
    29             tab = helpTransfer(tab, f);
    30 
    31         else { // 到这里就是说，f 是该位置的头结点，而且不为空
    32 
    33             V oldVal = null;
    34             // 获取数组该位置的头结点的监视器锁
    35             synchronized (f) {
    36                 if (tabAt(tab, i) == f) {
    37                     if (fh >= 0) { // 头结点的 hash 值大于 0，说明是链表
    38                         // 用于累加，记录链表的长度
    39                         binCount = 1;
    40                         // 遍历链表
    41                         for (Node<K,V> e = f;; ++binCount) {
    42                             K ek;
    43                             // 如果发现了"相等"的 key，判断是否要进行值覆盖，然后也就可以 break 了
    44                             if (e.hash == hash &&
    45                                 ((ek = e.key) == key ||
    46                                  (ek != null && key.equals(ek)))) {
    47                                 oldVal = e.val;
    48                                 if (!onlyIfAbsent)
    49                                     e.val = value;
    50                                 break;
    51                             }
    52                             // 到了链表的最末端，将这个新值放到链表的最后面
    53                             Node<K,V> pred = e;
    54                             if ((e = e.next) == null) {
    55                                 pred.next = new Node<K,V>(hash, key,
    56                                                           value, null);
    57                                 break;
    58                             }
    59                         }
    60                     }
    61                     else if (f instanceof TreeBin) { // 红黑树
    62                         Node<K,V> p;
    63                         binCount = 2;
    64                         // 调用红黑树的插值方法插入新节点
    65                         if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key,
    66                                                        value)) != null) {
    67                             oldVal = p.val;
    68                             if (!onlyIfAbsent)
    69                                 p.val = value;
    70                         }
    71                     }
    72                 }
    73             }
    74 
    75             if (binCount != 0) {
    76                 // 判断是否要将链表转换为红黑树，临界值和 HashMap 一样，也是 8
    77                 if (binCount >= TREEIFY_THRESHOLD)
    78                     // 这个方法和 HashMap 中稍微有一点点不同，那就是它不是一定会进行红黑树转换，
    79                     // 如果当前数组的长度小于 64，那么会选择进行数组扩容，而不是转换为红黑树
    80                     //    具体源码我们就不看了，扩容部分后面说
    81                     treeifyBin(tab, i);
    82                 if (oldVal != null)
    83                     return oldVal;
    84                 break;
    85             }
    86         }
    87     }
    88     // 
    89     addCount(1L, binCount);
    90     return null;
    91 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

流程的大概总结：

首先计算key的hash值，定位到数组的某一位置上；

若该数组为空，就进行数组的初始化initTable（）；

若数组不为空，找到hash值对应的数组下标，并返回第一个结点，若数组的该位置为空，就采用CAS操作将新元素放入到，该位置上put方法就可以宣告结束了。若CAS操作失败，说明有并发操作，等待下一次的循环就好；

若数该位置处的首元素的hash值为（"MOVED"），说明数组正在扩容，帮助数据迁移helpTransfer（）；

当数组该位置处的头结点不为空，也不进行扩容时：获取数组该位置处头结点的监视器锁，若头结点的hash值>0,说明是链表结构，遍历链表，看是否需要进行覆盖，否则就在链表的末尾处插入新值；否则为树结构，调用putTreeval方法插入新值。

若是链表结构，再进行判断是否需要转换成红黑树。

put主要操作的介绍：

初始化数组：（initTable）

初始化一个合适大小的数组，再设置sizeCtl，通过sizeCtl控制CAS操作。

若sizeCtl的值<0，说明有其他线程正在初始化；

否则采用CAS操作进行数组的初始化，将sizeCtl的值设为-1，说明抢到了锁；

初始化数组，长度为16，或者提供的长度，将这个数组赋值给table，table是Volatile的；

设置sizeCtl的值为sc。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 private final Node<K,V>[] initTable() {
     2     Node<K,V>[] tab; int sc;
     3     while ((tab = table) == null || tab.length == 0) {
     4         // 初始化的"功劳"被其他线程"抢去"了
     5         if ((sc = sizeCtl) < 0)
     6             Thread.yield(); // lost initialization race; just spin
     7         // CAS 一下，将 sizeCtl 设置为 -1，代表抢到了锁
     8         else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
     9             try {
    10                 if ((tab = table) == null || tab.length == 0) {
    11                     // DEFAULT_CAPACITY 默认初始容量是 16
    12                     int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
    13                     // 初始化数组，长度为 16 或初始化时提供的长度
    14                     Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];
    15                     // 将这个数组赋值给 table，table 是 volatile 的
    16                     table = tab = nt;
    17                     // 如果 n 为 16 的话，那么这里 sc = 12
    18                     // 其实就是 0.75 * n
    19                     sc = n - (n >>> 2);
    20                 }
    21             } finally {
    22                 // 设置 sizeCtl 为 sc，我们就当是 12 吧
    23                 sizeCtl = sc;
    24             }
    25             break;
    26         }
    27     }
    28     return tab;
    29 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

链表转红黑树：（treeifyBin）

treeifyBin不一定进行红黑树的转换，也可能只是数组的扩容。转换前先计算链表的长度，若长度小于限定值64 ，就只进行扩容操作，否则转红黑树。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 private final void treeifyBin(Node<K,V>[] tab, int index) {
     2     Node<K,V> b; int n, sc;
     3     if (tab != null) {
     4         // MIN_TREEIFY_CAPACITY 为 64
     5         // 所以，如果数组长度小于 64 的时候，其实也就是 32 或者 16 或者更小的时候，会进行数组扩容
     6         if ((n = tab.length) < MIN_TREEIFY_CAPACITY)
     7             // 后面我们再详细分析这个方法
     8             tryPresize(n << 1);
     9         // b 是头结点
    10         else if ((b = tabAt(tab, index)) != null && b.hash >= 0) {
    11             // 加锁
    12             synchronized (b) {
    13 
    14                 if (tabAt(tab, index) == b) {
    15                     // 下面就是遍历链表，建立一颗红黑树
    16                     TreeNode<K,V> hd = null, tl = null;
    17                     for (Node<K,V> e = b; e != null; e = e.next) {
    18                         TreeNode<K,V> p =
    19                             new TreeNode<K,V>(e.hash, e.key, e.val,
    20                                               null, null);
    21                         if ((p.prev = tl) == null)
    22                             hd = p;
    23                         else
    24                             tl.next = p;
    25                         tl = p;
    26                     }
    27                     // 将红黑树设置到数组相应位置中
    28                     setTabAt(tab, index, new TreeBin<K,V>(hd));
    29                 }
    30             }
    31         }
    32     }
    33 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

扩容：（tryPresize）

扩大容量为原先的2倍。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 // 首先要说明的是，方法参数 size 传进来的时候就已经翻了倍了
     2 private final void tryPresize(int size) {
     3     // c：size 的 1.5 倍，再加 1，再往上取最近的 2 的 n 次方。
     4     int c = (size >= (MAXIMUM_CAPACITY >>> 1)) ? MAXIMUM_CAPACITY :
     5         tableSizeFor(size + (size >>> 1) + 1);
     6     int sc;
     7     while ((sc = sizeCtl) >= 0) {
     8         Node<K,V>[] tab = table; int n;
     9 
    10         // 这个 if 分支和之前说的初始化数组的代码基本上是一样的，在这里，我们可以不用管这块代码
    11         if (tab == null || (n = tab.length) == 0) {
    12             n = (sc > c) ? sc : c;
    13             if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
    14                 try {
    15                     if (table == tab) {
    16                         @SuppressWarnings("unchecked")
    17                         Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];
    18                         table = nt;
    19                         sc = n - (n >>> 2); // 0.75 * n
    20                     }
    21                 } finally {
    22                     sizeCtl = sc;
    23                 }
    24             }
    25         }
    26         else if (c <= sc || n >= MAXIMUM_CAPACITY)
    27             break;
    28         else if (tab == table) {
    29             // 我没看懂 rs 的真正含义是什么，不过也关系不大
    30             int rs = resizeStamp(n);
    31 
    32             if (sc < 0) {
    33                 Node<K,V>[] nt;
    34                 if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 ||
    35                     sc == rs + MAX_RESIZERS || (nt = nextTable) == null ||
    36                     transferIndex <= 0)
    37                     break;
    38                 // 2. 用 CAS 将 sizeCtl 加 1，然后执行 transfer 方法
    39                 //    此时 nextTab 不为 null
    40                 if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1))
    41                     transfer(tab, nt);
    42             }
    43             // 1. 将 sizeCtl 设置为 (rs << RESIZE_STAMP_SHIFT) + 2)
    44             //     我是没看懂这个值真正的意义是什么？不过可以计算出来的是，结果是一个比较大的负数
    45             //  调用 transfer 方法，此时 nextTab 参数为 null
    46             else if (U.compareAndSwapInt(this, SIZECTL, sc,
    47                                          (rs << RESIZE_STAMP_SHIFT) + 2))
    48                 transfer(tab, null);
    49         }
    50     }
    51 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

数据的迁移：（transfer）

下面这个方法有点长，将原来的 tab 数组的元素迁移到新的 nextTab 数组中。

虽然我们之前说的 tryPresize 方法中多次调用 transfer 不涉及多线程，但是这个 transfer
方法可以在其他地方被调用，典型地，我们之前在说 put 方法的时候就说过了，请往上看 put 方法，是不是有个地方调用了 helpTransfer
方法，helpTransfer 方法会调用 transfer 方法的。

此方法支持多线程执行，外围调用此方法的时候，会保证第一个发起数据迁移的线程，nextTab 参数为 null，之后再调用此方法的时候，nextTab 不会为
null。

阅读源码之前，先要理解并发操作的机制。原数组长度为 n，所以我们有 n
个迁移任务，让每个线程每次负责一个小任务是最简单的，每做完一个任务再检测是否有其他没做完的任务，帮助迁移就可以了，而 Doug Lea 使用了一个
stride，简单理解就是步长，每个线程每次负责迁移其中的一部分，如每次迁移 16
个小任务。所以，我们就需要一个全局的调度者来安排哪个线程执行哪几个任务，这个就是属性 transferIndex 的作用。

第一个发起数据迁移的线程会将 transferIndex 指向原数组最后的位置，然后从后往前的 stride 个任务属于第一个线程，然后将
transferIndex 指向新的位置，再往前的 stride
个任务属于第二个线程，依此类推。当然，这里说的第二个线程不是真的一定指代了第二个线程，也可以是同一个线程，这个读者应该能理解吧。其实就是将一个大的迁移任务分为了一个个任务包。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
      1 private final void transfer(Node<K,V>[] tab, Node<K,V>[] nextTab) {
      2     int n = tab.length, stride;
      3 
      4     // stride 在单核下直接等于 n，多核模式下为 (n>>>3)/NCPU，最小值是 16
      5     // stride 可以理解为”步长“，有 n 个位置是需要进行迁移的，
      6     //   将这 n 个任务分为多个任务包，每个任务包有 stride 个任务
      7     if ((stride = (NCPU > 1) ? (n >>> 3) / NCPU : n) < MIN_TRANSFER_STRIDE)
      8         stride = MIN_TRANSFER_STRIDE; // subdivide range
      9 
     10     // 如果 nextTab 为 null，先进行一次初始化
     11     //    前面我们说了，外围会保证第一个发起迁移的线程调用此方法时，参数 nextTab 为 null
     12     //       之后参与迁移的线程调用此方法时，nextTab 不会为 null
     13     if (nextTab == null) {
     14         try {
     15             // 容量翻倍
     16             Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n << 1];
     17             nextTab = nt;
     18         } catch (Throwable ex) {      // try to cope with OOME
     19             sizeCtl = Integer.MAX_VALUE;
     20             return;
     21         }
     22         // nextTable 是 ConcurrentHashMap 中的属性
     23         nextTable = nextTab;
     24         // transferIndex 也是 ConcurrentHashMap 的属性，用于控制迁移的位置
     25         transferIndex = n;
     26     }
     27 
     28     int nextn = nextTab.length;
     29 
     30     // ForwardingNode 翻译过来就是正在被迁移的 Node
     31     // 这个构造方法会生成一个Node，key、value 和 next 都为 null，关键是 hash 为 MOVED
     32     // 后面我们会看到，原数组中位置 i 处的节点完成迁移工作后，
     33     //    就会将位置 i 处设置为这个 ForwardingNode，用来告诉其他线程该位置已经处理过了
     34     //    所以它其实相当于是一个标志。
     35     ForwardingNode<K,V> fwd = new ForwardingNode<K,V>(nextTab);
     36 
     37 
     38     // advance 指的是做完了一个位置的迁移工作，可以准备做下一个位置的了
     39     boolean advance = true;
     40     boolean finishing = false; // to ensure sweep before committing nextTab
     41 
     42     /*
     43      * 下面这个 for 循环，最难理解的在前面，而要看懂它们，应该先看懂后面的，然后再倒回来看
     44      * 
     45      */
     46 
     47     // i 是位置索引，bound 是边界，注意是从后往前
     48     for (int i = 0, bound = 0;;) {
     49         Node<K,V> f; int fh;
     50 
     51         // 下面这个 while 真的是不好理解
     52         // advance 为 true 表示可以进行下一个位置的迁移了
     53         //   简单理解结局：i 指向了 transferIndex，bound 指向了 transferIndex-stride
     54         while (advance) {
     55             int nextIndex, nextBound;
     56             if (--i >= bound || finishing)
     57                 advance = false;
     58 
     59             // 将 transferIndex 值赋给 nextIndex
     60             // 这里 transferIndex 一旦小于等于 0，说明原数组的所有位置都有相应的线程去处理了
     61             else if ((nextIndex = transferIndex) <= 0) {
     62                 i = -1;
     63                 advance = false;
     64             }
     65             else if (U.compareAndSwapInt
     66                      (this, TRANSFERINDEX, nextIndex,
     67                       nextBound = (nextIndex > stride ?
     68                                    nextIndex - stride : 0))) {
     69                 // 看括号中的代码，nextBound 是这次迁移任务的边界，注意，是从后往前
     70                 bound = nextBound;
     71                 i = nextIndex - 1;
     72                 advance = false;
     73             }
     74         }
     75         if (i < 0 || i >= n || i + n >= nextn) {
     76             int sc;
     77             if (finishing) {
     78                 // 所有的迁移操作已经完成
     79                 nextTable = null;
     80                 // 将新的 nextTab 赋值给 table 属性，完成迁移
     81                 table = nextTab;
     82                 // 重新计算 sizeCtl：n 是原数组长度，所以 sizeCtl 得出的值将是新数组长度的 0.75 倍
     83                 sizeCtl = (n << 1) - (n >>> 1);
     84                 return;
     85             }
     86 
     87             // 之前我们说过，sizeCtl 在迁移前会设置为 (rs << RESIZE_STAMP_SHIFT) + 2
     88             // 然后，每有一个线程参与迁移就会将 sizeCtl 加 1，
     89             // 这里使用 CAS 操作对 sizeCtl 进行减 1，代表做完了属于自己的任务
     90             if (U.compareAndSwapInt(this, SIZECTL, sc = sizeCtl, sc - 1)) {
     91                 // 任务结束，方法退出
     92                 if ((sc - 2) != resizeStamp(n) << RESIZE_STAMP_SHIFT)
     93                     return;
     94 
     95                 // 到这里，说明 (sc - 2) == resizeStamp(n) << RESIZE_STAMP_SHIFT，
     96                 // 也就是说，所有的迁移任务都做完了，也就会进入到上面的 if(finishing){} 分支了
     97                 finishing = advance = true;
     98                 i = n; // recheck before commit
     99             }
    100         }
    101         // 如果位置 i 处是空的，没有任何节点，那么放入刚刚初始化的 ForwardingNode ”空节点“
    102         else if ((f = tabAt(tab, i)) == null)
    103             advance = casTabAt(tab, i, null, fwd);
    104         // 该位置处是一个 ForwardingNode，代表该位置已经迁移过了
    105         else if ((fh = f.hash) == MOVED)
    106             advance = true; // already processed
    107         else {
    108             // 对数组该位置处的结点加锁，开始处理数组该位置处的迁移工作
    109             synchronized (f) {
    110                 if (tabAt(tab, i) == f) {
    111                     Node<K,V> ln, hn;
    112                     // 头结点的 hash 大于 0，说明是链表的 Node 节点
    113                     if (fh >= 0) {
    114                         // 下面这一块和 Java7 中的 ConcurrentHashMap 迁移是差不多的，
    115                         // 需要将链表一分为二，
    116                         //   找到原链表中的 lastRun，然后 lastRun 及其之后的节点是一起进行迁移的
    117                         //   lastRun 之前的节点需要进行克隆，然后分到两个链表中
    118                         int runBit = fh & n;
    119                         Node<K,V> lastRun = f;
    120                         for (Node<K,V> p = f.next; p != null; p = p.next) {
    121                             int b = p.hash & n;
    122                             if (b != runBit) {
    123                                 runBit = b;
    124                                 lastRun = p;
    125                             }
    126                         }
    127                         if (runBit == 0) {
    128                             ln = lastRun;
    129                             hn = null;
    130                         }
    131                         else {
    132                             hn = lastRun;
    133                             ln = null;
    134                         }
    135                         for (Node<K,V> p = f; p != lastRun; p = p.next) {
    136                             int ph = p.hash; K pk = p.key; V pv = p.val;
    137                             if ((ph & n) == 0)
    138                                 ln = new Node<K,V>(ph, pk, pv, ln);
    139                             else
    140                                 hn = new Node<K,V>(ph, pk, pv, hn);
    141                         }
    142                         // 其中的一个链表放在新数组的位置 i
    143                         setTabAt(nextTab, i, ln);
    144                         // 另一个链表放在新数组的位置 i+n
    145                         setTabAt(nextTab, i + n, hn);
    146                         // 将原数组该位置处设置为 fwd，代表该位置已经处理完毕，
    147                         //    其他线程一旦看到该位置的 hash 值为 MOVED，就不会进行迁移了
    148                         setTabAt(tab, i, fwd);
    149                         // advance 设置为 true，代表该位置已经迁移完毕
    150                         advance = true;
    151                     }
    152                     else if (f instanceof TreeBin) {
    153                         // 红黑树的迁移
    154                         TreeBin<K,V> t = (TreeBin<K,V>)f;
    155                         TreeNode<K,V> lo = null, loTail = null;
    156                         TreeNode<K,V> hi = null, hiTail = null;
    157                         int lc = 0, hc = 0;
    158                         for (Node<K,V> e = t.first; e != null; e = e.next) {
    159                             int h = e.hash;
    160                             TreeNode<K,V> p = new TreeNode<K,V>
    161                                 (h, e.key, e.val, null, null);
    162                             if ((h & n) == 0) {
    163                                 if ((p.prev = loTail) == null)
    164                                     lo = p;
    165                                 else
    166                                     loTail.next = p;
    167                                 loTail = p;
    168                                 ++lc;
    169                             }
    170                             else {
    171                                 if ((p.prev = hiTail) == null)
    172                                     hi = p;
    173                                 else
    174                                     hiTail.next = p;
    175                                 hiTail = p;
    176                                 ++hc;
    177                             }
    178                         }
    179                         // 如果一分为二后，节点数少于 8，那么将红黑树转换回链表
    180                         ln = (lc <= UNTREEIFY_THRESHOLD) ? untreeify(lo) :
    181                             (hc != 0) ? new TreeBin<K,V>(lo) : t;
    182                         hn = (hc <= UNTREEIFY_THRESHOLD) ? untreeify(hi) :
    183                             (lc != 0) ? new TreeBin<K,V>(hi) : t;
    184 
    185                         // 将 ln 放置在新数组的位置 i
    186                         setTabAt(nextTab, i, ln);
    187                         // 将 hn 放置在新数组的位置 i+n
    188                         setTabAt(nextTab, i + n, hn);
    189                         // 将原数组该位置处设置为 fwd，代表该位置已经处理完毕，
    190                         //    其他线程一旦看到该位置的 hash 值为 MOVED，就不会进行迁移了
    191                         setTabAt(tab, i, fwd);
    192                         // advance 设置为 true，代表该位置已经迁移完毕
    193                         advance = true;
    194                     }
    195                 }
    196             }
    197         }
    198     }
    199 }

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

4.3get过程的分析：

计算key的hash值，根据hash值定位到数组的某一位置；

根据该位置处结点的性质进行查找：

若该位置为null，直接返回null；

若该位置处的结点是要get的，就返回该节点的值即可；

若该位置结点的hash值小于0，说明正在进行扩容，或者是树结构；

否则，就是链表结构，直接进行对比key值即可。

[![复制代码](//common.cnblogs.com/images/copycode.gif)](javascript:void\(0\);
"复制代码")

    
    
     1 public V get(Object key) {
     2     Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
     3     int h = spread(key.hashCode());
     4     if ((tab = table) != null && (n = tab.length) > 0 &&
     5         (e = tabAt(tab, (n - 1) & h)) != null) {
     6         // 判断头结点是否就是我们需要的节点
     7         if ((eh = e.hash) == h) {
     8             if ((ek = e.key) == key || (ek != null && key.equals(ek)))
     9                 return e.val;
    10         }
    11         // 如果头结点的 hash 小于 0，说明 正在扩容，或者该位置是红黑树
    12         else if (eh < 0)
    13             // 参考 ForwardingNode.find(int h, Object k) 和 TreeBin.find(int h, Object k)
    14             return (p = e.find(h, key)) != null ? p.val : null;
    15 
    16         // 遍历链表
    17         while ((e = e.next) != null) {
    18             if (e.hash == h &&
    19                 ((ek = e.key) == key || (ek != null && key.equals(ek))))
    20                 return e.val;
    21         }
    22     }
    23     return null;
    24 }
