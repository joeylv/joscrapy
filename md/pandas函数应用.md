1、管道函数

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    
    #pipe管道函数的应用
    import pandas as pd
    import numpy as np
    
    def adder(ele1,ele2):
       return ele1+ele2
    
    df = pd.DataFrame(np.random.randn(5,3),columns=["col1","col2","col3"])
    print(df)
    df2=df.pipe(adder,2)#df中每一个元素都加2
    print("-"*100)
    print("df.pipe(adder,2) df中每一个元素都加2")
    print (df2)
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
           col1      col2      col3
    0 -0.541685 -1.009440 -1.680244
    1 -0.881437  0.022469  0.911686
    2  0.930035  1.073783  0.096894
    3 -1.282204 -0.039941  0.147482
    4 -1.743847 -1.187832 -0.402219
    ----------------------------------------------------------------------------------------------------
    df.pipe(adder,2) df中每一个元素都加2
           col1      col2      col3
    0  1.458315  0.990560  0.319756
    1  1.118563  2.022469  2.911686
    2  2.930035  3.073783  2.096894
    3  0.717796  1.960059  2.147482
    4  0.256153  0.812168  1.597781
    
    Process finished with exit code 0

2、

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    
    #可以使用apply()方法沿DataFrame或Panel的轴应用任意函数，它与描述性统计方法一样，采用可选的轴参数。
    #  默认情况下，操作按列执行，将每列列为数组。
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5,3),columns=["col1","col2","col3"])
    print (df)
    print("-"*100)
    print("df1=df.apply(np.mean)=df.apply(np.mean,axis=0) 默认按列执行操作:")
    df1=df.apply(np.mean)
    print (df1)
    print("-"*100)
    print("df2=df.apply(np.mean,axis=1) 按行执行操作:")
    df2=df.apply(np.mean,axis=1)
    print (df2)
    print("-"*100)
    df3=df.apply(lambda x: x.max() - x.min())
    print("df3=df.apply(lambda x: x.max() - x.min()):")
    print (df3)
    print("-"*100)
    df4=df["col1"].map(lambda x:x*100)
    print("df4=df["col1"].map(lambda x:x*100):")
    print (df4)
    print("-"*100)
    df5=df.applymap(lambda x:x*100)
    print("df5=df.applymap(lambda x:x*100):")
    print (df5)
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
           col1      col2      col3
    0  0.735342  0.438729 -0.261747
    1 -1.490907  0.397943  0.105613
    2 -0.298617 -0.328284  0.599502
    3 -0.842654  0.324976 -0.047985
    4  0.452950  1.102824  0.023971
    ----------------------------------------------------------------------------------------------------
    df1=df.apply(np.mean)=df.apply(np.mean,axis=0) 默认按列执行操作:
    col1   -0.288777
    col2    0.387238
    col3    0.083871
    dtype: float64
    ----------------------------------------------------------------------------------------------------
    df2=df.apply(np.mean,axis=1) 按行执行操作:
    0    0.304108
    1   -0.329117
    2   -0.009133
    3   -0.188555
    4    0.526582
    dtype: float64
    ----------------------------------------------------------------------------------------------------
    df3=df.apply(lambda x: x.max() - x.min()):
    col1    2.226249
    col2    1.431108
    col3    0.861248
    dtype: float64
    ----------------------------------------------------------------------------------------------------
    df4=df["col1"].map(lambda x:x*100):
    0     73.534186
    1   -149.090744
    2    -29.861721
    3    -84.265380
    4     45.295040
    Name: col1, dtype: float64
    ----------------------------------------------------------------------------------------------------
    df5=df.applymap(lambda x:x*100):
             col1        col2       col3
    0   73.534186   43.872940 -26.174660
    1 -149.090744   39.794331  10.561263
    2  -29.861721  -32.828359  59.950153
    3  -84.265380   32.497553  -4.798542
    4   45.295040  110.282391   2.397062
    
    Process finished with exit code 0

