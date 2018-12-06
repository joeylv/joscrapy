##java提高篇(九)-----实现多重继承

##
## 多重继承指的是一个类可以同时从多于一个的父类那里继承行为和特征，然而我们知道Java为了保证数据安全，它只允许单继承。有些时候我们会认为如果系统中需要使用多重继承往往都是糟糕的设计,这个时候我们往往需要思考的不是怎么使用多重继承,而是您的设计是否存在问题.但有时候我们确实是需要实现多重继承，而且现实生活中也真正地存在这样的情况，比如遗传：我们即继承了父亲的行为和特征也继承了母亲的行为和特征。可幸的是Java是非常和善和理解我们的,它提供了两种方式让我们曲折来实现多重继承：接口和内部类。
##一、 接口

##
## 在介绍接口和抽象类的时候了解到子类只能继承一个父类，也就是说只能存在单一继承，但是却可以实现多个接口，这就为我们实现多重继承做了铺垫。

##
## 对于接口而已，有时候它所表现的不仅仅只是一个更纯粹的抽象类，接口是没有任何具体实现的，也就是说，没有任何与接口相关的存储，因此也就无法阻止多个接口的组合了。	interface CanFight {    void fight();	}interface CanSwim {    void swim();	}interface CanFly {    void fly();	}public class ActionCharacter {    public void fight(){            	}	}public class Hero extends ActionCharacter implements CanFight,CanFly,CanSwim{    public void fly() {    	}    public void swim() {    	}    /**     * 对于fight()方法，继承父类的，所以不需要显示声明     */	}
##二、内部类

##
## 上面使用接口实现多重继承是一种比较可行和普遍的方式，在介绍内部类的时候谈到内部类使的多继承的实现变得更加完美了，同时也明确了如果父类为抽象类或者具体类，那么我就仅能通过内部类来实现多重继承了。如何利用内部类实现多重继承，请看下面实例：儿子是如何利用多重继承来继承父亲和母亲的优良基因。

##
##首先是父亲Father和母亲Mother：	public class Father {    public int strong(){        return 9;    	}	}public class Mother {    public int kind(){        return 8;    	}	}

##
## 重头戏在这里，儿子类Son：	public class Son {        /**     * 内部类继承Father类     */    class Father_1 extends Father{        public int strong(){            return super.strong() + 1;        	}    	}        class Mother_1 extends  Mother{        public int kind(){            return super.kind() - 2;        	}    	}        public int getStrong(){        return new Father_1().strong();    	}        public int getKind(){        return new Mother_1().kind();    	}	}

##
## 测试程序：	public class Test1 {    public static void main(String[] args) {        Son son = new Son();        System.out.println("Son 的Strong：" + son.getStrong());        System.out.println("Son 的kind：" + son.getKind());    	}	}----------------------------------------Output:Son 的Strong：10Son 的kind：6

##
## 儿子继承了父亲，变得比父亲更加强壮，同时也继承了母亲，只不过温柔指数下降了。这里定义了两个内部类，他们分别继承父亲Father类、母亲类Mother类，且都可以非常自然地获取各自父类的行为，这是内部类一个重要的特性：内部类可以继承一个与外部类无关的类，保证了内部类的独立性，正是基于这一点，多重继承才会成为可能。

##
## 有关于更多接口和内部类的详情，请参考这里:

##
## 内部类： java提高篇----详解内部类

##
## 接口： java提高篇-----抽象类与接口