## 前言

> 源于前一篇博文中提到，将`Spring`项目转化为`Spring
Web`项目，发现添加项目文件和修改`pom.xml`文件等都是手动完成的，心想着开发一个`Idea`插件来自动化完成上面的过程，实现一键转化。

## 思路

  * 记录手动完成转化时需要的步骤。 
    * 修改`pom.xml`文件，如添加`<packaging>war</packaging>`和`spring web`的依赖。
    * 在指定文件夹下添加`web.xml`文件，并写入数据。
  * 使用程序自动化完成各步骤。

> 由于项目中的`web.mxl`文件内容一定(模版)，所以对于项目中`web.xml`的创建和写入，步骤如下。

  * 首先在本地先创建`web.xml`模版，添加内容，并上传至`cnblogs`，获取`url`地址。
  * 在项目的`src/main/webapp/WEB-INF/`目录下创建`web.xml`文件。
  * 使用`HttpClient`访问`url`地址获取内容后写入`web.xml`中。

> 对于`pom.xml`文件的修改而言，步骤如下。

  * 与`web.xml`相同，现在本地创建`pom.xml`模版，添加内容，并上传至`cnblogs`，获取`url`地址。
  * 读取项目的`pom.xml`文件，并进行解析。
  * 判断是否存在`<packaging>`元素，若不存在，或者存在且内容不为`war`，则添加`<packaging>war</packaging>`元素。
  * 

## 技术点

> 该插件涉及到的技术点如下。

  * `Idea`插件开发流程。
  * `HttpClient`使用。
  * `XML`文件的操作。

## 源码

> 源码逻辑结构较为简单，所有源码也已经放置在`Github`上。欢迎`Fork And Star`

[点击访问源码](https://github.com/leesf/SpringWebConverter)

## 总结

> 当发现一些比较机械的事情时，不妨试着思考可否通过程序解决，技术让生活更美好。其实后来发现可以直接在`File -> Project Structure
-> Facets`中添加`Web`模块，不管如何，就当熟悉了`idea`插件开发的流程。

