一、PL/SQL程序流程控制

![](http://my.csdn.net/uploads/201205/02/1335931848_7303.jpg)

上面的结构与其他的高级语言程序一样，就不做介绍了。

下就条件结构和循环结构说明。

1）IF条件控制句

1.1 IF...THEN语句

其语法是：

IF p THEN

基本语句段；

END IF;

例如：

    
    
    declare 
      flag1 integer := 1;
      flag2 integer := 2;
    begin
      if flag1 < flag 2 then
        dbms_output.put_line("Flag1<flag2");
       end if;
    end;
    

注意：上面的IF 与END IF必须成对出现

1.2 IF...THEN...ELSE语句

该语句用于需要在两个语句段之间做出选择时。其语法如下：

IF P THEN

语句段1;

ELSE

语句段2;

EDN IF;

在该语句中，如果p的值为true，则执行语句段1,否则执行语句段2;实例：

    
    
     1 declare
     2    flag1 integer := 5;
     3    flag2 integer := 8;
     4 begin
     5   if flag1 <flag2 then
     6     dbms_output.put_line("flag1<flag2");
     7   else
     8     dbms_output.put_line("flag1>flag2");
     9   end if;
    10 end;

1.3 IF...THEN...ELSIF语句

该语句用于在三个或者三个以上的语句段之间做出选择。其语法段为：

IF P1 THEN

语句段1;

ELSIF P2 THEN

语句段2;

ELSE

语句段3;

END IF;

实例：

    
    
     1 declare
     2   grade number := 98;
     3   results varchar2(10);
     4 begin
     5   if grade >=90 then
     6     results := "优";
     7   elsif grade >= 80 then
     8      results :="良";
     9   elsif grade >=70 then
    10      results :="中";
    11   elsif grade >= 60 then
    12      results :="及格";
    13   else
    14     results :="差";
    15   end if;
    16   dbms_output.put_line(results);
    17 end;

1.4 CASE选择控制

该语句用于控制多分支选择功能。其实 IF...THEN...ELSIF语句也可以实现这个功能，但是非常的麻烦。其语法结构为：

CASE E

WHEN e1: THEN 语句段1;

WHEN e2: THEN 语句段2 ;

WHEN e3: THEN 语句段3;

....................

WHEN en: THEN 语句段n ;

END CASE;

实例：

    
    
     1 declare 
     2    results varchar2(20) := "B";
     3    grade varchar2(20);
     4 begin
     5   case results
     6      when "A" then grade := "90-100";
     7      when "B" then grade := "80-89";
     8      when "C" then grade := "70-79";
     9      when "D" then grade := "60-69";
    10      when "E" then grade := "<60";
    11      else grade := "不存在这个成绩等级";
    12   end case;
    13   dbms_output.put_line(grade);
    14 end;

2)、循环控制

2.1 FOR...LOOP语句

该形式如下：

FOR I [REVERSE]IN lb..hb LOOP

语句段;

END LOOP;

其中，i为整型变量，一般称为循环计算器，lb和hb均为整型常量，分别代表了i的下限和上限，..为范围操作符。当没有使用参数REVERSE时，i的初值被设置为lb。实例：

    
    
    1 declare 
    2    i int := 0;
    3 begin
    4   for i in 1..3 loop
    5     dbms_output.put_line("循环第"||to_char(i)||"次时"||to_char(i));
    6   end loop;
    7 end;

  
2.2 LOOP...EXIT循环控制

该语句用于控制死循环的。一般对于死循环的控制，有如下三种方式：

2.2.1 利用if语句

LOOP

语句段;

IF P THEN

EXIT；

END IF;

END LOOP;

实例：

    
    
     1 declare
     2    i int := 0;
     3    results integer := 0;
     4 begin
     5   loop
     6     results := results + i;
     7     if i = 10 then
     8       exit;
     9     end if;
    10     i : i+1;
    11   end loop;
    12   dbms_output.put_line("累加结果为:"||to_char(results));
    13 end;

  

2.2.2 利用EXIT...WHEN

LOOP

.........

EXIT WHEN e;

.............

END LOOP;

其中e为布尔表达式，如果e的值为true则循环退出，否则继续执行循环语句。实例：

    
    
     1 declare 
     2    i int := 1;
     3    results integer := 0;
     4 begin
     5   loop 
     6     results :=  results+i;
     7     exit when i = 10;
     8     i := i+1;
     9   end loop;
    10   dbms_output.put_line("累加结果为:"||to_char(results));
    11 end;

2.2.3: 利用标签

该语句的格式如下：

<<标签名>>

LOOP

.......

EXIT 标签名 WHEN e;

........

END LOOP;

当e为true时退出。注意，标签名必须在loop语句之前用“<<>>”定义实例：

    
    
     1 declare
     2    i integer := 1;
     3    results integer := 0;
     4 begin
     5   <<my_label>>
     6   loop
     7     results := results + i;
     8     exit my_label when i = 10;
     9     i := i+1;
    10   end loop;
    11   dbms_output.put_line("累加的结果为:"||to_char(results));
    12 end; 

2.3 WHILE...LOOP循环控制

WHILE e LOOP

语句段;

END LOOP;

E为循环条件，当e的值为true时则执行循环体，否则退出循环。

实例：

    
    
     1 declare
     2    m integer := 100;
     3    n integer := 7;
     4    results integer;
     5 begin
     6   results := m;
     7   while results >=n loop
     8     results := results - n;
     9   end loop;
    10   dbms_output.put_line(to_char(m)||"除以"||to_char(n)||"的余数"||to_char(results));
    11 end;

二、在PL/SQL程序中调用SQL语句

实际上在PL/SQL程序中i调用SQL语句，对于不同的SQL语句调用的方法是不一样的。在这里介绍常用的 几种语句的调用方法。

2.1调用SELECT语句

在调用这个语句之间，应该定义一个变量用来存储SELECT语句产生的结果，而且 这个变量的结果要与SELECT之后的字段列表相一致。实例：

    
    
    1 declare
    2   temp_emp scott.emp%rowtype;
    3 begin
    4   select * into temp_emp from emp where empno=7369;
    5   dbms_output.put_line(to_char(temp_emp.empno||","||temp_emp.ename));
    6 end;

注意：这种变量只能是一条记录，否则就会出错。而且如果SELECT语句无返回结果，同样会报错。

2.2调用INSERT语句

这条语句可以直接调用。实例：

    
    
     1 declare
     2   empno emp.empno%type;
     3   ename emp.ename%type;
     4   job emp.job%type;
     5   mgr emp.mgr%type;
     6   hiredate emp.hiredate%type;
     7   sal emp.sal%type;
     8   comm emp.comm%type;
     9   deptno emp.deptno%type;
    10 begin
    11   empno := 6676;
    12   ename := "LILY";
    13   job := "CLERK";
    14   mgr := 7899;
    15   hiredate := to_date("1981-12-12","yyyy-mm-dd");
    16   sal := 999.00;
    17   comm := 433.00;
    18   deptno := 20;
    19   insert into emp values(empno,ename,job,mgr,hiredate,sal,comm,deptno);
    20 end;

2.3调用UPDATE语句

同样可以之间调用。实例:

    
    
    1 declare
    2   tempno scott.emp.empno%type;
    3 begin
    4   tempno := 7677;
    5   update emp set ename="AAA" where empno = tempno;
    6 end;

2.4调用DELETE语句

直接调用。实例：

    
    
    1 declare
    2   tempno scott.emp.empno%type;
    3 begin
    4   tempno := 7677;
    5   delete form emp where empno = tempno;
    6 end;
    7   

