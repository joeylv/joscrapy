  * 1 从源码到字节码
  * 2 2.Java 虚拟机的基本结构及其内存分区
  * 3 类加载器加载 Student.class 到内存
  * 4 执行引擎找到 main()
  * 5 简单查看 Student.main() 的运行过程

> 作者：某人的喵星人  
>  原文：<https://www.cnblogs.com/dqrcsc/p/4671879.html>

简单说来，一个java程序的运行需要编辑源码、编译生成class文件、加载class文件、解释或编译运行class中的字节码指令。

下面有一段简单的java源码，通过它来看一下java程序的运行流程：

    
    
    class Person{
    
           private String name;
           private int age;
    
           public Person(int age, String name){
                  this.age = age;
                  this.name = name;
           }
    
           public void run(){
           }
    
    }
    
    
    interface IStudyable{
           public int study(int a, int b);
    }
    
    public class Student extends Person implements IStudyable{
           private static int cnt=5;
    
           static{
                cnt++;
           }
    
           private String sid;
    
           public Student(int age, String name, String sid){
                  super(age,name);
                  this.sid = sid;
           }
    
           public void run(){
                  System.out.println("run()...");
           }
    
           public int study(int a, int b){
                  int c = 10;
                  int d = 20;
                  return a+b*c-d;
           }
    
           public static int getCnt(){
                  return cnt;
           }
    
           public static void main(String[] args){
                  Student s = new Student(23,"dqrcsc","20150723");
                  s.study(5,6);
                  Student.getCnt();
                  s.run();
    
           }
    
    }
    

**1、编辑源码**

无论是使用记事本还是别的什么，编写上面的代码，然后保存到Student.java，我直接就放到桌面了

![201808191001](http://cmsblogs.qiniudn.com/201808191001.png)

**2.编译生成class字节码文件**

打开命令窗口，输入命令javac Student.java将该源码文件编译生成.class字节码文件。

![201808191002](http://cmsblogs.qiniudn.com/201808191002.png)

由于在源码文件中定义了两个类，一个接口，所以生成了3个.clsss文件：

![201808191003](http://cmsblogs.qiniudn.com/201808191003.png)

这样能在java虚拟机上运行的字节码文件就生成了

**启动java虚拟机运行字节码文件**

![201808191004](http://cmsblogs.qiniudn.com/201808191004.png)

在命令行中输入 `java Student` 这个命令，就启动了一个 java 虚拟机，然后加载 Student.class
字节码文件到内存，然后运行内存中的字节码指令了。

我们从编译到运行 java 程序，只输入了两个命令，甚至，如果使用集成开发环境，如 eclipse，只要 ctrl+s
保存就完成了增量编译，只需要按下一个按钮就运行了 java 程序。但是，在这些简单操作的背后还有一些操作……

![201808191005](http://cmsblogs.qiniudn.com/201808191005.png)

## 从源码到字节码

字节码文件，看似很微不足道的东西，却真正实现了 java 语言的跨平台。各种不同平台的虚拟机都统一使用这种相同的程序存储格式。更进一步说，jvm 运行的是
class 字节码文件，只要是这种格式的文件就行，所以，实际上 jvm 并不像我之前想象地那样与 java
语言紧紧地捆绑在一起。如果非常熟悉字节码的格式要求，可以使用二进制编辑器自己写一个符合要求的字节码文件，然后交给 jvm
去运行；或者把其他语言编写的源码编译成字节码文件，交给 jvm 去运行，只要是合法的字节码文件， jvm 都会正确地跑起来。所以，它还实现了跨语言……

通过 jClassLib 可以直接查看一个 .class 文件中的内容，也可以给 JDK 中的 javap 命令指定参数，来查看 .class
文件的相关信息：

`javap –v Student`

![201808191006](http://cmsblogs.qiniudn.com/201808191006.png)

好多输出，在命令行窗口查看不是太方便，可以输出重定向下：

`javap –v Student > Student.class.txt`

![201808191007](http://cmsblogs.qiniudn.com/201808191007.png)

桌面上多出了一个 `Student.class.txt` 文件，里面存放着便于阅读的Student.class文件中相关的信息

![201808191008](http://cmsblogs.qiniudn.com/201808191008.png)

里面的内容如下（部分）：

![201808191009](http://cmsblogs.qiniudn.com/201808191009.png)

部分 class 文件内容，从上面图中，可以看到这些信息来自于 Student.class ，编译自 Student.java ，编译器的主版本号是
52，也就是 jdk1.8，这个类是 public ，然后是存放类中常量的常量池，各个方法的字节码等，这里就不一一记录了。

**总之，我想说的就是字节码文件很简单很强大，它存放了这个类的各种信息：字段、方法、父类、实现的接口等各种信息。**

##  2.Java 虚拟机的基本结构及其内存分区

Java 虚拟机要运行字节码指令，就要先加载字节码文件，谁来加载，怎么加载，加载到哪里……谁来运行，怎么运行，同样也要考虑……

![2018081910010](http://cmsblogs.qiniudn.com/2018081910010.png)

上面是一个JVM的基本结构及内存分区的图，有点抽象，简单说明下：

JVM中把内存分为直接内存、方法区、Java栈、Java堆、本地方法栈、PC寄存器等。

  * **直接内存** ：就是原始的内存区
  * **方法区** ：用于存放类、接口的元数据信息，加载进来的字节码数据都存储在方法区
  * **Java栈** ：执行引擎运行字节码时的运行时内存区，采用栈帧的形式保存每个方法的调用运行数据
  * **本地方法栈** ：执行引擎调用本地方法时的运行时内存区
  * **Java堆** ：运行时数据区，各种对象一般都存储在堆上
  * **PC寄存器** ：功能如同CPU中的PC寄存器，指示要执行的字节码指令。

JVM的功能模块主要包括 **类加载器、执行引擎和垃圾回收系统** 。

## 类加载器加载 Student.class 到内存

  1. 类加载器会在指定的 classpath 中找到 Student.class 这个文件，然后读取字节流中的数据，将其存储在方法区中。
  2. 会根据 Student.class 的信息建立一个 Class 对象，这个对象比较特殊，一般也存放在方法区中，用于作为运行时访问 Student 类的各种数据的接口。
  3. 必要的验证工作，格式、语义等
  4. 为 Student 中的静态字段分配内存空间，也是在方法区中，并进行零初始化，即数字类型初始化为 0 ，boolean 初始化为 false，引用类型初始化为 null 等。在 Student.java 中只有一个静态字段： `private static int cnt=5; `此时，并不会执行赋值为5的操作，而是将其初始化为0。
  5. 由于已经加载到内存了，所以原来字节码文件中存放的部分方法、字段等的符号引用可以解析为其在内存中的直接引用了，而不一定非要等到真正运行时才进行解析。
  6. 在编译阶段，编译器收集所有的静态字段的赋值语句及静态代码块，并按语句出现的顺序拼接出一个类初始化方法 `<clinit>()`。此时，执行引擎会调用这个方法对静态字段进行代码中编写的初始化操作。

在 Student.java 中关于静态字段的赋值及静态代码块有两处：

    
    
    private static int cnt=5;
    static{
        cnt++;
    }
    

将按出现顺序拼接，形式如下：

    
    
    void <clinit>(){
        cnt = 5;
        cnt++;
    }
    

可以通过 jClassLib 这个工具看到生成的 `<clinit>()` 方法的字节码指令：

![2018081910011](http://cmsblogs.qiniudn.com/2018081910011.png)

  * iconst_5 ：指令把常数5入栈
  * putstatic #6：将栈顶的5赋值给 Student.cnt 这个静态字段
  * getstatic #6：获取Student.cnt这个静态字段的值，并将其放入栈顶
  * iconst_1：把常数1入栈
  * iadd：取出栈顶的两个整数，相加，结果入栈
  * putstatic #6：取出栈顶的整数，赋值给Student.cnt
  * return：从当前方法中返回，没有任何返回值。

从字节码来看，确实先后执行了 `cnt =5` 及 `cnt++` 这两行代码。

在这里有一点要注意的是，这里笼统的描述了下类的加载及初始化过程，但是，实际中，有可能只进行了类加载，而没有进行初始化工作，原因就是在程序中并没有访问到该类的字段及方法等。

此外，实际加载过程也会相对来说比较复杂，一个类加载之前要加载它的父类及其实现的接口：加载的过程可以通过java
–XX:+TraceClassLoading参数查看：

如：`java -XX:+TraceClassLoading Student`，信息太多，可以重定向下：

![2018081910012](http://cmsblogs.qiniudn.com/2018081910012.png)

查看输出的 loadClass.txt 文件：

![2018081910013](http://cmsblogs.qiniudn.com/2018081910013.png)

可以看到最先加载的是 Object.class 这个类，当然了，所有类的父类。

![2018081910014](http://cmsblogs.qiniudn.com/2018081910014.png)

直到第 390 行才看到自己定义的部分被加载，先是 Studen t实现的接口 IStudyable ，然后是其父类 Person ，然后才是
Student 自身，然后是一个启动类的加载，然后就是找到 main() 方法，执行了。

## 执行引擎找到 main()

要了解方法的运行，需要先稍微了解下 java 栈：

JVM 中通过 java
栈，保存方法调用运行的相关信息，每当调用一个方法，会根据该方法的在字节码中的信息为该方法创建栈帧，不同的方法，其栈帧的大小有所不同。栈帧中的内存空间还可以分为3块，分别存放不同的数据：

  * **局部变量表** ：存放该方法调用者所传入的参数，及在该方法的方法体中创建的局部变量。
  * **操作数栈** ：用于存放操作数及计算的中间结果等。
  * **其他栈帧信息** ：如返回地址、当前方法的引用等。

只有当前正在运行的方法的栈帧位于栈顶，当前方法返回，则当前方法对应的栈帧出栈，当前方法的调用者的栈帧变为栈顶；当前方法的方法体中若是调用了其他方法，则为被调用的方法创建栈帧，并将其压入栈顶。

![2018081910015](http://cmsblogs.qiniudn.com/2018081910015.png)

注意：局部变量表及操作数栈的最大深度在编译期间就已经确定了，存储在该方法字节码的Code属性中。

## 简单查看 Student.main() 的运行过程

简单看下main()方法：

    
    
    public static void main(String[] args){
        Student s = new Student(23,"dqrcsc","20150723");
        s.study(5,6);
        Student.getCnt();
        s.run();
    }
    

对应的字节码，两者对照着看起来更易于理解些：

![2018081910016](http://cmsblogs.qiniudn.com/2018081910016.png)

注意main()方法的这几个信息：

![2018081910017](http://cmsblogs.qiniudn.com/2018081910017.png)

  * **Mximum stack depth** ：指定当前方法即 main() 方法对应栈帧中的操作数栈的最大深度，当前值为5
  * **Maximum local variables** ：指定main()方法中局部变量表的大小，当前为2，及有两个slot用于存放方法的参数及局部变量。
  * **Code length** ：指定main()方法中代码的长度。

开始模拟main()中一条条字节码指令的运行：

创建栈帧：

![2018081910018](http://cmsblogs.qiniudn.com/2018081910018.png)

局部变量表长度为 2，slot0 存放参数 args ，slot1 存放局部变量 Student s，操作数栈最大深度为 5。

new #7 指令：在 java 堆中创建一个 Student 对象，并将其引用值放入栈顶。

![2018081910019](http://cmsblogs.qiniudn.com/2018081910019.png)

  * dup指令：复制栈顶的值，然后将复制的结果入栈。
  * bipush 23：将单字节常量值23入栈。
  * ldc #8：将#8这个常量池中的常量即”dqrcsc”取出，并入栈。
  * ldc #9：将#9这个常量池中的常量即”20150723”取出，并入栈。

![2018081910020](http://cmsblogs.qiniudn.com/2018081910020.png)

invokespecial #10：调用#10这个常量所代表的方法，即Student.()这个方法

`<init>()` 方法，是编译器将调用父类的 `<init>()`
的语句、构造代码块、实例字段赋值语句，以及自己编写的构造方法中的语句整合在一起生成的一个方法。保证调用父类的 `<init>()`
方法在最开头，自己编写的构造方法语句在最后，而构造代码块及实例字段赋值语句按出现的顺序按序整合到 `<init>()` 方法中。

![2018081910021](http://cmsblogs.qiniudn.com/2018081910021.png)

注意到 `Student.<init>()` 方法的最大操作数栈深度为 3，局部变量表大小为 4。

此时需注意：从 dup 到 ldc #9 这四条指令向栈中添加了4个数据，而Student.()方法刚好也需要4个参数：

    
    
    public Student(int age, String name, String sid){
        super(age,name);
        this.sid = sid;
    
    }
    

虽然定义中只显式地定义了传入3个参数，而实际上会隐含传入一个当前对象的引用作为第一个参数，所以四个参数依次为this，age，name，sid。

上面的4条指令刚好把这四个参数的值依次入栈，进行参数传递，然后调用了Student.()方法，会创建该方法的栈帧，并入栈。栈帧中的局部变量表的第0到4个slot分别保存着入栈的那四个参数值。

创建 `Studet.<init>()` 方法的栈帧：

![2018081910022](http://cmsblogs.qiniudn.com/2018081910022.png)

Student.()方法中的字节码指令：

![2018081910023](http://cmsblogs.qiniudn.com/2018081910023.png)

  * aload_0：将局部变量表slot0处的引用值入栈
  * aload_1：将局部变量表slot1处的int值入栈
  * aload_2：将局部变量表slot2处的引用值入栈

![2018081910024](http://cmsblogs.qiniudn.com/2018081910024.png)

  * invokespecial #1：调用Person.()方法，同调用Student.过程类似，创建栈帧，将三个参数的值存放到局部变量表等，这里就不画图了……

从Person.()返回之后，用于传参的栈顶的3个值被回收了。

  * aload_0：将slot0处的引用值入栈。
  * aload_3：将slot3处的引用值入栈。

![2018081910025](http://cmsblogs.qiniudn.com/2018081910025.png)

  * putfield #2：将当前栈顶的值”20150723”赋值给0x2222所引用对象的sid字段，然后栈中的两个值出栈。
  * return：返回调用方，即main()方法，当前方法栈帧出栈。

重新回到main()方法中，继续执行下面的字节码指令：

astore_1：将当前栈顶引用类型的值赋值给slot1处的局部变量，然后出栈。

![2018081910026](http://cmsblogs.qiniudn.com/2018081910026.png)

  * aload_1：slot1处的引用类型的值入栈
  * iconst_5：将常数5入栈，int型常数只有0-5有对应的iconst_x指令
  * bipush 6：将常数6入栈

![20180819100027](http://cmsblogs.qiniudn.com/20180819100027.png)

  * invokevirtual #11：调用虚方法study()，这个方法是重写的接口中的方法，需要动态分派，所以使用了invokevirtual指令。

创建study()方法的栈帧：

![2018081910028](http://cmsblogs.qiniudn.com/2018081910028.png)

最大栈深度3，局部变量表5  
![2018081911002](http://cmsblogs.qiniudn.com/2018081911002.png)

方法的java源码：

    
    
    public int study(int a, int b){
        int c = 10;
        int d = 20;
        return a+b*c-d;
    
    }
    

对应的字节码：  
![2018081911001](http://cmsblogs.qiniudn.com/2018081911001.png)

注意到这里，通过 jClassLib 工具查看的字节码指令有点问题，与源码有偏差……

改用通过命令 javap –v Student 查看 study() 的字节码指令：

![2018081910030](http://cmsblogs.qiniudn.com/2018081910030.png)

  * bipush 10：将10入栈
  * istore_3：将栈顶的10赋值给slot3处的int局部变量，即c，出栈。
  * bipush 20：将20入栈
  * istore 4：将栈顶的20付给slot4处的int局部变量，即d，出栈。

上面4条指令，完成对c和d的赋值工作。

iload_1、iload_2、iload_3这三条指令将slot1、slot2、slot3这三个局部变量入栈：

![2018081910031](http://cmsblogs.qiniudn.com/2018081910031.png)

  * imul：将栈顶的两个值出栈，相乘的结果入栈：

![2018081910032](http://cmsblogs.qiniudn.com/2018081910032.png)

  * iadd：将当前栈顶的两个值出栈，相加的结果入栈
  * iload 4：将slot4处的int型的局部变量入

![2018081910033](http://cmsblogs.qiniudn.com/2018081910033.png)

  * isub：将栈顶两个值出栈，相减结果入栈：
  * ireturn：将当前栈顶的值返回到调用方。

![2018081910034](http://cmsblogs.qiniudn.com/2018081910034.png)

重新回到main()方法中：

  * pop指令，将study()方法的返回值出栈
  * invokestatic #12 调用静态方法getCnt()不需要传任何参数
  * pop：getCnt()方法有返回值，将其出栈
  * aload_1：将slot1处的引用值入栈
  * invokevirtual #13：调用0x2222对象的run()方法，重写自父类的方法，需要动态分派，所以使用invokevirtual指令
  * return：main()返回，程序运行结束。

以上，就是一个简单程序运行的大致过程

