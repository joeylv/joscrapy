1、可以使用单个列表或列表列表创建数据帧( _DataFrame_ )。

单个列表

    
    
    import pandas as pd
    data = [1,2,3,4,5]
    df = pd.DataFrame(data)
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
         0
    0    1
    1    2
    2    3
    3    4
    4    5

列表列表

    
    
    import pandas as pd
    data = [["Alex",10],["Bob",12],["Clarke",13]]
    df = pd.DataFrame(data,columns=["Name","Age"])
    print df
    #执行上面示例代码，得到以下结果 -
    
          Name      Age
    0     Alex      10
    1     Bob       12
    2     Clarke    13
    
    import pandas as pd
    data = [["Alex",10],["Bob",12],["Clarke",13]]
    df = pd.DataFrame(data,columns=["Name","Age"],dtype=float)
    print df
    #执行上面示例代码，得到以下结果 -可以观察到，dtype参数将Age列的类型更改为浮点。
    
          Name     Age
    0     Alex     10.0
    1     Bob      12.0
    2     Clarke   13.0

2、从ndarrays/Lists的字典来创建DataFrame

    
    
    #所有的ndarrays必须具有相同的长度。如果传递了索引(index)，则索引#的长度应等于数组的长度。
    #如果没有传递索引，则默认情况下，索引将为range(n)，其中n为数组长#度。
    import pandas as pd
    data = {"Name":["Tom", "Jack", "Steve", "Ricky"],"Age":[28,34,29,42]}
    df = pd.DataFrame(data)
    print df
    #执行上面示例代码，得到以下结果 -
    
          Age      Name
    0     28        Tom
    1     34       Jack
    2     29      Steve
    3     42      Ricky
    #注 - 观察值0,1,2,3。它们是分配给每个使用函数range(n)的默认索引。
    
    #使用数组创建一个索引的数据帧(DataFrame)。
    import pandas as pd
    data = {"Name":["Tom", "Jack", "Steve", "Ricky"],"Age":[28,34,29,42]}
    df = pd.DataFrame(data, index=["rank1","rank2","rank3","rank4"])
    print df
    #执行上面示例代码，得到以下结果 -
    
             Age    Name
    rank1    28      Tom
    rank2    34     Jack
    rank3    29    Steve
    rank4    42    Ricky
    
    #注意 - index参数为每行分配一个索引。

3、字典列表可作为输入数据传递以用来创建数据帧( _DataFrame_ )，字典键默认为列名。

    
    
    #以下示例显示如何通过传递字典列表来创建数据帧(DataFrame)。
    
    import pandas as pd
    data = [{"a": 1, "b": 2},{"a": 5, "b": 10, "c": 20}]
    df = pd.DataFrame(data)
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
        a    b      c
    0   1   2     NaN
    1   5   10   20.0
    #Shell
    #注意 - 观察到，NaN(不是数字)被附加在缺失的区域。
    
    #示例-2
    
    #以下示例显示如何通过传递字典列表和行索引来创建数据帧(DataFrame)。
    
    import pandas as pd
    data = [{"a": 1, "b": 2},{"a": 5, "b": 10, "c": 20}]
    df = pd.DataFrame(data, index=["first", "second"])
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
            a   b       c
    first   1   2     NaN
    second  5   10   20.0
    #Shell
    #实例-3
    
    #以下示例显示如何使用字典，行索引和列索引列表创建数据帧(DataFrame)。
    
    import pandas as pd
    data = [{"a": 1, "b": 2},{"a": 5, "b": 10, "c": 20}]
    
    #With two column indices, values same as dictionary keys
    df1 = pd.DataFrame(data, index=["first", "second"], columns=["a", "b"])
    
    #With two column indices with one index with other name
    df2 = pd.DataFrame(data, index=["first", "second"], columns=["a", "b1"])
    print df1
    print df2
    #Python
    #执行上面示例代码，得到以下结果 -
    
    #df1 output
             a  b
    first    1  2
    second   5  10
    
    #df2 output
             a  b1
    first    1  NaN
    second   5  NaN
    #Shell
    #注意 - 观察，df2使用字典键以外的列索引创建DataFrame; 因此，附加了NaN到位置上。 而df1是使用列索引创建的，与字典键相同，所以也附加了NaN。

4、从系列的字典来创建DataFrame

    
    
    #字典的系列可以传递以形成一个DataFrame。 所得到的索引是通过的所有系列索引的并集。
    
    #示例
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]),
          "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    print df
    #`
    #Python
    #执行上面示例代码，得到以下结果 -
    
          one    two
    a     1.0    1
    b     2.0    2
    c     3.0    3
    d     NaN    4
    #Shell
    #注意 - 对于第一个系列，观察到没有传递标签"d"，但在结果中，对于d标签，附加了NaN。
    
    #现在通过实例来了解列选择，添加和删除。
    
    #列选择
    #下面将通过从数据帧(DataFrame)中选择一列。
    
    #示例
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]),
          "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    print df ["one"]
    #Python
    #执行上面示例代码，得到以下结果 -
    
    
     
    a     1.0
    b     2.0
    c     3.0
    d     NaN
    Name: one, dtype: float64
    #Shell
    #列添加
    #下面将通过向现有数据框添加一个新列来理解这一点。
    
    #示例
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]),
          "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    
    # Adding a new column to an existing DataFrame object with column label by passing new series
    
    print ("Adding a new column by passing as Series:")
    df["three"]=pd.Series([10,20,30],index=["a","b","c"])
    print df
    
    print ("Adding a new column using the existing columns in DataFrame:")
    df["four"]=df["one"]+df["three"]
    
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
    Adding a new column by passing as Series:
         one   two   three
    a    1.0    1    10.0
    b    2.0    2    20.0
    c    3.0    3    30.0
    d    NaN    4    NaN
    
    #Adding a new column using the existing columns in DataFrame:
          one   two   three    four
    a     1.0    1    10.0     11.0
    b     2.0    2    20.0     22.0
    c     3.0    3    30.0     33.0
    d     NaN    4     NaN     NaN
    #Shell
    #列删除
    #列可以删除或弹出; 看看下面的例子来了解一下。
    
    #例子
    
    # Using the previous DataFrame, we will delete a column
    # using del function
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]), 
         "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"]), 
         "three" : pd.Series([10,20,30], index=["a","b","c"])}
    
    df = pd.DataFrame(d)
    print ("Our dataframe is:")
    print df
    
    # using del function
    print ("Deleting the first column using DEL function:")
    del df["one"]#删除标签为one的行
    print df
    
    # using pop function
    print ("Deleting another column using POP function:")
    df.pop("two")#删除标签为two的行
    print df
    Python
    #执行上面示例代码，得到以下结果 -
    
    Our dataframe is:
          one   three  two
    a     1.0    10.0   1
    b     2.0    20.0   2
    c     3.0    30.0   3
    d     NaN     NaN   4
    
    Deleting the first column using DEL function:
          three    two
    a     10.0     1
    b     20.0     2
    c     30.0     3
    d     NaN      4
    
    Deleting another column using POP function:
       three
    a  10.0
    b  20.0
    c  30.0
    d  NaN
    #Shell
    #行选择，添加和删除
    #现在将通过下面实例来了解行选择，添加和删除。我们从选择的概念开始。
    
    #标签选择
    
    #可以通过将行标签传递给loc()函数来选择行。参考以下示例代码 -
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]), 
         "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    print df.loc["b"]
    #Python
    #执行上面示例代码，得到以下结果 -
    
    one 2.0
    two 2.0
    Name: b, dtype: float64
    #Shell
    #结果是一系列标签作为DataFrame的列名称。 而且，系列的名称是检索的标签。
    
    按整数位置选择
    #
    #可以通过将整数位置传递给iloc()函数来选择行。参考以下示例代码 -
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]),
         "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    print df.iloc[2]
    #Python
    #执行上面示例代码，得到以下结果 -
    
    one   3.0
    two   3.0
    Name: c, dtype: float64
    #Shell
    #行切片
    #可以使用:运算符选择多行。参考以下示例代码 -
    
    import pandas as pd
    
    d = {"one" : pd.Series([1, 2, 3], index=["a", "b", "c"]), 
        "two" : pd.Series([1, 2, 3, 4], index=["a", "b", "c", "d"])}
    
    df = pd.DataFrame(d)
    print df[2:4]
    #Python
    #执行上面示例代码，得到以下结果 -
    
          one    two
    c     3.0     3
    d     NaN     4
    #Shell
    #附加行
    
    #使用append()函数将新行添加到DataFrame。 此功能将附加行结束。
    
    import pandas as pd
    
    df = pd.DataFrame([[1, 2], [3, 4]], columns = ["a","b"])
    df2 = pd.DataFrame([[5, 6], [7, 8]], columns = ["a","b"])
    
    df = df.append(df2)#添加多行
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
       a  b
    0  1  2
    1  3  4
    0  5  6
    1  7  8
    #Shell
    #删除行
    
    #使用索引标签从DataFrame中删除或删除行。 如果标签重复，则会删除多行。
    
    #如果有注意，在上述示例中，有标签是重复的。这里再多放一个标签，看看有多少行被删除。
    
    import pandas as pd
    
    df = pd.DataFrame([[1, 2], [3, 4]], columns = ["a","b"])
    df2 = pd.DataFrame([[5, 6], [7, 8]], columns = ["a","b"])
    
    df = df.append(df2)
    
    # Drop rows with label 0
    df = df.drop(0) #删除多行同标签的数据
    
    print df
    #Python
    #执行上面示例代码，得到以下结果 -
    
      a b
    1 3 4
    1 7 8
    #Shell
    #在上面的例子中，一共有两行被删除，因为这两行包含相同的标签0。

