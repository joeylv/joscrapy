
    #-*- coding: utf-8 -*-
    #主成分分析 降维
    import pandas as pd
    
    #参数初始化
    inputfile = "../data/principal_component.xls"
    outputfile = "../tmp/dimention.xls" #降维后的数据
    
    data = pd.read_excel(inputfile, header = None) #读入数据
    
    from sklearn.decomposition import PCA
    
    pca = PCA(3)#选取3个主成分
    pca.fit(data)
    low_d=pca.transform(data)#用他来降低维度
    pd.DataFrame(low_d).to_excel(outputfile)
    pca.inverse_transform(low_d)#恢复降维之前的数据
    print(pca.components_) #返回模型的各个特征向量
    print(pca.explained_variance_ratio_) #返回各个成分各自的方差百分比

