首先我们先来看如下代码示例：

    
    
    1 public class Test_1 {
    2     public static void main(String[] args) {
    3         System.out.println(0.06+0.01);
    4         System.out.println(1.0-0.42);
    5         System.out.println(4.015*100);
    6         System.out.println(303.1/1000);
    7     }
    8     
    9 }

运行结果如下。

0.06999999999999999

0.5800000000000001

401.49999999999994

0.30310000000000004

你认为你看错了，但结果却是是这样的。问题在哪里呢？原因在于我们的计算机是二进制的。浮点数没有办法是用二进制进行精确表示。我们的CPU表示浮点数由两个部分组成：指数和尾数，这样的表示方法一般都会失去一定的精确度，有些浮点数运算也会产生一定的误差。如：2.4的二进制表示并非就是精确的2.4。反而最为接近的二进制表示是
2.3999999999999999。浮点数的值实际上是由一个特定的数学公式计算得到的。

其实java的float只能用来进行科学计算或工程计算，在大多数的商业计算中，一般采用java.math.BigDecimal类来进行精确计算。

在使用BigDecimal类来进行计算的时候，主要分为以下步骤：

1、用float或者double变量构建BigDecimal对象。

2、通过调用BigDecimal的加，减，乘，除等相应的方法进行算术运算。

3、把BigDecimal对象转换成float，double，int等类型。

一般来说，可以使用BigDecimal的构造方法或者静态方法的valueOf()方法把基本类型的变量构建成BigDecimal对象。

    
    
    1 BigDecimal b1 = new BigDecimal(Double.toString(0.48));
    2 BigDecimal b2 = BigDecimal.valueOf(0.48);

对于常用的加，减，乘，除，BigDecimal类提供了相应的成员方法。

    
    
    1 public BigDecimal add(BigDecimal value);                        //加法
    2 public BigDecimal subtract(BigDecimal value);                   //减法 
    3 public BigDecimal multiply(BigDecimal value);                   //乘法
    4 public BigDecimal divide(BigDecimal value);                     //除法

  
进行相应的计算后，我们可能需要将BigDecimal对象转换成相应的基本数据类型的变量，可以使用floatValue()，doubleValue()等方法。

下面是一个工具类，该工具类提供加，减，乘，除运算。

    
    
     1 public class Arith {
     2     /**
     3      * 提供精确加法计算的add方法
     4      * @param value1 被加数
     5      * @param value2 加数
     6      * @return 两个参数的和
     7      */
     8     public static double add(double value1,double value2){
     9         BigDecimal b1 = new BigDecimal(Double.valueOf(value1));
    10         BigDecimal b2 = new BigDecimal(Double.valueOf(value2));
    11         return b1.add(b2).doubleValue();
    12     }
    13     
    14     /**
    15      * 提供精确减法运算的sub方法
    16      * @param value1 被减数
    17      * @param value2 减数
    18      * @return 两个参数的差
    19      */
    20     public static double sub(double value1,double value2){
    21         BigDecimal b1 = new BigDecimal(Double.valueOf(value1));
    22         BigDecimal b2 = new BigDecimal(Double.valueOf(value2));
    23         return b1.subtract(b2).doubleValue();
    24     }
    25     
    26     /**
    27      * 提供精确乘法运算的mul方法
    28      * @param value1 被乘数
    29      * @param value2 乘数
    30      * @return 两个参数的积
    31      */
    32     public static double mul(double value1,double value2){
    33         BigDecimal b1 = new BigDecimal(Double.valueOf(value1));
    34         BigDecimal b2 = new BigDecimal(Double.valueOf(value2));
    35         return b1.multiply(b2).doubleValue();
    36     }
    37     
    38     /**
    39      * 提供精确的除法运算方法div
    40      * @param value1 被除数
    41      * @param value2 除数
    42      * @param scale 精确范围
    43      * @return 两个参数的商
    44      * @throws IllegalAccessException
    45      */
    46     public static double div(double value1,double value2,int scale) throws IllegalAccessException{
    47         //如果精确范围小于0，抛出异常信息
    48         if(scale<0){         
    49             throw new IllegalAccessException("精确度不能小于0");
    50         }
    51         BigDecimal b1 = new BigDecimal(Double.valueOf(value1));
    52         BigDecimal b2 = new BigDecimal(Double.valueOf(value2));
    53         return b1.divide(b2, scale).doubleValue();    
    54     }
    55 }

  

