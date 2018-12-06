##【MyBatis】MyBatis自动生成代码之查询爬坑记前言

##
##项目使用SSM框架搭建Web后台服务，前台后使用restful api，后台使用MyBatisGenerator自动生成代码，在前台使用关键字进行查询时，遇到了一些很宝贵的坑，现记录如下。为展示所遇问题，将项目进行了精简。项目框架后台框架

##
##后台框架选型为Spring + SpringMVC + Mybatis + Jetty，其中使用MyBatisGenerator创建代码，Jetty为内嵌的Web服务器。项目代码

##
##代码已上传至github项目介绍数据准备

##
##创建库ssm和表users，其中创建表users的SQL如下。CREATE TABLE `users` (  `id` int(10) NOT NULL AUTO_INCREMENT,  `name` varchar(32) DEFAULT NULL,  `address` varchar(32) DEFAULT NULL,  `hobby` varchar(64) DEFAULT NULL,  `content` text,  PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=latin1insert into users(name, address, hobby, content) values("leesf", "hubei", "sport, race", "he is a boy");insert into users(name, address, hobby, content) values("dyd", "hubei", "painting, reading", "she is a girl");自动生成代码框架

##
##使用MyBatisGenerator自动生成相应代码，其源码如下。package com.leesf;import org.junit.Test;import org.mybatis.generator.api.MyBatisGenerator;import org.mybatis.generator.config.Configuration;import org.mybatis.generator.config.xml.ConfigurationParser;import org.mybatis.generator.internal.DefaultShellCallback;import java.io.File;import java.util.ArrayList;import java.util.List;public class MybatisGenerator {  @Test public void generator() throws Exception {    List<String> warnings = new ArrayList<String>();    File configFile = new File(        "F:/01_Code/01_Idea/ssm-master/src/test/generatorConfig.xml");    ConfigurationParser cp = new ConfigurationParser(warnings);    Configuration config = cp.parseConfiguration(configFile);    DefaultShellCallback callback = new DefaultShellCallback(true);    MyBatisGenerator myBatisGenerator =        new MyBatisGenerator(config, callback, warnings);    myBatisGenerator.generate(null);  	}	}

##
##其中generatorConfig.xml文件如下。<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE generatorConfiguration        PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"        "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd"><generatorConfiguration>    <!-- <context> 元素用于指定生成一组对象的环境。 子元素用于指定要连接到的数据库、 要生成对象的类型和要内省的表 -->    <context id="testTables" targetRuntime="MyBatis3">        <commentGenerator>            <!-- 是否去除自动生成的注释 true：是 ： false:否 -->            <property name="suppressAllComments" value="true"/>        </commentGenerator>        <!--数据库连接的信息：驱动类、连接地址、用户名、密码 -->        <jdbcConnection driverClass="com.mysql.jdbc.Driver"                        connectionURL="jdbc:mysql://localhost:3306/ssm?useUnicode=true&amp;amp;characterEncoding=UTF-8"                        userId="root"                        password="">        </jdbcConnection>        <!-- 默认false，把JDBC DECIMAL 和 NUMERIC 类型解析为 Integer，为 true时把JDBC DECIMAL 和            NUMERIC 类型解析为java.math.BigDecimal -->        <javaTypeResolver>            <property name="forceBigDecimals" value="false"/>        </javaTypeResolver>        <!-- targetProject:生成PO类的位置         注意对于targetProject：In other environments（other than Eclipse）,         this value should be an existing directory on the local file system.         即对于非eclipse项目需要指定绝对路径         -->        <javaModelGenerator targetPackage="com.leesf.po"                            targetProject="F:/01_Code/01_Idea/ssm-master/src/main/java">            <!-- enableSubPackages:是否让schema作为包的后缀 -->            <property name="enableSubPackages" value="false"/>            <!-- 从数据库返回的值被清理前后的空格 -->            <property name="trimStrings" value="true"/>        </javaModelGenerator>        <!-- targetProject:mapper映射文件生成的位置 -->        <sqlMapGenerator targetPackage="com.leesf.mapper"                         targetProject="F:/01_Code/01_Idea/ssm-master/src/main/java">            <!-- enableSubPackages:是否让schema作为包的后缀 -->            <property name="enableSubPackages" value="false"/>        </sqlMapGenerator>        <!-- targetPackage：mapper接口生成的位置 -->        <javaClientGenerator type="XMLMAPPER"                             targetPackage="com.leesf.mapper"                             targetProject="F:/01_Code/01_Idea/ssm-master/src/main/java">            <!-- enableSubPackages:是否让schema作为包的后缀 -->            <property name="enableSubPackages" value="false"/>        </javaClientGenerator>        <!-- 指定数据库表 -->        <table tableName="users"></table>        <!-- <table schema="" tableName="sys_user"></table>        <table schema="" tableName="sys_role"></table>        <table schema="" tableName="sys_permission"></table>        <table schema="" tableName="sys_user_role"></table>        <table schema="" tableName="sys_role_permission"></table> -->        <!-- 有些表的字段需要指定java类型         <table schema="" tableName="">            <columnOverride column="" javaType="" />        </table> -->    </context></generatorConfiguration>WebServer

##
##WebServer为Web容器，其源码如下。package com.leesf.main;import java.net.UnknownHostException;import java.util.concurrent.ArrayBlockingQueue;import java.util.concurrent.TimeUnit;import org.apache.commons.lang3.StringUtils;import org.eclipse.jetty.server.Connector;import org.eclipse.jetty.server.Server;import org.eclipse.jetty.server.nio.SelectChannelConnector;import org.eclipse.jetty.util.thread.ExecutorThreadPool;import org.eclipse.jetty.webapp.WebAppContext;import org.slf4j.Logger;import org.slf4j.LoggerFactory;public class WebServer {  public static final String CONTEXT = "/";  private static final Logger LOG = LoggerFactory.getLogger(WebServer.class);  private static final String DEFAULT_WEBAPP_PATH = "webapps/";  private Server server;  private int port;  public WebServer() {  	}  public Server createServerInSource() throws UnknownHostException {    port = 8081;    server = new Server();    server.setStopAtShutdown(true);    SelectChannelConnector connector = new SelectChannelConnector();    connector.setPort(port);    connector.setReuseAddress(false);    connector.setAcceptQueueSize(50);    connector.setAcceptors(2);    connector.setThreadPool(        new ExecutorThreadPool(20,            40, 0, TimeUnit.SECONDS,            new ArrayBlockingQueue<Runnable>(                16, false)));    connector.setLowResourcesMaxIdleTime(3000);    connector.setReuseAddress(true);    connector.setRequestBufferSize(        16 * 1024);    connector.setRequestHeaderSize(        8 * 1024);    server.setConnectors(new Connector[] { connector 	});    String basePath = "src/main/webapps";    if (StringUtils.isEmpty(basePath)) {      basePath = DEFAULT_WEBAPP_PATH;    	}    WebAppContext webContext = new WebAppContext(basePath, CONTEXT);    webContext.setContextPath(CONTEXT);    webContext.setDescriptor(basePath + "/WEB-INF/web.xml");    System.out.println("-------------web.xml path is " + webContext.getDescriptor()        + "--------------");    webContext.setResourceBase(basePath);    webContext.setClassLoader(Thread.currentThread().getContextClassLoader());    server.setHandler(webContext);    return server;  	}  public void start() throws Exception {    if (server == null) {      createServerInSource();    	}    if (server != null) {      server.start();      LOG.info("WebServer has started at port:" + port);    	}  	}  public void stop() throws Exception {    if (server != null) {      server.stop();    	}  	}  public static void main(String[] args) throws Exception {    WebServer webServer = new WebServer();    webServer.start();  	}	}

##
##使用内嵌Jetty方式提供Web服务，只做演示，其中参数并未进行调优处理。Controller

##
##只存在UserController，其源码如下。package com.leesf.controller;import com.leesf.po.Users;import com.leesf.service.UserService;import com.leesf.utils.ResultUtils;import org.springframework.beans.factory.annotation.Autowired;import org.springframework.stereotype.Controller;import org.springframework.web.bind.annotation.RequestMapping;import org.springframework.web.bind.annotation.RequestMethod;import org.springframework.web.bind.annotation.RequestParam;import org.springframework.web.bind.annotation.ResponseBody;import javax.servlet.http.HttpServletRequest;import javax.servlet.http.HttpServletResponse;import java.io.OutputStreamWriter;import java.util.List;@Controller @RequestMapping(value = "/users")public class UserController {  @Autowired UserService userService;  @ResponseBody @RequestMapping(value = "/listUsers", method = {      RequestMethod.POST, RequestMethod.GET 	}) public void listUsers(      HttpServletRequest request, HttpServletResponse response,      @RequestParam(required = false) String name,      @RequestParam(required = false) String key) throws Exception {    System.out.println("xxxxxx");    OutputStreamWriter out = new OutputStreamWriter(response.getOutputStream());    List<Users> users = userService.getUsers(name, key);    ResultUtils.resultSuccess(users, out);  	}	}

##
##可以根据用户名字和关键字查询用户。Service

##
##UserServiceImp为UserService的实现类。根据用户名查询指定记录

##
##其源码如下。package com.leesf.service.impl;import com.leesf.mapper.UsersMapper;import com.leesf.po.Users;import com.leesf.po.UsersExample;import com.leesf.service.UserService;import org.apache.commons.lang3.StringUtils;import org.slf4j.Logger;import org.slf4j.LoggerFactory;import org.springframework.beans.factory.annotation.Autowired;import org.springframework.stereotype.Service;import java.util.HashMap;import java.util.List;import java.util.Map;@Service("userService") public class UserServiceImp implements UserService {  @Autowired UsersMapper usersMapper;  private Logger LOG = LoggerFactory.getLogger(this.getClass());  public List<Users> getUsers(String name, String key) {    UsersExample usersExample = new UsersExample();    usersExample.createCriteria().andNameLike(name);    List<Users> users = usersMapper.selectByExampleWithBLOBs(usersExample);    return users;  	}	}

##
##可以看到，该Service根据name查找匹配name的记录，启动WebServer，访问http://localhost:8081/users/listUsers?name=sport，查看编译器运行的信息，发现构造了如下SQL语句，

##
##select id, name, address, hobby , content from users WHERE ( name like ? )。

##
##url访问结果如下：{    result_code: "0",    result_msg: "Succeed!",    result_content: [{        id: 1,        name: "leesf",        address: "hubei",        hobby: "sport, race",        content: "he is a boy"    	}]	}根据用户名和关键字查询指定记录

##
##其源码如下package com.leesf.service.impl;import com.leesf.mapper.UsersMapper;import com.leesf.po.Users;import com.leesf.po.UsersExample;import com.leesf.service.UserService;import org.apache.commons.lang3.StringUtils;import org.slf4j.Logger;import org.slf4j.LoggerFactory;import org.springframework.beans.factory.annotation.Autowired;import org.springframework.stereotype.Service;import java.util.HashMap;import java.util.List;import java.util.Map;@Service("userService") public class UserServiceImp implements UserService {  @Autowired UsersMapper usersMapper;  private Logger LOG = LoggerFactory.getLogger(this.getClass());  public List<Users> getUsers(String name, String key) {    UsersExample usersExample = new UsersExample();    if (StringUtils.isNotEmpty(key)) {      usersExample.or().andAddressLike(key);      usersExample.or().andHobbyLike(key);    	}    if (StringUtils.isNotEmpty(name)) {      if (usersExample.getOredCriteria().size() == 0){        usersExample.createCriteria();      	}      usersExample.getOredCriteria().get(0).andNameEqualTo(name);    	}    List<Users> users = usersMapper.selectByExampleWithBLOBs(usersExample);    return users;  	}	}

##
##key可以匹配address或者hobby，而name必须要匹配name，也就是希望构造这样的一条查询SQLselect * from users where (address like "%sport%" or hobby like "%sport%") and name = "leesf"。

##
##启动WebServer，访问http://localhost:8081/users/listUsers?key=sport&amp;name=leesf。

##
##结果如下{    result_code: "0",    result_msg: "Succeed!",    result_content: []	}

##
##可以看到访问结果中result_content为空，查看运行日志，发现如下SQL语句	select id, name, address, hobby , content from users WHERE ( address like ? and name = ? ) or( hobby like ? ) 

##
##程序实际构造的SQL并非之前所想的那样，此时查阅资料，发现MyBatis自动生成代码还不支持纯生的(a or b) and c 这样的SQL语句，需要进行等价变化，即(a or b) and c = (a and c) or (b and c)，具体可查看如下链接，按照这样的思路进行如下修改。  public List<Users> getUsers(String name, String key) {    UsersExample usersExample = new UsersExample();    if (StringUtils.isNotEmpty(key)) {      usersExample.or().andAddressLike(key);      usersExample.or().andHobbyLike(key);    	}    if (StringUtils.isNotEmpty(name)){      if (usersExample.getOredCriteria().size() == 0){        usersExample.createCriteria();      	}      usersExample.getOredCriteria().get(0).andNameEqualTo(name);      usersExample.getOredCriteria().get(1).andNameEqualTo(name);    	}    List<Users> users = usersMapper.selectByExampleWithBLOBs(usersExample);    return users;  	}

##
##此时，再次查询，发现还是没有结果，查看运行时信息发现如下SQL。

##
##select id, name, address, hobby , content from users WHERE ( address like ? and name = ? ) or( hobby like ? and name = ? )，看似SQL语句没有任何问题，但是就是出不来结果，like和前面也是一样的，百思不得其解，继续查阅资料也无解，后面尝试对like添加%处理，修改如下。  public List<Users> getUsers(String name, String key) {    UsersExample usersExample = new UsersExample();    if (StringUtils.isNotEmpty(key)) {      usersExample.or().andAddressLike("%" + key + "%");      usersExample.or().andHobbyLike("%" + key + "%");    	}    if (StringUtils.isNotEmpty(name)) {      if (usersExample.getOredCriteria().size() == 0){        usersExample.createCriteria();      	}      usersExample.getOredCriteria().get(0).andNameEqualTo(name);      usersExample.getOredCriteria().get(1).andNameEqualTo(name);    	}    List<Users> users = usersMapper.selectByExampleWithBLOBs(usersExample);    return users;  	}

##
##重新运行并访问url，得到如下结果：{    result_code: "0",    result_msg: "Succeed!",    result_content: [{        id: 1,        name: "leesf",        address: "hubei",        hobby: "sport, race",        content: "he is a boy"    	}]	}

##
##在配合or使用的情况下，like必须显示添加%才能生效，虽然按照这种等价的方式可以进行处理，还是有些麻烦，特别是当or字段非常多的时候，处理比较麻烦，如(a or b or c or d) and e，其需要处理成(a and e) or (b and e) or (c and e) or (d and e)，继续查阅资料，看是否有更为简便的写法，在stackoverflow上发现有这样的处理方式，进行如下改造。  public List<Users> getUsers(String name, String key) {    UsersExample usersExample = new UsersExample();    if (StringUtils.isNotEmpty(key)) {      Map<String, String> maps = new HashMap<String, String>();      maps.put("address", key);      maps.put("hobby", key);      usersExample.createCriteria().multiColumnOrLike(maps);    	}    if (StringUtils.isNotEmpty(name)) {      if (usersExample.getOredCriteria().size() == 0){        usersExample.createCriteria();      	}      usersExample.getOredCriteria().get(0).andNameEqualTo(name);    	}    List<Users> users = usersMapper.selectByExampleWithBLOBs(usersExample);    return users;  	}

##
##修改UserExample.java的Criteria如下。    public static class Criteria extends GeneratedCriteria {        protected Criteria() {            super();        	}        public Criteria multiColumnOrLike(Map<String, String> maps) {            StringBuffer stringBuffer = new StringBuffer();            stringBuffer.append("( ");            for (Map.Entry<String, String> entry : maps.entrySet()) {                stringBuffer.append(entry.getKey());                stringBuffer.append(" like ");                stringBuffer.append("\"%");                stringBuffer.append(entry.getValue());                stringBuffer.append("%\"");                stringBuffer.append(" or ");            	}            int index = stringBuffer.lastIndexOf("or");            stringBuffer.delete(index, stringBuffer.length());            stringBuffer.append(")");            addCriterion(stringBuffer.toString());            return this;        	}    	}

##
##再次启动运行，结果如下。{    result_code: "0",    result_msg: "Succeed!",    result_content: [{        id: 1,        name: "leesf",        address: "hubei",        hobby: "sport, race",        content: "he is a boy"    	}]	}总结

##
##可以看到使用MyBatisGenerator自动生成代码时，需要注意如下可能出现的坑。当进行(a or b) and c查询时，可通过转变为(a and c) or (b and c)方式进行查询，但个人认为更好的方法是修改Example文件，进行定制化的查询处理。单独使用andxxxLike时，不需要添加"%"处理，而配合or时，必须添加"%"才行。