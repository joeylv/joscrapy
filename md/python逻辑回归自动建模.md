
    #-*- coding: utf-8 -*-
    #逻辑回归 自动建模
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression as LR
    from sklearn.linear_model import RandomizedLogisticRegression as RLR
    #参数初始化
    filename = "../data/bankloan.xls"
    data = pd.read_excel(filename)
    x = data.iloc[:,:8].as_matrix()#使用pandas读取文件  就可以不用管label column标签
    y = data.iloc[:,8].as_matrix()
    
    rlr = RLR() #建立随机逻辑回归模型，进行特征选择和变量筛选
    rlr.fit(x, y) #训练模型
    egeList=rlr.get_support() #获取筛选后的特征
    egeList=np.append(egeList,False)#往numpy数组中 添加一个False元素  使用np.append(array,ele)方法
    print("rlr.get_support():")
    print(egeList)
    print(u"随机逻辑回归模型特征选择结束！！！")
    print(u"有效特征为：%s" % ",".join(data.columns[egeList]))
    x = data[data.columns[egeList]].as_matrix() #筛选好特征值
    
    lr = LR() #建立逻辑回归模型
    lr.fit(x, y) #用筛选后的特征进行训练
    print(u"逻辑回归训练模型结束！！！")
    print(u"模型的平均正确率：%s" % lr.score(x, y)) #给出模型的平均正确率，本例为81.4%
      
      
      
    D:\Download\python3\python3.exe "D:\Program Files\JetBrains\PyCharm 2017.3.3\helpers\pydev\pydev_run_in_console.py" 56033 56034 "E:/A正在学习/python data dig/chapter5/demo/code/5-1_logistic_regression.py"
    Running E:/A正在学习/python data dig/chapter5/demo/code/5-1_logistic_regression.py
    import sys; print("Python %s on %s" % (sys.version, sys.platform))
    sys.path.extend(["E:\\A正在学习\\python data dig", "E:/A正在学习/python data dig/chapter5/demo/code"])
    C:\Users\Snow\AppData\Roaming\Python\Python35\site-packages\sklearn\utils\deprecation.py:58: DeprecationWarning: Class RandomizedLogisticRegression is deprecated; The class RandomizedLogisticRegression is deprecated in 0.19 and will be removed in 0.21.
      warnings.warn(msg, category=DeprecationWarning)
    rlr.get_support():
    [False False  True  True False  True  True False False]
    随机逻辑回归模型特征选择结束！！！
    有效特征为：工龄,地址,负债率,信用卡负债
    逻辑回归训练模型结束！！！
    模型的平均正确率：0.8142857142857143
    PyDev console: starting.
    Python 3.5.4 (v3.5.4:3f56838, Aug  8 2017, 02:17:05) [MSC v.1900 64 bit (AMD64)] on win32

