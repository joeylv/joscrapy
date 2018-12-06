##【Spring】Spring的bean装配前言

##
##bean是Spring最基础最核心的部分，Spring简化代码主要是依赖于bean，下面学习Spring中如何装配bean。装配bean

##
##Spring在装配bean时非常灵活，其提供了三种方式装配bean。在XML中进行显式配置。在Java中进行显式配置。隐式的bean发现机制和自动装配。自动化装配bean

##
##自动化装配技术最为便利，Spring从两个角度实现自动化装配。组件扫描：Spring会自动发现应用上下文中所创建的bean。自动装配：Spring自动满足bean之间的依赖。自动装配示例pom.xml<?xml version="1.0" encoding="UTF-8"?><project xmlns="http://maven.apache.org/POM/4.0.0"         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">    <modelVersion>4.0.0</modelVersion>    <groupId>com.hust.grid.leesf.spring</groupId>    <artifactId>spring-learning</artifactId>    <version>1.0-SNAPSHOT</version>    <properties>        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>        <spring.version>3.1.2.RELEASE</spring.version>        <cglib.version>3.1</cglib.version>        <junit.version>4.11</junit.version>    </properties>    <dependencies>        <dependency>            <groupId>org.springframework</groupId>            <artifactId>spring-context</artifactId>            <version>${spring.version	}</version>        </dependency>        <dependency>            <groupId>junit</groupId>            <artifactId>junit</artifactId>            <version>${junit.version	}</version>        </dependency>        <dependency>            <groupId>org.springframework</groupId>            <artifactId>spring-test</artifactId>            <version>${spring.version	}</version>        </dependency>        <dependency>            <groupId>cglib</groupId>            <artifactId>cglib-nodep</artifactId>            <version>${cglib.version	}</version>        </dependency>    </dependencies></project>CompactDiscpackage ch2;interface CompactDisc {  void play();	}

##
##其只定义了一个play接口，由子类实现。SgtPepperspackage ch2;import org.springframework.stereotype.Component;@Componentpublic class SgtPeppers implements CompactDisc {  private String title = "Sgt. Pepper"s Lonely Hearts Club Band";    private String artist = "The Beatles";    public void play() {    System.out.println("Playing " + title + " by " + artist);  	}	}

##
##SgtPeppers继承了CompactDisc接口，使用Component注释为一个Bean。CDPlayerConfigpackage ch2;import org.springframework.context.annotation.ComponentScan;import org.springframework.context.annotation.Configuration;@Configuration@ComponentScan("ch2")public class CDPlayerConfig {	}

##
##配置类，Spring会自动加载上下文并扫描ch2包下的所有bean。CDPlayerTestpackage ch2;import org.junit.Test;import org.junit.runner.RunWith;import org.springframework.beans.factory.annotation.Autowired;import org.springframework.test.context.ContextConfiguration;import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;import static org.junit.Assert.assertNotNull;@RunWith(SpringJUnit4ClassRunner.class)@ContextConfiguration(classes = CDPlayerConfig.class)public class CDPlayerTest {    @Autowired    private CompactDisc cd;    @Test    public void cdShouldNotNull() {        assertNotNull(cd);    	}	}

##
##该类用于测试是否成功装配CompactDisc的bean，测试成功。设置Bean名称

##
##上述示例中bean的名称默认为sgtPeppers，即将类名的首字母小写，当然可通过@Component("sp")设置其名称为sp；或者使用@Named("sp")进行设置。设置组建扫描基础包

##
##上述示例中指定扫描ch2包，这是通过@ComponentScan("ch")指定的，当然可以通过@ComponentScan(basePackages="ch2")进行设置。若设置多个包，则可采用@ComponentScan(basePackages={"ch2","video"	})方式进行设置。除了使用字符串格式表明包名，也可使用类名格式，如@ComponentScan(basePackageClasses = SgtPeppers.class)指定扫描类。设置自动装配

##
##示例中使用@Autowired实现自动装配，Spring应用上下文中寻找某个匹配的bean，由于示例中CompactDisc只有一个声明为bean的子类，若有多个声明为bean的子类，则会报错，若没有子类，也会报错。@Autowired注解不仅可以用在属性上，也可以用在构造函数上，还可以用在Setter方法上。若使用@Autowired(required=false)时，那么没有符合的bean时不会报错，而是处于未装配的状态，要防止空指针情况，其与@Inject注解功能类似。构造函数使用@Autowired注解@Componentpublic class CDPlayer implements MediaPlayer {    private CompactDisc cd;        @Autowired    public CDPlayer(CompactDisc cd) {        this.cd = cd;    	}    public void play() {    	}	}Setter方法使用@Autowired注解@Autowiredpublic void setCompactDisc(CompactDisc cd) {    this.cd = cd;	}在Java中显式配置

##
##在配置类中显式配置bean，将CDPlayerConfig中的@ComponentScan("ch2")移除，此时运行测试用例会报错，下面通过显式配置方法来配置bean。修改CDPlayerConfig代码如下。package ch2;import org.springframework.context.annotation.Bean;import org.springframework.context.annotation.Configuration;@Configurationpublic class CDPlayerConfig {    @Bean    public CompactDisc sgtPeppers() {        return new SgtPeppers();    	}	}

##
##上述生成的bean名称与方法名相同，若想设置名称，可通过@Bean(name=sp)进行设置。对于如下代码，调用sgtPeppers会生成同一个sgtPeppers的bean，这是由于sgtPeppers方法标记为Bean，Spring会拦截所有对该方法的调用，并且返回一个已经创建的bean实例。默认情况下，Spring中的bean都是单例的。    @Bean    public CDPlayer cdPlayer() {        return new CDPlayer(sgtPeppers());    	}    @Bean    public CDPlayer anotherCDPlayer() {        return new CDPlayer(sgtPeppers());    	}

##
##还可以使用如下方法来引用bean@Beanpublic CDPlayer cdPlayer(CompactDisc compactDisc) {    return new CDPlayer(compactDisc);	}

##
##这样会自动装配一个CompactDisc到配置方法中，不用明确使用sgtPeppers方法来构造CDPlayer。通过xml装配bean

##
##除了使用JavaConfig来显式装配bean外，还可以使用xml文件来装配bean。若想在xml中声明一个bean元素，则需要如下操作。<?xml version="1.0" encoding="UTF-8"?><beans xmlns="http://www.springframework.org/schema/beans"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  xmlns:context="http://www.springframework.org/schema/context"  xmlns:c="http://www.springframework.org/schema/c"  xmlns:p="http://www.springframework.org/schema/p"  xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd        http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context.xsd">  <bean id="sgtPeppers" class="ch2.SgtPeppers" /></beans>

##
##上述xml文件中声明了一个名为sgtPeppers的bean，会调用SgtPeppers的默认构造函数创建bean。使用构造器注入初始化bean使用constructor-arg元素<bean id="cdPlayer" class="ch2.CDPlayer">    <constructor-arg ref="compactDisc"/></bean>

##
##上述代码表示将ID为compactDisc的bean引用传递到CDPlayer的构造器中。使用c-命令空间<bean id="cdPlayer" class="ch2.CDPlayer"    c:cd-ref="compactDisc"/></bean>

##
##其中c:表示命名空间前缀；cd表示构造器参数名；-ref表示注入的bean的引用；compactDisc表示要注入的bean的ID。将字面量注入到构造器中<bean id="compactDisc" class="ch2.BlankDisc">    <constructor-arg value="Sgt. Pepper"s Lonely Hearts Club Band" />    <constructor-arg value="The Beatles" />

##
##或者使用<bean id="compactDisc" class="ch2.BlankDisc"    <c:_title="Sgt. Pepper"s Lonely Hearts Club Band" />    <c:artist="The Beatles" />装配集合到构造器中装配字面量到List集合<bean id="compactDisc" class="ch2.BlankDisc">    <constructor-arg value="Sgt. Pepper"s Lonely Hearts Club Band" />    <constructor-arg value="The Beatles" />    <constructor-arg>        <list>            <value>Sgt.AA</value>            <value>Sgt.BB</value>            <value>Sgt.CC</value>        </list>    </constructor-arg></bean>装配引用List集合<bean id="compactDisc" class="ch2.BlankDisc">    <constructor-arg value="Sgt. Pepper"s Lonely Hearts Club Band" />    <constructor-arg value="The Beatles" />    <constructor-arg>        <list>            <ref bean="sgtPeppers"/>            <ref bean="whiteAlbum"/>            <ref bean="revolver"/>        </list>    </constructor-arg></bean>

##
##同理，对于Set集合只需修改list为set即可。设置属性使用xml设置属性<bean id="cdPlayer" class="ch2.CDPlayer">    <property name="compactDisc" ref="compactDisc"></bean>使用p-命令空间进行装配<bean id="cdPlayer" class="ch2.CDPlayer"    p:compactDisc-ref="compactDisc"></bean>

##
##其组成与c-类似。将字面量装配到属性中<bean id="compactDisc" class="ch2.BlankDisc">    <property name="title" value="Sgt. Pepper"s Lonely Hearts Club Band" />    <property name="artist"value="The Beatles" />    <property name="tracks">        <list>            <value>Sgt.AA</value>            <value>Sgt.BB</value>            <value>Sgt.CC</value>        </list>    </property></bean>使用p-装配属性<bean id="compactDisc" class="ch2.BlankDisc">    <p:title="Sgt. Pepper"s Lonely Hearts Club Band" />    <p:artist="value="The Beatles" />    <property name="tracks">        <list>            <value>Sgt.AA</value>            <value>Sgt.BB</value>            <value>Sgt.CC</value>        </list>    </property></bean>使用util-命名空间装配集合<util:list id="tractList">    <value>Sgt.AA</value>    <value>Sgt.BB</value>    <value>Sgt.CC</value></util:list>

##
##此时对应修改如下<bean id="compactDisc" class="ch2.BlankDisc">    <p:title="Sgt. Pepper"s Lonely Hearts Club Band" />    <p:artist="value="The Beatles" />    <p:tracks-ref="trackList" /></bean>导入和混合配置在JavaConfig中引用xml配置

##
##将BlankDisc从CDPlayerConfig中剥离出来，放置在自己的配置文件CDConfig中。此时需要在CDPlayerConfig中使用@Import(CDConfig.class)将两者组合；或者使用更高级别的Config中使用@Import({CDPlayerConfig.class,CDConfig.class	})组合两者。若将BlankDisc配置在cd-config.xml文件中，则可使用@ImportResource("classpath:cd-config.xml")导入。在xml配置中引用JavaConfig

##
##可以使用import元素引用配置，如<import resource="cd-config.xml" />总结

##
##Spring有三种方式装配bean，使用自动化装配技术使得代码更简洁；并且有多种方式注入属性。