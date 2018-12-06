##【Java并发编程实战】-----“J.U.C”：Condition

##
##在看Condition之前，我们先来看下面这个例子：  

##
##工厂类，用来存放、取出商品：     	public class Depot {    private int depotSize;     //仓库大小    private Lock lock;         //独占锁        public Depot(){        depotSize = 0;        lock = new ReentrantLock();    	}        /**     * 商品入库     * @param value     */    public void put(int value){        try {            lock.lock();            depotSize += value;            System.out.println(Thread.currentThread().getName() + " put " + value +" ----> the depotSize: " + depotSize);        	} finally{            lock.unlock();        	}    	}        /**     * 商品出库     * @param value     */    public void get(int value){        try {            lock.lock();            depotSize -= value;            System.out.println(Thread.currentThread().getName() + " get " + value +" ----> the depotSize: " + depotSize);        	} finally{            lock.unlock();        	}    	}	}

##
##生产者，生产商品，往仓库里面添加商品：  	public class Producer {    private Depot depot;        public Producer(Depot depot){        this.depot = depot;    	}        public void produce(final int value){        new Thread(){            public void run(){                depot.put(value);            	}        	}.start();    	}	}

##
##消费者，消费商品，从仓库里面取出商品：  	public class Customer {    private Depot depot;        public Customer(Depot depot){        this.depot = depot;    	}        public void consume(final int value){        new Thread(){            public void run(){                depot.get(value);            	}        	}.start();    	}	}

##
##测试类：  	public class Test {    public static void main(String[] args) {        Depot depot = new Depot();                Producer producer = new Producer(depot);        Customer customer = new Customer(depot);                producer.produce(10);        customer.consume(5);        producer.produce(20);        producer.produce(5);        customer.consume(35);    	}	}

##
##运行结果：  	Thread-0 put 10 ----> the depotSize: 10Thread-1 get 5 ----> the depotSize: 5Thread-2 put 20 ----> the depotSize: 25Thread-3 put 5 ----> the depotSize: 30Thread-4 get 35 ----> the depotSize: -5

##
##程序的运行结果是没有错误的，先put10、然后get5、put20、put5、get35。程序运行结果非常正确，但是在现实生活中，这个实例存在两处错误：

##
##第一：仓库的容量是有限的，我们不可能无限制的往仓库里面添加商品。

##
##第二：仓库的容量是不可能为负数的，但是最后的结果为-5，与现实存在冲突。

##
##针对于上面两处错误，怎么解决？这就轮到Condition大显神通了。
##Condition

##
##通过前面几篇博客我们知道Lock提供了比synchronized更加强大、灵活的锁机制，它从某种程度上来说替代了synchronized方式的使用。Condition从字面上面理解就是条件。对于线程而言它为线程提供了一个含义，以便在某种状态（条件Condition）可能为true的另一个线程通知它之前，一直挂起该线程。

##
##对于Condition，JDK API中是这样解释的：

##
##Condition 将 Object 监视器方法（wait、notify 和 notifyAll）分解成截然不同的对象，以便通过将这些对象与任意 Lock 实现组合使用，为每个对象提供多个等待 set（wait-set）。其中，Lock 替代了 synchronized 方法和语句的使用，Condition 替代了 Object 监视器方法的使用。 

##
##条件（也称为条件队列 或条件变量）为线程提供了一个含义，以便在某个状态条件现在可能为 true 的另一个线程通知它之前，一直挂起该线程（即让其“等待”）。因为访问此共享状态信息发生在不同的线程中，所以它必须受保护，因此要将某种形式的锁与该条件相关联。等待提供一个条件的主要属性是：以原子方式 释放相关的锁，并挂起当前线程，就像 Object.wait 做的那样。 

##
##Condition 实例实质上被绑定到一个锁上。要为特定 Lock 实例获得 Condition 实例，请使用其newCondition() 方法。下面我们通过Condition来解决上面的问题：这里只改仓库Depot的代码：  	public class Depot {    private int depotSize;     //仓库大小    private Lock lock;         //独占锁        private int capaity;       //仓库容量        private Condition fullCondition;            private Condition emptyCondition;        public Depot(){        this.depotSize = 0;        this.lock = new ReentrantLock();        this.capaity = 15;        this.fullCondition = lock.newCondition();        this.emptyCondition = lock.newCondition();    	}        /**     * 商品入库     * @param value     */    public void put(int value){        lock.lock();        try {            int left = value;            while(left > 0){                //库存已满时，“生产者”等待“消费者”消费                while(depotSize >= capaity){                    fullCondition.await();                	}                //获取实际入库数量：预计库存（仓库现有库存 + 生产数量） > 仓库容量   ? 仓库容量 - 仓库现有库存     :    生产数量                //                  depotSize   left   capaity  capaity - depotSize     left                int inc = depotSize + left > capaity ? capaity - depotSize : left;                 depotSize += inc;                left -= inc;                System.out.println(Thread.currentThread().getName() + "----要入库数量: " + value +";;实际入库数量：" + inc + ";;仓库货物数量：" + depotSize + ";;没有入库数量：" + left);                            //通知消费者可以消费了                emptyCondition.signal();            	}        	} catch (InterruptedException e) {        	} finally{            lock.unlock();        	}    	}        /**     * 商品出库     * @param value     */    public void get(int value){        lock.lock();        try {            int left = value;            while(left > 0){                //仓库已空，“消费者”等待“生产者”生产货物                while(depotSize <= 0){                    emptyCondition.await();                	}                //实际消费      仓库库存数量     < 要消费的数量     ?   仓库库存数量     : 要消费的数量                int dec = depotSize < left ? depotSize : left;                depotSize -= dec;                left -= dec;                System.out.println(Thread.currentThread().getName() + "----要消费的数量：" + value +";;实际消费的数量: " + dec + ";;仓库现存数量：" + depotSize + ";;有多少件商品没有消费：" + left);                            //通知生产者可以生产了                fullCondition.signal();            	}        	} catch (InterruptedException e) {            e.printStackTrace();        	} finally{            lock.unlock();        	}    	}	}

##
##test:  	public class Test {    public static void main(String[] args) {        Depot depot = new Depot();                Producer producer = new Producer(depot);        Customer customer = new Customer(depot);                producer.produce(10);        customer.consume(5);        producer.produce(15);        customer.consume(10);        customer.consume(15);        producer.produce(10);    	}	}

##
##运行结果：  	Thread-0----要入库数量: 10;;实际入库数量：10;;仓库货物数量：10;;没有入库数量：0Thread-1----要消费的数量：5;;实际消费的数量: 5;;仓库现存数量：5;;有多少件商品没有消费：0Thread-4----要消费的数量：15;;实际消费的数量: 5;;仓库现存数量：0;;有多少件商品没有消费：10Thread-2----要入库数量: 15;;实际入库数量：15;;仓库货物数量：15;;没有入库数量：0Thread-4----要消费的数量：15;;实际消费的数量: 10;;仓库现存数量：5;;有多少件商品没有消费：0Thread-5----要入库数量: 10;;实际入库数量：10;;仓库货物数量：15;;没有入库数量：0Thread-3----要消费的数量：10;;实际消费的数量: 10;;仓库现存数量：5;;有多少件商品没有消费：0

##
##在Condition中，用await()替换wait()，用signal()替换 notify()，用signalAll()替换notifyAll()，对于我们以前使用传统的Object方法，Condition都能够给予实现。