
    def log(func):
        def wrapper():
            print "func.__name__:",func.__name__
            return func()#返回函数调用
        return wrapper#返回函数名字
    
    @log
    def now():
        print "I am Banner brother!"
    now()  
    #结果

#func.__name__: now  
#I am Banner brother!

    
    
    #含有参数的装饰器
    def log(text):
        def decorator(func):
            def wrapper(*args, **kw):
                print("%s %s():" % (text, func.__name__))
                return func(*args, **kw)
            return wrapper
        return decorator
    @log("execute")
    def now():
        print("2015-3-25")
    #结果：
    #execute now():
    #2015-3-25

