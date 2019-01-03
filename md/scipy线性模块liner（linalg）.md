
    #liner
    import numpy as np
    from scipy import linalg as lg
    arr=np.array([[1,1],[0,1]])
    matr=np.mat("[1,2;0,2]")
    print ("matrix:",matr)#matrix: [[1 2]，[0 2]]
    print ("Det:",lg.det(arr))#array行列式
    print ("Inv:",lg.inv(arr))#array矩阵的逆
    print ("Inv.T:",matr.I)#mat矩阵的逆
    print ("trans:",arr.T)#array矩阵的转置
    print ("Eig:",lg.eig(arr))#array特征值 特征向量
    print ("LU:",lg.lu(arr))#array LU分解
    print ("QR:",lg.qr(arr))#QR分解
    print ("SVD:",lg.svd(arr))#奇异值分解
    print ("Schur:",lg.schur(arr))#schur分解
    b=np.array([6,14])
    print ("Solver:",lg.solve(arr,b))#解线性方程组

