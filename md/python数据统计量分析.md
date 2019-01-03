
    #-*- coding: utf-8 -*-
    #餐饮销量数据统计量分析
    from __future__ import print_function
    import pandas as pd
    
    catering_sale = "../data/catering_sale.xls" #餐饮数据
    data = pd.read_excel(catering_sale, index_col = u"日期") #读取数据，指定“日期”列为索引列
    data = data[(data[u"销量"] > 400)&(data[u"销量"] < 5000)] #过滤异常数据
    statistics = data.describe() #保存基本统计量
    
    statistics.loc["range"] = statistics.loc["max"]-statistics.loc["min"] #极差
    statistics.loc["var"] = statistics.loc["std"]/statistics.loc["mean"] #变异系数
    statistics.loc["dis"] = statistics.loc["75%"]-statistics.loc["25%"] #四分位数间距
    
    print(statistics)
    
    D:\Download\python3\python3.exe "E:/A正在学习/python data dig/chapter3/demo/code/3-2_statistics_analyze.py"
                    销量
    count   195.000000
    mean   2744.595385
    std     424.739407
    min     865.000000
    25%    2460.600000
    50%    2655.900000
    75%    3023.200000
    max    4065.200000
    range  3200.200000
    var       0.154755
    dis     562.600000
    
    Process finished with exit code 0

