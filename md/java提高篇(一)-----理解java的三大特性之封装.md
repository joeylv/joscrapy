##java提高篇(一)-----理解java的三大特性之封装

##
## 从大二接触java开始，到现在也差不多三个年头了。从最基础的HTML、CSS到最后的SSH自己都是一步一个脚印走出来的，其中开心过、失落过、寂寞过。虽然是半道出家但是经过自己的努力也算是完成了“学业”。期间参加过培训机构，但是极其不喜欢那种培训方式，于是毅然的放弃了选择自学(可怜我出了6000块钱啊)，虽然自学途中苦很多，但是乐更多，当中的付出和收获只有自己知道。黄天不负有心人，鄙人愚钝，在大四第一学期终于自学完成java(其中走了弯路，荒废半年)，并且凭借它得到了一份不错的工作，不胜感激！

##
## 闲话过多！进入正题，LZ最近刚刚看完设计模式，感触良多。而且在工作过程中深感java基础不够扎实，例如IO不熟、垃圾回收不知所云、多态七窍通五窍、反射不知、甚至连最基本的三大特性都搞得我迷糊了！所以我发狠心一定要好好弥补java基础！从第一课开始---封装!!!!!!
##三大特性之---封装

##
## 封装从字面上来理解就是包装的意思，专业点就是信息隐藏，是指利用抽象数据类型将数据和基于数据的操作封装在一起，使其构成一个不可分割的独立实体，数据被保护在抽象数据类型的内部，尽可能地隐藏内部的细节，只保留一些对外接口使之与外部发生联系。系统的其他对象只能通过包裹在数据外面的已经授权的操作来与这个封装的对象进行交流和交互。也就是说用户是无需知道对象内部的细节（当然也无从知道），但可以通过该对象对外的提供的接口来访问该对象。

##
## 对于封装而言，一个对象它所封装的是自己的属性和方法，所以它是不需要依赖其他对象就可以完成自己的操作。

##
## 使用封装有三大好处：

##
## 1、良好的封装能够减少耦合。

##
## 2、类内部的结构可以自由修改。

##
## 3、可以对成员进行更精确的控制。

##
## 4、隐藏信息，实现细节。

##
## 首先我们先来看两个类：Husband.java、Wife.java	public class Husband {        /*     * 对属性的封装     * 一个人的姓名、性别、年龄、妻子都是这个人的私有属性     */    private String name ;    private String sex ;    private int age ;    private Wife wife;        /*     * setter()、getter()是该对象对外开发的接口     */    public String getName() {        return name;    	}    public void setName(String name) {        this.name = name;    	}    public String getSex() {        return sex;    	}    public void setSex(String sex) {        this.sex = sex;    	}    public int getAge() {        return age;    	}    public void setAge(int age) {        this.age = age;    	}    public void setWife(Wife wife) {        this.wife = wife;    	}	}	public class Wife {    private String name;    private int age;    private String sex;    private Husband husband;    public String getName() {        return name;    	}    public void setName(String name) {        this.name = name;    	}    public String getSex() {        return sex;    	}    public void setSex(String sex) {        this.sex = sex;    	}    public void setAge(int age) {        this.age = age;    	}    public void setHusband(Husband husband) {        this.husband = husband;    	}    public Husband getHusband() {        return husband;    	}    	}

##
## 从上面两个实例我们可以看出Husband里面wife引用是没有getter()的，同时wife的age也是没有getter()方法的。至于理由我想各位都懂的，男人嘛深屋藏娇妻嘛，没有那个女人愿意别人知道她的年龄。

##
## 所以封装把一个对象的属性私有化，同时提供一些可以被外界访问的属性的方法，如果不想被外界方法，我们大可不必提供方法给外界访问。但是如果一个类没有提供给外界访问的方法，那么这个类也没有什么意义了。比如我们将一个房子看做是一个对象，里面的漂亮的装饰，如沙发、电视剧、空调、茶桌等等都是该房子的私有属性，但是如果我们没有那些墙遮挡，是不是别人就会一览无余呢？没有一点儿隐私！就是存在那个遮挡的墙，我们既能够有自己的隐私而且我们可以随意的更改里面的摆设而不会影响到其他的。但是如果没有门窗，一个包裹的严严实实的黑盒子，又有什么存在的意义呢？所以通过门窗别人也能够看到里面的风景。所以说门窗就是房子对象留给外界访问的接口。

##
## 通过这个我们还不能真正体会封装的好处。现在我们从程序的角度来分析封装带来的好处。如果我们不使用封装，那么该对象就没有setter()和getter()，那么Husband类应该这样写：	public class Husband {    public String name ;    public String sex ;    public int age ;    public Wife wife;	}

##
##  我们应该这样来使用它：	Husband husband = new Husband();        husband.age = 30;        husband.name = "张三";        husband.sex = "男";    //貌似有点儿多余

##
## 但是那天如果我们需要修改Husband，例如将age修改为String类型的呢？你只有一处使用了这个类还好，如果你有几十个甚至上百个这样地方，你是不是要改到崩溃。如果使用了封装，我们完全可以不需要做任何修改，只需要稍微改变下Husband类的setAge()方法即可。	public class Husband {        /*     * 对属性的封装     * 一个人的姓名、性别、年龄、妻子都是这个人的私有属性     */    private String name ;    private String sex ;    private String age ;    /* 改成 String类型的*/    private Wife wife;        public String getAge() {        return age;    	}        public void setAge(int age) {        //转换即可        this.age = String.valueOf(age);    	}        /** 省略其他属性的setter、getter **/    	}

##
## 其他的地方依然那样引用(husband.setAge(22))保持不变。

##
## 到了这里我们确实可以看出，封装确实可以使我们容易地修改类的内部实现，而无需修改使用了该类的客户代码。

##
## 我们在看这个好处：可以对成员变量进行更精确的控制。

##
## 还是那个Husband，一般来说我们在引用这个对象的时候是不容易出错的，但是有时你迷糊了，写成了这样：	Husband husband = new Husband();        husband.age = 300;

##
## 也许你是因为粗心写成了，你发现了还好，如果没有发现那就麻烦大了，逼近谁见过300岁的老妖怪啊！

##
## 但是使用封装我们就可以避免这个问题，我们对age的访问入口做一些控制(setter)如：	public class Husband {        /*     * 对属性的封装     * 一个人的姓名、性别、年龄、妻子都是这个人的私有属性     */    private String name ;    private String sex ;    private int age ;    /* 改成 String类型的*/    private Wife wife;    public int getAge() {        return age;    	}    public void setAge(int age) {        if(age > 120){            System.out.println("ERROR：error age input....");    //提示錯誤信息        	}else{            this.age = age;        	}            	}        /** 省略其他属性的setter、getter **/    	}

##
## 上面都是对setter方法的控制，其实通过使用封装我们也能够对对象的出口做出很好的控制。例如性别我们在数据库中一般都是已1、0方式来存储的，但是在前台我们又不能展示1、0，这里我们只需要在getter()方法里面做一些转换即可。	public String getSexName() {        if("0".equals(sex)){            sexName = "女";        	}        else if("1".equals(sex)){            sexName = "男";        	}        else{            sexName = "人妖???";        	}        return sexName;    	}

##
## 在使用的时候我们只需要使用sexName即可实现正确的性别显示。同理也可以用于针对不同的状态做出不同的操作。	public String getCzHTML(){        if("1".equals(zt)){            czHTML = "<a href="javascript:void(0)" onclick="qy("+id+")">启用</a>";        	}        else{            czHTML = "<a href="javascript:void(0)" onclick="jy("+id+")">禁用</a>";        	}        return czHTML;    	}

##
## 鄙人才疏学浅，只能领悟这么多了，如果文中有错误之处，望指正，鄙人不胜感激！
##吐槽

##
## 宅了三天今天就出去走走，在公交车上遇到一极品美女！我坐着，一美女上车，站在我旁边，开始还好，过了一会儿她就对我笑，笑笑还好，但是你也不能总对着人家笑吧！笑的我都不好意了(鄙人脸皮薄，容易害羞??)。难道是我没有洗脸？照照镜子蛮干净的啊！难道是我衣服又或者裤子没**，看来衣服裤子蛮好的！难道是我帅，对我有意思？(程序员屌丝一枚，貌似没可能)！实在受不了了，哥想惹不起我还躲不起么？哥下车！我一下车，那枚美女就飞速的占我座位！哥当时就憋出一个字：靠！！！！！！！！