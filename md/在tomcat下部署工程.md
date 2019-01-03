xx系统第一期工程完成，今天老大要我去部署系统，从来就没有在tomcat下部署过，一直都是在myeclipse下部署、启动、运行即可，所以这次遇到了几个问题，记录下来。

## tomcat启动

在安装tomcat后，配置好环境变量，双击tomcat\bin路径下的startup.bat，并没有出现我预期的命令框，而是一闪而过。这里肯定有错，至于是什么错误我还不知道，所以cmd命令启动报如下错误：

The CATALINA_HOME enviernment variable is not defined correctly  
This environment variable is needed to run this program  
大致的意思就是说运行这个程序需要的环境变量CATALINA_HOME没有定义。对于这个CATALINA_HOME是什么东东我还真的木有遇到过，百度一把：原来在Tomcat
4.0以后采用了新的Servlet容器Catalina，所以很显然CATALINA_HOME是tomcat运行时的环境变量，类似于JAVA_HOME。所以在环境变量中配置CATALINA_HOME=”
D:\tomcat-6.0.29\tomcat-6.0.29”，该值为tomcat的解压(安装)路劲。  
重新启动tomcat即可。

> **总结： 在启动tomcat时我们配置的环境变量应该包括如下几个：JAVA_HOME、classpath、Path、CATALINA_HOME。  
> **

## 在tomcat下部署项目

在tomcat下部署项目主要有如下三种方式：  
**第一种：**
直接拷贝。将项目下的WebRoot文件夹复制到$CATALINA_HOME\webapps路劲下，命名为qyzygl，启动服务即可，这种方式非常简单，也是想我这样的初学者经常用到的方式。访问地址如下：

[http://localhost:8080/qyzygl](http://localhost:8080/qyzygl)  
**第二种：**
这种方式并不需要将项目拷贝到webapps路径下，可以直接F:/路径下部署。方法如下：更改$CATALINA_HOME\conf\server.xml文件，在<host>标签内添加<Context>标签，内容如下：<Context
docBase="D:/creator/workspace/qyzygl/WebRoot" reloadable="false" path="/
qyzygl
"/>。其中reloadable="false"表示当应用程序中的内容发生更改之后服务器不会自动加载，这个属性在开发阶段通常都设为true，方便开发，在发布阶段应该设置为false，提高应用程序的访问速度。docBase为路径，可以使用绝对路径，也可以使用相对路径，相对路径相对于webapps。
path属性的值是访问时的根地址。访问地址如下：[http://localhost:8080/qyzygl](http://localhost:8080/qyzygl)  
**第三种：**
CATALINA_HOME\conf\Catalina\localhost中添加一个xml文件，如qyzygl.xml，内容如下：<Context
docBase="F:/qyzygl" reloadable="false"
/>大家可能发现和第二种方式差不多，但是缺少了path属性，这种方式服务器会使用.xml的名字作为path属性的值。访问地址如下：[http://localhost:8080/qyzygl/](http://localhost:8080/qyzygl/)  
**第四种：** 使用.war文件包  
其实前面三种我们一直都是将qyzygl文件部署在服务器中，其实我们可以将应用程序打包成.war包，然后再部署在服务器上。打包步骤如下：  
打开cmd命令提示符。  
在命令提示框中进入D:/creator/workspace/qyzygl文件中，然后输入如下命令：jar cvf qyzygl.war
*/.然后提示框会出现非常多的类似于xxx写入之类的，这个过程就是在将qyzygl文件中的内容打包成.war文件，完成之后会在该目录下生成qyzygl.war文件。  
部署.war文件非常简单，将.war文件拷贝到webapps文件路径下或者将docBase=”
D:/creator/workspace/qyzygl/WebRoot”更改为docBase="F:\qyzygl.war"即可。重写启动服务就可以完成部署了。  

