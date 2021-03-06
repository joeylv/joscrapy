Struts 2提供了大量的标签来开发表现层页面。这些标签的大部分，都可以在各种表现层技术中使用。

Struts 2 将所有标签分为以下三类：

UI(用户界面)：主要用于生成HTML元素的标签

非UI标签：主要用于数据访问、逻辑控制等的标签

Ajax标签：用于Ajax支持的标签

1、控制标签

1)、if/elseif/else ：都是用来进行分支控制的

语法格式为：

    
    
     1  <s: if test="表达式">
     2     标签体
     3    </s:if>
     4     <s: elseif test="表达式">
     5     标签体
     6    </s:elseif>
     7    
     8     <s: else test="表达式">
     9     标签体
    10    </s:else>

对于上面三个标签的组合使用，只有<s:if.../>可以单独使用。其余两个必须和<s:if.../>配合使用。在这个当中可以与多个<s:elseif.../>标签结合使用。

2）、iterator：用于将List、Map、ArrayList等集合进行循环遍历  
迭代输出时，可以指定一下三个属性：

对于上面三个标签的组合使用，只有<s:if.../>可以单独使用。其余两个必须和<s:if.../>配合使用。在这个当中可以与多个<s:elseif.../>标签结合使用。  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

value属性指定的是被迭代的集合。如果没有指定value属性，则使用ValueStack栈顶的集合

</td> </tr>  
<tr>  
<td>

id

</td>  
<td>

id属性指定集合里元素的ID

</td> </tr>  
<tr>  
<td>

status

</td>  
<td>

status属性指定迭代的IteratorStatus实例。通过该实例可以判断当前迭代元素的属性

</td> </tr> </table>

3）、append标签：用于将多个集合对象拼接起来，组成一个新的集合。它允许通过一个<iterator.../>标签来完成对多个集合的迭代

该标签需要指定一个var属性，该属性确定拼接生成的新集合的名字。

<s:append.../>可以接受多个<s:param.../>子标签，每个子标签指定一个集合。

4）、generator标签：可以将指定字符串按指定分隔符分隔成多个子串。

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

count

</td>  
<td>

该属性指定生成集合中元素的总数

</td> </tr>  
<tr>  
<td>

separator

</td>  
<td>

该属性指定用于解析字符串的分隔符

</td> </tr>  
<tr>  
<td>

val

</td>  
<td>

该属性指定被解析的字符串

</td> </tr>  
<tr>  
<td>

converter

</td>  
<td>

该属性指定一个转换器，该转换器负责将集合中的每个字符串转换成对象

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性，则将生成的Iterator对象放入StackContext中

</td> </tr> </table>

5）、merge标签：和append标签相似。

假如有两个集合{"abc","def","ghi"} 、{"123","456","789"}

通过append方式拼接，新集合的元素顺序为：

abc def ghi 123 456 789

通过merge方式拼接，新集合的元素顺序为：

abc 123 def 456 ghi 789

6)、subset标签：用于取得集合的子集

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

count

</td>  
<td>

该属性指定子集合中元素的个数。如果不指定该属性，则默认取得源集合的全部元素

</td> </tr>  
<tr>  
<td>

source

</td>  
<td>

该属性指定源集合。如果不指定该属性，则默认取得ValueStack栈顶的集合

</td> </tr>  
<tr>  
<td>

start

</td>  
<td>

该属性指定子集从源集合的第几个元素开始截取。默认从第一个

</td> </tr>  
<tr>  
<td>

decider

</td>  
<td>

该属性指定由开发者子集决定是否选中该元素

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性，则将生成的Iterator对象设置为page范围的属性

</td> </tr> </table>

7）、sort标签：用于对指定的集合元素进行排序。

进行排序时，必须提供自己的排序规则。即实现自己的Comparator。

有如下几个属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

comparator

</td>  
<td>

该属性指定指定进行排序的Comparator实例

</td> </tr>  
<tr>  
<td>

source

</td>  
<td>

该属性指定被排序的集合。如果不指定，则默认对ValueStack栈顶的集合进行排序

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性，则将生成的Iterator对象设置成page范围的属性，不放入StackContext中

</td> </tr> </table>

数据标签：

数据标签主要用于提供各种数据访问相关的功能，包含显示一个Action里的属性，以及生成国际化输出等功能。

1）、action标签

使用action标签可以允许在jsp页面中直接调用Action。如果指定了executeResult参数的属性值为true，该标签还会把Action的处理结果包含到本页面中来。

它有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果定义了该属性,那么该Action将会被放入ValueStack中

</td> </tr>  
<tr>  
<td>

name

</td>  
<td>

指定该标签调用哪个Action

</td> </tr>  
<tr>  
<td>

namespace

</td>  
<td>

该属性指定了该标签调用的Action所在的namespace

</td> </tr>  
<tr>  
<td>

executeResult

</td>  
<td>

该属性指定了是否要将Action的处理结果页面包含到本页面中

</td> </tr>  
<tr>  
<td>

ignoreContextParams

</td>  
<td>

该属性指定了该页面中的请求参数是否需要传入调用的action

</td> </tr> </table>

2）、bean标签：用于创建一个javaBean实例。

它有如下两个属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

name

</td>  
<td>

该属性指定了要实例化的javaBean的实现类

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性，则该JavaBean实例会被放入发哦Stack Context中，并放入requestScope中

</td> </tr> </table>

3）、date标签：该标签用于格式化一个日期。还可以计算指定日期和当前时刻的时差

有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

form

</td>  
<td>

如果指定了该属性，将根据该属性指定的格式来格式化日期

</td> </tr>  
<tr>  
<td>

nice

</td>  
<td>

该属性用于指定是否输出指定日期和当前时刻之间的时差。该属性值只能为true或false

</td> </tr>  
<tr>  
<td>

name

</td>  
<td>

该属性指定要格式化的日期值

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性格式化后的字符串将被放入Stack Context中

</td> </tr> </table>

注：如果既指定了nice="true"，也指定了format属性，则会输出指定日期和当前时刻之间的时差，format属性会失效。

4)、debug标签：它会在页面生成一个超级链接，通过该链接可以查看到ValueStack和Stack Context中所有的信息

5）include标签：用于将一个jsp页面或者一个Servlet包含到本页面中。

它有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

该属性指定需要被包含的jsp页面或者Servlet

</td> </tr> </table>

还可以为该标签指定多个<s:param.../>子标签，用于将多个参数值传入被包含的jsp页面或者Servlet

6）、param标签：用于为其他标签提供参数

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

name

</td>  
<td>

指定需要设置参数的参数名

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

指定需要设置参数的参数值

</td> </tr> </table>

7）、push标签：用于将某个值放到ValueStack的栈顶

有下面一个属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

该属性指定需要放到ValueStack栈顶的值

</td> </tr> </table>

只有在push标签内时，被push标签放入ValueStack中的对象才存在；一旦离开了push标签，则刚刚放入的对象将会立即被移除ValueStack

8）、set标签：该标签用于将某个值放入到指定的范围内。

Set标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

scope

</td>  
<td>

指定新变量被放置的范围，该属性可以接受application、session、request、page或者action5个值。默认为action

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

指定将赋给变量的值

</td> </tr>  
<tr>  
<td>

var

</td>  
<td>

如果指定了该属性，则会将被放入到request范围中，并被放入ONGL的Stack Context中

</td> </tr> </table>

9）、url标签：该标签用于生成一个URL地址。

可以通过为url标签指定param子元素，从而向指定URL发送请求参数。

10）、property标签：该标签的作用是输出指定值。

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

default

</td>  
<td>

如果需要输出的属性值为null。则显示default属性指定的值

</td> </tr>  
<tr>  
<td>

escape

</td>  
<td>

指定是否escape HTML代码

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

指定需要输出的属性值

</td> </tr> </table>

表单标签

1）checkboxlist标签：创建复选框。相当于HTML中的checkbox标签：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

list

</td>  
<td>

根据指定的集合来生成多个复写框

</td> </tr>  
<tr>  
<td>

listKey

</td>  
<td>

该属性指定集合元素中的某个属性作为复选框的value。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的value

</td> </tr>  
<tr>  
<td>

listValue

</td>  
<td>

该属性指定集合元素中的某个属性作为复选框的标签。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的标签

</td> </tr> </table>

2）、doubleselect标签：该标签用于生成一个级联列表框。当选择第一个下拉列表框时，第二个下拉列表框的内容会随着改变。

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

list

</td>  
<td>

指定用于输出第一个下拉类表框中选项的集合

</td> </tr>  
<tr>  
<td>

listKey

</td>  
<td>

该属性指定集合元素中的某个属性作为第一个下拉列表框的value。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的value

</td> </tr>  
<tr>  
<td>

listValue

</td>  
<td>

该属性指定集合元素中的某个属性作为第一个下拉列表框的标签。如果集合是Map，则可以使用key和value指定Map对象的key和value作为第一个下拉列表框的标签

</td> </tr>  
<tr>  
<td>

doubleList

</td>  
<td>

指定用于输出第二个下拉类表框中选项的集合

</td> </tr>  
<tr>  
<td>

doubleListKey

</td>  
<td>

该属性指定集合元素中的某个属性作为第二个下拉列表框的value。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的value

</td> </tr>  
<tr>  
<td>

doubleListValue

</td>  
<td>

该属性指定集合元素中的某个属性作为第二个下拉列表框的标签。如果集合是Map，则可以使用key和value指定Map对象的key和value作为第二个下拉列表框的标签

</td> </tr>  
<tr>  
<td>

doubleName

</td>  
<td>

指定第二个下拉列表框的name属性

</td> </tr> </table>

4）、head标签：用于生产HTML主要页面的head部分。

5）、optiontransferselect标签：该标签会生成两个列表选择框。并生成系列的按钮用于控制各选项在两个下拉列表之间的移动、升降。当提交表单时，两个列表选择框对应的请求参数都会被提交。

该属性有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

addAllToLeftLabel

</td>  
<td>

设置全部移动到左边按钮上的文本

</td> </tr>  
<tr>  
<td>

addAllToRightLabel

</td>  
<td>

设置全部移动到右边按钮上的文本

</td> </tr>  
<tr>  
<td>

addToLeftLabel

</td>  
<td>

设置移动到左边按钮上的文本

</td> </tr>  
<tr>  
<td>

addToRightLabel

</td>  
<td>

设置移动到右边按钮上的文本

</td> </tr>  
<tr>  
<td>

allowAddAllToLeft

</td>  
<td>

设置是否出现全部移动到左边的按钮

</td> </tr>  
<tr>  
<td>

allowAddAllToRight

</td>  
<td>

设置是否出现全部移动到右边的按钮

</td> </tr>  
<tr>  
<td>

allowAddToLeft

</td>  
<td>

设置是否出现移动到左边的按钮

</td> </tr>  
<tr>  
<td>

allowAddToRight

</td>  
<td>

设置是否出现移动到右边的按钮

</td> </tr>  
<tr>  
<td>

leftTitle

</td>  
<td>

设置左边列表框的标题

</td> </tr>  
<tr>  
<td>

rightTitle

</td>  
<td>

设置右边列表框的标题

</td> </tr>  
<tr>  
<td>

allowSelectAll

</td>  
<td>

设置是否出现全部选择按钮

</td> </tr>  
<tr>  
<td>

selectAllLabel

</td>  
<td>

设置全部选择按钮上的文本

</td> </tr>  
<tr>  
<td>

doubleList

</td>  
<td>

设置用于创建第二个下拉选择框的集合

</td> </tr>  
<tr>  
<td>

doubleListKey

</td>  
<td>

设置用于创建第二个下拉列表框的选项value的属性

</td> </tr>  
<tr>  
<td>

doubleListValue

</td>  
<td>

设置用于创建第二个下拉列表框的选项label的属性

</td> </tr>  
<tr>  
<td>

doubleName

</td>  
<td>

设置第二个下拉选择框的name属性

</td> </tr>  
<tr>  
<td>

doubleValue

</td>  
<td>

设置第二个下拉选择框的value属性

</td> </tr>  
<tr>  
<td>

doubleMultiple

</td>  
<td>

设置第二个下拉选择框是否允许多选

</td> </tr>  
<tr>  
<td>

list

</td>  
<td>

设置用于创建第一个下拉选择框的集合

</td> </tr>  
<tr>  
<td>

listKey

</td>  
<td>

设置用于创建第一个下拉列表框的选项value的属性

</td> </tr>  
<tr>  
<td>

listValue

</td>  
<td>

设置用于创建第一个下拉列表框的选项label的属性

</td> </tr>  
<tr>  
<td>

name

</td>  
<td>

设置第一个下拉选择框的name属性

</td> </tr>  
<tr>  
<td>

value

</td>  
<td>

设置第一个下拉选择框的value属性

</td> </tr>  
<tr>  
<td>

multiple

</td>  
<td>

设置第一个下拉选择框是否允许多选

</td> </tr> </table>

6)、select标签：该标签用于生成一个下拉列表框。

使用该标签是必须制定list属性。系统会使用list属性指定的集合来生成下拉列表框的选项

该标签有如下属性：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

listKey

</td>  
<td>

该属性指定集合元素中的某个属性作为复选框的value。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的value

</td> </tr>  
<tr>  
<td>

listValue

</td>  
<td>

该属性指定集合元素中的某个属性作为复选框的标签。如果集合是Map，则可以使用key和value指定Map对象的key和value作为复选框的标签

</td> </tr>  
<tr>  
<td>

multiple

</td>  
<td>

设置该列表是否允许多选

</td> </tr> </table>

7）、radio标签：该标签用于生成多个单选框；

8）、optgroup标签：该标签用于生成一个下拉列表框的选项组：

该标签必须放在<s:select.../>标签中使用

9）、token标签:该标签用于阻止多次提交表单的问题。如果需要该标签起作用，则应该在Struts 2的配置文件中启用TokenInterceptor拦截器

Token标签的实现原理是：在表单中增加一个隐藏域。每次加载该页面时，该隐藏域的值都会不同。而TokenInterceptor拦截器则拦截所有用户请求，如果两次请求时该token对应隐藏域的值相同，则会阻止表单提交。

10）、updownSelect标签：该标签用于生产可以上下移动的列表框；

该标签的属性如下：  
  
<table>  
<tr>  
<td>

属性

</td>  
<td>

说明

</td> </tr>  
<tr>  
<td>

allowMoveUP

</td>  
<td>

是否显示“上移”按钮

</td> </tr>  
<tr>  
<td>

allowMoveDown

</td>  
<td>

是否显示“下移”按钮

</td> </tr>  
<tr>  
<td>

allowSelectAll

</td>  
<td>

是否显示“全选”按钮

</td> </tr>  
<tr>  
<td>

moveUpLabel

</td>  
<td>

设置“上移”按钮上的文本

</td> </tr>  
<tr>  
<td>

moveDownLabel

</td>  
<td>

设置“下移”按钮上的文本

</td> </tr>  
<tr>  
<td>

selectAllLabel

</td>  
<td>

设置“全选”按钮上的文本

</td> </tr> </table>

