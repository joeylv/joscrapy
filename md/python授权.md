1.“包装”意思是一个已经存在的对象进行包装，不管他是数据类型还是一段代码，可以是对一个已经存在的对象增加新的，删除不要的或者修改其他已经存在的功能

2.包装 包括定义一个类，他的实例拥有标准类型的核心行为，换句话说，他现在不仅能唱能跳，还能像原类型一样步行。  
![这里写图片描述](https://img-blog.csdn.net/20160926113332749)  
这个图片说明了在类中包装的类型看起来像什么样子，在图的中心为标准类型的核心行为，但他也通过新的或者最新的功能，甚至可能通过访问实际数据的不同方法得到提高

3.实现授权是包装的一个特性，可用于简化处理相关命令性功能，采用也存在的功能以达到最大限度的代码重用。

4.实现授权的关键点是覆盖`__getattr__()`
方法，在代码中包含一个对getattr()内建函数的调用，调用getattr()得到默认对象的属性（数据属性或者方法）并返回他以便于访问或者调用。

    
    
    #! /usr/bin/env python
    #coding:utf-8
    
    """
    包装对象的授权
    
    """
    
    class WrapMe(object):
        def __init__(self,obj):
            self.__obj=obj;
    
        def get(self):
            return self.__obj
    
        def __str__(self):
            return self.__obj
    
        __repr__=__str__
    
        def __getattr__(self, item):
            "这个方法用于实现授权，即返回的对象可以使用接受到的对象的属性（方法，函数），但是不能使用原有对象的特殊行为"
            return getattr(self.__obj,item)
    
    
    #以复数为例
    m=WrapMe(3.5+4.2j)
    print m.real    #3.5 这就是复数这个对象的方法，此时因为进行了授权，我们任然可以使用复数的属性
    """
    搜索属性的顺序是 解释器将试着在局部名称空间中查找哪个名字，如果没有就搜索类名称空间，最后如果两个搜索都是失败了，搜索则对原对象开始授权请求，此时__getattr__()会被调用
    """
    
    
    "getattr()这个函数没有办法做到让对象使用原有对象的特殊行为，比如列表的切片属性"
    m1=WrapMe(["a","b","c"])
    #print m1[1]   #TypeError: "WrapMe" object does not support indexing
    #这就是为什么我们要在类中创建一个get（）函数，他返回了原来的对象
    m_list=m1.get()
    print m_list[1]  #b 成功解决问题
    
    
    
    """
    对比
    """
    class WrapMe_compare(object):
        def __init__(self,obj):
            self.__obj=obj;
    
        def get(self):
            return self.__obj
    
        def __str__(self):
            return self.__obj
    
        __repr__=__str__
    
    mc=WrapMe_compare(3.5+4.2j)
    #print mc.real()  #AttributeError: "WrapMe_compare" object has no attribute "real"  这就是没有进行授权

5.包装标准类型

    
    
    #!/usr/bin/env python
    #coding:utf-8
    
    """
    包装标准类型
    """
    from time import time,ctime,sleep
    
    class TimeWrapMe(object):
        def __init__(self,obj):
            self.__data=obj;
            self.__mtime=self.__ctime=self.__atime=time();
    
        def get(self):
            "获取属性，需要修改访问时间"
            self.__atime=time();
            return self.__data;
    
    
        def gettimeval(self,t_type):
            if not isinstance(t_type,str) or t_type not in "cma":
                raise TypeError,"argument of "c","m","a"";
            return getattr(self,"_%s__%stime"%(self.__class__.__name__,t_type));   #相当于getattr(self,_TimeWrapMe__(c|m|a)time)，传过去的是修改，更新，创建的时间
    
        def gettimestr(self,t_type):
            "获取时间，返回一个经time.ctime()函数格式化的字符串形式的时间"
            """
            ctime(seconds) -> string
            """
            return ctime(self.gettimeval(t_type));
    
        def set(self,obj):
            "修改实例属性，同时自动刷新修改时间"
            self.__mtime=time();
            self.__data=obj;
    
        def __repr__(self):
            self.__atime=time();
            return self.__data;
    
        def __str__(self):
            self.__atime=time();
            return str(self.__data);
    
        def __getattr__(self, item):
            "授权"
            self.__atime=time();
            return getattr(self.__data,item);
    
    
    t=TimeWrapMe(932)
    print t.gettimestr("c")
    print t.gettimestr("m")
    print t.gettimestr("a")
    print "{:*^30}".format("*")
    sleep(3)    #3秒之后再次进行访问
    print t.get()
    print t.gettimestr("c")
    print t.gettimestr("m")
    print t.gettimestr("a")
    
    结果：
    Mon Sep 26 13:04:16 2016
    Mon Sep 26 13:04:16 2016
    Mon Sep 26 13:04:16 2016
    ******************************
    932
    Mon Sep 26 13:04:16 2016
    Mon Sep 26 13:04:16 2016
    Mon Sep 26 13:04:19 2016  #访问时间发生了改变

