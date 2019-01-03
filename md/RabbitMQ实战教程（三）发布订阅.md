  * 1 交换器（Exchanges）
  * 2 临时队列（Temporary queues）
  * 3 绑定（Bindings）
  * 4 案例实战
    * 4.1 发送端
    * 4.2 接受端
  * 5 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

为了说明这种模式，我们将建立一个简单的日志系统。这个系统将由两个程序组成，第一个将发出日志消息，第二个将接收并处理日志消息。在我们的日志系统中，每一个运行的接收程序的副本都会收到日志消息。

## 交换器（Exchanges）

在本教程的前面部分，我们主要介绍了发送者和接受者，发送者发送消息给 RabbitMQ 队列，接收者从 RabbitMQ
队列获取消息。在这一篇教程，我们会引入交换器，展示 RabbitMQ 的完整的消息模型。

让我们快速了解在前面的教程中介绍的内容：

  * 生产者是发送消息的用户应用程序。
  * 队列是存储消息的缓冲区。
  * 消费者是接收消息的用户应用程序。

RabbitMQ 消息模型的核心思想是，生产者不直接发送任何消息给队列。实际上，一般的情况下，生产者甚至不知道消息应该发送到哪些队列。

相反的，生产者只能将信息发送到交换器。交换器是非常简单的。它一边收到来自生产者的消息，另一边将它们推送到队列。交换器必须准确知道接收到的消息如何处理。是否被添加到一个特定的队列吗？是否应该追加到多个队列？或者是否应该被丢弃？这些规则通过交换器类型进行定义。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_exchanges.png)

交换器一共四种类型：direct、topic、headers、fanout。目前，我们先关注 fanout 类型的交换器。

    
    
    channel.exchangeDeclare("logs", "fanout");
    

fanout 类型的交换器非常简单，它只是将所有收到的消息广播到所有它所知道的队列。

在上一个教程中，我们不知道交换器，但仍然能够发送消息到队列。这是因为我们使用了一个默认的交换器，我们用空的字符串（“”）。

    
    
    // 参数1 exchange ：交换器
    // 参数2 routingKey ： 路由键
    // 参数3 props ： 消息的其他参数
    // 参数4 body ： 消息体
    channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
    

其中，第一个参数表示交换器的名称，我们设置为””，第二个参数表示消息由路由键决定发送到哪个队列。

现在，我们可以发布消息到我们命名的交换器。

    
    
    channel.basicPublish("logs", "", null, message.getBytes());
    

## 临时队列（Temporary queues）

之前，我们都是使用的队列指定了一个特定的名称。不过，对于我们的日志系统而言，我们并不关心队列的名称。我们想要接收到所有的消息，而且我们也只对当前正在传递的消息感兴趣。要解决我们需求，需要做两件事。

首先，每当我们连接到 RabbitMQ，我们需要一个新的空的队列。为此，我们可以创建一个具有随机名称的队列，或者甚至更好 –
让服务器或者，让服务器为我们选择一个随机队列名称。

其次，一旦消费者与 RabbitMQ 断开，消费者所接收的那个队列应该被自动删除。

在 Java 客户端中，我们可以使用 queueDeclare() 方法来创建一个非持久的、唯一的、自动删除的队列，且队列名称由服务器随机产生。

    
    
    String queueName = channel.queueDeclare().getQueue();
    

此时，queueName 包含一个随机队列名称。

## 绑定（Bindings）

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_bindings.png)

我们已经创建了一个 fanout 类型的交换器和队列。现在，我们需要告诉交换器发送消息到我们的队列。交换器和队列之间的关系称为绑定。

    
    
    // 绑定交换器和队列
    // 参数1 queue ：队列名
    // 参数2 exchange ：交换器名
    // 参数3 routingKey ：路由键名
    channel.queueBind(queueName, "logs", "");
    

## 案例实战

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_python-three-overall.png)

### 发送端

发送端，连接到 RabbitMQ，发送一条数据，然后退出。

    
    
    public class EmitLog {
        private static final String EXCHANGE_NAME = "logs";
    
        public static void main(String[] args) throws IOException, TimeoutException {
            // 创建连接
            ConnectionFactory factory = new ConnectionFactory();
            // 设置 RabbitMQ 的主机名
            factory.setHost("localhost");
            // 创建一个连接
            Connection connection = factory.newConnection();
            // 创建一个通道
            Channel channel = connection.createChannel();    
            // 指定一个交换器
            channel.exchangeDeclare(EXCHANGE_NAME, "fanout");
            // 发送消息  
            String message = "Liang-MSG log.";  
            channel.basicPublish(EXCHANGE_NAME, "", null, message.getBytes());  
            System.out.println(" [x] Sent "" + message + """);  
    
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

### 接受端

接受端，不断等待服务器推送消息，然后在控制台输出。

    
    
    public class ReceiveLogs {
        private static final String EXCHANGE_NAME = "logs";
    
        public static void main(String[] args) throws IOException, TimeoutException {
            // 创建连接
            ConnectionFactory factory = new ConnectionFactory();
            // 设置 RabbitMQ 的主机名
            factory.setHost("localhost");
            // 创建一个连接
            Connection connection = factory.newConnection();
            // 创建一个通道
            Channel channel = connection.createChannel();
            // 指定一个交换器
            channel.exchangeDeclare(EXCHANGE_NAME, "fanout");
            // 创建一个非持久的、唯一的、自动删除的队列
            String queueName = channel.queueDeclare().getQueue();
            // 绑定交换器和队列
            // queueBind(String queue, String exchange, String routingKey)
            // 参数1 queue ：队列名
            // 参数2 exchange ：交换器名
            // 参数3 routingKey ：路由键名
            channel.queueBind(queueName, EXCHANGE_NAME, "");
            // 创建队列消费者
            final Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties,
                        byte[] body) throws IOException {
                    String message = new String(body, "UTF-8");
                    System.out.println(" [x] Received "" + message + """);
                }
            };
            channel.basicConsume(queueName, true, consumer);
        }
    }
    

现在，做一个实验，我们开启两个 ReceiveLogs 工作程序：ReceiveLogs1 与 ReceiveLogs2。

ReceiveLogs1

    
    
     [x] Received "Liang-MSG log."
    

ReceiveLogs 2

    
    
     [x] Received "Liang-MSG log."
    

此时，ReceiveLogs1 与 ReceiveLogs2 同时收到了消息。

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-action>

