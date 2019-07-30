





# ELK+Filebeat搭建实时日志分析平台

`Elasticsearch` `Logstash` `Kibana` `Nginx` `filebeat`

* * *

## ELK Stack 简介

ELK 不是一款软件，而是 Elasticsearch、Logstash 和 Kibana
三种软件产品的首字母缩写。这三者都是开源软件，通常配合使用，而且又先后归于 Elastic.co 公司名下，所以被简称为 ELK Stack。根据
Google Trend 的信息显示，ELK Stack 已经成为目前最流行的集中式日志解决方案。

>   * Elasticsearch：分布式搜索和分析引擎，具有高可伸缩、高可靠和易管理等特点。基于 Apache Lucene
构建，能对大容量的数据进行接近实时的存储、搜索和分析操作。通常被用作某些应用的基础搜索引擎，使其具有复杂的搜索功能；

>   * Logstash：数据收集引擎。它支持动态的从各种数据源搜集数据，并对数据进行过滤、分析、丰富、统一格式等操作，然后存储到用户指定的位置；

>   * Kibana：数据分析和可视化平台。通常与 Elasticsearch 配合使用，对其中数据进行搜索、分析和以统计图表的方式展示；

>   * Filebeat：ELK 协议栈的新成员，一个轻量级开源日志文件数据搜集器，基于 Logstash-Forwarder
源代码开发，是对它的替代。在需要采集日志数据的 server 上安装 Filebeat，并指定日志目录或日志文件后，Filebeat  
>  就能读取数据，迅速发送到 Logstash 进行解析，亦或直接发送到 Elasticsearch 进行集中式存储和分析。

>

## ELK 常用架构及使用场景

### 最简单架构

在这种架构中，只有一个 Logstash、Elasticsearch 和 Kibana 实例。Logstash
通过输入插件从多种数据源（比如日志文件、标准输入 Stdin 等）获取数据，再经过滤插件加工数据，然后经 Elasticsearch 输出插件输出到
Elasticsearch，通过 Kibana 展示。详见图 1。  
图 1. 最简单架构  
![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/image001.png)  
这种架构非常简单，使用场景也有限。初学者可以搭建这个架构，了解 ELK 如何工作。

### Logstash 作为日志搜集器

这种架构是对上面架构的扩展，把一个 Logstash 数据搜集节点扩展到多个，分布于多台机器，将解析好的数据发送到 Elasticsearch server
进行存储，最后在 Kibana 查询、生成日志报表等。详见图 2。  
图 2. Logstash 作为日志搜索器  
![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/image002.png)  
这种结构因为需要在各个服务器上部署 Logstash，而它比较消耗 CPU
和内存资源，所以比较适合计算资源丰富的服务器，否则容易造成服务器性能下降，甚至可能导致无法正常工作。

### Beats 作为日志搜集器

这种架构引入 Beats 作为日志搜集器。目前 Beats 包括四种：

>   * Packetbeat（搜集网络流量数据）；

>   * Topbeat（搜集系统、进程和文件系统级别的 CPU 和内存使用情况等数据）；

>   * Filebeat（搜集文件数据）；

>   * Winlogbeat（搜集 Windows 事件日志数据）。

>

Beats 将搜集到的数据发送到 Logstash，经 Logstash 解析、过滤后，将其发送到 Elasticsearch 存储，并由 Kibana
呈现给用户。详见图 3。

图 3. Beats 作为日志搜集器  
![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/image003.png)

这种架构解决了 Logstash 在各服务器节点上占用系统资源高的问题。相比 Logstash，Beats 所占系统的 CPU
和内存几乎可以忽略不计。另外，Beats 和 Logstash 之间支持 SSL/TLS 加密传输，客户端和服务器双向认证，保证了通信安全。  
因此这种架构适合对数据安全性要求较高，同时各服务器性能比较敏感的场景。

### 引入消息队列机制的架构

这种架构使用 Logstash 从各个数据源搜集数据，然后经消息队列输出插件输出到消息队列中。目前 Logstash 支持
Kafka、Redis、RabbitMQ 等常见消息队列。然后 Logstash 通过消息队列输入插件从队列中获取数据，分析过滤后经输出插件发送到
Elasticsearch，最后通过 Kibana 展示。详见图 4。

图 4. 引入消息队列机制的架构  
![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/image004.png)

这种架构适合于日志规模比较庞大的情况。但由于 Logstash 日志解析节点和 Elasticsearch
的负荷比较重，可将他们配置为集群模式，以分担负荷。引入消息队列，均衡了网络传输，从而降低了网络闭塞，尤其是丢失数据的可能性，但依然存在 Logstash
占用系统资源过多的问题。

### 基于 Filebeat 架构的配置部署详解

前面提到 Filebeat 已经完全替代了 Logstash-Forwarder
成为新一代的日志采集器，同时鉴于它轻量、安全等特点，越来越多人开始使用它。这个章节将详细讲解如何部署基于 Filebeat 的 ELK
集中式日志解决方案，具体架构见图 5。

图 5. 基于 Filebeat 的 ELK 集群架构  
![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/image005.png)

因为免费的 ELK 没有任何安全机制，所以这里使用了 Nginx 作反向代理，避免用户直接访问 Kibana 服务器。加上配置 Nginx
实现简单的用户认证，一定程度上提高安全性。另外，Nginx 本身具有负载均衡的作用，能够提高系统访问性能。

#### Filebeat安装

  1. 下载地址：<https://www.elastic.co/downloads/beats/filebeat>
  2. 编辑filebeat.yml
  3. 启动sudo ./filebeat -e -c filebeat.yml
  4. filebeat input配置介绍

    
          1. filebeat:
      2.     spool_size: 1024                                    # 最大可以攒够 1024 条数据一起发送出去
      3.     idle_timeout: "5s"                                  # 否则每 5 秒钟也得发送一次
      4.     registry_file: ".filebeat"                          # 文件读取位置记录文件，会放在当前工作目录下。所以如果你换一个工作目录执行 filebeat 会导致重复传输！
      5.     config_dir: "path/to/configs/contains/many/yaml"    # 如果配置过长，可以通过目录加载方式拆分配置
      6.     prospectors:                                        # 有相同配置参数的可以归类为一个 prospector
      7.         -
      8.             fields:
      9.                 ownfield: "mac"                         # 类似 logstash 的 add_fields
      10.             paths:
      11.                 - /var/log/system.log                   # 指明读取文件的位置
      12.                 - /var/log/wifi.log
      13.             include_lines: ["^ERR", "^WARN"]            # 只发送包含这些字样的日志
      14.             exclude_lines: ["^OK"]                      # 不发送包含这些字样的日志
      15.         -
      16.             document_type: "apache"                     # 定义写入 ES 时的 _type 值
      17.             ignore_older: "24h"                         # 超过 24 小时没更新内容的文件不再监听。在 windows 上另外有一个配置叫 force_close_files，只要文件名一变化立刻关闭文件句柄，保证文件可以被删除，缺陷是可能会有日志还没读完
      18.             scan_frequency: "10s"                       # 每 10 秒钟扫描一次目录，更新通配符匹配上的文件列表
      19.             tail_files: false                           # 是否从文件末尾开始读取
      20.             harvester_buffer_size: 16384                # 实际读取文件时，每次读取 16384 字节
      21.             backoff: "1s"                               # 每 1 秒检测一次文件是否有新的一行内容需要读取
      22.             paths:
      23.                 - "/var/log/apache/*"                   # 可以使用通配符
      24.             exclude_files: ["/var/log/apache/error.log"]
      25.         -
      26.             input_type: "stdin"                         # 除了 "log"，还有 "stdin"
      27.             multiline:                                  # 多行合并
      28.                 pattern: '^[[:space:]]'
      29.                 negate: false
      30.                 match: after
      31. output:
      32.     ...
    
    

#### Elasticsearch安装

下载地址：<https://www.elastic.co/downloads/elasticsearch>

#### Logstash安装

下载地址：<https://www.elastic.co/downloads/logstash>

#### Kibana安装

下载地址：<https://www.elastic.co/downloads/kibana>

## Kibana视图构建示例及配置

  * 以收集Nginx访问日志为例，我们希望能统计到api接口调用排行，浏览器类型，操作系统类型，http状态分布，响应时间分布。虽然logstash可以通过內建模板解析Nginx日志字符串，不过直接在Nginx配置中直接json字符串最为方便。

### 编辑/usr/local/nginx/conf/nginx.conf

在server节定义json日志格式

    
          1. log_format json '{"@timestamp_local":"$time_iso8601",'
      2.     '"host":"$server_addr",'
      3.     '"clientip":"$remote_addr",'
      4.     '"size":$body_bytes_sent,'
      5.     '"responsetime":$request_time,'
      6.     '"upstreamtime":"$upstream_response_time",'
      7.     '"upstreamhost":"$upstream_addr",'
      8.     '"http_host":"$host",'
      9.     '"url":"$uri",'
      10.     '"type":"newnginx-api",'
      11.     '"request":"$request",'
      12.     '"time_local":"$time_local",'
      13.     '"xff":"$http_x_forwarded_for",'
      14.     '"referer":"$http_referer",'
      15.     '"agent":"$http_user_agent",'
      16.     '"status":"$status"}';
    
    

然后在各网站Nginx配置下指定json模板日志格式

    
          1. access_log  /home/wwwlogs/abc.com.log json;
    
    

重启Nginx，日志格式输出结果示例如下：

    
          1. {"@timestamp_local":"2017-02-23T16:16:19+08:00","host":"192.168.56.10","clientip":"192.168.56.1","size":5,"responsetime":0.085,"upstreamtime":"0.085","upstreamhost":"unix:/tmp/php-cgi.sock","http_host":"www.abc.com","url":"/index.php","type":"newnginx-api","request":"GET / HTTP/1.1","time_local":"23/Feb/2017:16:16:19 +0800","xff":"-","referer":"-","agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36","status":"500"}
    
    

### 编辑filebeat.yml

增加或更新以下配置

    
          1. filebeat.registry_file: ".filebeat"
      2. filebeat.prospectors:
      3. - input_type: log
      4.     paths:
      5.         - /home/wwwlogs/abc.com.log
      6.     tail_files: true #从文件末尾开始读取
      7.     document_type: "newnginx-api"
      8. output.logstash:
      9.     # The Logstash hosts
      10.     hosts: ["localhost:5044"]
    
    

### 编辑logstash.yml

    
          1. input {
      2.     beats {
      3.         port => 5044
      4.         codec => "json"
      5.     }
      6. }
      7. filter {
      8.   9.     grok {
      10.         match => {
      11.             "request" => "\s+(?<api_path>.+?)(\?.*)?\s+"
      12.         }
      13.     }
      14.     grok {
      15.         match => {
      16.             "agent" => "(?<browser>Maxthon|QQBrowser|Chrome|Safari|Firefox|Opera|MSIE?)(/[0-9.]+)?"
      17.         }
      18.     }
      19.     grok {
      20.         match => {
      21.             "agent" => "(?<os>Android|SymbianOS|Macintosh|iPad|iPhone|iPod|Linux|Windows?)"
      22.         }
      23.     }
      24.     mutate {
      25.         split => [ "upstreamtime", "," ]
      26.     }
      27.     mutate {
      28.         convert => [ "upstreamtime", "float" ]
      29.     }
      30.   31. }
      32. output {
      33.     stdout {
      34.         codec => rubydebug
      35.     }
      36.   37.     elasticsearch {
      38.         hosts => ["localhost:9200"]
      39.         index => "%{type}-%{+YYYY.MM.dd}"
      40.         flush_size => 2000
      41.         idle_flush_time => 10
      42.         sniffing => false
      43.         template_overwrite => true
      44.     }
      45. }
    
    

logstash filter主要从日志中提取api_path，os，browser三个字段作为之后排序依据。

### 增加Kibana索引index pattern

> 菜单 -> Management -> Index Patterns -> Add New

我们在filebeat.yml中配置了`document_type: "newnginx-api"`，所以index name
pattern写为`newnginx-api-*`，*表示所有日期的。见图：

![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/kibana_index.png)

### 视图示例配置

#### 1\. 饼图：HTTP状态及响应时间

  * metrics选择Count
  * 第一个buckets以Terms为聚合，选择status字段，order by count，Size填5
  * 第二个bucket以Range为子聚合，选择responsetime字段，from-to指定响应时间范围，比如`0-0.1，0.1-0.2，0.2-0.5，0.5-1，1-2，2-5，5-10`

![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/visualize_status.png)

#### 2\. 直方图：http状态时间轴直方图

  * metrics选择Count
  * buckets X-Axis选择timestamp_local，时间间隔可选择秒，分，小时等
  * buckets Split Bars选择Terms为子聚合，选择status字段，order by term（相当于对status进行group分组）

![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/bar_timestamp.png)

#### 3\. 线形图：所有接口调用数时间曲线图

  * metrics选择Count
  * buckets X-Axis选择Data Histogram（时间片），选择timestamp_local字段，时间间隔可选择秒，分，小时等。

![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/line_apis.png)

#### 4\. 聚合数字：接口调用总数

  * metric 可视化为你选择的聚合显示一个单独的数字。

#### 5\. 直方图：接口调用排行榜

  * metrics选择Count
  * buckets X-Axis选择Terms聚合，选取api_path字段，order by count，size填30（前30调用最高）
  * buckets Split Bars选择Terms子聚合，选取api_path字段，order by count

![此处输入图片的描述](http://lnpan.b0.upaiyun.com/upload/note/bar_api_rank.png)

其他视图配置根据需要选择metrics和buckets。

### Kibana功能简要介绍

#### 可视化类型  
  
<table>  
<tr>  
<th>

类型

</th>  
<th>

用途

</th> </tr>  
<tr>  
<td>

Area chart

</td>  
<td>

用区块图来可视化多个不同序列的总体贡献。

</td> </tr>  
<tr>  
<td>

Data table

</td>  
<td>

用数据表来显示聚合的原始数据。其他可视化可以通过点击底部的方式显示数据表。

</td> </tr>  
<tr>  
<td>

Line chart

</td>  
<td>

用折线图来比较不同序列。

</td> </tr>  
<tr>  
<td>

Markdown widget

</td>  
<td>

用Markdown显示自定义格式的信息或和你仪表盘有关的用法说明。

</td> </tr>  
<tr>  
<td>

Metric

</td>  
<td>

用指标可视化在你仪表盘上显示单个数字。

</td> </tr>  
<tr>  
<td>

Pie chart

</td>  
<td>

用饼图来显示每个来源对总体的贡献。

</td> </tr>  
<tr>  
<td>

Tile map

</td>  
<td>

用瓦片地图将聚合结果和经纬度联系起来。

</td> </tr>  
<tr>  
<td>

Timeseries

</td>  
<td>

计算和展示多个时间序列数据。

</td> </tr>  
<tr>  
<td>

Vertical bar chart

</td>  
<td>

用垂直条形图作为一个通用图形。

</td> </tr> </table>

#### metrics聚合

>   * Count count 聚合返回选中索引模式中元素的原始计数。

>   * Average 这个聚合返回一个数值字段的 average。

>   * Sum sum 聚合返回一个数值字段的总和。

>   * Min min聚合返回一个数值字段的最小值。

>   * Max max 聚合返回一个数值字段的最大值。

>   * Unique Count cardinality 聚合返回一个字段的去重数据值。

>   * Standard Deviation extended stats 聚合返回一个数值字段数据的标准差。

>   * Percentile percentile聚合返回一个数值字段中值的百分比分布。从下拉菜单选择一个字段，然后在 Percentiles
框内指定范围。点击 X 移除一个百分比框，点击+Add 添加一个百分比框。

>   * Percentile Rank percentile ranks聚合返回一个数值字段中你指定值的百分位排名。从下拉菜单选择一个字段，然后在
Values 框内指定一到多个百分位排名值。点击 X移除一个百分比框，点击 +Add 添加一个数值框。

>

#### buckets 聚合

>   * Date Histogram  
>  date histogram基于数值字段创建，由时间组织起来。你可以指定时间片的间隔，单位包括秒，分，小时，天，星期，月，年。

>   * Histogram  
>  标准histogram 基于数值字段创建。为这个字段指定一个整数间隔。勾选 Show empty buckets 让直方图中包含空的间隔。

>   * Range  
>  通过 range 聚合。你可以为一个数值字段指定一系列区间。点击 Add Range 添加一对区间端点。点击红色 (x)符号移除一个区间。

>   * Date Range  
>  date range 聚合计算你指定的时间区间内的值。你可以使用 date math  
>  表达式指定区间。点击 Add Range 添加新的区间端点。点击红色 (/) 符号移除区间。

>   * IPv4 Range  
>  IPv4 range 聚合用来指定 IPv4 地址的区间。点击 Add Range 添加新的区间端点。点击红色 (/) 符号移除区间。

>   * Terms terms  
>  聚合允许你指定展示一个字段的首尾几个元素，排序方式可以是计数或者其他自定义的metric。

>   * Filters  
>  你可以为数据指定一组filters。你可以用 query string，也可以用 JSON 格式来指定过滤器，就像在 Discover
页的搜索栏里一样。点击Add Filter  
>  添加下一个过滤器。

>   * Significant Terms  
>  展示实验性的 significant terms 聚合的结果。

>

#### Discover数据查询

提交搜索请求，得到json搜索结果文档。 搜索词可用Lucene query syntax 或 Elasticsearch Query DSL

>   * 直接输入文本字符串： 比如搜索所有字段中包含Chrome的数据，直接输入`Chrome`即可。

>   *
搜索指定字段，在搜索词前加上字段名：比如`browser:Chrome`，搜索browser字段包含Chrome关键词的数据。如果要精确搜索，需加上双引号，如`browser:”Chrome”`。

>   * 范围搜索：比如 `timestamp:[ 1487520000 TO 1487779200
}`，[]表示端点包含在范围内，{}表示端点不包含在范围内。`status:>400` 大于400的状态值。

>   * 布尔操作符AND、OR、NOT：比如 `timestamp:[ 1487520000 TO 1487779200] AND
(browser:Chrome OR NOT status:500)`，指定时间范围并且是Chrome浏览器或非500状态的文档。

>   * 通配符搜索：单个词使用 ? 符号。0个或多个使用 * 符号。如 `te?t` 可匹配test 或 te7t，但不匹配 tes2t。`te*t`
可匹配 tet 或 test 或 tes2t。

>   * 近似搜索：`roam~` 可匹配foam 或 roams。

>   * 正则匹配：比如 `message:/mes{2}ages?/`

>   * 字段是否存在：`_exists_:user` 表示要求 user字段存在，`_missing_:user` 表示要求 user 字段不存在。


## 参考资料

<https://www.elastic.co/guide/en/elasticsearch/reference/current/term-level-queries.html>  
<https://lucene.apache.org/core/2_9_4/queryparsersyntax.html>

