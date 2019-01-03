最近，开源社区发生了一件大事，那个全国 Java 开发者使用最广的开源服务框架 Dubbo 低调重启维护，并且 3 个月连续发布了 4 个维护版本。

我上次在写[放弃Dubbo，选择最流行的Spring
Cloud微服务架构实践与经验总结](http://mp.weixin.qq.com/s/bciSlKearaVFQg1QWOSn_g)这篇文章的时候，就有很多的网友给我留言说，Dubbo
又开始更新了。我当然是清楚的，我也一直在关注着 Dubbo 的走向，在几个月前技术圈里面就有一个消息说是 Dubbo
又开始更新了，大家议论纷纷不知真伪。我还专门跑到 GitHub 上面进行了留言询问，最后在 Dubbo 的 gitter
聊天室里面找到了确信的答案，说是正在组建团队。虽然稍稍有所期待，但也不知道阿里这次拿出了多少的诚意来做这件事，于是我昨天又到 GitHub 逛了一下，发现从
9 月开始，阿里三个月连着发布了四个版本，还是非常有诚意的，值得关注。

  

## Dubbo简介

Dubbo 是阿里巴巴公司一个开源的高性能服务框架，致力于提供高性能和透明化的 RPC 远程服务调用方案，以及 SOA 服务治理方案，使得应用可通过高性能
RPC 实现服务的输出、输入功能和 Spring 框架无缝集成。Dubbo 包含远程通讯、集群容错和自动发现三个核心部分。

它提供透明化的远程方法调用，实现像调用本地方法一样调用远程方法，只需简单配置，没有任何 API 侵入。同时它具备软负载均衡及容错机制，可在内网替代 F5
等硬件负载均衡器，降低成本，减少单点。它可以实现服务自动注册与发现，不再需要写死服务提供方地址，注册中心基于接口名查询服务提供者的 IP
地址，并且能够平滑添加或删除服务提供者。

2011 年末，阿里巴巴在 GitHub 上开源了基于 Java 的分布式服务治理框架
Dubbo，之后它成为了国内该类开源项目的佼佼者，许多开发者对其表示青睐。同时，先后有不少公司在实践中基于 Dubbo 进行分布式系统架构。目前在
GitHub 上，它的 fork、star 数均已破万。

**Dubbo核心功能** :

  * 远程通讯，提供对多种基于长连接的 NIO 框架抽象封装，包括多种线程模型，序列化，以及“请求-响应”模式的信息交换方式。
  * 集群容错，提供基于接口方法的透明远程过程调用，包括多协议支持，以及软负载均衡，失败容错，地址路由，动态配置等集群支持。
  * 自动发现，基于注册中心目录服务，使服务消费方能动态的查找服务提供方，使地址透明，使服务提供方可以平滑增加或减少机器。

![](../md/img/ityouknow/dubbo-architecture.png)

  

## Dubbo发展史

  
  
**发展到开源**

2008 年底在阿里内部开始规划调用，2009 年初开发 1.0 版本；2010 年 04 月在 1.0 的版本之上进行了重构，发布了 2.0
版本；2011 年 10 月阿里宣布将 Dubbo 开源，开源的第一个版本为版本 **dubbo-2.0.7** 。  
  
  
**开源成长**

Dubbo 开源之后，框架发展比较迅速，几乎两三个月会发布一个版本，于 2012 年 3 月 14 号发布版本
dubbo-2.1.0。随后又进入另一个快速发展期，版本发布频繁，几乎每一个月会发布好几次。直到 2013 年 3 月 17 号发布了
dubbo-2.4.10，版本陷入停滞；2014 年 10 月 30 号发布版本 dubbo-2.4.11，修复了一个小
Bug，版本又陷入漫长的停滞到现在。  
  
  
**阿里之外的发展**

2014 年的 10 月 20 号，当当网 Fork 了阿里的一个 Dubbo 版本开始维护，并命名为 dubbox-2.8.0。值得注意的是，当当网扩展
Dubbo 服务框架支持 REST 风格远程调用，并且跟随着 ZooKeepe 和 Spring 升级了对应的版本。之后 Dubbox
一直在小版本维护，2015 年 3 月 31 号发布了最后一个版本 **dubbox-2.8.4** 。

![](../md/img/ityouknow/dubbox_rest.jpg)  
  

## Dubbo团队这三个月都做了什么

目前 Dubbo 的主力开发以阿里巴巴中间件团队为主，同时在阿里内部也招募了一些对 Dubbo 感兴趣的同事。大家要知道，Dubbo
距离今年开始维护的上一个版本是什么时间发布的吗？是 2014 年 10 月 30 号，差了整整将近 3 年，Dubbo 所依赖的
Jdk、Spring、Zookeeper、Zkclient 等等不知道都更新了多少个版本。因此阿里恢复更新的第一步就是适配所依赖的各组件版本，让 Dubbo
所依赖的基础环境不要太落伍，另外也 Fixed 掉了一些严重的 Bug。  
  
  
**dubbo-2.5.4/5版本**

2017 年 9 月，阿里发布了 dubbo-2.5.4/5 版本，更新内容如下：

**依赖升级**  
  
<table>  
<tr>  
<th>

依赖

</th>  
<th>

当前版本

</th>  
<th>

目标版本

</th>  
<th>

影响点

</th> </tr>  
<tr>  
<td>

spring

</td>  
<td>

3.2.16.RELEASE

</td>  
<td>

4.3.10.RELEASE

</td>  
<td>

schema配置解析；Http RPC协议

</td> </tr>  
<tr>  
<td>

zookeeper

</td>  
<td>

3.3.3

</td>  
<td>

3.4.9

</td>  
<td>

常用注册中心

</td> </tr>  
<tr>  
<td>

zkclient

</td>  
<td>

0.1 0.10

</td>  
<td>

zookeeper

</td>  
<td>

客户端工具

</td> </tr>  
<tr>  
<td>

curator

</td>  
<td>

1.1.16

</td>  
<td>

2.12.0

</td>  
<td>

zookeeper客户端工具

</td> </tr>  
<tr>  
<td>

commons-logging

</td>  
<td>

1.1.1

</td>  
<td>

1.2

</td>  
<td>

日志实现集成

</td> </tr>  
<tr>  
<td>

hessian

</td>  
<td>

4.0.6

</td>  
<td>

4.0.38

</td>  
<td>

hessian RPC协议

</td> </tr>  
<tr>  
<td>

jedis

</td>  
<td>

2.1.0

</td>  
<td>

2.9.0

</td>  
<td>

redis注册中心；缓存RPC

</td> </tr>  
<tr>  
<td>

httpclient

</td>  
<td>

4.1.2

</td>  
<td>

4.5.3

</td>  
<td>

hessian等用http连接池

</td> </tr>  
<tr>  
<td>

validator

</td>  
<td>

1.0.0

</td>  
<td>

1.1.0.Final

</td>  
<td>

java validation规范

</td> </tr>  
<tr>  
<td>

cxf

</td>  
<td>

2.6.1

</td>  
<td>

3.0.14

</td>  
<td>

webservice

</td> </tr>  
<tr>  
<td>

jcache

</td>  
<td>

0.4

</td>  
<td>

1.0.0

</td>  
<td>

jcache规范

</td> </tr> </table>

这版在升级相关依赖版本的同时，以问题反馈频率和影响面排定优先级，优先解决了几个反馈最多、影响较大的一些缺陷，包括优雅停机、异步调用、动态配置、MonitorFilter
监控统计等问题。

  
  
**dubbo-2.5.6版本**

2017 年 10 月，阿里发布了 dubbo-2.5.6 版本，又 Fixed 掉了一大批严重的 Bug。

**发布内容**

  * 泛化调用PojoUtils工具类不能正确处理枚举类型、私有字段等问题
  * provider业务线程池满后，拒绝请求的异常无法通知到consumer端
  * 业务返回值payload超阈值时，payload被重复发送回consumer
  * slf4jLogger正确输出log调用实际所在行号
  * 延迟(delay)暴露存在潜在并发问题，导致不同服务占用多个端口
  * 无provider时，consumer端mock逻辑不能生效
  * 一些小优化：OverrideListener监听逻辑、provider端关闭心跳请求、Main启动类停机逻辑等
  * 一些小bug修复：动态配置不能删除、telnet支持泛型json调用、monitor统计错误等  
  
  
**dubbo-2.5.7版本**

2017 年 11 月，也就是 12 天前，阿里发布了 dubbo-2.5.7。这次不但修复了一批主要的 Bug，还做了一处小功能的完善。

**发布内容**

  * 完善注解配置方式，修复社区反馈的旧版注解bug
  * 支持启动时从环境变量读取注册ip port、绑定ip port，支持社区反馈的容器化部署场景等
  * 调整、开放一些不完善的xml配置项，如dump.directory等
  * 解决启动阶段zk无法连接导致应用无限阻塞的问题
  * 解决zk无法连接时，MonitorService初次访问会导致rpc请求阻塞问题 #672
  * 内部json实现标记deprecate，转为依赖开源fastjson实现
  * RMI协议支持传递attachments
  * Hessian支持EnumSet类型序列化
  * 社区反馈的一些小bug修复及优化

这次版本发布内容较多，因此还给出了升级建议。  
  
  
**升级请注意**

  * 此次升级存在以下不兼容或需要注意点，但对核心功能均无影响，且只需添加依赖或遵守配置规则即可避免。这里只是把潜在的注意点列出来，如果你没用到这些功能无需额外关注。  

  * AccesslogFilter、telnet、mock等部分功能依赖了老版JSON实现，如开启以上功能，升级后请添加fastjson作为第三方依赖。
  * 此次升级完善了注解配置方式，同时保留了老的注解配置代码，如工程从之前的老版本注解配置转到2.5.7版本，请确保删除老的注解扫描配置，使用新的配置形式。
  * 在工程启动阶段，如遇到zk不可达，当前版本的行为是使用注册中心缓存继续启动（具体由check参数决定。  
MonitorService初次调用，如遇zk不可达，当前版本会忽略monitor数据上传，以避免阻塞rpc主流程。  
  
  
**重点**

在 2.5.7 版本更新的同时还给出了下一步的预告，近期即将提供 dubbo-spring-boot-starter 启动配置模块。

这个提示说明了两个事情：

  * Dubbo 还会继续完善，后续会开发很多的新的功能，所以希望大家关注。
  * 说明 Spring Boot 的影响力也越来越大，各种牛逼的开源软件纷纷给出了支持，现在也将包括 Dubbo。  
  

## Dubbo 下一步会做什么？

  
  
**根据阿里技术的信息，最近三个版本会做的事情如下：**

  * 优先解决社区使用过程中的问题和框架的缺陷，吸收社区贡献的新特性，解决文档访问和不全面的问题。  

  * 提供服务延迟暴乱、优雅停机 API 接口支持 RESTFULE 风格服务调用，提供 netty http 的支持，集成高性能序列化协议。  

  * 路由功能优化、消费端异步功能优化、提供端异步调用支持注册中心推送通知异步、合并处理改造等。  
  
  
**未来计划** ：

重构动态配置模块，动态配置和注册中心分离，集成流行的开源分布式配置管理框架，服务元数据注册与注册中心分离，丰富元数据内容，适配流行的 consul etcd
等注册中心方案。考虑提供 opentrace、oauth2、metrics、health、gateway 等部分服务化基础组件的支持，服务治理平台 OPS
重做，除代码、UI 重构外，期望能提供更强的服务测试、健康检查、服务动态治理等特性。Dubbo
模块化，各个模块可单独打包、单独依赖，集群熔断和自动故障检测能力。

继续在 Dubbo 框架现代化、国际化这两个大的方向上进行探索。现代化方面主要是考虑到目前微服务架构以及容器化日渐流行的大趋势，Dubbo 作为 RPC
框架如何很好地融入其中，成为其生态体系中不可或缺的一个组件。 **强调的是 Dubbo 未来的定位并不是要成为一个微服务的全面解决方案，而是专注在 RPC
领域，成为微服务生态体系中的一个重要组件。** 至于大家关注的微服务化衍生出的服务治理需求， Dubbo
将积极适配开源解决方案，甚至启动独立的开源项目予以支持。  
  

## Dubbo和Spring Cloud有何不同？

首先做一个简单的功能对比：  
  
<table>  
<tr>  
<th>

</th>  
<th>

Dubbo

</th>  
<th>

Spring Cloud

</th> </tr>  
<tr>  
<td>

服务注册中心

</td>  
<td>

Zookeeper

</td>  
<td>

Spring Cloud Netflix Eureka

</td> </tr>  
<tr>  
<td>

服务调用方式

</td>  
<td>

RPC

</td>  
<td>

REST API

</td> </tr>  
<tr>  
<td>

服务监控

</td>  
<td>

Dubbo-monitor

</td>  
<td>

Spring Boot Admin

</td> </tr>  
<tr>  
<td>

断路器

</td>  
<td>

不完善

</td>  
<td>

Spring Cloud Netflix Hystrix

</td> </tr>  
<tr>  
<td>

服务网关

</td>  
<td>

无

</td>  
<td>

Spring Cloud Netflix Zuul

</td> </tr>  
<tr>  
<td>

分布式配置

</td>  
<td>

无

</td>  
<td>

Spring Cloud Config

</td> </tr>  
<tr>  
<td>

服务跟踪

</td>  
<td>

无

</td>  
<td>

Spring Cloud Sleuth

</td> </tr>  
<tr>  
<td>

消息总线

</td>  
<td>

无

</td>  
<td>

Spring Cloud Bus

</td> </tr>  
<tr>  
<td>

数据流

</td>  
<td>

无

</td>  
<td>

Spring Cloud Stream

</td> </tr>  
<tr>  
<td>

批量任务

</td>  
<td>

无

</td>  
<td>

Spring Cloud Task

</td> </tr>  
<tr>  
<td>

……

</td>  
<td>

……

</td>  
<td>

……

</td> </tr> </table>

  
  
**从上图可以看出其实Dubbo的功能只是Spring Cloud体系的一部分。**

这样对比是不够公平的，首先 Dubbo 是 SOA 时代的产物，它的关注点主要在于服务的调用，流量分发、流量监控和熔断。而 Spring Cloud
诞生于微服务架构时代，考虑的是微服务治理的方方面面，另外由于依托了 Spirng、Spirng Boot 的优势之上，两个框架在开始目标就不一致，Dubbo
定位服务治理、Spirng Cloud 是一个生态。  
  
  
**如果仅仅关注于服务治理的这个层面，Dubbo其实还优于Spring Cloud很多：**

  * Dubbo 支持更多的协议，如：rmi、hessian、http、webservice、thrift、memcached、redis 等。  

  * Dubbo 使用 RPC 协议效率更高，在极端压力测试下，Dubbo 的效率会高于 Spring Cloud 效率一倍多。  

  * Dubbo 有更强大的后台管理，Dubbo 提供的后台管理 Dubbo Admin 功能强大，提供了路由规则、动态配置、访问控制、权重调节、均衡负载等诸多强大的功能。  

  * 可以限制某个 IP 流量的访问权限，设置不同服务器分发不同的流量权重，并且支持多种算法，利用这些功能我们可以在线上做灰度发布、故障转移等，Spring Cloud 到现在还不支持灰度发布、流量权重等功能。

![](../md/img/ityouknow/dubbo_admin.png)

**所以Dubbo专注于服务治理；Spring Cloud关注于微服务架构生态。**  
  

## Dubbo发布对Spring Cloud有影响吗？

国内技术人喜欢拿 Dubbo 和 Spring Cloud 进行对比，是因为两者都是服务治理非常优秀的开源框架。但它们两者的出发点是不一样的，Dubbo
关注于服务治理这块并且以后也会继续往这个方向去发展。Spring Cloud
关注的是微服务治理的生态。因为微服务治理的方方面面都是它所关注的内容，服务治理也只是微服务生态的一部分而已。因此可以大胆的断定，Dubbo
未来会在服务治理方面更为出色，而 Spring Cloud 在微服务治理上面无人能敌。

同时根据 Dubbo 最新的更新技术来看，Dubbo 也会积极的拥抱开源，拥抱新技术。Dubbo 接下来的版本将会很快的支持 Spring
Boot，方便我们享受高效开发的同时，也可以支持高效的服务调用。Dubbo
被广泛应用于中国各互联网公司，如今阿里又重新重视起来并且发布了新版本和一系列的计划，对于正在使用 Dubbo
的公司来说是一个喜讯，对于中国广大的开发者来说更是一件非常喜悦的事情。我们非常乐于看到中国有一款非常优秀的开源框架，让我们有更多的选择，有更好的支持。

**两者其实不一定有竞争关系，如果使用得当甚至可以互补；另外两个关注的领域也不一致，因此对 Spring Cloud 的影响甚微。**

  

## 如何选择？

可能很多人正在犹豫，在服务治理的时候应该选择那个框架呢？如果公司对效率有极高的要求建议使用 Dubbo，相对比 RPC 的效率会比 HTTP
高很多；如果团队不想对技术架构做大的改造建议使用 Dubbo，Dubbo
仅仅需要少量的修改就可以融入到内部系统的架构中。但如果技术团队喜欢挑战新技术，建议选择 Spring Cloud，Spring Cloud
架构体系有有趣很酷的技术。如果公司选择微服务架构去重构整个技术体系，那么 Spring Cloud 是当仁不让之选，它可以说是目前最好的微服务框架没有之一。

最后，技术选型是一个综合的问题，需要考虑团队的情况、业务的发展以及公司的产品特征。最炫最酷的技术并不一定是最好的，选择适合自己团队、符合公司业务的框架才是最佳方案。技术的发展永远没有尽头，因此我们对技术也要保持空杯、保持饥饿、保持敬畏！

原文出处[阿里Dubbo疯狂更新，关Spring
Cloud什么事？](http://mp.weixin.qq.com/s/aYlHAXNbwiXq7DPFOYTK6A)

