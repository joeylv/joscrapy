1、通过指定周期和频率，使用`date.range()`函数就可以创建日期序列。 默认情况下，范围的频率是天。

2、`bdate_range()`用来表示商业日期范围，不同于`date_range()`，它不包括星期六和星期天。’

    
    
    #encoding:utf8
    
    import pandas as pd
    datelist = pd.date_range("2020/11/21", periods=5)
    print("===============================================================")
    print(datelist)
    datelist = pd.date_range("2020/11/21", periods=5,freq="M")
    print("===============================================================")
    print(datelist)
    datelist = pd.bdate_range("2011/11/03", periods=5)
    print("===============================================================")
    print(datelist)
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    ===============================================================
    DatetimeIndex(["2020-11-21", "2020-11-22", "2020-11-23", "2020-11-24",
                   "2020-11-25"],
                  dtype="datetime64[ns]", freq="D")
    ===============================================================
    DatetimeIndex(["2020-11-30", "2020-12-31", "2021-01-31", "2021-02-28",
                   "2021-03-31"],
                  dtype="datetime64[ns]", freq="M")
    ===============================================================
    DatetimeIndex(["2011-11-03", "2011-11-04", "2011-11-07", "2011-11-08",
                   "2011-11-09"],
                  dtype="datetime64[ns]", freq="B")
    
    Process finished with exit code 0

