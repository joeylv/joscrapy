阻塞队列是Java5线程新特征中的内容，Java定义了阻塞队列的接口java.util.concurrent.BlockingQueue，阻塞队列的概念是，一个指定长度的队列，如果队列满了，添加新元素的操作会被阻塞等待，直到有空位为止。同样，当队列为空时候，请求队列元素的操作同样会阻塞等待，直到有可用元素为止。

有了这样的功能，就为多线程的排队等候的模型实现开辟了便捷通道，非常有用。

java.util.concurrent.BlockingQueue继承了java.util.Queue接口，可以参看API文档。

下面给出一个简单应用的例子：

    
    
    public class Test { 
            public static void main(String[] args) throws InterruptedException { 
                    BlockingQueue bqueue = new ArrayBlockingQueue(20); 
                    for (int i = 0; i < 30; i++) { 
                            //将指定元素添加到此队列中，如果没有可用空间，将一直等待（如果有必要）。 
                            bqueue.put(i); 
                            System.out.println("向阻塞队列中添加了元素:" + i); 
                    } 
                    System.out.println("程序到此运行结束，即将退出----"); 
            } 
    }
    
    
    向阻塞队列中添加了元素:0 
    向阻塞队列中添加了元素:1 
    向阻塞队列中添加了元素:2 
    向阻塞队列中添加了元素:3 
    向阻塞队列中添加了元素:4 
    向阻塞队列中添加了元素:5 
    向阻塞队列中添加了元素:6 
    向阻塞队列中添加了元素:7 
    向阻塞队列中添加了元素:8 
    向阻塞队列中添加了元素:9 
    向阻塞队列中添加了元素:10 
    向阻塞队列中添加了元素:11 
    向阻塞队列中添加了元素:12 
    向阻塞队列中添加了元素:13 
    向阻塞队列中添加了元素:14 
    向阻塞队列中添加了元素:15 
    向阻塞队列中添加了元素:16 
    向阻塞队列中添加了元素:17 
    向阻塞队列中添加了元素:18 
    向阻塞队列中添加了元素:19

可以看出，输出到元素19时候，就一直处于等待状态，因为队列满了，程序阻塞了。

这里没有用多线程来演示，没有这个必要。

另外，阻塞队列还有更多实现类，用来满足各种复杂的需求：ArrayBlockingQueue, DelayQueue,
LinkedBlockingQueue, PriorityBlockingQueue, SynchronousQueue ，具体的API差别也很小。

**本文出自 “**[ **熔 岩**](http://lavasoft.blog.51cto.com/) **” 博客，请务必保留此出处**[
**http://lavasoft.blog.51cto.com/62575/222524**](http://lavasoft.blog.51cto.com/62575/222524)

