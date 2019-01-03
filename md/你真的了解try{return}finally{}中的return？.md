    *       * 0.0.1 验证 finally 语句是否会执行，以及 return 和 finally的执行顺序
  * 1 个人验证
    *       * 1.0.1 验证为什么是2不是3
    * 1.1 总结

今天去逛论坛 时发现了一个很有趣的[问题](http://bbs.csdn.net/topics/391005556)：

> 谁能给我我解释一下这段程序的结果为什么是：2.而不是：3

代码如下：

    
    
     class Test {
        public int aaa() {
            int x = 1;
    
            try {
                return ++x;
            } catch (Exception e) {
    
            } finally {
                ++x;
            }
            return x;
        }
    
        public static void main(String[] args) {
            Test t = new Test();
            int y = t.aaa();
            System.out.println(y);
        }
    }
    
    

* * *

看了问题后，得出了以下几个问题：

  * 如果在 **try** 语句块里使用 **return** 语句，那么 **finally** 语句块还会执行吗？（果你的答案是不会执行，请务必要看下去 ^_^）
  * 如果执行，那么是怎样实现既执行 **return** 又执行 **finally** 的呢？（如果你的答案是不知道，请继续看下去！！）
  * 上面的程序输出为什么是2？（ 如果不知道，继续看下去 ~~）~~
  * 在网上看到还有人还问“是先执行return还是先执行finally？”的  
（个人觉得，如果知道finally会执行就可以得出是，先执行finally再执行return的。因为，如果先执行return，那么整个函数都跳出了，那么还怎么执行finally？^_^）

刚看到这个问题后。突然发现基础不够扎实，居然来第一个都答不出来。。。（不知道还有木有和我也一样也回答不出以上的问题的？
如果有请在评论里告诉我一声，让我知道，我并不孤独 ~~）~~

> 根据已有的知识知道：  
>  **return**
是可以当作终止语句来用的，我们经常用它来跳出当前方法，并返回一个值给调用方法。然后该方法就结束了，不会执行return下面的语句。  
>  **finally** ：无论try语句发生了什么，无论抛出异常还是正常执行。finally语句都会执行。  
>
那么问题来了。。。。在try语句里使用return后，finally是否还会执行？finally一定会执行的说法是否还成立？如果成立，那么先执行return还是先执行finally？

####  验证 finally 语句是否会执行，以及 return 和 finally的执行顺序

在求知欲的驱动下，我继续进行更深的探索，果断打开了Oracle的主页，翻阅了[java
官方教程的finally语句](http://docs.oracle.com/javase/tutorial/essential/exceptions/finally.html)。发现了官方教程对这个特殊情况有说明：

The finally block always executes when the try block exits. This ensures that
the finally block is executed even if an unexpected exception occurs. But
finally is useful for more than just exception handling — it allows the
programmer to avoid having cleanup code accidentally bypassed by a return,
continue, or break. Putting cleanup code in a finally block is always a good
practice, even when no exceptions are anticipated.

> Note: If the JVM exits while the try or catch code is being executed, then
the finally block may not execute. Likewise, if the thread executing the try
or catch code is interrupted or killed, the finally block may not execute even
though the application as a whole continues.

个人简单翻译：

当try语句退出时肯定会执行finally语句。这确保了即使发了一个意想不到的异常也会执行finally语句块。但是finally的用处不仅是用来处理异常——它可以让程序员不会因为return、continue、或者break语句而忽略了清理代码。把清理代码放在finally语句块里是一个很好的做法，即便可能不会有异常发生也要这样做。

>
注意，当try或者catch的代码在运行的时候，JVM退出了。那么finally语句块就不会执行。同样，如果线程在运行try或者catch的代码时被中断了或者被杀死了(killed)，那么finally语句可能也不会执行了，即使整个运用还会继续执行。

从上面的官方说明，我们知道 **无论try里执行了return语句、break语句、还是continue语句，finally语句块还会继续执行**
。同时，在[stackoverflow](http://stackoverflow.com/questions/65035/does-finally-
always-execute-in-java/65185#65185)里也找到了一个答案，我们可以调用`System.exit()`来终止它：

finally will be called.  
The only time finally won’t be called is: if you call System.exit(), another
thread interrupts current one, or if the JVM crashes first.

另外，在[java的语言规范](http://docs.oracle.com/javase/specs/jls/se7/html/jls-14.html#jls-14.17)有讲到，如果在try语句里有return语句，finally语句还是会执行。它会在把控制权转移到该方法的调用者或者构造器前执行finally语句。也就是说，使用return语句把控制权转移给其他的方法前会执行finally语句。

## 个人验证

我们依然使用上面的代码作为例子。首先，分别在以下三行代码前加上断点：

  * _int x = 1;_
  * _return ++x;_
  * _++x;_

然后以debug模式运行代码。

刚开始时，效果如下图：

![201504010001](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010001.png)

按一下F6，我们可以发现，程序已经执行到 _return ++x;_ ,但还没执行该语句，此刻x=1

![201504010002](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010002.png)

继续按一下F6，程序执行到 _++x;_ ,但还没执行该语句，因此此时的x=2（刚执行完return ++x语句的++x，但没执行return）

![201504010003](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010003.png)

继续按一下F6，此时，我们发现程序又跳回到 _return +xx_ 这一行，此刻x=3(执行了finally语句里的++x)

![201504010004](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010004.png)

从上面过程中可以看到，

  * 在 **try** 里 使用 **return** 还是会执行finally语句的（我们用debug的模式看到了程序会条件 finally语句里执行）
  * 执行完finally语句才执行 return。为什么?从上面的图可以合理推理出return +xx;是分开来执行的，先执行++x，再执行finally，最后才执行return跳出函数。因为程序调两次跳到了 return +xx; 语句上。（其实要验证 _return ++x_ 是分开两部分执行的方法很简单，把变量x变成static变量并在main函数里输出，会发现x的值还是3，即使两次跳到 _return ++x_ 也只是第一次执行了加1操作，第二次只是执行了return而没有执行++x。这里是合理推理，后面有真凭实据 ~~）~~

看到这，我们可能会再次纠结起来了。从上面的验证可以看出，finally语句执行了，而且x的值也确实加到3了，那么为什么y是2呢？

#### 验证为什么是2不是3

翻看[官方的jvm规范](http://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html#jvms-4.10.2.5)就会把一切的谜团解开了：

> If the try clause executes a return, the compiled code does the following:

>

>   1. Saves the return value (if any) in a local variable.

>   2. Executes a jsr to the code for the finally clause.

>   3. Upon return from the finally clause, returns the value saved in the
local variable.

>

简单翻译下：

> 如果try语句里有return，那么代码的行为如下：  
>  1.如果有返回值，就把返回值保存到局部变量中  
>  2.执行jsr指令跳到finally语句里执行  
>  3.执行完finally语句后，返回之前保存在局部变量表里的值

根据上面的说明就可以轻易地解释为什么是2了。  
当执行到return ++x;时，jvm在执行完++x后会在局部变量表里另外分配一个空间来保存当前x的值。  
注意，现在还没把值返回给y，而是继续执行finally语句里的语句。等执行完后再把之前保存的值（是2不是x）返回给y。  
所以就有了y是2不是3的情况。

其实这里还有一点要注意的是，如果你在finally里也用了return语句，比如return
+xx。那么y会是3。因为规范规定了，当try和finally里都有return时，会忽略try的return，而使用finally的return。

查看Test.class的字节码我们同样也可以很轻松地知道为什么是2而不是3：

![201504010005](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010005.png)

大概讲讲指令操作顺序：  
iconst_1： 把常数1进栈 —> istore_1： 栈顶元素出栈并把元素保存在本地变量表的第二个位置里（下标为1的位置里） —> iinc 1, 1
： 本地变量表的第二个元素自增1 —>iload_1：第二个元素进栈 —> istore_2：栈顶元素出栈并把元素保存在本地变量表的第2个位置里 —>
iinc 1, 1 ： 本地变量表的第二个元素自增1 —> iload_2：第二个元素进栈 （注意，此时栈顶元素为2）—> ireturn：返回栈顶元素。

后面的指令是要在2-7行出现异常时在跳到12行的，这个例子没出现异常，不用关注。

上面流程栈和本地变量表的情况如下图：

![201504010006](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/201504010006.png)

### 总结

  * 再次发现帮助别人解决问题的好处，不仅能帮人还能完善自己
  * 字节码的知识还是挺实用的，有空要深入研究下
  * 再次证明官方教程和资料真的很有用

