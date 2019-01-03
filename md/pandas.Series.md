1、系列(`Series`)是能够保存任何类型的数据(整数，字符串，浮点数，Python对象等)的一维标记数组。轴标签统称为索引。

_Pandas_ 系列可以使用以下构造函数创建 -

    
    
    pandas.Series( data, index, dtype, copy)。  
      
      
  
<table>  
<tr>  
<th>

编号

</th>  
<th>

参数

</th>  
<th>

描述

</th></tr>  
<tr>  
<td>

1

</td>  
<td>

`data`

</td>  
<td>

数据采取各种形式，如：`ndarray`，`list`，`constants`

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

`index`

</td>  
<td>

索引值必须是唯一的和散列的，与数据的长度相同。 默认`np.arange(n)`如果没有索引被传递。

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

`dtype`

</td>  
<td>

`dtype`用于数据类型。如果没有，将推断数据类型

</td> </tr>  
<tr>  
<td>

4

</td>  
<td>

`copy`

</td>  
<td>

复制数据，默认为`false`。

</td> </tr> </table>

可以使用各种输入创建一个系列，如 数组、字典、标量值、或、常数

2、

    
    
    import numpy as np
    from scipy import linalg as lg
    import pandas as pd
    s = pd.Series()#创建一个基本系列是一个空系列
    print(s)#Series([], dtype: float64)
    
    data = np.array(["a","b","c","d"])
    s = pd.Series(data)#如果数据是ndarray，则传递的索引必须具有相同的长度。
    # 如果没有传递索引值，那么默认的索引将是范围(n)，其中n是数组长度
    print (s)
    # 0   a
    # 1   b
    # 2   c
    # 3   d
    # dtype: object
    
    data = np.array(["a","b","c","d"])
    s = pd.Series(data,index=[100,101,102,103])#在这里传递了索引值。现在可以在输出中看到自定义的索引值
    print (s)
    # 100  a
    # 101  b
    # 102  c
    # 103  d
    # dtype: object
    
    data = {"a" : 0., "b" : 1., "c" : 2.}
    s = pd.Series(data)#字典(dict)可以作为输入传递，如果没有指定索引，则按排序顺序取得字典键以构造索引。
    # 如果传递了索引，索引中与标签对应的数据中的值将被拉出。
    print (s)
    # a 0.0
    # b 1.0
    # c 2.0
    # dtype: float64
    
    data = {"a" : 0., "b" : 1., "c" : 2.}
    s = pd.Series(data,index=["b","c","d","a"])#注意观察 - 索引顺序保持不变，缺少的元素使用NaN(不是数字)填充
    print (s)
    # b 1.0
    # c 2.0
    # d NaN
    # a 0.0
    # dtype: float64
    
    s = pd.Series(5, index=[0, 1, 2, 3])#如果数据是标量值，则必须提供索引。将重复该值以匹配索引的长度
    print (s)
    # 0  5
    # 1  5
    # 2  5
    # 3  5
    # dtype: int64
    
    s = pd.Series([1,2,3,4,5],index = ["a","b","c","d","e"])
    #retrieve the first element
    # 系列中的数据可以使用类似于访问ndarray中的数据来访问。
    # 检索第一个元素。比如已经知道数组从零开始计数，第一个元素存储在零位置等等
    print (s[0])# 1
    
    s = pd.Series([1,2,3,4,5],index = ["a","b","c","d","e"])
    #retrieve the first three element
    # 检索系列中的前三个元素。 如果a:被插入到其前面，则将从该索引向前的所有项目被提取。
    # 如果使用两个参数(使用它们之间)，两个索引之间的项目(不包括停止索引)
    print (s[:3])
    # a  1
    # b  2
    # c  3
    # dtype: int64
    
    s = pd.Series([1,2,3,4,5],index = ["a","b","c","d","e"])
    #retrieve a single element
    #一个系列就像一个固定大小的字典，可以通过索引标签获取和设置值。
    print (s["a"])# 1
    
    s = pd.Series([1,2,3,4,5],index = ["a","b","c","d","e"])
    #retrieve multiple elements 使用索引标签值列表检索多个元素。 如果不包含标签，则会出现异常。
    print (s[["a","c","d"]])
    # a  1
    # c  3
    # d  4
    # dtype: int64
    
    
     

