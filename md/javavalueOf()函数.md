valueOf() 方法用于返回给定参数的原生 Number 对象值，参数可以是原生数据类型, String等。

该方法是静态方法。该方法可以接收两个参数一个是字符串，一个是基数。

### 语法

该方法有以下几种语法格式：

    
    
    static Integer valueOf(int i)
    static Integer valueOf(String s)
    static Integer valueOf(String s, int radix)

### 参数

  * **i** \-- Integer 对象的整数。

  * **s** \-- Integer 对象的字符串。

  * **radix** \--在解析字符串 s 时使用的基数，用于指定使用的进制数。

### 返回值

  * **Integer valueOf(int i)：** 返回一个表示指定的 int 值的 Integer 实例。

  * **Integer valueOf(String s):** 返回保存指定的 String 的值的 Integer 对象。

  * **Integer valueOf(String s, int radix):** 返回一个 Integer 对象，该对象中保存了用第二个参数提供的基数进行解析时从指定的 String 中提取的值。

### 实例

    
    
     public class Test{ 
    public static void main(String args[]){
            Integer x =Integer.valueOf(9);
            Double c = Double.valueOf(5);
            Float a = Float.valueOf("80");               
    
            Integer b = Integer.valueOf("444",16);   // 使用 16 进制
    
            System.out.println(x); 
            System.out.println(c);
            System.out.println(a);
            System.out.println(b);
        }
    }

编译以上程序，输出结果为：

    
    
    9
    5.0
    80.0
    1092

