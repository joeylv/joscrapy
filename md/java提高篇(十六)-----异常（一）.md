> **Java的基本理念是“结构不佳的代码不能运行”！！！！！**

大成若缺，其用不弊。

大盈若冲，其用不穷。

在这个世界不可能存在完美的东西，不管完美的思维有多么缜密，细心，我们都不可能考虑所有的因素，这就是所谓的智者千虑必有一失。同样的道理，计算机的世界也是不完美的，异常情况随时都会发生，我们所需要做的就是避免那些能够避免的异常，处理那些不能避免的异常。这里我将记录如何利用异常还程序一个“完美世界”。

## 一、为什么要使用异常

首先我们可以明确一点就是异常的处理机制可以确保我们程序的健壮性，提高系统可用率。虽然我们不是特别喜欢看到它，但是我们不能不承认它的地位，作用。有异常就说明程序存在问题，有助于我们及时改正。在我们的程序设计当做，任何时候任何地方因为任何原因都有可能会出现异常，在没有异常机制的时候我们是这样处理的
：通过函数的返回值来判断是否发生了异常（这个返回值通常是已经约定好了的），调用该函数的程序负责检查并且分析返回值。虽然可以解决异常问题，但是这样做存在几个缺陷：

1、 容易混淆。如果约定返回值为-11111时表示出现异常，那么当程序最后的计算结果真的为-1111呢？

2、 代码可读性差。将异常处理代码和程序代码混淆在一起将会降低代码的可读性。

3、 由调用函数来分析异常，这要求程序员对库函数有很深的了解。

在OO中提供的异常处理机制是提供代码健壮的强有力的方式。使用异常机制它能够降低错误处理代码的复杂度，如果不使用异常，那么就必须检查特定的错误，并在程序中的许多地方去处理它，而如果使用异常，那就不必在方法调用处进行检查，因为异常机制将保证能够捕获这个错误，并且，只需在一个地方处理错误，即所谓的异常处理程序中。这种方式不仅节约代码，而且把“概述在正常执行过程中做什么事”的代码和“出了问题怎么办”的代码相分离。总之，与以前的错误处理方法相比，异常机制使代码的阅读、编写和调试工作更加井井有条。（摘自《Think
in java 》）。

在初学时，总是听老师说把有可能出错的地方记得加异常处理，刚刚开始还不明白，有时候还觉得只是多此一举，现在随着自己的不断深入，代码编写多了，渐渐明白了异常是非常重要的。

## 二、基本定义

在《Think in
java》中是这样定义异常的：异常情形是指阻止当前方法或者作用域继续执行的问题。在这里一定要明确一点：异常代码某种程度的错误，尽管Java有异常处理机制，但是我们不能以“正常”的眼光来看待异常，异常处理机制的原因就是告诉你：这里可能会或者已经产生了错误，您的程序出现了不正常的情况，可能会导致程序失败！

那么什么时候才会出现异常呢？只有在你当前的环境下程序无法正常运行下去，也就是说程序已经无法来正确解决问题了，这时它所就会从当前环境中跳出，并抛出异常。抛出异常后，它首先会做几件事。首先，它会使用new创建一个异常对象，然后在产生异常的位置终止程序，并且从当前环境中弹出对异常对象的引用，这时。异常处理机制就会接管程序，并开始寻找一个恰当的地方来继续执行程序，这个恰当的地方就是异常处理程序，它的任务就是将程序从错误状态恢复，以使程序要么换一种方法执行，要么继续执行下去。

总的来说异常处理机制就是当程序发生异常时，它强制终止程序运行，记录异常信息并将这些信息反馈给我们，由我们来确定是否处理异常。

## 三、异常体系

java为我们提供了非常完美的异常处理机制，使得我们可以更加专心于我们的程序，在使用异常之前我们需要了解它的体系结构：如下（该图摘自：[http://blog.csdn.net/zhangerqing/article/details/8248186](http://blog.csdn.net/zhangerqing/article/details/8248186
"http://blog.csdn.net/zhangerqing/article/details/8248186")）。

[![1354439580_6933](../md/img/chenssy/22185952-834d92bc2bfe498f9a33414cc7a2c8a4.png)](https://images0.cnblogs.com/blog/381060/201311/22185948-7b9c14a60cbc4772a96ff710e58d18cd.png)

从上面这幅图可以看出，Throwable是java语言中所有错误和异常的超类（万物即可抛）。它有两个子类：Error、Exception。

其中Error为错误，是程序无法处理的，如OutOfMemoryError、ThreadDeath等，出现这种情况你唯一能做的就是听之任之，交由JVM来处理，不过JVM在大多数情况下会选择终止线程。

而Exception是程序可以处理的异常。它又分为两种CheckedException（受捡异常），一种是UncheckedException（不受检异常）。其中CheckException发生在编译阶段，必须要使用try…catch（或者throws）否则编译不通过。而UncheckedException发生在运行期，具有不确定性，主要是由于程序的逻辑问题所引起的，难以排查，我们一般都需要纵观全局才能够发现这类的异常错误，所以在程序设计中我们需要认真考虑，好好写代码，尽量处理异常，即使产生了异常，也能尽量保证程序朝着有利方向发展。

所以：对于可恢复的条件使用被检查的异常（CheckedException），对于程序错误（言外之意不可恢复，大错已经酿成）使用运行时异常（RuntimeException）。

**java的异常类实在是太多了，产生的原因也千变万化，所以 下篇博文我将会整理，统计java中经常出现的异常，望各位关注！！**

## 四、异常使用

在网上看了这样一个搞笑的话：世界上最真情的相依，是你在try我在catch。无论你发神马脾气，我都默默承受，静静处理。对于初学者来说异常就是try…catch，（鄙人刚刚接触时也是这么认为的，碰到异常就是try…catch）。个人感觉try…catch确实是用的最多也是最实用的。

在异常中try快包含着可能出现异常的代码块，catch块捕获异常后对异常进行处理。先看如下实例：

    
    
    public class ExceptionTest {
        public static void main(String[] args) {
            String file = "D:\\exceptionTest.txt";
            FileReader reader;
            try {
                reader = new FileReader(file);
                Scanner in = new Scanner(reader);  
                String string = in.next();  
                System.out.println(string + "不知道我有幸能够执行到不.....");
            } catch (FileNotFoundException e) {
                e.printStackTrace();
                System.out.println("对不起,你执行不到...");
            }  
            finally{
                System.out.println("finally 在执行...");
            }
        }
    }

这是段非常简单的程序，用于读取D盘目录下的exceptionText.txt文件，同时读取其中的内容、输出。首先D盘没有该文件，运行程序结果如下：

    
    
    java.io.FileNotFoundException: D:\exceptionTest.txt (系统找不到指定的文件。)
        at java.io.FileInputStream.open(Native Method)
        at java.io.FileInputStream.<init>(FileInputStream.java:106)
        at java.io.FileInputStream.<init>(FileInputStream.java:66)
        at java.io.FileReader.<init>(FileReader.java:41)
        at com.test9.ExceptionTest.main(ExceptionTest.java:19)
    对不起,你执行不到...
    finally 在执行...

从这个结果我们可以看出这些：

1、当程序遇到异常时会终止程序的运行（即后面的代码不在执行），控制权交由异常处理机制处理。

2、catch捕捉异常后，执行里面的函数。

当我们在D盘目录下新建一个exceptionTest.txt文件后，运行程序结果如下：

    
    
    1111不知道我有幸能够执行到不.....
    finally 在执行...

11111是该文件中的内容。从这个运行结果可以得出这个结果：
**不论程序是否发生异常，finally代码块总是会执行。所以finally一般用来关闭资源。**

在这里我们在看如下程序：

    
    
    public class ExceptionTest {
        public static void main(String[] args) {
            int[] a = {1,2,3,4};
            System.out.println(a[4]);
            System.out.println("我执行了吗???");
        }
    }

程序运行结果：

    
    
    Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: 4
        at com.test9.ExceptionTest.main(ExceptionTest.java:14)

各位请注意这个异常信息和上面的异常信息错误，为了看得更加清楚，我将他们列在一起：

    
    
    java.io.FileNotFoundException: D:\exceptionTest.txt (系统找不到指定的文件。)
            Exception in thread "main" **java.lang.ArrayIndexOutOfBoundsException:** 4

在这里我们发现两个异常之间存在如下区别：第二个异常信息多了 Exception in thread
"main"，这显示了出现异常信息的位置。在这里可以得到如下结论：
**若程序中显示的声明了某个异常，则抛出异常时不会显示出处，若程序中没有显示的声明某个异常，当抛出异常时，系统会显示异常的出处。**

**
由于这篇博文会比较长，所以分两篇来介绍。下篇博文主要介绍Java异常的自定义异常、异常链、异常的使用误区、使用异常注意地方以及try…catch、throw、throws。望各位看客关注！！！！**

