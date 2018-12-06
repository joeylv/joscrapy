##【集合框架】JDK1.8源码分析之Comparable && Comparator（九）

##
##一、前言

##
##　　在Java集合框架里面，各种集合的操作很大程度上都离不开Comparable和Comparator，虽然它们与集合没有显示的关系，但是它们只有在集合里面的时候才能发挥最大的威力。下面是开始我们的分析。

##
##二、示例

##
##　　在正式讲解Comparable与Comparator之前，我们通过一个例子来直观的感受一下它们的使用。

##
##　　首先，定义好我们的Person类　　	class Person {    String name;    int age;        public Person(String name, int age) {        this.name = name;        this.age = age;    	}        public String toString() {        return "[name = " + name + ", age = " + age + "]";    	}	}

##
##　　其次编写测试代码，代码如下　	public class Test {    public static void main(String[] args) {        List<String> nameLists = new ArrayList<String>();        nameLists.addAll(Arrays.asList("aa", "ab", "bc", "ba"));        Collections.sort(nameLists);        System.out.println(nameLists);                List<Person> personLists = new ArrayList<Person>();  personLists.addAll(Arrays.asList(new Person("leesf", 24), new Person("dyd", 24), new Person("ld", 0)));  Collections.sort(personLists); // 出错  System.out.println(personLists);    	}	}

##
##　　说明：上述代码是两份同样的逻辑，同样的操作，但是，对于List<String>不会报错，对于List<Person>类型就会报错，为什么？为了解决这个问题，我们需要讲解今天的主角Comparable &amp;&amp; Comparator。如果知道怎么解决的园友也不妨瞧瞧，开始分析。

##
##三、源码分析

##
##　　3.1 Comparable

##
##　　1. 类的继承关系　	public interface Comparable<T>

##
##　　说明：Comparable就是一个泛型接口，很简单。

##
##　　2. compareTo方法	public int compareTo(T o);

##
##　　说明：compareTo方法就构成了整个Comparable源码的唯一的有效方法。

##
##　　3.2 Comparator

##
##　　1. 类的继承关系　　	public interface Comparator<T>

##
##　　说明：同样，Comparator也是一个泛型接口，很简单。

##
##　　2. compare方法　	int compare(T o1, T o2);

##
##　　说明：Comparator接口中一个核心的方法。

##
##　　3. equals方法	boolean equals(Object obj);

##
##　　说明：此方法是也是一个比较重要的方法，但是一般不会使用，可以直接使用Object对象的equals方法（所有对象都继承自Object）。

##
##　　其他在JDK1.8后添加的方法对我们的分析不产生影响，有感兴趣的读者可以自行阅读源码，了解更多细节。

##
##四、解决思路

##
##　　4.1. 分析问题

##
##　　在我们的程序中，List<String>类型是可以通过编译的，但是List<Person>类型却不行，我们猜测肯定是和元素类型String、Person有关系。既然是这样，我们来看String在Java中的定义。	public final class String    implements java.io.Serializable, Comparable<String>, CharSequence

##
##　　说明：我们平时说String为final类型，不可被继承，查看源码，确实是这样。注意查看String实现的接口，直觉告诉我们Comparable<String>很重要，之前我们已经分析过了Comparable接口，既然String实现了这个接口，那么肯定也实现了compareTo方法，顺藤摸瓜，String的compareTo方法如下:	public int compareTo(String anotherString) {    // this对象所对应的字符串的长度    int len1 = value.length;     // 参数对象所对应字符串的长度    int len2 = anotherString.value.length;     // 取长度较小者    int lim = Math.min(len1, len2);     // value是String底层的实现，为char[]类型数组    // this对象所对应的字符串    char v1[] = value;    // 参数对象所对应的字符串    char v2[] = anotherString.value;        int k = 0;    // 遍历两个字符串    while (k < lim) {        char c1 = v1[k];        char c2 = v2[k];        // 如果不相等，则返回        if (c1 != c2) {            return c1 - c2;        	}        // 继续遍历        k++;    	}    // 一个字符串是另外一个字符串的子串    return len1 - len2;	}

##
##　　说明：我们可以看到String中compareTo方法具体的实现。比较同一索引位置的字符大小。

##
##　　分析了String的compareTo方法后，并且按照在compareTo方法中的逻辑进行排序，之于如何排序涉及到具体的算法问题，以后我们会进行分析。于是乎，我们知道了之前示例程序的问题所在：Person类没有实现Comparable接口。

##
##　　4.2. 解决问题

##
##　　1. 修改我们的Person类的定义，修改为如下：　　	Person implements Comparable<Person>

##
##　　2. 实现compareTo方法，并实现我们自己的想要比较的逻辑，如我们想要首先根据年龄比较（采用升序），若年龄相同，则根据姓名的ASCII顺序来比较。那么我们实现的compareTo方法如下：　	    int compareTo(Person anthor) {        if (this.age < anthor.age)            return -1;        else if (this.age == anthor.age)            return this.name.compareTo(anthor.name);        else            return 1;    	}

##
##　　说明：于是乎，修改后的程序如下：

##
##　　Person类代码如下　　	class Person implements Comparable<Person> {    String name;    int age;        public Person(String name, int age) {        this.name = name;        this.age = age;    	}        public String toString() {        return "[name = " + name + ", age = " + age + "]";    	}        @Override    public int compareTo(Person anthor) {        if (this.age < anthor.age)            return -1;        else if (this.age == anthor.age)            return this.name.compareTo(anthor.name);        else            return 1;    	}	}

##
##　　测试类代码不变

##
##　　运行结果如下：

##
##　　[aa, ab, ba, bc]　　[[name = ld, age = 0], [name = dyd, age = 24], [name = leesf, age = 24]]

##
##　　说明：我们可以看到Person类的排序确实按照了在compareTo方法中定义的逻辑进行排序。这样，就修正了错误。

##
##五、问题提出

##
##　　上面的Comparable接口解决之前出现的问题。但是，如果我现在不想按照刚刚的逻辑进行排序了，想按照一套新的逻辑排序，如只根据姓名比较来进行排序。此时，我们需要修改Comparable接口的compare方法，添加新的比较逻辑。过了一久，用户又希望采用别的逻辑进行排序，那么，又得重新修改compareTo方法里面的逻辑，可以通过标志位来做if判断，用来判断用户想要使用哪种比较逻辑，这样会造成会造成代码很臃肿，不易于维护。此时，一种更好的解决办法就是使用Comparator接口。

##
##　　5.1 比较逻辑一

##
##　　首先根据年龄比较（采用升序），若年龄相同，则根据姓名的ASCII顺序来比较。

##
##　　那么我们可以定义这样的Comparator，具体代码如下：　	class ComparatorFirst implements Comparator<Person> {        public int compare(Person o1, Person o2) {        if (o1.age < o2.age)            return -1;        else if (o1.age == o2.age)            return o1.name.compareTo(o2.name);        else             return 1;    	}    	}

##
##　　测试代码做如下修改：

##
##　　将Collections.sort(personLists) 改成 Collections.sort(personLists, new ComparatorFirst());

##
##　　sort的两种重载方法，后一种允许我们传入自定义的比较器。

##
##　　运行结果如下：

##
##　　[aa, ab, ba, bc]　　[[name = ld, age = 0], [name = dyd, age = 24], [name = leesf, age = 24]]

##
##　　结果说明：我们看到和前面使用Comparable接口得到的结果相同。

##
##　　5.2 比较逻辑二

##
##　　直接根据姓名的ASCII顺序来比较。

##
##　　则我们可以定义如下比较器　　	class ComparatorSecond implements Comparator<Person> {    public int compare(Person o1, Person o2) {        return o1.name.compareTo(o2.name);    	}    	}

##
##　　测试代码做如下修改：

##
##　　将Collections.sort(personLists) 改成 Collections.sort(personLists, new ComparatorSecond());

##
##　　运行结果：

##
##　　[aa, ab, ba, bc]　　[[name = dyd, age = 24], [name = ld, age = 0], [name = leesf, age = 24]]

##
##　　说明：我们可以看到这个比较逻辑和上一个比较器的逻辑不相同，但是也同样完成了用户的逻辑。

##
##　　我们还可以按照我们的意愿定义其他更多的比较器，只需要在compareTo中正确完成我们的逻辑即可。

##
##　　5.3 Comparator优势

##
##　　从上面两个例子我们应该可以感受到Comparator比较器比Comparable接口更加灵活，可以更友好的完成用户所定义的各种比较逻辑。

##
##六、总结

##
##　　分析了Comparable和Comparator，掌握了在不同的场景中使用不同的比较器，写此篇博客后对两者的使用和区别也更加的清晰了。谢谢各位园友的观看~

##
##　　

##
##　　

##
##　　

##
##　　

##
##　　

##
##　　

##
##　　

##
##

##
##　　