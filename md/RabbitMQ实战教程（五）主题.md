  * 1 主题交换（Topic exchange）
  * 2 案例实战
    * 2.1 发送端
    * 2.2 接受端
  * 3 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

## 主题交换（Topic exchange）

使用 topic
类型的交换器，不能有任意的绑定键，它必须是由点隔开的一系列的标识符组成。标识符可以是任何东西，但通常它们指定与消息相关联的一些功能。其中，有几个有效的绑定键，例如
“stock.usd.nyse”， “nyse.vmw”， “quick.orange.rabbit”。可以有任何数量的标识符，最多可达 255 个字节。

topic 类型的交换器和 direct
类型的交换器很类似，一个特定路由的消息将被传递到与匹配的绑定键绑定的匹配的所有队列。关于绑定键有两种有两个重要的特殊情况：

    
    
    * 可以匹配一个标识符。
    # 可以匹配零个或多个标识符。
    

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_python-five.png)

在这个例子中，我们将发送所有描述动物的消息。消息将使用由三个字（两个点）组成的绑定键发送。绑定键中的第一个字将描述速度，第二个颜色和第三个种类：“..”。其中，
Q1 对所有的橙色动物感兴趣。而 Q2 想听听有关兔子的一切，以及关于懒惰动物的一切。

如果我们违反合同并发送一个或四个字的消息，如 “quick.orange.male.rabbit”
会发生什么？那么，这些消息将不会匹配任何绑定，并将被丢失。

topic 类型的交换器是强大的，可以实现其他类型的交换器。

当一个队列与“＃”绑定绑定键时，它将接收所有消息，类似 fanout 类型的交换器。

当一个队列与 `“*”` 和 `“＃”` 在绑定中不被使用时，类似 direct 类型的交换器。

## 案例实战

### 发送端

发送端，连接到 RabbitMQ，发送一条数据，然后退出。

    
    
    public class EmitLogTopic {
        private static final String EXCHANGE_NAME = "topic_logs";
        private static final String[] LOG_LEVEL_ARR = {"dao.debug", "dao.info", "dao.error",
                "service.debug", "service.info", "service.error",
                "controller.debug", "controller.info", "controller.error"};
    
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
            channel.exchangeDeclare(EXCHANGE_NAME, "topic");
            // 发送消息  
            for (String severity : LOG_LEVEL_ARR) {
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

    
    
    public class ReceiveLogsTopic {
        private static final String EXCHANGE_NAME = "topic_logs";
        private static final String[] LOG_LEVEL_ARR = {"#", "dao.error", "*.error", "dao.*", "service.#", "*.controller.#"};  
    
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
            channel.exchangeDeclare(EXCHANGE_NAME, "topic");
            // 设置日志级别
            int rand = new Random().nextInt(5);
            String severity  = LOG_LEVEL_ARR[rand];
            // 创建一个非持久的、唯一的、自动删除的队列
            String queueName = channel.queueDeclare().getQueue();
            // 绑定交换器和队列
            channel.queueBind(queueName, EXCHANGE_NAME, severity);
            // 打印
            System.out.println(" [*] LOG INFO : " + severity);
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
    

现在，做一个实验，我们开启三个 ReceiveLogsTopic 工作程序：ReceiveLogsTopic1、 ReceiveLogsTopic2 与
ReceiveLogsTopic3。

ReceiveLogsTopic1

    
    
    [*] LOG INFO : dao.error
    [x] Received "Liang-MSG log : [dao.error]041cd8ba-df7d-4d20-a11f-ba21a0c2a02a"
    

ReceiveLogsTopic2

    
    
    [*] LOG INFO : *.error
    [x] Received "Liang-MSG log : [dao.error]041cd8ba-df7d-4d20-a11f-ba21a0c2a02a"
    [x] Received "Liang-MSG log : [service.error]e3565f12-9782-4c22-a91c-f513f31b037d"
    [x] Received "Liang-MSG log : [controller.error]4436101a-3346-41f6-a9af-b8a4fbda451e"
    

ReceiveLogsTopic3

    
    
    [*] LOG INFO : #
    [x] Received "Liang-MSG log : [dao.debug]4eb08245-2c05-490b-a5a5-2742cb70d831"
    [x] Received "Liang-MSG log : [dao.info]e9d4073b-1e61-4c6f-b531-ac42eaa346af"
    [x] Received "Liang-MSG log : [dao.error]041cd8ba-df7d-4d20-a11f-ba21a0c2a02a"
    [x] Received "Liang-MSG log : [service.debug]0ec84cbf-47ab-4813-a5db-e57d5e78830e"
    [x] Received "Liang-MSG log : [service.info]2e12e1b7-7a09-4eb7-8ad1-8e53f533121c"
    [x] Received "Liang-MSG log : [service.error]e3565f12-9782-4c22-a91c-f513f31b037d"
    [x] Received "Liang-MSG log : [controller.debug]94e5be72-15f6-496d-84f3-2a107bafc92b"
    [x] Received "Liang-MSG log : [controller.info]62bbe378-617d-4214-beb4-98cc53e73272"
    [x] Received "Liang-MSG log : [controller.error]4436101a-3346-41f6-a9af-b8a4fbda451e"
    

此时，ReceiveLogsTopic1 、ReceiveLogsTopic2 与 ReceiveLogsTopic3 同时收到了属于自己级别的消息。

我们发现，ReceiveLogsTopic1、ReceiveLogsTopic2、ReceiveLogsTopic3、ReceiveLogsTopic4同时收到了属于自己匹配的消息。尤其是ReceiveLogsTopic1
类似于 direct 类型的交换器，ReceiveLogsTopic3 类似于 fanout 类型的交换器。

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-action>

