**一、前言**

分析完了CopyOnWriteArrayList后，下面接着分析CopyOnWriteArraySet，CopyOnWriteArraySet与CopyOnWriteArrayList有莫大的联系，因为CopyOnWriteArraySet的底层是由CopyOnWriteArrayList提供支持，并且将对其的操作转发至对CopyOnWriteArrayList的操作。但是，CopyOnWriteArraySet的元素不允许重复，这是和CopyOnWriteArrayList不相同的地方，下面开始分析。

**二、CopyOnWriteArraySet数据结构**

由于CopyOnWriteArraySet底层是使用CopyOnWriteArrayList，所以其数据结构与CopyOnWriteArrayList相同，采用数组结构。其结构如下

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASoAAABDCAIAAACk1N9eAAAFoElEQVR4Ae2czS50SxSGj5NzFSIiuAYDYWKASzA0knABTNwAMSYxMsIlYGCAuAsiIm7Deb+s863sdJfu/mqvXaX7PD1otaur1lr1rPXW/unoqa+vr794QQACNQj8XcMpPiEAgV8EkB91AIFqBJBfNfQ4hgDyowYgUI0A8quGHscQ+GcogqmpqaFjGAABCAwmkPyKYbj8ZDQ5c7CzET+VtjHezwos/UzUM9ZYkivi4jOJhU4IlCCA/EpQxgcEkgSQXxILnRAoQQD5laCMDwgkCSC/JBY6IVCCAPIrQRkfEEgSQH5JLHRCoAQB5FeCMj4gkCSA/JJY6IRACQLIrwRlfEAgSQD5JbHQCYESBJBfCcr4gECSAPJLYqETAiUIIL8SlPEBgSQB5JfEQicEShBAfiUo4wMCSQLIL4mFTgiUIID8SlDGBwSSBJBfEgudEChBAPmVoIwPCCQJIL8kFjohUIIA8itBGR8QSBJAfkksdEKgBAHkV4IyPiCQJID8kljohEAJAsN/ZJofmS+RB3xMOoHkr7kPl9+kY2F9EKhGgIvPauhxDAHkRw1AoBoB5FcNPY4hgPyoAQhUI4D8qqHHMQSQHzUAgWoEkF819DiGAPKjBiBQjQDyq4YexxBAftQABKoRQH7V0OMYAsiPGoBANQLIrxp6HEMA+VEDEKhGoJX8jo+P9d+A9rq+vg5fhGzKuLzEWn59ff0d9a+/nRqXr1j7Zm1vb0+R6z3QuNnsjoxC3dzcdPtRBfP09OQ2vSFHgWSaYQdXo/4LMO91dHSkFdrcx8dHta+urvJMJWdtbGwYQTlKDsjuXFhYUMA2XW29sk31T1TYblztWOPmzmjL+O7ubn8A2T2yJpvZ04dOVDZjA/7Oo5gH1oxi9iQa+cA6/08/361kQL9oNhepzAUmz7Xd42VAPHkfCaVcvLy85E0fPKsj46oGWRbt2GruVH5KaGB5DMAezrxHzD2HAyIZ5aPMi0+d8VW1y8vLerfX2tra7e3t76O2f/f39xV9WysjzJ+ZmRlhVOaQ9/d3zZyfn8+cn5pmFz9bW1upD39u3/n5uSqkQHwXFxfSeSDzxcXF+/t7i1y3EtqpZ2dnoxaSKb+Pjw9FMD097XEExuQ2CzQuLy+1nwVmy2NWqg4ODnRK8Z72DbOpCmtvKmlBG6jfPtkOmxyW0amqfXt7c+Ox92Yej2LWEg4PD72nfeP09NSwyLhKRQkN3Psy5dd+VT/Bgqr57OxsZ2cnNhgrMqVK27CSF2j85ORE6V9ZWQm06aYUql8vycvq6mqUAsVZXvTu9lXQsc+NbBW2mcby0dasvUP2BUTvsQn9X8tvfX1dCtGFriUv6t2LTJmTFK342huXGLRZxKb/u6jMi6r5uwEZ/dvb2z5L8r67u/PDqEYXm6mu9rWT2uM0VYsSGvXMVqvOlJ/dMn1+fjo43ecoSj/8+Q1d/2hXu7m56S5UFbGY6JQV4uL5+Vl2/PpNJxBVW6C8e4IMzGb/tf3c3FyPu/aHdlccu5lq69QdhB7n2BlV1SIFBl7cZsrPorE7QAOn21OdTNpDLGNBVz4q3zJPd6JWZI+j/NSqOtA5RIf9xR3iUXtToEgk5oeHBw9M1aJHGn4Y0tDTHQEJMeVG7ASztLTkPcEPkDydf9qwpdose9prJ+g/tTN4vJbd/Hpj8OARP7VvNVReI44ffZjdJPj47hzJhcvP3bVpKHIpxC3IuMj7YftGE0X4t2cKr9MKtG3OIAhL87AlmVaILUm2McRqz7Jllu1dvlou1ac3zYYb74m8C5HbQmLlJ5vNbDal6NxaNpqnpthqseC7iFmWbUv1mgnUnozzK9cOlgYEShPIvPcrHSb+IDCJBJDfJGaVNY0JAeQ3JokizEkkgPwmMausaUwIIL8xSRRhTiIB5DeJWWVNY0LgXxiHDp/DQM2BAAAAAElFTkSuQmCC)

说明：CopyOnWriteArraySet由于是基于CopyOnWriteArrayList的，所以对其操作都是基于CopyOnWriteArrayList的，其中所有可变操作（add、set
等等）都是通过对底层数组进行一次新的复制来实现的。

三、 **CopyOnWriteArraySet** 源码分析

3.1 类的继承关系

    
    
    public class CopyOnWriteArraySet<E> extends AbstractSet<E>
            implements java.io.Serializable {}

说明：CopyOnWriteArraySet继承了AbstractSet抽象类，AbstractSet提供 Set
接口的骨干实现，从而最大限度地减少了实现此接口所需的工作；同时实现了Serializable接口，表示可以序列化。

3.2 类的属性

    
    
    public class CopyOnWriteArraySet<E> extends AbstractSet<E>
            implements java.io.Serializable {
        // 版本序列号
        private static final long serialVersionUID = 5457747651344034263L;
        // 由其对CopyOnWriteArraySet提供支持
        private final CopyOnWriteArrayList<E> al;
    }

说明：其属性中包含了一个CopyOnWriteArrayList类型的变量al，对CopyOnWriteArraySet的操作会转发至al上执行。

3.3 类的构造函数

1\. CopyOnWriteArraySet()型构造函数

![]()![]()

    
    
        public CopyOnWriteArraySet() {
            // 初始化al
            al = new CopyOnWriteArrayList<E>();
        }

View Code

说明：此构造函数用于创建一个空 set。

2\. CopyOnWriteArraySet(Collection<? extends E>)型构造函数

![]()![]()

    
    
        public CopyOnWriteArraySet(Collection<? extends E> c) {
            if (c.getClass() == CopyOnWriteArraySet.class) { // c集合为CopyOnWriteArraySet类型
                // 初始化al
                @SuppressWarnings("unchecked") CopyOnWriteArraySet<E> cc =
                    (CopyOnWriteArraySet<E>)c;
                al = new CopyOnWriteArrayList<E>(cc.al);
            }
            else { // c集合不为CopyOnWriteArraySet类型
                // 初始化al
                al = new CopyOnWriteArrayList<E>();
                // 添加c集合(c集合的元素在al中部存在时，才会添加)
                al.addAllAbsent(c);
            }
        }

View Code

说明：此构造函数用于创建一个包含指定 collection 所有元素的 set。处理流程如下

①
判断集合c的类型是否为CopyOnWriteArraySet类型，若是，则获取c的al，并且初始当前CopyOnWriteArraySet的al域（调用CopyOnWriteArrayList的构造函数），否则，进入步骤②

② 新生CopyOnWriteArrayList，并赋值给al，之后调用addAllIfAbsent函数（al中不存在的元素，才添加）。

3.4 核心函数分析

由于对CopyOnWriteArraySet的操作（如add、remove、clear等）都转化为对CopyOnWriteArrayList的操作，所以在此不再进行讲解，有疑惑的读者可以参考[CopyOnWriteArrayList](http://www.cnblogs.com/leesf456/p/5547853.html)的源码分析。

**四、示例**

**** 下面通过一个示例来了解CopyOnWriteArraySet的使用。

![]()![]()

    
    
    package com.hust.grid.leesf.collections;
    
    import java.util.Iterator;
    import java.util.concurrent.CopyOnWriteArraySet;
    
    class PutThread extends Thread {
        private CopyOnWriteArraySet<Integer> cowas;
    
        public PutThread(CopyOnWriteArraySet<Integer> cowas) {
            this.cowas = cowas;
        }
    
        public void run() {
            for (int i = 0; i < 10; i++) {
                cowas.add(i);
            }
        }
    }
    
    public class CopyOnWriteArraySetDemo {
        public static void main(String[] args) {
            CopyOnWriteArraySet<Integer> cowas = new CopyOnWriteArraySet<Integer>();
            for (int i = 0; i < 10; i++) {
                cowas.add(i);
            }
            PutThread p1 = new PutThread(cowas);
            p1.start();
            Iterator<Integer> iterator = cowas.iterator();
            while (iterator.hasNext()) {
                System.out.print(iterator.next() + " ");
            }
            System.out.println();
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
    
            iterator = cowas.iterator();
            while (iterator.hasNext()) {
                System.out.print(iterator.next() + " ");
            }
        }
    }

View Code

运行结果（某一次）

    
    
    0 1 2 3 4 5 6 7 8 9 
    0 1 2 3 4 5 6 7 8 9 

说明：首先，主线程向CopyWriteArraySet也添加了元素，然后，PutThread线程向CopyOnWriteArraySet中添加元素（与之前添加了元素重复），两次迭代，遍历集合，发现结果相同，即CopyWriteArraySet中没有重复的元素。

**五、总结**

CopyOnWriteArraySet的源码比较简单，是依托CopyOnWriteArrayList而言，所以当分析完了CopyOnWriteArrayList后，CopyOnWriteArraySet的分析就非常简单，谢谢各位园友的观看~

