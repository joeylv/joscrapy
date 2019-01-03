  * 1 准备
  * 2 介绍
  * 3 常见术语
    * 3.1 生产者
    * 3.2 队列
    * 3.3 消费者
  * 4 案例实战 – 使用 Java 客户端实现 “Hello World!”
    * 4.1 准备工作
    * 4.2 发送端
    * 4.3 接受端
  * 5 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

## 准备

本教程假定 RabbitMQ 已在标准端口（5672） 的 localhost 上安装并运行。如果使用不同的主机，端口或凭据，连接设置将需要调整。

## 介绍

RabbitMQ 是一个消息代理：它接受并转发消息。你可以将其视为邮局：当你将要发布的邮件放在邮箱中时，您可以确信 Postman
先生最终会将邮件发送给收件人。在这个比喻中，RabbitMQ 是一个邮箱，邮局和邮递员。

RabbitMQ 和邮局之间的主要区别在于它不处理纸张，而是接受，存储和转发二进制数据块的消息。

## 常见术语

RabbitMQ 使用一些术语：生产者、队列、消费者。

### 生产者

一个发送消息的程序是一个生产者。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_producer.png)

### 队列

队列类似于邮箱。虽然消息通过 RabbitMQ
在你的应用中传递，但是它们只能存储在队列中。队列只受主机的内存和磁盘限制的限制，它本质上是一个大的消息缓冲区。不同的生产者可以通过同一个队列发送消息，此外，不同的消费者也可以从同一个队列上接收消息。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_queue.png)

### 消费者

一个等待接收消息的程序是一个消费者。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_consumer.png)

整个过程非常简单，生产者创建消息，消费者接收这些消息。你的应用程序既可以作为生产者向其他应用程序发送消息，也可以作为消费者，等待接收其他应用程序的消息。其中，存储消息的是消息队列，它类似于邮箱，消息通过消息队列进行投递。

## 案例实战 – 使用 Java 客户端实现 “Hello World!”

在本教程的这一部分，我们将用 Java 编写一个 “Hello World”
的消息传递案例，它涉及两个程序：发送单个消息的生产者，以及接收消息并将其打印出来的消费者。

在下图中，“P”是我们的生产者，“C”是我们的消费者。中间的框是队列 – RabbitMQ 代表消费者的消息缓冲区。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_python-one.png)

### 准备工作

使用 Maven 进行依赖管理。

    
    
    <dependency>
        <groupId>com.rabbitmq</groupId>
        <artifactId>amqp-client</artifactId>
        <version>3.6.3</version>
    </dependency>
    

### 发送端

我们会调用生产者发送消息给消费者。生产者连接到 RabbitMQ，发送一条数据，然后退出。

    
    
    public class Send {
        private final static String QUEUE_NAME = "hello";
    
        public static void main(String[] args) throws IOException, TimeoutException {
            // 创建连接
            ConnectionFactory factory = new ConnectionFactory();
            // 设置 RabbitMQ 的主机名
            factory.setHost("localhost");
            // 创建一个连接
            Connection connection = factory.newConnection();
            // 创建一个通道
            Channel channel = connection.createChannel();    
            // 指定一个队列
            // queueDeclare(String queue, boolean durable, boolean exclusive, boolean autoDelete, Map<String, Object> arguments)
            // 参数1 queue ：队列名
            // 参数2 durable ：是否持久化
            // 参数3 exclusive ：仅创建者可以使用的私有队列，断开后自动删除
            // 参数4 autoDelete : 当所有消费客户端连接断开后，是否自动删除队列
            // 参数5 arguments
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 发送消息
            String message = "Hello World!";
            // basicPublish(String exchange, String routingKey, BasicProperties props, byte[] body)
            // 参数1 exchange ：交换器
            // 参数2 routingKey ： 路由键
            // 参数3 props ： 消息的其他参数
            // 参数4 body ： 消息体
            channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
            System.out.println(" [x] Sent "" + message + """);
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

声明队列是幂等的, 队列只会在它不存在时才会被创建，多次声明并不会重复创建。消息内容是一个字节数组，也就意味着可以传递任何数据。

### 接受端

这就是我们的消费者。它不断等待消息队列推送消息，然后在控制台输出。

    
    
    public class Recv {
        private final static String QUEUE_NAME = "hello";
    
        public static void main(String[] args) throws IOException, TimeoutException {
            // 创建连接
            ConnectionFactory factory = new ConnectionFactory();
            // 设置 RabbitMQ 的主机名
            factory.setHost("localhost");
            // 创建一个连接
            Connection connection = factory.newConnection();
            // 创建一个通道
            Channel channel = connection.createChannel();
            // 指定一个队列
            // queueDeclare(String queue, boolean durable, boolean exclusive, boolean autoDelete, Map<String, Object> arguments)
            // 参数1 queue ：队列名
            // 参数2 durable ：是否持久化
            // 参数3 exclusive ：仅创建者可以使用的私有队列，断开后自动删除
            // 参数4 autoDelete : 当所有消费客户端连接断开后，是否自动删除队列
            // 参数5 arguments
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            System.out.println(" [*] Waiting for messages. To exit press CTRL+C");
            // 创建队列消费者
            Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String consumerTag, Envelope envelope,
                                           AMQP.BasicProperties properties, byte[] body) throws IOException {
                    String message = new String(body, "UTF-8");
                    System.out.println(" [x] Received "" + message + """);
                }
            };
            // basicConsume(String queue, boolean autoAck, Consumer callback)
            // 参数1 queue ：队列名
            // 参数2 autoAck ： 是否自动ACK
            // 参数3 callback ： 消费者对象的一个接口，用来配置回调
            channel.basicConsume(QUEUE_NAME, true, consumer);
        }
    }
    

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-action>

