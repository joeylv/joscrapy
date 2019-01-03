
    nums=[12,23,2,3,2,3,4,23]  
    sumCount = nums.aggregate(  
    (0, 0),  
    (lambda acc, value: (acc[0] + value, acc[1] + 1),(lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])))  
    )
    return sumCount[0] / float(sumCount[1])

。与fold() 类似，使用aggregate() 时，需要提供我们期待返回的类型的初始值。然后  
通过一个函数把RDD 中的元素合并起来放入累加器。lambda acc, value: (acc[0] + value, acc[1] + 1)

考虑到每个节点是在本地进行累加 _的，最终，还需要提供 第二个函数来将累加器两两合并_

    
    
    (lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])))

lambda acc, value: (acc[0] + value, acc[1] + 1)中，acc为初始值（0，0），value为nums中的元素值。

