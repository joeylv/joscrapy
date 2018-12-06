##java提高篇(四)-----理解java的三大特性之多态

##
## 面向对象编程有三大特性：封装、继承、多态。

##
## 封装隐藏了类的内部实现机制，可以在不影响使用的情况下改变类的内部结构，同时也保护了数据。对外界而已它的内部细节是隐藏的，暴露给外界的只是它的访问方法。

##
## 继承是为了重用父类代码。两个类若存在IS-A的关系就可以使用继承。，同时继承也为实现多态做了铺垫。那么什么是多态呢？多态的实现机制又是什么？请看我一一为你揭开：

##
## 所谓多态就是指程序中定义的引用变量所指向的具体类型和通过该引用变量发出的方法调用在编程时并不确定，而是在程序运行期间才确定，即一个引用变量倒底会指向哪个类的实例对象，该引用变量发出的方法调用到底是哪个类中实现的方法，必须在由程序运行期间才能决定。因为在程序运行时才确定具体的类，这样，不用修改源程序代码，就可以让引用变量绑定到各种不同的类实现上，从而导致该引用调用的具体方法随之改变，即不修改程序代码就可以改变程序运行时所绑定的具体代码，让程序可以选择多个运行状态，这就是多态性。

##
## 比如你是一个酒神，对酒情有独钟。某日回家发现桌上有几个杯子里面都装了白酒，从外面看我们是不可能知道这是些什么酒，只有喝了之后才能够猜出来是何种酒。你一喝，这是剑南春、再喝这是五粮液、再喝这是酒鬼酒….在这里我们可以描述成如下：

##
## 酒 a = 剑南春

##
## 酒 b = 五粮液

##
## 酒 c = 酒鬼酒

##
## …

##
## 这里所表现的的就是多态。剑南春、五粮液、酒鬼酒都是酒的子类，我们只是通过酒这一个父类就能够引用不同的子类，这就是多态——我们只有在运行的时候才会知道引用变量所指向的具体实例对象。

##
## 诚然，要理解多态我们就必须要明白什么是“向上转型”。在继承中我们简单介绍了向上转型，这里就在啰嗦下：在上面的喝酒例子中，酒（Win）是父类，剑南春（JNC）、五粮液（WLY）、酒鬼酒（JGJ）是子类。我们定义如下代码：

##
## JNC a = new JNC();

##
## 对于这个代码我们非常容易理解无非就是实例化了一个剑南春的对象嘛！但是这样呢？

##
## Wine a = new JNC();

##
## 在这里我们这样理解，这里定义了一个Wine 类型的a，它指向JNC对象实例。由于JNC是继承与Wine，所以JNC可以自动向上转型为Wine，所以a是可以指向JNC实例对象的。这样做存在一个非常大的好处，在继承中我们知道子类是父类的扩展，它可以提供比父类更加强大的功能，如果我们定义了一个指向子类的父类引用类型，那么它除了能够引用父类的共性外，还可以使用子类强大的功能。

##
## 但是向上转型存在一些缺憾，那就是它必定会导致一些方法和属性的丢失，而导致我们不能够获取它们。所以父类类型的引用可以调用父类中定义的所有属性和方法，对于只存在与子类中的方法和属性它就望尘莫及了---1。	public class Wine {    public void fun1(){        System.out.println("Wine 的Fun.....");        fun2();    	}        public void fun2(){        System.out.println("Wine 的Fun2...");    	}	}public class JNC extends Wine{    /**     * @desc 子类重载父类方法     *        父类中不存在该方法，向上转型后，父类是不能引用该方法的     * @param a     * @return void     */    public void fun1(String a){        System.out.println("JNC 的 Fun1...");        fun2();    	}        /**     * 子类重写父类方法     * 指向子类的父类引用调用fun2时，必定是调用该方法     */    public void fun2(){        System.out.println("JNC 的Fun2...");    	}	}public class Test {    public static void main(String[] args) {        Wine a = new JNC();        a.fun1();    	}	}-------------------------------------------------Output:Wine 的Fun.....JNC 的Fun2...

##
## 从程序的运行结果中我们发现，a.fun1()首先是运行父类Wine中的fun1().然后再运行子类JNC中的fun2()。

##
## 分析：在这个程序中子类JNC重载了父类Wine的方法fun1()，重写fun2()，而且重载后的fun1(String a)与 fun1()不是同一个方法，由于父类中没有该方法，向上转型后会丢失该方法，所以执行JNC的Wine类型引用是不能引用fun1(String a)方法。而子类JNC重写了fun2() ，那么指向JNC的Wine引用会调用JNC中fun2()方法。

##
## 所以对于多态我们可以总结如下：

##
## 指向子类的父类引用由于向上转型了，它只能访问父类中拥有的方法和属性，而对于子类中存在而父类中不存在的方法，该引用是不能使用的，尽管是重载该方法。若子类重写了父类中的某些方法，在调用该些方法的时候，必定是使用子类中定义的这些方法（动态连接、动态调用）。

##
## 对于面向对象而已，多态分为编译时多态和运行时多态。其中编辑时多态是静态的，主要是指方法的重载，它是根据参数列表的不同来区分不同的函数，通过编辑之后会变成两个不同的函数，在运行时谈不上多态。而运行时多态是动态的，它是通过动态绑定来实现的，也就是我们所说的多态性。
##多态的实现

##
## 2.1实现条件

##
## 在刚刚开始就提到了继承在为多态的实现做了准备。子类Child继承父类Father，我们可以编写一个指向子类的父类类型引用，该引用既可以处理父类Father对象，也可以处理子类Child对象，当相同的消息发送给子类或者父类对象时，该对象就会根据自己所属的引用而执行不同的行为，这就是多态。即多态性就是相同的消息使得不同的类做出不同的响应。

##
## Java实现多态有三个必要条件：继承、重写、向上转型。

##
## 继承：在多态中必须存在有继承关系的子类和父类。

##
## 重写：子类对父类中某些方法进行重新定义，在调用这些方法时就会调用子类的方法。

##
## 向上转型：在多态中需要将子类的引用赋给父类对象，只有这样该引用才能够具备技能调用父类的方法和子类的方法。

##
## 只有满足了上述三个条件，我们才能够在同一个继承结构中使用统一的逻辑实现代码处理不同的对象，从而达到执行不同的行为。

##
## 对于Java而言，它多态的实现机制遵循一个原则：当超类对象引用变量引用子类对象时，被引用对象的类型而不是引用变量的类型决定了调用谁的成员方法，但是这个被调用的方法必须是在超类中定义过的，也就是说被子类覆盖的方法。

##
## 2.2实现形式

##
## 在Java中有两种形式可以实现多态。继承和接口。

##
## 2.2.1、基于继承实现的多态

##
## 基于继承的实现机制主要表现在父类和继承该父类的一个或多个子类对某些方法的重写，多个子类对同一方法的重写可以表现出不同的行为。	public class Wine {    private String name;        public String getName() {        return name;    	}    public void setName(String name) {        this.name = name;    	}    public Wine(){    	}        public String drink(){        return "喝的是 " + getName();    	}        /**     * 重写toString()     */    public String toString(){        return null;    	}	}public class JNC extends Wine{    public JNC(){        setName("JNC");    	}        /**     * 重写父类方法，实现多态     */    public String drink(){        return "喝的是 " + getName();    	}        /**     * 重写toString()     */    public String toString(){        return "Wine : " + getName();    	}	}public class JGJ extends Wine{    public JGJ(){        setName("JGJ");    	}        /**     * 重写父类方法，实现多态     */    public String drink(){        return "喝的是 " + getName();    	}        /**     * 重写toString()     */    public String toString(){        return "Wine : " + getName();    	}	}public class Test {    public static void main(String[] args) {        //定义父类数组        Wine[] wines = new Wine[2];        //定义两个子类        JNC jnc = new JNC();        JGJ jgj = new JGJ();                //父类引用子类对象        wines[0] = jnc;        wines[1] = jgj;                for(int i = 0 ; i < 2 ; i++){            System.out.println(wines[i].toString() + "--" + wines[i].drink());        	}        System.out.println("-------------------------------");    	}	}OUTPUT:Wine : JNC--喝的是 JNCWine : JGJ--喝的是 JGJ-------------------------------

##
## 在上面的代码中JNC、JGJ继承Wine，并且重写了drink()、toString()方法，程序运行结果是调用子类中方法，输出JNC、JGJ的名称，这就是多态的表现。不同的对象可以执行相同的行为，但是他们都需要通过自己的实现方式来执行，这就要得益于向上转型了。

##
## 我们都知道所有的类都继承自超类Object，toString()方法也是Object中方法，当我们这样写时：	Object o = new JGJ();      System.out.println(o.toString());

##
##

##
## 输出的结果是Wine : JGJ。

##
## Object、Wine、JGJ三者继承链关系是：JGJ—>Wine—>Object。所以我们可以这样说：当子类重写父类的方法被调用时，只有对象继承链中的最末端的方法才会被调用。但是注意如果这样写：

##
##	Object o = new Wine();System.out.println(o.toString());

##
## 输出的结果应该是Null，因为JGJ并不存在于该对象继承链中。

##
## 所以基于继承实现的多态可以总结如下：对于引用子类的父类类型，在处理该引用时，它适用于继承该父类的所有子类，子类对象的不同，对方法的实现也就不同，执行相同动作产生的行为也就不同。

##
## 如果父类是抽象类，那么子类必须要实现父类中所有的抽象方法，这样该父类所有的子类一定存在统一的对外接口，但其内部的具体实现可以各异。这样我们就可以使用顶层类提供的统一接口来处理该层次的方法。

##
## 2.2.2、基于接口实现的多态

##
## 继承是通过重写父类的同一方法的几个不同子类来体现的，那么就可就是通过实现接口并覆盖接口中同一方法的几不同的类体现的。

##
## 在接口的多态中，指向接口的引用必须是指定这实现了该接口的一个类的实例程序，在运行时，根据对象引用的实际类型来执行对应的方法。

##
## 继承都是单继承，只能为一组相关的类提供一致的服务接口。但是接口可以是多继承多实现，它能够利用一组相关或者不相关的接口进行组合与扩充，能够对外提供一致的服务接口。所以它相对于继承来说有更好的灵活性。
##三、经典实例。

##
## 通过上面的讲述，可以说是对多态有了一定的了解。现在趁热打铁，看一个实例。该实例是有关多态的经典例子，摘自：http://blog.csdn.net/thinkGhoster/archive/2008/04/19/2307001.aspx。	public class A {    public String show(D obj) {        return ("A and D");    	}    public String show(A obj) {        return ("A and A");    	} 	}public class B extends A{    public String show(B obj){        return ("B and B");    	}        public String show(A obj){        return ("B and A");    	} 	}public class C extends B{	}public class D extends B{	}public class Test {    public static void main(String[] args) {        A a1 = new A();        A a2 = new B();        B b = new B();        C c = new C();        D d = new D();                System.out.println("1--" + a1.show(b));        System.out.println("2--" + a1.show(c));        System.out.println("3--" + a1.show(d));        System.out.println("4--" + a2.show(b));        System.out.println("5--" + a2.show(c));        System.out.println("6--" + a2.show(d));        System.out.println("7--" + b.show(b));        System.out.println("8--" + b.show(c));        System.out.println("9--" + b.show(d));          	}	}

##
## 运行结果：	1--A and A2--A and A3--A and D4--B and A5--B and A6--A and D7--B and B8--B and B9--A and D

##
## 在这里看结果1、2、3还好理解，从4开始就开始糊涂了，对于4来说为什么输出不是“B and B”呢？

##
## 首先我们先看一句话：当超类对象引用变量引用子类对象时，被引用对象的类型而不是引用变量的类型决定了调用谁的成员方法，但是这个被调用的方法必须是在超类中定义过的，也就是说被子类覆盖的方法。这句话对多态进行了一个概括。其实在继承链中对象方法的调用存在一个优先级：this.show(O)、super.show(O)、this.show((super)O)、super.show((super)O)。

##
## 分析：

##
##  从上面的程序中我们可以看出A、B、C、D存在如下关系。

##
## ![Alt text](../md/img/16192518-a6d0f673554a4b85b079c4227aefd9a9.png) 

##
## 首先我们分析5，a2.show(c)，a2是A类型的引用变量，所以this就代表了A，a2.show(c),它在A类中找发现没有找到，于是到A的超类中找(super)，由于A没有超类（Object除外），所以跳到第三级，也就是this.show((super)O)，C的超类有B、A，所以(super)O为B、A，this同样是A，这里在A中找到了show(A obj)，同时由于a2是B类的一个引用且B类重写了show(A obj)，因此最终会调用子类B类的show(A obj)方法，结果也就是B and A。

##
## 按照同样的方法我也可以确认其他的答案。

##
## 方法已经找到了但是我们这里还是存在一点疑问，我们还是来看这句话：当超类对象引用变量引用子类对象时，被引用对象的类型而不是引用变量的类型决定了调用谁的成员方法，但是这个被调用的方法必须是在超类中定义过的，也就是说被子类覆盖的方法。这我们用一个例子来说明这句话所代表的含义：a2.show(b)；

##
## 这里a2是引用变量，为A类型，它引用的是B对象，因此按照上面那句话的意思是说有B来决定调用谁的方法,所以a2.show(b)应该要调用B中的show(B obj)，产生的结果应该是“B and B”，但是为什么会与前面的运行结果产生差异呢？这里我们忽略了后面那句话“但是这儿被调用的方法必须是在超类中定义过的”，那么show(B obj)在A类中存在吗？根本就不存在！所以这句话在这里不适用？那么难道是这句话错误了？非也！其实这句话还隐含这这句话：它仍然要按照继承链中调用方法的优先级来确认。所以它才会在A类中找到show(A obj)，同时由于B重写了该方法所以才会调用B类中的方法，否则就会调用A类中的方法。

##
## 所以多态机制遵循的原则概括为：当超类对象引用变量引用子类对象时，被引用对象的类型而不是引用变量的类型决定了调用谁的成员方法，但是这个被调用的方法必须是在超类中定义过的，也就是说被子类覆盖的方法，但是它仍然要根据继承链中方法调用的优先级来确认方法，该优先级为：this.show(O)、super.show(O)、this.show((super)O)、super.show((super)O)。

##
## 参考资料：http://blog.csdn.net/thinkGhoster/archive/2008/04/19/2307001.aspx。

##
## 百度文库：http://wenku.baidu.com/view/73f66f92daef5ef7ba0d3c03.html

##
## 在这里面向对象的三大特性已经介绍完成，下一步继续是java基础部分—巩固基础，提高技术，不惧困难，攀登高峰！！！！！！

##
## 更多：

##
## java提高篇-----理解java的三大特性之封装

##
## java提高篇-----理解java的三大特性之继承

##
##

##
##看书和学习——是思想的经常营养，是思想的无穷发展。