在Java5之前，线程是没有返回值的，常常为了“有”返回值，破费周折，而且代码很不好写。或者干脆绕过这道坎，走别的路了。

现在Java终于有可返回值的任务（也可以叫做线程）了。

可返回值的任务必须实现Callable接口，类似的，无返回值的任务必须Runnable接口。

执行Callable任务后，可以获取一个Future的对象，在该对象上调用get就可以获取到Callable任务返回的Object了。

下面是个很简单的例子：

    
    
    public class Test { 
            public static void main(String[] args) throws ExecutionException, InterruptedException { 
                    //创建一个线程池 
                    ExecutorService pool = Executors.newFixedThreadPool(2); 
                    //创建两个有返回值的任务 
                    Callable c1 = new MyCallable("A"); 
                    Callable c2 = new MyCallable("B"); 
                    //执行任务并获取Future对象 
                    Future f1 = pool.submit(c1); 
                    Future f2 = pool.submit(c2); 
                    //从Future对象上获取任务的返回值，并输出到控制台 
                    System.out.println(">>>"+f1.get().toString()); 
                    System.out.println(">>>"+f2.get().toString()); 
                    //关闭线程池 
                    pool.shutdown(); 
            } 
    } 
    
    class MyCallable implements Callable{ 
            private String oid; 
    
            MyCallable(String oid) { 
                    this.oid = oid; 
            } 
    
            @Override 
            public Object call() throws Exception { 
                    return oid+"任务返回的内容"; 
            } 
    }
    
    
    >>>A任务返回的内容 
    >>>B任务返回的内容

非常的简单，要深入了解还需要看Callable和Future接口的API啊。

**本文出自 “**[ **熔 岩**](http://lavasoft.blog.51cto.com/) **” 博客，请务必保留此出处**[
**http://lavasoft.blog.51cto.com/62575/222082**](http://lavasoft.blog.51cto.com/62575/222082)

