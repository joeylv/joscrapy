  * 1 orchestration简介
    * 1.1 1.架构图
    * 1.2 2\. 注册中心数据结构
      * 1.2.1 config节点
      * 1.2.2 state节点
    * 1.3 3.总结
    * 1.4 4.问题
    * 1.5 附:zookeeper监听机制
  * 2 orchestration使用
    * 2.1 1.POM配置
    * 2.2 2.配置数据源
    * 2.3 3.集成sharding数据源
    * 2.4 4.Main测试

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/c33191385767>

* * *

# orchestration简介

sharding-
jdbc2.x核心功能之一就是orchestration，即编排治理，什么意思呢？官方文档介绍–2.0.0.M1版本开始，sharding-
jdbc提供了数据库治理功能，主要包括：

  * 配置集中化与动态化。可支持数据源、表与分片及读写分离策略的 **动态切换** ；
  * 数据治理。提供熔断数据库访问程序对数据库的访问和禁用从库的访问的能力；
  * 支持Zookeeper和etcd的注册中心；

> 摘自[sharding-
jdbc编排治理](http://shardingjdbc.io/document/legacy/2.x/cn/02-guide/orchestration/)，官方文档也有比较详细的使用文档；

## 1.架构图

![201808091001](http://cmsblogs.qiniudn.com/201808091001.png)

由sharding-jdbc2.x新的架构图可知，sharding-jdbc2.x与sharding-
jdbc1.x版本最大的变化就是最左边的sharding-jdbc-
orchestration。即为了动态修改配置引入的注册中心和编排模块。而sharding-jdbc内部实现架构几乎没有任何改变。

## 2\. 注册中心数据结构

注册中心在定义的命名空间下，创建数据库访问对象运行节点，用于区分不同数据库访问实例。命名空间中包含2个数据子节点，分别是config和state。

### config节点

config节点信息如下：

    
    
    config
        ├──datasource                                数据源（可能多个，数据结构为json数组）配置
        ├──sharding                                  分库分表（包括分库分表+读写分离）配置根节点
        ├      ├──rule                               分库分表（包括分库分表+读写分离）规则
        ├      ├──configmap                          分库分表ConfigMap配置，以K/V形式存储，如：{"k1":"v1"}
        ├      ├──props                              Properties配置
        ├──masterslave                               读写分离独立使用配置
        ├      ├──rule                               读写分离规则
        ├      ├──configmap                          读写分离ConfigMap配置，以K/V形式存储，如：{"k1":"v1"}
    

> 首先大概了解持久化在注册中心的数据结构图，更容易理解后面的源码分析。各节点详细信息可参考官方文档；

### state节点

state节点包括instances和datasource节点。  
instances节点信息如下：

    
    
    instances
        ├──your_instance_ip_a@-@your_instance_pid_x
        ├──your_instance_ip_b@-@your_instance_pid_y
        ├──....
    

## 3.总结

如果熟悉dubbo的注册发现机制，就很容易理解sharding-
jdbc的编排治理。服务治理原理都是大同小异：将配置信息持久化并注册监听，如果配置信息改变，通过监听机制可动态改变适应新配置。从而达到不需要重启服务的目的；sharding-
jdbc的编排治理核心步骤如下所示：

  1. sharding-jdbc启动时，将相关配置信息以JSON格式存储，包括数据源，分库分表，读写分离、ConfigMap及Properties配置等信息持久化到zookeeper（或者etcd）节点上；
  2. 注册zookeeper（或者etcd）的监听。
  3. 当节点信息发生变化，sharding-jdbc将刷新配置信息；

> 下一篇文章基于源码分析这三步骤sharding-jdbc的编排治理是如何实现的；

## 4.问题

遗憾的是，sharding-
jdbc2.x没有提供可视化操作途径。以zookeeper配置中心为例，用户需要自己登陆zkClient，并通过set命令修改某节点对应的值；例如在zkClient中执行如下命令开启输出sql日志：

    
    
    set /orchestration-yaml-test/demo_ds_ms/config/sharding/props {"sql.show":false}
    

## 附:zookeeper监听机制

ZooKeeper supports the concept of watches. **Clients can set a watch on a
znodes**. **A watch will be triggered and removed when the znode changes**.
When a watch is triggered the client receives a packet saying that the znode
has changed.

> 摘自[Conditional updates and
watches](http://zookeeper.apache.org/doc/current/zookeeperOver.html#Conditional+updates+and+watches)

#  orchestration使用

接下来讲解如何在ssm（spring、springmvc、mybatis）结构的程序上集成sharding-jdbc（版本为 **2.0.3**
）进行分库分表，并集成sharding-jdbc2.x最新特性orchestration；  
假设分库分表行为如下：

  * 将auth_user表分到4个库（user_0~user_3）中；
  * 其他表不进行分库分表，保留在default_db库中；
  * 集成orchestration特性，即编排治理，可动态维护配置信息；

## 1.POM配置

以spring配置文件为例，新增如下POM配置：

    
    
    <dependency>
        <groupId>io.shardingjdbc</groupId>
        <artifactId>sharding-jdbc-core</artifactId>
        <version>2.0.3</version>
    </dependency>
    
    <!--orchestration特性需要引入下面这个maven坐标-->
    <dependency>
        <groupId>io.shardingjdbc</groupId>
        <artifactId>sharding-jdbc-orchestration</artifactId>
        <version>${io-shardingjdbc.version}</version>
    </dependency>
    
    <!--如果通过spring配置集成orchestration特性, 需要增加如下maven坐标-->
    <dependency>
        <groupId>io.shardingjdbc</groupId>
        <artifactId>sharding-jdbc-orchestration-spring-namespace</artifactId>
        <version>${io-shardingjdbc.version}</version>
    </dependency>
    

  * 说明

由于引入了maven坐标：sharding-jdbc-orchestration-spring-
namespace，所以一定不要同时引入maven坐标：sharding-jdbc-core-spring-
namespace。因为前者对应的sharding的namespace为：
**<http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding>** ，且通过
**sharding-jdbc-orchestration-spring-namespace** 模块中 **spring.handlers**
的定义得到该namespace的NamespaceHandler的处理类为：`http\://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding=io.shardingjdbc.orchestration.spring.namespace.handler.OrchestrationShardingNamespaceHandler`。而后者对应的sharding的namespace为：
**<http://shardingjdbc.io/schema/shardingjdbc/sharding>** ，且通过 **sharding-
jdbc-core-spring-namespace** 模块中 **spring.handlers**
的定义得到该namespace的NamespaceHandler的处理类为：`http\://shardingjdbc.io/schema/shardingjdbc/sharding=io.shardingjdbc.spring.namespace.handler.ShardingNamespaceHandler`；如果同时配置两个maven坐标：sharding-
jdbc-core-spring-namespace和sharding-jdbc-orchestration-spring-
namespace，可能会导致加载出错抛出下面的异常信息：

    
    
    英文环境错误信息：
    [spring.xml] is invalid; nested exception is org.xml.sax.SAXParseException; systemId: http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding/sharding.xsd; lineNumber: 7; columnNumber: 48; TargetNamespace.1: Expecting namespace "http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding", but the target namespace of the schema document is "http://shardingjdbc.io/schema/shardingjdbc/sharding".
    
    中文环境错误信息：
    [spring.xml] is invalid; nested exception is org.xml.sax.SAXParseException; systemId: http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding/sharding.xsd; lineNumber: 7; columnNumber: 48; TargetNamespace.1: 应为名称空间 "http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding", 但方案文档的目标名称空间为 "http://shardingjdbc.io/schema/shardingjdbc/sharding"。
    

## 2.配置数据源

spring-datasource.xml和[20\. sharding-
jdbc2.0.3集成–基于ssm](https://www.jianshu.com/p/7b6997c3586d)中” **配置数据源** “保持一致；

## 3.集成sharding数据源

spring-sharding.xml配置如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:sharding="http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding"
           xmlns="http://www.springframework.org/schema/beans"
           xmlns:reg="http://shardingjdbc.io/schema/shardingjdbc/orchestration/reg"
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                            http://www.springframework.org/schema/beans/spring-beans.xsd
                            http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding
                            http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding/sharding.xsd
                            http://shardingjdbc.io/schema/shardingjdbc/orchestration/reg
                            http://shardingjdbc.io/schema/shardingjdbc/orchestration/reg/reg.xsd
                            ">
    
        <!--使用orchestration特性需要增加的注册中心配置-->
        <reg:zookeeper id="regCenter" server-lists="localhost:2181"
                       namespace="orchestration-spring-namespace-test"
                       base-sleep-time-milliseconds="1000"
                       max-sleep-time-milliseconds="3000"
                       max-retries="3" />
    
        <!--数据库sharding策略-->
        <sharding:standard-strategy id="databaseStrategy" sharding-column="id"
                                    precise-algorithm-class="com.crt.fin.ospsso.service.shardingjdbc.AuthUserDatabaseShardingAlgorithm" />
        <!--auth_user表sharding策略:无 -->
    
        <sharding:none-strategy id="noneStrategy" />
    
        <sharding:data-source id="shardingDataSource" overwrite="true" registry-center-ref="regCenter" >
            <!--default-data-source指定默认数据源, 即没有在<rdb:table-rules>申明的logic-table表,
            即不需要分库分表的表, 全部走默认数据源-->
            <sharding:sharding-rule data-source-names="sj_ds_0,sj_ds_1,sj_ds_2,sj_ds_3,sj_ds_default"
                                    default-data-source-name="sj_ds_default"
                                    default-database-strategy-ref="noneStrategy"
                                    default-table-strategy-ref="noneStrategy">
                <sharding:table-rules>
                    <!--auth_user只分库不分表, actual-tables的值一定要加上:sj_ds_${0..3}.,
                    否则会遍历data-sources, 而sj_ds_default中并没有auth_user表 -->
                    <sharding:table-rule logic-table="auth_user" actual-data-nodes="sj_ds_${0..3}.auth_user"
    
                                    database-strategy-ref="databaseStrategy"/>
                </sharding:table-rules>
            </sharding:sharding-rule>
            <sharding:props>
                <prop key="sql.show">false</prop>
                <prop key="executor.size">2</prop>
            </sharding:props>
        </sharding:data-source>
    
        <!-- 配置sqlSessionFactory -->
        <bean id="sqlSessionFactory" class="org.mybatis.spring.SqlSessionFactoryBean">
            <!---datasource交给sharding-jdbc托管-->
            <property name="dataSource" ref="shardingDataSource"/>
            <property name="mapperLocations" value="classpath*:mybatis/*Mapper.xml"/>
        </bean>
    
        <bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
            <property name="basePackage" value="com.crt.fin.ospsso.dal.mapper"/>
            <property name="sqlSessionFactoryBeanName" value="sqlSessionFactory"/>
        </bean>
    
    </beans>
    

说明：这些的代码和[20\. sharding-
jdbc2.0.3集成–基于ssm](https://www.jianshu.com/p/7b6997c3586d)非常类似，但是有几处重要的不同点：

  1. **namespace** 的变更（对应的sharding的命名空间由： **<http://shardingjdbc.io/schema/shardingjdbc/sharding>** ，变更为： **<http://shardingjdbc.io/schema/shardingjdbc/orchestration/sharding>** ）；
  2. `中新增`registry-center-ref="regCenter"`，并新增`即配置中心节点配置；

## 4.Main测试

Main.java用来测试分库分表是否OK，其源码如下：

    
    
    /**
     * @author wangzhenfei9
     * @version 1.0.0
     * @since 2018年05月14日
     */
    public class Main {
    
        public static void main(String[] args) {
            ApplicationContext context = new ClassPathXmlApplicationContext(
                    "/META-INF/spring/spring-*.xml");
    
            // auth_user有进行分库，
            AuthUserMapper authUserMapper = context.getBean(AuthUserMapper.class);
            AuthUser authUser = authUserMapper.selectByPrimaryKey(7L);
            System.out.println("-----> The auth user: "+JSON.toJSONString(authUser));
    
            System.out.println("sleeping...."+new Date());
            // 留点时间以便通过zkClient执行set命令
            Thread.sleep(15000);
    
            AuthUserMapper authUserMapper2 = context.getBean(AuthUserMapper.class);
            AuthUser authUser2 = authUserMapper2.selectByPrimaryKey(7L);
            System.out.println("-----> The auth user: "+JSON.toJSONString(authUser2));
        }
    
    }
    

说明：  
在执行第二条SQL之前，sleep一段时间，为了留出时间通过zkClient执行set命令动态更新配置信息，执行的set命令如下：

    
    
    set /orchestration-spring-namespace-test/shardingDataSource/config/sharding/props {"executor.size":"2","sql.show":"true"}
    

  * 验证日志  
由于xml文件中初始配置`false`，所以执行的第一条SQL不会输出逻辑SQL和实际SQL信息；然后通过set命令动态更新配置后，执行第二条SQL时会输出逻辑SQL和实际SQL信息；

  * 重启问题  
上面的修改只会影响zookeeper即配置中心里的配置，而程序里的配置并没有变更，如果重启服务的话，配置又会退回去，这个问题怎么办？一般服务都会集成分布式配置管理平台例如disconf，apollo等。这样的话，把
**spring-sharding.xml**
以及其他xml文件中的具体配置抽离到一个properties文件中。当我们通过set命令更新配置中心里的配置的同时，也同步修改分布式配置管理平台上维护的配置，这样的话，即使重启也会加载到最新的配置。

