1、axes返回标签列表

    
    
    import pandas as pd
    import numpy as np
    dates = pd.date_range("20170101", periods=8)
    df = pd.DataFrame(np.random.randn(8,4), index=dates, columns=list("ABCD"))
    print("df:")
    print(df)
    print("-"*50)
    print ("The axes are:")
    print (df .axes)  
    print (df.empty)# **empty示例，** 返回布尔值，表示对象是否为空。返回True则表示对象为空
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    df:
                       A         B         C         D
    2017-01-01 -0.579966 -0.435075  0.308428 -0.684288
    2017-01-02 -0.046761  0.209575  1.426686 -0.152909
    2017-01-03  0.649144 -1.312502 -0.520895 -0.128796
    2017-01-04  0.469305  0.738260  3.650268 -1.290882
    2017-01-05  0.195328 -1.236598  0.245380 -0.845111
    2017-01-06  0.886847 -0.946261 -0.884007 -0.527200
    2017-01-07  1.002840  2.183883  0.709170 -0.618336
    2017-01-08 -1.626558 -0.077388 -2.251855 -1.709279
    --------------------------------------------------
    The axes are:
    [DatetimeIndex(["2017-01-01", "2017-01-02", "2017-01-03", "2017-01-04",
                   "2017-01-05", "2017-01-06", "2017-01-07", "2017-01-08"],
                  dtype="datetime64[ns]", freq="D"), Index(["A", "B", "C", "D"], dtype="object")]
    
    Process finished with exit code 0

2、 **empty示例，** 返回布尔值，表示对象是否为空。返回`True`则表示对象为空

print(df.empty)

3、

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    from scipy import linalg as lg
    #按标签选择
    #通过标签选择多轴
    
    import pandas as pd
    import numpy as np
    dates = pd.date_range("20170101", periods=8)
    s = pd.DataFrame(np.random.randn(8,4), index=dates, columns=list("ABCD"))
    print("s:")
    print(s)
    print("-"*50)
    print ("The axes are 数据的标签:")
    print (s .axes)
    print ("The dimensions of the object 数据的维数:")
    print (s.ndim)
    print ("Is the Object empty 是否为空?")
    print (s.empty)
    print ("The size of the object 元素数据所占的字节数:")
    print (s.size)
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    s:
                       A         B         C         D
    2017-01-01  0.007545  0.688495  0.973736  0.487351
    2017-01-02 -0.196882  0.936148 -1.264392 -0.828813
    2017-01-03  0.127409 -0.276271  0.837958 -0.559367
    2017-01-04 -0.464785  0.800002  0.663286  0.455558
    2017-01-05  1.030087  0.031511 -0.043613  0.004243
    2017-01-06 -0.024684  0.656596  0.944321  1.237634
    2017-01-07 -0.606596  0.464559 -0.071484  0.035291
    2017-01-08  0.527749  0.409902  0.752180  1.407739
    --------------------------------------------------
    The axes are 数据的标签:
    [DatetimeIndex(["2017-01-01", "2017-01-02", "2017-01-03", "2017-01-04",
                   "2017-01-05", "2017-01-06", "2017-01-07", "2017-01-08"],
                  dtype="datetime64[ns]", freq="D"), Index(["A", "B", "C", "D"], dtype="object")]
    The dimensions of the object 数据的维数:
    2
    Is the Object empty 是否为空?
    False
    The size of the object 元素数据所占的字节数:
    32
    
    Process finished with exit code 0

