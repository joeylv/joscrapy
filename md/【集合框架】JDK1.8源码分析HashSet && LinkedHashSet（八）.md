##【集合框架】JDK1.8源码分析HashSet && LinkedHashSet（八）

##
##一、前言

##
##　　分析完了List的两个主要类之后，我们来分析Set接口下的类，HashSet和LinkedHashSet，其实，在分析完HashMap与LinkedHashMap之后，再来分析HashSet与LinkedHashSet，就会变成异常简单，下面开始进行分析。

##
##二、数据结构

##
##　　2.1 HashSet数据结构

##
##　　老规矩，先上数据结构，因为HashSet底层是基于HashMap 或者 LinkedHashMap实现的，所以HashSet数据结构就是HashMap或者LinkedHashMap的数据结构，因为前面已经分析过了，所以不再累赘。直接看这里，JDK1.8源码分析之HashMap（一） &amp;&amp;JDK1.8源码分析之LinkedHashMap（二）。

##
##　　2.2 LinkedHashSet数据结构

##
##　　LinkedHashSet基于LinkedHashMap实现，所以数据结构直接看这里。JDK1.8源码分析之LinkedHashMap（二）。

##
##三、源码分析

##
##　　3.1 HashSet　　

##
##　　1. 类的继承关系	public class HashSet<E>    extends AbstractSet<E>    implements Set<E>, Cloneable, java.io.Serializable

##
##　　2. 类的属性　 ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	public class HashSet<E>    extends AbstractSet<E>    implements Set<E>, Cloneable, java.io.Serializable{    // 版本序列号    static final long serialVersionUID = -5024744406713321676L;    // 键值Map    private transient HashMap<E,Object> map;    // 用作所有键对应的值，键所对应的值都相等    private static final Object PRESENT = new Object();	}View Code

##
##　　说明：HashSet中由于只包含键，不包含值，由于在底层具体实现时，使用的HashMap或者是LinkedHashMap(可以指定构造函数来确定使用哪种结构)，我们知道HashMap是键值对存储，所以为了适应HashMap存储，HashSet增加了一个PRESENT类域（类所有），所有的键都有同一个值（PRESENT）。

##
##　　3. 其他分析

##
##　　add、contains、remove函数都是基于HashMap或者LinkedHashMap做的操作，之前已经给出源码分析，不再累赘。

##
##　　3.2 LinkedHashSet

##
##　　1. 类的继承关系　　	public class LinkedHashSet<E>    extends HashSet<E>    implements Set<E>, Cloneable, java.io.Serializable

##
##　　说明LinkedHashSet继承自HashSet，也实现了一些接口，不再累赘。

##
##　　2. 其他说明

##
##　　LinkedHashSet会调用HashSet的父类构造函数，让其底层实现为LinkedHashMap，这样就很好的实现了LinkedHashSet所需要的功能。

##
##四、总结

##
##　　HashSet、LinkedHashSet与HashMap、LinkedHashMap相对应。分析了HashMap、LinkedHashMap的源码之后，HashSet、LinkedHashSet也就很浅显易懂了。谢谢各位园友观看~

##
##

##
##　　