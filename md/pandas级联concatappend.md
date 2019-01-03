连接的一个有用的快捷方式是在Series和DataFrame实例的`append`方法。这些方法实际上早于`concat()`方法。
它们沿`axis=0`连接

    
    
    #encoding:utf8
    import pandas as pd
    one = pd.DataFrame({
             "Name": ["Alex", "Amy", "Allen", "Alice", "Ayoung"],
             "subject_id":["sub1","sub2","sub4","sub6","sub5"],
             "Marks_scored":[98,90,87,69,78]},
             index=[1,2,3,4,5])
    two = pd.DataFrame({
             "Name": ["Billy", "Brian", "Bran", "Bryce", "Betty"],
             "subject_id":["sub2","sub4","sub3","sub6","sub5"],
             "Marks_scored":[89,80,79,97,88]},
             index=[1,2,3,4,5])
    print("one:")
    print(one)
    print("two:")
    print(two)
    rs = pd.concat([one,two])
    print("rs = pd.concat([one,two])")
    print(rs)
    print("rs = pd.concat([one,two],keys=["x","y"])")
    rs = pd.concat([one,two],keys=["x","y"])
    print(rs)
    print("结果的索引是重复的; 每个索引重复。如果想要生成的对象必须遵循自己的索引，请将ignore_index设置为True:")
    print("rs = pd.concat([one,two],keys=["x","y"],ignore_index=True)")
    rs = pd.concat([one,two],keys=["x","y"],ignore_index=True)
    print(rs)
    print("观察，索引完全改变，键也被覆盖。如果需要沿axis=1添加两个对象，则会添加新列:")
    rs = pd.concat([one,two],axis=1)
    print(rs)
    print("rs = one.append(two):")
    rs = one.append(two)
    print(rs)
    print("append()函数也可以带多个对象:")
    rs = one.append([two,one,two])
    print(rs)
    
    
    
    
    D:\Download\python3\python3.exe D:/Download/pycharmworkspace/s.py
    one:
       Marks_scored    Name subject_id
    1            98    Alex       sub1
    2            90     Amy       sub2
    3            87   Allen       sub4
    4            69   Alice       sub6
    5            78  Ayoung       sub5
    two:
       Marks_scored   Name subject_id
    1            89  Billy       sub2
    2            80  Brian       sub4
    3            79   Bran       sub3
    4            97  Bryce       sub6
    5            88  Betty       sub5
    rs = pd.concat([one,two])
       Marks_scored    Name subject_id
    1            98    Alex       sub1
    2            90     Amy       sub2
    3            87   Allen       sub4
    4            69   Alice       sub6
    5            78  Ayoung       sub5
    1            89   Billy       sub2
    2            80   Brian       sub4
    3            79    Bran       sub3
    4            97   Bryce       sub6
    5            88   Betty       sub5
    rs = pd.concat([one,two],keys=["x","y"])
         Marks_scored    Name subject_id
    x 1            98    Alex       sub1
      2            90     Amy       sub2
      3            87   Allen       sub4
      4            69   Alice       sub6
      5            78  Ayoung       sub5
    y 1            89   Billy       sub2
      2            80   Brian       sub4
      3            79    Bran       sub3
      4            97   Bryce       sub6
      5            88   Betty       sub5
    结果的索引是重复的; 每个索引重复。如果想要生成的对象必须遵循自己的索引，请将ignore_index设置为True:
    rs = pd.concat([one,two],keys=["x","y"],ignore_index=True)
       Marks_scored    Name subject_id
    0            98    Alex       sub1
    1            90     Amy       sub2
    2            87   Allen       sub4
    3            69   Alice       sub6
    4            78  Ayoung       sub5
    5            89   Billy       sub2
    6            80   Brian       sub4
    7            79    Bran       sub3
    8            97   Bryce       sub6
    9            88   Betty       sub5
    观察，索引完全改变，键也被覆盖。如果需要沿axis=1添加两个对象，则会添加新列:
       Marks_scored    Name subject_id  Marks_scored   Name subject_id
    1            98    Alex       sub1            89  Billy       sub2
    2            90     Amy       sub2            80  Brian       sub4
    3            87   Allen       sub4            79   Bran       sub3
    4            69   Alice       sub6            97  Bryce       sub6
    5            78  Ayoung       sub5            88  Betty       sub5
    rs = one.append(two):
       Marks_scored    Name subject_id
    1            98    Alex       sub1
    2            90     Amy       sub2
    3            87   Allen       sub4
    4            69   Alice       sub6
    5            78  Ayoung       sub5
    1            89   Billy       sub2
    2            80   Brian       sub4
    3            79    Bran       sub3
    4            97   Bryce       sub6
    5            88   Betty       sub5
    append()函数也可以带多个对象:
       Marks_scored    Name subject_id
    1            98    Alex       sub1
    2            90     Amy       sub2
    3            87   Allen       sub4
    4            69   Alice       sub6
    5            78  Ayoung       sub5
    1            89   Billy       sub2
    2            80   Brian       sub4
    3            79    Bran       sub3
    4            97   Bryce       sub6
    5            88   Betty       sub5
    1            98    Alex       sub1
    2            90     Amy       sub2
    3            87   Allen       sub4
    4            69   Alice       sub6
    5            78  Ayoung       sub5
    1            89   Billy       sub2
    2            80   Brian       sub4
    3            79    Bran       sub3
    4            97   Bryce       sub6
    5            88   Betty       sub5
    
    Process finished with exit code 0

