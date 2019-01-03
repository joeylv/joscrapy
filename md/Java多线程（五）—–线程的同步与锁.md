  * 1 一、同步问题提出
  * 2 二、同步和锁定
    * 2.1 1、锁的原理
  * 3 三、静态方法同步
  * 4 四、如果线程不能不能获得锁会怎么样
  * 5 五、何时需要同步
  * 6 六、线程安全类
  * 7 七、线程死锁
  * 8 八、线程同步小结

## 一、同步问题提出

线程的同步是为了防止多个线程访问一个数据对象时，对数据造成的破坏。

例如：两个线程ThreadA、ThreadB都操作同一个对象Foo对象，并修改Foo对象上的数据。

    
    
    public class Foo { 
        private int x = 100; 
    
        public int getX() { 
            return x; 
        } 
    
        public int fix(int y) { 
            x = x - y; 
            return x; 
        } 
    }
    
    
    public class MyRunnable implements Runnable { 
        private Foo foo = new Foo(); 
    
        public static void main(String[] args) { 
            MyRunnable r = new MyRunnable(); 
            Thread ta = new Thread(r, "Thread-A"); 
            Thread tb = new Thread(r, "Thread-B"); 
            ta.start(); 
            tb.start(); 
        } 
    
        public void run() { 
            for (int i = 0; i < 3; i++) { 
                this.fix(30); 
                try { 
                    Thread.sleep(1); 
                } catch (InterruptedException e) { 
                    e.printStackTrace(); 
                } 
                System.out.println(Thread.currentThread().getName() + " : 当前foo对象的x值= " + foo.getX()); 
            } 
        } 
    
        public int fix(int y) { 
            return foo.fix(y); 
        } 
    }

运行结果：

    
    
    Thread-A : 当前foo对象的x值= 40 
    Thread-B : 当前foo对象的x值= 40 
    Thread-B : 当前foo对象的x值= -20 
    Thread-A : 当前foo对象的x值= -50 
    Thread-A : 当前foo对象的x值= -80 
    Thread-B : 当前foo对象的x值= -80 
    
    Process finished with exit code 0

从结果发现，这样的输出值明显是不合理的。原因是两个线程不加控制的访问Foo对象并修改其数据所致。如果要保持结果的合理性，只需要达到一个目的，就是将对Foo的访问加以限制，每次只能有一个线程在访问。这样就能保证Foo对象中数据的合理性了。在具体的Java代码中需要完成一下两个操作：

把竞争访问的资源类Foo变量x标识为private；

同步哪些修改变量的代码，使用synchronized关键字同步方法或代码。

## 二、同步和锁定

### 1、锁的原理

Java中每个对象都有一个内置锁。当程序运行到非静态的synchronized同步方法上时，自动获得与正在执行代码类的当前实例（this实例）有关的锁。获得一个对象的锁也称为获取锁、锁定对象、在对象上锁定或在对象上同步。当程序运行到synchronized同步方法或代码块时才该对象锁才起作用。

一个对象只有一个锁。所以，如果一个线程获得该锁，就没有其他线程可以获得锁，直到第一个线程释放（或返回）锁。这也意味着任何其他线程都不能进入该对象上的synchronized方法或代码块，直到该锁被释放。释放锁是指持锁线程退出了synchronized同步方法或代码块。

关于锁和同步，有一下几个要点：

1）、只能同步方法，而不能同步变量和类；

2）、每个对象只有一个锁；当提到同步时，应该清楚在什么上同步？也就是说，在哪个对象上同步？

3）、不必同步类中所有的方法，类可以同时拥有同步和非同步方法。

4）、如果两个线程要执行一个类中的synchronized方法，并且两个线程使用相同的实例来调用方法，那么一次只能有一个线程能够执行方法，另一个需要等待，直到锁被释放。也就是说：如果一个线程在对象上获得一个锁，就没有任何其他线程可以进入（该对象的）类中的任何一个同步方法。

5）、如果线程拥有同步和非同步方法，则非同步方法可以被多个线程自由访问而不受锁的限制。

6）、线程睡眠时，它所持的任何锁都不会释放。

7）、线程可以获得多个锁。比如，在一个对象的同步方法里面调用另外一个对象的同步方法，则获取了两个对象的同步锁。

8）、同步损害并发性，应该尽可能缩小同步范围。同步不但可以同步整个方法，还可以同步方法中一部分代码块。

9）、在使用同步代码块时候，应该指定在哪个对象上同步，也就是说要获取哪个对象的锁。例如：

    
    
    public int fix(int y) {
            synchronized (this) {
                x = x - y;
            }
            return x;
        }

当然，同步方法也可以改写为非同步方法，但功能完全一样的，例如：

    
    
    public synchronized int getX() {
            return x++;
        }

与

    
    
    public int getX() {
            synchronized (this) {
                return x;
            }
        }

效果是完全一样的。

## 三、静态方法同步

要同步静态方法，需要一个用于整个类对象的锁，这个对象是就是这个类（XXX.class)。

例如：

    
    
    public static synchronized int setName(String name){
    
          Xxx.name = name;
    
    }

等价于

    
    
    public static int setName(String name){
          synchronized(Xxx.class){
                Xxx.name = name;
          }
    }

## 四、如果线程不能不能获得锁会怎么样

如果线程试图进入同步方法，而其锁已经被占用，则线程在该对象上被阻塞。实质上，线程进入该对象的的一种池中，必须在哪里等待，直到其锁被释放，该线程再次变为可运行或运行为止。

当考虑阻塞时，一定要注意哪个对象正被用于锁定：

1、调用同一个对象中非静态同步方法的线程将彼此阻塞。如果是不同对象，则每个线程有自己的对象的锁，线程间彼此互不干预。

2、调用同一个类中的静态同步方法的线程将彼此阻塞，它们都是锁定在相同的Class对象上。

3、静态同步方法和非静态同步方法将永远不会彼此阻塞，因为静态方法锁定在Class对象上，非静态方法锁定在该类的对象上。

4、对于同步代码块，要看清楚什么对象已经用于锁定（synchronized后面括号的内容）。在同一个对象上进行同步的线程将彼此阻塞，在不同对象上锁定的线程将永远不会彼此阻塞。

## 五、何时需要同步

在多个线程同时访问互斥（可交换）数据时，应该同步以保护数据，确保两个线程不会同时修改更改它。

对于非静态字段中可更改的数据，通常使用非静态方法访问。

对于静态字段中可更改的数据，通常使用静态方法访问。

如果需要在非静态方法中使用静态字段，或者在静态字段中调用非静态方法，问题将变得非常复杂。已经超出SJCP考试范围了。

## 六、线程安全类

当一个类已经很好的同步以保护它的数据时，这个类就称为“线程安全的”。即使是线程安全类，也应该特别小心，因为操作的线程是间仍然不一定安全。

举个形象的例子，比如一个集合是线程安全的，有两个线程在操作同一个集合对象，当第一个线程查询集合非空后，删除集合中所有元素的时候。第二个线程也来执行与第一个线程相同的操作，也许在第一个线程查询后，第二个线程也查询出集合非空，但是当第一个执行清除后，第二个再执行删除显然是不对的，因为此时集合已经为空了。看个代码：

    
    
    public class NameList { 
        private List nameList = Collections.synchronizedList(new LinkedList()); 
    
        public void add(String name) { 
            nameList.add(name); 
        } 
    
        public String removeFirst() { 
            if (nameList.size() > 0) { 
                return (String) nameList.remove(0); 
            } else { 
                return null; 
            } 
        } 
    }
    
    
    public class Test { 
        public static void main(String[] args) { 
            final NameList nl = new NameList(); 
            nl.add("aaa"); 
            class NameDropper extends Thread{ 
                public void run(){ 
                    String name = nl.removeFirst(); 
                    System.out.println(name); 
                } 
            } 
    
            Thread t1 = new NameDropper(); 
            Thread t2 = new NameDropper(); 
            t1.start(); 
            t2.start(); 
        } 
    }

虽然集合对象private List nameList = Collections.synchronizedList(new
LinkedList());是同步的，但是程序还不是线程安全的。出现这种事件的原因是，上例中一个线程操作列表过程中无法阻止另外一个线程对列表的其他操作。解决上面问题的办法是，在操作集合对象的NameList上面做一个同步。改写后的代码如下：

    
    
    public class NameList { 
        private List nameList = Collections.synchronizedList(new LinkedList()); 
    
        public synchronized void add(String name) { 
            nameList.add(name); 
        } 
    
        public synchronized String removeFirst() { 
            if (nameList.size() > 0) { 
                return (String) nameList.remove(0); 
            } else { 
                return null; 
            } 
        } 
    }

这样，当一个线程访问其中一个同步方法时，其他线程只有等待。

## 七、线程死锁

死锁对Java程序来说，是很复杂的，也很难发现问题。当两个线程被阻塞，每个线程在等待另一个线程时就发生死锁。还是看一个比较直观的死锁例子：

    
    
    public class DeadlockRisk { 
        private static class Resource { 
            public int value; 
        } 
    
        private Resource resourceA = new Resource(); 
        private Resource resourceB = new Resource(); 
    
        public int read() { 
            synchronized (resourceA) { 
                synchronized (resourceB) { 
                    return resourceB.value + resourceA.value; 
                } 
            } 
        } 
    
        public void write(int a, int b) { 
            synchronized (resourceB) { 
                synchronized (resourceA) { 
                    resourceA.value = a; 
                    resourceB.value = b; 
                } 
            } 
        } 
    }

假设read()方法由一个线程启动，write()方法由另外一个线程启动。读线程将拥有resourceA锁，写线程将拥有resourceB锁，两者都坚持等待的话就出现死锁。实际上，上面这个例子发生死锁的概率很小。因为在代码内的某个点，CPU必须从读线程切换到写线程，所以，死锁基本上不能发生。

但是，无论代码中发生死锁的概率有多小，一旦发生死锁，程序就死掉。有一些设计方法能帮助避免死锁，包括始终按照预定义的顺序获取锁这一策略。已经超出SCJP的考试范围。

## 八、线程同步小结

1、线程同步的目的是为了保护多个线程反问一个资源时对资源的破坏。

2、线程同步方法是通过锁来实现，每个对象都有切仅有一个锁，这个锁与一个特定的对象关联，线程一旦获取了对象锁，其他访问该对象的线程就无法再访问该对象的其他同步方法。

3、对于静态同步方法，锁是针对这个类的，锁对象是该类的Class对象。静态和非静态方法的锁互不干预。一个线程获得锁，当在一个同步方法中访问另外对象上的同步方法时，会获取这两个对象锁。

4、对于同步，要时刻清醒在哪个对象上同步，这是关键。

5、编写线程安全的类，需要时刻注意对多个线程竞争访问资源的逻辑和安全做出正确的判断，对“原子”操作做出分析，并保证原子操作期间别的线程无法访问竞争资源。

6、当多个线程等待一个对象锁时，没有获取到锁的线程将发生阻塞。

7、死锁是线程间相互等待锁锁造成的，在实际中发生的概率非常的小。真让你写个死锁程序，不一定好使，呵呵。但是，一旦程序发生死锁，程序将死掉。

