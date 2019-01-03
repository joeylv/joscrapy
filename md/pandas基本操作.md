1、通过传递`numpy`数组，使用`datetime`索引和标记列来创建`DataFrame`

    
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=7)#
    print(dates)
    
    print("--"*16)
    df = pd.DataFrame(np.random.randn(7,4), index=dates, columns=list("ABCD"))
    print(df)  
    #index为主键，为索引值；columns为列的label值；
    
    
    结果为：  
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
    DatetimeIndex(["2017-01-01", "2017-01-02", "2017-01-03", "2017-01-04",
                   "2017-01-05", "2017-01-06", "2017-01-07"],
                  dtype="datetime64[ns]", freq="D")
    --------------------------------
                       A         B         C         D
    2017-01-01 -0.732038  0.329773 -0.156383  0.270800
    2017-01-02  0.750144  0.722037 -0.849848 -1.105319
    2017-01-03 -0.786664 -0.204211  1.246395  0.292975
    2017-01-04 -1.108991  2.228375  0.079700 -1.738507
    2017-01-05  0.348526 -0.960212  0.190978 -2.223966
    2017-01-06 -0.579689 -1.355910  0.095982  1.233833
    2017-01-07  1.086872  0.664982  0.377787  1.012772

2、通过传递可以转换为类似系列的对象的字典来创建DataFrame

    
    
    import pandas as pd
    import numpy as np
    
    df2 = pd.DataFrame({ "A" : 1.,
                         "B" : pd.Timestamp("20170102"),
                         "C" : pd.Series(1,index=list(range(4)),dtype="float32"),
                         "D" : np.array([3] * 4,dtype="int32"),
                         "E" : pd.Categorical(["test","train","test","train"]),
                         "F" : "foo" })
    
    print(df2)
    Python
    #执行上面示例代码后，输出结果如下 -
    
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
         A          B    C  D      E    F
    0  1.0 2017-01-02  1.0  3   test  foo
    1  1.0 2017-01-02  1.0  3  train  foo
    2  1.0 2017-01-02  1.0  3   test  foo
    3  1.0 2017-01-02  1.0  3  train  foo

3、

    
    
    import pandas as pd
    import numpy as np
    dates = pd.date_range("20170101", periods=7)
    df = pd.DataFrame(np.random.randn(7,4), index=dates, columns=list("ABCD"))
    print(df)
    print("-"*20)
    print(df.head(3))#选取前3行数据
    print("--------------" * 10)
    print(df.tail(3))#选取后3行数据
    #结果为：
                       A         B         C         D
    2017-01-01 -0.793688  2.181523  0.557200 -0.279401
    2017-01-02  0.671325 -0.756951  1.081400  1.008983
    2017-01-03  0.302179  0.567060  0.006960 -0.091598
    2017-01-04  0.510611  0.389851  2.271782 -0.700009
    2017-01-05  0.393021  0.306979  1.935575  0.867504
    2017-01-06 -1.306705  0.324890 -0.271238  1.234804
    2017-01-07  1.090559 -0.427427  0.902197  0.157098
    --------------------
                       A         B        C         D
    2017-01-01 -0.793688  2.181523  0.55720 -0.279401
    2017-01-02  0.671325 -0.756951  1.08140  1.008983
    2017-01-03  0.302179  0.567060  0.00696 -0.091598
    --------------------------------------------------------------------------------------------------------------------------------------------
                       A         B         C         D
    2017-01-05  0.393021  0.306979  1.935575  0.867504
    2017-01-06 -1.306705  0.324890 -0.271238  1.234804
    2017-01-07  1.090559 -0.427427  0.902197  0.157098

4、

    
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=7)
    df = pd.DataFrame(np.random.randn(7,4), index=dates, columns=list("ABCD"))
    print("index is :" )
    print(df.index)#获取主键值
    print("columns is :" )
    print(df.columns)#获取column值
    print("values is :" )
    print(df.values)#获取数据值
    
    
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
    index is :
    DatetimeIndex(["2017-01-01", "2017-01-02", "2017-01-03", "2017-01-04",
                   "2017-01-05", "2017-01-06", "2017-01-07"],
                  dtype="datetime64[ns]", freq="D")
    columns is :
    Index(["A", "B", "C", "D"], dtype="object")
    values is :
    [[ 2.23820398  0.18440123  0.08039084 -0.27751926]
     [-0.12335513  0.36641304 -0.28617579  0.34383109]
     [-0.85403491  0.63876989  1.26032173 -1.27382333]
     [-0.07262661 -0.01788962  0.28748668  1.12715561]
     [-1.14293392 -0.88263364  0.72250762 -1.64051326]
     [ 0.41864083  0.40545953 -0.14591541 -0.57168728]
     [ 1.01383531 -0.22793823 -0.44045634  1.04799829]]

5、描述显示数据的快速统计摘要

    
    
    import pandas as pd
    import numpy as np
    dates = pd.date_range("20170101", periods=7)
    df = pd.DataFrame(np.random.randn(7,4), index=dates, columns=list("ABCD"))
    print(df.describe())
    ##################################
                  A         B         C         D
    count  7.000000  7.000000  7.000000  7.000000
    mean   0.254545 -0.124449  0.466692  0.076727
    std    0.701449  1.038154  1.058242  0.633414
    min   -0.826816 -1.775741 -1.025271 -0.885684
    25%   -0.202499 -0.649271 -0.173390 -0.275273
    50%    0.401212  0.030409  0.588951  0.211761
    75%    0.724367  0.556147  1.094887  0.411284
    max    1.163683  1.060436  1.860166  0.938987

6、调换数据 行列转换 类似矩阵转置

    
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    print(df.T)################
    Python
    执行上面示例代码后，输出结果如下 -
    
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
       2017-01-01  2017-01-02  2017-01-03  2017-01-04  2017-01-05  2017-01-06
    A    0.932454   -2.148503    1.398975    1.565676   -0.167527   -0.242041
    B    0.584585    1.373330   -0.069801   -0.102857    1.286432   -0.703491
    C   -0.345119   -0.680955    1.686750    1.184996    0.016170   -0.663963
    D    0.431751    0.444830   -1.524739    0.040007    0.220172    1.423627

7、通过轴排序

    
    
    import pandas as pd
    import numpy as np
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    print("df:")
    print(df)
    print("axis=1 ascending=False: ")
    print(df.sort_index(axis=1, ascending=False))
    print("axis=0 ascending=False: ")
    print(df.sort_index(axis=0, ascending=False))
    print("axis=1 ascending=True: ")
    print(df.sort_index(axis=1, ascending=True))
    print("axis=0 ascending=True: ")
    print(df.sort_index(axis=0, ascending=True))
    
    df:
                       A         B         C         D
    2017-01-01  1.383892 -0.723536  0.335398  0.450175
    2017-01-02 -0.614480  1.076641 -1.102721 -1.418669
    2017-01-03  1.337403 -0.176513  0.992887  0.094828
    2017-01-04  0.897667  0.488634  1.648647  0.056338
    2017-01-05 -0.241695  1.560610  0.391279  0.361618
    2017-01-06  1.052111 -1.719268  0.341144  2.130635
    axis=1 ascending=False: 
                       D         C         B         A
    2017-01-01  0.450175  0.335398 -0.723536  1.383892
    2017-01-02 -1.418669 -1.102721  1.076641 -0.614480
    2017-01-03  0.094828  0.992887 -0.176513  1.337403
    2017-01-04  0.056338  1.648647  0.488634  0.897667
    2017-01-05  0.361618  0.391279  1.560610 -0.241695
    2017-01-06  2.130635  0.341144 -1.719268  1.052111
    axis=0 ascending=False: 
                       A         B         C         D
    2017-01-06  1.052111 -1.719268  0.341144  2.130635
    2017-01-05 -0.241695  1.560610  0.391279  0.361618
    2017-01-04  0.897667  0.488634  1.648647  0.056338
    2017-01-03  1.337403 -0.176513  0.992887  0.094828
    2017-01-02 -0.614480  1.076641 -1.102721 -1.418669
    2017-01-01  1.383892 -0.723536  0.335398  0.450175
    axis=1 ascending=True: 
                       A         B         C         D
    2017-01-01  1.383892 -0.723536  0.335398  0.450175
    2017-01-02 -0.614480  1.076641 -1.102721 -1.418669
    2017-01-03  1.337403 -0.176513  0.992887  0.094828
    2017-01-04  0.897667  0.488634  1.648647  0.056338
    2017-01-05 -0.241695  1.560610  0.391279  0.361618
    2017-01-06  1.052111 -1.719268  0.341144  2.130635
    axis=0 ascending=True: 
                       A         B         C         D
    2017-01-01  1.383892 -0.723536  0.335398  0.450175
    2017-01-02 -0.614480  1.076641 -1.102721 -1.418669
    2017-01-03  1.337403 -0.176513  0.992887  0.094828
    2017-01-04  0.897667  0.488634  1.648647  0.056338
    2017-01-05 -0.241695  1.560610  0.391279  0.361618
    2017-01-06  1.052111 -1.719268  0.341144  2.130635

8、

    
    
    #按值排序，参考以下示例程序 -
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    print(df.sort_values(by="B"))  
    或者 print(df.sort_values("B"))
    
    
    #` #Python #执行上面示例代码后，输出结果如下 -  A B C D 2017-01-06 0.764517 -1.526019 0.400456 -0.182082 2017-01-05 -0.177845 -1.269836 -0.534676 0.796666 2017-01-04 -0.981485 -0.082572 -1.272123 0.508929 2017-01-02 -0.290117 0.053005 -0.295628 -0.346965 2017-01-03 0.941131 0.799280 2.054011 -0.684088 2017-01-01 0.597788 0.892008 0.903053 -0.821024

9、

    
    
    #选择一列，产生一个系列，相当于df.A，参考以下示例程序 -
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    
    print(df["A"])
    `
    Python
    执行上面示例代码后，输出结果如下 -
    
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
    2017-01-01    0.317460
    2017-01-02   -0.933726
    2017-01-03    0.167860
    2017-01-04    0.816184
    2017-01-05   -0.745503
    2017-01-06    0.505319
    Freq: D, Name: A, dtype: float64
    
    
    #选择通过[]操作符，选择切片行。参考以下示例程序 -
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    
    print(df[0:3])
    
    print("========= 指定选择日期 ========")
    
    print(df["20170102":"20170103"])
    `
    Python
    执行上面示例代码后，输出结果如下 -
    
    runfile("C:/Users/Administrator/.spyder-py3/temp.py", wdir="C:/Users/Administrator/.spyder-py3")
                       A         B         C         D
    2017-01-01  1.103449  0.926571 -1.649978 -0.309270
    2017-01-02  0.516404 -0.734076 -0.081163 -0.528497
    2017-01-03  0.240356  0.231224 -1.463315 -1.157256
    ========= 指定选择日期 ========
                       A         B         C         D
    2017-01-02  0.516404 -0.734076 -0.081163 -0.528497
    2017-01-03  0.240356  0.231224 -1.463315 -1.157256
    
    
    #按标签选择
    #使用标签获取横截面，参考以下示例程序 -
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range("20170101", periods=6)
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list("ABCD"))
    print("df:")
    print(df)
    print("-"*50)
    print(df.loc[dates[0]])
    
    
    
    df:
                       A         B         C         D
    2017-01-01  0.592135 -0.763021  0.420110 -0.766594
    2017-01-02 -0.203704  0.471745 -1.770516  1.100931
    2017-01-03  0.717300  0.299209 -0.856983  1.163530
    2017-01-04 -0.581382 -0.633760 -0.012644 -0.058334
    2017-01-05 -0.081392  0.091552  1.159507  0.802206
    2017-01-06  1.126909  2.306718  0.511462 -0.864211
    --------------------------------------------------
    A    0.592135
    B   -0.763021
    C    0.420110
    D   -0.766594
    Name: 2017-01-01 00:00:00, dtype: float64

8、排序算法

    
    
    #排序算法
    #sort_values()提供了从mergeesort，heapsort和quicksort中选择算法的一个配置。Mergesort是唯一稳定的算法。参考以下示例代码 -
    
    import pandas as pd
    import numpy as np
    
    unsorted_df = pd.DataFrame({"col1":[2,1,1,1],"col2":[1,3,2,4]})
    sorted_df = unsorted_df.sort_values(by="col1" ,kind="mergesort")
    
    print (sorted_df)

