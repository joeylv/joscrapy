  * 1 1\. POM配置
  * 2 2 . 配置数据源
  * 3 3\. 集成sharding数据源
  * 4 4\. 注意事项
  * 5 5\. Main测试
  * 6 6\. 遗留问题

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/7b6997c3586d>

本篇文章讲解如何在ssm（spring、springmvc、mybatis）结构的程序上集成sharding-jdbc（版本为 **2.0.3**
）进行分库分表；  
假设分库分表行为如下：

  * 将auth_user表分到4个库（user_0~user_3）中；
  * 其他表不进行分库分表，保留在default_db库中；

## 1\. POM配置

以spring配置文件为例，新增如下POM配置：

    
    
    <dependency>
        <groupId>io.shardingjdbc</groupId>
        <artifactId>sharding-jdbc-core</artifactId>
        <version>2.0.3</version>
    </dependency>
    
    <!--如果通过spring配置, 需要增加如下maven坐标-->
    <dependency>
        <groupId>io.shardingjdbc</groupId>
        <artifactId>sharding-jdbc-core-spring-namespace</artifactId>
        <version>2.0.3</version>
    </dependency>
    

## 2 . 配置数据源

spring-
datasource.xml配置所有需要的数据源如下–auth_user分库分表后需要的4个库user_0~user_3，以及不分库分表的默认库default_db：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.springframework.org/schema/beans
            http://www.springframework.org/schema/beans/spring-beans.xsd">
    
        <!-- 配置数据源 -->
        <bean id="sj_ds_0" class="com.alibaba.druid.pool.DruidDataSource"
              init-method="init" destroy-method="close">
            <property name="url" value="${sj_user_0.url}" />
            <property name="username" value="${sj_user_0.username}" />
            <property name="password" value="${sj_user_0.password}" />
            <!--druid配置优化可以放在这里-->
        </bean>
    
        <!-- 配置数据源 -->
        <bean id="sj_ds_1" class="com.alibaba.druid.pool.DruidDataSource"
              init-method="init" destroy-method="close">
            <property name="url" value="${sj_user_1.url}" />
            <property name="username" value="${sj_user_1.username}" />
            <property name="password" value="${sj_user_1.password}" />
            <!--druid配置优化可以放在这里-->
        </bean>
    
        <!-- 配置数据源 -->
        <bean id="sj_ds_2" class="com.alibaba.druid.pool.DruidDataSource"
              init-method="init" destroy-method="close">
            <property name="url" value="${sj_user_2.url}" />
            <property name="username" value="${sj_user_2.username}" />
            <property name="password" value="${sj_user_2.password}" />
            <!--druid配置优化可以放在这里-->
        </bean>
    
        <!-- 配置数据源 -->
        <bean id="sj_ds_3" class="com.alibaba.druid.pool.DruidDataSource"
              init-method="init" destroy-method="close">
            <property name="url" value="${sj_user_3.url}" />
            <property name="username" value="${sj_user_3.username}" />
            <property name="password" value="${sj_user_3.password}" />
            <!--druid配置优化可以放在这里-->
        </bean>
    
        <!-- 配置数据源 -->
        <bean id="sj_ds_default" class="com.alibaba.druid.pool.DruidDataSource"
              init-method="init" destroy-method="close">
            <property name="url" value="${sj_default.url}" />
            <property name="username" value="${sj_default.username}" />
            <property name="password" value="${sj_default.password}" />
            <!--druid配置优化可以放在这里-->
        </bean>
    </beans>
    

properties配置文件内容如下：

    
    
    sj_user_0.driver=com.mysql.jdbc.Driver
    sj_user_0.url=jdbc:mysql://localhost:3306/user_0
    sj_user_0.username=root
    sj_user_0.password=RootAfei_1
    
    sj_user_1.driver=com.mysql.jdbc.Driver
    sj_user_1.url=jdbc:mysql://localhost:3306/user_1
    sj_user_1.username=root
    sj_user_1.password=RootAfei_1
    
    sj_user_2.driver=com.mysql.jdbc.Driver
    sj_user_2.url=jdbc:mysql://localhost:3306/user_2
    sj_user_2.username=root
    sj_user_2.password=RootAfei_1
    
    sj_user_3.driver=com.mysql.jdbc.Driver
    sj_user_3.url=jdbc:mysql://localhost:3306/user_3
    sj_user_3.username=root
    sj_user_3.password=RootAfei_1
    
    sj_default.driver=com.mysql.jdbc.Driver
    sj_default.url=jdbc:mysql://localhost:3306/default_db
    sj_default.username=root
    sj_default.password=RootAfei_1
    

## 3\. 集成sharding数据源

spring-sharding.xml配置如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:sharding="http://shardingjdbc.io/schema/shardingjdbc/sharding"
           xsi:schemaLocation="http://www.springframework.org/schema/beans
                            http://www.springframework.org/schema/beans/spring-beans.xsd
                            http://shardingjdbc.io/schema/shardingjdbc/sharding
                            http://shardingjdbc.io/schema/shardingjdbc/sharding/sharding.xsd">
    
        <!--数据库sharding策略-->
        <sharding:standard-strategy id="databaseStrategy" sharding-column="id"
                                    precise-algorithm-class="com.crt.fin.ospsso.service.shardingjdbc.AuthUserDatabaseShardingAlgorithm" />
        <!--auth_user表sharding策略:无 -->
    
        <sharding:none-strategy id="noneStrategy" />
    
        <sharding:data-source id="shardingDataSource">
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
                <prop key="sql.show">true</prop>
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
    

> 说明：spring-
sharding.xml配置的分库分表规则：auth_user表分到id为sj_ds_${0..3}的四个库中，表名保持不变；其他表在id为sj_ds_default库中，不分库也不分表；
**集成sharding-
jdbc的核心就是将SqlSessionFactoryBean需要的dataSource属性修改为`shardingDataSource`**
，把数据源交给sharding-jdbc处理；

另外，通过对比这里和sharding-
jdbc1.5.4.1版本的配置[请戳链接：https://www.jianshu.com/p/602e24845ed3](https://www.jianshu.com/p/602e24845ed3)，差异还是比较大，大概提现在如下一些地方：

  1. namespace由rdb改为sharding；
  2. 默认数据库策略和默认表策略被设置为“节点的属性，分别是`default-database-strategy-ref`和`default-table-strategy-ref`；
  3. 默认数据源被设置为“节点的属性，即`default-data-source-name`；
  4. “一些属性变更，例如：actual-tables改为actual-data-nodes，database-strategy改为database-strategy-ref；

> 我们平常开发过程中，可以参考sharding-jdbc源码sharding-jdbc-core-spring-
namespace模块中META.rdb目录下的xml，作者对几乎各种使用方式都有实例；

分库逻辑`AuthUserDatabaseShardingAlgorithm`的代码很简单，源码如下：

    
    
    /**
     * @author wangzhenfei9
     * @version 1.0.0
     * @since 2018年05月14日
     */
    public class AuthUserDatabaseShardingAlgorithm implements PreciseShardingAlgorithm<Long> {
    
        private final Logger logger = LoggerFactory.getLogger(this.getClass());
    
        private static final int SHARDING_NUMBER = 4;
    
        @Override
        public String doSharding(final Collection<String> availableTargetNames,
                                 final PreciseShardingValue<Long> shardingValue) {
            for (String each : availableTargetNames) {
                if (each.endsWith(shardingValue.getValue() % SHARDING_NUMBER + "")) {
                    logger.debug("the target database name: {}", each);
                    return each;
                }
            }
            throw new UnsupportedOperationException();
        }
    
    }
    

> 这段代码参考sharding-
jdbc源码中`PreciseShardingAlgorithm.java`接口的实现即可，例如`PreciseModuloDatabaseShardingAlgorithm.java`；这里和sharding-
jdbc1.5.4.1版本的差异也比较大，sharding-
jdbc1.5.4.1对于分库或者分表sharding算法实现的接口是不一样的，sharding-
jdbc2.0.3将两者合二为一，且只有一个方法，即doSharding();

## 4\. 注意事项

无法识别sharding-jdbc分库分表规则inline-expression问题，例如：  
“

  1. 根本原因：  
根本原因是spring把`${}`当做占位符，`${0..3}`这种表达式，spring会尝试去properties文件中找key为`0..3`的属性。但是这里是sharding-
jdbc分库分表规则的inline表达式，需要spring忽略这种行为。否则会抛出异常:  
java.lang.IllegalArgumentException: Could not resolve placeholder ‘0..3’ in
value “sj_ds_${0..3}.auth_user”

  2. 解决办法：  
配置: `或者:`

## 5\. Main测试

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
    
            // user_permission没有分库分表
            UserPermissionMapper userPermissionMapper = context.getBean(UserPermissionMapper.class);
            UserPermission userPermission = userPermissionMapper.selectPermissionByUsername("wangzhenfei", "FINANCE_WALLET");
            System.out.println("-----< The user permission: "+JSON.toJSONString(userPermission));
        }
    
    }
    

>
AuthUserMapper.selectByPrimaryKey()和UserPermissionMapper.selectPermissionByUsername()的代码和没有分库分表的代码完全一样；

## 6\. 遗留问题

Main方法测试，或者启动服务后的调用测试都没有问题，但是通过junit测试用例访问就会抛出异常，作为一个待解决的遗留问题：

    
    
    org.springframework.beans.factory.NoUniqueBeanDefinitionException: No qualifying bean of type "javax.sql.DataSource" available: expected single matching bean but found 6: sj_ds_0,sj_ds_1,sj_ds_2,sj_ds_3,sj_ds_default,shardingDataSource
    

