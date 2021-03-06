乱码，我们前台展示的杀手，可能有些朋友和我的经历一样：遇到乱码先按照自己的经验来解决，如果没有解决就google，运气好一搜就可以解决，运气不好可能够你折腾一番了。LZ之所以写这个系列博客就是因为遇到这个令人讨厌的问题，虽然是小问题但又不得不解决。

在这个系列博文中LZ并没有阐述归纳乱码的方法，出现乱码的原因各式各样但根本原因就是编码转换过程中的格式不一样，所以我们只需要了解了java在运行过程中是如何来完成编码和解码的，乱码也许就真不是什么问题了。

在前面三篇博客中LZ说明了各种编码的来由、编码规则，尤其是Unicode编码更是重点阐述。接着两篇是说明java内部是如何来完成编码解码工作的，分三种情况（IO、servlet/JSP、数据库）来阐述编码转换过程。最后就是java产生乱码的重灾区了：javaWeb，在这几篇博客中LZ介绍了URL编码，服务器端是如何来完成了解码工作的，JSP在转换过程中编码情况，URL产生乱码情况总结。

[JAVA中文乱码解决之道（一）-----认识字符集](http://www.cnblogs.com/chenssy/p/4200277.html)

[JAVA中文乱码解决之道（二）-----字符编码详解：基础知识 + ASCII +
GB**](http://www.cnblogs.com/chenssy/p/4202688.html)

[JAVA中文乱码解决之道（三）-----编码详情：伟大的创想---
Unicode编码](http://www.cnblogs.com/chenssy/p/4205130.html)

[java中文乱码解决之道（四）-----java编码转换过程](http://www.cnblogs.com/chenssy/p/4207554.html)

[java中文乱码解决之道（五）-----java是如何编码解码的](http://www.cnblogs.com/chenssy/p/4214835.html)

[Java中文乱码解决之道（六）-----javaWeb中的编码解码](http://www.cnblogs.com/chenssy/p/4220400.html)

[java中文乱码解决之道（七）-----JSP页面编码过程](http://www.cnblogs.com/chenssy/p/4235191.html)

[java中文乱码解决之道（八）-----解决URL中文乱码问题](http://www.cnblogs.com/chenssy/p/4237953.html)

>>>>>>>>>>[文档下载：java乱码解决之道](http://pan.baidu.com/s/1dDnKZNb)

## 推荐阅读：

1、字符编码笔记：ASCII，Unicode和UTF-8：<http://www.ruanyifeng.com/blog/2007/10/ascii_unicode_and_utf-8.html>

2、字符集和字符编码：<http://www.cnblogs.com/skynet/archive/2011/05/03/2035105.html>（[吴秦](http://www.cnblogs.com/skynet/)）

3、Java
编程技术中汉字问题的分析及解决：<http://www.ibm.com/developerworks/cn/java/java_chinese/>

* * *

**\-----原文出自:<http://cmsblogs.com/?p=1530>**[
****](http://cmsblogs.com/?p=1201) **,请尊重作者辛勤劳动成果,转载说明出处.**

**\-----个人站点:**[ **http://cmsblogs.com**](http://cmsblogs.com/)

