一般来说我们是无法实现EL表达式取整的。对于EL表达式的除法而言，他的结果是浮点型。

如：${6/7},他的结果是：0.8571428571428571。对于这个我们是无法来实现取整的。但是我们现在的目的就是要EL表达式来实现取整。这个时候需要用到<fmt:formatNumber
/>这个标签。该标签的说明如下：

功能：该标签用来格式化数值即设置特定语言环境下的数值输出方式

语法： <fmt:formatNumber value="数值" ......./>

属性说明：Value要转换的数值。

Type格式化方式(currency,number,percent) 。

Pattern用户自定义的格式。

var保存转换结果的变量。

scope变量的范围。

如：<fmt:formatNumber type="number" value="${8/7)}" maxFractionDigits="0"/>
结果为1。

其中maxFractionDigits="0"表示保留0位小数，这样就可以实现取整了。同时这里是按照四舍五入的规则来进行取整的。如果是${2/6}结果就是0，如果是${6/7}结果就是1。

在这里我们同样也可以设置保留n为小数，仅需要设置maxFractionDigits="n"即可实现。

  

EL表达式取整问题

