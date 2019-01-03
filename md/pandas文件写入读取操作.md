
    #encoding:utf8
    import pandas as pd
    import numpy as np
    from pylab import *
    df=pd.read_csv("./path")#CSV文件读取
    df1=pd.read_excel("./path")#excel文件读取
    df.to_csv("./path")#CSV文件写入
    df1.to_excel("./path")#excel文件写入

