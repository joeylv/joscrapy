1、检查缺失值

为了更容易地检测缺失值(以及跨越不同的数组`dtype`)，Pandas提供了`isnull()`和`notnull()`函数，它们也是Series和DataFrame对象的方法
-

    
    
    示例1
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    
    print (df["one"].isnull())
    Python
    执行上面示例代码，得到以下结果 -
    
    a    False
    b     True
    c    False
    d     True
    e    False
    f    False
    g     True
    h    False
    Name: one, dtype: bool
    Shell
    示例2
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    
    print (df["one"].notnull())
    Python
    执行上面示例代码，得到以下结果 -
    
    a     True
    b    False
    c     True
    d    False
    e     True
    f     True
    g    False
    h     True
    Name: one, dtype: bool
    Shell
    缺少数据的计算
    在求和数据时，NA将被视为0
    如果数据全部是NA，那么结果将是NA
    实例1
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    
    print (df["one"].sum())
    Python
    执行上面示例代码，得到以下结果 -
    
    -2.6163354325445014
    Shell
    示例2
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(index=[0,1,2,3,4,5],columns=["one","two"])
    print (df["one"].sum())
    Python
    执行上面示例代码，得到以下结果 -
    
    nan

2、清理/填充缺少

数据 _Pandas_ 提供了各种方法来清除缺失的值。

`fillna()`函数可以通过几种方法用非空数据“填充”`NA`值，

在下面的章节中将学习和使用。用标量值替换NaN

以下程序显示如何用`0`替换`NaN`

    
    
    import pandas as pd
    import numpy as np
    df = pd.DataFrame(np.random.randn(3, 3), index=["a", "c", "e"],columns=["one",
    "two", "three"])
    df = df.reindex(["a", "b", "c"])
    print (df)
    print ("NaN replaced with "0":")
    print (df.fillna(0))
    Python
    执行上面示例代码，得到以下结果 -
    
            one       two     three
    a -0.479425 -1.711840 -1.453384
    b       NaN       NaN       NaN
    c -0.733606 -0.813315  0.476788
    NaN replaced with "0":
            one       two     three
    a -0.479425 -1.711840 -1.453384
    b  0.000000  0.000000  0.000000
    c -0.733606 -0.813315  0.476788
    Shell
    在这里填充零值; 当然，也可以填写任何其他的值。
    
    填写NA前进和后退
    使用重构索引章节讨论的填充概念，来填补缺失的值。
    
    方法    动作
    pad/fill    填充方法向前
    bfill/backfill    填充方法向后
    示例1
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    
    print (df.fillna(method="pad"))
    Python
    执行上面示例代码，得到以下结果 -
    
    
     
            one       two     three
    a  0.614938 -0.452498 -2.113057
    b  0.614938 -0.452498 -2.113057
    c -0.118390  1.333962 -0.037907
    d -0.118390  1.333962 -0.037907
    e  0.699733  0.502142 -0.243700
    f  0.544225 -0.923116 -1.123218
    g  0.544225 -0.923116 -1.123218
    h -0.669783  1.187865  1.112835
    Shell
    示例2
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    print (df.fillna(method="backfill"))
    Python
    执行上面示例代码，得到以下结果 -
    
            one       two     three
    a  2.278454  1.550483 -2.103731
    b -0.779530  0.408493  1.247796
    c -0.779530  0.408493  1.247796
    d  0.262713 -1.073215  0.129808
    e  0.262713 -1.073215  0.129808
    f -0.600729  1.310515 -0.877586
    g  0.395212  0.219146 -0.175024
    h  0.395212  0.219146 -0.175024

3、丢失缺少的值

如果只想排除缺少的值，则使用`dropna`函数和`axis`参数。 默认情况下，`axis =
0`，即在行上应用，这意味着如果行内的任何值是`NA`，那么整个行被排除。

    
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    print (df.dropna())
    Python
    执行上面示例代码，得到以下结果 -
    
            one       two     three
    a -0.719623  0.028103 -1.093178
    c  0.040312  1.729596  0.451805
    e -1.029418  1.920933  1.289485
    f  1.217967  1.368064  0.527406
    h  0.667855  0.147989 -1.035978
    Shell
    示例2
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(np.random.randn(5, 3), index=["a", "c", "e", "f",
    "h"],columns=["one", "two", "three"])
    
    df = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
    print (df.dropna(axis=1))
    Python
    执行上面示例代码，得到以下结果 -
    
    Empty DataFrame
    Columns: []
    Index: [a, b, c, d, e, f, g, h]
    Shell
    替换丢失(或)通用值
    很多时候，必须用一些具体的值取代一个通用的值。可以通过应用替换方法来实现这一点。
    
    用标量值替换NA是fillna()函数的等效行为。
    
    示例1
    
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({"one":[10,20,30,40,50,2000],
    "two":[1000,0,30,40,50,60]})
    print (df.replace({1000:10,2000:60}))
    Python
    执行上面示例，得到以下结果 -
    
       one  two
    0   10   10
    1   20    0
    2   30   30
    3   40   40
    4   50   50
    5   60   60

