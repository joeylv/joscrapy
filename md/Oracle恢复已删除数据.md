  * 1 一、通过scn恢复删除且已提交的数据 
  * 2 二、通过时间恢复删除且已提交的数据 

分为两种方法：scn和时间戳两种方法恢复。

## 一、通过scn恢复删除且已提交的数据

1、获得当前数据库的scn号

select current_scn from v$database; (切换到sys用户或system用户查询)

查询到的scn号为：1499223

2、查询当前scn号之前的scn

select * from 表名 as of scn 1499220; (确定删除的数据是否存在，如果存在，则恢复数据；如果不是，则继续缩小scn号)

3、恢复删除且已提交的数据

flashback table 表名 to scn 1499220;

## 二、通过时间恢复删除且已提交的数据

1、查询当前系统时间

select to_char(sysdate,’yyyy-mm-dd hh24:mi:ss’) from dual;

2、查询删除数据的时间点的数据

select * from 表名 as of timestamp to_timestamp(‘2013-05-29 15:29:00′,’yyyy-mm-
dd hh24:mi:ss’); (如果不是，则继续缩小范围)

3、恢复删除且已提交的数据

flashback table 表名 to timestamp to_timestamp(‘2013-05-29 15:29:00′,’yyyy-mm-dd
hh24:mi:ss’);

注意：如果在执行上面的语句，出现错误。可以尝试执行 alter table 表名 enable row movement; //允许更改时间戳

或者insert into t_viradsl2 select * from t_viradsl2 as of timestamp
to_Date(‘2011-01-19 15:28:00’, ‘yyyy-mm-dd hh24:mi:ss’) //已将误删除数据插入表中

