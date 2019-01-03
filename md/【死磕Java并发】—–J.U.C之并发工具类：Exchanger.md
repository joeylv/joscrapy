  * 1 应用示例
  * 2 实现分析
  * 3 exchange(V x)

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

> 此篇博客所有源码均来自JDK 1.8

前面三篇博客分别介绍了CyclicBarrier、CountDownLatch、Semaphore，现在介绍并发工具类中的最后一个Exchange。Exchange是最简单的也是最复杂的，简单在于API非常简单，就一个构造方法和两个exchange()方法，最复杂在于它的实现是最复杂的（反正我是看晕了的）。

在API是这么介绍的：可以在对中对元素进行配对和交换的线程的同步点。每个线程将条目上的某个方法呈现给 exchange
方法，与伙伴线程进行匹配，并且在返回时接收其伙伴的对象。Exchanger 可能被视为 SynchronousQueue 的双向形式。Exchanger
可能在应用程序（比如遗传算法和管道设计）中很有用。

Exchanger，它允许在并发任务之间交换数据。具体来说，Exchanger类允许在两个线程之间定义同步点。当两个线程都到达同步点时，他们交换数据结构，因此第一个线程的数据结构进入到第二个线程中，第二个线程的数据结构进入到第一个线程中。

## 应用示例

Exchange实现较为复杂，我们先看其怎么使用，然后再来分析其源码。现在我们用Exchange来模拟生产-消费者问题：

    
    
    public class ExchangerTest {
    
        static class Producer implements Runnable{
    
            //生产者、消费者交换的数据结构
            private List<String> buffer;
    
            //步生产者和消费者的交换对象
            private Exchanger<List<String>> exchanger;
    
            Producer(List<String> buffer,Exchanger<List<String>> exchanger){
                this.buffer = buffer;
                this.exchanger = exchanger;
            }
    
            @Override
            public void run() {
                for(int i = 1 ; i < 5 ; i++){
                    System.out.println("生产者第" + i + "次提供");
                    for(int j = 1 ; j <= 3 ; j++){
                        System.out.println("生产者装入" + i  + "--" + j);
                        buffer.add("buffer：" + i + "--" + j);
                    }
    
                    System.out.println("生产者装满，等待与消费者交换...");
                    try {
                        exchanger.exchange(buffer);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    
        static class Consumer implements Runnable {
            private List<String> buffer;
    
            private final Exchanger<List<String>> exchanger;
    
            public Consumer(List<String> buffer, Exchanger<List<String>> exchanger) {
                this.buffer = buffer;
                this.exchanger = exchanger;
            }
    
            @Override
            public void run() {
                for (int i = 1; i < 5; i++) {
                    //调用exchange()与消费者进行数据交换
                    try {
                        buffer = exchanger.exchange(buffer);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
    
                    System.out.println("消费者第" + i + "次提取");
                    for (int j = 1; j <= 3 ; j++) {
                        System.out.println("消费者 : " + buffer.get(0));
                        buffer.remove(0);
                    }
                }
            }
        }
    
        public static void main(String[] args){
            List<String> buffer1 = new ArrayList<String>();
            List<String> buffer2 = new ArrayList<String>();
    
            Exchanger<List<String>> exchanger = new Exchanger<List<String>>();
    
            Thread producerThread = new Thread(new Producer(buffer1,exchanger));
            Thread consumerThread = new Thread(new Consumer(buffer2,exchanger));
    
            producerThread.start();
            consumerThread.start();
        }
    }
    

运行结果：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/sijava/2018120820001.png)

首先生产者Producer、消费者Consumer首先都创建一个缓冲列表，通过Exchanger来同步交换数据。消费中通过调用Exchanger与生产者进行同步来获取数据，而生产者则通过for循环向缓存队列存储数据并使用exchanger对象消费者同步。到消费者从exchanger哪里得到数据后，他的缓冲列表中有3个数据，而生产者得到的则是一个空的列表。上面的例子充分展示了消费者-
生产者是如何利用Exchanger来完成数据交换的。

在Exchanger中，如果一个线程已经到达了exchanger节点时，对于它的伙伴节点的情况有三种：

  1. 如果它的伙伴节点在该线程到达之前已经调用了exchanger方法，则它会唤醒它的伙伴然后进行数据交换，得到各自数据返回。
  2. 如果它的伙伴节点还没有到达交换点，则该线程将会被挂起，等待它的伙伴节点到达被唤醒，完成数据交换。
  3. 如果当前线程被中断了则抛出异常，或者等待超时了，则抛出超时异常。

## 实现分析

Exchanger算法的核心是通过一个可交换数据的slot，以及一个可以带有数据item的参与者。源码中的描述如下：

    
    
          for (;;) {
            if (slot is empty) {                       // offer
              place item in a Node;
              if (can CAS slot from empty to node) {
                wait for release;
                return matching item in node;
              }
            }
            else if (can CAS slot from node to empty) { // release
              get the item in node;
              set matching item in node;
              release waiting thread;
            }
            // else retry on CAS failure
          }
    

Exchanger中定义了如下几个重要的成员变量：

    
    
    private final Participant participant;
    private volatile Node[] arena;
    private volatile Node slot;
    

participant的作用是为每个线程保留唯一的一个Node节点。

slot为单个槽，arena为数组槽。他们都是Node类型。在这里可能会感觉到疑惑，slot作为Exchanger交换数据的场景，应该只需要一个就可以了啊？为何还多了一个Participant
和数组类型的arena呢？一个slot交换场所原则上来说应该是可以的，但实际情况却不是如此，多个参与者使用同一个交换场所时，会存在严重伸缩性问题。既然单个交换场所存在问题，那么我们就安排多个，也就是数组arena。通过数组arena来安排不同的线程使用不同的slot来降低竞争问题，并且可以保证最终一定会成对交换数据。但是Exchanger不是一来就会生成arena数组来降低竞争，只有当产生竞争是才会生成arena数组。那么怎么将Node与当前线程绑定呢？Participant
，Participant
的作用就是为每个线程保留唯一的一个Node节点，它继承ThreadLocal，同时在Node节点中记录在arena中的下标index。

Node定义如下：

    
    
        @sun.misc.Contended static final class Node {
            int index;              // Arena index
            int bound;              // Last recorded value of Exchanger.bound
            int collides;           // Number of CAS failures at current bound
            int hash;               // Pseudo-random for spins
            Object item;            // This thread"s current item
            volatile Object match;  // Item provided by releasing thread
            volatile Thread parked; // Set to this thread when parked, else null
        }
    

  * index：arena的下标；
  * bound：上一次记录的Exchanger.bound；
  * collides：在当前bound下CAS失败的次数；
  * hash：伪随机数，用于自旋；
  * item：这个线程的当前项，也就是需要交换的数据；
  * match：做releasing操作的线程传递的项；
  * parked：挂起时设置线程值，其他情况下为null；

在Node定义中有两个变量值得思考：bound以及collides。前面提到了数组area是为了避免竞争而产生的，如果系统不存在竞争问题，那么完全没有必要开辟一个高效的arena来徒增系统的复杂性。首先通过单个slot的exchanger来交换数据，当探测到竞争时将安排不同的位置的slot来保存线程Node，并且可以确保没有slot会在同一个缓存行上。如何来判断会有竞争呢？CAS替换slot失败，如果失败，则通过记录冲突次数来扩展arena的尺寸，我们在记录冲突的过程中会跟踪“bound”的值，以及会重新计算冲突次数在bound的值被改变时。这里阐述可能有点儿模糊，不着急，我们先有这个概念，后面在arenaExchange中再次做详细阐述。

我们直接看exchange()方法

## exchange(V x)

**exchange(V x)** ：等待另一个线程到达此交换点（除非当前线程被中断），然后将给定的对象传送给该线程，并接收该线程的对象。方法定义如下：

    
    
        public V exchange(V x) throws InterruptedException {
            Object v;
            Object item = (x == null) ? NULL_ITEM : x; // translate null args
            if ((arena != null ||
                 (v = slotExchange(item, false, 0L)) == null) &&
                ((Thread.interrupted() || // disambiguates null return
                  (v = arenaExchange(item, false, 0L)) == null)))
                throw new InterruptedException();
            return (v == NULL_ITEM) ? null : (V)v;
        }
    

这个方法比较好理解：arena为数组槽，如果为null，则执行slotExchange()方法，否则判断线程是否中断，如果中断值抛出InterruptedException异常，没有中断则执行arenaExchange()方法。整套逻辑就是：如果slotExchange(Object
item, boolean timed, long ns)方法执行失败了就执行arenaExchange(Object item, boolean
timed, long ns)方法，最后返回结果V。

NULL_ITEM 为一个空节点，其实就是一个Object对象而已，slotExchange()为单个slot交换。

**slotExchange(Object item, boolean timed, long ns)**

    
    
        private final Object slotExchange(Object item, boolean timed, long ns) {
            // 获取当前线程的节点 p
            Node p = participant.get();
            // 当前线程
            Thread t = Thread.currentThread();
            // 线程中断，直接返回
            if (t.isInterrupted())
                return null;
            // 自旋
            for (Node q;;) {
                //slot != null
                if ((q = slot) != null) {
                    //尝试CAS替换
                    if (U.compareAndSwapObject(this, SLOT, q, null)) {
                        Object v = q.item;      // 当前线程的项，也就是交换的数据
                        q.match = item;         // 做releasing操作的线程传递的项
                        Thread w = q.parked;    // 挂起时设置线程值
                        // 挂起线程不为null，线程挂起
                        if (w != null)
                            U.unpark(w);
                        return v;
                    }
                    //如果失败了，则创建arena
                    //bound 则是上次Exchanger.bound
                    if (NCPU > 1 && bound == 0 &&
                            U.compareAndSwapInt(this, BOUND, 0, SEQ))
                        arena = new Node[(FULL + 2) << ASHIFT];
                }
                //如果arena != null，直接返回，进入arenaExchange逻辑处理
                else if (arena != null)
                    return null;
                else {
                    p.item = item;
                    if (U.compareAndSwapObject(this, SLOT, null, p))
                        break;
                    p.item = null;
                }
            }
    
            /*
             * 等待 release
             * 进入spin+block模式
             */
            int h = p.hash;
            long end = timed ? System.nanoTime() + ns : 0L;
            int spins = (NCPU > 1) ? SPINS : 1;
            Object v;
            while ((v = p.match) == null) {
                if (spins > 0) {
                    h ^= h << 1; h ^= h >>> 3; h ^= h << 10;
                    if (h == 0)
                        h = SPINS | (int)t.getId();
                    else if (h < 0 && (--spins & ((SPINS >>> 1) - 1)) == 0)
                        Thread.yield();
                }
                else if (slot != p)
                    spins = SPINS;
                else if (!t.isInterrupted() && arena == null &&
                        (!timed || (ns = end - System.nanoTime()) > 0L)) {
                    U.putObject(t, BLOCKER, this);
                    p.parked = t;
                    if (slot == p)
                        U.park(false, ns);
                    p.parked = null;
                    U.putObject(t, BLOCKER, null);
                }
                else if (U.compareAndSwapObject(this, SLOT, p, null)) {
                    v = timed && ns <= 0L && !t.isInterrupted() ? TIMED_OUT : null;
                    break;
                }
            }
            U.putOrderedObject(p, MATCH, null);
            p.item = null;
            p.hash = h;
            return v;
        }
    

  * 程序首先通过participant获取当前线程节点Node。检测是否中断，如果中断return null，等待后续抛出InterruptedException异常。
  * 如果slot不为null，则进行slot消除，成功直接返回数据V，否则失败，则创建arena消除数组。
  * 如果slot为null，但arena不为null，则返回null，进入arenaExchange逻辑。
  * 如果slot为null，且arena也为null，则尝试占领该slot，失败重试，成功则跳出循环进入spin+block（自旋+阻塞）模式。

在自旋+阻塞模式中，首先取得结束时间和自旋次数。如果match(做releasing操作的线程传递的项)为null，其首先尝试spins+随机次自旋（改自旋使用当前节点中的hash，并改变之）和退让。当自旋数为0后，假如slot发生了改变（slot
!=
p）则重置自旋数并重试。否则假如：当前未中断&arena为null&（当前不是限时版本或者限时版本+当前时间未结束）：阻塞或者限时阻塞。假如：当前中断或者arena不为null或者当前为限时版本+时间已经结束：不限时版本：置v为null；限时版本：如果时间结束以及未中断则TIMED_OUT；否则给出null（原因是探测到arena非空或者当前线程中断）。

match不为空时跳出循环。

整个slotExchange清晰明了。

**arenaExchange(Object item, boolean timed, long ns)**

    
    
        private final Object arenaExchange(Object item, boolean timed, long ns) {
            Node[] a = arena;
            Node p = participant.get();
            for (int i = p.index;;) {                      // access slot at i
                int b, m, c; long j;                       // j is raw array offset
                Node q = (Node)U.getObjectVolatile(a, j = (i << ASHIFT) + ABASE);
                if (q != null && U.compareAndSwapObject(a, j, q, null)) {
                    Object v = q.item;                     // release
                    q.match = item;
                    Thread w = q.parked;
                    if (w != null)
                        U.unpark(w);
                    return v;
                }
                else if (i <= (m = (b = bound) & MMASK) && q == null) {
                    p.item = item;                         // offer
                    if (U.compareAndSwapObject(a, j, null, p)) {
                        long end = (timed && m == 0) ? System.nanoTime() + ns : 0L;
                        Thread t = Thread.currentThread(); // wait
                        for (int h = p.hash, spins = SPINS;;) {
                            Object v = p.match;
                            if (v != null) {
                                U.putOrderedObject(p, MATCH, null);
                                p.item = null;             // clear for next use
                                p.hash = h;
                                return v;
                            }
                            else if (spins > 0) {
                                h ^= h << 1; h ^= h >>> 3; h ^= h << 10; // xorshift
                                if (h == 0)                // initialize hash
                                    h = SPINS | (int)t.getId();
                                else if (h < 0 &&          // approx 50% true
                                         (--spins & ((SPINS >>> 1) - 1)) == 0)
                                    Thread.yield();        // two yields per wait
                            }
                            else if (U.getObjectVolatile(a, j) != p)
                                spins = SPINS;       // releaser hasn"t set match yet
                            else if (!t.isInterrupted() && m == 0 &&
                                     (!timed ||
                                      (ns = end - System.nanoTime()) > 0L)) {
                                U.putObject(t, BLOCKER, this); // emulate LockSupport
                                p.parked = t;              // minimize window
                                if (U.getObjectVolatile(a, j) == p)
                                    U.park(false, ns);
                                p.parked = null;
                                U.putObject(t, BLOCKER, null);
                            }
                            else if (U.getObjectVolatile(a, j) == p &&
                                     U.compareAndSwapObject(a, j, p, null)) {
                                if (m != 0)                // try to shrink
                                    U.compareAndSwapInt(this, BOUND, b, b + SEQ - 1);
                                p.item = null;
                                p.hash = h;
                                i = p.index >>>= 1;        // descend
                                if (Thread.interrupted())
                                    return null;
                                if (timed && m == 0 && ns <= 0L)
                                    return TIMED_OUT;
                                break;                     // expired; restart
                            }
                        }
                    }
                    else
                        p.item = null;                     // clear offer
                }
                else {
                    if (p.bound != b) {                    // stale; reset
                        p.bound = b;
                        p.collides = 0;
                        i = (i != m || m == 0) ? m : m - 1;
                    }
                    else if ((c = p.collides) < m || m == FULL ||
                             !U.compareAndSwapInt(this, BOUND, b, b + SEQ + 1)) {
                        p.collides = c + 1;
                        i = (i == 0) ? m : i - 1;          // cyclically traverse
                    }
                    else
                        i = m + 1;                         // grow
                    p.index = i;
                }
            }
        }
    

首先通过participant取得当前节点Node，然后根据当前节点Node的index去取arena中相对应的节点node。前面提到过arena可以确保不同的slot在arena中是不会相冲突的，那么是怎么保证的呢？我们先看arena的创建：

    
    
    arena = new Node[(FULL + 2) << ASHIFT];
    

这个arena到底有多大呢？我们先看FULL 和ASHIFT的定义：

    
    
    static final int FULL = (NCPU >= (MMASK << 1)) ? MMASK : NCPU >>> 1;
    private static final int ASHIFT = 7;
    
    private static final int NCPU = Runtime.getRuntime().availableProcessors();
    private static final int MMASK = 0xff;      // 255
    

假如我的机器NCPU = 8 ，则得到的是768大小的arena数组。然后通过以下代码取得在arena中的节点：

    
    
     Node q = (Node)U.getObjectVolatile(a, j = (i << ASHIFT) + ABASE);
    

他仍然是通过右移ASHIFT位来取得Node的，ABASE定义如下：

    
    
    Class<?> ak = Node[].class;
    ABASE = U.arrayBaseOffset(ak) + (1 << ASHIFT);
    

U.arrayBaseOffset获取对象头长度，数组元素的大小可以通过unsafe.arrayIndexScale(T[].class)
方法获取到。这也就是说要访问类型为T的第N个元素的话，你的偏移量offset应该是arrayOffset+N*arrayScale。也就是说BASE =
arrayOffset+ 128 。其次我们再看Node节点的定义

    
    
      @sun.misc.Contended static final class Node{
        ....
      }
    

在Java 8 中我们是可以利用sun.misc.Contended来规避伪共享的。所以说通过 <<
ASHIFT方式加上sun.misc.Contended，所以使得任意两个可用Node不会再同一个缓存行中。

关于伪共享请参考如下博文：  
[伪共享(False Sharing)](http://ifeve.com/falsesharing/)  
[ Java8中用sun.misc.Contended避免伪共享(false
sharing)](http://blog.csdn.net/aigoogle/article/details/41518369)

我们再次回到arenaExchange()。取得arena中的node节点后，如果定位的节点q
不为空，且CAS操作成功，则交换数据，返回交换的数据，唤醒等待的线程。

如果q等于null且下标在bound & MMASK范围之内，则尝试占领该位置，如果成功，则采用自旋 + 阻塞的方式进行等待交换数据。

如果下标不在bound & MMASK范围之内获取由于q不为null但是竞争失败的时候：消除p。加入bound 不等于当前节点的bond（b !=
p.bound），则更新p.bound = b，collides = 0 ，i = m或者m – 1。如果冲突的次数不到m 获取m
已经为最大值或者修改当前bound的值失败，则通过增加一次collides以及循环递减下标i的值；否则更新当前bound的值成功：我们令i为m+1即为此时最大的下标。最后更新当前index的值。

Exchanger使用、原理都比较好理解，但是这个源码看起来真心有点儿复杂，是真心难看懂，但是这种交换的思路Doug
Lea在后续博文中还会提到，例如SynchronousQueue、LinkedTransferQueue。

最后用一个在网上看到的段子结束此篇博客（http://brokendreams.iteye.com/blog/2253956），博主对其做了一点点修改，以便更加符合在1.8环境下的Exchanger：

其实就是”我”和”你”(可能有多个”我”，多个”你”)在一个叫Slot的地方做交易(一手交钱，一手交货)，过程分以下步骤：

  1. 我先到一个叫做Slot的交易场所交易，发现你已经到了，那我就尝试喊你交易，如果你回应了我，决定和我交易那么进入第2步；如果别人抢先一步把你喊走了，那我就进入第5步。
  2. 我拿出钱交给你，你可能会接收我的钱，然后把货给我，交易结束；也可能嫌我掏钱太慢(超时)或者接个电话(中断)，TM的不卖了，走了，那我只能再找别人买货了(从头开始)。
  3. 我到交易地点的时候，你不在，那我先尝试把这个交易点给占了(一屁股做凳子上…)，如果我成功抢占了单间(交易点)，那就坐这儿等着你拿货来交易，进入第4步；如果被别人抢座了，那我只能在找别的地方儿了，进入第5步。
  4. 你拿着货来了，喊我交易，然后完成交易；也可能我等了好长时间你都没来，我不等了，继续找别人交易去，走的时候我看了一眼，一共没多少人，弄了这么多单间(交易地点Slot)，太TM浪费了，我喊来交易地点管理员：一共也没几个人，搞这么多单间儿干毛，给哥撤一个！。然后再找别人买货(从头开始)；或者我老大给我打了个电话，不让我买货了(中断)。
  5. 我跑去喊管理员，尼玛，就一个坑交易个毛啊，然后管理在一个更加开阔的地方开辟了好多个单间，然后我就挨个来看每个单间是否有人。如果有人我就问他是否可以交易，如果回应了我，那我就进入第2步。如果我没有人，那我就占着这个单间等其他人来交易，进入第4步。  
6.如果我尝试了几次都没有成功，我就会认为，是不是我TM选的这个单间风水不好？不行，得换个地儿继续(从头开始)；如果我尝试了多次发现还没有成功，怒了，把管理员喊来：给哥再开一个单间(Slot)，加一个凳子，这么多人就这么几个破凳子够谁用！

