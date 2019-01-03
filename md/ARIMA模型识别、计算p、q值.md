
    #-*- coding: utf-8 -*-
    #确定最佳p、d、q值
    import pandas as pd
    
    #参数初始化
    discfile = "../data/discdata_processed.xls"
    
    data = pd.read_excel(discfile, index_col = "COLLECTTIME")
    data = data.iloc[: len(data)-5] #不使用最后5个数据
    xdata = data["CWXT_DB:184:D:\\"]
    
    from statsmodels.tsa.arima_model import ARIMA
    
    #定阶
    pmax = int(len(xdata)/10) #一般阶数不超过length/10
    qmax = int(len(xdata)/10) #一般阶数不超过length/10
    bic_matrix = [] #bic矩阵
    for p in range(pmax+1):
      tmp = []
      for q in range(qmax+1):
        try: #存在部分报错，所以用try来跳过报错。
          tmp.append(ARIMA(xdata, (p,1,q)).fit().bic)
        except:
          tmp.append(None)
      bic_matrix.append(tmp)
    print(bic_matrix)
    #[[1275.6868239439104, 1273.190434524266, 1273.5749982328914, 1274.4669152438114, None], 
    #[1276.7491283595593, 1271.8999324285992, None, None, None], 
    #[1279.6942963992901, 1277.5553412371614, None, 1280.0924824267408, None],
    # [1278.0659994468958, 1278.9885944429066, 1282.782534558853, 1285.943493708969, None],
    # [1281.220790614283, 1282.6999920212124, 1286.2975191780365, 1290.1950373803218, None]]
    bic_matrix = pd.DataFrame(bic_matrix) #从中可以找出最小值
    print(bic_matrix)
    #              0            1            2            3     4
    # 0  1275.686824  1273.190435  1273.574998  1274.466915  None
    # 1  1276.749128  1271.899932          NaN          NaN  None
    # 2  1279.694296  1277.555341          NaN  1280.092482  None
    # 3  1278.065999  1278.988594  1282.782535  1285.943494  None
    # 4  1281.220791  1282.699992  1286.297519  1290.195037  None
    print(bic_matrix.stack())
    # 0  0    1275.69
    #    1    1273.19
    #    2    1273.57
    #    3    1274.47
    # 1  0    1276.75
    #    1     1271.9
    # 2  0    1279.69
    #    1    1277.56
    #    3    1280.09
    # 3  0    1278.07
    #    1    1278.99
    #    2    1282.78
    #    3    1285.94
    # 4  0    1281.22
    #    1     1282.7
    #    2     1286.3
    #    3     1290.2
    p,q = bic_matrix.stack().astype("float64").idxmin() #先用stack展平，然后用idxmin找出最小值位置。
    print(u"BIC最小的p值和q值为：%s、%s" %(p,q))

