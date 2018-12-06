##【Spring】高级装配前言

##
##前面讲解了bean的核心装配技术，其可应付很多中装配情况，但Spring提供了高级装配技术，以此实现更为高级的bean装配功能。高级装配配置profile bean

##
##将所有不同bean定义放置在一个或多个profile中，在将应用部署到每个环境时，要确保对应的profile处于激活状态。如配置了如下数据源，并使用profile注解定义。JavaConfig配置profile开发环境中的数据源配置package com.hust.grid.leesf.ch3;import javax.activation.DataSource;import org.springframework.context.annotation.Bean;import org.springframework.context.annotation.Configuration;import org.springframework.context.annotation.Profile;import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;@Configuratoin@Profile("dev")public class DevelopmentProfileConcifg {    @Bean(destroyMethod = "shutdown")    public DataSource embeddedDataSource() {        return new EmbeddedDatabaseBuilder()            .setType(EmbeddedDatabaseType.H2)            .addScript("classpath:schema.sql")            .addScript("classpath:test-data.sql")            .build();    	}   	}生产环境下的数据源配置package com.hust.grid.leesf.ch3;import javax.sql.DataSource;import org.springframework.context.annotation.Bean;import org.springframework.context.annotation.Configuration;import org.springframework.context.annotation.Profile;import org.springframework.jndi.JndiObjectFactoryBean;@Configurationpublic class ProductionProfileConfig {   @Bean  @Profile("prod")  public DataSource jndiDataSource() {    JndiObjectFactoryBean jndiObjectFactoryBean = new JndiObjectFactoryBean();    jndiObjectFactoryBean.setJndiName("jdbc/myDS");    jndiObjectFactoryBean.setResourceRef(true);    jndiObjectFactoryBean.setProxyInterface(javax.sql.DataSource.class);    return (DataSource) jndiObjectFactoryBean.getObject();  	}	}

##
##只有在prod profile激活时，才会创建对应的bean。在Spring 3.1之前只能在类级别上使用@Profile注解，从Spring 3.2之后，可以从方法级别上使用@Profile注解，与@Bean注解一起使用，上述放在两个不同配置类可以转化为两个方法放在同一个配置类中。package com.hust.grid.leesf.ch3;import javax.sql.DataSource;import org.springframework.context.annotation.Bean;import org.springframework.context.annotation.Configuration;import org.springframework.context.annotation.Profile;import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;import org.springframework.jndi.JndiObjectFactoryBean;@Configurationpublic class DataSourceConfig {    @Bean(destroyMethod = "shutdown")  @Profile("dev")  public DataSource embeddedDataSource() {    return new EmbeddedDatabaseBuilder()        .setType(EmbeddedDatabaseType.H2)        .addScript("classpath:schema.sql")        .addScript("classpath:test-data.sql")        .build();  	}  @Bean  @Profile("prod")  public DataSource jndiDataSource() {    JndiObjectFactoryBean jndiObjectFactoryBean = new JndiObjectFactoryBean();    jndiObjectFactoryBean.setJndiName("jdbc/myDS");    jndiObjectFactoryBean.setResourceRef(true);    jndiObjectFactoryBean.setProxyInterface(javax.sql.DataSource.class);    return (DataSource) jndiObjectFactoryBean.getObject();  	}	}

##
##注意：尽管配置类中配置了不同的Profile，但只有规定的profile激活时，对应的bean才会被激活。XML配置profile<?xml version="1.0" encoding="UTF-8"?><beans xmlns="http://www.springframework.org/schema/beans"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:jdbc="http://www.springframework.org/schema/jdbc"  xmlns:jee="http://www.springframework.org/schema/jee" xmlns:p="http://www.springframework.org/schema/p"  xsi:schemaLocation="    http://www.springframework.org/schema/jee    http://www.springframework.org/schema/jee/spring-jee.xsd    http://www.springframework.org/schema/jdbc    http://www.springframework.org/schema/jdbc/spring-jdbc.xsd    http://www.springframework.org/schema/beans    http://www.springframework.org/schema/beans/spring-beans.xsd"  profile="dev">  <jdbc:embedded-database id="dataSource">    <jdbc:script location="classpath:schema.sql" />    <jdbc:script location="classpath:test-data.sql" />    </jdbc:embedded-database></beans>

##
##或者使用beans元素定义多个profile。<?xml version="1.0" encoding="UTF-8"?><beans xmlns="http://www.springframework.org/schema/beans"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:jdbc="http://www.springframework.org/schema/jdbc"  xmlns:jee="http://www.springframework.org/schema/jee" xmlns:p="http://www.springframework.org/schema/p"  xsi:schemaLocation="    http://www.springframework.org/schema/jee    http://www.springframework.org/schema/jee/spring-jee.xsd    http://www.springframework.org/schema/jdbc    http://www.springframework.org/schema/jdbc/spring-jdbc.xsd    http://www.springframework.org/schema/beans    http://www.springframework.org/schema/beans/spring-beans.xsd">  <beans profile="dev">    <jdbc:embedded-database id="dataSource">      <jdbc:script location="classpath:schema.sql" />      <jdbc:script location="classpath:test-data.sql" />    </jdbc:embedded-database>  </beans>  <beans profile="qa">    <bean id="dataSource"          class="org.apache.commons.dbcp.BasicDataSource"          destory-method="close"          p:url="jdbc:h2:tcp://dbserver/~/test"          p:driverClassName="org.h2.Driver"          p:username="sa"          p:password="password"          p:initialSize="20"          p:maxActive="30" />  </beans>    <beans profile="prod">    <jee:jndi-lookup id="dataSource"      jndi-name="jdbc/myDatabase"      resource-ref="true"      proxy-interface="javax.sql.DataSource" />  </beans></beans>

##
##三个bean的ID都是dataSource，在运行时会动态创建一个bean，这取决激活的哪个profile。激活profile

##
##Spring依赖spring.profiles.active和spring.profiles.default两个属性确定哪个profile处于激活状态，如果设置了spring.profiles.active，那么其值用于确定哪个profile是激活状态，如果未设置，则查找spring.profiles.defaults的值；如果均未设置，则没有激活的profile，只会创建那些没有定义在profile中的bean。如下是在web.xml中设置spring.profiles.default。<?xml version="1.0" encoding="UTF-8"?><web-app version="2.5"  ...><context-param>    <param-name>spring.profiles.default</param-name>    <param-value>dev</param-value></context-param><servlet>    <init-param>        <param-name>spring.profiles.default</param-name>        <param-value>dev</param-value>    </init-param></servlet>

##
##Spring提供了@ActiveProfiles注解启用profile。@Runwith(SpringJUnit4ClassRunner.class)@ContextConfiguration(classes={PersistenceTestConfig.class	})@ActiveProfiles("dev")public class PersistenceTest {    ...	}条件化的bean

##
##使用@Conditional注解，如果给定条件计算结果为true，那么创建bean，否则不创建。MagicBean@Bean@Condition(MagicExistsCondition.class)public MagicBean magicBean() {    return new MagicBean();	}MagicExistsConditionpackage com.hust.grid.leesf.ch3;import org.springframework.context.annotation.Condition;import org.springframework.context.annotation.ConditionContext;import org.springframework.core.type.AnnotatedTypeMetadata;import org.springframework.util.ClassUtils;public class MagicExistsCondition implements Condition {    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {        Environment env = context.getEnvironment();        return env.containsProperty("magic");    	}	}处理自动装配的歧义性

##
##如下代码@Autowiredpublic void setDessert(Dessert dessert) {    this.dessert = dessert;	}

##
##其中Dessert为一个接口，其有多个子类。@Componentpublic class Cake implements Dessert {	}@Componentpublic class Cookies implements Dessert {	}@Componentpublic class IceCream implements Dessert {	}

##
##此时，会发现不止一个bean可以匹配，Spring会抛出异常，可以将某个bean设置为首选的bean或使用限定符。标识首选bean

##
##使用Primary注解标识首选bean。@Component@Primarypublic class IceCream implements Dessert {	}

##
##或者使用xml配置首选bean<bean id="iceCream"      class="com.dessertteater.IceCream"      primary="true" />

##
##如果配置多个首选bean，那么也将无法工作。限定自动装配的bean

##
##使用@Qualifier注解进行限定。@Autowired@Qualifier("iceCream")pulbic void setDessert(Dessert dessert) {    this.dessert = dessert;	}创建自定义限定符

##
##可以为bean设置自己的限定符，而不依赖将bean ID作为限定符，在bean的声明上使用@Qualifier注解，其可以与@Component组合使用。@Component@Qualifier("cold")public class IceCream implements Dessert {	}

##
##这样，使用如下。@Autowired@Qualifier("cold")pulbic void setDessert(Dessert dessert) {    this.dessert = dessert;	}使用自定义的限定符注解

##
##如果多个bean都具备相同特性的话，那么也会出现问题，无法确定唯一bean，如定义@Cold注解@Target({ElementType.CONSTRUCTOR, ElementType.FIELD,            ElementType.METHOD, ElementType.TYPE	})@Retention(RetentionPolicy.RUNTIME)#Qualifierpublic @interface Cold {	}

##
##这样就可以使用如下注解进行定义@Component@Cold@Creamypublic class IceCream implements Dessert {	} 

##
##通过自定义注解后，然后可以通过多个注解的组合确定唯一一个符合条件的bean。@Autowired@Cold@Creamypulbic void setDessert(Dessert dessert) {    this.dessert = dessert;	}bean的作用域

##
##默认情况下，Spring上下文中所有bean都是作为以单例形式创建的。但有时候需要多个不同的bean实例，Spring定义了多种作用域，包括：单例，整个应用中，只创建一个bean实例。原型，每次注入或者通过Spring应用上下文获取时，都会创建一个新的bean实例。会话，在Web应用中，为每个会话创建一个bean实例。请求，在Web应用中，为每个请求创建一个bean实例。

##
##使用@Scope注解确定bean的作用域，如将如下bean声明为原型。@Component@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)public class NotePad {	}

##
##当使用xml文件配置时如下<bean id="notepad"      class="com.hust.grid.leesf.Notepad"      scope="prototype" />使用会话和请求作用域

##
##在Web应用中，可能需要实例化在会话和请求范围内共享的bean，如电商网站，需要会话作用域。@Component@Scope(    value=WebApplicationContext.SCOPE_SESSION,    proxyMode=ScopedProxyMode.INTERFACES)public ShoppingCart cart() {	}

##
##需要将ShoppingCart bean注入到单例StoreService bean中。@Componentpublic class StoreService {    @Autowired    public void setShoppingCart(ShoppingCart shoppingCart) {        this.shoppingCart = shoppingCart;    	}	}

##
##此时，由于ShoppingCart是会话作用域，直到某个用户创建了会话后，才会出现ShoppingCart实例，并且Spring会注入一个代理至StoreService中，这个代理与ShoppingCart有相同的方法，当处理时需要将调用委托给会话作用域内真正的ShoppingCart。在XML中声明作用域代理

##
##需要使用Spring aop命名空间的新元素<bean id="cart"      class="com.hust.grid.leesf.ShoppingCart"      scope="session">  <aop:scoped-proxy /></bean>

##
##上述情况会使用CGLib创建目标类的代理，但也可将proxy-target-class属性设置为false，进而要求它生成基于接口的代理。<bean id="cart"      class="com.hust.grid.leesf.ShoppingCart"      scope="session">  <aop:scoped-proxy proxy-target-class="false" /></bean>

##
##为使用<aop:scoped-proxy>元素，需要在XML中声明spring-aop.xsd命名空间。运行时值注入

##
##不使用硬编码注入，想让值在运行时确定，Spring提供了如下两种方式。属性占位符Spring表达式语言注入外部的值

##
##声明属性源并通过Spring的Environment来检索属性。...@Configuration@PropertySource("classpath:/com/hust/gird/leesf/app.properties")public class ExpressiveConfig {    @Autowired    Environment env;        @Bean    public BlankDisc disc() {        return new BlankDisc(            env.getProperty("disc.title"),            env.getProperty("disc.artist"));    	}	}

##
##通过在app.properties中配置对应的属性完成注入。还可使用占位符完成注入。public BlankDisc(    @Value("${disc.title	}") String title,    @Value("${disc.artist	}") String artist) {  this.title = title;   this.artist = artist;	}

##
##为使用占位符，需要配置PropertySourcesPlaceholderConfigurer。@Beanpublic static PropertySourcesPlaceholderConfigurer placeholderConfigurer() {    return new PropertySourcesPlaceholderConfigurer();	}

##
##或者在XML配置文件中使用<context:property-placeholder />，这样会生成一个PropertySourcesPlaceholderConfigurer的bean。总结

##
##本篇学习了更为高级的装配技巧，如Spring profile，还有条件化装配bean，以及bean的作用域等等。