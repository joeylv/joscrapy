java 中的instanceof
运算符是用来在运行时指出对象是否是特定类的一个实例。instanceof通过返回一个布尔值来指出，这个对象是否是这个特定类或者是它的子类的一个实例。

用法：  
result = object instanceof class  
参数：  
Result：布尔类型。  
Object：必选项。任意对象表达式。  
Class：必选项。任意已定义的对象类。  
说明：  
如果 object 是 class 的一个实例，则 instanceof 运算符返回 true。如果 object 不是指定类的一个实例，或者 object
是 null，则返回 false。

但是instanceof在Java的编译状态和运行状态是有区别的：

在编译状态中，class可以是object对象的父类，自身类，子类。在这三种情况下Java编译时不会报错。

在运行转态中，class可以是object对象的父类，自身类，不能是子类。在前两种情况下result的结果为true，最后一种为false。但是class为子类时编译不会报错。运行结果为false。

例子：

接口Person

public interface Person {  
public void eat();  
}

实现类People

public class People implements Person {  
private int a=0;  
@Override  
public void eat() {  
System.out.println("======"+a);  
  
}

}

子类xiaoming：

public class xiaoming extends People {  
private String name;

@Override  
public void eat() {  
System.out.println("+++++++++");  
}  
}

主函数

public static void main(String[] args) {  
People p=new People();  
xiaoming x=new xiaoming();  
System.out.println(p instanceof Person);  
System.out.println(p instanceof xiaoming); -----2  
System.out.println(x instanceof Person);  
System.out.println(x instanceof People);  
}

注意：上面2处的代码在编译时不会报错。

运行结果：

true  
false  
true  
true

