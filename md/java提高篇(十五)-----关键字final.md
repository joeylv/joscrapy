##java提高篇(十五)-----关键字final

##
## 在程序设计中，我们有时可能希望某些数据是不能够改变的，这个时候final就有用武之地了。final是java的关键字，它所表示的是“这部分是无法修改的”。不想被改变的原因有两个：效率、设计。使用到final的有三种情况：数据、方法、类。
##一、 final数据

##
## 有时候数据的恒定不变是很有用的，它能够减轻系统运行时的负担。对于这些恒定不变的数据我可以叫做“常量”。“常量”主要应用与以下两个地方：

##
## 1、编译期常量，永远不可改变。

##
## 2、运行期初始化时，我们希望它不会被改变。

##
## 对于编译期常量，它在类加载的过程就已经完成了初始化，所以当类加载完成后是不可更改的，编译期可以将它代入到任何用到它的计算式中，也就是说可以在编译期执行计算式。当然对于编译期常量，只能使用基本类型，而且必须要在定义时进行初始化。

##
## 有些变量，我们希望它可以根据对象的不同而表现不同，但同时又不希望它被改变，这个时候我们就可以使用运行期常量。对于运行期常量，它既可是基本数据类型，也可是引用数据类型。基本数据类型不可变的是其内容，而引用数据类型不可变的是其引用，引用所指定的对象内容是可变的。	public class Person {    private String name;    Person(String name){        this.name = name;    	}        public String getName() {        return name;    	}    public void setName(String name) {        this.name = name;    	}	}public class FinalTest {    private final String final_01 = "chenssy";    //编译期常量，必须要进行初始化，且不可更改    private final String final_02;                //构造器常量，在实例化一个对象时被初始化        private static Random random = new Random();    private final int final_03 = random.nextInt(50);    //使用随机数来进行初始化        //引用    public final Person final_04 = new Person("chen_ssy");    //final指向引用数据类型        FinalTest(String final_02){        this.final_02 = final_02;    	}        public String toString(){        return "final_01 = " + final_01 +"   final_02 = " + final_02 + "   final_03 = " + final_03 +               "   final_04 = " + final_04.getName();    	}        public static void main(String[] args) {        System.out.println("------------第一次创建对象------------");        FinalTest final1 = new FinalTest("cm");        System.out.println(final1);        System.out.println("------------第二次创建对象------------");        FinalTest final2 = new FinalTest("zj");        System.out.println(final2);        System.out.println("------------修改引用对象--------------");        final2.final_04.setName("chenssy");        System.out.println(final2);    	}	}------------------Output:------------第一次创建对象------------final_01 = chenssy   final_02 = cm   final_03 = 34   final_04 = chen_ssy------------第二次创建对象------------final_01 = chenssy   final_02 = zj   final_03 = 46   final_04 = chen_ssy------------修改引用对象--------------final_01 = chenssy   final_02 = zj   final_03 = 46   final_04 = chenssy

##
## 这里只阐述一点就是：不要以为某些数据是final就可以在编译期知道其值，通过final_03我们就知道了，在这里是使用随机数其进行初始化，他要在运行期才能知道其值。
##二、 final方法

##
## 所有被final标注的方法都是不能被继承、更改的，所以对于final方法使用的第一个原因就是方法锁定，以防止任何子类来对它的修改。至于第二个原因就是效率问题，鄙人对这个效率问题理解的不是很清楚，在网上摘抄这段话：在java的早期实现中，如果将一个方法指明为final，就是同意编译器将针对该方法的所有调用都转为内嵌调用。当编译器发现一个final方法调用命令时，它会根据自己的谨慎判断，跳过插入程序代码这种正常的调用方式而执行方法调用机制（将参数压入栈，跳至方法代码处执行，然后跳回并清理栈中的参数，处理返回值），并且以方法体中的实际代码的副本来代替方法调用。这将消除方法调用的开销。当然，如果一个方法很大，你的程序代码会膨胀，因而可能看不到内嵌所带来的性能上的提高，因为所带来的性能会花费于方法内的时间量而被缩减。

##
## 对这段话理解我不是很懂就照搬了，那位java牛人可以解释解释下！！

##
## 父类的final方法是不能被子类所覆盖的，也就是说子类是不能够存在和父类一模一样的方法的。	public class Custom extends Person{    public void method1(){        System.out.println("Person"s  method1....");    	}    //    Cannot override the final method from person：子类不能覆盖父类的final方法//    public void method2(){//        System.out.println("Person"s method2...");//    	}	}
##三、 final类

##
## 如果某个类用final修改，表明该类是最终类，它不希望也不允许其他来继承它。在程序设计中处于安全或者其他原因，我们不允许该类存在任何变化，也不希望它有子类，这个时候就可以使用final来修饰该类了。

##
## 对于final修饰的类来说，它的成员变量可以为final，也可以为非final。如果定义为final，那么final数据的规则同样适合它。而它的方法则会自动的加上final，因为final类是无法被继承，所以这个是默认的。
##四、 final参数

##
## 在实际应用中，我们除了可以用final修饰成员变量、成员方法、类，还可以修饰参数、若某个参数被final修饰了，则代表了该参数是不可改变的。

##
## 如果在方法中我们修改了该参数，则编译器会提示你：The final local variable i cannot be assigned. It must be blank and not using a compound assignment。	public class Custom {    public void test(final int i){      //i++;     ---final参数不可改变        System.out.println(i);    	}        public void test(final Person p){     //p = new Person();    --final参数不可变     p.setName("chenssy");    	}	}

##
## 同final修饰参数在内部类中是非常有用的，在匿名内部类中，为了保持参数的一致性，若所在的方法的形参需要被内部类里面使用时，该形参必须为final。详情参看：http://www.cnblogs.com/chenssy/p/3390871.html。
##六、final与static

##
## final和static在一起使用就会发生神奇的化学反应，他们同时使用时即可修饰成员变量，也可修饰成员方法。

##
## 对于成员变量，该变量一旦赋值就不能改变，我们称它为“全局常量”。可以通过类名直接访问。

##
## 对于成员方法，则是不可继承和改变。可以通过类名直接访问。 

##
##

##
## 更多：

##
## java提高篇------关键字static：http://www.cnblogs.com/chenssy/p/3386721.html

##
##

##
##巩固基础，提高技术，不惧困难，攀登高峰！！！！！！