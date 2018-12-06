##java提高篇（十九）-----数组之二

##
## 前面一节主要介绍了数组的基本概念，对什么是数组稍微深入了一点点，在这篇博文中主要介绍数组的其他方面。
##三、性能？请优先考虑数组

##
## 在java中有很多方式来存储一系列数据，而且在操作上面比数组方便的多？但为什么我们还需要使用数组，而不是替代它呢？数组与其他种类的容器之间的区别有三个方面：效率、类型和保存基本类型的能力。在java中，数组是一种效率最高的存储和随机访问对象引用序列的方式。

##
## 在项目设计中数组使用的越来越少了，而且它确实是没有List、Set这些集合使用方便，但是在某些方面数组还是存在一些优势的，例如：速度，而且集合类的底层也都是通过数组来实现的。	--------这是ArrayList的add()------    public boolean add(E e) {    ensureCapacity(size + 1);  // Increments modCount!!    elementData[size++] = e;    return true;    	}

##
## 下面利用数组和list来做一些操作比较。

##
## 一、求和	Long time1 = System.currentTimeMillis();        for(int i = 0 ; i < 100000000 ;i++){            sum += arrays[i%10];        	}        Long time2 = System.currentTimeMillis();        System.out.println("数组求和所花费时间：" + (time2 - time1) + "毫秒");        Long time3 = System.currentTimeMillis();        for (int i = 0; i < 100000000; i++) {            sum  += list.get(i%10);        	}        Long time4 = System.currentTimeMillis();        System.out.println("List求和所花费时间：" + (time4 - time3) + "毫秒");--------------Output:数组求和所花费时间：696毫秒List求和所花费时间：3498毫秒

##
## 从上面的时间消耗上面来说数组对于基本类型的求和计算的速度是集合的5倍左右。其实在list集合中，求和当中有一个致命的动作：list.get(i)。这个动作是进行拆箱动作，Integer对象通过intValue方法自动转换成一个int基本类型，在这里就产生了不必要的性能消耗。

##
##  所以在性能要求较高的场景中请优先考虑数组。
##四、变长数组？

##
## 数组是定长的，一旦初始化声明后是不可改变长度的。这对我们在实际开发中是非常不方便的，聪明的我们肯定是可以找到方法来实现的。就如java不能实现多重继承一样，我们一样可以利用内部类和接口来实现(请参考：java提高篇(九)-----实现多重继承)。

##
## 那么如何来实现变长数组呢？我们可以利用List集合add方法里面的扩容思路来模拟实现。下面是ArrayList的扩容方法:	public void ensureCapacity(int minCapacity) {        modCount++;          int oldCapacity = elementData.length;        /**         * 若当前需要的长度超过数组长度时进行扩容处理         */        if (minCapacity > oldCapacity) {            Object oldData[] = elementData;                int newCapacity = (oldCapacity * 3) / 2 + 1;    //扩容            if (newCapacity < minCapacity)                newCapacity = minCapacity;            //拷贝数组，生成新的数组            elementData = Arrays.copyOf(elementData, newCapacity);        	}    	}

##
## 这段代码对我们有用的地方就在于if语句后面。它的思路是将原始数组拷贝到新数组中，新数组是原始数组长度的1.5倍。所以模拟的数组扩容代码如下：	public class ArrayUtils {    /**     * @desc 对数组进行扩容     * @author chenssy     * @data 2013-12-8     * @param <T>     * @param datas 原始数组     * @param newLen 扩容大小     * @return T[]     */    public static <T> T[] expandCapacity(T[] datas,int newLen){        newLen = newLen < 0 ? datas.length :datas.length + newLen;           //生成一个新的数组        return Arrays.copyOf(datas, newLen);    	}        /**     * @desc 对数组进行扩容处理，1.5倍     * @author chenssy     * @data 2013-12-8     * @param <T>     * @param datas  原始数组     * @return T[]     */    public static <T> T[] expandCapacity(T[] datas){        int newLen = (datas.length * 3) / 2;      //扩容原始数组的1.5倍        //生成一个新的数组        return Arrays.copyOf(datas, newLen);    	}        /**     * @desc 对数组进行扩容处理，     * @author chenssy     * @data 2013-12-8     * @param <T>     * @param datas 原始数组     * @param mulitiple 扩容的倍数     * @return T[]     */    public static <T> T[] expandCapacityMul(T[] datas,int mulitiple){        mulitiple = mulitiple < 0 ? 1 : mulitiple;        int newLen = datas.length * mulitiple;        return Arrays.copyOf(datas,newLen );    	}	}

##
## 通过这种迂回的方式我们可以实现数组的扩容。因此在项目中如果确实需要变长的数据集，数组也是在考虑范围之内的，我们不能因为他是固定长度而排斥他！
##五、数组复制问题

##
## 以前在做集合拷贝的时候由于集合没有拷贝的方法，所以一个一个的复制是非常麻烦的，所以我就干脆使用List.toArray()方法转换成数组然后再通过Arrays.copyOf拷贝，在转换成集合，个人觉得非常方便，殊不知我已经陷入了其中的陷进！我们知道若数组元素为对象，则数组里面数据是对象引用	public class Test {    public static void main(String[] args) {        Person person_01 = new Person("chenssy_01");                Person[] persons1 = new Person[]{person_01	};        Person[] persons2 = Arrays.copyOf(persons1,persons1.length);                System.out.println("数组persons1:");        display(persons1);        System.out.println("---------------------");        System.out.println("数组persons2:");        display(persons2);        //改变其值        persons2[0].setName("chessy_02");        System.out.println("------------改变其值后------------");        System.out.println("数组persons1:");        display(persons1);        System.out.println("---------------------");        System.out.println("数组persons2:");        display(persons2);    	}    public static void display(Person[] persons){        for(Person person : persons){            System.out.println(person.toString());        	}    	}	}-------------Output:数组persons1:姓名是：chenssy_01---------------------数组persons2:姓名是：chenssy_01------------改变其值后------------数组persons1:姓名是：chessy_02---------------------数组persons2:姓名是：chessy_02

##
## 从结果中发现,persons1中的值也发生了改变，这是典型的浅拷贝问题。所以通过Arrays.copyOf()方法产生的数组是一个浅拷贝。同时数组的clone()方法也是，集合的clone()方法也是，所以我们在使用拷贝方法的同时一定要注意浅拷贝这问题。

##
## 有关于深浅拷贝的博文，参考： 渐析java的浅拷贝和深拷贝：http://www.cnblogs.com/chenssy/p/3308489.html。 使用序列化实现对象的拷贝：http://www.cnblogs.com/chenssy/p/3382979.html。
##六、数组转换为List注意地方

##
## 我们经常需要使用到Arrays这个工具的asList()方法将其转换成列表。方便是方便，但是有时候会出现莫名其妙的问题。如下：	public static void main(String[] args) {        int[] datas = new int[]{1,2,3,4,5	};        List list = Arrays.asList(datas);        System.out.println(list.size());    	}------------Output:1

##
## 结果是1,是的你没有看错, 结果就是1。但是为什么会是1而不是5呢？先看asList()的源码	public static <T> List<T> asList(T... a) {        return new ArrayList<T>(a);    	}

##
## 注意这个参数:T…a，这个参数是一个泛型的变长参数，我们知道基本数据类型是不可能泛型化的，也是就说8个基本数据类型是不可作为泛型参数的，但是为什么编译器没有报错呢？这是因为在java中，数组会当做一个对象来处理，它是可以泛型的，所以我们的程序是把一个int型的数组作为了T的类型，所以在转换之后List中就只会存在一个类型为int数组的元素了。所以我们这样的程序System.out.println(datas.equals(list.get(0)));输出结果肯定是true。当然如果将int改为Integer，则长度就会变成5了。

##
## 我们在看下面程序：	enum Week{Sum,Mon,Tue,Web,Thu,Fri,Sat	}    public static void main(String[] args) {        Week[] weeks = {Week.Sum,Week.Mon,Week.Tue,Week.Web,Week.Thu,Week.Fri	};        List<Week> list = Arrays.asList(weeks);        list.add(Week.Sat);    	}

##
## 这个程序非常简单，就是讲一个数组转换成list，然后改变集合中值，但是运行呢？	Exception in thread "main" java.lang.UnsupportedOperationException    at java.util.AbstractList.add(AbstractList.java:131)    at java.util.AbstractList.add(AbstractList.java:91)    at com.array.Test.main(Test.java:18)

##
## 编译没错，但是运行竟然出现了异常错误！UnsupportedOperationException ，当不支持请求的操作时，就会抛出该异常。从某种程度上来说就是不支持add方法，我们知道这是不可能的！什么原因引起这个异常呢？先看asList()的源代码：	public static <T> List<T> asList(T... a) {        return new ArrayList<T>(a);    	}

##
## 这里是直接返回一个ArrayList对象返回，但是注意这个ArrayList并不是java.util.ArrayList,而是Arrays工具类的一个内之类：	private static class ArrayList<E> extends AbstractList<E>    implements RandomAccess, java.io.Serializable{        private static final long serialVersionUID = -2764017481108945198L;        private final E[] a;        ArrayList(E[] array) {            if (array==null)                throw new NullPointerException();        a = array;    	}       /** 省略方法 **/    	}

##
## 但是这个内部类并没有提供add()方法，那么查看父类：	public boolean add(E e) {    add(size(), e);    return true;    	}    public void add(int index, E element) {    throw new UnsupportedOperationException();    	}

##
##  这里父类仅仅只是提供了方法，方法的具体实现却没有，所以具体的实现需要子类自己来提供，但是非常遗憾

##
##这个内部类ArrayList并没有提高add的实现方法。在ArrayList中，它主要提供了如下几个方法：

##
## 1、size：元素数量

##
## 2、toArray：转换为数组，实现了数组的浅拷贝。

##
## 3、get：获得指定元素。

##
## 4、contains：是否包含某元素。

##
## 所以综上所述，asList返回的是一个长度不可变的列表。数组是多长，转换成的列表是多长，我们是无法通过add、remove来增加或者减少其长度的。

##
##

##
## 参考文献：《编写高质量代码--改善Java程序的151个建议》