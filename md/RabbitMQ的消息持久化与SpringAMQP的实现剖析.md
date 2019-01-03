  * 1 原生的实现方式
  * 2 Spring AMQP 的实现方式

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

要从奔溃的 RabbitMQ 中恢复的消息，我们需要做消息持久化。如果消息要从 RabbitMQ 奔溃中恢复，那么必须满足三点，且三者缺一不可。

  * 交换器必须是持久化。
  * 队列必须是持久化的。
  * 消息必须是持久化的。

## 原生的实现方式

原生的 RabbitMQ 客户端需要完成三个步骤。

第一步，交换器的持久化。

    
    
    // 参数1 exchange ：交换器名
    // 参数2 type ：交换器类型
    // 参数3 durable ：是否持久化
    channel.exchangeDeclare(EXCHANGE_NAME, "topic", true);
    

第二步，队列的持久化。

    
    
    // 参数1 queue ：队列名
    // 参数2 durable ：是否持久化
    // 参数3 exclusive ：仅创建者可以使用的私有队列，断开后自动删除
    // 参数4 autoDelete : 当所有消费客户端连接断开后，是否自动删除队列
    // 参数5 arguments
    channel.queueDeclare(QUEUE_NAME, true, false, false, null);
    

第三步，消息的持久化。

    
    
    // 参数1 exchange ：交换器
    // 参数2 routingKey ： 路由键
    // 参数3 props ： 消息的其他参数,其中 MessageProperties.PERSISTENT_TEXT_PLAIN 表示持久化
    // 参数4 body ： 消息体
    channel.basicPublish("", queue_name, MessageProperties.PERSISTENT_TEXT_PLAIN, message.getBytes());
    

## Spring AMQP 的实现方式

Spring AMQP 是对原生的 RabbitMQ 客户端的封装。一般情况下，我们只需要定义交换器的持久化和队列的持久化。

其中，交换器的持久化配置如下。

    
    
    // 参数1 name ：交互器名
    // 参数2 durable ：是否持久化
    // 参数3 autoDelete ：当所有消费客户端连接断开后，是否自动删除队列
    new TopicExchange(name, durable, autoDelete)
    

此外，还需要再配置队列的持久化。

    
    
    // 参数1 name ：队列名
    // 参数2 durable ：是否持久化
    // 参数3 exclusive ：仅创建者可以使用的私有队列，断开后自动删除
    // 参数4 autoDelete : 当所有消费客户端连接断开后，是否自动删除队列
    new Queue(name, durable, exclusive, autoDelete);
    

至此，RabbitMQ 的消息持久化配置完毕。

那么，消息的持久化难道不需要配置么？确实如此，我们来看下源码。

一般情况下，我们会通过这种方式发送消息。

    
    
    rabbitTemplate.convertAndSend(exchange, routeKey, message);
    

其中，调用了 convertAndSend(String exchange, String routingKey, final Object object)
方法。

    
    
    @Override
    public void convertAndSend(String exchange, String routingKey, final Object object) throws AmqpException {
        convertAndSend(exchange, routingKey, object, (CorrelationData) null);
    }
    

接着，用调用了 convertAndSend(String exchange, String routingKey, final Object
object, CorrelationData correlationData) 方法。

    
    
    public void convertAndSend(String exchange, String routingKey, final Object object, CorrelationData correlationData) throws AmqpException {
            send(exchange, routingKey, convertMessageIfNecessary(object), correlationData);
        }
    

此时，最关键的方法出现了，它是 convertMessageIfNecessary(final Object object)。

    
    
    protected Message convertMessageIfNecessary(final Object object) {
        if (object instanceof Message) {
            return (Message) object;
        }
        return getRequiredMessageConverter().toMessage(object, new MessageProperties());
    }
    

其中，关键的是 MessageProperties 类,它持久化的策略是
MessageDeliveryMode.PERSISTENT，因此它会初始化时默认消息是持久化的。

    
    
    public class MessageProperties implements Serializable {
        public MessageProperties() {
            this.deliveryMode = DEFAULT_DELIVERY_MODE;
            this.priority = DEFAULT_PRIORITY;
        }
    
        static {
            DEFAULT_DELIVERY_MODE = MessageDeliveryMode.PERSISTENT;
            DEFAULT_PRIORITY = Integer.valueOf(0);
        }
    }
    

