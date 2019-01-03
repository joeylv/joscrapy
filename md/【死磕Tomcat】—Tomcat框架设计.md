  * 1 Server
  * 2 Service
  * 3 Connector
  * 4 Container
    * 4.1 Host
    * 4.2 Context
  * 5 代码模块简介
  * 6 参考资料

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79051404>

tomcat的总体架构如下图所示（摘自<http://blog.csdn.net/jiaomingliang/article/details/47393141>

![image](https://gitee.com/chenssy/blog-home/raw  
/master/image/201809/20180809011001.png)

如上图所示，tomcat由Server、Service、Engine、Connerctor、Host、Context组件组成，其中带有s的代表在一个tomcat实例上可以存在多个组件，比如Context(s)，tomcat允许我们部署多个应用，每个应用对应一个Context。这些组件在tomcat的conf/server.xml文件中可以找到，对tomcat的调优需要改动该文件

    
    
    server.xml
    <Service name="Catalina">
        <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" />
    
        <Connector port="8080" protocol="HTTP/1.1"
                   connectionTimeout="20000"
                   redirectPort="8443" />
    
        <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
    
        <Engine name="Catalina" defaultHost="localhost">
          <Realm className="org.apache.catalina.realm.LockOutRealm">
            <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
                   resourceName="UserDatabase"/>
          </Realm>
          <Host name="localhost"  appBase="webapps"
                unpackWARs="true" autoDeploy="true">
            <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
                   prefix="localhost_access_log" suffix=".txt"
                   pattern="%h %l %u %t "%r" %s %b" />
          </Host>
        </Engine>
    </Service>
    

## Server

![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180809011002.png)

Serve r组件对应org.apache.catalina.Server接口，类图如上所示。

  * Server继承至LifeCycle，LifeCycle是一个非常重要的接口，各大组件都继承了这个接口，用于管理tomcat的生命周期，比如init、start、stop、destory；另外，它使用了观察者模式，LifeCycle是一个监听者，它会向注册的LifecycleListener观察者发出各种事件 
  * Server提供了findService、getCatalina、getCatalinaHome、getCatalinaBase等接口，支持查找、遍历Service组件，这里似乎看到了和Serivce组件的些许联系

    
    
    public interface Server extends Lifecycle {
    
        public NamingResourcesImpl getGlobalNamingResources();
    
        public void setGlobalNamingResources(NamingResourcesImpl globalNamingResources);
    
        public javax.naming.Context getGlobalNamingContext();
    
        public int getPort();
    
        public void setPort(int port);
    
        public String getAddress();
    
        public void setAddress(String address);
    
        public String getShutdown();
    
        public void setShutdown(String shutdown);
    
        public ClassLoader getParentClassLoader();
    
        public void setParentClassLoader(ClassLoader parent);
    
        public Catalina getCatalina();
    
        public void setCatalina(Catalina catalina);
    
        public File getCatalinaBase();
    
        public void setCatalinaBase(File catalinaBase);
    
        public File getCatalinaHome();
    
        public void setCatalinaHome(File catalinaHome);
    
        public void await();
    
        public Service findService(String name);
    
        public Service[] findServices();
    
        public void removeService(Service service);
    
        public Object getNamingToken();
    }
    

## Service

Service的默认实现类是StardardService，类结构和StardardServer很相似，也是继承至LifecycleMBeanBase，实现了Service接口

由Service接口不难发现Service组件的内部结构

  * 持有Engine实例 
  * 持有Server实例 
  * 可以管理多个Connector实例 
  * 持有Executor引用

    
    
    public class StandardService extends LifecycleMBeanBase implements Service {
        // 省略若干代码
    }
    
    public interface Service extends Lifecycle {
    
        public Engine getContainer();
    
        public void setContainer(Engine engine);
    
        public String getName();
    
        public void setName(String name);
    
        public Server getServer();
    
        public void setServer(Server server);
    
        public ClassLoader getParentClassLoader();
    
        public void setParentClassLoader(ClassLoader parent);
    
        public String getDomain();
    
        public void addConnector(Connector connector);
    
        public Connector[] findConnectors();
    
        public void removeConnector(Connector connector);
    
        public void addExecutor(Executor ex);
    
        public Executor[] findExecutors();
    
        public Executor getExecutor(String name);
    
        public void removeExecutor(Executor ex);
    
        Mapper getMapper();
    }
    

## Connector

Connector是tomcat中监听TCP端口的组件，server.xml默认定义了两个Connector，分别用于监听http、ajp端口。对应的代码是org.apache.catalina.connector.Connector，它是一个实现类，并且实现了Lifecycle接口

    
    
    <code class="hljs xml has-numbering"><Connector port="8080" protocol="HTTP/1.1"
                   connectionTimeout="20000"
                   redirectPort="8443" /></code>
    

http对应的Connector配置如上所示，其中protocol用于指定http协议的版本，还可以支持2.0；connectionTimeout定义了连接超时时间，单位是毫秒；redirectPort是SSL的重定向端口，它会把请求重定向到8443这个端口

AJP

    
    
    <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
    

Apache
jserver协议(AJP)是一种二进制协议，它可以将来自web服务器的入站请求发送到位于web服务器后的应用服务器。如果我们希望把Tomcat集成到现有的(或新的)Apache
http
server中，并且希望Apache能够处理web应用程序中包含的静态内容，或者使用Apache的SSL处理，我们便可以使用该协议。但是，在实际的项目应用中，AJP协议并不常用，大多数应用场景会使用nginx+tomcat实现负载。

## Container

org.apache.catalina.Container接口定义了容器的api，它是一个处理用户servlet请求并返回对象给web用户的模块，它有四种不同的容器：

  * Engine，表示整个Catalina的servlet引擎 
  * Host，表示一个拥有若干个Context的虚拟主机 
  * Context，表示一个Web应用，一个context包含一个或多个wrapper 
  * Wrapper，表示一个独立的servlet

![Container接口](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180809011003.png)

Engine、Host、Context、Wrapper都有一个默认的实现类StandardXXX，均继承至ContainerBase。此外，一个容器还包含一系列的Lodder、Logger、Manager、Realm和Resources等

一个容器可以有一个或多个低层次上的子容器，并且一个Catalina功能部署并不一定需要全部四种容器。一个Context有一个或多个wrapper，而wrapper作为容器层次中的最底层，不能包含子容器。从一个容器添加到另一容器中可以使用在Container接口中定义的addChild()方法义：

    
    
    public void addChild(Container child);
    
    

删除一个容器可以使用Container接口中定义的removeChild()方法：

    
    
    public void removeChild(Container child);
    

另外容器接口支持子接口查找和获得所有子接口集合的方法findChild和findChildren方法：

    
    
    public Container findChild(String name);
    public Container[] findChildren();
    

Engine

![Engine类图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180809011004.png)

Engine表示Catalina的Servlet引擎，如果使用了Engine的话，则它是Catalina的顶层容器，因此在StardardCataline的setParent()方法中直接抛出的异常

    
    
    public interface Engine extends Container {
    
        public String getDefaultHost();
    
        public void setDefaultHost(String defaultHost);
    
        public String getJvmRoute();
    
        public void setJvmRoute(String jvmRouteId);
    
        public Service getService();
    
        public void setService(Service service);
    }
    
    public class StandardEngine extends ContainerBase implements Engine {
    
        // other code...
    
        public void setParent(Container container) {
            throw new IllegalArgumentException(sm.getString("standardEngine.notParent"));
        }
    }
    

**server.xml**

    
    
    <Engine name="Catalina" defaultHost="localhost">
      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase"/>
      </Realm>
    
      <Host name="localhost" appBase="webapps" unpackWARs="true" autoDeploy="true">
        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t "%r" %s %b" />
      </Host>
    </Engine>
    

###  Host

Host定义了一个虚拟主机，正所谓虚拟主机，当然是可以用来部署应用程序的，Tomcat的Host也是如此。它在server.xml中定义了一个localhost的Host，应用根目录在webapps下面，默认是支持解压重新部署的。

    
    
    <Host name="localhost" appBase="webapps" unpackWARs="true" autoDeploy="true">...</Host>
    

### Context

![Context类图](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180809011005.png)

Context代表一个独立的web应用，针对每个Context，tomcat都是使用不同的Classloader避免类冲突。如果我们希望使用一个自定义的目录作为部署路径的话，可以在server.xml中新增Context即可

    
    
    <Context path="/static" docBase="D:/static" reloadable="true"></Context>
    

## 代码模块简介

**catalina包**

Tomcat的核心模块，包括了HttpServlet、HttpSession的实现，以及各大组件的实现，这块的代码量是最多的，也是最复杂的一部分

**coyote包**

这块主要用于支持各种协议，比如http1.1、http2.0、ajp等，代码量较少

**tomcat包**

tomcat的基础包，包括了数据库连接池、websocket实现、tomcate的jni、工具类。org.apache.tomcat.util包的代码量也不少,其中还包括了对jdk源码的扩展，比如线程池。

下图罗列各个模块的大致用途以及代码量  
![image](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180809011006.png)

## 参考资料

<http://blog.csdn.net/jiaomingliang/article/details/47393141>

