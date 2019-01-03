  * 1 keys
  * 2 scan
  * 3 slowlog
  * 4 rename-command
  * 5 bigkeys
  * 6 monitor
  * 7 info
  * 8 config
  * 9 set

> 作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  链接：<https://www.jianshu.com/p/4df5f2356de9>

* * *

## keys

我把这个命令放在第一位，是因为笔者曾经做过的项目，以及一些朋友的项目，都因为使用`keys`这个命令，导致出现性能毛刺。这个命令的时间复杂度是O(N)，而且redis又是单线程执行，在执行keys时即使是时间复杂度只有O(1)例如SET或者GET这种简单命令也会堵塞，从而导致这个时间点性能抖动，甚至可能出现timeout。

> **强烈建议生产环境屏蔽keys命令** （后面会介绍如何屏蔽）。

## scan

既然 keys 命令不允许使用，那么有什么代替方案呢？有！那就是 `scan` 命令。如果把keys命令比作类似 `select * from users
where username like "%afei%"` 这种 SQL ，那么 scan 应该是 `select * from users where
id&gt;? limit 10` 这种命令。

官方文档用法如下：

    
    
    SCAN cursor [MATCH pattern] [COUNT count]
    

初始执行 scan 命令例如 `scan 0` 。SCAN
命令是一个基于游标的迭代器。这意味着命令每次被调用都需要使用上一次这个调用返回的游标作为该次调用的游标参数，以此来延续之前的迭代过程。当 SCAN
命令的游标参数被设置为 0时，服务器将开始一次新的迭代，而 **当redis服务器向用户返回值为0的游标时，表示迭代已结束**
，这是唯一迭代结束的判定方式，而不能通过返回结果集是否为空判断迭代结束。

使用方式：

    
    
    127.0.0.1:6380> scan 0
    1) "22"
    2)  1) "23"
        2) "20"
        3) "14"
        4) "2"
        5) "19"
        6) "9"
        7) "3"
        8) "21"
        9) "12"
       10) "25"
       11) "7"
    

返回结果分为两个部分：第一部分即 1) 就是下一次迭代游标，第二部分即 2) 就是本次迭代结果集。

## slowlog

上面提到不能使用 keys 命令，如果就有开发这么做了呢，我们如何得知？与其他任意存储系统例如 mysql，mongodb 可以查看慢日志一样，redis
也可以，即通过命令 `slowlog` 。用法如下：

    
    
    SLOWLOG subcommand [argument]
    

subcommand 主要有：

  * **get** ：用法：slowlog get [argument]，获取 argument 参数指定数量的慢日志。
  * **len** ：用法：slowlog len，总慢日志数量。
  * **reset** ：用法：slowlog reset，清空慢日志。

执行结果如下：

    
    
    127.0.0.1:6380> slowlog get 5
    1) 1) (integer) 2
       2) (integer) 1532656201
       3) (integer) 2033
       4) 1) "flushddbb"
    2) 1) (integer) 1  ----  慢日志编码，一般不用care
       2) (integer) 1532646897  ----  导致慢日志的命令执行的时间点，如果api有timeout，可以通过对比这个时间，判断可能是慢日志命令执行导致的
       3) (integer) 26424  ----  导致慢日志执行的redis命令，通过4)可知，执行config rewrite导致慢日志，总耗时26ms+
       4) 1) "config"
          2) "rewrite"
    

> 命令耗时超过多少才会保存到 slowlog 中，可以通过命令 `config set slowlog-log-slower-than 2000`
配置并且不需要重启 redis 。注意：单位是微妙，2000 微妙即 2 毫秒。

## rename-command

为了防止把问题带到生产环境，我们可以通过配置文件重命名一些危险命令，例如 `keys` 等一些高危命令。操作非常简单，只需要在 conf
配置文件增加如下所示配置即可：

    
    
    rename-command flushdb flushddbb
    rename-command flushall flushallall
    rename-command keys keysys
    

## bigkeys

随着项目越做越大，缓存使用越来越不规范。我们如何检查生产环境上一些有问题的数据。`bigkeys` 就派上用场了，用法如下：

    
    
    redis-cli -p 6380 --bigkeys
    

执行结果如下：

    
    
    ... ...
    -------- summary -------
    
    Sampled 526 keys in the keyspace!
    Total key length in bytes is 1524 (avg len 2.90)
    
    Biggest string found "test" has 10005 bytes
    Biggest   list found "commentlist" has 13 items
    
    524 strings with 15181 bytes (99.62% of keys, avg size 28.97)
    2 lists with 19 items (00.38% of keys, avg size 9.50)
    0 sets with 0 members (00.00% of keys, avg size 0.00)
    0 hashs with 0 fields (00.00% of keys, avg size 0.00)
    0 zsets with 0 members (00.00% of keys, avg size 0.00)
    

最后 5 行可知，没有 set,hash,zset 几种数据结构的数据。string 类型有 524 个，list 类型有两个；通过 `Biggest
... ...` 可知，最大 string 结构的 key 是 `test` ，最大 list 结构的 key 是`commentlist`。

需要注意的是，这个 **bigkeys得到的最大，不一定是最大** 。说明原因前，首先说明 `bigkeys` 的原理，非常简单，通过 scan
命令遍历，各种不同数据结构的 key ，分别通过不同的命令得到最大的 key：

  * 如果是 string 结构，通过 `strlen` 判断；
  * 如果是 list 结构，通过 `llen` 判断；
  * 如果是 hash 结构，通过 `hlen` 判断；
  * 如果是 set 结构，通过 `scard` 判断；
  * 如果是 sorted set 结构，通过 `zcard` 判断。

> 正因为这样的判断方式，虽然 string 结构肯定可以正确的筛选出最占用缓存，也可以说最大的 key。但是 list 不一定，例如，现在有两个 list
类型的 key，分别是：`numberlist--[0,1,2]，stringlist--["123456789123456789"]`，由于通过 llen
判断，所以 numberlist 要大于 stringlist 。而事实上 stringlist 更占用内存。其他三种数据结构
hash，set，sorted set 都会存在这个问题。使用 bigkeys 一定要注意这一点。

## monitor

假设生产环境没有屏蔽 keys 等一些高危命令，并且 slowlog 中还不断有新的 keys 导致慢日志。那我们如何揪出这些命令是由谁执行的呢？这就是
`monitor` 的用处，用法如下：

    
    
    redis-cli -p 6380 monitor
    

如果当前 redis 环境 OPS 比较高，那么建议结合 linux 管道命令优化，只输出 keys 命令的执行情况：

    
    
    [afei@redis ~]# redis-cli -p 6380 monitor | grep keys 
    1532645266.656525 [0 10.0.0.1:43544] "keyss" "*"
    1532645287.257657 [0 10.0.0.1:43544] "keyss" "44*"
    

执行结果中很清楚的看到 keys 命名执行来源。通过输出的 IP 和端口信息，就能在目标服务器上找到执行这条命令的进程，揪出元凶，勒令整改。

## info

如果说哪个命令能最全面反映当前 redis 运行情况，那么非 info 莫属。用法如下：

    
    
    INFO [section]
    

section可选值有：

  * **Server** ：运行的redis实例一些信息，包括：redis 版本，操作系统信息，端口，GCC 版本，配置文件路径等；
  * **Clients** ：redis 客户端信息，包括：已连接客户端数量，阻塞客户端数量等；
  * **Memory** ：使用内存，峰值内存，内存碎片率，内存分配方式。这几个参数都非常重要；
  * **Persistence** ：AOF 和 RDB 持久化信息；
  * **Stats** ：一些统计信息，最重要三个参数：OPS(`instantaneous_ops_per_sec`)， `keyspace_hits` 和 `keyspace_misses` 两个参数反应缓存命中率；
  * **Replication** ：redis 集群信息；
  * **CPU** ：CPU 相关信息；
  * **Keyspace** ：redis 中各个 DB 里 key 的信息；

## config

config 是一个非常有价值的命令，主要体现在对 redis 的运维。因为生产环境一般是不允许随意重启的，不能因为需要调优一些参数就修改 conf
配置文件并重启。redis 作者早就想到了这一点，通过 config 命令能热修改一些配置，不需要重启 redis
实例，可以通过如下命令查看哪些参数可以热修改：

    
    
    config get *
    

热修改就比较容易了，执行如下命令即可：

    
    
    config set
    

例如：`config set slowlog-max-len 100`，`config set maxclients 1024`

这样修改的话，如果以后由于某些原因 redis 实例故障需要重启，那通过 config 热修改的参数就会被配置文件中的参数覆盖，所以我们需要通过一个命令将
config 热修改的参数刷到 redis 配置文件中持久化，通过执行如下命令即可：

    
    
    config rewrite
    

执行该命令后，我们能在 config 文件中看到类似这种信息：

    
    
    # 如果conf中本来就有这个参数，通过执行config set，那么redis直接原地修改配置文件
    maxclients 1024
    # 如果conf中没有这个参数，通过执行config set，那么redis会追加在Generated by CONFIG REWRITE字样后面
    # Generated by CONFIG REWRITE
    save 600 60
    slowlog-max-len 100
    

## set

set 命令也能提升逼格？是的，我本不打算写这个命令，但是我见过太多人没有完全掌握这个命令，官方文档介绍的用法如下：

    
    
    SET key value [EX seconds] [PX milliseconds] [NX|XX]
    

你可能用的比较多的就是 `set key value` ，或者 `SETEX key seconds value` ，所以很多同学用 redis
实现分布式锁分为两步：首先执行 `SETNX key value` ，然后执行 `EXPIRE key seconds`
。很明显，这种实现有很严重的问题，因为两步执行不具备原子性，如果执行第一个命令后出现某些未知异常导致无法执行 `EXPIRE key seconds`
，那么分布式锁就会一直无法得到释放。

通过 `SET` 命令实现分布式锁的正式姿势应该是 `SET key value EX seconds
NX`（EX和PX任选，取决于对过期时间精度要求）。另外，value也有要求，最好是一个类似 UUID 这种具备唯一性的字符串。当然如果问你 redis
是否还有其他实现分布式锁的方案。你能说出 redlock ，那对方一定眼前一亮，心里对你竖起大拇指，但嘴上不会说。

关于 redis 分布式锁方案，强烈建议你阅读 redis 官方文档
[Redis分布式锁:http://redis.cn/topics/distlock.html](http://redis.cn/topics/distlock.html)

