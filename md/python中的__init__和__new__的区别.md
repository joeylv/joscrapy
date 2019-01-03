**一、__init__ 方法是什么？(init前后的线是双下划线)**

使用Python写过面向对象的代码的同学，可能对 __init__ 方法已经非常熟悉了，__init__ 方法通常用在初始化一个类实例的时候。例如：

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

    
    
     1 # -*- coding: utf-8 -*-
     2 
     3 class Person(object):
     4     """Silly Person"""
     5 
     6     def __init__(self, name, age):
     7         self.name = name
     8         self.age = age
     9 
    10     def __str__(self):
    11         return "<Person: %s(%s)>" % (self.name, self.age)
    12 
    13 if __name__ == "__main__":
    14     piglei = Person("piglei", 24)
    15     print piglei

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

这样便是__init__最普通的用法了。但__init__其实不是实例化一个类的时候第一个被调用 的方法。当使用 Persion(name, age)
这样的表达式来实例化一个类时，最先被调用的方法 其实是 __new__ 方法。

**二、__new__方法是什么？**

__new__方法接受的参数虽然也是和__init__一样，但__init__是在类实例创建之后调用，而 __new__方法正是创建这个类实例的方法。

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

    
    
     1 # -*- coding: utf-8 -*-
     2 
     3 class Person(object):
     4     """Silly Person"""
     5 
     6     def __new__(cls, name, age):
     7         print "__new__ called."
     8         return super(Person, cls).__new__(cls, name, age)
     9 
    10     def __init__(self, name, age):
    11         print "__init__ called."
    12         self.name = name
    13         self.age = age
    14 
    15     def __str__(self):
    16         return "<Person: %s(%s)>" % (self.name, self.age)
    17 
    18 if __name__ == "__main__":
    19     piglei = Person("piglei", 24)
    20     print piglei

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

执行结果 :

    
    
    1 piglei@macbook-pro:blog$ python new_and_init.py
    2 __new__ called.
    3 __init__ called.
    4 <Person: piglei(24)>

通过运行这段代码，我们可以看到，__new__方法的调用是发生在__init__之前的。其实当 你实例化一个类的时候，具体的执行逻辑是这样的：

1.p = Person(name, age)  
2.首先执行使用name和age参数来执行Person类的__new__方法，这个__new__方法会 返回Person类的一个实例（通常情况下是使用
super(Persion, cls).__new__(cls, … …) 这样的方式），  
3.然后利用这个实例来调用类的__init__方法，上一步里面__new__产生的实例也就是 __init__里面的的 self

所以，__init__ 和 __new__ 最主要的区别在于：  
1.__init__ 通常用于初始化一个新实例，控制这个初始化的过程，比如添加一些属性， 做一些额外的操作，发生在类实例被创建完以后。它是实例级别的方法。  
2.__new__ 通常用于控制生成一个新实例的过程。它是类级别的方法。  
但是说了这么多，__new__最通常的用法是什么呢，我们什么时候需要__new__？

**三、__new__的作用**

依照Python官方文档的说法，__new__方法主要是当你继承一些不可变的class时(比如int, str, tuple)，
提供给你一个自定义这些类的实例化过程的途径。还有就是实现自定义的metaclass。  
首先我们来看一下第一个功能，具体我们可以用int来作为一个例子：  
假如我们需要一个永远都是正数的整数类型，通过集成int，我们可能会写出这样的代码。

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

    
    
    1 class PositiveInteger(int):
    2     def __init__(self, value):
    3         super(PositiveInteger, self).__init__(self, abs(value))
    4 
    5 i = PositiveInteger(-3)
    6 print i

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

但运行后会发现，结果根本不是我们想的那样，我们任然得到了-3。这是因为对于int这种 不可变的对象，我们只有重载它的__new__方法才能起到自定义的作用。  
这是修改后的代码：

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

    
    
    1 class PositiveInteger(int):
    2     def __new__(cls, value):
    3         return super(PositiveInteger, cls).__new__(cls, abs(value))
    4 
    5 i = PositiveInteger(-3)
    6 print i

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

通过重载__new__方法，我们实现了需要的功能。  
另外一个作用，关于自定义metaclass。其实我最早接触__new__的时候，就是因为需要自定义
metaclass，但鉴于篇幅原因，我们下次再来讲python中的metaclass和__new__的关系。

**四、用__new__来实现单例**

事实上，当我们理解了__new__方法后，我们还可以利用它来做一些其他有趣的事情，比如实现 设计模式中的 单例模式(singleton) 。  
因为类每一次实例化后产生的过程都是通过__new__来控制的，所以通过重载__new__方法，我们 可以很简单的实现单例模式。

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

    
    
     1 class Singleton(object):
     2     def __new__(cls):
     3         # 关键在于这，每一次实例化的时候，我们都只会返回这同一个instance对象
     4         if not hasattr(cls, "instance"):
     5             cls.instance = super(Singleton, cls).__new__(cls)
     6         return cls.instance
     7 
     8 obj1 = Singleton()
     9 obj2 = Singleton()
    10 
    11 obj1.attr1 = "value1"
    12 print obj1.attr1, obj2.attr1
    13 print obj1 is obj2

![复制代码](../md/img/ggzhangxiaochao/copycode.gif)

输出结果：

value1 value1  
True

可以看到obj1和obj2是同一个实例。

