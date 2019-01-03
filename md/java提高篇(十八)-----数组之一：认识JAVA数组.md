>
**噢，它明白了，河水既没有牛伯伯说的那么浅，也没有小松鼠说的那么深，只有自己亲自试过才知道！道听途说永远只能看到表明现象，只有亲自试过了，才知道它的深浅！！！！！**

## 一、什么是数组

数组？什么是数组？在我印象中的数组是应该这样的：通过new关键字创建并组装他们，通过使用整形索引值访问它的元素，并且它的尺寸是不可变的！

但是这只是数组的最表面的东西！深一点？就是这样：数组是一个简单的复合数据类型，它是一系列有序数据的集合，它当中的每一个数据都具有相同的数据类型，我们通过数组名加上一个不会越界下标值来唯一确定数组中的元素。

还有更深的，那就是数组是一个特殊的对象！！（对于这个LZ理解的不是很好，对JVM也没有看，所以见解有限）。以下参考文献：<http://developer.51cto.com/art/201001/176671.htm>、<http://www.blogjava.net/flysky19/articles/92763.html?opt=admin>

不管在其他语言中数组是什么，在java中它就是对象。一个比较特殊的对象。

    
    
     public class Test {
        public static void main(String[] args) {
            int[] array = new int[10];
            System.out.println("array的父类是：" + array.getClass().getSuperclass());
            System.out.println("array的类名是：" + array.getClass().getName());
        }
    }
    -------Output:
    array的父类是：class java.lang.Object
    array的类名是：[I

从上面示例可以看出,数组的是Object的直接子类,它属于“第一类对象”，但是它又与普通的java对象存在很大的不同，从它的类名就可以看出：[I，这是什么东东？？在JDK中我就没有找到这个类，话说这个"[I”都不是一个合法标识符。怎么定义成类啊？所以我认为SUM那帮天才肯定对数组的底层肯定做了特殊的处理。

我们再看如下示例：

    
    
    public class Test {
        public static void main(String[] args) {
            int[] array_00 = new int[10];
            System.out.println("一维数组：" + array_00.getClass().getName());
            int[][] array_01 = new int[10][10];
            System.out.println("二维数组：" + array_01.getClass().getName());
            
            int[][][] array_02 = new int[10][10][10];
            System.out.println("三维数组：" + array_02.getClass().getName());
        }
    }
    -----------------Output:
    一维数组：[I
    二维数组：[[I
    三维数组：[[[I

通过这个实例我们知道：[代表了数组的维度，一个[表示一维，两个[表示二维。可以简单的说数组的类名由若干个"["和数组元素类型的内部名称组成。不清楚我们再看：

    
    
    public class Test {
        public static void main(String[] args) {
            System.out.println("Object[]:" + Object[].class);
            System.out.println("Object[][]:" + Object[][].class);
            System.err.println("Object[][][]:" + Object[][][].class);
            System.out.println("Object:" + Object.class);
        }
    }
    ---------Output:
    Object[]:class [Ljava.lang.Object;
    Object[][]:class [[Ljava.lang.Object;
    Object[][][]:class [[[Ljava.lang.Object;
    Object:class java.lang.Object

从这个实例我们可以看出数组的“庐山真面目”。同时也可以看出数组和普通的Java类是不同的，普通的java类是以全限定路径名+类名来作为自己的唯一标示的，而数组则是以若干个[+L+数组元素类全限定路径+类来最为唯一标示的。这个不同也许在某种程度上说明了数组也普通java类在实现上存在很大的区别，也许可以利用这个区别来使得JVM在处理数组和普通java类时作出区分。

我们暂且不论这个[I是什么东东，是由谁来声明的，怎么声明的（这些我现在也不知道！但是有一点可以确认：这个是在运行时确定的）。先看如下：

    
    
    public class Test {
        public static void main(String[] args) {
            int[] array = new int[10];
            Class clazz = array.getClass();   
            System.out.println(clazz.getDeclaredFields().length);   
            System.out.println(clazz.getDeclaredMethods().length);   
            System.out.println(clazz.getDeclaredConstructors().length);   
            System.out.println(clazz.getDeclaredAnnotations().length);   
            System.out.println(clazz.getDeclaredClasses().length);   
        }
    }
    ----------------Output：
    0
    0
    0
    0
    0

从这个运行结果可以看出，我们亲爱的[I没有生命任何成员变量、成员方法、构造函数、Annotation甚至连length成员变量这个都没有，它就是一个彻彻底底的空类。没有声明length，那么我们array.length时，编译器怎么不会报错呢？确实，数组的length是一个非常特殊的成员变量。我们知道数组的是Object的直接之类，但是Object是没有length这个成员变量的，那么length应该是数组的成员变量，但是从上面的示例中，我们发现数组根本就没有任何成员变量，这两者不是相互矛盾么？

    
    
    public class Main {
        public static void main(String[] args) {
            int a[] = new int[2];
            int i = a.length;
        }
    }

打开class文件，得到main方法的字节码：

    
    
    0 iconst_2                   //将int型常量2压入操作数栈  
        1 newarray 10 (int)          //将2弹出操作数栈，作为长度，创建一个元素类型为int, 维度为1的数组，并将数组的引用压入操作数栈  
        3 astore_1                   //将数组的引用从操作数栈中弹出，保存在索引为1的局部变量(即a)中  
        4 aload_1                    //将索引为1的局部变量(即a)压入操作数栈  
        5 arraylength                //从操作数栈弹出数组引用(即a)，并获取其长度(JVM负责实现如何获取)，并将长度压入操作数栈  
        6 istore_2                   //将数组长度从操作数栈弹出，保存在索引为2的局部变量(即i)中  
        7 return                     //main方法返回

在这个字节码中我们还是没有看到length这个成员变量，但是看到了这个:arraylength
,这条指令是用来获取数组的长度的，所以说JVM对数组的长度做了特殊的处理，它是通过arraylength这条指令来实现的。

## 二、数组的使用方法

通过上面算是对数组是什么有了一个初步的认识，下面将简单介绍数组的使用方法。

数组的使用方法无非就是四个步骤：声明数组、分配空间、赋值、处理。

声明数组：就是告诉计算机数组的类型是什么。有两种形式：int[] array、int array[]。

分配空间：告诉计算机需要给该数组分配多少连续的空间，记住是连续的。array = new int[10];

赋值：赋值就是在已经分配的空间里面放入数据。array[0] = 1 、array[1] =
2……其实分配空间和赋值是一起进行的，也就是完成数组的初始化。有如下三种形式：

    
    
    int a[] = new int[2];    //默认为0,如果是引用数据类型就为null
            int b[] = new int[] {1,2,3,4,5};    
            int c[] = {1,2,3,4,5};

处理：就是对数组元素进行操作。通过数组名+有效的下标来确认数据。

**PS：**
由于能力有限，所以“什么是数组”主要是参考这篇博文：<http://developer.51cto.com/art/201001/176671.htm>。下篇将更多的介绍数组的一些特性，例如：效率问题、Array的使用、浅拷贝以及与list之间的转换问题。

