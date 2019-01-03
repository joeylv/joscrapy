  * 1 总结
  * 2 博文列表
  * 3 Java内存模型推荐资料

> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

经过四篇博客阐述，我相信各位对Java内存模型有了最基本认识了，下面LZ就做一个比较简单的总结。

## 总结

JMM规定了线程的工作内存和主内存的交互关系，以及线程之间的可见性和程序的执行顺序。一方面，要为程序员提供足够强的内存可见性保证；另一方面，对编译器和处理器的限制要尽可能地放松。JMM对程序员屏蔽了CPU以及OS内存的使用问题，能够使程序在不同的CPU和OS内存上都能够达到预期的效果。

Java采用内存共享的模式来实现线程之间的通信。编译器和处理器可以对程序进行重排序优化处理，但是需要遵守一些规则，不能随意重排序。

  * **原子性** ：一个操作或者多个操作要么全部执行要么全部不执行；
  * **可见性** ：当多个线程同时访问一个共享变量时，如果其中某个线程更改了该共享变量，其他线程应该可以立刻看到这个改变；
  * **有序性** ：程序的执行要按照代码的先后顺序执行；

在并发编程模式中，势必会遇到上面三个概念，JMM对原子性并没有提供确切的解决方案，但是JMM解决了可见性和有序性，至于原子性则需要通过锁或者Synchronized来解决了。

如果一个操作A的操作结果需要对操作B可见，那么我们就认为操作A和操作B之间存在happens-before关系，即A happens-before B。

happens-
before原则是JMM中非常重要的一个原则，它是判断数据是否存在竞争、线程是否安全的主要依据，依靠这个原则，我们可以解决在并发环境下两个操作之间是否存在冲突的所有问题。JMM规定，两个操作存在happens-
before关系并不一定要A操作先于B操作执行，只要A操作的结果对B操作可见即可。

在程序运行过程中，为了执行的效率，编译器和处理器是可以对程序进行一定的重排序，但是他们必须要满足两个条件：1 执行的结果保持不变，2
存在数据依赖的不能重排序。重排序是引起多线程不安全的一个重要因素。

同时顺序一致性是一个比较理想化的参考模型，它为我们提供了强大而又有力的内存可见性保证，他主要有两个特征：1 一个线程中的所有操作必须按照程序的顺序来执行；2
所有线程都只能看到一个单一的操作执行顺序，在顺序一致性模型中，每个操作都必须原则执行且立刻对所有线程可见。

## 博文列表

  1. [【死磕Java并发】—–Java内存模型之happens-before](http://cmsblogs.com/?p=2102)
  2. [【死磕Java并发】—–Java内存模型之重排序](http://cmsblogs.com/?p=2116)
  3. [【死磕Java并发】—–Java内存模型之分析volatile](http://cmsblogs.com/?p=2148)
  4. [【死磕Java并发】—–Java内存模型之从JMM角度分析DCL](http://cmsblogs.com/?p=2161)

## Java内存模型推荐资料

  1. 程晓明：[深入Java内存模型](http://files.cnblogs.com/files/skywang12345/%E6%B7%B1%E5%85%A5Java%E5%86%85%E5%AD%98%E6%A8%A1%E5%9E%8B.pdf)
  2. 周志明：深入理解Java虚拟机-第五部分 高效并发
  3. [Java 并发编程：volatile的使用及其原理](http://www.cnblogs.com/paddix/p/5428507.html)
  4. [Java并发编程：volatile关键字解析](http://www.cnblogs.com/dolphin0520/p/3920373.html)
  5. [聊聊高并发（三十三）Java内存模型那些事（一）从一致性(Consistency)的角度理解Java内存模型](http://blog.csdn.net/iter_zc/article/details/41943387)
  6. [聊聊高并发（三十四）Java内存模型那些事（二）理解CPU高速缓存的工作原理](http://blog.csdn.net/iter_zc/article/details/41979189)
  7. [聊聊高并发（三十五）Java内存模型那些事（三）理解内存屏障](http://blog.csdn.net/iter_zc/article/details/42006811)
  8. [聊聊高并发（三十六）Java内存模型那些事（四）理解Happens-before规则](http://blog.csdn.net/iter_zc/article/details/42026511)
  9. [happens-before俗解](http://ifeve.com/easy-happens-before/)

