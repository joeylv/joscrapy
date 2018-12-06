##Java提高篇（三四）-----fail-fast机制

##
##在JDK的Collection中我们时常会看到类似于这样的话：

##
##例如，ArrayList:   

##
##注意，迭代器的快速失败行为无法得到保证，因为一般来说，不可能对是否出现不同步并发修改做出任何硬性保证。快速失败迭代器会尽最大努力抛出 ConcurrentModificationException。因此，为提高这类迭代器的正确性而编写一个依赖于此异常的程序是错误的做法：迭代器的快速失败行为应该仅用于检测 bug。 

##
##HashMap中：   

##
##注意，迭代器的快速失败行为不能得到保证，一般来说，存在非同步的并发修改时，不可能作出任何坚决的保证。快速失败迭代器尽最大努力抛出 ConcurrentModificationException。因此，编写依赖于此异常的程序的做法是错误的，正确做法是：迭代器的快速失败行为应该仅用于检测程序错误。 

##
##在这两段话中反复地提到”快速失败”。那么何为”快速失败”机制呢？

##
##“快速失败”也就是fail-fast，它是Java集合的一种错误检测机制。当多个线程对集合进行结构上的改变的操作时，有可能会产生fail-fast机制。记住是有可能，而不是一定。例如：假设存在两个线程（线程1、线程2），线程1通过Iterator在遍历集合A中的元素，在某个时候线程2修改了集合A的结构（是结构上面的修改，而不是简单的修改集合元素的内容），那么这个时候程序就会抛出 ConcurrentModificationException 异常，从而产生fail-fast机制。
##一、fail-fast示例   	public class FailFastTest {    private static List<Integer> list = new ArrayList<>();        /**     * @desc:线程one迭代list     * @Project:test     * @file:FailFastTest.java     * @Authro:chenssy     * @data:2014年7月26日     */    private static class threadOne extends Thread{        public void run() {            Iterator<Integer> iterator = list.iterator();            while(iterator.hasNext()){                int i = iterator.next();                System.out.println("ThreadOne 遍历:" + i);                try {                    Thread.sleep(10);                	} catch (InterruptedException e) {                    e.printStackTrace();                	}            	}        	}    	}        /**     * @desc:当i == 3时，修改list     * @Project:test     * @file:FailFastTest.java     * @Authro:chenssy     * @data:2014年7月26日     */    private static class threadTwo extends Thread{        public void run(){            int i = 0 ;             while(i < 6){                System.out.println("ThreadTwo run：" + i);                if(i == 3){                    list.remove(i);                	}                i++;            	}        	}    	}        public static void main(String[] args) {        for(int i = 0 ; i < 10;i++){            list.add(i);        	}        new threadOne().start();        new threadTwo().start();    	}	}

##
##运行结果：  	ThreadOne 遍历:0ThreadTwo run：0ThreadTwo run：1ThreadTwo run：2ThreadTwo run：3ThreadTwo run：4ThreadTwo run：5Exception in thread "Thread-0" java.util.ConcurrentModificationException    at java.util.ArrayList$Itr.checkForComodification(Unknown Source)    at java.util.ArrayList$Itr.next(Unknown Source)    at test.ArrayListTest$threadOne.run(ArrayListTest.java:23)
##二、fail-fast产生原因

##
##通过上面的示例和讲解，我初步知道fail-fast产生的原因就在于程序在对 collection 进行迭代时，某个线程对该 collection 在结构上对其做了修改，这时迭代器就会抛出 ConcurrentModificationException 异常信息，从而产生 fail-fast。

##
##要了解fail-fast机制，我们首先要对ConcurrentModificationException 异常有所了解。当方法检测到对象的并发修改，但不允许这种修改时就抛出该异常。同时需要注意的是，该异常不会始终指出对象已经由不同线程并发修改，如果单线程违反了规则，同样也有可能会抛出改异常。

##
##诚然，迭代器的快速失败行为无法得到保证，它不能保证一定会出现该错误，但是快速失败操作会尽最大努力抛出ConcurrentModificationException异常，所以因此，为提高此类操作的正确性而编写一个依赖于此异常的程序是错误的做法，正确做法是：ConcurrentModificationException 应该仅用于检测 bug。下面我将以ArrayList为例进一步分析fail-fast产生的原因。

##
##从前面我们知道fail-fast是在操作迭代器时产生的。现在我们来看看ArrayList中迭代器的源代码：  	private class Itr implements Iterator<E> {        int cursor;        int lastRet = -1;        int expectedModCount = ArrayList.this.modCount;        public boolean hasNext() {            return (this.cursor != ArrayList.this.size);        	}        public E next() {            checkForComodification();            /** 省略此处代码 */        	}        public void remove() {            if (this.lastRet < 0)                throw new IllegalStateException();            checkForComodification();            /** 省略此处代码 */        	}        final void checkForComodification() {            if (ArrayList.this.modCount == this.expectedModCount)                return;            throw new ConcurrentModificationException();        	}    	}

##
##从上面的源代码我们可以看出，迭代器在调用next()、remove()方法时都是调用checkForComodification()方法，该方法主要就是检测modCount == expectedModCount ? 若不等则抛出ConcurrentModificationException 异常，从而产生fail-fast机制。所以要弄清楚为什么会产生fail-fast机制我们就必须要用弄明白为什么modCount != expectedModCount ，他们的值在什么时候发生改变的。

##
##expectedModCount 是在Itr中定义的：int expectedModCount = ArrayList.this.modCount;所以他的值是不可能会修改的，所以会变的就是modCount。modCount是在 AbstractList 中定义的，为全局变量：  	protected transient int modCount = 0;

##
##那么他什么时候因为什么原因而发生改变呢？请看ArrayList的源码：  	    public boolean add(E paramE) {        ensureCapacityInternal(this.size + 1);        /** 省略此处代码 */    	}    private void ensureCapacityInternal(int paramInt) {        if (this.elementData == EMPTY_ELEMENTDATA)            paramInt = Math.max(10, paramInt);        ensureExplicitCapacity(paramInt);    	}        private void ensureExplicitCapacity(int paramInt) {        this.modCount += 1;    //修改modCount        /** 省略此处代码 */    	}       public boolean remove(Object paramObject) {        int i;        if (paramObject == null)            for (i = 0; i < this.size; ++i) {                if (this.elementData[i] != null)                    continue;                fastRemove(i);                return true;            	}        else            for (i = 0; i < this.size; ++i) {                if (!(paramObject.equals(this.elementData[i])))                    continue;                fastRemove(i);                return true;            	}        return false;    	}    private void fastRemove(int paramInt) {        this.modCount += 1;   //修改modCount        /** 省略此处代码 */    	}    public void clear() {        this.modCount += 1;    //修改modCount        /** 省略此处代码 */    	}

##
##从上面的源代码我们可以看出，ArrayList中无论add、remove、clear方法只要是涉及了改变ArrayList元素的个数的方法都会导致modCount的改变。所以我们这里可以初步判断由于expectedModCount 得值与modCount的改变不同步，导致两者之间不等从而产生fail-fast机制。知道产生fail-fast产生的根本原因了，我们可以有如下场景：

##
##有两个线程（线程A，线程B），其中线程A负责遍历list、线程B修改list。线程A在遍历list过程的某个时候（此时expectedModCount = modCount=N），线程启动，同时线程B增加一个元素，这是modCount的值发生改变（modCount + 1 = N + 1）。线程A继续遍历执行next方法时，通告checkForComodification方法发现expectedModCount = N ，而modCount = N + 1，两者不等，这时就抛出ConcurrentModificationException 异常，从而产生fail-fast机制。

##
##所以，直到这里我们已经完全了解了fail-fast产生的根本原因了。知道了原因就好找解决办法了。
##三、fail-fast解决办法

##
##通过前面的实例、源码分析，我想各位已经基本了解了fail-fast的机制，下面我就产生的原因提出解决方案。这里有两种解决方案：

##
##方案一：在遍历过程中所有涉及到改变modCount值得地方全部加上synchronized或者直接使用Collections.synchronizedList，这样就可以解决。但是不推荐，因为增删造成的同步锁可能会阻塞遍历操作。

##
##方案二：使用CopyOnWriteArrayList来替换ArrayList。推荐使用该方案。

##
##CopyOnWriteArrayList为何物？ArrayList 的一个线程安全的变体，其中所有可变操作（add、set 等等）都是通过对底层数组进行一次新的复制来实现的。 该类产生的开销比较大，但是在两种情况下，它非常适合使用。1：在不能或不想进行同步遍历，但又需要从并发线程中排除冲突时。2：当遍历操作的数量大大超过可变操作的数量时。遇到这两种情况使用CopyOnWriteArrayList来替代ArrayList再适合不过了。那么为什么CopyOnWriterArrayList可以替代ArrayList呢？

##
##第一、CopyOnWriterArrayList的无论是从数据结构、定义都和ArrayList一样。它和ArrayList一样，同样是实现List接口，底层使用数组实现。在方法上也包含add、remove、clear、iterator等方法。

##
##第二、CopyOnWriterArrayList根本就不会产生ConcurrentModificationException异常，也就是它使用迭代器完全不会产生fail-fast机制。请看：  	private static class COWIterator<E> implements ListIterator<E> {        /** 省略此处代码 */        public E next() {            if (!(hasNext()))                throw new NoSuchElementException();            return this.snapshot[(this.cursor++)];        	}        /** 省略此处代码 */    	}

##
##CopyOnWriterArrayList的方法根本就没有像ArrayList中使用checkForComodification方法来判断expectedModCount 与 modCount 是否相等。它为什么会这么做，凭什么可以这么做呢？我们以add方法为例：  	public boolean add(E paramE) {        ReentrantLock localReentrantLock = this.lock;        localReentrantLock.lock();        try {            Object[] arrayOfObject1 = getArray();            int i = arrayOfObject1.length;            Object[] arrayOfObject2 = Arrays.copyOf(arrayOfObject1, i + 1);            arrayOfObject2[i] = paramE;            setArray(arrayOfObject2);            int j = 1;            return j;        	} finally {            localReentrantLock.unlock();        	}    	}        final void setArray(Object[] paramArrayOfObject) {        this.array = paramArrayOfObject;    	}

##
##CopyOnWriterArrayList的add方法与ArrayList的add方法有一个最大的不同点就在于，下面三句代码：  	Object[] arrayOfObject2 = Arrays.copyOf(arrayOfObject1, i + 1);arrayOfObject2[i] = paramE;setArray(arrayOfObject2);

##
##就是这三句代码使得CopyOnWriterArrayList不会抛ConcurrentModificationException异常。他们所展现的魅力就在于copy原来的array，再在copy数组上进行add操作，这样做就完全不会影响COWIterator中的array了。

##
##所以CopyOnWriterArrayList所代表的核心概念就是：任何对array在结构上有所改变的操作（add、remove、clear等），CopyOnWriterArrayList都会copy现有的数据，再在copy的数据上修改，这样就不会影响COWIterator中的数据了，修改完成之后改变原有数据的引用即可。同时这样造成的代价就是产生大量的对象，同时数组的copy也是相当有损耗的。

###

##
###参考文档：http://www.cnblogs.com/skywang12345/p/3308762.html#a3

##
##

##
##-----原文出自:http://cmsblogs.com/?p=1220,请尊重作者辛勤劳动成果,转载说明出处.

##
##-----个人站点:http://cmsblogs.com