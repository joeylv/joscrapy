## 前言

>
`Java`中的`Object`提供了很多方法供所有的类使用，特别是`toString`、`hashCode`、`equals`、`getClass`等方法，在日常开发中作用很大，`Guava`中包含`Objects`类，其提供了很多更为强大的方法。

## Objects

> `Objects`是`Object`的子类，其提供了`equal`、`toStringHelper`等方法，下面根据一个示例来分析源码。

### 示例

    
    
    package com.hust.grid.leesf.guavalearning;
    
    import com.google.common.base.Objects;
    
    public class ObjectsTest {
        public static void main(String[] args) {
            Integer i1 = new Integer(10);
            Integer i2 = new Integer(10);
            System.out.println(Objects.equal(i1, i2));
            System.out.println(Objects.toStringHelper("Person").add("name", "leesf").add("age", 25));
        }
    }
    
    

运行结果：

> true  
>  Person{name=leesf, age=25}

可以看到，`Objects`对象可以很轻松的比较两个对象是否相等，并且还可以使用`toStringHelper`来格式化对象的属性，清晰易懂，便于定位异常。

### equal方法

>
`Java`中的`Object`对象的`equals`方法，传递一个参数；而`Objects`提供`equal`方法，传递两个参数，来比较两个对象是否相等。

    
    
    public static boolean equal(@Nullable Object a, @Nullable Object b) {
      return a == b || (a != null && a.equals(b));
    }
    

> 可以看到，`equal`方法只是预先进行了一次判断，若为同一个引用，则返回`true`，否则，调用`Object
a`的`equals`方法，若其重写了`equals`方法，则调用自身方法，否则调用父类的`equals`方法，直至最后`Object`类的`equals`方法。

### toStringHelper方法

>
该方法是`Objects`中非常有用的方法，可以格式化对象的输出，一般情况下是重写`toString`方法，然后将对象的属性逐一写出，而`Objects`中提供了`toStringHelper`方法，可以很方便的格式化输出。

  * `toStringHelper`会生成一个`ToStringHelper`对象，若传递的为非`String`类型值，则首先会调用`simpleName`方法简化类名，如传递的为整形`3`，`simpleName`方法则返回`Integer`。

### ToStringHelper类

> 在调用`toStringHelper`方法返回一个`ToStringHelper`对象，其结构如下。

    
    
    public static final class ToStringHelper {
        private final String className;
        private ValueHolder holderHead = new ValueHolder();
        private ValueHolder holderTail = holderHead;
        private boolean omitNullValues = false;
        
        // methods
    ｝
    

可以看到其存在一个`className`属性，用来保存类名，如`Person`、`Integer`等字符串；存在一个`ValueHolder`类型的`holderHead`对象，表示链表的头结点；存在一个`ValueHolder`类型的`holderTail`对象，表示链表的尾节点；存在一个`omitNullValues`变量用来指示是否跳过`null`值，其中`ValueHolder`是实际存放元素的地方，其结构如下。

    
    
    private static final class ValueHolder {
        String name;
        Object value;
        ValueHolder next;
    }
    

可以看到`ValueHolder`会单链表结构，当调用`add`方法时，其就在链表末尾添加一个节点。

### add方法

>
在调用`toStirngHelper`方法返回`ToStringHelper`对象后，可调用`add`方法。`add`方法整个调用会在链表的末尾添加一个`ValueHolder`节点，并且使用`ToStringHelper`的`holderTail`对象指向尾节点。

### toString方法

> 当打印时，会调用`ValueHolder`对象的`toString`方法，其会首先输出`className{`，然后遍历链表，将包含`key-
value`或只包含`value`类型的节点按照指定格式输出，最后添加`}`。

## 总结

> `Objects`类源码相对简单，其提供了格式化对象的方法，使用也非常简单，非常方便在实际开发的时候使用。

