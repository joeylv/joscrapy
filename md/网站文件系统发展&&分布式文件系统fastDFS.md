## **网站文件系统发展**

1、 **单机时代的图片服务器架构**

初创时期由于时间紧迫，开发人员水平也很有限等原因。所以通常就直接在
website文件所在的目录下，建立1个upload子目录，用于保存用户上传的图片文件。如果按业务再细分，可以在upload目录下再建立不同的子目录来区分。例如：upload\QA,upload\Face等

**优点** ：实现起来最简单，无需任何复杂技术，就能成功将用户上传的文件写入指定目录。保存数据库记录和访问起来倒是也很方便。

**缺点** ：上传方式混乱，严重不利于网站的扩展。

2、 **单独立文件服务器**

随着公司的业务不断的发展，将服务和文件放在同一服务器下面的弊端越来越明显；这个时候就该上线独立的图片服务器系统；通过
ftp或者ssh工具将文件上传到图片服务器的某个目录下面，在通过ngnix或者apache服务器来做图片的访问，给图片服务器配置独立的子域名，例如
img.xx.com。在业务处理文件时通过ftp或者ssh将文件上传到文件服务器，返回给程序一个独立域名的图片url地址，网站正常访问的时候就通过这个URL地址来访问文件。

**优点**
：图片访问是很消耗服务器资源的（因为会涉及到操作系统的上下文切换和磁盘I/O操作）。分离出来后，Web/App服务器可以更专注发挥动态处理的能力；独立存储，更方便做扩容、容灾和数据迁移；方便做图片访问请求的负载均衡，方便应用各种缓存策略（HTTP
Header、Proxy Cache等），也更加方便迁移到CDN。

**缺点** ：单机存在性能瓶颈，容灾、垂直扩展性稍差

3、 **分布式文件系统**

业务继续发展，单独单台的服务器存储和响应也很快到达了瓶颈，新的业务要求，文件访问高响应性，高可用性来响应业务对系统的要求。分布式文件系统，一般分为三块内容来配合，服务的存储、访问的仲裁系统，文件存储系统，文件的容灾系统来构成，总裁系统相当于文件服务器的大脑，根据一定的算法来决定文件存储的位置，文件存储系统负责报错文件，容灾系统负责文件系统和自己的相互备份。

**优点** ：扩展能力: 毫无疑问，扩展能力是一个分布式文件系统最重要的特点；高可用性:
在分布式文件系统中，高可用性包含两层，一是整个文件系统的可用性，二是数据的完整和一致性；弹性存储:
可以根据业务需要灵活地增加或缩减数据存储以及增删存储池中的资源，而不需要中断系统运行

**缺点** ：系统复杂度稍高，需要更多服务器

## **分布式文件系统 fastDFS**

1、 **什么是 FastDFS**

FastDFS是一个开源的轻量级分布式文件系统。它解决了大数据量存储和负载均衡等问题。特别适合以中小文件（建议范围：4KB < file_size
<500MB）为载体的在线服务，如相册网站、视频网站等等。在UC基于FastDFS开发向用户提供了：网盘，社区，广告和应用下载等业务的存储服务。

2、 **FastDFS 架构和原理**

FastDFS服务端有三个角色：跟踪服务器（tracker server）、存储服务器（storage server）和客户端（client）。

tracker
server：跟踪服务器，主要做调度工作，起负载均衡的作用。在内存中记录集群中所有存储组和存储服务器的状态信息，是客户端和数据服务器交互的枢纽。相比GFS中的master更为精简，不记录文件索引信息，占用的内存量很少。

storage server：存储服务器（又称：存储节点或数据服务器），文件和文件属性（meta data）都保存到存储服务器上。Storage
server直接利用OS的文件系统调用管理文件。

client：客户端，作为业务请求的发起方，通过专有接口，使用TCP/IP协议与跟踪器服务器或存储节点进行数据交互。

[![FastDFS架构图1_thumb\[9\]](../md/img/ityouknow/331425-20160401142238160-784483379.png)](http://images2015.cnblogs.com/blog/331425/201604/331425-20160401142237098-1095335699.png)

Tracker相当于FastDFS的大脑，不论是上传还是下载都是通过tracker来分配资源；客户端一般可以使用ngnix等静态服务器来调用或者做一部分的缓存；存储服务器内部分为卷（或者叫做组），卷于卷之间是平行的关系，可以根据资源的时候情况随时增加，卷内服务器文件相互同步备份，以达到容灾的目的

**上传机制** ：

首先客户端请求Tracker服务获取到存储服务器的ip地址和端口，然后客户端根据返回的IP地址和端口号请求上传文件，存储服务器接收到请求后，生产文件file_id并且将文件内容写入磁盘返回给客户端file_id和路径信息、文件名，客户端保存相关信息上传完毕

![](http://tech.uc.cn/wp-
content/uploads/2012/08/FastDFS%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B.png)

**下载机制** ：

客户端带上文件名信息请求Tracker服务获取到存储服务器的ip地址和端口，然后客户端根据返回的IP地址和端口号请求下载文件，存储服务器接收到请求后返回文件给客户端。

![](http://tech.uc.cn/wp-
content/uploads/2012/08/FastDFS%E4%B8%8B%E8%BD%BD%E6%B5%81%E7%A8%8B.png)

3、 **如何搭建 fastDFS**

请参考以下文章：

[FastDFS + Nginx 反向代理缓存 安装与配置](http://www.linux178.com/storage/fastdfs-nginx-
cache.html)

地址：[http://www.linux178.com/storage/fastdfs-nginx-
cache.html](http://www.linux178.com/storage/fastdfs-nginx-cache.html)

4、 **使用 java调用fastDFS**

以下代码是一个spring mvc中一个完整的上传请求

    
    
        @RequestMapping(value = "/upload", method = RequestMethod.POST)
        @ResponseBody
        public Object upload(@RequestParam MultipartFile file) {
            UploadResponse res = new UploadResponse();
            try {
                if(file.isEmpty()){
                    res.setRet_code(UserCodeEnum.ERR_FILE_NULL.getCode());
                    res.setRet_msg(UserCodeEnum.ERR_FILE_NULL.getDesc());
                }else{
                    logger.info("UserController-upload-request-file=" + file.getOriginalFilename());
                    
                    String tempFileName = file.getOriginalFilename();
                    //fastDFS方式
                    ClassPathResource cpr = new ClassPathResource("fdfs_client.conf");
                    ClientGlobal.init(cpr.getClassLoader().getResource("fdfs_client.conf").getPath());
                    byte[] fileBuff = file.getBytes();
                    String fileId = "";
                    String fileExtName = tempFileName.substring(tempFileName.lastIndexOf("."));
                    
                    //建立连接
                    TrackerClient tracker = new TrackerClient();
                    TrackerServer trackerServer = tracker.getConnection();
                    StorageServer storageServer = null;
                    StorageClient1 client = new StorageClient1(trackerServer, storageServer);
                    
                    //设置元信息
                    NameValuePair[] metaList = new NameValuePair[3];
                    metaList[0] = new NameValuePair("fileName", tempFileName);
                    metaList[1] = new NameValuePair("fileExtName", fileExtName);
                    metaList[2] = new NameValuePair("fileLength", String.valueOf(file.getSize()));
                    
                    //上传文件
                    fileId = client.upload_file1(fileBuff, fileExtName, metaList);
                    
                    res.setHead_img(UserConstants.FILE_IMG_URL+fileId);
                    
                    res.setRet_code(UserCodeEnum.SUCCESS.getCode());
                    res.setRet_msg(UserCodeEnum.SUCCESS.getDesc());
                }
                
                logger.info("UserController-upload-response-" + JsonUtils.o2j(res));
            } catch (Exception e) {
                res.setRet_code(UserCodeEnum.ERR_UNKNOWN.getCode());
                res.setRet_msg(UserCodeEnum.ERR_UNKNOWN.getDesc());
                logger.error("UserController-upload-error", e);
            }
            return res;
        }

fastDFS java客户端配置文件fdfs_client.conf配置如下：

    
    
    connect_timeout = 30
    network_timeout = 60
    charset = ISO8859-1
    http.tracker_http_port = 8090
    http.anti_steal_token = no
    http.secret_key = 123456
    
    tracker_server = 192.168.11.***:22122

参考：

[http://blog.chinaunix.net/uid-20196318-id-4058561.html](http://blog.chinaunix.net/uid-20196318-id-4058561.html)

[http://tech.uc.cn/?p=221](http://tech.uc.cn/?p=221)

