##【Java基础】RTTI与反射之Java

##
##一、引言　

##
##　　很多时候我们的程序可能需要在运行时识别对象和类的信息，比如多态就是基于运行时环境进行动态判断实际引用的对象。在运行时识别对象和类的信息主要有两种方式：1.RTTI，具体是Class对象，它假定我们在编译时已经知道了所有类型。2.反射机制，运行我们在运行时发现和使用类的信息。

##
##二、RTTI

##
##　　RTTI（Run-Time Type Infomation），运行时类型信息。可以在运行时识别一个对象的类型。类型信息在运行时通过Class对象表示，Class对象包含与类有关的信息，可以使用Class对象来创建类的实例。

##
##　　每个类对应一个Class对象，这个Class对象放在.class文件中，当我们的程序中首次主动使用某类型时，会把该类型所对应的Class对象加载进内存，在这篇文章JVM之类加载器中阐述了哪些情况符合首次主动使用。

##
##　　既然RTTI和Class对象有莫大的关系，即有了Class对象，就可以进行很多操作，那么，我们如何获取到Class对象呢？有三种方法1. Class.forName("全限定名")；（其中，全限定名为包名+类名）。2. 类字面常量，如String.class，对应String类的Class对象。3.通过getClass()方法获取Class对象，如String str = "abc";str.getClass();。

##
##　　通过一个类对应的Class对象后，我们可以做什么？我们可以获取该类的父类、接口、创建该类的对象、该类的构造器、字段、方法等等。总之，威力相当大。

##
##　　下面我们通过一个例子来熟悉Class对象的各种用法。 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	package com.hust.grid.leesf.algorithms;import java.lang.reflect.Constructor;import java.lang.reflect.Method;interface SuperInterfaceA {	};interface SuperInterfaceB {	};class SuperC {    private String name;    public SuperC() {    	}    public SuperC(String name) {        this.name = name;    	}    @Override    public String toString() {        return name;    	}	}class Sub extends SuperC implements SuperInterfaceA, SuperInterfaceB {    private String name;    public Sub() {        super();    	}    public Sub(String name) {            super(name);        this.name = name;        	}        public String getName() {        return name;    	}	}public class Main {    public static Sub makeInstance(Class<?> clazz) {        Sub sub = null;        try {            sub = (Sub) clazz.newInstance();        	} catch (InstantiationException | IllegalAccessException e) {            e.printStackTrace();        	}        return sub;    	}    public static void printBasicInfo(Class<?> clazz) {        System.out.println("CanonicalName : " + clazz.getCanonicalName());        System.out.println("Name : " + clazz.getName());        System.out.println("Simple Name : " + clazz.getSimpleName());        System.out.println("SuperClass Name : "                + clazz.getSuperclass().getName());        Class<?>[] interfaces = clazz.getInterfaces();        for (Class<?> inter : interfaces) {            System.out.println("Interface SimpleName : "                    + inter.getSimpleName());        	}        Constructor<?>[] constructors = clazz.getConstructors();        for (Constructor<?> cons : constructors) {            System.out.println("Constructor Name : " + cons.getName()                    + " And Parameter Count : " + cons.getParameterCount());        	}        Method[] methods = clazz.getDeclaredMethods();        for (Method method : methods) {            System.out.println("Method Name : " + method.getName());        	}    	}    public static void main(String[] args) {        //Sub sub = new Sub();        //Class<?> clazz = sub.getClass();        Class<?> clazz = Sub.class;        Sub instance = makeInstance(clazz);        if (instance != null) {            System.out.println("make instance successful");        	} else {            System.out.println("make instance unsuccessful");        	}        printBasicInfo(clazz);    	}	}View Code

##
##　　运行结果：　 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	make instance successfulCanonicalName : com.hust.grid.leesf.algorithms.SubName : com.hust.grid.leesf.algorithms.SubSimple Name : SubSuperClass Name : com.hust.grid.leesf.algorithms.SuperCInterface SimpleName : SuperInterfaceAInterface SimpleName : SuperInterfaceBConstructor Name : com.hust.grid.leesf.algorithms.Sub And Parameter Count : 0Constructor Name : com.hust.grid.leesf.algorithms.Sub And Parameter Count : 1Method Name : getNameView Code

##
##　　说明：使用method1、method2、method3三种方法都可以获得Class对象，运行结果是等效的。但是三者还是有稍许的区别。区别是从类的初始化角度来看的。如Class.forName("全限定名")会导致类型的加载、链接、初始化过程，而.class则不会初始化该类。显然，getClass肯定是会初始化该类的，因为这个方法时依托于类的对象。

##
##　　下面我们通过一个例子比较.class和forName()两种方法的区别。 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	package com.hust.grid.leesf.algorithms;import java.util.Random;class Init1 {    static final int staticFinal1 = 1;    static final int staticFinal2 = Main.random.nextInt(100);    static {        System.out.println("init init1");    	}	}class Init2 {    static int staticNonFinal1 = 3;    static {        System.out.println("init init2");    	}	}class Init3 {    static int staticNonFinal1 = 5;    static {        System.out.println("init init3");    	}	}public class Main {    public static Random random = new Random(47);    public static void main(String[] args) {        Class<?> clazzClass = Init1.class;        System.out.println("after init init1 ref");        System.out.println(Init1.staticFinal1);        System.out.println(Init1.staticFinal2);                System.out.println(Init2.staticNonFinal1);        try {            Class<?> clazz1 = Class.forName("com.hust.grid.leesf.algorithms.Init3");            System.out.println("after init init3 ref");            System.out.println(Init3.staticNonFinal1);        	} catch (ClassNotFoundException e1) {            // TODO Auto-generated catch block            e1.printStackTrace();        	}    	}	}View Code

##
##　　运行结果： ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	after init init1 ref1init init158init init23init init3after init init3 ref5View Code

##
##　　说明：从结果也进一步验证了.class不会初始化类，而.forName()会初始化类。并且，对常量静态域的使用也不会导致类的初始化。

##
##三、反射

##
##　　与RTTI必须在编译器就知道所有类型不同，反射不必在编译期就知道所有的类型，它可以在运行过程中使用动态加载的类，而这个类不必在编译期就已经知道。反射主要由java.lang.reflect类库的Field、Method、Constructor类支持。这些类的对象都是JVM在运行时进行创建，用来表示未知的类。

##
##　　关于两者的区别更深刻表达如下：对于RTTI而言，编译器在编译时打开和检查.class文件；对于反射而言，.class文件在编译时是不可获取的，所以在运行时打开和检查.class文件。

##
##　　其实在的第一个例子中我们已经用到了Constructor、Method类，现在我们来更加具体的了解Constructor、Method、Field类。　　 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	package com.hust.grid.leesf.algorithms;import java.lang.reflect.Constructor;import java.lang.reflect.Field;import java.lang.reflect.InvocationTargetException;import java.lang.reflect.Method;import java.util.Scanner;class Human {	}class Girl extends Human {    private boolean beautiful;    private int height;    private String name;        public Girl() {    	}    public Girl(String name, int height, boolean beautiful) {        this.name = name;        this.height = height;        this.beautiful = beautiful;    	}    public boolean isBeautiful() {        return beautiful;    	}    public String toString() {        return "height = " + height + " name = " + name + " beautiful = " + beautiful;    	}        private void print() {        System.out.println("i am a private method");    	}	}class Boy extends Human {    private boolean handsome;    private int height;    private String name;    public Boy() {    	}    public Boy(String name, int height, boolean handsome) {        this.name = name;        this.height = height;        this.handsome = handsome;    	}    public boolean isHandsome() {        return handsome;    	}    public String toString() {        return "height = " + height + " name = " + name + " handsome = " + handsome;    	}    private void print() {        System.out.println("i am a private method");    	}	}public class Test {    public static void main(String[] args) throws NoSuchMethodException,            SecurityException, InstantiationException, IllegalAccessException,            IllegalArgumentException, InvocationTargetException,            NoSuchFieldException {        Scanner scanner = new Scanner(System.in);        String input = scanner.nextLine();        Human human = null;        String name = "leesf";        int height = 180;        boolean handsome = true;        boolean flag = false;        if ("boy".equals(input)) {            human = new Boy(name, height, handsome);            flag = true;        	} else {            human = new Girl("dyd", 168, true);        	}        scanner.close();        Class<?> clazz = human.getClass();        Constructor<?> constructor = clazz.getConstructor(String.class,                int.class, boolean.class);        Human human1 = (Human) constructor.newInstance("leesf_dyd", 175, true);        System.out.println(human1);        Method method = null;        if (flag) {            method = clazz.getMethod("isHandsome");        	} else {            method = clazz.getMethod("isBeautiful");        	}        System.out.println(method.invoke(human));        Method method2 = clazz.getDeclaredMethod("print");        method2.setAccessible(true);        method2.invoke(human);        Field field = clazz.getDeclaredField("height");        System.out.println(human);        field.setAccessible(true);        field.set(human, 200);        System.out.println(human);    	}	}View Code

##
##　　输入：boy

##
##　　运行结果：　 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	boyheight = 175 name = leesf_dyd handsome = truetruei am a private methodheight = 180 name = leesf handsome = trueheight = 200 name = leesf handsome = trueView Code

##
##　　说明：反射可以让我们创建一个类的实例、在类外部访问类的私有方法、私有字段。反射真的很强大~

##
##四、动态代理-反射的应用

##
##　　动态创建代理并且动态处理对所代理方法的调用。在动态代理上所做的所有调用都会被重定向到单一的调用处理器上。

##
##　　下面是动态代理的例子 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	import java.lang.reflect.InvocationHandler;import java.lang.reflect.Method;import java.lang.reflect.Proxy;interface Interface {    void doSomething();    void doSomethingElse(String str);	}class RealObject implements Interface {    @Override    public void doSomething() {        System.out.println("doSomething");    	}    @Override    public void doSomethingElse(String str) {        System.out.println("doSomething else " + str);    	}	}class DynamicProxyHandler implements InvocationHandler {    private Object proxied;    public DynamicProxyHandler(Object proxied) {        this.proxied = proxied;    	}    @Override    public Object invoke(Object proxy, Method method, Object[] args)            throws Throwable {        if (method.getName().startsWith("do")) {            System.out.println("call do*** methods");        	}        method.invoke(proxied, args);        return null;    	}	}public class DynamicProxy {    public static void main(String[] args) {        RealObject proxied = new RealObject();        proxied.doSomething();        proxied.doSomethingElse("leesf");        Interface proxy = (Interface) Proxy.newProxyInstance(Interface.class                .getClassLoader(), new Class[] { Interface.class 	},                new DynamicProxyHandler(proxied));        proxy.doSomething();        proxy.doSomethingElse("leesf");    	}	}View Code

##
##　　运行结果：　 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	doSomethingdoSomething else leesfcall do*** methodsdoSomethingcall do*** methodsdoSomething else leesfView Code

##
##　　说明：可以在invoke方法中进行过滤操作。过滤出以do开头的方法进行转发。

##
##五、总结

##
##　　RTTI和反射分析就到此为止，RTTI和反射确实很强大，可以帮助我们干很多事情，用对地方绝对威力无穷，谢谢各位园友的观看~

##
##　　