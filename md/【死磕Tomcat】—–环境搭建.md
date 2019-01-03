  * 1 前言
  * 2 上传源码

> 原文作者：黄晓峰  
>  原文链接：<https://blog.csdn.net/dwade_mia/article/details/79051370>

## 前言

  * 为什么要学习tomcat源码？

tomcat是目前非常流行的web容器，其性能和稳定性也是非常出色的，学习其框架设计和底层的实现，不管是使用、性能调优，还是应用框架设计方面，肯定会有很大的帮助

  * tomcat版本

该系列博客的tomcat版本是8.5.24

**下载源码**

从apache官网下载tomcat源码包，本人以8.5.24版本为例，<http://tomcat.apache.org/download-80.cgi>

**maven**

本人习惯使用maven，因此将源码转成maven工程。新建pom.xml，加入相关依赖，如附录所示

**导入开发工具**

导入maven项目，因为有些测试类依赖了examples目录的类，因此把`apache-
tomcat-8.5.24-src\webapps\examples\WEB-INF\classes`目录在开发工具上面设置为java源文件，编译的
class 输出目录设为 classes ，如下图所示

![20180102005200018](https://gitee.com/chenssy/blog-
home/raw/master/image/201809/20180102005200018.png)

## 上传源码

在看源码过程中经常需要对源码进行注释，建议大家把源码上传至自己的git，方便后续查漏补缺。tips:在.gitignore文件需要忽略target目录(class文件输出目录)

附上本人的码云地址，`git@gitee.com:bestkobe/tomcat.git`

**附录**

pom.xml

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
        <modelVersion>4.0.0</modelVersion>
        <groupId>org.apache</groupId>
        <artifactId>tomcat</artifactId>
        <name>apache-tomcat-8.5.24</name>
        <version>8.5.24</version>
    
        <build>
            <finalName>Tomcat-8.5.24</finalName>
            <sourceDirectory>java</sourceDirectory>
            <testSourceDirectory>test</testSourceDirectory>
            <resources>
                <resource>
                    <directory>java</directory>
                </resource>
            </resources>
            <testResources>
                <testResource>
                    <directory>test</directory>
                </testResource>
            </testResources>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.5.1</version>
                    <configuration>
                        <encoding>UTF-8</encoding>
                        <source>1.8</source>
                        <target>1.8</target>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    
        <dependencies>
            <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>4.12</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.easymock</groupId>
                <artifactId>easymock</artifactId>
                <version>3.4</version>
                <scope>test</scope>
            </dependency>
    
            <dependency>
                <groupId>org.apache.ant</groupId>
                <artifactId>ant</artifactId>
                <version>1.10.0</version>
            </dependency>
            <dependency>
                <groupId>wsdl4j</groupId>
                <artifactId>wsdl4j</artifactId>
                <version>1.6.2</version>
            </dependency>
            <dependency>
                <groupId>javax.xml</groupId>
                <artifactId>jaxrpc</artifactId>
                <version>1.1</version>
            </dependency>
            <dependency>
                <groupId>org.eclipse.jdt.core.compiler</groupId>
                <artifactId>ecj</artifactId>
                <version>4.6.1</version>
            </dependency>
        </dependencies>
    </project>
    

