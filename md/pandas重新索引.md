
    #重新索引会更改DataFrame的行标签和列标签。重新索引意味着符合数据以匹配特定轴上的一组给定的标签。
    
    #可以通过索引来实现多个操作 -
    
    #重新排序现有数据以匹配一组新的标签。
    #在没有标签数据的标签位置插入缺失值(NA)标记。
    #示例
    
    import pandas as pd
    import numpy as np
    
    N=20
    
    df = pd.DataFrame({
       "A": pd.date_range(start="2016-01-01",periods=N,freq="D"),
       "x": np.linspace(0,stop=N-1,num=N),
       "y": np.random.rand(N),
       "C": np.random.choice(["Low","Medium","High"],N).tolist(),
       "D": np.random.normal(100, 10, size=(N)).tolist()
    })
    
    #reindex the DataFrame
    df_reindexed = df.reindex(index=[0,2,5], columns=["A", "C", "B"])
    
    print (df_reindexed)
    #Python
    #执行上面示例代码，得到以下结果 -
    
                A    C     B
    0  2016-01-01  Low   NaN
    2  2016-01-03  High  NaN
    5  2016-01-06  Low   NaN
    #Shell
    #重建索引与其他对象对齐
    #有时可能希望采取一个对象和重新索引，其轴被标记为与另一个对象相同。 考虑下面的例子来理解这一点。
    
    #示例
    
    import pandas as pd
    import numpy as np
    
    df1 = pd.DataFrame(np.random.randn(10,3),columns=["col1","col2","col3"])
    df2 = pd.DataFrame(np.random.randn(7,3),columns=["col1","col2","col3"])
    
    df1 = df1.reindex_like(df2)
    print df1
    #Python
    #执行上面示例代码，得到以下结果 -
    
              col1         col2         col3
    0    -2.467652    -1.211687    -0.391761
    1    -0.287396     0.522350     0.562512
    2    -0.255409    -0.483250     1.866258
    3    -1.150467    -0.646493    -0.222462
    4     0.152768    -2.056643     1.877233
    5    -1.155997     1.528719    -1.343719
    6    -1.015606    -1.245936    -0.295275
    #Shell
    #注意 - 在这里，df1数据帧(DataFrame)被更改并重新编号，如df2。 列名称应该匹配，否则将为整个列标签添加NAN。
    
    #填充时重新加注
    #reindex()采用可选参数方法，它是一个填充方法，其值如下：
    
    #pad/ffill - 向前填充值
    #bfill/backfill - 向后填充值
    #nearest - 从最近的索引值填充
    #示例
    
    import pandas as pd
    import numpy as np
    
    df1 = pd.DataFrame(np.random.randn(6,3),columns=["col1","col2","col3"])
    df2 = pd.DataFrame(np.random.randn(2,3),columns=["col1","col2","col3"])
    
    # Padding NAN"s
    print df2.reindex_like(df1)
    
    # Now Fill the NAN"s with preceding Values
    print ("Data Frame with Forward Fill:")
    print df2.reindex_like(df1,method="ffill")
    #Python
    #执行上面示例代码时，得到以下结果 -
    
             col1        col2       col3
    0    1.311620   -0.707176   0.599863
    1   -0.423455   -0.700265   1.133371
    2         NaN         NaN        NaN
    3         NaN         NaN        NaN
    4         NaN         NaN        NaN
    5         NaN         NaN        NaN
    
    Data Frame with Forward Fill:
             col1        col2        col3
    0    1.311620   -0.707176    0.599863
    1   -0.423455   -0.700265    1.133371
    2   -0.423455   -0.700265    1.133371
    3   -0.423455   -0.700265    1.133371
    4   -0.423455   -0.700265    1.133371
    5   -0.423455   -0.700265    1.133371
    #Shell
    #注 - 最后四行被填充了。
    
    #重建索引时的填充限制
    #限制参数在重建索引时提供对填充的额外控制。限制指定连续匹配的最大计数。考虑下面的例子来理解这个概念 -
    
    #示例
    
    
     
    import pandas as pd
    import numpy as np
    
    df1 = pd.DataFrame(np.random.randn(6,3),columns=["col1","col2","col3"])
    df2 = pd.DataFrame(np.random.randn(2,3),columns=["col1","col2","col3"])
    
    # Padding NAN"s
    print df2.reindex_like(df1)
    
    # Now Fill the NAN"s with preceding Values
    print ("Data Frame with Forward Fill limiting to 1:")
    print df2.reindex_like(df1,method="ffill",limit=1)
    #Python
    #在执行上面示例代码时，得到以下结果 -
    
             col1        col2        col3
    0    0.247784    2.128727    0.702576
    1   -0.055713   -0.021732   -0.174577
    2         NaN         NaN         NaN
    3         NaN         NaN         NaN
    4         NaN         NaN         NaN
    5         NaN         NaN         NaN
    
    #Data Frame with Forward Fill limiting to 1:
             col1        col2        col3
    0    0.247784    2.128727    0.702576
    1   -0.055713   -0.021732   -0.174577
    2   -0.055713   -0.021732   -0.174577
    3         NaN         NaN         NaN
    4         NaN         NaN         NaN
    5         NaN         NaN         NaN
    #Shell
    #注意 - 只有第7行由前6行填充。 然后，其它行按原样保留。
    
    #重命名
    #rename()方法允许基于一些映射(字典或者系列)或任意函数来重新标记一个轴。
    #看看下面的例子来理解这一概念。
    
    #示例
    
    import pandas as pd
    import numpy as np
    
    df1 = pd.DataFrame(np.random.randn(6,3),columns=["col1","col2","col3"])
    print df1
    
    print ("After renaming the rows and columns:")
    print df1.rename(columns={"col1" : "c1", "col2" : "c2"},index = {0 : "apple", 1 : "banana", 2 : "durian"})
    #Python
    #执行上面示例代码，得到以下结果 -
    
             col1        col2        col3
    0    0.486791    0.105759    1.540122
    1   -0.990237    1.007885   -0.217896
    2   -0.483855   -1.645027   -1.194113
    3   -0.122316    0.566277   -0.366028
    4   -0.231524   -0.721172   -0.112007
    5    0.438810    0.000225    0.435479
    
    #After renaming the rows and columns:
                    c1          c2        col3
    apple     0.486791    0.105759    1.540122
    banana   -0.990237    1.007885   -0.217896
    durian   -0.483855   -1.645027   -1.194113
    3        -0.122316    0.566277   -0.366028
    4        -0.231524   -0.721172   -0.112007
    5         0.438810    0.000225    0.435479
    #Shell
    #rename()方法提供了一个inplace命名参数，默认为False并复制底层数据。 指定传递inplace = True则表示将数据重命名。

