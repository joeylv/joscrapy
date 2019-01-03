
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2018/5/24 15:03
    # @Author  : zhang chao
    # @File    : s.py
    
    #integral积分
    import numpy as np
    from scipy.integrate import quad,dblquad,nquad
    print(quad(lambda x:np.exp(-x),0,np.inf))#lambda x:np.exp(-x)定义函数，它的积分；定义区间为0-inf
    #结果为(1.0000000000000002, 5.842606703608969e-11)
    #1.0000000000000002为积分的值；5.842606703608969e-11为误差的范围
    print(dblquad(lambda t,x:np.exp(-x*t)/t**3,0,np.inf,lambda x:1,lambda x:np.inf))
    #dblquad为二元积分，lambda t,x:np.exp(-x*t)/t**3为积分函数；0,np.inf为t的取值范围；
    #lambda x:1,lambda x:np.inf其实为x的取值范围，定义为t的函数
    #结果为(0.33333333325010883, 1.3888461883425516e-08)
    #nquad为多维积分，多元积分
    def f(x,y):
        return x*y
    def bound_y():
        return [0,0.5]
    def bound_x(y):
        return [0,1-2*y]
    print(nquad(f,[bound_x,bound_y]))#(0.010416666666666668, 4.101620128472366e-16)

