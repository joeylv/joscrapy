Pandas对象可以分成任何对象。有多种方式来拆分对象，如 -

  * _obj.groupby(‘key’)_
  * _obj.groupby([‘key1’,’key2’])_
  * _obj.groupby(key,axis=1)_

现在来看看如何将分组对象应用于DataFrame对象

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    import numpy as np
    import pandas as pd
    ipl_data = {"Team": ["Riders", "Riders", "Devils", "Devils", "Kings",
             "kings", "Kings", "Kings", "Riders", "Royals", "Royals", "Riders"],
             "Rank": [1, 2, 2, 3, 3,4 ,1 ,1,2 , 4,1,2],
             "Year": [2014,2015,2014,2015,2014,2015,2016,2017,2016,2014,2015,2017],
             "Points":[876,789,863,673,741,812,756,788,694,701,804,690]}
    df = pd.DataFrame(ipl_data)
    print (df)
    print("=======================================")
    print (df.groupby("Team"))
    print("=======================================")
    print (df.groupby("Team").groups)
    print("=======================================")
    print (df.groupby(["Team","Year"]).groups)
    #迭代遍历分组
    print("迭代遍历分组:")
    print("=======================================")
    grouped = df.groupby("Year")
    for name,group in grouped:
        print (name)
        print (group)
    #使用get_group()方法，可以选择一个组
    print("使用get_group()方法，可以选择一个组:")
    print("=======================================")
    grouped = df.groupby("Year")
    print (grouped.get_group(2014))
    print("=======================================")
    grouped = df.groupby("Year")
    print (grouped["Points"].agg(np.mean))
    #另一种查看每个分组的大小的方法是应用size()函数
    print("另一种查看每个分组的大小的方法是应用size()函数:")
    print("=======================================")
    grouped = df.groupby("Team")
    print (grouped.agg(np.size))
    #通过分组系列，还可以传递函数的列表或字典来进行聚合
    print("通过分组系列，还可以传递函数的列表或字典来进行聚合:")
    print("=======================================")
    grouped = df.groupby("Team")
    agg = grouped["Points"].agg([np.sum, np.mean, np.std])
    print (agg)
    #分组或列上的转换返回索引大小与被分组的索引相同的对象。因此，转换应该返回与组块大小相同的结果。
    print("分组或列上的转换返回索引大小与被分组的索引相同的对象。因此，转换应该返回与组块大小相同的结果。:")
    print("=======================================")
    grouped = df.groupby("Team")
    score = lambda x: (x - x.mean()) / x.std()*10
    print (grouped.transform(score))
    #过滤根据定义的标准过滤数据并返回数据的子集。filter()函数用于过滤数据
    print("=======================================")
    print("过滤根据定义的标准过滤数据并返回数据的子集。filter()函数用于过滤数据:")
    df = pd.DataFrame(ipl_data)
    filter = df.groupby("Team").filter(lambda x: len(x) >= 3)
    print (filter)
    print("=======================================")
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
        Points  Rank    Team  Year
    0      876     1  Riders  2014
    1      789     2  Riders  2015
    2      863     2  Devils  2014
    3      673     3  Devils  2015
    4      741     3   Kings  2014
    5      812     4   kings  2015
    6      756     1   Kings  2016
    7      788     1   Kings  2017
    8      694     2  Riders  2016
    9      701     4  Royals  2014
    10     804     1  Royals  2015
    11     690     2  Riders  2017
    =======================================
    <pandas.core.groupby.DataFrameGroupBy object at 0x000000000D6317B8>
    =======================================
    {"Kings": Int64Index([4, 6, 7], dtype="int64"), "Riders": Int64Index([0, 1, 8, 11], dtype="int64"), "Devils": Int64Index([2, 3], dtype="int64"), "Royals": Int64Index([9, 10], dtype="int64"), "kings": Int64Index([5], dtype="int64")}
    =======================================
    {("Kings", 2017): Int64Index([7], dtype="int64"), ("Riders", 2015): Int64Index([1], dtype="int64"), ("Kings", 2016): Int64Index([6], dtype="int64"), ("Riders", 2014): Int64Index([0], dtype="int64"), ("Royals", 2015): Int64Index([10], dtype="int64"), ("Royals", 2014): Int64Index([9], dtype="int64"), ("kings", 2015): Int64Index([5], dtype="int64"), ("Kings", 2014): Int64Index([4], dtype="int64"), ("Riders", 2017): Int64Index([11], dtype="int64"), ("Devils", 2014): Int64Index([2], dtype="int64"), ("Riders", 2016): Int64Index([8], dtype="int64"), ("Devils", 2015): Int64Index([3], dtype="int64")}
    迭代遍历分组:
    =======================================
    2014
       Points  Rank    Team  Year
    0     876     1  Riders  2014
    2     863     2  Devils  2014
    4     741     3   Kings  2014
    9     701     4  Royals  2014
    2015
        Points  Rank    Team  Year
    1      789     2  Riders  2015
    3      673     3  Devils  2015
    5      812     4   kings  2015
    10     804     1  Royals  2015
    2016
       Points  Rank    Team  Year
    6     756     1   Kings  2016
    8     694     2  Riders  2016
    2017
        Points  Rank    Team  Year
    7      788     1   Kings  2017
    11     690     2  Riders  2017
    使用get_group()方法，可以选择一个组:
    =======================================
       Points  Rank    Team  Year
    0     876     1  Riders  2014
    2     863     2  Devils  2014
    4     741     3   Kings  2014
    9     701     4  Royals  2014
    =======================================
    Year
    2014    795.25
    2015    769.50
    2016    725.00
    2017    739.00
    Name: Points, dtype: float64
    另一种查看每个分组的大小的方法是应用size()函数:
    =======================================
            Points  Rank  Year
    Team                      
    Devils       2     2     2
    Kings        3     3     3
    Riders       4     4     4
    Royals       2     2     2
    kings        1     1     1
    通过分组系列，还可以传递函数的列表或字典来进行聚合:
    =======================================
             sum        mean         std
    Team                                
    Devils  1536  768.000000  134.350288
    Kings   2285  761.666667   24.006943
    Riders  3049  762.250000   88.567771
    Royals  1505  752.500000   72.831998
    kings    812  812.000000         NaN
    分组或列上的转换返回索引大小与被分组的索引相同的对象。因此，转换应该返回与组块大小相同的结果。:
    =======================================
           Points       Rank       Year
    0   12.843272 -15.000000 -11.618950
    1    3.020286   5.000000  -3.872983
    2    7.071068  -7.071068  -7.071068
    3   -7.071068   7.071068   7.071068
    4   -8.608621  11.547005 -10.910895
    5         NaN        NaN        NaN
    6   -2.360428  -5.773503   2.182179
    7   10.969049  -5.773503   8.728716
    8   -7.705963   5.000000   3.872983
    9   -7.071068   7.071068  -7.071068
    10   7.071068  -7.071068   7.071068
    11  -8.157595   5.000000  11.618950
    =======================================
    过滤根据定义的标准过滤数据并返回数据的子集。filter()函数用于过滤数据:
        Points  Rank    Team  Year
    0      876     1  Riders  2014
    1      789     2  Riders  2015
    4      741     3   Kings  2014
    6      756     1   Kings  2016
    7      788     1   Kings  2017
    8      694     2  Riders  2016
    11     690     2  Riders  2017
    =======================================
    
    Process finished with exit code 0

