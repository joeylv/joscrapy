**一、前言**

前面学习了Scala中包和导入的相关知识点，接着学习Traits（特质）

**二、Traits**

Scala的特质与Java的接口基本相同，当遇到可以使用Java接口的情形，就可以考虑使用特质，Scala的类可以使用extends和with关键字继承多个特质，如类或对象继承多个特质

    
    
     class Woodpecker extends Bird with TreeScaling with Pecking

特质除了可以拥有Java中接口的抽象方法，同时还可以拥有已经实现的方法，可以将多余一个的特质混入类，并且特质可以控制哪些类可以混入该特质

2.1 将特质作为接口

1\. 问题描述

像其他语言如Java创建接口一样，你想在Scala也创建类似东西

2\. 解决方案

可以将特质类比为Java的接口，在特质中声明需要子类实现的方法

    
    
    trait BaseSoundPlayer {
        def play
        def close
        def pause
        def stop
        def resume
    }

如果方法不带参数，则只需要写方法名即可，但若带参数，需要如下定义

    
    
    trait Dog {
        def speak(whatToSay: String)
        def wagTail(enabled: Boolean)
    }

当一个类继承特质时，需要使用extends和with关键字，当继承一个特质时，使用extends关键字

    
    
    class Mp3SoundPlayer extends BaseSoundPlayer { ...}

继承多个特质时，使用extends和with关键字

    
    
    class Foo extends BaseClass with Trait1 with Trait2 { ...}

除非实现特质的类是抽象的，否则其需要实现特质中所有方法

    
    
    class Mp3SoundPlayer extends BaseSoundPlayer {
        def play { // code here ... }
        def close { // code here ... }
        def pause { // code here ... }
        def stop { // code here ... }
        def resume { // code here ... }
    }

如果没有实现所有抽象方法，则该类需要被申明为抽象的

    
    
    abstract class SimpleSoundPlayer extends BaseSoundPlayer {
        def play { ... }
        def close { ... }
    }

特质也可以集成其他特质

    
    
    trait Mp3BaseSoundFilePlayer extends BaseSoundFilePlayer {
        def getBasicPlayer: BasicPlayer
        def getBasicController: BasicController
        def setGain(volume: Double)
    }

3\. 讨论

特质可被作为Java的接口使用，并且在特质中申明需要被子类实现的方法，当继承特质时使用extends或者with关键字，当继承一个特质时，使用extends，若继承多个特质，则第一个使用extends，其他的使用with；若类继承类（抽象类）和特质，则抽象类使用extends，特质使用with，特质中可以有已经实现了的方法，如WaggingTail

    
    
    abstract class Animal {
        def speak
    }
    
    trait WaggingTail {
        def startTail { println("tail started") }
        def stopTail { println("tail stopped") }
    }
    
    trait FourLeggedAnimal {
        def walk
        def run
    }
    
    class Dog extends Animal with WaggingTail with FourLeggedAnimal {
        // implementation code here ...
        def speak { println("Dog says "woof"") }
        def walk { println("Dog is walking") }
        def run { println("Dog is running") }
    }

2.2 在特质中使用抽象和具体的字段

1\. 问题描述

你想要在特质中定义抽象和具体的字段，以便继承特质的类可以使用字段

2\. 解决方案

使用初始值赋值的字段是具体的，没有赋值的字段是抽象的

    
    
    trait PizzaTrait {
        var numToppings: Int // abstract
        var size = 14 // concrete
        val maxNumToppings = 10 // concrete
    }

继承特质的类，需要初始化抽象字段，或者让该类为抽象类

    
    
    class Pizza extends PizzaTrait {
        var numToppings = 0 // "override" not needed
        size = 16 // "var" and "override" not needed
    }

3\. 讨论

特质中的字段可以被声明为val或var，你不需要使用override字段来覆盖var字段，但是需要使用override来覆盖val字段

    
    
    trait PizzaTrait {
        val maxNumToppings: Int
    }
    
    class Pizza extends PizzaTrait {
        override val maxNumToppings = 10 // "override" is required
    }

2.3 像抽象类一样使用特质

1\. 问题描述

你想要像Java中的抽象类一样使用特质

2\. 解决方案

在特质中定义方法，继承特质的类中，可以覆盖该方法，或者是直接使用

    
    
    trait Pet {
        def speak { println("Yo") } // concrete implementation
        def comeToMaster // abstract method
    }
    
    class Dog extends Pet {
        // don"t need to implement "speak" if you don"t need to
        def comeToMaster { ("I"m coming!") }
    }
    
    class Cat extends Pet {
        // override the speak method
        override def speak { ("meow") }
        def comeToMaster { ("That"s not gonna happen.") }
    }

如果一个类没有实现特质的抽象方法，那么它也需要被声明为抽象的

    
    
    abstract class FlyingPet extends Pet {
        def fly { ("I"m flying!") }
    }

3\. 讨论

一个类仅仅只能继承一个抽象类，但是可以继承多个特质，使用特质更为灵活

2.4 把特质作为简单的混合物

1\. 问题描述

你想要将多个特质混合进一个类中

2\. 解决方案

为实现简单的混合，在特质中定义方法，然后使用extends和with继承特质，如定义Tail特质

    
    
    trait Tail {
        def wagTail { println("tail is wagging") }
        def stopTail { println("tail is stopped") }
    }

可以使用该特质和抽象的Pet类来创建Dog类

    
    
    abstract class Pet (var name: String) {
        def speak // abstract
        def ownerIsHome { println("excited") }
        def jumpForJoy { println("jumping for joy") }
    }
    
    class Dog (name: String) extends Pet (name) with Tail {
        def speak { println("woof") }
        override def ownerIsHome {
            wagTail
            speak
        }
    }

Dog类通知拥有特质Tail和抽象类Pet的行为

2.5 通过继承控制哪个类可以使用特质

1\. 问题描述

你想限制的特性，只能将其添加至一个父类或者另一个特质的类

2\. 解决方案

使用下面语法声明名为TraitName的特质，而TraitName只能被混入继承了SuperThing的类，SuperThing可以是一个特质、抽象类、类。

    
    
    trait [TraitName] extends [SuperThing]

例如，Starship和StarfleetWarpCore都继承了StarfleetComponent，所以StarfleetWarpCore特质可以被混入Starship中

    
    
    class StarfleetComponent
    trait StarfleetWarpCore extends StarfleetComponent
    class Starship extends StarfleetComponent with StarfleetWarpCore

然而，Warbird不能继承StarfleetWarpCore特质，因为其不继承StarfleetComponent类

    
    
    class StarfleetComponent
    trait StarfleetWarpCore extends StarfleetComponent
    class RomulanStuff
    
    // won"t compile
    class Warbird extends RomulanStuff with StarfleetWarpCore 

3\. 讨论

一个特质继承一个类不是一种普遍情况，但是当其发生时，需要保证拥有相同的父类

2.6 标记特质以使得其仅仅能被某种类型子类使用

1\. 问题描述

你想要标记您的特性，因此只能用于扩展给定基类型的类型

2\. 解决方案

保证MyTrait的特质仅仅只能被混入BaseType的子类，可以使用this: BaseType =>声明开始特质

    
    
    trait MyTrait {
        this: BaseType =>

例如，为了是StarfleetWarpCore特质只能用于Starship，可以标记StarfleetWarpCore特质如下  

    
    
    trait StarfleetWarpCore {
        this: Starship =>
        // more code here ...
    }

给定上面的定义，下面代码将会运行良好

    
    
    class Starship
    class Enterprise extends Starship with StarfleetWarpCore

而如下代码则编译错误

    
    
    class RomulanShip
    // this won"t compile
    class Warbird extends RomulanShip with StarfleetWarpCore

3\. 讨论

任何混入特质的具体类型需要保证其能够转化为特质的自我类型，特质也可要求继承其的子类必须继承多种类型

    
    
    trait WarpCore {
        this: Starship with WarpCoreEjector with FireExtinguisher =>
    }

如下代码中的Enterprise将会通过编译，因为其签名满足特质的定义

    
    
    class Starship
    trait WarpCoreEjector
    trait FireExtinguisher
    // this works
    class Enterprise extends Starship
    with WarpCore
    with WarpCoreEjector
    with FireExtinguisher

若Enterprise不继承特质，则无法满足签名，会报错

2.7 保证特质只能被混入含有某特定方法的类

1\. 问题描述

你想要将特质混入包含了某种方法签名的类

2\. 解决方案

WarpCore特质要求其所混入的类必须包含ejectWrapCore方法

    
    
    trait WarpCore {
        this: { def ejectWarpCore(password: String): Boolean } =>
    }

Enterprise类满足要求，编译成功

    
    
    class Starship {
        // code here ...
    }
    
    class Enterprise extends Starship with WarpCore {
        def ejectWarpCore(password: String): Boolean = {
            if (password == "password") {
                println("ejecting core")
                true
            } else {
                false
            }
        }
    }

特质可以要求混入的类包含多个方法

    
    
    trait WarpCore {
        this: {
            def ejectWarpCore(password: String): Boolean
            def startWarpCore: Unit
        } =>
    }
    
    class Starship
        
    class Enterprise extends Starship with WarpCore {
        def ejectWarpCore(password: String): Boolean = {
            if (password == "password") { println("core ejected"); true } else false
        }
        
        def startWarpCore { println("core started") }
    }

3\. 讨论

该方法也被称为结构类型，因为你规定了某些类必须具有的结构

2.8 将特质添加至对象实例

1\. 问题描述

当对象实例创建时，你想要混入特质

2\. 解决方案

可以使用如下方法

    
    
    class DavidBanner
    
    trait Angry {
        println("You won"t like me ...")
    }
    
    object Test extends App {
        val hulk = new DavidBanner with Angry
    }

当运行代码时，会出现You won"t like me ...结果，因为Angry特质会被实例化

3\. 讨论

混入debugging和logging可能是更为常用的用法

    
    
    trait Debugger {
        def log(message: String) {
            // do something with message
        }
    }
    
    // no debugger
    val child = new Child
    
    // debugger added as the object is created
    val problemChild = new ProblemChild with Debugger

2.9 像特质一样继承Java接口

1\. 问题描述

你想要在Scala应用中实现Java接口

2\. 解决方案

可以使用extends和with关键字继承接口，如同继承特质一样，给定如下Java代码

    
    
    // java
    public interface Animal {
        public void speak();
    }
    
    public interface Wagging {
        public void wag();
    }
    
    public interface Running {
        public void run();
    }

你可以以Scala方式创建Dog类

    
    
    // scala
    class Dog extends Animal with Wagging with Running {
        def speak { println("Woof") }
        def wag { println("Tail is wagging!") }
        def run { println("I"m running!") }
    }

区别在于Java接口不能实现方法，所以当继承接口时，要么实现所有方法，要么声明为抽象的

**三、总结**

本篇博文讲解了Scala中的特质相关点，其可以类比于Java的接口，但是比接口更为灵活，如可添加字段和已经实现方法（在Java
8后的接口也可以添加已实现的方法），谢谢各位园友的观看~

