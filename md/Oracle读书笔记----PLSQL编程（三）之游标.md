游标是从数据库中提取出来一临时表的形式存放在内存中的数据。可以把游标看作是内存的SQL工作区域，游标名称相当于该区域的句柄。通过该句柄可以有效地控制游标，从而实现对数据的操作。所以对游标的操作实际上就是对数据库库的间接操作。

1.1游标的定义

定义游标的格式如下：

CURSOR 游标 IS SELECT 语句;

例如：把数据表中emp中部门号为20的员工定义为游标：

    
    
    1 CURSOR exce_emp is select * from scott.emp where deptno=20;

定义游标后，我们就可以使用游标了。但是要对游标进行操作我们必须先打开游标：

Open 游标名;

打开游标实际上是从数据表中读取数据的过程，在这个过程中主要完成两件事：

1、把select查询结果读入内存工作区中。

2、将游标指针定位在第一条记录。

游标在使用后，要关闭：close 游标名;

1.2利用fetch命令从游标中提取数据

我们定义游标并且打开游标后，就可以利用fetch命令从游标中提取数据。

FETCH 游标名 INTO变量名1，变量名2......

或者

FFETCJ 游标名 INTO 纪录型变量名;

FETCH命令首先将当前游标指针所指的行读出来并且置于相应的变量中，然后把游标指针移到下一行。所以FETCH命令每一个执行的时候，只能提取一行或者部分的数据。

实例：

    
    
    1 declare
    2    cursor exce_emp is select * from emp where empno=6676;            --定义游标
    3    var_exce_emp exce_emp%rowtype;          --定义变量
    4 begin
    5   open exce_emp;         --打开游标
    6   fetch exce_emp into var_exce_emp;            --fetch提取数据
    7   dbms_output.put_line("提取的数据为:员工的姓名:"||var_exce_emp.ename||",员工的工作为:"||var_exce_emp.job);
    8   close exce_emp;
    9 end;

存在这样一种情况，如果游标指针已经指到了游标的末尾，那么FETCH命令将读不到数据了，所以应该有这样一种机制，这种机制可以测出游标是否已经指到了游标的末尾。这种机制就是游标的属性。

1.3游标的属性

游标有四个属性：%FOUND、%ISOPEN、%NOTFOUND、%ROWCOUNT。

下面就分别这四个属性介绍：

1.3.1%FOUND

该属性用于测试在自己所在语句之前的最后一个FETCH命令是否提取到了数据。如果能够提取到数据就返回true，否则返回false。但是如果一个游标还没有被打开就运用%FOUND，那么将会产生INVALID_CURSOR异常。

实例：

    
    
     1 declare
     2    cursor exce_emp is select empno,ename from emp where deptno=20;
     3    var_exce_emp exce_emp%rowtype;
     4    i int := 1;
     5 begin
     6   open exce_emp;
     7   loop
     8     fetch exce_emp into var_exce_emp;
     9     if exce_emp %found then        --利用%found属性检测是否提取到了数据
    10       dbms_output.put_line("第"||to_char(i)||"个员工的信息-------编号:"||var_exce_emp.empno||"员工姓名:"||var_exce_emp.ename);
    11       i := i+1;
    12     else
    13       exit;
    14     end if;
    15   end loop;
    16   close exce_emp;
    17 end;

  
1.3.2%ISOPEN

该属性主要用于测试游标是否已经打开。

实例：

    
    
     1 declare
     2    cursor exce_emp is select empno,ename from emp;
     3    var_exce_emp exce_emp%rowtype;
     4 begin
     5   if not exce_emp%isopen then        --检测游标是否已经打开
     6     dbms_output.put_line("游标没有打开");
     7     open exce_emp;
     8   else
     9     dbms_output.put_line("游标已经打开了")；
    10   end if;
    11 end;

  
1.3.3%NOFOUND

该属性与%FOUND相反。这里就不做介绍了。

1.3.4%ROWCOUNT

当刚刚打开游标时，%ROWCOUNT的值为0。每运行一次FETCH命令，%ROWCOUNT的值就会自增1。因此%ROWCOUNT的值可以看着是游标中当前被读取了的记录的条数，即游标循环中处理的当前行数。如果一个有游标在打开之前调用%ROWCOUNT属性，就会产生异常INVALID_CURSOR。

实例：

    
    
     1 declare
     2   cursor exce_emp is empno,ename from emp where deptno=20;
     3   var_exce_emp exce_emp%rowtype;
     4   n int := 5;
     5 begin
     6   open exce_emp;
     7   loop
     8     fetch exce_emp into var_exce_emp;
     9     exit when exce_emp%notfound;
    10     dbms_output.put_line("员工号:"||var_exce_emp.empno||",员工姓名:"||var_exce_emp.ename);
    11     exit when exce_emp%rowcount=n;
    12   end loop;
    13   close exce_emp;
    14 end;

  
1.4隐式游标

上面介绍的都是显示游标。其实Oracle还默认了一种游标，这个游标就是隐式游标。其被定义为SQL。它同时也具有4个属性。如下：

    
    
     1 declare
     2   tempdeptno := 20;
     3   counts int := 0;
     4 begin
     5   update emp set job="CLERK" where deptno = tempdeptno;
     6   if sql%found then
     7     counts := sql%rowcount;
     8   end if;
     9   dbms_output.put_line("对"||to_char(counts)||"行语句做了修改")；
    10 end;

  
注意：隐式游标时不需要打开和关闭的。

下面就显示游标和隐式游标做一个比较

![](http://my.csdn.net/uploads/201205/02/1335970198_7007.jpg)

