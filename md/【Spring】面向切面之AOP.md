## 前言

> 前面已经讲解了`bean`的装配技术，接着学习`Spring`中另外一个核心概念：`切面`。

## 面向切面

### 面向切面编程

> 切面能够帮助模块化`横切关注点`，`横切关注点`可以被描述为影响应用的功能，如为业务添加安全和事务管理等。

#### AOP(Aspect Orient Programming)

  * 通知，通知定义切面何时被使用，`Spring`切面可以应用`5`种类型的通知。 
    * 前置通知(Before)，在目标方法被调用之前调用通知功能。
    * 后置通知(After)，在目标方法完成之后调用通知，并不关心方法的输出。
    * 返回通知(AfterReturning)，在目标方法成功执行之后调用通知。
    * 异常通知(AfterThrowing)，在目标方法抛出异常后调用通知。
    * 环形通知(Around)，通知包裹了被通知的方法，在被通知的方法调用之前和调用之后执行自定义的行为。
  * 连接点，在应用执行过程中能够插入切面的一个点。
  * 切点，匹配通知所要织入的一个或多个连接点。
  * 切面，通知和切点的结合。
  * 引入，允许向现有类添加新方法或属性。
  * 织入，把切面应用到目标对象并创建新的代理对象的过程，切面可以在指定的连接点被织入到目标对象中，在目标对象的生命周期中有多个点可以进行织入。 
    * 编译期，在目标类编译时被织入，需要特殊的编译器支持。
    * 类加载器，切面在目标类加载到`JVM`时被织入，需要特殊类加载器。
    * 运行期，在应用运行的某个时刻被织入，`AOP`容器会为目标对象动态创建代理对象，这也是`Spring AOP`的织入方式。

#### Spring AOP

> `Spring`对`AOP`的支持在很多方面借鉴了`AspectJ`项目，提供如下四种支持。

  * 基于代理的经典`Spring AOP`。
  * 纯`POJO`切面。
  * `@AspectJ`注解的切面。
  * 注入式`AspectJ`切面(适用于`Spring`各版本)。

`Spring
AOP`构建在动态代理基础上，只能局限于对方法拦截；`Spring`在运行时通知对象(通过在代理类中包裹切面，在运行期把切面织入到`Spring`管理的`bean`中，代理类封装了目标类，并拦截被通知方法的调用，执行切面逻辑，再把调用转发给真正的目标`bean`)；`Spring`只支持方法级别的连接点(基于动态代理决定)。

### 通过切点选择连接点

#### 编写切点

> 首先先定义一个方法

    
    
    package ch4
    
    public interface Performance {
        void perform();
    }
    

> 然后使用切点表达式设置当`perform`方法执行时触发通知的调用 **execution(*
ch4.Performance.perform(..))**
，*表示并不关心返回值，然后指定具体的方法名，方法中的`..`表示切点要选择任意的`perform`方法。还可使用`&&、and、||、or`对切点进行限定。

#### 切点中选择bean

> 切点表达式中可使用`bean`的`ID`来标识`bean`，如下切点表达式 **execution(*
ch4.Performance.perform(..)) &&
bean(musicPerformance)**，表示限定`beanID`为`musicPerformance`时调用通知，其中`musicPerformance`是`Performance`的一个子类实现。

### 使用注解创建切面

#### 定义切面

> 定义一个切面如下。

    
    
    package ch4;
    
    import org.aspectj.lang.ProceedingJoinPoint;
    import org.aspectj.lang.annotation.*;
    import org.springframework.stereotype.Component;
    
    @Aspect
    @Component
    public class Audience {
        @Before("execution(* ch4.Performance.perform(..))")
        public void silenceCellPhones() {
            System.out.println("Silencing cell phones");
        }
    
        @Before("execution(* ch4.Performance.perform(..))")
        public void takeSeats() {
            System.out.println("Taking seats");
        }
    
        @AfterReturning("execution(* ch4.Performance.perform(..))")
        public void applause() {
            System.out.println("CLAP CLAP CLAP CLAP");
        }
    
        @AfterThrowing("execution(* ch4.Performance.perform(..))")
        public void demandRefund() {
            System.out.println("Demanding a refund");
        }
    }
    

>
可以看到配合注解和切点表达式可以使得在执行`perform`方法之前、之后完成指定动作，当然，对于每个方法都使用了`execution`切点表达式，可以进一步进行精简。

    
    
    package ch4;
    
    import org.aspectj.lang.ProceedingJoinPoint;
    import org.aspectj.lang.annotation.*;
    import org.springframework.stereotype.Component;
    
    @Aspect
    @Component
    public class Audience {
        @Pointcut("execution(* ch4.Performance.perform(..))")
        public void performance() {
    
        }
    
        @Before("performance()")
        public void silenceCellPhones() {
            System.out.println("Silencing cell phones");
        }
    
        @Before("performance()")
        public void takeSeats() {
            System.out.println("Taking seats");
        }
    
        @AfterReturning("performance()")
        public void applause() {
            System.out.println("CLAP CLAP CLAP CLAP");
        }
    
        @AfterThrowing("performance()")
        public void demandRefund() {
            System.out.println("Demanding a refund");
        }
    }
    
    

> 可以看到使用`@Pointcut`定义切点，然后在其他方法中直接使用注解和切点方法即可，不需要再繁琐的使用`execution`切点表达式。

#### 启动代理功能

> 在定义了注解后，需要启动，否则无法识别，启动方法分为在`JavaConfig`中显式配置和`XML`注解。

  * JavaConfig显式配置

    
    
    package ch4;
    
    import org.springframework.context.annotation.Bean;
    import org.springframework.context.annotation.ComponentScan;
    import org.springframework.context.annotation.Configuration;
    import org.springframework.context.annotation.EnableAspectJAutoProxy;
    
    
    @Configuration
    @EnableAspectJAutoProxy
    @ComponentScan
    public class ConcertConfig {
    
        @Bean
        public Audience audience() {
            return new Audience();
        }
    }
    
    

  * XML配置

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:aop="http://www.springframework.org/schema/aop"
           xmlns:context="http://www.springframework.org/schema/context"
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                               http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
                               http://www.springframework.org/schema/aop
                               http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
                               http://www.springframework.org/schema/context
                               http://www.springframework.org/schema/context/spring-context-3.1.xsd">
        
        <aop:aspectj-autoproxy/>
        <context:component-scan base-package="ch4"/>
    
    </beans>
    

#### 创建环绕通知

> 将被通知的目标方法完全包装起来，就像在一个通知方法中同时编写前置通知和后置通知。

    
    
    package ch4;
    
    import org.aspectj.lang.ProceedingJoinPoint;
    import org.aspectj.lang.annotation.*;
    import org.springframework.stereotype.Component;
    
    @Aspect
    @Component
    public class Audience {
        @Pointcut("execution(* ch4.Performance.perform(..)) && ! bean(musicPerformance)")
        public void performance() {
    
        }
    
        @Around("performance()")
        public void watchPerformance(ProceedingJoinPoint jp) {
            try {
                System.out.println("Silencing cell phones");
                System.out.println("Taking seats");
                jp.proceed();
                System.out.println("CLAP CLAP CLAP CLAP");
            } catch (Throwable e) {
                System.out.println("Demanding a refund");
            }
        }
    }
    
    

> 使用`Around`注解表示环绕通知，注意需要调用`proceed()`方法来调用实际的通知方法。

#### 处理通知中的参数

> 在`perform`方法中添加`int number`参数表示有多少观众，使用如下切点表达式`execution(\*
ch4.Performance.perform(int)) &&
args(number)`，表示需要匹配`perform(int)`型方法并且通知方法的参数名为`number`。

  * `MusicPerformance`如下

    
    
    package ch4;
    
    import org.springframework.stereotype.Service;
    
    @Service
    public class MusicPerformance implements Performance {
        public void perform(int number) {
            System.out.println("perform music, and the audience number is " + number);
        }
    }
    

  * `Audience`如下

    
    
    package ch4;
    
    import org.aspectj.lang.ProceedingJoinPoint;
    import org.aspectj.lang.annotation.*;
    import org.springframework.stereotype.Component;
    
    @Aspect
    @Component
    public class Audience {
        @Pointcut("execution(* ch4.Performance.perform(int)) && args(number)")
        public void performance(int number) {
    
        }
    
        @Before("performance(int)")
        public void silenceCellPhones() {
            System.out.println("Silencing cell phones");
        }
    
        @Before("performance(int)")
        public void takeSeats() {
            System.out.println("Taking seats");
        }
    
        @AfterReturning("performance(int)")
        public void applause() {
            System.out.println("CLAP CLAP CLAP CLAP");
        }
    
        @AfterThrowing("performance(int)")
        public void demandRefund() {
            System.out.println("Demanding a refund");
        }
    
        @Around("performance(int)")
        public void watchPerformance(ProceedingJoinPoint jp) {
            try {
                System.out.println("Silencing cell phones");
                System.out.println("Taking seats");
                jp.proceed();
                System.out.println("CLAP CLAP CLAP CLAP");
            } catch (Throwable e) {
                System.out.println("Demanding a refund");
            }
        }
    }
    
    

  * 测试`AOPTest`如下

    
    
    package ch4;
    
    import org.junit.Test;
    import org.junit.runner.RunWith;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.test.context.ContextConfiguration;
    import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
    
    import static org.junit.Assert.assertNotNull;
    @RunWith(SpringJUnit4ClassRunner.class)
    @ContextConfiguration(locations = "classpath*:spring-learning.xml")
    public class AOPTest {
        @Autowired
        private Performance performance;
    
        @Test
        public void notNull() {
            assertNotNull(performance);
            performance.perform(100);
    
            System.out.println("++++++++++++++++++");
            performance.perform(999);
            System.out.println("++++++++++++++++++");
        }
    }
    
    

运行结果：

> Silencing cell phones  
>  Taking seats  
>  Taking seats  
>  Silencing cell phones  
>  perform music, and the audience number is 100  
>  CLAP CLAP CLAP CLAP  
>  CLAP CLAP CLAP CLAP  
>  ++++++++++++++++++  
>  Silencing cell phones  
>  Taking seats  
>  Taking seats  
>  Silencing cell phones  
>  perform music, and the audience number is 999  
>  CLAP CLAP CLAP CLAP  
>  CLAP CLAP CLAP CLAP  
>  ++++++++++++++++++

### 在XML中声明切面

> 除了使用注解方式声明切面外，还可通过`XML`方式声明切面。

#### 前置通知和后置通知

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:p="http://www.springframework.org/schema/p"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:aop="http://www.springframework.org/schema/aop"
           xmlns:context="http://www.springframework.org/schema/context"
    
    
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                               http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
                               http://www.springframework.org/schema/aop
                               http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
                               http://www.springframework.org/schema/context
                               http://www.springframework.org/schema/context/spring-context-3.1.xsd">
    
        <aop:aspectj-autoproxy/>
        <context:component-scan base-package="ch4"/>
    
        <aop:config>
            <aop:aspect ref="audience">
                <aop:before
                    pointcut="execution(* ch4.Performance.perform(..))"
                    method="silenceCellPhones" />
    
                <aop:before
                        pointcut="execution(* ch4.Performance.perform(..))"
                        method="takeSeats" />
    
                <aop:after-returning
                        pointcut="execution(* ch4.Performance.perform(..))"
                        method="applause" />
    
                <aop:after-throwing
                        pointcut="execution(* ch4.Performance.perform(..))"
                        method="demandRefund" />
    
            </aop:aspect>
        </aop:config>
    
    </beans>
    
    

> 将`Audience`注解删除后运行单元测试可得出正确结果；当然上述`XML`也有点复杂，可进一步简化。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:p="http://www.springframework.org/schema/p"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:aop="http://www.springframework.org/schema/aop"
           xmlns:context="http://www.springframework.org/schema/context"
    
    
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                               http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
                               http://www.springframework.org/schema/aop
                               http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
                               http://www.springframework.org/schema/context
                               http://www.springframework.org/schema/context/spring-context-3.1.xsd">
    
        <aop:aspectj-autoproxy/>
        <context:component-scan base-package="ch4"/>
    
        <aop:config>
            <aop:aspect ref="audience">
                <aop:pointcut
                        id="performance"
                        expression="execution(* ch4.Performance.perform(..))" />
    
                <aop:before
                        pointcut-ref="performance"
                        method="silenceCellPhones" />
    
                <aop:before
                        pointcut-ref="performance"
                        method="takeSeats" />
    
                <aop:after-returning
                        pointcut-ref="performance"
                        method="applause" />
    
                <aop:after-throwing
                        pointcut-ref="performance"
                        method="demandRefund" />
    
            </aop:aspect>
        </aop:config>
    
    </beans>
    
    

#### 声明环绕通知

XML如下

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:p="http://www.springframework.org/schema/p"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:aop="http://www.springframework.org/schema/aop"
           xmlns:context="http://www.springframework.org/schema/context"
    
    
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                               http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
                               http://www.springframework.org/schema/aop
                               http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
                               http://www.springframework.org/schema/context
                               http://www.springframework.org/schema/context/spring-context-3.1.xsd">
    
        <aop:aspectj-autoproxy/>
        <context:component-scan base-package="ch4"/>
    
        <aop:config>
            <aop:aspect ref="audience">
                <aop:pointcut
                        id="performance"
                        expression="execution(* ch4.Performance.perform(..))"/>
                <aop:around
                    pointcut-ref="performance"
                    method="watchPerformance" />
            </aop:aspect>
        </aop:config>
    
    </beans>
    
    

> 运行单元测试，可得正确结果。

#### 为通知传递参数

XML文件如下

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:p="http://www.springframework.org/schema/p"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:aop="http://www.springframework.org/schema/aop"
           xmlns:context="http://www.springframework.org/schema/context"
    
    
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                               http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
                               http://www.springframework.org/schema/aop
                               http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
                               http://www.springframework.org/schema/context
                               http://www.springframework.org/schema/context/spring-context-3.1.xsd">
    
        <aop:aspectj-autoproxy/>
        <context:component-scan base-package="ch4"/>
    
        <aop:config>
            <aop:aspect ref="audience">
                <aop:pointcut
                        id="performance"
                        expression="execution(* ch4.Performance.perform(int)) and args(int)" />
                <aop:before
                    pointcut-ref="performance"
                    method="silenceCellPhones" />
    
                <aop:before
                        pointcut-ref="performance"
                        method="takeSeats" />
    
                <aop:after-returning
                        pointcut-ref="performance"
                        method="applause" />
    
                <aop:after-throwing
                        pointcut-ref="performance"
                        method="demandRefund" />
            </aop:aspect>
        </aop:config>
    
    </beans>
    
    

> 运行单元测试，可得正确结果。

## 总结

>
`AOP`是`Spring`的核心概念，通过`AOP`，我们可以把切面插入到方法执行的周围，通过本篇博文可以大致了解`AOP`的使用方法。源码已经上传至[github](https://github.com/leesf/springlearning)，欢迎`fork
and star`。

