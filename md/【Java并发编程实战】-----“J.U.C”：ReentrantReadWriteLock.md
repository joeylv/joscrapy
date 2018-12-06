##【Java并发编程实战】-----“J.U.C”：ReentrantReadWriteLock

##
##ReentrantLock实现了标准的互斥操作，也就是说在某一时刻只有有一个线程持有锁。ReentrantLock采用这种独占的保守锁直接，在一定程度上减低了吞吐量。在这种情况下任何的“读/读”、“读/写”、“写/写”操作都不能同时发生。然而在实际的场景中我们就会遇到这种情况：有些资源并发的访问中，它大部分时间都是执行读操作，写操作比较少，但是读操作并不影响数据的一致性，如果在进行读操作时采用独占的锁机制，这样势必会大大降低吞吐量。所以如果能够做到读写分离，那就非常完美了。  

##
##ReadWriteLock， 维护了一对相关的锁，一个用于只读操作，另一个用于写入操作。只要没有 writer，读取锁可以由多个 reader 线程同时保持。写入锁是独占的。对于ReadWriteLock而言，一个资源能够被多个读线程访问，或者被一个写线程访问，但是不能同时存在读写线程。也就是说读写锁使用的场合是一个共享资源被大量读取操作，而只有少量的写操作（修改数据）。如下：     	public interface ReadWriteLock {    Lock readLock();    Lock writeLock();	}

##
##ReadWriteLock为一个接口，他定义了两个方法readLock、writeLock，从方法名我们就可以看出这两个方法是干嘛用的。ReentrantReadWriteLock作为ReadWriteLock的实现类，在API文档中详细介绍了它的特性。

##
##(一) 公平性

##
## 1)、 非公平锁（默认） 这个和独占锁的非公平性一样，由于读线程之间没有锁竞争，所以读操作没有公平性和非公平性，写操作时，由于写操作可能立即获取到锁，所以会推迟一个或多个读操作或者写操作。因此非公平锁的吞吐量要高于公平锁。

##
## 2)、 公平锁 利用AQS的CLH队列，释放当前保持的锁（读锁或者写锁）时，优先为等待时间最长的那个写线程分配写入锁，当前前提是写线程的等待时间要比所有读线程的等待时间要长。同样一个线程持有写入锁或者有一个写线程已经在等待了，那么试图获取公平锁的（非重入）所有线程（包括读写线程）都将被阻塞，直到最先的写线程释放锁。如果读线程的等待时间比写线程的等待时间还有长，那么一旦上一个写线程释放锁，这一组读线程将获取锁。

##
##(二) 重入性

##
## 1)、 读写锁允许读线程和写线程按照请求锁的顺序重新获取读取锁或者写入锁。当然了只有写线程释放了锁，读线程才能获取重入锁。

##
## 2)、 写线程获取写入锁后可以再次获取读取锁，但是读线程获取读取锁后却不能获取写入锁。

##
## 3)、 另外读写锁最多支持65535个递归写入锁和65535个递归读取锁。(为何是65535后面介绍）

##
##(三) 锁降级

##
## 1)、 写线程获取写入锁后可以获取读取锁，然后释放写入锁，这样就从写入锁变成了读取锁，从而实现锁降级的特性。

##
##(四) 锁升级

##
## 1)、 读取锁是不能直接升级为写入锁的。因为获取一个写入锁需要释放所有读取锁，所以如果有两个读取锁视图获取写入锁而都不释放读取锁时就会发生死锁。

##
##(五) 锁获取中断

##
## 1)、 读取锁和写入锁都支持获取锁期间被中断。这个和独占锁一致。

##
##(六) 条件变量

##
## 1)、 写入锁提供了条件变量(Condition)的支持，这个和独占锁一致，但是读取锁却不允许获取条件变量，将得到一个UnsupportedOperationException异常。

##
##(七) 重入数

##
## 1)、 读取锁和写入锁的数量最大分别只能是65535（包括重入数）。

##
##(八) 监测

##
## 1)、 此类支持一些确定是保持锁还是争用锁的方法。这些方法设计用于监视系统状态，而不是同步控制。

##
##ReentrantReadWriteLock与ReentrantLock一样，其锁主体依然是Sync，它的读锁、写锁都是依靠Sync来实现的。所以ReentrantReadWriteLock实际上只有一个锁，只是在获取读取锁和写入锁的方式上不一 样而已，它的读写锁其实就是两个类：ReadLock、writeLock，这两个类都是lock实现。  	/** 读锁 */    private final ReentrantReadWriteLock.ReadLock readerLock;        /** 写锁 */    private final ReentrantReadWriteLock.WriteLock writerLock;            final Sync sync;    /** 使用默认（非公平）的排序属性创建一个新的 ReentrantReadWriteLock */    public ReentrantReadWriteLock() {        this(false);    	}    /** 使用给定的公平策略创建一个新的 ReentrantReadWriteLock */    public ReentrantReadWriteLock(boolean fair) {        sync = fair ? new FairSync() : new NonfairSync();        readerLock = new ReadLock(this);        writerLock = new WriteLock(this);    	}        /** 返回用于写入操作的锁 */    public ReentrantReadWriteLock.WriteLock writeLock() { return writerLock; 	}    /** 返回用于读取操作的锁 */    public ReentrantReadWriteLock.ReadLock  readLock()  { return readerLock; 	}        public static class WriteLock implements Lock, java.io.Serializable{        public void lock() {            //独占锁            sync.acquire(1);        	}        /**         * 省略其余源代码         */    	}        public static class ReadLock implements Lock, java.io.Serializable {        public void lock() {            //共享锁            sync.acquireShared(1);        	}        /**         * 省略其余源代码         */    	}

##
##从上面的源代码我们可以看到WriteLock就是一个独占锁，readLock是一个共享锁，他们内部都是使用AQS的acquire、release来进行操作的。但是还是存在一些区别的。关于独占锁、共享锁，请关注前面的博客：

##
##【Java并发编程实战】—–“J.U.C”：ReentrantLock之二lock方法分析

##
##【Java并发编程实战】—–“J.U.C”：ReentrantLock之三unlock方法分析

##
##【Java并发编程实战】-----“J.U.C”：Semaphore

##
##下面LZ就ReadLock、WriteLock的获取锁（lock）、释放锁（release）进行分析。
##WriteLocklock()

##
##   	public void lock() {        sync.acquire(1);    	}

##
##与ReentrantLock一样，调用AQS的acquire()：   	public final void acquire(int arg) {        if (!tryAcquire(arg) &amp;&amp;            acquireQueued(addWaiter(Node.EXCLUSIVE), arg))            selfInterrupt();    	}

##
##第一步，写锁调用tryAcquire方法，该方法与ReentrantLock中的tryAcquire方法略有不同：  	protected final boolean tryAcquire(int acquires) {        //当前线程        Thread current = Thread.currentThread();        //当前锁个数        int c = getState();        //写锁个数        int w = exclusiveCount(c);                //当前锁个数 != 0（是否已经有线程持有锁），线程重入        if (c != 0) {            //w == 0,表示写线程数为0            //或者独占锁不是当前线程，返回false            if (w == 0 || current != getExclusiveOwnerThread())                return false;                        //超出最大范围（65535）            if (w + exclusiveCount(acquires) > MAX_COUNT)                throw new Error("Maximum lock count exceeded");            //设置锁的线程数量            setState(c + acquires);            return true;        	}                //是否阻塞        if (writerShouldBlock() ||            !compareAndSetState(c, c + acquires))            return false;                //设置锁为当前线程所有        setExclusiveOwnerThread(current);        return true;    	}

##
##在tryAcquire()中有一个段代码

##
##int w = exclusiveCount(c);

##
##该段代码主要是获取线程的数量的，在前面的特性里面有讲过读取锁和写入锁的数量最大分别只能是65535（包括重入数）。为何是65535呢？在前面LZ也提到过独占锁ReentrantLock中有一个state，共享锁中也有一个state，其中独占锁中的state为0或者1如果有重入，则表示重入的次数，共享锁中表示的持有锁的数量。而在ReadWriteLock中则不同，由于ReadWriteLock中存在两个锁，他们之间有联系但是也有差异，所以需要有两个state来分别表示他们。于是ReentrantReadWriteLock就将state一分二位，高16位表示共享锁的数量，低16位表示独占锁的数量。2^16 – 1 = 65535。这就是前面提过的为什么读取锁和写入锁的数量最大分别只能是65535。  	·   static final int SHARED_SHIFT   = 16;    static final int SHARED_UNIT    = (1 << SHARED_SHIFT);    static final int MAX_COUNT      = (1 << SHARED_SHIFT) - 1;    static final int EXCLUSIVE_MASK = (1 << SHARED_SHIFT) - 1;        /** 返回共享锁持有线程的数量 **/    static int sharedCount(int c)    { return c >>> SHARED_SHIFT; 	}    /** 返回独占锁持有线程的数量 **/    static int exclusiveCount(int c) { return c &amp; EXCLUSIVE_MASK; 	}

##
##这段代码可以清晰表达计算写锁、读书持有线程的数量。

##
##在上段tryAcquire方法的源代码中，主要流程如下：

##
##1、首先获取c、w。然后判断是否已经有线程持有写锁（c != 0），如果持有，则线程进行重入。若w == 0（写入锁==0）或者 current != getExclusiveOwnerThread()（锁的持有者不是当前线程），则返回false。如果写入锁的数量超出最大范围（65535），则抛出error。

##
##2、如果当且写线程数为0（那么读线程也应该为0，因为上面已经处理c!=0的情况），并且当前线程需要阻塞那么就返回失败；如果通过CAS增加写线程数失败也返回失败。

##
##3、当c ==0或者c>0,w >0,则设置锁的持有则为当前线程。unlock()  	public void unlock() {            sync.release(1);        	}

##
##unlock()调用Sync的release()：  	public final boolean release(int arg) {        if (tryRelease(arg)) {            Node h = head;            if (h != null &amp;&amp; h.waitStatus != 0)                unparkSuccessor(h);            return true;        	}        return false;    	}

##
##在release()中首先调用tryRelease方法进行尝试释放锁：  	protected final boolean tryRelease(int releases) {        //若锁的持有者不是当前线程，抛出异常        if (!isHeldExclusively())            throw new IllegalMonitorStateException();        //写锁的新线程数        int nextc = getState() - releases;        //若写锁的新线程数为0，则将锁的持有者设置为null        boolean free = exclusiveCount(nextc) == 0;        if (free)            setExclusiveOwnerThread(null);        //设置写锁的新线程数        setState(nextc);        return free;    	}

##
##写锁的释放过程还是相对而言比较简单的：首先查看当前线程是否为写锁的持有者，如果不是抛出异常。然后检查释放后写锁的线程数是否为0，如果为0则表示写锁空闲了，释放锁资源将锁的持有线程设置为null，否则释放仅仅只是一次重入锁而已，并不能将写锁的线程清空。

##
##由于写锁与独占锁存在很大的相似之处，所以相同的地方，LZ不再阐述，更多请查阅：

##
##【Java并发编程实战】—–“J.U.C”：ReentrantLock之二lock方法分析

##
##【Java并发编程实战】—–“J.U.C”：ReentrantLock之三unlock方法分析
##ReadLocklock()

##
##读锁的内在机制就是共享锁：  	public void lock() {            sync.acquireShared(1);        	}

##
##lock方法内部调用Sync的acquireShared()：  	public final void acquireShared(int arg) {        if (tryAcquireShared(arg) < 0)            doAcquireShared(arg);    	}

##
##对于tryAquireShared():  	protected final int tryAcquireShared(int unused) {        Thread current = Thread.currentThread();        //锁的持有线程数        int c = getState();        /*         * 如果写锁线程数 != 0 ，且独占锁不是当前线程则返回失败，因为存在锁降级         */        if (exclusiveCount(c) != 0 &amp;&amp;            getExclusiveOwnerThread() != current)            return -1;        //读锁线程数        int r = sharedCount(c);        /*         * readerShouldBlock():读锁是否需要等待（公平锁原则）         * r < MAX_COUNT：持有线程小于最大数（65535）         * compareAndSetState(c, c + SHARED_UNIT)：设置读取锁状态         */        if (!readerShouldBlock() &amp;&amp; r < MAX_COUNT &amp;&amp;            compareAndSetState(c, c + SHARED_UNIT)) {            /*             * holdCount部分后面讲解             */            if (r == 0) {                firstReader = current;                firstReaderHoldCount = 1;            	} else if (firstReader == current) {                firstReaderHoldCount++;        //            	} else {                HoldCounter rh = cachedHoldCounter;                if (rh == null || rh.tid != current.getId())                    cachedHoldCounter = rh = readHolds.get();                else if (rh.count == 0)                    readHolds.set(rh);                rh.count++;            	}            return 1;        	}        return fullTryAcquireShared(current);    	}

##
##读锁获取锁的过程比写锁稍微复杂些：

##
##1、写锁的线程数C！=0且写锁的线程持有者不是当前线程，返回-1。因为存在锁降级，写线程获取写入锁后可以获取读取锁。

##
##2、依据公平性原则，判断读锁是否需要阻塞，读锁持有线程数小于最大值（65535），且设置锁状态成功，执行以下代码（对于HoldCounter下面再阐述），并返回1。如果不满足改条件，执行fullTryAcquireShared()：（HoldCounter部分后面讲解）  	final int fullTryAcquireShared(Thread current) {         HoldCounter rh = null;         for (;;) {             //锁的线程持有数             int c = getState();             //如果写锁的线程持有数 != 0 且锁的持有者不是当前线程，返回-1             if (exclusiveCount(c) != 0) {                 if (getExclusiveOwnerThread() != current)                     return -1;             	}              //若读锁需要阻塞             else if (readerShouldBlock()) {                 //若队列的头部是当前线程                 if (firstReader == current) {                 	}                  else {   //下面讲解                     if (rh == null) {                         rh = cachedHoldCounter;                         if (rh == null || rh.tid != current.getId()) {                             rh = readHolds.get();                             if (rh.count == 0)                                 readHolds.remove();                         	}                     	}                     if (rh.count == 0)                         return -1;                 	}             	}             //读锁的线程数到达最大值：65536，抛出异常             if (sharedCount(c) == MAX_COUNT)                 throw new Error("Maximum lock count exceeded");             //设置锁的状态成功             if (compareAndSetState(c, c + SHARED_UNIT)) {                 //                 if (sharedCount(c) == 0) {                     firstReader = current;                     firstReaderHoldCount = 1;                 	}//                 else if (firstReader == current) {                     firstReaderHoldCount++;                 	}//下面讲解                 else {                     if (rh == null)                         rh = cachedHoldCounter;                     if (rh == null || rh.tid != current.getId())                         rh = readHolds.get();                     else if (rh.count == 0)                         readHolds.set(rh);                     rh.count++;                     cachedHoldCounter = rh;                 	}                 return 1;             	}         	}     	}

##
##unlock()  	public  void unlock() {            sync.releaseShared(1);        	}

##
##unlock调用releaseShared()方法，releaseShared()是AQS中的方法，如下：  	public final boolean releaseShared(int arg) {        if (tryReleaseShared(arg)) {            doReleaseShared();            return true;        	}        return false;    	}

##
##tryReleaseShared是ReentrantReadWriteLock中的方法：  	protected final boolean tryReleaseShared(int unused) {        //当前线程        Thread current = Thread.currentThread();        /*         * HoldCounter部分后面阐述         */        if (firstReader == current) {            if (firstReaderHoldCount == 1)                firstReader = null;            else                firstReaderHoldCount--;        	} else {            HoldCounter rh = cachedHoldCounter;            if (rh == null || rh.tid != current.getId())                rh = readHolds.get();            int count = rh.count;            if (count <= 1) {                readHolds.remove();                if (count <= 0)                    throw unmatchedUnlockException();            	}            --rh.count;        	}        //不断循环，不断尝试CAS操作        for (;;) {            int c = getState();            int nextc = c - SHARED_UNIT;            if (compareAndSetState(c, nextc))                return nextc == 0;        	}    	}

##
##在这里同样忽略HoldCounter，其实在该方法中最关键的部分在于for(;;)部分，该部分其实就是一个不断尝试的CAS过程，直到修状态成功。

##
##在读锁的获取、释放过程中，总是会有一个对象存在着，同时该对象在获取线程获取读锁是+1，释放读锁时-1，该对象就是HoldCounter。HoldCounter

##
##要明白HoldCounter就要先明白读锁。前面提过读锁的内在实现机制就是共享锁，对于共享锁其实我们可以稍微的认为它不是一个锁的概念，它更加像一个计数器的概念。一次共享锁操作就相当于一次计数器的操作，获取共享锁计数器+1，释放共享锁计数器-1。只有当线程获取共享锁后才能对共享锁进行释放、重入操作。所以HoldCounter的作用就是当前线程持有共享锁的数量，这个数量必须要与线程绑定在一起，否则操作其他线程锁就会抛出异常。

##
##先看读锁获取锁的部分：  	if (r == 0) {        //r == 0，表示第一个读锁线程，第一个读锁firstRead是不会加入到readHolds中        firstReader = current;        firstReaderHoldCount = 1;    	} else if (firstReader == current) {    //第一个读锁线程重入        firstReaderHoldCount++;        	} else {    //非firstReader计数        HoldCounter rh = cachedHoldCounter;        //readHoldCounter缓存        //rh == null 或者 rh.tid != current.getId()，需要获取rh        if (rh == null || rh.tid != current.getId())                cachedHoldCounter = rh = readHolds.get();        else if (rh.count == 0)            readHolds.set(rh);        //加入到readHolds中        rh.count++;        //计数+1    	}

##
##这里为什么要搞一个firstRead、firstReaderHoldCount呢？而不是直接使用else那段代码？这是为了一个效率问题，firstReader是不会放入到readHolds中的，如果读锁仅有一个的情况下就会避免查找readHolds。可能就看这个代码还不是很理解HoldCounter。我们先看firstReader、firstReaderHoldCount的定义：  	private transient Thread firstReader = null;private transient int firstReaderHoldCount;

##
##这两个变量比较简单，一个表示线程，当然该线程是一个特殊的线程，一个是firstReader的重入计数。

##
##HoldCounter的定义：  	static final class HoldCounter {            int count = 0;            final long tid = Thread.currentThread().getId();        	}

##
##在HoldCounter中仅有count和tid两个变量，其中count代表着计数器，tid是线程的id。但是如果要将一个对象和线程绑定起来仅记录tid肯定不够的，而且HoldCounter根本不能起到绑定对象的作用，只是记录线程tid而已。

##
##诚然，在java中，我们知道如果要将一个线程和对象绑定在一起只有ThreadLocal才能实现。所以如下：  	static final class ThreadLocalHoldCounter            extends ThreadLocal<HoldCounter> {            public HoldCounter initialValue() {                return new HoldCounter();            	}        	}	ThreadLocalHoldCounter继承ThreadLocal，并且重写了initialValue方法。

##
##故而，HoldCounter应该就是绑定线程上的一个计数器，而ThradLocalHoldCounter则是线程绑定的ThreadLocal。从上面我们可以看到ThreadLocal将HoldCounter绑定到当前线程上，同时HoldCounter也持有线程Id，这样在释放锁的时候才能知道ReadWriteLock里面缓存的上一个读取线程（cachedHoldCounter）是否是当前线程。这样做的好处是可以减少ThreadLocal.get()的次数，因为这也是一个耗时操作。需要说明的是这样HoldCounter绑定线程id而不绑定线程对象的原因是避免HoldCounter和ThreadLocal互相绑定而GC难以释放它们（尽管GC能够智能的发现这种引用而回收它们，但是这需要一定的代价），所以其实这样做只是为了帮助GC快速回收对象而已（引自[1]）。
##示例  	public class Reader implements Runnable{        private PricesInfo pricesInfo;        public Reader(PricesInfo pricesInfo){        this.pricesInfo = pricesInfo;    	}    @Override    public void run() {        for (int i = 0; i < 10; i++) {            System.out.println(Thread.currentThread().getName() + "--Price 1:" + pricesInfo.getPrice1());            System.out.println(Thread.currentThread().getName() + "--Price 1:" + pricesInfo.getPrice2());        	}    	}	}

##
##Writer  	public class Writer implements Runnable{    private PricesInfo pricesInfo;    public Writer(PricesInfo pricesInfo){        this.pricesInfo = pricesInfo;    	}        @Override    public void run() {        for (int i=0; i<3; i++) {            System.out.printf("Writer: Attempt to modify the prices.\n");            pricesInfo.setPrices(Math.random()*10, Math.random()*8);            System.out.printf("Writer: Prices have been modified.\n");            try {                Thread.sleep(2);            	} catch (InterruptedException e) {                e.printStackTrace();            	}        	}            	}	}

##
##PriceInfo  	public class PricesInfo {    private double price1;    private double price2;        private ReadWriteLock  lock;        public PricesInfo(){        price1 = 1.0;        price2 = 2.0;                lock = new ReentrantReadWriteLock();    	}        public double getPrice1(){        lock.readLock().lock();        double value = price1;        lock.readLock().unlock();        return value;    	}        public double getPrice2(){        lock.readLock().lock();        double value = price2;        lock.readLock().unlock();        return value;    	}        public void setPrices(double price1, double price2){        lock.writeLock().lock();         this.price1 = price1;        this.price2 = price2;        lock.writeLock().unlock();    	}	}

##
##Test：  	public class Test {    public static void main(String[] args) {        PricesInfo pricesInfo = new PricesInfo();                Reader[] readers = new Reader[5];        Thread[] readerThread = new Thread[5];        for (int i=0; i<5; i++){            readers[i]=new Reader(pricesInfo);            readerThread[i]=new Thread(readers[i]);        	}                Writer writer=new Writer(pricesInfo);        Thread threadWriter=new Thread(writer);                for (int i=0; i<5; i++){            readerThread[i].start();        	}        threadWriter.start();    	}	}

##
##

##
##参考资料：

##
##1、Java多线程（十）之ReentrantReadWriteLock深入分析

##
##2、JUC 可重入 读写锁 ReentrantReadWriteLock