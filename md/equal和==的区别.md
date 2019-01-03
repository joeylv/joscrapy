equal和“==”都是表示相等的意思，但是它们在进行实际的相等判定的时候，却有着非常大的区别

先看看一个例子

    
    
     1  public class EqualTest{
     2      public static void main(string[] args){
     3          String str1 = "abcd";
     4     String str2 = "abcd";
     5     String str3 = new String("abcd");
     6         
     7     System.out.println(str1==str2);    
     8     System.out.println(str1==str3);
     9     System.out.println(str1.equals(str3));
    10   }
    11 }

以上代码中定义了三个字符串变量，它们的值都是"abcd"，按理来说，它们的结果应该都是true。但是事实上，它们执行得结果是

true

false

true

第二个为false的原因在于str1和str3指向的是不同的对象。

==运用在基本数据类型的时候，通过比较它们的实际值来判定是否相同；但是用于比较引用类型的时候。则是比较两个引用的地址是否相同，也就是说是否指向同一个对象。通过new
string()来创建的字符串会单独生成一个对象，所以str1和str3指向的并不是同一个对象。java的双引号表达式本身就会创建一个字符串对象。

equal()方法是java.lang.Object的方法。也就是说所有的java类都会有这个方法。它可以被覆盖重写，通过自定义的方式来判定两个对象是否相等，其中默认的方式与==相同。但是java.lang.String类并不同，它是不可以被继承的。它的equal()方法用来比较字符串的字符串序列是否完全相等。

如：

    
    
     1 public class Student {
     2     private String name;
     3     private int age ;
     4     
     5     public Student(String name ,int age){
     6         this.name = name;
     7         this.age = age;
     8     }
     9     public boolean equals(Object object){
    10         Student student = (Student) object;
    11         return this.name.equals(student.name)&&this.age==student.age;
    12     }
    13 }
    14 
    15 public class EqualTest {
    16 
    17     public static void main(String[] args) {
    18         Student stud1 = new Student("liming", 11);
    19         Student stud2 = new Student("liming", 11);
    20         System.out.println(stud1.equals(stud2));
    21     }
    22 
    23 }

执行结果为true

