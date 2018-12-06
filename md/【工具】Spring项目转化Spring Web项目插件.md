##【工具】Spring项目转化Spring Web项目插件前言

##
##源于前一篇博文中提到，将Spring项目转化为Spring Web项目，发现添加项目文件和修改pom.xml文件等都是手动完成的，心想着开发一个Idea插件来自动化完成上面的过程，实现一键转化。思路记录手动完成转化时需要的步骤。修改pom.xml文件，如添加<packaging>war</packaging>和spring web的依赖。在指定文件夹下添加web.xml文件，并写入数据。使用程序自动化完成各步骤。

##
##由于项目中的web.mxl文件内容一定(模版)，所以对于项目中web.xml的创建和写入，步骤如下。首先在本地先创建web.xml模版，添加内容，并上传至cnblogs，获取url地址。在项目的src/main/webapp/WEB-INF/目录下创建web.xml文件。使用HttpClient访问url地址获取内容后写入web.xml中。

##
##对于pom.xml文件的修改而言，步骤如下。与web.xml相同，现在本地创建pom.xml模版，添加内容，并上传至cnblogs，获取url地址。读取项目的pom.xml文件，并进行解析。判断是否存在<packaging>元素，若不存在，或者存在且内容不为war，则添加<packaging>war</packaging>元素。技术点

##
##该插件涉及到的技术点如下。Idea插件开发流程。HttpClient使用。XML文件的操作。源码

##
##源码逻辑结构较为简单，所有源码也已经放置在Github上。欢迎Fork And Star

##
##点击访问源码总结

##
##当发现一些比较机械的事情时，不妨试着思考可否通过程序解决，技术让生活更美好。其实后来发现可以直接在File -> Project Structure -> Facets中添加Web模块，不管如何，就当熟悉了idea插件开发的流程。