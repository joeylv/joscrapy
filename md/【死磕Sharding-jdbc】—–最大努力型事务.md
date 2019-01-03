  * 1 BASE Transaction
    * 1.1 最大努力送达型事务
    * 1.2 最大努力送达型事务的架构图
    * 1.3 适用场景
    * 1.4 使用限制
    * 1.5 开发示例
    * 1.6 核心源码分析
      * 1.6.1 柔性事务管理器
    * 1.7 1.事务日志存储器
      * 1.7.1 1.1.1事务日志核心接口
      * 1.7.2 1.1.2事务日志存储核心源码
      * 1.7.3 1.1.3事务日志存储样例
    * 1.8 1.2最大努力送达型事务监听器
    * 1.9 1.3 异步送达JOB任务

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/a8a370119663>

* * *

# BASE Transaction

  * Best efforts delivery transaction (已经实现).
  * Try confirm cancel transaction (待定).

> Sharding-JDBC由于性能方面的考量，决定不支持强一致性分布式事务。

## 最大努力送达型事务

在分布式数据库的场景下，相信对于该数据库的操作最终一定可以成功，所以通过最大努力反复尝试送达操作。

## 最大努力送达型事务的架构图

![](//upload-
images.jianshu.io/upload_images/6918995-df94f8b1ba5ae413.jpeg?imageMogr2/auto-
orient/strip%7CimageView2/2/w/640)

最大努力送达型事务的架构图

> 摘自[sharding-
jdbc使用指南☞事务支持](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2F1.x%2Fdocs%2F02-guide%2Ftransaction%2F)

执行过程有以下几种情况：

  1. **执行成功** –如图所示，执行结果事件->监听执行事件->执行成功->清理事务日志
  2. **执行失败，同步重试成功** –如图所示，执行结果事件->监听执行事件->执行失败->重试执行->执行成功->清理事务日志
  3. **执行失败，同步重试失败，异步重试成功** –如图所示，执行结果事件->监听执行事件->执行失败->重试执行->执行失败->”异步送达作业”重试执行->执行成功->清理事务日志
  4. **执行失败，同步重试失败，异步重试失败，事务日志保留** —-如图所示，执行结果事件->监听执行事件->执行失败->重试执行->执行失败->”异步送达作业”重试执行->执行失败->… …

> 说明：不管执行结果如何， **执行前事件** 都会 **记录事务日志** ；执行事件类型包括3种： **BEFORE_EXECUTE** ，
**EXECUTE_FAILURE** 和 **EXECUTE_SUCCESS** ；另外，这里的” **同步**
“不是绝对的同步执行，而是通过google-
guava的EventBus发布事件后，在监听端判断是EXECUTE_FAILURE事件，最多重试`syncMaxDeliveryTryTimes`次；后面对`BestEffortsDeliveryListener`的源码分析有介绍；这里的”
**异步** “通过外挂实现，在后面的文章[10\. sharding-
jdbc源码之异步送达JOB](https://www.jianshu.com/p/0f1a938c9017)会有分析；

## 适用场景

  * 根据主键删除数据。
  * 更新记录永久状态，如更新通知送达状态。

## 使用限制

  * 使用最大努力送达型柔性事务的SQL需要满足幂等性。
  * INSERT语句要求必须包含主键，且不能是自增主键。
  * UPDATE语句要求幂等，不能是UPDATE xxx SET x=x+1
  * DELETE语句无要求。

## 开发示例

    
    
    // 1\. 配置SoftTransactionConfiguration
    SoftTransactionConfiguration transactionConfig = new SoftTransactionConfiguration(dataSource);
    // 配置相关请看后面的备注
    transactionConfig.setXXX();
    
    // 2\. 初始化SoftTransactionManager
    SoftTransactionManager transactionManager = new SoftTransactionManager(transactionConfig);
    transactionManager.init();
    
    // 3\. 获取BEDSoftTransaction
    BEDSoftTransaction transaction = (BEDSoftTransaction) transactionManager.getTransaction(SoftTransactionType.BestEffortsDelivery);
    
    // 4\. 开启事务
    transaction.begin(connection);
    
    // 5\. 执行JDBC
    /* 
        code here
    */
    * 
    // 6.关闭事务
    transaction.end();
    

> 备注：SoftTransactionConfiguration支持的配置以及含义请参考[sharding-
jdbc使用指南☞事务支持](https://link.jianshu.com?t=http%3A%2F%2Fshardingjdbc.io%2Fdocs%2F02-guide%2Ftransaction%2F)，这段开发示例的代码也摘自这里；也可参考`sharding-
jdbc-
transaction`模块中`com.dangdang.ddframe.rdb.transaction.soft.integrate.SoftTransactionTest`如何使用柔性事务，
**但是这里的代码需要稍作修改，否则只是普通的执行逻辑，不是sharding-jdbc的执行逻辑** ：

    
    
    @Test
    public void bedSoftTransactionTest() throws SQLException {
        SoftTransactionManager transactionManagerFactory = new SoftTransactionManager(getSoftTransactionConfiguration(getShardingDataSource()));
        // 初始化柔性事务管理器
        transactionManagerFactory.init();
        BEDSoftTransaction transactionManager = (BEDSoftTransaction) transactionManagerFactory.getTransaction(SoftTransactionType.BestEffortsDelivery);
        transactionManager.begin(getShardingDataSource().getConnection());
        // 执行INSERT SQL（DML类型），如果执行过程中异常，会在`BestEffortsDeliveryListener`中重试
        insert();
        transactionManager.end();
    }
    
    private void insert() {
        String dbSchema = "insert into transaction_test(id, remark) values (2, ?)";
        try (
                // 将.getConnection("db_trans", SQLType.DML)移除，这样的话，得到的才是ShardingConnection 
                Connection conn = getShardingDataSource().getConnection();
                PreparedStatement preparedStatement = conn.prepareStatement(dbSchema)) {
            preparedStatement.setString(1, "JUST TEST IT .");
            preparedStatement.executeUpdate();
        } catch (final SQLException e) {
            e.printStackTrace();
        }
    }
    

## 核心源码分析

通过[3\. sharding-jdbc源码之路由&执行](https://www.jianshu.com/p/09efada2d086)中对
**ExecutorEngine** 的分析可知，sharding-
jdbc在执行SQL前后，分别调用`EventBusInstance.getInstance().post()`提交了事件，那么调用`EventBusInstance.getInstance().register()`的地方，就是柔性事务处理的地方，通过查看源码的调用关系可知，只有`SoftTransactionManager.init()`调用了`EventBusInstance.getInstance().register()`，所以柔性事务实现的核心在
**SoftTransactionManager** 这里；

### 柔性事务管理器

柔性事务实现在`SoftTransactionManager`中，核心源码如下：

    
    
    public final class SoftTransactionManager {
    
        // 柔性事务配置对象 
        @Getter
        private final SoftTransactionConfiguration transactionConfig;
    
        /**
         * Initialize B.A.S.E transaction manager.
         * @throws SQLException SQL exception
         */
        public void init() throws SQLException {
            // 初始化注册最大努力送达型柔性事务监听器；
            EventBusInstance.getInstance().register(new BestEffortsDeliveryListener());
            if (TransactionLogDataSourceType.RDB == transactionConfig.getStorageType()) {
                // 如果事务日志数据源类型是关系型数据库，则创建事务日志表transaction_log
                createTable();
            }
            // 内嵌的最大努力送达型异步JOB任务，依赖当当开源的elastic-job
            if (transactionConfig.getBestEffortsDeliveryJobConfiguration().isPresent()) {
                new NestedBestEffortsDeliveryJobFactory(transactionConfig).init();
            }
        }
    
        // 从这里可知创建的事务日志表表名是transaction_log（所以需要保证每个库中用户没有自定义创建transaction_log表）
        private void createTable() throws SQLException {
            String dbSchema = "CREATE TABLE IF NOT EXISTS `transaction_log` ("
                    + "`id` VARCHAR(40) NOT NULL, "
                    + "`transaction_type` VARCHAR(30) NOT NULL, "
                    + "`data_source` VARCHAR(255) NOT NULL, "
                    + "`sql` TEXT NOT NULL, "
                    + "`parameters` TEXT NOT NULL, "
                    + "`creation_time` LONG NOT NULL, "
                    + "`async_delivery_try_times` INT NOT NULL DEFAULT 0, "
                    + "PRIMARY KEY (`id`));";
            try (
                    Connection conn = transactionConfig.getTransactionLogDataSource().getConnection();
                    PreparedStatement preparedStatement = conn.prepareStatement(dbSchema)) {
                preparedStatement.executeUpdate();
            }
        }
    

> 从这段源码可知，柔性事务的几个重点如下，接下来一一根据源码进行分析；

>

>   * 事务日志存储器；

>   * 最大努力送达型事务监听器；

>   * 异步送达JOB任务；

>

## 1.事务日志存储器

柔性事务日志接口类为`TransactionLogStorage.java`，有两个实现类：

  1. **RdbTransactionLogStorage** ：关系型数据库存储柔性事务日志；
  2. **MemoryTransactionLogStorage** ：内存存储柔性事务日志；

### 1.1.1事务日志核心接口

TransactionLogStorage中几个重要接口在两个实现类中的实现：

  * **void add(TransactionLog)** ：Rdb实现就是把事务日志TransactionLog 插入到`transaction_log`表中，Memory实现就是把事务日志保存到`ConcurrentHashMap`中；
  * **void remove(String id)** ：Rdb实现就是从`transaction_log`表中删除事务日志，Memory实现从`ConcurrentHashMap`中删除事务日志；
  * **void increaseAsyncDeliveryTryTimes(String id)** ：异步增加送达重试次数，即TransactionLog中的asyncDeliveryTryTimes+1；Rdb实现就是update `transaction_log`表中`async_delivery_try_times`字段加1；Memory实现就是TransactionLog中重新给asyncDeliveryTryTimes赋值`new AtomicInteger(transactionLog.getAsyncDeliveryTryTimes()).incrementAndGet()`；
  * **findEligibleTransactionLogs()** : 查询需要处理的事务日志，条件是：①`异步处理次数async_delivery_try_times小于参数最大处里次数maxDeliveryTryTimes`，②`transaction_type是BestEffortsDelivery`，③`系统当前时间与事务日志的创建时间差要超过参数maxDeliveryTryDelayMillis`，每次最多查询参数size条；Rdb实现通过sql从transaction_log表中查询，Memory实现遍历ConcurrentHashMap匹配符合条件的TransactionLog；
  * **boolean processData()** ：Rdb实现执行TransactionLog中的sql，如果执行过程中抛出异常，那么调用increaseAsyncDeliveryTryTimes()增加送达重试次数并抛出异常，如果执行成功，删除事务日志，并返回true；Memory实现直接返回false（因为processData()的目的是执行TransactionLog中的sql，而Memory类型无法触及数据库，所以返回false）

### 1.1.2事务日志存储核心源码

`RdbTransactionLogStorage.java`实现源码：

    
    
    public final class RdbTransactionLogStorage implements TransactionLogStorage {
    
        private final DataSource dataSource;
    
        @Override
        public void add(final TransactionLog transactionLog) {
            // 保存事务日志到rdb中的sql
            String sql = "INSERT INTO `transaction_log` (`id`, `transaction_type`, `data_source`, `sql`, `parameters`, `creation_time`) VALUES (?, ?, ?, ?, ?, ?);";
            try (
                Connection conn = dataSource.getConnection();
                PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
                ... ...
                preparedStatement.executeUpdate();
            } catch (final SQLException ex) {
                throw new TransactionLogStorageException(ex);
            }
        }
    
        @Override
        public void remove(final String id) {
            // 根据id删除事务日志的sql
            String sql = "DELETE FROM `transaction_log` WHERE `id`=?;";
            try (
                Connection conn = dataSource.getConnection();
                PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
                preparedStatement.setString(1, id);
                preparedStatement.executeUpdate();
            } catch (final SQLException ex) {
                throw new TransactionLogStorageException(ex);
            }
        }
    
        @Override
        public List findEligibleTransactionLogs(final int size, final int maxDeliveryTryTimes, final long maxDeliveryTryDelayMillis) {
            List result = new ArrayList(size);
            // 执行该sql查询需要处理的事务日志，最多取size条；
            String sql = "SELECT `id`, `transaction_type`, `data_source`, `sql`, `parameters`, `creation_time`, `async_delivery_try_times` FROM `transaction_log` WHERE `async_delivery_try_times`&lt;? AND `transaction_type`=? AND `creation_time`&lt;? LIMIT ?;&quot;;
            try (Connection conn = dataSource.getConnection()) {
                try (PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
                    ... ...
                    preparedStatement.setLong(3, System.currentTimeMillis() - maxDeliveryTryDelayMillis);
                    ... ...
                }
            } catch (final SQLException ex) {
                throw new TransactionLogStorageException(ex);
            }
            return result;
        }
    
        @Override
        public void increaseAsyncDeliveryTryTimes(final String id) {
            // 更新处理次数+1
            String sql = &quot;UPDATE `transaction_log` SET `async_delivery_try_times`=`async_delivery_try_times`+1 WHERE `id`=?;&quot;;
            try (
                ... ...
            } catch (final SQLException ex) {
                throw new TransactionLogStorageException(ex);
            }
        }
    
        @Override
        public boolean processData(final Connection connection, final TransactionLog transactionLog, final int maxDeliveryTryTimes) {
            try (
                Connection conn = connection;
                // 执行TransactionLog中的sql
                PreparedStatement preparedStatement = conn.prepareStatement(transactionLog.getSql())) {
                for (int parameterIndex = 0; parameterIndex &lt; transactionLog.getParameters().size(); parameterIndex++) {
                    preparedStatement.setObject(parameterIndex + 1, transactionLog.getParameters().get(parameterIndex));
                }
                preparedStatement.executeUpdate();
            } catch (final SQLException ex) {
                如果抛出异常，表示执行sql失败，那么把增加处理次数并把异常抛出去；
                increaseAsyncDeliveryTryTimes(transactionLog.getId());
                throw new TransactionCompensationException(ex);
            }
            // 如果没有抛出异常，表示执行sql成功，那么删除该事务日志；
            remove(transactionLog.getId());
            return true;
        }
    }
    

### 1.1.3事务日志存储样例  
  
<table>  
<tr>  
<th>

id

</th>  
<th>

transction_type

</th>  
<th>

data_source

</th>  
<th>

sql

</th>  
<th>

parameters

</th>  
<th>

creation_time

</th>  
<th>

async_delivery_try_times

</th> </tr>  
<tr>  
<td>

85c141c4-1b8f-4e54-9010-0cc661bb1864

</td>  
<td>

BestEffortsDelivery

</td>  
<td>

db_trans

</td>  
<td>

insert into transaction_test(id, remark) values (3, ?)

</td>  
<td>

[“TEST BY AFEI.”]

</td>  
<td>

1517899200989

</td>  
<td>

0

</td> </tr> </table>

transaction_log中存储的事务日志样例：  
  
<table>  
<tr>  
<th>

id

</th>  
<th>

transction_type

</th>  
<th>

data_source

</th>  
<th>

sql

</th>  
<th>

parameters

</th>  
<th>

creation_time

</th>  
<th>

async_delivery_try_times

</th> </tr>  
<tr>  
<td>

85c141c4-1b8f-4e54-9010-0cc661bb1864

</td>  
<td>

BestEffortsDelivery

</td>  
<td>

db_trans

</td>  
<td>

insert into transaction_test(id, remark) values (3, ?)

</td>  
<td>

[“TEST BY AFEI.”]

</td>  
<td>

1517899200989

</td>  
<td>

0

</td> </tr> </table>

## 1.2最大努力送达型事务监听器

核心源码如下：

“`  
/**  
* Best efforts delivery B.A.S.E transaction listener.  
*  
* @author zhangliang  
*/  
@Slf4j  
public final class BestEffortsDeliveryListener {

    
    
    @Subscribe
    @AllowConcurrentEvents
    // 从方法可知，只监听DML执行事件（DML即数据维护语言，包括INSERT, UPDATE, DELETE）
    public void listen(final DMLExecutionEvent event) {
        // 判断是否需要继续，判断逻辑为：事务存在，并且是BestEffortsDelivery类型事务
        if (!isProcessContinuously()) {
            return;
        }
        // 从柔性事务管理器中得到柔性事务配置
        SoftTransactionConfiguration transactionConfig = SoftTransactionManager.getCurrentTransactionConfiguration().get();
        // 得到配置的柔性事务存储器
        TransactionLogStorage transactionLogStorage = TransactionLogStorageFactory.createTransactionLogStorage(transactionConfig.buildTransactionLogDataSource());
        // 这里肯定是最大努力送达型事务（如果不是BEDSoftTransaction，isProcessContinuously()就是false）
        BEDSoftTransaction bedSoftTransaction = (BEDSoftTransaction) SoftTransactionManager.getCurrentTransaction().get();
        // 根据事件类型做不同处理
        switch (event.getEventExecutionType()) {
            case BEFORE_EXECUTE:
                // 如果执行前事件，那么先保存事务日志；
                //TODO for batch SQL need split to 2-level records
                transactionLogStorage.add(new TransactionLog(event.getId(), bedSoftTransaction.getTransactionId(), bedSoftTransaction.getTransactionType(), 
                        event.getDataSource(), event.getSql(), event.getParameters(), System.currentTimeMillis(), 0));
                return;
            case EXECUTE_SUCCESS: 
                // 如果执行成功事件，那么删除事务日志；
                transactionLogStorage.remove(event.getId());
                return;
            case EXECUTE_FAILURE: 
                boolean deliverySuccess = false;
                // 如果执行成功事件，最大努力送达型最多尝试3次（可配置，SoftTransactionConfiguration中的参数syncMaxDeliveryTryTimes）；
                for (int i = 0; i &lt; transactionConfig.getSyncMaxDeliveryTryTimes(); i++) {
                    // 如果在该Listener中执行成功，那么返回，不需要再尝试
                    if (deliverySuccess) {
                        return;
                    }
                    boolean isNewConnection = false;
                    Connection conn = null;
                    PreparedStatement preparedStatement = null;
                    try {
                        conn = bedSoftTransaction.getConnection().getConnection(event.getDataSource(), SQLType.DML);
                        // 通过执行&quot;select 1&quot;判断conn是否是有效的数据库连接；如果不是有效的数据库连接，释放掉并重新获取一个数据库连接；
                        if (!isValidConnection(conn)) {
                            bedSoftTransaction.getConnection().release(conn);
                            conn = bedSoftTransaction.getConnection().getConnection(event.getDataSource(), SQLType.DML);
                            isNewConnection = true;
                        }
                        preparedStatement = conn.prepareStatement(event.getSql());
                        //TODO for batch event need split to 2-level records
                        for (int parameterIndex = 0; parameterIndex  BestEffortsDeliveryListener源码总结：
    

>   * 执行前，插入事务日志；

>   * 执行成功，则删除事务日志；

>   * 执行失败，则最大努力尝试`syncMaxDeliveryTryTimes`次；

>

## 1.3 异步送达JOB任务

  * 部署用于存储事务日志的数据库。
  * 部署用于异步作业使用的zookeeper。
  * 配置YAML文件,参照示例文件config.yaml。
  * 下载并解压文件sharding-jdbc-transaction-async-job-$VERSION.tar，通过start.sh脚本启动异步作业。

> 异步送达JOB任务基于elastic-job，所以需要部署zookeeper；

