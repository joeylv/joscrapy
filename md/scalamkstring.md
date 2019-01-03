如果你想要把集合元素转化为字符串，可能还会添加分隔符，前缀，后缀。  
Solution  
使用mkString方法来打印一个集合内容，下面给一个简单的例子：

    
    
    scala> val a = Array("apple", "banana", "cherry")
    a: Array[String] = Array(apple, banana, cherry)
    scala> a.mkString
    res3: String = applebananacherry

使用mkString方法你会看到结果并不漂亮，我们来加一个分隔符：

    
    
    scala> a.mkString(",")
    res4: String = apple,banana,cherry
    
    scala> a.mkString(" ")
    res5: String = apple banana cherry

这样看起来就好看多了，同样你可以添加一个前缀和一个后缀：

    
    
    scala> a.mkString("[", ", ", "]")
    res6: String = [apple, banana, cherry]
    如果你想把一个潜逃集合转化为一个字符串，比如嵌套数组，首先你要展开这个嵌套数组，然后调用mkString方法：
    scala> val a = Array(Array("a", "b"), Array("c", "d"))
    a: Array[Array[String]] = Array(Array(a, b), Array(c, d))
    
    scala> a.flatten.mkString(",")
    res7: String = a,b,c,d

