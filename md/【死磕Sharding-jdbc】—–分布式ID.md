  * 1 实现动机
  * 2 分布式ID简介
  * 3 分布式ID源码分析
  * 4 获取workerId的三种方式
    * 4.1 HostNameKeyGenerator
    * 4.2 IPKeyGenerator
    * 4.3 IPSectionKeyGenerator
    * 4.4 建议

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>
原文链接：[https://www.jianshu.com/p/7f0661ddd6dd](https://www.jianshu.com/p/28b953c5d4b2)

* * *

# 实现动机

传统数据库软件开发中，主键自动生成技术是基本需求。而各大数据库对于该需求也提供了相应的支持，比如MySQL的自增键。
对于MySQL而言，分库分表之后，不同表生成全局唯一的Id是非常棘手的问题。因为同一个逻辑表内的不同实际表之间的自增键是无法互相感知的，
这样会造成重复Id的生成。我们当然可以通过约束表生成键的规则来达到数据的不重复，但是这需要引入额外的运维力量来解决重复性问题，并使框架缺乏扩展性。

目前有许多第三方解决方案可以完美解决这个问题，比如UUID等依靠特定算法自生成不重复键（由于InnoDB采用的B+Tree索引特性，UUID生成的主键插入性能较差），或者通过引入Id生成服务等。
但也正因为这种多样性导致了Sharding-JDBC如果强依赖于任何一种方案就会限制其自身的发展。

基于以上的原因，最终采用了以JDBC接口来实现对于生成Id的访问，而将底层具体的Id生成实现分离出来。

> 摘自[sharding-
jdbc分布式主键](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2F1.x%2Fdocs%2F02-guide%2Fkey-
generator%2F)

sharding-
jdbc的分布式ID采用twitter开源的snowflake算法，不需要依赖任何第三方组件，这样其扩展性和维护性得到最大的简化；但是snowflake算法的缺陷（强依赖时间，如果时钟回拨，就会生成重复的ID），sharding-
jdbc没有给出解决方案，如果用户想要强化，需要自行扩展；

>
扩展：美团的分布式ID生成系统也是基于snowflake算法，并且解决了时钟回拨的问题，读取有兴趣请阅读[Leaf——美团点评分布式ID生成系统](https://link.jianshu.com?t=https%3A%2F%2Ftech.meituan.com%2FMT_Leaf.html)

# 分布式ID简介

github上对分布式ID这个特性的描述是：`Distributed Unique Time-Sequence Generation`，两个重要特性是：
**分布式唯一** 和 **时间序** ；基于[Twitter
Snowflake](https://link.jianshu.com?t=https%3A%2F%2Fgithub.com%2Ftwitter%2Fsnowflake)算法实现，长度为64bit；64bit组成如下：

  * 1bit sign bit.
  * 41bits timestamp offset from 2016.11.01(Sharding-JDBC distributed primary key published data) to now.
  * 10bits worker process id.
  * 12bits auto increment offset in one mills.

# 分布式ID源码分析

核心源码在 **sharding-jdbc-core**
模块中的`com.dangdang.ddframe.rdb.sharding.keygen.DefaultKeyGenerator.java`中：

    
    
    public final class DefaultKeyGenerator implements KeyGenerator {
    
        public static final long EPOCH;
    
        // 自增长序列的长度（单位是位时的长度）
        private static final long SEQUENCE_BITS = 12L;
    
        // workerId的长度（单位是位时的长度）
        private static final long WORKER_ID_BITS = 10L;
    
        private static final long SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1;
    
        private static final long WORKER_ID_LEFT_SHIFT_BITS = SEQUENCE_BITS;
    
        private static final long TIMESTAMP_LEFT_SHIFT_BITS = WORKER_ID_LEFT_SHIFT_BITS + WORKER_ID_BITS;
    
        // 位运算计算workerId的最大值（workerId占10位，那么1向左移10位就是workerId的最大值）
        private static final long WORKER_ID_MAX_VALUE = 1L <= 0L && workerId < WORKER_ID_MAX_VALUE);
            DefaultKeyGenerator.workerId = workerId;
        }
    
        /**
         * 调用该方法，得到分布式唯一ID
         * @return key type is @{@link Long}.
         */
        @Override
        public synchronized Number generateKey() {
            long currentMillis = timeService.getCurrentMillis();
            // 每次取分布式唯一ID的时间不能少于上一次取时的时间
            Preconditions.checkState(lastTime <= currentMillis, "Clock is moving backwards, last time is %d milliseconds, current time is %d milliseconds", lastTime, currentMillis);
            // 如果同一毫秒范围内，那么自增，否则从0开始
            if (lastTime == currentMillis) {
                // 如果自增后的sequence值超过4096，那么等待直到下一个毫秒
                if (0L == (sequence = ++sequence & SEQUENCE_MASK)) {
                    currentMillis = waitUntilNextTime(currentMillis);
                }
            } else {
                sequence = 0;
            }
            // 更新lastTime的值，即最后一次获取分布式唯一ID的时间
            lastTime = currentMillis;
            // 从这里可知分布式唯一ID的组成部分；
            return ((currentMillis - EPOCH) << TIMESTAMP_LEFT_SHIFT_BITS) | (workerId << WORKER_ID_LEFT_SHIFT_BITS) | sequence;
        }
    
        // 获取下一毫秒的方法：死循环获取当前毫秒与lastTime比较，直到大于lastTime的值；
        private long waitUntilNextTime(final long lastTime) {
            long time = timeService.getCurrentMillis();
            while (time <= lastTime) {
                time = timeService.getCurrentMillis();
            }
            return time;
        }
    }
    

# 获取workerId的三种方式

sharding-jdbc的`sharding-jdbc-
plugin`模块中，提供了三种方式获取workerId的方式，并提供接口获取分布式唯一ID的方法–`generateKey()`，接下来对各种方式如何生成workerId进行分析；

## HostNameKeyGenerator

  1. 根据hostname获取，源码如下（HostNameKeyGenerator.java）：

    
    
    /**
     * 根据机器名最后的数字编号获取工作进程Id.如果线上机器命名有统一规范,建议使用此种方式.
     * 例如机器的HostName为:dangdang-db-sharding-dev-01(公司名-部门名-服务名-环境名-编号)
     * ,会截取HostName最后的编号01作为workerId.
     *
     * @author DonneyYoung
     **/
     static void initWorkerId() {
        InetAddress address;
        Long workerId;
        try {
            address = InetAddress.getLocalHost();
        } catch (final UnknownHostException e) {
            throw new IllegalStateException("Cannot get LocalHost InetAddress, please check your network!");
        }
        // 先得到服务器的hostname，例如JTCRTVDRA44，linux上可通过命令"cat /proc/sys/kernel/hostname"查看；
        String hostName = address.getHostName();
        try {
            // 计算workerId的方式：
            // 第一步hostName.replaceAll("\\d+$", "")，即去掉hostname后纯数字部分，例如JTCRTVDRA44去掉后就是JTCRTVDRA
            // 第二步hostName.replace(第一步的结果, "")，即将原hostname的非数字部分去掉，得到纯数字部分，就是workerId
            workerId = Long.valueOf(hostName.replace(hostName.replaceAll("\\d+$", ""), ""));
        } catch (final NumberFormatException e) {
            throw new IllegalArgumentException(String.format("Wrong hostname:%s, hostname must be end with number!", hostName));
        }
        DefaultKeyGenerator.setWorkerId(workerId);
    }
    

## IPKeyGenerator

  1. 根据IP获取，源码如下（IPKeyGenerator.java）：

    
    
    /**
     * 根据机器IP获取工作进程Id,如果线上机器的IP二进制表示的最后10位不重复,建议使用此种方式
     * ,列如机器的IP为192.168.1.108,二进制表示:11000000 10101000 00000001 01101100
     * ,截取最后10位 01 01101100,转为十进制364,设置workerId为364.
     */
    static void initWorkerId() {
        InetAddress address;
        try {
            // 首先得到IP地址，例如192.168.1.108
            address = InetAddress.getLocalHost();
        } catch (final UnknownHostException e) {
            throw new IllegalStateException(&quot;Cannot get LocalHost InetAddress, please check your network!&quot;);
        }
        // IP地址byte[]数组形式，这个byte数组的长度是4，数组0~3下标对应的值分别是192，168，1，108
        byte[] ipAddressByteArray = address.getAddress();
        // 由这里计算workerId源码可知，workId由两部分组成：
        // 第一部分(ipAddressByteArray[ipAddressByteArray.length - 2] &amp; 0B11) &lt;&lt; Byte.SIZE：ipAddressByteArray[ipAddressByteArray.length - 2]即取byte[]倒数第二个值，即1，然后&amp;0B11，即只取最后2位（IP段倒数第二个段取2位，IP段最后一位取全部8位，总计10位），然后左移Byte.SIZE，即左移8位（因为这一部分取得的是IP段中倒数第二个段的值）；
        // 第二部分(ipAddressByteArray[ipAddressByteArray.length - 1] &amp; 0xFF)：ipAddressByteArray[ipAddressByteArray.length - 1]即取byte[]最后一位，即108，然后&amp;0xFF，即通过位运算将byte转为int；
        // 最后将第一部分得到的值加上第二部分得到的值就是最终的workId
        DefaultKeyGenerator.setWorkerId((long) (((ipAddressByteArray[ipAddressByteArray.length - 2] &amp; 0B11) &lt;&lt; Byte.SIZE) + (ipAddressByteArray[ipAddressByteArray.length - 1] &amp; 0xFF)));
    }
    

## IPSectionKeyGenerator

  1. 根据IP段获取，源码如下（IPSectionKeyGenerator.java）：

    
    
    /**
     * 浏览 {@link IPKeyGenerator} workerId生成的规则后，感觉对服务器IP后10位（特别是IPV6）数值比较约束.
     * 
     * 
     * 有以下优化思路：
     * 因为workerId最大限制是2^10，我们生成的workerId只要满足小于最大workerId即可。
     * 1.针对IPV4:
     * ....IP最大 255.255.255.255。而（255+255+255+255) &lt; 1024。
     * ....因此采用IP段数值相加即可生成唯一的workerId，不受IP位限制。
     * 2.针对IPV6:
     * ....IP最大ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
     * ....为了保证相加生成出的workerId &lt; 1024,思路是将每个bit位的后6位相加。这样在一定程度上也可以满足workerId不重复的问题。
     * 
     * 使用这种IP生成workerId的方法,必须保证IP段相加不能重复
     *
     * @author DogFc
     */
    static void initWorkerId() {
        InetAddress address;
        try {
            address = InetAddress.getLocalHost();
        } catch (final UnknownHostException e) {
            throw new IllegalStateException("Cannot get LocalHost InetAddress, please check your network!");
        }
        // 得到IP地址的byte[]形式值
        byte[] ipAddressByteArray = address.getAddress();
        long workerId = 0L;
        //如果是IPV4，计算方式是遍历byte[]，然后把每个IP段数值相加得到的结果就是workerId
        if (ipAddressByteArray.length == 4) {
            for (byte byteNum : ipAddressByteArray) {
                workerId += byteNum &amp; 0xFF;
            }
            //如果是IPV6，计算方式是遍历byte[]，然后把每个IP段后6位（&amp; 0B111111 就是得到后6位）数值相加得到的结果就是workerId
        } else if (ipAddressByteArray.length == 16) {
            for (byte byteNum : ipAddressByteArray) {
                workerId += byteNum &amp; 0B111111;
            }
        } else {
            throw new IllegalStateException("Bad LocalHost InetAddress, please check your network!");
        }
        DefaultKeyGenerator.setWorkerId(workerId);
    }
    

## 建议

**大道至简** ，强烈推荐 **HostNameKeyGenerator**
方式获取workerId，只需服务器按照标准统一配置好hostname即可；这种方案有点类似spring-boot： **约定至上**
；并能够让架构最简化，不依赖任何第三方组件；

