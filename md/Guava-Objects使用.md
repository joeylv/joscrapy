##Guava-Objects使用前言

##
##Java中的Object提供了很多方法供所有的类使用，特别是toString、hashCode、equals、getClass等方法，在日常开发中作用很大，Guava中包含Objects类，其提供了很多更为强大的方法。Objects

##
##Objects是Object的子类，其提供了equal、toStringHelper等方法，下面根据一个示例来分析源码。示例package com.hust.grid.leesf.guavalearning;import com.google.common.base.Objects;public class ObjectsTest {    public static void main(String[] args) {        Integer i1 = new Integer(10);        Integer i2 = new Integer(10);        System.out.println(Objects.equal(i1, i2));        System.out.println(Objects.toStringHelper("Person").add("name", "leesf").add("age", 25));    	}	}

##
##运行结果：

##
##truePerson{name=leesf, age=25	}

##
##可以看到，Objects对象可以很轻松的比较两个对象是否相等，并且还可以使用toStringHelper来格式化对象的属性，清晰易懂，便于定位异常。equal方法

##
##Java中的Object对象的equals方法，传递一个参数；而Objects提供equal方法，传递两个参数，来比较两个对象是否相等。public static boolean equal(@Nullable Object a, @Nullable Object b) {  return a == b || (a != null &amp;&amp; a.equals(b));	}

##
##可以看到，equal方法只是预先进行了一次判断，若为同一个引用，则返回true，否则，调用Object a的equals方法，若其重写了equals方法，则调用自身方法，否则调用父类的equals方法，直至最后Object类的equals方法。toStringHelper方法

##
##该方法是Objects中非常有用的方法，可以格式化对象的输出，一般情况下是重写toString方法，然后将对象的属性逐一写出，而Objects中提供了toStringHelper方法，可以很方便的格式化输出。toStringHelper会生成一个ToStringHelper对象，若传递的为非String类型值，则首先会调用simpleName方法简化类名，如传递的为整形3，simpleName方法则返回Integer。ToStringHelper类

##
##在调用toStringHelper方法返回一个ToStringHelper对象，其结构如下。public static final class ToStringHelper {    private final String className;    private ValueHolder holderHead = new ValueHolder();    private ValueHolder holderTail = holderHead;    private boolean omitNullValues = false;        // methods｝

##
##可以看到其存在一个className属性，用来保存类名，如Person、Integer等字符串；存在一个ValueHolder类型的holderHead对象，表示链表的头结点；存在一个ValueHolder类型的holderTail对象，表示链表的尾节点；存在一个omitNullValues变量用来指示是否跳过null值，其中ValueHolder是实际存放元素的地方，其结构如下。private static final class ValueHolder {    String name;    Object value;    ValueHolder next;	}

##
##可以看到ValueHolder会单链表结构，当调用add方法时，其就在链表末尾添加一个节点。add方法

##
##在调用toStirngHelper方法返回ToStringHelper对象后，可调用add方法。add方法整个调用会在链表的末尾添加一个ValueHolder节点，并且使用ToStringHelper的holderTail对象指向尾节点。toString方法

##
##当打印时，会调用ValueHolder对象的toString方法，其会首先输出className{，然后遍历链表，将包含key-value或只包含value类型的节点按照指定格式输出，最后添加	}。总结

##
##Objects类源码相对简单，其提供了格式化对象的方法，使用也非常简单，非常方便在实际开发的时候使用。