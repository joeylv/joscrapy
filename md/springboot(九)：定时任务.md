在我们的项目开发过程中，经常需要定时任务来帮助我们来做一些内容，springboot默认已经帮我们实行了，只需要添加相应的注解就可以实现

## 1、pom包配置

pom包里面只需要引入springboot starter包即可

    
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
         <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

## 2、启动类启用定时

在启动类上面加上`@EnableScheduling`即可开启定时

    
    
    @SpringBootApplication
    @EnableScheduling
    public class Application {
    
        public static void main(String[] args) {
            SpringApplication.run(Application.class, args);
        }
    }

## 3、创建定时任务实现类

定时任务1：

    
    
    @Component
    public class SchedulerTask {
    
        private int count=0;
    
        @Scheduled(cron="*/6 * * * * ?")
        private void process(){
            System.out.println("this is scheduler task runing  "+(count++));
        }
    
    }

定时任务2：

    
    
    @Component
    public class Scheduler2Task {
    
        private static final SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");
    
        @Scheduled(fixedRate = 6000)
        public void reportCurrentTime() {
            System.out.println("现在时间：" + dateFormat.format(new Date()));
        }
    
    }

结果如下：

    
    
    this is scheduler task runing  0
    现在时间：09:44:17
    this is scheduler task runing  1
    现在时间：09:44:23
    this is scheduler task runing  2
    现在时间：09:44:29
    this is scheduler task runing  3
    现在时间：09:44:35

## 参数说明

`@Scheduled` 参数可以接受两种定时的设置，一种是我们常用的`cron="*/6 * * * * ?"`,一种是 `fixedRate =
6000`，两种都表示每隔六秒打印一下内容。

**fixedRate 说明**

  * `@Scheduled(fixedRate = 6000)` ：上一次开始执行时间点之后6秒再执行
  * `@Scheduled(fixedDelay = 6000)` ：上一次执行完毕时间点之后6秒再执行
  * `@Scheduled(initialDelay=1000, fixedRate=6000)` ：第一次延迟1秒后执行，之后按fixedRate的规则每6秒执行一次

[示例代码地址](https://github.com/ityouknow/spring-boot-starter/tree/master/spring-
boot-scheduler)

* * *

**作者：纯洁的微笑**  
**出处：[http://www.ityouknow.com/](http://www.ityouknow.com/springboot/2016/12/02/springboot\(%E4%B9%9D\)-%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1.html)**  
**版权所有，欢迎保留原文链接进行转载：)**

