##java提高篇(十三)-----equals()方法总结
##equals()

##
## 超类Object中有这个equals()方法，该方法主要用于比较两个对象是否相等。该方法的源码如下：	public boolean equals(Object obj) {    return (this == obj);    	}

##
## 我们知道所有的对象都拥有标识(内存地址)和状态(数据)，同时“==”比较两个对象的的内存地址，所以说使用Object的equals()方法是比较两个对象的内存地址是否相等，即若object1.equals(object2)为true，则表示equals1和equals2实际上是引用同一个对象。虽然有时候Object的equals()方法可以满足我们一些基本的要求，但是我们必须要清楚我们很大部分时间都是进行两个对象的比较，这个时候Object的equals()方法就不可以了，实际上JDK中，String、Math等封装类都对equals()方法进行了重写。下面是String的equals()方法：	public boolean equals(Object anObject) {    if (this == anObject) {        return true;    	}    if (anObject instanceof String) {        String anotherString = (String)anObject;        int n = count;        if (n == anotherString.count) {        char v1[] = value;        char v2[] = anotherString.value;        int i = offset;        int j = anotherString.offset;        while (n-- != 0) {            if (v1[i++] != v2[j++])            return false;        	}        return true;        	}    	}    return false;    	}

##
## 对于这个代码段:if (v1[i++] != v2[j++])return false;我们可以非常清晰的看到String的equals()方法是进行内容比较，而不是引用比较。至于其他的封装类都差不多。

##
## 在Java规范中，它对equals()方法的使用必须要遵循如下几个规则：

##
## equals 方法在非空对象引用上实现相等关系： 

##
## 1、自反性：对于任何非空引用值 x，x.equals(x) 都应返回 true。 

##
## 2、对称性：对于任何非空引用值 x 和 y，当且仅当 y.equals(x) 返回 true 时，x.equals(y) 才应返回 true。 

##
## 3、传递性：对于任何非空引用值 x、y 和 z，如果 x.equals(y) 返回 true，并且 y.equals(z) 返回 true，那么 x.equals(z) 应返回 true。 

##
## 4、一致性：对于任何非空引用值 x 和 y，多次调用 x.equals(y) 始终返回 true 或始终返回 false，前提是对象上 equals 比较中所用的信息没有被修改。 

##
## 5、 对于任何非空引用值 x，x.equals(null) 都应返回 false。 

##
## 对于上面几个规则，我们在使用的过程中最好遵守，否则会出现意想不到的错误。

##
## 在java中进行比较，我们需要根据比较的类型来选择合适的比较方式：

##
## 1) 对象域，使用equals方法 。  2) 类型安全的枚举，使用equals或== 。      3) 可能为null的对象域 : 使用 == 和 equals 。      4) 数组域 : 使用 Arrays.equals 。      5) 除float和double外的原始数据类型 : 使用 == 。      6) float类型: 使用Float.foatToIntBits转换成int类型，然后使用==。  7) double类型: 使用Double.doubleToLongBit转换成long类型，然后使用==。

##
##至于6）、7）为什么需要进行转换，我们可以参考他们相应封装类的equals()方法，下面的是Float类的：	public boolean equals(Object obj) {    return (obj instanceof Float)           &amp;&amp; (floatToIntBits(((Float)obj).value) == floatToIntBits(value));    	}

##
##原因嘛，里面提到了两点：	However, there are two exceptions:If f1 and f2 both representFloat.NaN, then the equals method returnstrue, even though Float.NaN==Float.NaNhas the value false.If <code>f1 represents +0.0f whilef2 represents -0.0f, or viceversa, the equal test has the valuefalse, even though 0.0f==-0.0fhas the value true.
## 在equals()中使用getClass进行类型判断

##
## 我们在覆写equals()方法时，一般都是推荐使用getClass来进行类型判断，不是使用instanceof。我们都清楚instanceof的作用是判断其左边对象是否为其右边类的实例，返回boolean类型的数据。可以用来判断继承中的子类的实例是否为父类的实现。注意后面这句话：可以用来判断继承中的子类的实例是否为父类的实现，正是这句话在作怪。我们先看如下实例(摘自《高质量代码 改善java程序的151个建议》)。

##
## 父类：Person	public class Person {    protected String name;    public String getName() {        return name;    	}    public void setName(String name) {        this.name = name;    	}        public Person(String name){        this.name = name;    	}        public boolean equals(Object object){        if(object instanceof Person){            Person p = (Person) object;            if(p.getName() == null || name == null){                return false;            	}            else{                return name.equalsIgnoreCase(p.getName());            	}        	}        return false;    	}	}

##
## 子类：Employee	public class Employee extends Person{    private int id;        public int getId() {        return id;    	}    public void setId(int id) {        this.id = id;    	}    public Employee(String name,int id){        super(name);        this.id = id;    	}        /**     * 重写equals()方法     */    public boolean equals(Object object){        if(object instanceof Employee){            Employee e = (Employee) object;            return super.equals(object) &amp;&amp; e.getId() == id;        	}        return false;    	}	}

##
## 上面父类Person和子类Employee都重写了equals(),不过Employee比父类多了一个id属性。测试程序如下：	public class Test {    public static void main(String[] args) {        Employee e1 = new Employee("chenssy", 23);        Employee e2 = new Employee("chenssy", 24);        Person p1 = new Person("chenssy");                System.out.println(p1.equals(e1));        System.out.println(p1.equals(e2));        System.out.println(e1.equals(e2));    	}	}

##
## 上面定义了两个员工和一个普通人，虽然他们同名，但是他们肯定不是同一人，所以按理来说输出结果应该全部都是false，但是事与愿违，结果是：true、true、false。

##
## 对于那e1!=e2我们非常容易理解，因为他们不仅需要比较name,还需要比较id。但是p1即等于e1也等于e2，这是非常奇怪的，因为e1、e2明明是两个不同的类，但为什么会出现这个情况？首先p1.equals(e1)，是调用p1的equals方法，该方法使用instanceof关键字来检查e1是否为Person类，这里我们再看看instanceof：判断其左边对象是否为其右边类的实例，也可以用来判断继承中的子类的实例是否为父类的实现。他们两者存在继承关系，肯定会返回true了，而两者name又相同，所以结果肯定是true。

##
## 所以出现上面的情况就是使用了关键字instanceof，这是非常容易“专空子”的。故在覆写equals时推荐使用getClass进行类型判断。而不是使用instanceof。

##
##巩固基础，提高技术，不惧困难，攀登高峰！！！！！！