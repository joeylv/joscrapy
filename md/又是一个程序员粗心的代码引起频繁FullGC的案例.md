  * 1 重现问题
  * 2 CPU飙高
  * 3 揪出真凶
  * 4 解决问题

> 作者： 阿飞的博客  
>
[又是一个程序员粗心的代码引起频繁FullGC的案例](https://mp.weixin.qq.com/s?__biz=MzU5ODUwNzY1Nw==&mid=2247484100&idx=1&sn=3e584bd09732aab777e6b8cc12bcf388&chksm=fe426b22c935e234ff67ed18b007a4f0c65df4f2da1f8d2320b7f3da8579333d469fe5cddab6&mpshare=1&scene=1&srcid=1107Lbpeqr0jijvD2iCQweRJ#rd)

* * *

这是笨神JVMPocket群里一位名为” **云何*住** “的同学提出来的问题，问题现象是 **CPU飙高** 并且 **频繁FullGC** 。

## 重现问题

这位同学的业务代码比较复杂，为了简化业务场景，笔者将其代码压缩成如下的代码片段：

    
    
    public class FullGCDemo {
    
        private static ScheduledThreadPoolExecutor executor = new ScheduledThreadPoolExecutor(50,
                new ThreadPoolExecutor.DiscardOldestPolicy());
    
        public static void main(String[] args) throws Exception {
            executor.setMaximumPoolSize(50);
    
            // 模拟xxl-job 100ms 调用一次, 原代码没有这么频繁
            for (int i=0; i<Integer.MAX_VALUE; i++){
                buildBar();
                Thread.sleep(100);
            }
        }
    
        private static void buildBar(){
            List<FutureContract> futureContractList = getAllFutureContract();
            futureContractList.forEach(contract -> {
                // do something
                executor.scheduleWithFixedDelay(() -> {
                    try{
                        doFutureContract(contract);
                    }catch (Exception e){
                        e.printStackTrace();
                    }
                }, 2, 3, TimeUnit.SECONDS);
            });
        }
    
        private static void doFutureContract(FutureContract contract){
            // do something with futureContract
        }
    
        private static List<FutureContract> getAllFutureContract(){
            List<FutureContract> futureContractList = new ArrayList<>();
            // 问题代码这里每次只会new不到10个对象, 我这里new了100个是为了更快重现问题
            for (int i = 0; i < 100; i++) {
                FutureContract contract = new FutureContract(i, ... ...);
                futureContractList.add(contract);
            }
            return futureContractList;
        }
    }
    

说明，为了更好的还原问题， **FutureContract.java** 的定义建议尽量与问题代码保持一致：

  * 16个BigDecimal类型属性
  * 3个Long类型属性
  * 3个String类型属性
  * 4个Integer类型属性
  * 2个Date类型属性

问题代码运行时的JVM参数如下（JDK8）：

    
    
    java -Xmx256m -Xms256m -Xmn64m FullGCDemo
    

你也可以先自己独立思考一下这块代码问题何在。

## CPU飙高

这是第一个现象，top命令就能看到，找到我们的进程ID，例如91782。然后执行命令`top -H -p 91782`查看进程里的线程情况：

    
    
    PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND                                                     
    91784 yyapp     20   0 2670m 300m  12m R 92.2  7.8   4:14.39 java                                                         
    91785 yyapp     20   0 2670m 300m  12m R 91.9  7.8   4:14.32 java                                                         
    91794 yyapp     20   0 2670m 300m  12m S  1.0  7.8   0:09.38 java                                                         
    91799 yyapp     20   0 2670m 300m  12m S  1.0  7.8   0:09.39 java
    

由这段结果可知线程91784和91785很消耗CPU。将91784和91785分别转为16进制，得到16688和16689。接下来通过执行命令命令`jstack
-l 91782 > 91782.log`导出线程栈信息（命令中是进程ID），并在线程dump文件中寻找16进制数16688和16689，得到如下两条信息：

    
    
    "GC task thread#0 (ParallelGC)" os_prio=0 tid=0x00007f700001e000 nid=0x16688 runnable 
    "GC task thread#1 (ParallelGC)" os_prio=0 tid=0x00007f7000020000 nid=0x16689 runnable
    

由这两行结果可知，消耗CPU的是ParallelGC线程。因为问题代码搭配的JVM参数没有指定任何垃圾回收期，所以用的是默认的PS垃圾回收，所以这个JVM实例应该在频繁FullGC，通过命令`jstat
-gcutil 91782
5s`查看GC表现可以验证，由这段结果可知，Eden和Old都占满了，且不再发生YGC，但是却在频繁FGC，此时的应用已经不能处理任务，相当于假死了，好可怕：

    
    
    S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT 
      0.00   0.00 100.00  99.98  78.57  83.36      5    0.633   366  327.647  328.281
      0.00   0.00 100.00  99.98  78.57  83.36      5    0.633   371  331.965  332.598
      0.00   0.00 100.00  99.98  78.57  83.36      5    0.633   376  336.996  337.629
      0.00   0.00 100.00  99.98  78.57  83.36      5    0.633   381  340.795  341.428
      0.00   0.00 100.00  99.98  78.57  83.36      5    0.633   387  346.268  346.901
    

## 揪出真凶

到这里基本可以确认是有对象没有释放导致即使发生FullGC也回收不了引起的，准备dump进行分析看看Old区都是些什么妖魔鬼怪，执行命令`jmap
-dump:format=b,file=91782.bin 91782`，用MAT分析时，强烈建议开启`keep unreachable objects`：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811072001.png)

接下来点击Actions下的 **Histogram** ，查找大对象:

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811072002.png)

下面贴出的是原图，而不是笔者的Demo代码跑出来的：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811072003.png)

由这段代码可知，大量的FutureContract和BigDecimal（说明：因为FutureContract中有多达16个BigDecimal类型的属性），FutureContract占了120MB，BigDecimal占了95MB。那么就可以断定问题是与FutureContract相关的代码造成的，如果是正常的JVM示例，
**Histogram** 试图最占内存的是byte[]和char[]两个数组，两者合计一般会占去80%左右的内存，远远超过其他对象占用的内存。

接下来通过FutureContract就找到上面这块buildBar方法代码，那么为什么是这块代码无法释放呢？单独把这块代码拧出来看看，这里用到了
**ScheduledThreadPoolExecutor**
定时调度，且每3秒执行一次，然而定时器中需要的参数来自外面的`List<FutureContract>`，这就会导致`List<FutureContract>`这个对象一致被一个定时任务引用，永远无法回收，从而导致FutureContract不断晋升到Old区，直到占满Old区然后频繁FullGC。

    
    
    private static void buildBar(){
        List<FutureContract> futureContractList = getAllFutureContract();
        futureContractList.forEach(contract -> {
            // do something
            executor.scheduleWithFixedDelay(() -> {
                try{
                    doFutureContract(contract);
                }catch (Exception e){
                    e.printStackTrace();
                }
            }, 2, 3, TimeUnit.SECONDS);
        });
    }
    

那么为什么会出现这种情况呢？我相信一个程序员不应该犯这样的低级错误，后来看到原生代码，我做出一个比较合理的猜测，其本意可能是想通过调用`Executor
executor`来异步执行，谁知小手一抖，在红色框那里输入了taskExecutor，而不是executor：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811072004.png)

## 解决问题

OK，知道问题的根因，想解决问题就比较简单了，将taskExecutor改成executor即可：

    
    
    private static ThreadPoolExecutor executor = new ThreadPoolExecutor(50, 50, 0L, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<>(128));
    private static void buildBar(){
        List<FutureContract> futureContractList = getAllFutureContract();
        futureContractList.forEach(contract -> {
            // do something
            executor.execute(() -> {
                try{
                    doFutureContract(contract);
                }catch (Exception e){
                    e.printStackTrace();
                }
            });
        });
    }
    

或者将这一块直接改成同步处理，不需要线程池：

    
    
    private static void buildBar(){
        List<FutureContract> futureContractList = getAllFutureContract();
        futureContractList.forEach(contract -> {
            // do something
            try{
                doFutureContract(contract);
            }catch (Exception e){
                e.printStackTrace();
            }
        });
    }
    

