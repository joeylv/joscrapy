  * 1 实验
  * 2 结论

> 原文出自：[Java 中的 try catch
影响性能吗？？](https://mp.weixin.qq.com/s?__biz=MzA4MjIyNTY0MQ==&mid=2647739215&idx=1&sn=cd64ea5acd2e29297ff85b630e1262bc&chksm=87ad1bc9b0da92dfd1043e0fa7f136c9db5c191efb31a095bf31d341b419638d5c1793751e65&mpshare=1&scene=1&srcid=0916GgRSGeJijrKC0QHT7myt#rd)

前几天在 code review 时发现有一段代码中存在滥用 try catch
的现象。其实这种行为我们也许都经历过，刚参加工作想尽量避免出现崩溃问题，因此在很多地方都想着 try catch 一下。

但实际上这种习惯不仅会让代码很难看，更会影响代码的运行性能。有些人会觉得，不就是一个 try catch 么，怎么会影响性能啊。那就让我们来测试看看吧。

## 实验

首先，我们看看没有 try-catch 情况下，进行 100 万次加法的耗时：

    
    
    long start = System.nanoTime();
    int a = 0;
    for (int i = 0; i < 1000000; i++) {
        a++;
    }
    System.out.println(System.nanoTime() - start);
    

经过5次统计，其平均耗时为：1816048 纳秒，即 1.8 毫秒。

接着，我们来看看在有 try-catch 情况下，进行 100 万次加法的耗时：

    
    
    long start = System.nanoTime();
    int a = 0;
    for (int i = 0; i < 1000000; i++) {
        try {
            a++;
        } catch (Exception e) {
            e.printStackTrace();
        }
    } 
    System.out.println(System.nanoTime() - start);
    

经过5次统计，其平均耗时为： 1928394 纳秒，即 1.9 毫秒。

我们再来看看，如果 try-catch 抛出异常，进行 100 万次加法的耗时：

    
    
    long start = System.nanoTime();
    int a = 0;
    for (int i = 0; i < 1000000; i++) {
        try {
            a++;
            throw new Exception();
        } catch (Exception e) {
            e.printStackTrace();
        }
    } 
    System.out.println(System.nanoTime() - start);
    

经过 5 次统计，其平均耗时为：780950471 纳秒，即 780 毫秒。

经过上面三次统计，我们可以看到在没有 try catch 时，耗时 1.8 毫秒。在有 try catch 但是没有抛出异常，耗时 1.9
毫秒。在有抛出异常，耗时 780 毫秒。我们能得出一个结论： **如果 try catch
没有抛出异常，那么其对性能几乎没有影响。但如果抛出异常，那对程序将造成几百倍的性能影响。**

##  结论

虽然在没有抛出异常时，try catch 几乎没有性能影响。但是一旦抛出异常，那么其对性能的影响将是巨大的。因此我们在实际编程的时候，需要特别注意 try
catch 语句的使用，不在没有必要的地方过多使用。

