1、注意 - 不要尝试在迭代时修改任何对象。迭代是用于读取，迭代器返回原始对象(视图)的副本，因此更改将不会反映在原始对象上。

2、`itertuples()`方法将为`DataFrame`中的每一行返回一个产生一个命名元组的迭代器。元组的第一个元素将是行的相应索引值，而剩余的值是行值。

3、`iterrows()`返回迭代器，产生每个索引值以及包含每行数据的序列

4、

要遍历数据帧(DataFrame)中的行，可以使用以下函数 -

  * `iteritems()` \- 迭代`(key，value)`对
  * `iterrows()` \- 将行迭代为(索引，系列)对
  * `itertuples()` \- 以`namedtuples`的形式迭代行

**iteritems()示例**

将每个列作为键，将值与值作为键和列值迭代为Series对象。

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    
    #可以使用apply()方法沿DataFrame或Panel的轴应用任意函数，它与描述性统计方法一样，采用可选的轴参数。
    #  默认情况下，操作按列执行，将每列列为数组。
    import pandas as pd
    import numpy as np
    
    N=20
    
    df = pd.DataFrame({
        "A": pd.date_range(start="2016-01-01",periods=N,freq="D"),
        "x": np.linspace(0,stop=N-1,num=N),
        "y": np.random.rand(N),
        "C": np.random.choice(["Low","Medium","High"],N).tolist(),
        "D": np.random.normal(100, 10, size=(N)).tolist()
        })
    print("-"*100)
    print("for col in df:")
    for col in df:
       print (col)
    ##########################################################################
    df = pd.DataFrame(np.random.randn(4,3),columns=["col1","col2","col3"])
    print("-"*100)
    print("for key,value in df.iteritems():")#观察一下，单独迭代每个列作为系列中的键值对
    for key,value in df.iteritems():
       print (key,value)
    print("-"*100)
    print("for row_index,row in df.iterrows():")
    print("由于iterrows()遍历行，因此不会跨该行保留数据类型。0,1,2是行索引，col1，col2，col3是列索引:")
    for row_index,row in df.iterrows():
       print (row_index,row)
    #注意 - 由于iterrows()遍历行，因此不会跨该行保留数据类型。0,1,2是行索引，col1，col2，col3是列索引。
    print("-"*100)
    print("for row in df.itertuples():")
    for row in df.itertuples():
        print (row)
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    ----------------------------------------------------------------------------------------------------
    for col in df:
    A
    C
    D
    x
    y
    ----------------------------------------------------------------------------------------------------
    for key,value in df.iteritems():
    col1 0    0.477335
    1    1.181332
    2    1.561019
    3    1.847981
    Name: col1, dtype: float64
    col2 0   -0.785008
    1   -1.157689
    2   -1.122126
    3   -0.986387
    Name: col2, dtype: float64
    col3 0   -0.863011
    1    0.907147
    2   -1.100768
    3    0.128576
    Name: col3, dtype: float64
    ----------------------------------------------------------------------------------------------------
    for row_index,row in df.iterrows():
    由于iterrows()遍历行，因此不会跨该行保留数据类型。0,1,2是行索引，col1，col2，col3是列索引:
    0 col1    0.477335
    col2   -0.785008
    col3   -0.863011
    Name: 0, dtype: float64
    1 col1    1.181332
    col2   -1.157689
    col3    0.907147
    Name: 1, dtype: float64
    2 col1    1.561019
    col2   -1.122126
    col3   -1.100768
    Name: 2, dtype: float64
    3 col1    1.847981
    col2   -0.986387
    col3    0.128576
    Name: 3, dtype: float64
    ----------------------------------------------------------------------------------------------------
    for row in df.itertuples():
    Pandas(Index=0, col1=0.4773350765799035, col2=-0.7850081060024958, col3=-0.8630110792391069)
    Pandas(Index=1, col1=1.1813320974672603, col2=-1.1576889340133183, col3=0.9071469334830587)
    Pandas(Index=2, col1=1.561018528282379, col2=-1.1221261428911304, col3=-1.1007676640353743)
    Pandas(Index=3, col1=1.8479811833066473, col2=-0.9863873037251529, col3=0.12857649143591193)
    
    Process finished with exit code 0

