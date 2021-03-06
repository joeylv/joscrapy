PL/SQL是一种高效的事物处理语言，它具有如下优点

1、支持SQL

2、支持面向对象的编程方法

3、更好的性能和更高的效率

4、编写方便

5、与Oracle高度集成

6、安全性好

一、PL/SQL变量和基本数据类型

1、PL/SQL变量的定义

基本数据类型变量的定义方法如下：

变量名 类型标识符 [:= 值];

如： Str varchar2[100] := "中国";

也可以使用关键字default来代替赋值符。

str varchar2[100] default "中国";

注意：赋值符合中的冒号和等号是不能分开的；

2、基本数据类型

![](http://my.csdn.net/uploads/201205/01/1335878832_2669.jpg)

三、PL/SQL程序的结构

首先看一个简单的例子：以下是一个完整的PL/SQL程序，用于求方程ax²+bx+c=0的根

    
    
     1 declare
     2     a int := 3;
     3     b int := 8;
     4     c int := 2;
     5     x1 number(8,2);
     6     x2 number(8,2);
     7     t number(8,2);
     8     error exception;
     9 begin
    10   t := b**2-4*a*c;
    11   if t<0 then
    12      raise error;
    13   end if;
    14   x1 := (-b+sqrt(t)/(2*a));
    15   x2 := (b+sqrt(t)/(2*a));
    16   dbms_output.put_line("x1="||x1);
    17   dbms_output.put_line("x2="||x2);
    18  exception
    19    when error then dbms_output.put_line("此方程无解");
    20 end;

从上面可以看出一个PL/SQL程序分为3个部分：

1）、定义部分。在PL/SQL程序中，所用到的常量、变量、游标等必须在这一部分中定义。

但是这个部分的变量定义不能使用逗号分隔的办法来同时声明多个变量。

分号是每个变量声明和语句的结束符。

如果一个PL/SQL程序中没有变量需要定义，那么这个部分是可以去掉的。

2）、执行部分。这个部分是PL/SQL程序中的核心部分，包括赋值语句、对数据库的操作语句和流程控制语句等，构成 PL/SQL程序的基本块结构。

执行部分至少有一个可执行语句。

3）异常处理部分。当程序检测到错误情况时即产生异常。由exception标识的部分来处理程序过程产生的异常。

所以一个PL/SQL程序的基本结构可以是以下结构：

Declare

定义部分

Begin

执行部分

Exception

异常处理部分

End;

