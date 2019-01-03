在很多情况下我们都需要将一个对象转换为String类型。一般来说有三种方法可以实现：Object.toString()、(String)Object、String.valueOf(Object)。下面对这三种方法一一分析：

一、采用Object.toString()

toString方法是java.lang.Object对象的一个public方法。在java中任何对象都会继承Object对象，所以一般来说任何对象都可以调用toString这个方法。这是采用该种方法时，常派生类会覆盖Object里的toString()方法。

但是在使用该方法时要注意，必须保证Object不是null值，否则将抛出NullPointerException异常。

二、采用(String)Object

该方法是一个标准的类型转换的方法，可以将Object转换为String。但是在使用该方法是要注意的是需要转换的类型必须是能够转换为String的，否则会出现CalssCastException异常错误。

    
    
    1         Object o = new Integer(100);
    2         String string = (String)o;

这段程序代码会出现java.lang.ClassCastException: java.lang.Integer cannot be cast to
java.lang.String。因为将Integer类型强制转换为String类型，无法通过。

三、String.valueOf(Object)

上面我们使用Object.toString()方法时需要担心null问题。但是使用该方法无需担心null值问题。因为在使用String.valueOf(Object)时，它会判断Object是否为空值，如果是，则返回null。下面为String.valueOf(Object)的源码：

    
    
    1 public static String valueOf(Object obj) {
    2      return (obj == null) ? "null" : obj.toString(); 
    3 
    4 }

从上面我们可以看出两点：一是不需要担心null问题。二是它是以toString()方法为基础的。

但是一定要注意：当object为null时，String.valueOf（object）的值是字符串对象："null"，而不是null！！！

  
  

