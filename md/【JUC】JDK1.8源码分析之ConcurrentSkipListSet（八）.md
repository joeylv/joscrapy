**一、前言**

分析完了CopyOnWriteArraySet后，继续分析Set集合在JUC框架下的另一个集合，ConcurrentSkipListSet，ConcurrentSkipListSet一个基于
ConcurrentSkipListMap 的可缩放并发 NavigableSet 实现。set 的元素可以根据它们的自然顺序进行排序，也可以根据创建
set 时所提供的 Comparator 进行排序，具体取决于使用的构造方法。

**二、ConcurrentSkipListSet的数据结构**

由于ConcurrentSkipListSet是基于ConcurrentSkipListMap的实现，所以，其底层数据结构与ConcurrentSkipListMap的相同，具体可以参考[ConcurrentSkipListMap，](http://www.cnblogs.com/leesf456/p/5512817.html)其数据结构如下。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA2IAAADiCAIAAACjleOAAAAgAElEQVR4Ae2dX8hdxfX337w+8ovSiwihBAmSqIEUDKQQJQ1aqgX1MlZBLQmm0ILGghGiXmhIQi1FK2gRtBgw3qlE0Qsh0YJKFRUNxKIYoWqCCSpEMBfFBBT8fXS9rne69z777P9nZp/vuTjPnJk1a9Z8Zs3M2rP3c86i77777v/oJQIiIAIiIAIiIAIiIAL/TeD//vdHfRIBERABERABERABERCB7wkoTJQfiIAIiIAIiIAIiIAIFBBQmFgARVkiIAIiIAIiIAIiIAIKE+UDIiACIiACIiACIiACBQQUJhZAUZYIiIAIiIAIiIAIiIDCRPmACIiACIiACIiACIhAAYFewsSTJ0/ecccdF1988VlnnbVozl50mY7ffvvtX375ZQFvZc2CQCoOKeeZhXfMoE055Aygq0kR6J/AKKd292Hi66+/vmbNmtOnT//1r3/9/PPP+V7GuXrR5YcffnhhYQEIBw4c6N8t1cIUAgk5pJxnyliOolgOOYphVCdEIEtgtFO72xjuq6++Wr58+b59+7pVm6K2/fv3L1269NixYykaPxqbE3VIOc9oPDDTETlkBog+isA4CIx4ai9ihLIhcYvP3GvmHJHjtBY6xlN1x44dX3zxxZ49e8bTpdR6kq5DynlS87VK9sohK2GSkAikRmDEU7vjm86vvvrqTTfdlNr49mXv9ddf/9Zbb/WlXXorEMAhr7322gqC0Ylg9sGDB6MzSwa1I8CYJuqQWs3ajbxqj5xAusHP1L2m49NEnsHn6HXx4sUj94jK3eMfeLo9r63csgS/J4BD8sDfkiVLksPBqfw555xz6tSp5CyXwSUEGNMjR46k6JB0SqtZyciqaM4JpBv8TN1rOg5itI5kpoqAZIAM/DFp/kkbP/BAp9Jc0mOatPGpeIjsTJRA0rOj3PiObzonOsAyWwREQAREQAREQAREIENAYWIGiD6KgAiIgAiIgAiIgAh8T2BUYeLWrVsvvPDCNgN79Q+vNhpUd64I4G943Vx1WZ2NmQA3j+6///6YLZRtIiACaRGYGCY+9dRTrDj2ahl7ORHT+cknn3gOCZroY11rHzKGRio9egK6Qhj9EKfVQV2BpDVeslYEqhMgPiHyyRwxhLFQfvoTOCFAEEUrfI83ad7DFkOBML99emKYeOONN/qXXn788ceZ/rRvWBpEQAREQAREQAREYN4I2GHZo48+mjk1i5PDxDAx/BqXW2655aWXXoqzA7JKBEIC/KRm+FFpEZgtAb5sYrYGqHUREIFuCfAViddcc827777bRu1VV111wQUXPPDAA22UDFN3YpgYNk/A29V951BtYZqGOE21VyjAPcEfsxeFAbgd3lKEQCgfppHhxa1t05CRdM3IhLVI540xJW5A/mQ4o0EfBybwi1/84vbbb+fHb9q0+4O/THQY9wqcIdOKF+FpViSHySCat4845K5du1peveBX3GzylSrjeL4w2g0pJ8wy5UW+6JFAm8mYQKaWV1dCBERgEoHnn3/+5z//ectg8d577+VAMXPveFKLM8xfmNo2i8iLL7745JNPTpVsL8D6deWVVz7yyCOosv3VDjVZ2rZs2XLgwAHy2cKR+eijj0wGytwTP//885G/6667CM8LzUCMM1HTxtKJ8J133mna6J3lo5k0Mb5pKDSGWo899hiSGIMSmjZrCxtV5vAEOLx56KGH/v73v99www133313YwMmOYxtt+6WOIA3IYdxFEo4AQLE3bt3/+1vf7vtttu2bdvm+XUTPAXEIsyyw6Zy2WWXbdiw4dJLL0UJXseSZWsjaVdLCMhiSBUmApn4LS/EWK/ItwWQdYy6JuAVJyWYVhStXLlykoDy54TAT37yk6VLl85JZwu76Vd9BIu8Nm7cuHfv3kLJ8kym3j333EOwaPO3XHiGpRPDRFuMzLL77ruv4lJSpSeTIjlaDKMuAjLCPoJUmg4h/vKXv2QLt4aI2LCNGJGPyB89enTSzXFWQ4/niBdffvllCxNR5REwAn5MWGLME088wTKNYZjndUs6roW1BE7nRcePH0cnwSLD1OaYpNBhcA8uJF577TUzG7f0jblDhwmZ+KlkmDmmNPsNu86YepTpizmkB4uZ0uoffREmOmQJfeONN0iY1/mix8WzO8wzzzwThoDsRqxaODCrJapYu8477zycObzOKTeGC3XO6V955ZVyMZWOnsB//vOfL7/8cvTdLOkgt5v9jjMx4s6dOxv/rhIxIleATGS76itpdIZFE8NEjLYjE4xjLyQgswO89rayMFlgZ6p8XWPhI8c/ZhrChvyKRg6LXUayykfriwWFy5cvz1cpMQYyBJoMbbgK5zV4jhZWRzFAgr2QjXlhYWHTpk2cJq5ataqTRs1hPvvsM7Sde+65eZ0dOkyo3OdgmDmmNI8HjPvpPXNIhuxXv/oV28nll1/eyfBxSYwei0HD5dSVcyVMFFi4nNotEVYwv8b2WiUJ2whXrFhRIqMiEZgfAhYgrl27tk2XOQXjRCPyA8WJYWLYc65WuX61g70wv/M0rRQGo8SIvKwIM1jgOm86r3CSMUhafFloal6PFtY8k/5y+D1xjj0IEHGY/lop1NyVwxQqH2vmsmXLxto16xdXLBYg8j5wT7ma9VsomabtkttizUyRPoqACJQTYE8/dOhQywDRm7CT/sy9r0n7V+GplqvqKVHpX1h6ajujlnNBFi+LwMIicsgHZZhpaTbmTz/9NJ9fMceuwu2KPFNlkjGIMZx25xGreMQnU1EfZ0uAO8I8JjJpjrW0zc4R7Uwxo0oOkwGij0bgueee435CTzGi7Rn5NZOmWdz8ZnRmLHgkkZWTB2Z45Ia7XZlSfRQBESgnQJjYVYxIQ9yf5M4kZ4pho/n5+/bbbyNQeC8rrNhHujhMJBLieWdvz5aVDh9PdM1hAv0sXrTlmXbHxII5u6nHghgeJfK/LDxkY/JEbP7MomuYmmB4PAClaeI/qzLJGErtZg1Da4/4FK7RU9uVQE8Eej2dwhVxUW4QmPHMETuV4aMcpqcBTV1th9tJHgWrEJn+nRrh1dH27dvD61jCQVvSSbBOsifhsax+HL3n1SpHBERgSAKc+nvsYe3a/PVwyCKfWk+JdGh/cZjICkIbRGn24u5qxRusLS2zhn5sdpHvwRwREQ6SzyYNKW8FuKx0Js8NlCr/UOJ1LWH/HGMauEQIlRcaYxGz/fsL75m4NqNcH8dHAK+wR77wGbZY7ut5H+UwjkKJwQiwSBL22QpG8Md6aE1zSUORLZvmq7bWmdNafMn6GYaSg9mshkRABEICzFbbSvx/LcjhwXSf2kQahDcWeFDRzhR57tkmPu8c7VGFIo6xPLOru52Lun1GHvu6VRiiTDEtILMdtaT5J238bMc92taTHtOkjY/WJWTYOAgkPTvKjS8+TRzHsKkXIiACIiACIiACIiACjQkoTGyMThVFQAREQAREQAREYMwEFCaOeXTVNxEQAREQAREQARFoTKDjMJEvCRv3l+U2Bq2KMyGAQ/oPK83EgMaNfvvttxjfuLoqxkmAL6lO1yHjRCqrRCAGAukGP1P3mo7DxIsuuuj999+PYcxisIF/fQ2/oiIGk+bNBhzyww8/TLHXmL169eoULZfNJQQY03QdUqtZyciqaM4JpBv8TN1rOg4T169f//TTT8+5u3j3+VlVgPhHJYYnAP9nn312+Hbbt/jCCy/0+pV77S2UhgYE1q1bl65DajVrMOKqMicE0g1+pu81fH9Nh68TJ07w/cb79+/vUGeiqviuR24wHTlyJFH7x2F2og4p5xmH++V7IYfMM1GOCIyAwIin9hm7du3qMNg/++yzOXrdvHnz119/TZDEaw6fr+Je82OPPXbrrbfu2bNnw4YNHeKVqroEknNIOU/dIU5LXg6Z1njJWhGoSGDMU7uPKP7YsWN81//cPshCxzdt2qRzxD5cq5nOhBxSztNsiNOqJYdMa7xkrQhUJDDKqT3aH00p/1bxitcHEhOBcgJys3I+Kh2GgPxwGM5qRQTmkEDH/8IyhwTVZREQAREQAREQAREYJQGFiaMcVnVKBERABERABERABNoSUJjYlqDqi4AIiIAIiIAIiMAoCShMHOWwqlMiIAIiIAIiIAIi0JaAwsS2BFVfBERABERABERABEZJQGHiKIdVnRIBERABERABERCBtgQUJrYlqPoiIAIiIAIiIAIiMEoCChNHOazqlAiIgAiIgAiIgAi0JaAwsS1B1RcBERABERABERCBURJQmDjKYVWnREAEREAEREAERKAtAYWJbQmqvgiIgAiIgAiIgAiMkoDCxFEOqzolAiIgAiIgAiIgAm0JKExsS1D1RUAEREAEREAERGCUBBQmjnJY1SkREAEREAEREAERaEtAYWJbgqovAiIgAiIgAiIgAqMkoDBxlMOqTomACIiACIiACIhAWwIKE9sSVH0REAEREAEREAERGCUBhYmjHFZ1SgREQAREQAREQATaElCY2Jag6ouACIiACIiACIjAKAkoTBzlsKpTIiACIiACIiACItCWgMLEtgRVXwREQAREQAREQARGSUBh4iiHVZ0SAREQAREQAREQgbYEFCa2Jaj6IiACIiACIiACIjBKAmMLE0+ePHnOOecsWrSI0eL9zDPPPHr06ChHTp2aIQG52Qzhq2knID90FEqIgAj0RGBsYeKSJUtuu+02h7Vp06YVK1b4RyVEoBMCcrNOMEpJSwLyw5YAVV0ERGAqgUXffffdVKG0BLjCXrly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rrrV3Ks2fuQNy3ttQspFQAREQAREoJxAx2Eiv432/vvvlzc5P6U838m/LM1Pf+PsKT754YcfxmlbiVXYvHr16hIBFYmACIiACIhA3wQ6DhPXr1//9NNP9210Kvr5IQSApGLtWO1kCJ599tnkevfCCy+0/KqF5Lo8DwYvWbIkxbNthobj7XkYIPVRBBoQSPc+apXbVh3f1frTn/60Zs2aX//611dffXUD1mOqwheS8f/tfLXSmDqVYl9S9Ek5T4qeVsVmTog5J07x6hGzdW+kyhBLZg4J2H3UdevWJdf3Kretzti1a1eHHTv77LPhtXnz5q+//prvlf3pT3/aofJUVHGvmd/CuvXWW/fs2bNhw4ZUzB6rnWn5pJxnrH5o/frXv/7173//m5+PSq6bjz/++P/8z//85je/Sc5yGSwCfRNIel6fccYZU+Z1lW9frCtz7Ngxfnlibi896fimTZv4ZeG63CTfH4FUfFLO058PxKD5xIkT/BzL/v37YzCmug18bRu3y7WmVScmybkiMO553fEX4vQds1fXP/V/vKurkqQIFBKQjxViUWY5AX7Ckfst3G3gB2G5B80vPpfLz7CU55a4J8Vjsjw/w70Rfr9+hsaoaRGImcCI57XCxJgdT7ZFTUBhYtTDE7Fxx48f37FjB0+gxv9jVxxv8yQlD/jyI7YRE5VpIjB7AmOd1woTZ+9bsiBRAgoTEx248ZktVxzfmKpHIhAJgY6/ECeSXskMERABERABERABERCBlgQUJrYEqOoiIAIiIAIiIAIiME4CChPHOa7qlQiIgAiIgAiIgAi0JKAwsSVAVRcBERABERABERCBcRJQmDjOcVWvREAEREAEREAERKAlAYWJLQGqugiIgAiIgAiIgAiMk4DCxHGOq3olAiIgAiIgAiIgAi0JKExsCVDVRUAEREAEREAERGCcBBQmjnNc1SsREAEREAEREAERaElAYWJLgKouAiIgAiIgAiIgAuMkoDBxnOOqXomACIiACIiACIhASwIKE1sCVHUREAEREAEREAERGCcBhYnjHFf1SgREQAREQAREQARaElCY2BKgqouACIiACIiACIjAOAkoTBznuKpXIiACIiACIiACItCSgMLElgBVXQREQAREQAREQATGSUBh4jjHVb0SAREQAREQAREQgZYEFCa2BKjqIiACIiACIiACIjBOAgoT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)

说明： **ConcurrentSkipListSet将所有键（key）所对应的值（value）均为Boolean.TRUE**
，所以数据结构与ConcurrentSkipListMap完全相同，并且对ConcurrentSkipListSet的操作都会转化为对ConcurrentSkipListMap的操作。

**三、ConcurrentSkipListSet源码分析**

3.1 类的继承关系

    
    
    public class ConcurrentSkipListSet<E>
        extends AbstractSet<E>
        implements NavigableSet<E>, Cloneable, java.io.Serializable {}

说明：ConcurrentSkipListSet继承了AbstractSet抽象类，AbstractSet提供 Set
接口的骨干实现，从而最大限度地减少了实现此接口所需的工作；同时实现了NavigableSet接口，NavigableSet具有了为给定搜索目标报告最接近匹配项的导航方法；同时实现了额Serializable接口，表示可以被序列化。

3.2 类的属性

![]()![]()

    
    
    public class ConcurrentSkipListSet<E>
        extends AbstractSet<E>
        implements NavigableSet<E>, Cloneable, java.io.Serializable {
        // 版本序列号
        private static final long serialVersionUID = -2479143111061671589L;
        // 对ConcurrentSkipListSet提供支持
        private final ConcurrentNavigableMap<E,Object> m;
        // 反射机制
        private static final sun.misc.Unsafe UNSAFE;
        // m字段的内存偏移量
        private static final long mapOffset;
        static {
            try {
                UNSAFE = sun.misc.Unsafe.getUnsafe();
                Class<?> k = ConcurrentSkipListSet.class;
                mapOffset = UNSAFE.objectFieldOffset
                    (k.getDeclaredField("m"));
            } catch (Exception e) {
                throw new Error(e);
            }
        }
    }

View Code

说明：可以看到ConcurrentSkipListSet有一个ConcurrentNavigableMap字段m，表示一个接口类型，ConcurrentSkipListMap类实现了该接口，也正是ConcurrentNavigableMap对ConcurrentSkipListSet提供了支持。

3.3 类的构造函数

1\. ConcurrentSkipListSet()型构造函数

![]()![]()

    
    
        public ConcurrentSkipListSet() {
            // 初始化m字段
            m = new ConcurrentSkipListMap<E,Object>();
        }

View Code

说明：该构造函数用于构造一个新的空 set，该 set 按照元素的自然顺序对其进行排序。

2. ConcurrentSkipListSet(Comparator<? super E>)型构造函数 

![]()![]()

    
    
        public ConcurrentSkipListSet(Comparator<? super E> comparator) {
            // 初始化m字段,带有构造器
            m = new ConcurrentSkipListMap<E,Object>(comparator);
        }

View Code

说明：该构造函数用于构造一个新的空 set，该 set 按照指定的比较器对其元素进行排序。

3\. ConcurrentSkipListSet(Collection<? extends E>)型构造函数

![]()![]()

    
    
        public ConcurrentSkipListSet(Collection<? extends E> c) {
            // 初始化m字段
            m = new ConcurrentSkipListMap<E,Object>();
            // 添加s集合所有元素
            addAll(c);
        }

View Code

说明：该构造函数用于构造一个包含指定 collection 中元素的新 set，这个新 set 按照元素的自然顺序对其进行排序。

4. ConcurrentSkipListSet(SortedSet<E>)型构造函数 

![]()![]()

    
    
        public ConcurrentSkipListSet(SortedSet<E> s) {
            // 初始化m字段
            m = new ConcurrentSkipListMap<E,Object>(s.comparator());
            // 添加s集合所有元素
            addAll(s);
        }

View Code

说明：该构造函数用于构造一个新 set，该 set 所包含的元素与指定的有序 set 包含的元素相同，使用的顺序也相同。

5\. ConcurrentSkipListSet(ConcurrentNavigableMap<E, Object>)型构造函数

![]()![]()

    
    
        ConcurrentSkipListSet(ConcurrentNavigableMap<E,Object> m) {
            // 初始化m字段
            this.m = m;
        }

View Code

说明：该构造函数不是public的，在外部无法调用，用于生成子集时调用。

3.4 核心函数分析

对ConcurrentSkipListSet的操作（如add、remove、clear等操作）都是基于ConcurrentSkipListMap，所以参考ConcurrentSkipListMap的核心函数分析即可，这里不再累赘。

**四、示例**

下面通过一个示例来理解ConcurrentSkipListSet的使用。

![]()![]()

    
    
     package com.hust.grid.leesf.collections;
    
    import java.util.Iterator;
    import java.util.concurrent.ConcurrentSkipListSet;
    
    class PutThread extends Thread {
        private ConcurrentSkipListSet<Integer> csls;
        public PutThread(ConcurrentSkipListSet<Integer> csls) {
            this.csls = csls;
        }
        
        public void run() {
            for (int i = 0; i < 10; i++) {
                csls.add(i);
            }
        }
    }
    public class ConcurrentSkipListSetDemo {
        public static void main(String[] args) {
            ConcurrentSkipListSet<Integer> csls = new ConcurrentSkipListSet<Integer>();
            PutThread p1 = new PutThread(csls);
            PutThread p2 = new PutThread(csls);
            p1.start();
            p2.start();
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            Iterator<Integer> iterator = csls.iterator();
            while (iterator.hasNext()) {
                System.out.print(iterator.next() + " ");
            }        
        }
    }

View Code

运行结果（某一次）

    
    
    0 1 2 3 4 5 6 7 8 9 

说明：有两个PutThread线程向ConcurrentSkipListSet中添加元素，并且添加的元素是相同的，之后通过迭代器访问ConcurrentSkipListSet，发现元素只会出现一次，并且，值得注意的是，
**迭代器是弱一致的，返回的元素将反映迭代器创建时或创建后某一时刻的映射状态。它们不抛出
ConcurrentModificationException，可以并发处理其他操作。**

**五、总结**

****
ConcurrentSkipListSet是基于ConcurrentSkipListMap实现的，并且迭代器是弱一致性的，即在迭代的过程中，可以有其他修改ConcurrentSkipListSet的操作，不会抛出ConcurrentModificationException异常，在分析了ConcurrentSkipListMap后，再分析ConcurrentSkipListSet就变得十分简单了。谢谢各位园友的观看~
**  
**

