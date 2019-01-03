`datetime.now()`用于获取当前的日期和时间

`print pd.datetime.now()`

    
    
    #encoding:utf8
    
    import pandas as pd
    print("(pd.datetime.now()):")
    print (pd.datetime.now())
    time = pd.Timestamp("2018-11-01")
    print("time = pd.Timestamp("2018-11-01")")
    print(time)
    time = pd.Timestamp(1588686880,unit="s")
    print("pd.Timestamp(1588686880,unit="s"):")
    print(time)
    time = pd.date_range("12:00", "23:59", freq="30min").time
    print("pd.date_range("12:00", "23:59", freq="30min").time")
    print(time)
    time = pd.date_range("12:00", "23:59", freq="H").time
    print("freq=;H;")
    print(time)
    #要转换类似日期的对象(例如字符串，时代或混合)的序列或类似列表的对象，可以使用to_datetime函数。
    # 当传递时将返回一个Series(具有相同的索引)，而类似列表被转换为DatetimeIndex
    print("================================================================")
    time = pd.to_datetime(pd.Series(["Jul 31, 2009","2019-10-10", None]))
    print(time)
    
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    (pd.datetime.now()):
    2018-05-26 21:16:50.838958
    time = pd.Timestamp("2018-11-01")
    2018-11-01 00:00:00
    pd.Timestamp(1588686880,unit="s"):
    2020-05-05 13:54:40
    pd.date_range("12:00", "23:59", freq="30min").time
    [datetime.time(12, 0) datetime.time(12, 30) datetime.time(13, 0)
     datetime.time(13, 30) datetime.time(14, 0) datetime.time(14, 30)
     datetime.time(15, 0) datetime.time(15, 30) datetime.time(16, 0)
     datetime.time(16, 30) datetime.time(17, 0) datetime.time(17, 30)
     datetime.time(18, 0) datetime.time(18, 30) datetime.time(19, 0)
     datetime.time(19, 30) datetime.time(20, 0) datetime.time(20, 30)
     datetime.time(21, 0) datetime.time(21, 30) datetime.time(22, 0)
     datetime.time(22, 30) datetime.time(23, 0) datetime.time(23, 30)]
    freq=;H;
    [datetime.time(12, 0) datetime.time(13, 0) datetime.time(14, 0)
     datetime.time(15, 0) datetime.time(16, 0) datetime.time(17, 0)
     datetime.time(18, 0) datetime.time(19, 0) datetime.time(20, 0)
     datetime.time(21, 0) datetime.time(22, 0) datetime.time(23, 0)]
    ================================================================
    0   2009-07-31
    1   2019-10-10
    2          NaT
    dtype: datetime64[ns]
    
    Process finished with exit code 0

