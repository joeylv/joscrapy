  * 1 绑定（Bindings）
  * 2 直接交换（Direct exchange）
  * 3 多重绑定（Multiple bindings）
  * 4 发送日志（Emitting logs）
  * 5 订阅（Subscribing）
  * 6 案例实战
    * 6.1 发送端
    * 6.2 接受端
  * 7 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

## 绑定（Bindings）

在上一个教程中，我们已经使用过绑定。你可能会记得如下代码：

    
    
    channel.queueBind(queueName, EXCHANGE_NAME, "");
    

绑定是建立交换器和队列之间的关系。这可以简单地理解：队列对该交换器上的消息感兴趣。

为了避免与 basicPublish 方法的参数混淆，我们将其称为 **绑定键** 。下面是我们如何用一个绑定键创建一个绑定：

    
    
    channel.queueBind(queueName, EXCHANGE_NAME, "black");
    

绑定键的意义依赖于交换器的类型。以前我们以前使用的 fanout 类型的交换器可以忽略此参数。

## 直接交换（Direct exchange）

我们从上一个教程的日志记录系统向所有消费者广播所有消息。现在，我们需要一个将错误日志消息写入磁盘，而不会把硬盘空间浪费警告或消息类型日志消息上。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_direct-exchange.png)

其中，第一个队列与绑定键 orange 绑定，第二个队列有两个绑定，一个绑定键为 black，另一个绑定为 green。在这样的设置中，具有 orange
的交换器的消息将被路由到队列 Q1。具有 black 或 green 的交换器的消息将转到 Q2。所有其他消息将被丢弃。

## 多重绑定（Multiple bindings）

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_direct-exchange-multiple.png)

此外，使用相同的绑定键绑定多个队列是完全合法的。在我们的示例中，我们可以在 X 和 Q1 之间添加绑定键 black。在这种情况下，direct
类型的交换器将消息广播到所有匹配的队列 Q1 和 Q2。

## 发送日志（Emitting logs）

我们将使用 direct 类型的交换器进行日志记录系统。

    
    
    channel.exchangeDeclare(EXCHANGE_NAME, "direct");
    

现在，我们准备发送一条消息：

    
    
    channel.basicPublish(EXCHANGE_NAME, severity, null, message.getBytes());
    

为了简化代码，我们假定 ‘severity’ 是 ‘info’， ‘warning’， ‘error’ 中的一个。

## 订阅（Subscribing）

接收消息将像上一个教程一样工作，除了一个例外 – 我们给我们所感兴趣的严重性类型的日志创建一个绑定。

    
    
    String queueName = channel.queueDeclare().getQueue();
    
    for(String severity : argv){    
      channel.queueBind(queueName, EXCHANGE_NAME, severity);
    }
    

## 案例实战

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_python-four.png)

### 发送端

发送端，连接到 RabbitMQ，发送一条数据，然后退出。

    
    
    public class EmitLogDirect {
        private static final String EXCHANGE_NAME = "direct_logs";
        private static final String[] LOG_LEVEL_ARR = {"debug", "info", "error"};  
    
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
            channel.exchangeDeclare(EXCHANGE_NAME, "direct");
            // 发送消息  
            for (int i = 0; i < 10; i++)  {  
                int rand = new Random().nextInt(3);
                String severity  = LOG_LEVEL_ARR[rand];
                String message = "Liang-MSG log : [" +severity+ "]" + UUID.randomUUID().toString();  
                // 发布消息至交换器
                channel.basicPublish(EXCHANGE_NAME, severity, null, message.getBytes());  
                System.out.println(" [x] Sent "" + message + """);  
            }  
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

### 接受端

接受端，不断等待服务器推送消息，然后在控制台输出。

    
    
    public class ReceiveLogsDirect {
        private static final String EXCHANGE_NAME = "direct_logs";
        private static final String[] LOG_LEVEL_ARR = {"debug", "info", "error"};  
    
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
            channel.exchangeDeclare(EXCHANGE_NAME, "direct");
            // 设置日志级别
            int rand = new Random().nextInt(3);
            String severity  = LOG_LEVEL_ARR[rand];
            // 创建一个非持久的、唯一的、自动删除的队列
            String queueName = channel.queueDeclare().getQueue();
            // 绑定交换器和队列
            // queueBind(String queue, String exchange, String routingKey)
            // 参数1 queue ：队列名
            // 参数2 exchange ：交换器名
            // 参数3 routingKey ：路由键名
            channel.queueBind(queueName, EXCHANGE_NAME, severity);
            // 创建队列消费者
            final Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String consumerTag, Envelope envelope,
                                           AMQP.BasicProperties properties, byte[] body) throws IOException {
                    String message = new String(body, "UTF-8");
                    System.out.println(" [x] Received "" + message + """);
                }
            };
            channel.basicConsume(queueName, true, consumer);
        }
    }
    

现在，做一个实验，我们开启三个 ReceiveLogsDirect 工作程序：ReceiveLogsDirect1 、ReceiveLogsDirect2
与 ReceiveLogsDirect3。

ReceiveLogsDirect1

    
    
    [*] Waiting for messages. To exit press CTRL+C
    [*] LOG LEVEL : info
    [x] Received "Liang-MSG log : [info]0dd0ae0c-bf74-4aa9-9852-394e65fbf939"
    [x] Received "Liang-MSG log : [info]b2b032f6-e907-4c95-b676-1790204c5f73"
    [x] Received "Liang-MSG log : [info]14482461-e432-4866-9eb5-a28f4edeb47f"
    

ReceiveLogsDirect2

    
    
    [*] Waiting for messages. To exit press CTRL+C
    [*] LOG LEVEL : error
    [x] Received "Liang-MSG log : [error]493dce2a-7ce1-4111-953c-99ab2564a2d0"
    [x] Received "Liang-MSG log : [error]2446dd80-d5f0-4d39-888f-31579b9d2724"
    [x] Received "Liang-MSG log : [error]fe8219e0-5548-40ba-9810-d922d1b03dd8"
    [x] Received "Liang-MSG log : [error]797b6d0e-9928-4505-9c76-56043322b1f0"
    

ReceiveLogsDirect3

    
    
    [*] Waiting for messages. To exit press CTRL+C
    [*] LOG LEVEL : debug
    [x] Received "Liang-MSG log : [debug]c05eee3e-b820-4b69-9c3f-c2bbded85195"
    [x] Received "Liang-MSG log : [debug]4645c9ba-4070-41d7-adc9-7f8b2df1e3c8"
    [x] Received "Liang-MSG log : [debug]d3d3ad5c-8f97-49ea-8fd6-c434790e40eb"
    

此时，ReceiveLogsDirect1 、ReceiveLogsDirect2 与 ReceiveLogsDirect3 同时收到了属于自己级别的消息。

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-action>

