
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    import numpy as np
    import pandas as pd
    df = pd.DataFrame(np.arange(24).reshape(6,4),
                      index=pd.date_range(start="20170101",periods=6),columns=["A","B","C","D"])
    print("df")
    print("======================================================")
    print(df)
    print("df.shift(2)")
    print("======================================================")
    print(df.shift(2))
    print("df.shift(2,axis=0,freq="2D"")
    print("======================================================")
    print(df.shift(2,axis=0,freq="2D") )
    print("pd.pivot_table(df, index="B", columns="C") ")
    print("======================================================")
    print(pd.pivot_table(df, index="B", columns="C")  )
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    df
    ======================================================
                 A   B   C   D
    2017-01-01   0   1   2   3
    2017-01-02   4   5   6   7
    2017-01-03   8   9  10  11
    2017-01-04  12  13  14  15
    2017-01-05  16  17  18  19
    2017-01-06  20  21  22  23
    df.shift(2)
    ======================================================
                   A     B     C     D
    2017-01-01   NaN   NaN   NaN   NaN
    2017-01-02   NaN   NaN   NaN   NaN
    2017-01-03   0.0   1.0   2.0   3.0
    2017-01-04   4.0   5.0   6.0   7.0
    2017-01-05   8.0   9.0  10.0  11.0
    2017-01-06  12.0  13.0  14.0  15.0
    df.shift(2,axis=0,freq="2D"
    ======================================================
                 A   B   C   D
    2017-01-05   0   1   2   3
    2017-01-06   4   5   6   7
    2017-01-07   8   9  10  11
    2017-01-08  12  13  14  15
    2017-01-09  16  17  18  19
    2017-01-10  20  21  22  23
    pd.pivot_table(df, index="B", columns="C") 
    ======================================================
          A                                D                             
    C    2    6    10    14    18    22   2    6     10    14    18    22
    B                                                                    
    1   0.0  NaN  NaN   NaN   NaN   NaN  3.0  NaN   NaN   NaN   NaN   NaN
    5   NaN  4.0  NaN   NaN   NaN   NaN  NaN  7.0   NaN   NaN   NaN   NaN
    9   NaN  NaN  8.0   NaN   NaN   NaN  NaN  NaN  11.0   NaN   NaN   NaN
    13  NaN  NaN  NaN  12.0   NaN   NaN  NaN  NaN   NaN  15.0   NaN   NaN
    17  NaN  NaN  NaN   NaN  16.0   NaN  NaN  NaN   NaN   NaN  19.0   NaN
    21  NaN  NaN  NaN   NaN   NaN  20.0  NaN  NaN   NaN   NaN   NaN  23.0
    
    Process finished with exit code 0

