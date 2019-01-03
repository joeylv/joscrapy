Pandas具有功能全面的高性能内存中连接操作，与SQL等关系数据库非常相似。  
Pandas提供了一个单独的`merge()`函数，作为DataFrame对象之间所有标准数据库连接操作的入口 -

    
    
    pd.merge(left, right, how="inner", on=None, left_on=None, right_on=None,
    left_index=False, right_index=False, sort=True)
    

Python

在这里，有以下几个参数可以使用 -

  * _left_ \- 一个DataFrame对象。
  * _right_ \- 另一个DataFrame对象。
  * _on_ \- 列(名称)连接，必须在左和右DataFrame对象中存在(找到)。
  * _left_on_ \- 左侧DataFrame中的列用作键，可以是列名或长度等于DataFrame长度的数组。
  * _right_on_ \- 来自右的DataFrame的列作为键，可以是列名或长度等于DataFrame长度的数组。
  * _left_index_ \- 如果为`True`，则使用左侧DataFrame中的索引(行标签)作为其连接键。 在具有MultiIndex(分层)的DataFrame的情况下，级别的数量必须与来自右DataFrame的连接键的数量相匹配。
  * _right_index_ \- 与右DataFrame的 _left_index_ 具有相同的用法。
  * _how_ \- 它是 _left_ , _right_ , _outer_ 以及 _inner_ 之中的一个，默认为内 _inner_ 。 下面将介绍每种方法的用法。
  * _sort_ \- 按照字典顺序通过连接键对结果DataFrame进行排序。默认为`True`，设置为`False`时，在很多情况下大大提高性能。

现在创建两个不同的DataFrame并对其执行合并操作。

## 合并使用“how”的参数

如何合并参数指定如何确定哪些键将被包含在结果表中。如果组合键没有出现在左侧或右侧表中，则连接表中的值将为`NA`。

这里是`how`选项和SQL等效名称的总结 -  
  
<table>  
<tr>  
<th>

合并方法

</th>  
<th>

SQL等效

</th>  
<th>

描述

</th></tr>  
<tr>  
<td>

`left`

</td>  
<td>

`LEFT OUTER JOIN`

</td>  
<td>

使用左侧对象的键

</td> </tr>  
<tr>  
<td>

`right`

</td>  
<td>

`RIGHT OUTER JOIN`

</td>  
<td>

使用右侧对象的键

</td> </tr>  
<tr>  
<td>

`outer`

</td>  
<td>

`FULL OUTER JOIN`

</td>  
<td>

使用键的联合

</td> </tr>  
<tr>  
<td>

`inner`

</td>  
<td>

`INNER JOIN`

</td>  
<td>

使用键的交集

</td> </tr> </table>

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    
    import pandas as pd
    left = pd.DataFrame({
             "id":[1,2,3,4,5],
             "Name": ["Alex", "Amy", "Allen", "Alice", "Ayoung"],
             "subject_id":["sub1","sub2","sub4","sub6","sub5"]})
    right = pd.DataFrame(
             {"id":[1,2,3,4,5],
             "Name": ["Billy", "Brian", "Bran", "Bryce", "Betty"],
             "subject_id":["sub2","sub4","sub3","sub6","sub5"]})
    print (left)
    print("========================================")
    print (right)
    print("========================================")
    print("在一个键上合并两个数据帧,how - 它是left, right, outer以及inner之中的一个，默认为内inner为交集")
    rs = pd.merge(left,right,on="id")#在一个键上合并两个数据帧,how - 它是left, right, outer以及inner之中的一个，默认为内inner
    print(rs)
    print("========================================")
    print("合并多个键上的两个数据框,默认为交集：")
    rs = pd.merge(left,right,on=["id","subject_id"])
    print(rs)
    print("========================================")
    print("使用左侧对象的键：")
    rs = pd.merge(left, right, on="subject_id", how="left")
    print (rs)
    print("========================================")
    print("使用键的联合：")
    rs = pd.merge(left, right, how="outer", on="subject_id")
    print (rs)
    print("========================================")
    print("使用键的交集：")
    rs = pd.merge(left, right, how="inner", on="subject_id")
    print (rs)
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
         Name  id subject_id
    0    Alex   1       sub1
    1     Amy   2       sub2
    2   Allen   3       sub4
    3   Alice   4       sub6
    4  Ayoung   5       sub5
    ========================================
        Name  id subject_id
    0  Billy   1       sub2
    1  Brian   2       sub4
    2   Bran   3       sub3
    3  Bryce   4       sub6
    4  Betty   5       sub5
    ========================================
    在一个键上合并两个数据帧,how - 它是left, right, outer以及inner之中的一个，默认为内inner为交集
       Name_x  id subject_id_x Name_y subject_id_y
    0    Alex   1         sub1  Billy         sub2
    1     Amy   2         sub2  Brian         sub4
    2   Allen   3         sub4   Bran         sub3
    3   Alice   4         sub6  Bryce         sub6
    4  Ayoung   5         sub5  Betty         sub5
    ========================================
    合并多个键上的两个数据框,默认为交集：
       Name_x  id subject_id Name_y
    0   Alice   4       sub6  Bryce
    1  Ayoung   5       sub5  Betty
    ========================================
    使用左侧对象的键：
       Name_x  id_x subject_id Name_y  id_y
    0    Alex     1       sub1    NaN   NaN
    1     Amy     2       sub2  Billy   1.0
    2   Allen     3       sub4  Brian   2.0
    3   Alice     4       sub6  Bryce   4.0
    4  Ayoung     5       sub5  Betty   5.0
    ========================================
    使用键的联合：
       Name_x  id_x subject_id Name_y  id_y
    0    Alex   1.0       sub1    NaN   NaN
    1     Amy   2.0       sub2  Billy   1.0
    2   Allen   3.0       sub4  Brian   2.0
    3   Alice   4.0       sub6  Bryce   4.0
    4  Ayoung   5.0       sub5  Betty   5.0
    5     NaN   NaN       sub3   Bran   3.0
    ========================================
    使用键的交集：
       Name_x  id_x subject_id Name_y  id_y
    0     Amy     2       sub2  Billy     1
    1   Allen     3       sub4  Brian     2
    2   Alice     4       sub6  Bryce     4
    3  Ayoung     5       sub5  Betty     5
    
    Process finished with exit code 0

