### 抽象类

抽象类是用来捕捉子类的通用特性的
。它不能被实例化，只能被用作子类的超类。抽象类是被用来创建继承层级里子类的模板。以JDK中的GenericServlet为例：  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

</td>  
<td>

`public` `abstract` `class` `GenericServlet ``implements` `Servlet,
ServletConfig, Serializable {`

` ``// abstract method`

` ``abstract` `void` `service(ServletRequest req, ServletResponse res);`

` ``void` `init() {`

` ``// Its implementation`

` ``}`

` ``// other method related to Servlet`

`}`

</td> </tr> </table>

当HttpServlet类继承GenericServlet时，它提供了service方法的实现：  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

</td>  
<td>

`public` `class` `HttpServlet ``extends` `GenericServlet {`

` ``void` `service(ServletRequest req, ServletResponse res) {`

` ``// implementation`

` ``}`

` ``protected` `void` `doGet(HttpServletRequest req, HttpServletResponse resp)
{`

` ``// Implementation`

` ``}`

` ``protected` `void` `doPost(HttpServletRequest req, HttpServletResponse
resp) {`

` ``// Implementation`

` ``}`

` ``// some other methods related to HttpServlet`

`}`

</td> </tr> </table>

### 接口

接口是抽象方法的集合。如果一个类实现了某个接口，那么它就继承了这个接口的抽象方法。这就像契约模式，如果实现了这个接口，那么就必须确保使用这些方法。接口只是一种形式，接口自身不能做任何事情。以Externalizable接口为例：  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

</td>  
<td>

`public` `interface` `Externalizable ``extends` `Serializable {`

` ``void` `writeExternal(ObjectOutput out) ``throws` `IOException;`

` ``void` `readExternal(ObjectInput in) ``throws` `IOException,
ClassNotFoundException;`

`}`

</td> </tr> </table>

当你实现这个接口时，你就需要实现上面的两个方法：  
  
<table>  
<tr>  
<td>

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

</td>  
<td>

`public` `class` `Employee ``implements` `Externalizable {`

` ``int` `employeeId;`

` ``String employeeName;`

` ``@Override`

` ``public` `void` `readExternal(ObjectInput in) ``throws` `IOException,
ClassNotFoundException {`

` ``employeeId = in.readInt();`

` ``employeeName = (String) in.readObject();`

` ``}`

` ``@Override`

` ``public` `void` `writeExternal(ObjectOutput out) ``throws` `IOException {`

` ``out.writeInt(employeeId);`

` ``out.writeObject(employeeName);`

` ``}`

`}`

</td> </tr> </table>

### 抽象类和接口的对比  
  
<table>  
<tr>  
<td>

**参数**

</td>  
<td>

**抽象类**

</td>  
<td>

**接口**

</td> </tr>  
<tr>  
<td>

默认的方法实现

</td>  
<td>

它可以有默认的方法实现

</td>  
<td>

接口完全是抽象的。它根本不存在方法的实现

</td> </tr>  
<tr>  
<td>

实现

</td>  
<td>

子类使用 **extends** 关键字来继承抽象类。如果子类不是抽象类的话，它需要提供抽象类中所有声明的方法的实现。

</td>  
<td>

子类使用关键字 **implements** 来实现接口。它需要提供接口中所有声明的方法的实现

</td> </tr>  
<tr>  
<td>

构造器

</td>  
<td>

抽象类可以有构造器

</td>  
<td>

接口不能有构造器

</td> </tr>  
<tr>  
<td>

与正常Java类的区别

</td>  
<td>

除了你不能实例化抽象类之外，它和普通Java类没有任何区别

</td>  
<td>

接口是完全不同的类型

</td> </tr>  
<tr>  
<td>

访问修饰符

</td>  
<td>

抽象方法可以有 **public** 、 **protected** 和 **default** 这些修饰符

</td>  
<td>

接口方法默认修饰符是 **public** 。你不可以使用其它修饰符。

</td> </tr>  
<tr>  
<td>

main方法

</td>  
<td>

抽象方法可以有main方法并且我们可以运行它

</td>  
<td>

接口没有main方法，因此我们不能运行它。

</td> </tr>  
<tr>  
<td>

多继承

</td>  
<td>

抽象方法可以继承一个类和实现多个接口

</td>  
<td>

接口只可以继承一个或多个其它接口

</td> </tr>  
<tr>  
<td>

速度

</td>  
<td>

它比接口速度要快

</td>  
<td>

接口是稍微有点慢的，因为它需要时间去寻找在类中实现的方法。

</td> </tr>  
<tr>  
<td>

添加新方法

</td>  
<td>

如果你往抽象类中添加新的方法，你可以给它提供默认的实现。因此你不需要改变你现在的代码。

</td>  
<td>

如果你往接口中添加方法，那么你必须改变实现该接口的类。

</td> </tr> </table>

### 什么时候使用抽象类和接口

  * 如果你拥有一些方法并且想让它们中的一些有默认实现，那么使用抽象类吧。
  * 如果你想实现多重继承，那么你必须使用接口。由于 **Java不支持多继承** ，子类不能够继承多个类，但可以实现多个接口。因此你就可以使用接口来解决它。
  * 如果基本功能在不断改变，那么就需要使用抽象类。如果不断改变基本功能并且使用接口，那么就需要改变所有实现了该接口的类。

### Java8中的默认方法和静态方法

Oracle已经开始尝试向接口中引入默认方法和静态方法，以此来减少抽象类和接口之间的差异。现在，我们可以为接口提供默认实现的方法了并且不用强制子类来实现它。这类内容我将在下篇博客进行阐述。

