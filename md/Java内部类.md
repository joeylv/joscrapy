
    一: 内部类
        定义在类体部,方法体部,甚至比方法体更小的代码块内部的类(if 语句里面等)
        1.静态内部类（内部类中最简单的形式）
            1.声明在类体部，方法体外，并且使用static修饰的内部类
            2.访问特点可以类比静态变量和静态方法
            3.脱离外部类的实例独立创建
                在外部类的外部构建内部类的实例
                    new Outer.Inner();
                在外部类的内部构建内部类的实例
                    new Inner();
            4.静态内部类体部可以直接访问外部类中所有的静态成员，包含私有 
    例子1：  
    /**
     * @author gress
     *静态内部类
     */
    public class StaticInnerTest {
        public static void main(String[] args) {
     
            StaticOuter.StaticInner si = new StaticOuter.StaticInner();
            si.test2();
            //StaticOuter.StaticInner.test();
            System.out.println("si.b = "+si.b);
            System.out.println("si.a = "+si.a);
        //    System.out.println("StaticOuter.b  = "+StaticOuter.b);  这里报错
        }
     
    }
    class StaticOuter {
    private int a = 100;
    private static int b = 150;
    public static void test(){
        System.out.println("Outer static test ...");
    }
    public  void test2(){
        System.out.println("Outer instabce test ...");
    }    
    static class StaticInner {
            public  int a = 200;
            static int b =300;
            public static void test(){
                System.out.println("Inner static test ...");
            }
            public  void test2(){
                System.out.println("Inner instance test ...");
                StaticOuter.test();
                new StaticOuter().test2();
                System.out.println("StaticOuter.b  = "+StaticOuter.b);
            }    
    }
    }  
    
    
    
    例子2：  
    package three;
    
    public class StaticTest {  
        private static String name="abc";
        private String sex="男";
        
        static class Person{
            private String age = "18";//内部私有成员
            public String heigth = "180";//内部类公有成员
            public void display(){
                //System.out.println(sex);//报错，不能直接访问外部类的非静态成员
                System.out.println(name);//只能直接访问外部类的静态成员
                System.out.println(age);//访问本内部类成员。
            }  
        }
        
        public void testone(){
            Person person = new Person();
            person.display();
            //System.out.println(heigth);//报错，是因为不可以直接访问内部类私有成员
            //System.out.println(age);//报错，是因为不可以直接访问内部类公有成员
            System.out.println(person.age);//可以访问内部类的私有成员
            System.out.println(person.heigth);//可以访问内部类的公有成员
        } 
        
        public void testtwo(){
            StaticTest st = new StaticTest();
            System.out.println(name);
            System.out.println(sex);
            //System.out.println(age);//不可以直接访问内部类的成员
            //System.out.println(heigth);//不可以直接访问内部类的成员
        }
        
        public static void main(String[] args) { 
            //调用StaticTest
            StaticTest staticTest = new StaticTest();  
            staticTest.testone(); 
            staticTest.testtwo();
        }  
    }
    
    
    2.成员内部类(实例内部类)
            1.没有使用static修饰的内部类。
            2.在成员内部类中不允许出现静态变量和静态方法的声明。
                static只能用在静态常量的声明上。
            3.成员内部类中可以访问外部类中所有的成员(变量，方法)，包含私有成员，如果在内部类中定义有和外部类同名的实例变量，访问：
                OuterClass.this.outerMember;
            4.构建内部类的实例，要求必须外部类的实例先存在
                外部类的外部/外部类的静态方法：new Outer().new Inner();
                外部类的实例方法：
                    new Inner();
                    this.new Inner();
    
    
    package one;
    
    public class Outer{
        private static int outer_i = 1;
        private int k=20;
        public static void outer1(){
           //...
        }
        //成员内部类
        class Inner{
            int j=100;//内部类中外部类的实例变量可以共存
            int inner_i=1;
            void inner1(){
               System.out.println(outer_i);//外部类的变量如果和内部类的变量没有同名的，则可以直接用变量名访问外部类的变量
               System.out.println(j);//在内部类中访问内部类自己的变量直接用变量名
               System.out.println(this.j);//也可以在内部类中用"this.变量名"来访问内部类变量
               //访问外部类中与内部类同名的实例变量可用"外部类名.this.变量名"。
               System.out.println(k);//外部类的变量如果和内部类的变量没有同名的，则可以直接用变量名访问外部类的变量
               outer1();
            }
        }
        //外部类的非静态方法访问成员内部类
        public void outer2(){
           Inner inner = new Inner();
           inner.inner1();
        }
        //外部类的静态方法访问成员内部类，与在外部类外部访问成员内部类一样
        public static void outer3(){
           Outer out = new Outer();//step1 建立外部类对象
           Inner inner=out.new Inner();//step2 根据外部类对象建立内部类对象
           inner.inner1();//step3 访问内部类的方法
        }
        public static void main(String[] args){
            outer3();
        }
    }

不过要注意的是，当成员内部类拥有和外部类同名的成员变量或者方法时，会发生隐藏现象，即默认情况下访问的是成员内部类的成员。

如果要访问外部类的同名成员，需要以下面的形式进行访问：

`外部类.``this``.成员变量`

`外部类.``this``.成员方法`

``虽然成员内部类可以无条件地访问外部类的成员，而外部类想访问成员内部类的成员却不是这么随心所欲了。

在外部类中如果要访问成员内部类的成员，必须先创建一个成员内部类的对象，再通过指向这个对象的引用来访问

    
    
    3.局部内部类:
            1.定义在方法体，甚至比方法体更小的代码块中
            2.类比局部变量。
            3.局部内部类是所有内部类中最少使用的一种形式。
            4.局部内部类可以访问的外部类的成员根据所在方法体不同。
                如果在静态方法中：
                    可以访问外部类中所有静态成员，包含私有
                如果在实例方法中：
                    可以访问外部类中所有的成员，包含私有。
              局部内部类可以访问所在方法中定义的局部变量，但是要求局部变量必须使用final修饰。         
    例子1：  
    
    
    
    public class Outer {
    
        public void say(){
            System.out.println("关门说真话！");
        }
    }
    public class Test {
    
        public void ting(){
            class MiMi extends Outer{//定义一个局部的内部类，继承Outer方法
                //……
            }
            
            new MiMi().say();//调用局部内部类中继承的say方法
            
            System.out.println("别人都不知道");
        }
        
        public static void main(String[] args) {
            new Test().ting();
        }
    }
    
    
    例子2：  
    **
     * @author gress 局部内部类
     *
     */
    public class LocalInnerTest {
        private int a = 1;
        private static int b = 2;
        public void test() {
            final int c = 3;
            class LocalInner {
                public void add1() {
                    System.out.println("a= " + a);
                    System.out.println("b= " + b);
                    System.out.println("c= " + c);
                }
            }
            new LocalInner().add1();
        }
        static public void test2() {
            final int d = 5;
            class LocalInner2 {
                public void add1() {
                    // System.out.println("a= " + a);
                    System.out.println("b= " + b);
                    System.out.println("c= " + d);
                }
            }
            new LocalInner2().add1();
        }
        public static void main(String args[]) {
            // LocalInnerTest() lc = new LocalInnerTest();
            new LocalInnerTest().test2();
            new LocalInnerTest().test();
        }
    }
        4.匿名内部类
            1.没有名字的局部内部类。
            2.没有class,interface,implements,extends关键字
            3.没有构造器。
            4.一般隐式的继承某一个父类或者实现某一个接口
            5.吃货老师讲的一个很生动的例子
            /**
             * @author gress 匿名内部类,我只会使用一次的类
             * 假如我想吃一个泡面,但我不可能建一个厂,制造一个流水线,生产一包泡面之后就在也不去使用这个泡面厂了
             * 所以这里引申出匿名内部类 ,而我们建立的泡面厂就像这里构建的一个类Pencil 铅笔类一样
             */
    **
     * @author gress 匿名内部类,我只会使用一次的类
     * 
     * 就假如我想吃一个泡面,但我不可能建一个厂,制造一个流水线,生产一包泡面之后就在也不去使用这个泡面厂了
     * 所以这里引申出匿名内部类 ,而我们建立的泡面厂就像这里构建的一个类Pencil 铅笔类一样
     */
    interface Pen {
        public void write();
    }
     
    class  Pencil implements Pen {
        @Override
        public void write() {
            //铅笔 的工厂
        }
    } 
    class Person {
        public void user(Pen pen) {
            pen.write();
        }
    }
     
    public class AnyInnerTest {
        public static void main(String args[]) {
            Person guo = new Person();
            guo.user(new Pen() {
                @Override
                public void write() {
                    System.out.println("写子");
                }
            });
        }
     
    }  
    例子2：  
    
    
    
    package three;
    
    abstract class parent {
    
    public abstract void like();
    }
    
    public class Demo {
        public static void main(String[] args) {
            parent pt = new parent(){
                public void like(){
                    System.out.println("吃饭睡觉打豆豆。。。");
                }
            };
            pt.like();
        }
    }

内部类总结：

1.内部类作为外部类的一个特殊的成员来看待，因此它有类成员的封闭等级：private ,protected,默认(friendly),public
它有类成员的修饰符: static,final,abstract

2.非静态内部类nested inner
class,内部类隐含有一个外部类的指针this,因此，它可以访问外部类的一切资源（当然包括private）外部类访问内部类的成员，先要取得内部类的对象,并且取决于内部类成员的封装等级。非静态内部类不能包含任何static成员.

3.静态内部类：static inner class,不再包含外部类的this指针，并且在外部类装载时初始化. 静态内部类只能访问外部类static成员.
外部类访问静态内部类的成员：static成员：类名.成员；非static成员：对象.成员

4.对于方法中的内部类或块中内部类只能访问块中或方法中的final变量。

    
    
    二: abstract  只能单继承
        1.方法:抽象方法
          不能有方法体 
          抽象方法所在类一定是抽象类
          抽象方法存在就是被覆盖的,如果子类继承带有抽象方法的抽象类,必须对所以的抽象方法进行覆盖    
        2.类 :抽象类
          抽象类不能被实例化
          抽象类是对类的抽象,抽象所具有的共有特征和行为
          抽象类所存在的目的就是用来被继承,实现代码的复用
          抽象类可以有抽象方法也可以没有抽象方法,可以像普通的一个类具有成员变量和方法
          如果一个类继承抽象类,必须实现抽象父类的抽象方法,或者子类也是一个抽象方法
    三: interface  可以多实现(继承)
        1.接口是比抽象类还抽象的存在，接口是抽象类的极致抽象。
        2.接口中所有的方法都是public abstracht，接口中所有的变量都是public static final
        3.接口主要用来定义标准。
        4.接口可以多继承。一个类可以实现多个接口。
        5.接口的存在本身可以规避java不能多继承的操作特点。
        interface USBDevice{
        String type="USB";
            void driver();
        }
        
        class Mouse{
            select();
        }
        class USBMouse extends Mouse implements USBDevice{
    
        }
        
        class Computer{
            void use(USBDevice usb){
                usb.driver();
            }
        }

