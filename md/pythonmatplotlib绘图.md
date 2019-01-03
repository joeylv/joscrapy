
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.constants.constants import alpha
    from matplotlib.patches import ArrowStyle
    x=np.linspace(-np.pi,np.pi,256,endpoint=True)
    #np.linspace定义横轴，在-pi到pi之间共256个点，endpoint=True表示包括最后一个点
    c,s=np.sin(x),np.cos(x)
    plt.figure(1)#生成一幅图
    plt.plot(x,c,color="blue",linewidth=1.0,linestyle="-",label="COS",alpha=0.5)#alpha=0.5透明度
    plt.plot(x,s,"r*",label="sin")
    plt.title("sin")#添加标题
    ax=plt.gca()#轴编辑器
    #spines指的是图形中的上下左右四条刻度线
    ax.spines["right"].set_color("none")#将右边刻度线 隐藏set_color为None
    ax.spines["top"].set_color("none")#将上边刻度线 隐藏
    ax.spines["left"].set_position(("data",0))#将左边刻度线 放到 数据域的 刻度0处 显示y轴
    ax.spines["bottom"].set_position(("data",0))#将左边刻度线 放到 数据域的 刻度0处 显示x轴
    ax.xaxis.set_ticks_position("bottom")#横坐标的刻度值 放在横轴的下面
    ax.yaxis.set_ticks_position("left")#纵坐标的刻度值 放在纵轴的左面
    plt.xticks([-np.pi,-np.pi/2,0,np.pi/2,np.pi],["1","2","3","4","5",])#将原来刻度值变为[1,2,3,4,5]的显示形式
    plt.yticks(np.linspace(-1, 1, 5, endpoint=True))#从-1到1，标记5个点，endpoint=True最后一个点显示
    for label in ax.get_xticklabels()+ax.get_yticklabels():
        #ax.get_xticklabels()获取横轴标签 ax.get_yticklabels()获取纵轴标签
        label.set_fontsize(16)#设置标签的字体大小
        label.set_bbox(dict(facecolor="red",edgecolor="None",alpha=0.2))
        #设置标签的方框 facecolor为方框填充颜色  edgecolor为边框颜色  alpha为透明度
        label.set_rotation(90)#标签旋转90度
    plt.legend()#展示plt.plot中label 显示图例
    plt.legend(loc="upper left")#展示plt.plot中label 显示图例 偏上偏左
    plt.grid()#展示网格线
    plt.axis([-1,1,-0.5,1])#展示图形的显示范围
    plt.fill_between(x,np.abs(x)<0.5,c,c>0.5,color="green",alpha=0.25)
    #fill_between填充颜色   给出图形中填充的范围
    t=1#在t=1的地方添加注释
    plt.plot([t,t],[0,np.cos(t)],"y",linewidth=3,linestyle="--")#"y"为黄色
    #
    plt.annotate("cos(1)",xy=(t,np.cos(t)),xycoords="data",xytext=(+10,+30),
                 textcoords="offset points",arrowprops=dict(arrowstyle="->",connectionstyle="arc3,rad=.2"))
    #cos(1)注释显示  xy注释的位置 xycoords定义为data域  xytext增加的偏移量
    #textcoords指定注释为相对位置 相对偏移 arrowstyle箭头的样子 connectionstyle箭头的弧度值
    plt.show()#显示图

