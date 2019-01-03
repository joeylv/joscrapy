  * 1 源码分析
    * 1.1 1.创建数据源
    * 1.2 2.持久化
      * 1.2.1 2.1持久化sharding规则配置
      * 1.2.2 2.2节点配置信息与源码对应关系
    * 1.3 3.创建监听器
      * 1.3.1 3.1 rule节点监听分析
      * 1.3.2 3.2 props节点监听分析
      * 1.3.3 3.3 instances节点监听分析
      * 1.3.4 3.4 其他节点监听分析

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/60440c317d95>

* * *

![201808091002](http://cmsblogs.qiniudn.com/201808091002.png)

orchestration源码结构图.png

根据源码图解可知， **sharding-jdbc-orchestration** 模块中创建数据源有两种方式：工厂类和spring；且有两种数据源类型：
**OrchestrationShardingDataSource** 和 **OrchestrationMasterSlaveDataSource** ；

  * 左边是 **OrchestrationShardingDataSource** 类型数据源创建，配置信息持久化以及监听&刷新过程；右边是 **OrchestrationMasterSlaveDataSource** 类型数据源创建，配置信息持久化以及监听&刷新过程；
  * 工厂类方式通过 **OrchestrationShardingDataSourceFactory** 或者 **OrchestrationMasterSlaveDataSourceFactory** 创建；
  * spring方式通过解析xml配置文件创建（可以参考 **OrchestrationShardingNamespaceTest** 测试用例）；
  * 得到数据源后，调用OrchestrationFacade.init()方法；在该init()方法中持久化配置信息到注册中心中；并创建监听器；

> 由图可知，两种类型数据源的处理大同小异，本篇文章只分析 **OrchestrationShardingDataSource** 这种类型的数据源；

# 源码分析

接下来通过工厂类创建 **OrchestrationShardingDataSource** 类型数据源源码剖析orchestration的实现原理；

## 1.创建数据源

通过测试用例 **YamlOrchestrationShardingIntegrateTest** 可知，创建数据源的代码为
**OrchestrationShardingDataSourceFactory.createDataSource(yamlFile);**
这段代码的实现如下所示：

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class OrchestrationShardingDataSourceFactory {
    
        public static DataSource createDataSource(
                final Map<String, DataSource> dataSourceMap, final ShardingRuleConfiguration shardingRuleConfig, 
                final Map<String, Object> configMap, final Properties props, 
                final OrchestrationConfiguration orchestrationConfig) throws SQLException {
            // step3.1 创建OrchestrationShardingDataSource数据源
            OrchestrationShardingDataSource result = new OrchestrationShardingDataSource(dataSourceMap, shardingRuleConfig, configMap, props, orchestrationConfig);
            // step3.2 初始化（这里是sharding-jdb orchestration编排治理的核心）
            result.init();
            return result;
        }
    
        public static DataSource createDataSource(final File yamlFile) throws SQLException, IOException {
            // step1\. 解析yaml文件得到YamlOrchestrationShardingRuleConfiguration
            YamlOrchestrationShardingRuleConfiguration config = unmarshal(yamlFile);
            // step2\. 得到分库分表规则配置，即根据yaml文件中shardingRule节点信息得到的分库分表规则配置
            YamlShardingRuleConfiguration shardingRuleConfig = config.getShardingRule();
            // step3\. 调用上面的方法创建数据源
            return createDataSource(config.getDataSources(), shardingRuleConfig.getShardingRuleConfiguration(),  
                    shardingRuleConfig.getConfigMap(), shardingRuleConfig.getProps(), config.getOrchestration().getOrchestrationConfiguration());
        }
    
        // 一些其他创建数据源的方式，大同小异，暂时省略
        ... ...
    }
    

>
OrchestrationShardingDataSource.init()方法会调用OrchestrationFacade.init()方法，所以分析后者即可；

## 2.持久化

OrchestrationFacade.init()核心源码如下：

    
    
    public void init(
            final Map<String, DataSource> dataSourceMap, 
            final ShardingRuleConfiguration shardingRuleConfig, 
            final Map<String, Object> configMap, 
            final Properties props, 
            final ShardingDataSource shardingDataSource) throws SQLException {
        // step1\. 持久化sharding规则配置，且为PERSISTENT类型节点
        configService.persistShardingConfiguration(getActualDataSourceMapForMasterSlave(dataSourceMap), shardingRuleConfig, configMap, props, isOverwrite);
        // step2\. 持久化sharding实例信息，且为EPHEMERAL类型节点
        instanceStateService.persistShardingInstanceOnline();
        // step3\. 持久化数据源节点信息，且为PERSISTENT类型节点
        dataSourceService.persistDataSourcesNode();
        // step4\. 注册监听器
        listenerManager.initShardingListeners(shardingDataSource);
    }
    

> 所以说，这里就是sharding-jdbc编排治理的核心–配置信息持久化，注册监听器；接下来先分析编排治理的配置信息持久化；

### 2.1持久化sharding规则配置

持久化sharding规则配置的核心实现如下，我们接下来一一分析其持久化的内容；

    
    
    public void persistShardingConfiguration(
            final Map<String, DataSource> dataSourceMap, 
            final ShardingRuleConfiguration shardingRuleConfig, 
            final Map<String, Object> configMap, 
            final Properties props, final boolean isOverwrite) {
        persistDataSourceConfiguration(dataSourceMap, isOverwrite);
        persistShardingRuleConfiguration(shardingRuleConfig, isOverwrite);
        persistShardingConfigMap(configMap, isOverwrite);
        persistShardingProperties(props, isOverwrite);
    }
    

  * 持久化数据源配置  
对应源码为 **persistDataSourceConfiguration(dataSourceMap, isOverwrite);**
核心实现源码如下：

    
    
    private void persistDataSourceConfiguration(final Map<String, DataSource> dataSourceMap, final boolean isOverwrite) {
        // 如果配置了overwrite，或者/demo_ds_ms/config/datasource节点还不存在，那么就持久化数据源相关配置；
        if (isOverwrite || !hasDataSourceConfiguration()) {
            regCenter.persist(configNode.getFullPath(ConfigurationNode.DATA_SOURCE_NODE_PATH), DataSourceJsonConverter.toJson(dataSourceMap));
        }
    }
    

根据上面的分析得出数据源配置路径为：`/orchestration-yaml-
test/demo_ds_ms/config/datasource`。即完整路径表达式为：`/${orchestration.zookeeper.namespace}/${orchestration.name}/config/datasource`；其他几个配置信息持久化的源码分析类似；

### 2.2节点配置信息与源码对应关系

    
    
    config
        ├──datasource                                persistDataSourceConfiguration()
        ├──sharding                                  
        ├      ├──rule                               persistShardingRuleConfiguration()
        ├      ├──configmap                          persistShardingConfigMap()
        ├      ├──props                              persistShardingProperties()
        ├──masterslave                               
        ├      ├──rule                               
        ├      ├──configmap  
    state
        ├──instances                                persistShardingInstanceOnline()
        ├      ├──${instance1-ip}@${pid}@${uuid}                              
        ├      ├──${instance2-ip}@${pid}@${uuid}  
        ├──datasources                              persistDataSourcesNode()
    

>
说明：节点信息省略了路径前缀`/${orchestration.zookeeper.namespace}/${orchestration.name}`；例如，某instance节点的完整路径：：`/${orchestration.zookeeper.namespace}/${orchestration.name}/state/instances/${ip}@${pid}@${uuid}`（/demo_ds_ms/state/instances/10.0.0.189@10072@6f8f1b1e-90a4-4edd-
baf9-aeb906a664bd）；

## 3.创建监听器

**OrchestrationFacade.init()** 中调用persist* **()方法持久化各配置信息到注册中心后，再调用**
listenerManager.initShardingListeners(shardingDataSource)**创建监听器，核心源码如下：

    
    
    public void initShardingListeners(final ShardingDataSource shardingDataSource) {
        // 监听三个节点(/config/datasource, /config/sharding/rule, /config/sharding/props)
        configurationListenerManager.start(shardingDataSource);
        // 监听节点/state/instances/${instance-ip}@${pid}@${uuid}，即监听表示当前实例的节点
        instanceListenerManager.start(shardingDataSource);
        // 监听节点/state/datasources
        dataSourceListenerManager.start(shardingDataSource);
        // 监听节点/config/sharding/cofigmap
        configMapListenerManager.start(shardingDataSource);
    }
    

### 3.1 rule节点监听分析

核心源码如下：

    
    
    private void start(final String node, final ShardingDataSource shardingDataSource) {
        // 得到监听的路径/config/sharding/rule
        String cachePath = configNode.getFullPath(node);
        // watch该注册中心中该路径
        regCenter.watch(cachePath, new EventListener() {
    
            @Override
            public void onChange(final DataChangedEvent event) {
                // 只处理UPDATED类型事件
                if (DataChangedEvent.Type.UPDATED == event.getEventType()) {
                    try {
                        // 调用loadShardingProperties()从配置中心中拿出/config/datasource和/config/sharding/props两个路径的数据准备刷新sharding数据源
                        shardingDataSource.renew(dataSourceService.getAvailableShardingRuleConfiguration().build(dataSourceService.getAvailableDataSources()), configService.loadShardingProperties());
                    } catch (final SQLException ex) {
                        throw new ShardingJdbcException(ex);
                    }
                }
            }
        });
    }
    
    public class ShardingDataSource extends AbstractDataSourceAdapter implements AutoCloseable {
        ... ...
        // 刷新ShardingContext
        public void renew(final ShardingRule newShardingRule, final Properties newProps) throws SQLException {
            ShardingProperties newShardingProperties = new ShardingProperties(null == newProps ? new Properties() : newProps);
            // 得到更新前的executor.size的值
            int originalExecutorSize = shardingProperties.getValue(ShardingPropertiesConstant.EXECUTOR_SIZE);
            // 得到更新后的executor.size的值
            int newExecutorSize = newShardingProperties.getValue(ShardingPropertiesConstant.EXECUTOR_SIZE);
            // 如果executor.size的值有变化则重新构造ExecutorEngine
            if (originalExecutorSize != newExecutorSize) {
                executorEngine.close();
                executorEngine = new ExecutorEngine(newExecutorSize);
            }
            // 得到更新后的sql.show的值
            boolean newShowSQL = newShardingProperties.getValue(ShardingPropertiesConstant.SQL_SHOW);
            shardingProperties = newShardingProperties;
            // 重新构造ShardingContext
            shardingContext = new ShardingContext(newShardingRule, getDatabaseType(), executorEngine, newShowSQL);
        }
        ... ...
    }
    

ShardingContext 包含如下属性–rule节点有变更时，这些属性都会得到更新；

    
    
    public final class ShardingContext {
        private final ShardingRule shardingRule;   
        private final DatabaseType databaseType;    
        private final ExecutorEngine executorEngine;  
        private final boolean showSQL;
    }
    

### 3.2 props节点监听分析

props节点监听源码如下：

    
    
    private void start(final String node, final ShardingDataSource shardingDataSource) {
        // 监听的路径，即/${orchestration.zookeeper.namespace}/${orchestration.name}/config/sharding/props
        String cachePath = configNode.getFullPath(node);
        // watch该路径
        regCenter.watch(cachePath, new EventListener() {        
            @Override
            public void onChange(final DataChangedEvent event) {
                // 如果有UPDATED变更事件(只考虑UPDATED事件)
                if (DataChangedEvent.Type.UPDATED == event.getEventType()) {
                    try {
                        // 这里的逻辑和rule节点类型，刷新ShardingContext
                        shardingDataSource.renew(
                                dataSourceService.getAvailableShardingRuleConfiguration().build(dataSourceService.getAvailableDataSources()),
                                configService.loadShardingProperties()
                        );
                    } catch (final SQLException ex) {
                        throw new ShardingJdbcException(ex);
                    }
                }
            }
        });
    }
    

### 3.3 instances节点监听分析

实际监听的是instances下代表某具体实例的节点，例如 **/orchestration-spring-namespace-
test/shardingDataSource/state/instances/10.0.0.188@13272@42533e85-9bb1-4484-baa1-2a2f9b2480a6**
。核心源码如下：

    
    
    @Override
    public void start(final ShardingDataSource shardingDataSource) {
        regCenter.watch(stateNode.getInstancesNodeFullPath(OrchestrationInstance.getInstance().getInstanceId()), new EventListener() {
    
            @Override
            public void onChange(final DataChangedEvent event) {
                // 当收到UPDATED类型事件
                if (DataChangedEvent.Type.UPDATED == event.getEventType()) {
                    // 首先拿到所有数据源
                    Map<String, DataSource> dataSourceMap = configService.loadDataSourceMap();
                    // 如果具体实例的节点的value被置为disabled（大小写不敏感），那么将该实例下所有数据源置为CircuitBreakerDataSource（这是sharding-jdbc自定义的一个特殊数据源，如果SQL路由到该数据源上，那么执行时不返回任何数据，也不实际执行该SQL，相当于一个mock的数据源）
                    if (StateNodeStatus.DISABLED.toString().equalsIgnoreCase(regCenter.get(event.getKey()))) {
                        for (String each : dataSourceMap.keySet()) {
                            dataSourceMap.put(each, new CircuitBreakerDataSource());
                        }
                    }
                    try {
                        shardingDataSource.renew(configService.loadShardingRuleConfiguration().build(dataSourceMap), configService.loadShardingProperties());
                    } catch (final SQLException ex) {
                        throw new ShardingJdbcException(ex);
                    }
                }
            }
        });
    }
    

> 说明：将某个具体实例的节点的value置为 **disabled** 的命令(基于zookeeper)： **set /orchestration-
spring-namespace-
test/shardingDataSource/state/instances/10.52.16.134@13272@42533e85-9bb1-4484-baa1-2a2f9b2480a6
disabled** ，instances后面的
**10.52.16.134@13272@42533e85-9bb1-4484-baa1-2a2f9b2480a6** 视具体情况而定。

### 3.4 其他节点监听分析

其他节点监听处理和上面两个的处理逻辑几乎大同小异，监听UPDATED事件，然后从注册中心加载最新的配置后刷新数据；

