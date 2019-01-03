今天朋友问我String的内容是真的不可变吗？我肯定告诉他是的？因为在我的主观意识里String就是一个不可变的对象。于是他给我发了这段程序：

    
    
    public class StringTest {
        public static void main(String[] args) throws Exception {
            String a = "chenssy";
            System.out.println("a = " + a);
            Field a_ = String.class.getDeclaredField("value");
            a_.setAccessible(true);
            char[] value=(char[])a_.get(a);
            value[4]="_";   //修改a所指向的值
            System.out.println("a = " + a);
        }
    }

看到这个简单的程序，我笑了，你这不是从底层来修改String的值么？从这里来理解String的值肯定是可以改变的啦（我们应该始终相信String的不可变性）！接着他再给我一段程序：

    
    
    public class StringTest {
        public static void main(String[] args) throws Exception {
            String a = "chenssy";
            String b = "chenssy";
            String c = new String("chenssy");
            System.out.println("--------------修改前值-------------------");
            System.out.println("a = " + a);
            System.out.println("b = " + b);
            System.out.println("c = " + c);
            //修改String的值
            Field a_ = String.class.getDeclaredField("value");
            a_.setAccessible(true);
            char[] value=(char[])a_.get(a);
            value[4]="_";   //修改a所指向的值
            
            System.out.println("--------------修改后值-------------------");
            System.out.println("a = " + a);
            System.out.println("b = " + b);
            System.out.println("chenssy");
            System.out.println("c = " + c);
        }
    }

乍看这程序是异常的简单，无非就是赋值、改值、输出嘛！可能你现在就会毫不犹豫的说太简单了结果就是……。但是！！你的毫不犹豫会害死你，而且你的结果很可能错误。那么运行结果是什么呢？

    
    
    --------------修改前值-------------------
    a = chenssy
    b = chenssy
    c = chenssy
    --------------修改后值-------------------
    a = chen_sy
    b = chen_sy
    chen_sy
    c = chen_ssy

修改前值很容易理解，但是修改后值呢？是不是有点儿不理解呢？你可能会问：为什么System.out.println("chenssy");的结果会是chen_ssy，System.out.println("c
= " + c);也是chen_ssy呢？

要明白这个其实也比较简单，掌握一个知识点：字符串常量池。

我们知道字符串的分配和其他对象分配一样，是需要消耗高昂的时间和空间的，而且字符串我们使用的非常多。JVM为了提高性能和减少内存的开销，在实例化字符串的时候进行了一些优化：使用字符串常量池。每当我们创建字符串常量时，JVM会首先检查字符串常量池，如果该字符串已经存在常量池中，那么就直接返回常量池中的实例引用。如果字符串不存在常量池中，就会实例化该字符串并且将其放到常量池中。由于String字符串的不可变性我们可以十分肯定常量池中一定不存在两个相同的字符串（这点对理解上面至关重要）。

我们再来理解上面的程序。

String a = "chenssy";

String b = "chenssy";

a、b和字面上的chenssy都是指向JVM字符串常量池中的”chenssy”对象，他们指向同一个对象。

String c = new String("chenssy");

new关键字一定会产生一个对象chenssy（注意这个chenssy和上面的chenssy不同），同时这个对象是存储在堆中。所以上面应该产生了两个对象：保存在栈中的c和保存堆中chenssy。但是在Java中根本就不存在两个完全一模一样的字符串对象。故堆中的chenssy应该是引用字符串常量池中chenssy。所以c、chenssy、池chenssy的关系应该是：c--->chenssy--->池chenssy。整个关系如下：

[![201404271001](../md/img/chenssy/272149156708549.png)](https://images0.cnblogs.com/blog/381060/201404/272149150297421.png)

通过上面的图我们可以非常清晰的认识他们之间的关系。所以我们修改内存中的值，他变化的是所有。

**总结：** 虽然a、b、c、chenssy是不同的对象，但是从String的内部结构我们是可以理解上面的。String c = new
String("chenssy");虽然c的内容是创建在堆中，但是他的内部value还是指向JVM常量池的chenssy的value，它构造chenssy时所用的参数依然是chenssy字符串常量。

为了让各位充分理解常量池，特意准备了如下一个简单的题目：

    
    
    String a = "chen";
    String b = a + new String("ssy");

创建了几个String对象？？

