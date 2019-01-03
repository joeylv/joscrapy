> 原文出处：<http://cmsblogs.com/> 『 **chenssy** 』

* * *

在上篇博客[【死磕Java并发】—–J.U.C之线程池：ThreadPoolExecutor](http://cmsblogs.com/?p=2448)已经介绍了线程池中最核心的类
**ThreadPoolExecutor** ，这篇就来看看另一个核心类 **ScheduledThreadPoolExecutor** 的实现。

# ScheduledThreadPoolExecutor解析

我们知道Timer与TimerTask虽然可以实现线程的周期和延迟调度，但是Timer与TimerTask存在一些缺陷，所以对于这种定期、周期执行任务的调度策略，我们一般都是推荐ScheduledThreadPoolExecutor来实现。下面就深入分析ScheduledThreadPoolExecutor是如何来实现线程的周期、延迟调度的。

ScheduledThreadPoolExecutor，继承ThreadPoolExecutor且实现了ScheduledExecutorService接口，它就相当于提供了“延迟”和“周期执行”功能的ThreadPoolExecutor。在JDK
API中是这样定义它的：ThreadPoolExecutor，它可另行安排在给定的延迟后运行命令，或者定期执行命令。需要多个辅助线程时，或者要求
ThreadPoolExecutor 具有额外的灵活性或功能时，此类要优于 Timer。
一旦启用已延迟的任务就执行它，但是有关何时启用，启用后何时执行则没有任何实时保证。按照提交的先进先出 (FIFO)
顺序来启用那些被安排在同一执行时间的任务。

它提供了四个构造方法：

    
    
        public ScheduledThreadPoolExecutor(int corePoolSize) {
            super(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS,
                    new DelayedWorkQueue());
        }
    
        public ScheduledThreadPoolExecutor(int corePoolSize,
                                           ThreadFactory threadFactory) {
            super(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS,
                    new DelayedWorkQueue(), threadFactory);
        }
    
        public ScheduledThreadPoolExecutor(int corePoolSize,
                                           RejectedExecutionHandler handler) {
            super(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS,
                    new DelayedWorkQueue(), handler);
        }
    
    
        public ScheduledThreadPoolExecutor(int corePoolSize,
                                           ThreadFactory threadFactory,
                                           RejectedExecutionHandler handler) {
            super(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS,
                    new DelayedWorkQueue(), threadFactory, handler);
        }
    

当然我们一般都不会直接通过其构造函数来生成一个ScheduledThreadPoolExecutor对象（例如new
ScheduledThreadPoolExecutor(10)之类的），而是通过Executors类（例如Executors.newScheduledThreadPool(int);）

在ScheduledThreadPoolExecutor的构造函数中，我们发现它都是利用ThreadLocalExecutor来构造的，唯一变动的地方就在于它所使用的阻塞队列变成了DelayedWorkQueue，而不是ThreadLocalhExecutor的LinkedBlockingQueue（通过Executors产生ThreadLocalhExecutor对象）。DelayedWorkQueue为ScheduledThreadPoolExecutor中的内部类，它其实和阻塞队列DelayQueue有点儿类似。DelayQueue是可以提供延迟的阻塞队列，它只有在延迟期满时才能从中提取元素，其列头是延迟期满后保存时间最长的Delayed元素。如果延迟都还没有期满，则队列没有头部，并且
poll 将返回
null。有关于DelayQueue的更多介绍请参考这篇博客[【死磕Java并发】—–J.U.C之阻塞队列：DelayQueue](http://cmsblogs.com/?p=2413)。所以DelayedWorkQueue中的任务必然是按照延迟时间从短到长来进行排序的。下面我们再深入分析DelayedWorkQueue，这里留一个引子。

ScheduledThreadPoolExecutor提供了如下四个方法，也就是四个调度器：

  1. schedule(Callable callable, long delay, TimeUnit unit) :创建并执行在给定延迟后启用的 ScheduledFuture。
  2. schedule(Runnable command, long delay, TimeUnit unit) :创建并执行在给定延迟后启用的一次性操作。
  3. scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit) :创建并执行一个在给定初始延迟后首次启用的定期操作，后续操作具有给定的周期；也就是将在 initialDelay 后开始执行，然后在 initialDelay+period 后执行，接着在 initialDelay + 2 * period 后执行，依此类推。
  4. scheduleWithFixedDelay(Runnable command, long initialDelay, long delay, TimeUnit unit) :创建并执行一个在给定初始延迟后首次启用的定期操作，随后，在每一次执行终止和下一次执行开始之间都存在给定的延迟。

第一、二个方法差不多，都是一次性操作，只不过参数一个是Callable，一个是Runnable。稍微分析下第三（scheduleAtFixedRate）、四个（scheduleWithFixedDelay）方法，加入initialDelay
= 5，period/delay =
3，unit为秒。如果每个线程都是都运行非常良好不存在延迟的问题，那么这两个方法线程运行周期是5、8、11、14、17…….，但是如果存在延迟呢？比如第三个线程用了5秒钟，那么这两个方法的处理策略是怎样的？第三个方法（scheduleAtFixedRate）是周期固定，也就说它是不会受到这个延迟的影响的，每个线程的调度周期在初始化时就已经绝对了，是什么时候调度就是什么时候调度，它不会因为上一个线程的调度失效延迟而受到影响。但是第四个方法（scheduleWithFixedDelay），则不一样，它是每个线程的调度间隔固定，也就是说第一个线程与第二线程之间间隔delay，第二个与第三个间隔delay，以此类推。如果第二线程推迟了那么后面所有的线程调度都会推迟，例如，上面第二线程推迟了2秒，那么第三个就不再是11秒执行了，而是13秒执行。

查看着四个方法的源码，会发现其实他们的处理逻辑都差不多，所以我们就挑scheduleWithFixedDelay方法来分析，如下：

    
    
        public ScheduledFuture<?> scheduleWithFixedDelay(Runnable command,
                                                         long initialDelay,
                                                         long delay,
                                                         TimeUnit unit) {
            if (command == null || unit == null)
                throw new NullPointerException();
            if (delay <= 0)
                throw new IllegalArgumentException();
            ScheduledFutureTask<Void> sft =
                new ScheduledFutureTask<Void>(command,
                                              null,
                                              triggerTime(initialDelay, unit),
                                              unit.toNanos(-delay));
            RunnableScheduledFuture<Void> t = decorateTask(command, sft);
            sft.outerTask = t;
            delayedExecute(t);
            return t;
        }
    

scheduleWithFixedDelay方法处理的逻辑如下：

  1. 校验，如果参数不合法则抛出异常
  2. 构造一个task，该task为ScheduledFutureTask
  3. 调用delayedExecute()方法做后续相关处理

这段代码涉及两个类ScheduledFutureTask和RunnableScheduledFuture，其中RunnableScheduledFuture不用多说，他继承RunnableFuture和ScheduledFuture两个接口，除了具备RunnableFuture和ScheduledFuture两类特性外，它还定义了一个方法isPeriodic()
，该方法用于判断执行的任务是否为定期任务，如果是则返回true。而ScheduledFutureTask作为ScheduledThreadPoolExecutor的内部类，它扮演着极其重要的作用，因为它的作用则是负责ScheduledThreadPoolExecutor中任务的调度。

ScheduledFutureTask内部继承FutureTask，实现RunnableScheduledFuture接口，它内部定义了三个比较重要的变量

    
    
            /** 任务被添加到ScheduledThreadPoolExecutor中的序号 */
            private final long sequenceNumber;
    
            /** 任务要执行的具体时间 */
            private long time;
    
            /**  任务的间隔周期 */
            private final long period;
    

这三个变量与任务的执行有着非常密切的关系，什么关系？先看ScheduledFutureTask的几个构造函数和核心方法：

    
    
            ScheduledFutureTask(Runnable r, V result, long ns) {
                super(r, result);
                this.time = ns;
                this.period = 0;
                this.sequenceNumber = sequencer.getAndIncrement();
            }
    
            ScheduledFutureTask(Runnable r, V result, long ns, long period) {
                super(r, result);
                this.time = ns;
                this.period = period;
                this.sequenceNumber = sequencer.getAndIncrement();
            }
    
            ScheduledFutureTask(Callable<V> callable, long ns) {
                super(callable);
                this.time = ns;
                this.period = 0;
                this.sequenceNumber = sequencer.getAndIncrement();
            }
    
            ScheduledFutureTask(Callable<V> callable, long ns) {
                super(callable);
                this.time = ns;
                this.period = 0;
                this.sequenceNumber = sequencer.getAndIncrement();
            }
    

ScheduledFutureTask
提供了四个构造方法，这些构造方法与上面三个参数是不是一一对应了？这些参数有什么用，如何用，则要看ScheduledFutureTask在那些方法使用了该方法，在ScheduledFutureTask中有一个compareTo()方法：

    
    
        public int compareTo(Delayed other) {
            if (other == this) // compare zero if same object
                return 0;
            if (other instanceof ScheduledFutureTask) {
                ScheduledFutureTask<?> x = (ScheduledFutureTask<?>)other;
                long diff = time - x.time;
                if (diff < 0)
                    return -1;
                else if (diff > 0)
                    return 1;
                else if (sequenceNumber < x.sequenceNumber)
                    return -1;
                else
                    return 1;
            }
            long diff = getDelay(NANOSECONDS) - other.getDelay(NANOSECONDS);
            return (diff < 0) ? -1 : (diff > 0) ? 1 : 0;
        }
    

相信各位都知道该方法是干嘛用的，提供一个排序算法，该算法规则是：首先按照time排序，time小的排在前面，大的排在后面，如果time相同，则使用sequenceNumber排序，小的排在前面，大的排在后面。那么为什么在这个类里面提供compareTo()方法呢？在前面就介绍过ScheduledThreadPoolExecutor在构造方法中提供的是DelayedWorkQueue()队列中，也就是说ScheduledThreadPoolExecutor是把任务添加到DelayedWorkQueue中的，而DelayedWorkQueue则是类似于DelayQueue，内部维护着一个以时间为先后顺序的队列，所以compareTo()方法使用与DelayedWorkQueue队列对其元素ScheduledThreadPoolExecutor
task进行排序的算法。

排序已经解决了，那么ScheduledThreadPoolExecutor
是如何对task任务进行调度和延迟的呢？任何线程的执行，都是通过run()方法执行，ScheduledThreadPoolExecutor
的run()方法如下：

    
    
            public void run() {
                boolean periodic = isPeriodic();
                if (!canRunInCurrentRunState(periodic))
                    cancel(false);
                else if (!periodic)
                    ScheduledFutureTask.super.run();
                else if (ScheduledFutureTask.super.runAndReset()) {
                    setNextRunTime();
                    reExecutePeriodic(outerTask);
                }
            }
    

  1. 调用isPeriodic()获取该线程是否为周期性任务标志，然后调用canRunInCurrentRunState()方法判断该线程是否可以执行，如果不可以执行则调用cancel()取消任务。
  2. 如果当线程已经到达了执行点，则调用run()方法执行task，该run()方法是在FutureTask中定义的。
  3. 否则调用runAndReset()方法运行并充值，调用setNextRunTime()方法计算任务下次的执行时间，重新把任务添加到队列中，让该任务可以重复执行。

**isPeriodic()**

该方法用于判断指定的任务是否为定期任务。

    
    
            public boolean isPeriodic() {
                return period != 0;
            }
    

canRunInCurrentRunState()判断任务是否可以取消，cancel()取消任务，这两个方法比较简单，而run()执行任务，runAndReset()运行并重置状态，牵涉比较广，我们放在FutureTask后面介绍。所以重点介绍setNextRunTime()和reExecutePeriodic()这两个涉及到延迟的方法。

**setNextRunTime()**

setNextRunTime()方法用于重新计算任务的下次执行时间。如下：

    
    
            private void setNextRunTime() {
                long p = period;
                if (p > 0)
                    time += p;
                else
                    time = triggerTime(-p);
            }
    

该方法定义很简单，p > 0 ,time += p ，否则调用triggerTime()方法重新计算time：

    
    
        long triggerTime(long delay) {
            return now() +
                ((delay < (Long.MAX_VALUE >> 1)) ? delay : overflowFree(delay));
        }
    

**reExecutePeriodic**

    
    
        void reExecutePeriodic(RunnableScheduledFuture<?> task) {
            if (canRunInCurrentRunState(true)) {
                super.getQueue().add(task);
                if (!canRunInCurrentRunState(true) && remove(task))
                    task.cancel(false);
                else
                    ensurePrestart();
            }
        }
    

reExecutePeriodic重要的是调用super.getQueue().add(task);将任务task加入的队列DelayedWorkQueue中。ensurePrestart()在[【死磕Java并发】—–J.U.C之线程池：ThreadPoolExecutor](http://cmsblogs.com/?p=2448)已经做了详细介绍。

到这里ScheduledFutureTask已经介绍完了，ScheduledFutureTask在ScheduledThreadPoolExecutor扮演作用的重要性不言而喻。其实ScheduledThreadPoolExecutor的实现不是很复杂，因为有FutureTask和ThreadPoolExecutor的支撑，其实现就显得不是那么难了。

