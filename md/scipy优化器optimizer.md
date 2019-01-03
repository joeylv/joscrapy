
    #optimazer优化器
    from scipy.optimize import minimize
    def rosem(x):
        return sum(100.0*(x[1:]-x[:-1])**2.0+(1-x[:-1])**2.0)
    x0=np.array([1.3,.7,.8,1.9,1.2])
    res=minimize(rosem,x0,method="nelder-mead",options={"xtol":1e-8,"disp":True})
    #method="nelder-mead"优化器采用的算法；"xtol":1e-8为精度；"disp":True显示中间过程
    print("rose mini:",res)#求函数最小值
    print("rose mini:",res.x)
    #有约束条件的求最小值，目标值
    def func(x):
        return (2*x[0]*x[1]+2*x[0]-x[0]**2-2*x[1]**2)
    def func_derive(x):#求导数
        dfdx0=(-2*x[0]+2*x[1]+2)#x0的导数 x[0]
        dfdx1 = (2 * x[0] -4* x[1])  # x1的导数 x[1]
        return np.array([dfdx0,dfdx1])
    constriate=({"type":"eq","fun":lambda x：},"jac":lambda x:,#等式约束
                        "ineq", "fun": lambda x：}, "jac": lambda x:)#不等式约束
    res=minimize(func,[-1,1],jac=func_derive,constraints=constriate,method="SLSQP",
           options={"xtol":1e-8,"disp":True})#jac为雅可比行列式，constraints约束条件，method算法
    #求根
    from scipy.optimize import root
    def fun(x):
        return x**2
    sol=root(fun,0.1)#求根，赋值0.1
    print (sol.x,sol.fun)#sol.x为根，sol.fun为根的值

