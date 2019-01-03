## 作为函数的参数

一个匿名的函数传递给一个方法或者函数的时候，scala会尽量推断出参数类型。例如一个完整的匿名函数作为参数可以写为

    
    
    scala> def compute(f: (Double)=>Double) = f(3)
    compute: (f: Double => Double)Double
    
    //传递一个匿名函数作为compute的参数
    scala> compute((x: Double) => 2 * x)
    res1: Double = 6.0
    

如果参数`x`在`=>`右侧只出现一次，可以用`_`替代这个参数，简写为

    
    
    scala> compute(2 * _)
    res2: Double = 6.0
    

更常见的使用方式为

    
    
    scala> (1 to 9).filter(_ % 2 == 0)
    res0: scala.collection.immutable.IndexedSeq[Int] = Vector(2, 4, 6, 8)
    
    scala> (1 to 3).map(_ * 3)
    res1: scala.collection.immutable.IndexedSeq[Int] = Vector(3, 6, 9)
    

以上所说的为一元函数，那么对于二元函数，即有两个参数x和y的函数，是如何使用`_`的？可以参考sortWith方法的定义  
def sortWith(lt: (T, T) ⇒ Boolean): Array[T]  
这个方法的参数官方解释为

> the comparison function which tests whether its first argument precedes its
second argument in the desired ordering.

这个方法需要的参数是一个二元函数，而且函数参数的类型为T，例如

    
    
    scala> List(10, 5, 8, 1, 7).sortWith(_ < _)
    res0: List[Int] = List(1, 5, 7, 8, 10)
    

可以用`_`分别表示二元函数中的参数x和y。

## 作为标识符

例如定义一个变量`val _num = 123`

## 作为通配符

  * import语句  
例如`import scala.math._`

  * case语句  
例如

    
    
    object MatchTest extends App {
      def matchTest(x: Int): String = x match {
        case 1 => "one"
        case 2 => "two"
        case _ => "many"
      }
      println(matchTest(3))
    }
    

  * 元组（tuple）  
例如

    
    
    //可以定义一个tuple
    scala> val t = (1, 3.14, "Fred")
    t: (Int, Double, String) = (1,3.14,Fred)
    //可以用_1，_2，_3访问这个元组
    scala> t._1
    res3: Int = 1
    
    scala> t._2
    res4: Double = 3.14
    
    scala> t._3
    res5: String = Fred
    

可以通过模式匹配获取元组的元素，当不需要某个值的时候可以使用`_`替代，例如

    
    
    scala> val t = (1, 3.14, "Fred")
    t: (Int, Double, String) = (1,3.14,Fred)
    
    scala> val (first, second, _) = t
    first: Int = 1
    second: Double = 3.14
    
    scala> val (first, _, _) = t
    first: Int = 1
    

## 下划线和其他符号组合的使用方式

  * 下划线与等号（_=）  
自定义setter方法，请参见[《Overriding def with var in
Scala》](https://www.jianshu.com/p/4a3362ec22de)

  * 下划线与星号（_*）  
1.变长参数  
例如定义一个变长参数的方法sum，然后计算1-5的和，可以写为

    
    
    scala> def sum(args: Int*) = {
         | var result = 0
         | for (arg <- args) result += arg
         | result
         | }
    sum: (args: Int*)Int
    
    scala> val s = sum(1,2,3,4,5)
    s: Int = 15
    

但是如果使用这种方式就会报错

    
    
    scala> val s = sum(1 to 5)
    <console>:12: error: type mismatch;
     found   : scala.collection.immutable.Range.Inclusive
     required: Int
           val s = sum(1 to 5)
                         ^
    

这种情况必须在后面写上`: _*`将`1 to 5`转化为参数序列

    
    
    scala> val s = sum(1 to 5: _*)
    s: Int = 15
    

2.变量声明中的模式  
例如，下面代码分别将arr中的第一个和第二个值赋给first和second

    
    
    scala> val arr = Array(1,2,3,4,5)
    arr: Array[Int] = Array(1, 2, 3, 4, 5)
    
    scala> val Array(1, 2, _*) = arr
    
    scala> val Array(first, second, _*) = arr
    first: Int = 1
    second: Int = 2
    

链接：https://www.jianshu.com/p/0497583ec538  
  

