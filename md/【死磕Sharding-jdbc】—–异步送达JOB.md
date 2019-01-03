> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/0f1a938c9017>

* * *

### 最大努力送达型异步JOB任务

当最大努力送达型监听器多次失败尝试后，把任务交给最大努力送达型异步JOB任务处理，异步多次尝试处理；核心源码在模块`sharding-jdbc-
transaction-async-job`中。该模块是一个独立异步处理模块，使用者决定是否需要启用，源码比较少，大概看一下源码结构：

![201805051009](http://cmsblogs.qiniudn.com/201805051009.png)

源码结构

>
resouces目录下的脚本和dubbo非常相似（作者应该也看过dubbo源码，哈），start.sh&stop.sh分别是服务启动脚本和服务停止脚本；根据start.sh脚本可知，该模块的主方法是
**BestEffortsDeliveryJobMain** ：

    
    
    CONTAINER_MAIN=com.dangdang.ddframe.rdb.transaction.soft.bed.BestEffortsDeliveryJobMain
    nohup java -classpath $CONF_DIR:$LIB_DIR:. $CONTAINER_MAIN >/dev/null 2>&1 &
    

Main方法的核心源码如下：

    
    
    public final class BestEffortsDeliveryJobMain {
    
        public static void main(final String[] args) throws Exception {
            try (InputStreamReader inputStreamReader = new InputStreamReader(BestEffortsDeliveryJobMain.class.getResourceAsStream("/conf/config.yaml"), "UTF-8")) {
                BestEffortsDeliveryConfiguration config = new Yaml(new Constructor(BestEffortsDeliveryConfiguration.class)).loadAs(inputStreamReader, BestEffortsDeliveryConfiguration.class);
                new BestEffortsDeliveryJobFactory(config).init();
            }
        }
    }
    

> 由源码可知，主配置文件是`config.yaml`；将该文件解析为 **BestEffortsDeliveryConfiguration**
，然后调用`new BestEffortsDeliveryJobFactory(config).init()`；

config.yaml配置文件中job相关配置内容如下：

    
    
    jobConfig:
      #作业名称
      name: bestEffortsDeliveryJob
    
      #触发作业的cron表达式--每5s重试一次
      cron: 0/5 * * * * ?
    
      #每次作业获取的事务日志最大数量
      transactionLogFetchDataCount: 100
    
      #事务送达的最大尝试次数.
      maxDeliveryTryTimes: 3
    
      #执行送达事务的延迟毫秒数,早于此间隔时间的入库事务才会被作业执行，其SQL为 where *** AND `creation_time` `maxDeliveryTryDelayMillis: 60000`这个配置也可以理解为60s内的transaction_log不处理；
    
    BestEffortsDeliveryJobFactory核心源码：
    
    

@RequiredArgsConstructor  
public final class BestEffortsDeliveryJobFactory {

    
    
    // 这个属性赋值通过有参构造方法进行赋值--new BestEffortsDeliveryJobFactory(config)，就是通过`config.yaml`配置的属性
    private final BestEffortsDeliveryConfiguration bedConfig;
    
    /**
     * BestEffortsDeliveryJobMain中调用该init()方法，初始化最大努力尝试型异步JOB，该JOB基于elastic-job；
     * Initialize best efforts delivery job.
     */
    public void init() {
        // 根据config.yaml中配置的zkConfig节点，得到协调调度中心CoordinatorRegistryCenter
        CoordinatorRegistryCenter regCenter = new ZookeeperRegistryCenter(createZookeeperConfiguration(bedConfig));
        // 调度中心初始化
        regCenter.init();
        // 构造elastic-job调度任务
        JobScheduler jobScheduler = new JobScheduler(regCenter, createBedJobConfiguration(bedConfig));
        jobScheduler.setField("bedConfig", bedConfig);
        jobScheduler.setField("transactionLogStorage", TransactionLogStorageFactory.createTransactionLogStorage(new RdbTransactionLogDataSource(bedConfig.getDefaultTransactionLogDataSource())));
        jobScheduler.init();
    }
    
    // 根据该方法可知，创建的是BestEffortsDeliveryJob
    private JobConfiguration createBedJobConfiguration(final BestEffortsDeliveryConfiguration bedJobConfig) {
        // 根据config.yaml中配置的jobConfig节点得到job配置信息，且指定job类型为BestEffortsDeliveryJob
        JobConfiguration result = new JobConfiguration(bedJobConfig.getJobConfig().getName(), BestEffortsDeliveryJob.class, 1, bedJobConfig.getJobConfig().getCron());
        result.setFetchDataCount(bedJobConfig.getJobConfig().getTransactionLogFetchDataCount());
        result.setOverwrite(true);
        return result;
    }
    
    
    
      
    BestEffortsDeliveryJob核心源码:
    
    

@Slf4j  
public class BestEffortsDeliveryJob extends
AbstractIndividualThroughputDataFlowElasticJob {

    
    
    @Setter
    private BestEffortsDeliveryConfiguration bedConfig;
    
    @Setter
    private TransactionLogStorage transactionLogStorage;
    
    @Override
    public List fetchData(final JobExecutionMultipleShardingContext context) {
        // 从transaction_log表中抓取最多100条事务日志（相关参数都在config.yaml中jobConfig节点下）
        return transactionLogStorage.findEligibleTransactionLogs(context.getFetchDataCount(), 
            bedConfig.getJobConfig().getMaxDeliveryTryTimes(), bedConfig.getJobConfig().getMaxDeliveryTryDelayMillis());
    }
    
    @Override
    public boolean processData(final JobExecutionMultipleShardingContext context, final TransactionLog data) {
        try (
            Connection conn = bedConfig.getTargetDataSource(data.getDataSource()).getConnection()) {
            // 调用事务日志存储器的processData()进行处理
            transactionLogStorage.processData(conn, data, bedConfig.getJobConfig().getMaxDeliveryTryTimes());
        } catch (final SQLException | TransactionCompensationException ex) {
            log.error(String.format("Async delivery times %s error, max try times is %s, exception is %s", data.getAsyncDeliveryTryTimes() + 1, 
                bedConfig.getJobConfig().getMaxDeliveryTryTimes(), ex.getMessage()));
            return false;
        }
        return true;
    }
    

}  
“`

