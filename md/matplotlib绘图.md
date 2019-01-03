
        fig = plt.figure()
        ax=plt.gca()
    
        timeList = np.array(timeList)
        timeList=timeList*100
        timeList1 = np.array(timeList1)
        timeList1=timeList1*100
        timeList2 = np.array(timeList2)
        timeList2=timeList2*100
        timeList3 = np.array(timeList3)
        timeList3=timeList3*100
        timeList4 = np.array(timeList4)
        timeList4=timeList4*100
        plt.plot(timeList,"go-",label="ratio-threshold=%d"%(threValue))
        plt.plot(timeList1,"bs-",label="ratio-threshold=%d"%(threValue1))
        plt.plot(timeList2,"r^-",label="ratio-threshold=%d"%(threValue2))
        plt.plot(timeList3,"kp-",label="ratio-threshold=%d"%(threValue3))
        plt.plot(timeList4,"m+-",label="ratio-threshold=%d"%(threValue4))
        plt.yticks([0,2,4,6,8,10,12],["0%", "2%", "4%", "6%", "8%","10%", "12%"])
        for label in ax.get_xticklabels():        
            label.set_rotation(90)
        plt.xlabel("time axis")
        plt.ylabel("ratio")
        plt.title(r"Among 3/25-3/26 period")
        plt.legend()
        plt.show()  
      
    
    
    
    plt.plot(t1,"k--")
        plt.plot(t2,"k--")
        plt.plot(t3,"k--")
        plt.plot(t4,"k--")
        plt.plot(t5,"k--")
        plt.annotate("25%", xy=(60, 10), xytext=(63, 12),arrowprops=dict(facecolor="black", shrink=0.05),)
        plt.annotate("18%", xy=(60, 25), xytext=(63, 27),arrowprops=dict(facecolor="black", shrink=0.1),)
        plt.annotate("13%", xy=(60, 50), xytext=(63, 52),arrowprops=dict(facecolor="black", shrink=0.1),)
        plt.annotate("9%", xy=(60, 75), xytext=(63, 77),arrowprops=dict(facecolor="black", shrink=0.1),)
        plt.annotate("8%", xy=(60, 100), xytext=(63, 102),arrowprops=dict(facecolor="black", shrink=0.1),)   
        plt.annotate("10", xy=(0, 10), xytext=(-2, 12),)
        plt.annotate("25", xy=(0, 25), xytext=(-2, 27),)
        plt.annotate("50", xy=(0, 50), xytext=(-2, 52),)
        plt.annotate("75", xy=(0, 75), xytext=(-2, 77),)
        plt.annotate("100", xy=(0, 100), xytext=(-2, 102),) 

