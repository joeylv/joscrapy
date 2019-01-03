  * 1 准备工作
    * 1.1 发送端
    * 1.2 接收端
  * 2 轮询调度（Round-robin dispatching）
  * 3 消息应答（Message acknowledgment）
    * 3.1 发送端
    * 3.2 接收端
  * 4 消息持久化（Message durability）
  * 5 公平转发（Fair dispatch）
  * 6 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

工作队列，又称任务队列，主要思想是避免立即执行资源密集型任务，并且必须等待完成。相反地，我们进行任务调度，我们将一个任务封装成一个消息，并将其发送到队列。工作进行在后台运行不断的从队列中取出任务然后执行。当你运行了多个工作进程时，这些任务队列中的任务将会被工作进程共享执行。

这个概念在 Web 应用程序中特别有用，在短时间 HTTP 请求内需要执行复杂的任务。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201810/rabbitmq_python-two.png)

## 准备工作

现在，假装我们很忙，我们使用 Thread.sleep 来模拟耗时的任务。

### 发送端

    
    
    public class NewTask {
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
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 发送消息
            for (int i = 0; i < 10; i++) {  
                String message = "Liang:" + i;
                channel.basicPublish("", QUEUE_NAME, null, message.getBytes());  
                System.out.println(" [x] Sent "" + message + """);  
            }  
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

### 接收端

    
    
    public class Worker {
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
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 创建队列消费者
            final Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String consumerTag, Envelope envelope,
                                           AMQP.BasicProperties properties, byte[] body) throws IOException {
                    String message = new String(body, "UTF-8");
    
                    System.out.println(" [x] Received "" + message + """);
                    try {
                        doWork(message);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            };
            // acknowledgment is covered below
            boolean autoAck = true;
            channel.basicConsume(QUEUE_NAME, autoAck, consumer);
        }
    
        private static void doWork(String task) throws InterruptedException {
            String[] taskArr = task.split(":");
            TimeUnit.SECONDS.sleep(Long.valueOf(taskArr[1]));
        }
    }
    

## 轮询调度（Round-robin dispatching）

使用任务队列的优点之一是能够轻松地并行工作。如果我们积压了很多任务，我们可以增加更多的工作进程，这样可以轻松扩展。

首先，我们尝试在同一时间运行两个工作进程实例。他们都会从队列中获取消息，但是究竟如何？让我们来看看。

你需要三个控制台打开。两个将运行工作程序。这些控制台将是我们两个消费者 – C1 和 C2。

Worker1

    
    
     [x] Received "Liang:0"
     [x] Received "Liang:2"
     [x] Received "Liang:4"
     [x] Received "Liang:6"
     [x] Received "Liang:8"
    
    

Worker2

    
    
    [x] Received "Liang-1"
    [x] Received "Liang-3"
    [x] Received "Liang-5"
    [x] Received "Liang-7"
    [x] Received "Liang-9"
    

再做一个实验，我们开启三个工作程序。

Worker1

    
    
    [x] Received "Liang-0"
    [x] Received "Liang-3"
    [x] Received "Liang-6"
    [x] Received "Liang-9"
    

Worker2

    
    
    [x] Received "Liang-1"
    [x] Received "Liang-4"
    [x] Received "Liang-7"
    

Worker3

    
    
    [x] Received "Liang-2"
    [x] Received "Liang-5"
    [x] Received "Liang-8"
    

我们发现，通过增加更多的工作程序就可以进行并行工作，并且接受的消息平均分配。注意的是，这种分配过程是一次性分配，并非一个一个分配。

默认情况下，RabbitMQ 将会发送的每一条消息按照顺序给下一个消费者。平均每一个消费者将获得相同数量的消息。这种分发消息的方式叫做轮询调度。

## 消息应答（Message acknowledgment）

执行一个任务可能需要几秒钟。你可能会想，如果一个消费者开始一个长期的任务，并且只有部分地完成它，会发生什么事情？使用我们当前的代码，一旦 RabbitMQ
向客户发送消息，它立即将其从内存中删除。在这种情况下，如果你杀死正在执行任务的某个工作进程，我们会丢失它正在处理的信息。我们还会丢失所有发送给该特定工作进程但尚未处理的消息。

但是，我们不想失去任何消息。如果某个工作进程被杀死时，我们希望把这个任务交给另一个工作进程。

为了确保消息永远不会丢失，RabbitMQ 支持消息应答。从消费者发送一个确认信息告诉 RabbitMQ
已经收到消息并已经被接收和处理，然后RabbitMQ 可以自由删除它。

如果消费者被杀死而没有发送应答，RabbitMQ
会认为该信息没有被完全的处理，然后将会重新转发给别的消费者。如果同时有其他消费者在线，则会迅速将其重新提供给另一个消费者。这样就可以确保没有消息丢失，即使工作进程偶尔也会死亡。

默认情况下，消息应答是开启的。在前面的例子中，我们通过 autoAck = true 标志明确地将它们关闭。现在是一旦完成任务，将此标志设置为false
，并向工作进程发送正确的确认。

### 发送端

    
    
    public class AckNewTask {
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
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 发送消息
            for (int i = 0; i < 10; i++) {  
                String message = "Liang:" + i;  
                channel.basicPublish("", QUEUE_NAME, null, message.getBytes());  
                System.out.println(" [x] Sent "" + message + """);  
            }  
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

### 接收端

    
    
    public class AckWorker {
        private final static String QUEUE_NAME = "hello";
    
        public static void main(String[] args) throws IOException, TimeoutException {
            // 创建连接
            ConnectionFactory factory = new ConnectionFactory();
            // 设置 RabbitMQ 的主机名
            factory.setHost("localhost");
            // 创建一个连接
            Connection connection = factory.newConnection();
            // 创建一个通道
            final Channel channel = connection.createChannel();
            // 指定一个队列
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 创建队列消费者
            final Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties,
                        byte[] body) throws IOException {
                    String message = new String(body, "UTF-8");
    
                    System.out.println(" [x] Received "" + message + """);
                    try {
                        doWork(message);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    } finally{
                        // 每次处理完成一个消息后，手动发送一次应答。  
                        channel.basicAck(envelope.getDeliveryTag(), false);
                    }
                }
            };
            boolean autoAck = false;
            channel.basicConsume(QUEUE_NAME, autoAck, consumer);
        }
    
        private static void doWork(String task) throws InterruptedException {
            String[] taskArr = task.split(":");
            TimeUnit.SECONDS.sleep(Long.valueOf(taskArr[1]));
        }
    }
    

其中，首先关闭自动应答机制。

    
    
    boolean ack = false ;  
    channel.basicConsume(QUEUE_NAME, ack, consumer);  
    

然后，每次处理完成一个消息后，手动发送一次应答。

    
    
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
    

此时，我们开启三个工作进程，然后，随机关闭一个工作进程，观察输出结果。

## 消息持久化（Message durability）

我们已经学会了如何确保即使消费者死了，任务也不会丢失。但是如果 RabbitMQ 服务器停止，我们的任务仍然会丢失。

当 RabbitMQ 退出或崩溃时，将会丢失所有的队列和信息，除非你告诉它不要丢失。需要两件事来确保消息不丢失：我们需要分别将队列和消息标记为持久化。

首先，我们需要确保 RabbitMQ 永远不会失去我们的队列。为了这样做，我们需要将其声明为持久化的。

    
    
    boolean durable = true;
    channel.queueDeclare("hello_dirable", durable, false, false, null);
    

其次，我们需要标识我们的信息为持久化的。通过设置 MessageProperties 值为 PERSISTENT_TEXT_PLAIN。

    
    
    channel.basicPublish("", "hello_dirable", MessageProperties.PERSISTENT_TEXT_PLAIN, message.getBytes());
    

注意的是，在RabbitMQ 中，已经存在的队列，我们无法修改其属性。

此时，我们开启一个发送者发送消息，然后，关闭 RabbitMQ 服务，再重新开启，观察输出结果。

## 公平转发（Fair dispatch）

您可能已经注意到，调度仍然无法正常工作。例如在两个工作线程的情况下，一个工作线程将不断忙碌，另一个工作人员几乎不会做任何工作。那么，RabbitMQ
不知道什么情况，还会平均分配消息。

这是因为当消息进入队列时，RabbitMQ 只会分派消息。它不看消费者的未确认消息的数量。它只是盲目地向第 n 个消费者发送每个第 n 个消息。

为了解决这样的问题，我们可以使用 basicQos 方法，并将传递参数为 prefetchCount = 1。

这样告诉 RabbitMQ
不要一次给一个工作线程多个消息。换句话说，在处理并确认前一个消息之前，不要向工作线程发送新消息。相反，它将发送到下一个还不忙的工作线程。

    
    
    public class FairNewTask {
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
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            // 公平转发
            int prefetchCount = 1;  
            channel.basicQos(prefetchCount);  
            // 发送消息
            for (int i = 10; i >0; i--) {  
                String message = "Liang:" + i;
                channel.basicPublish("", QUEUE_NAME, null, message.getBytes());  
                System.out.println(" [x] Sent "" + message + """);  
            }  
            // 关闭频道和连接  
            channel.close();
            connection.close();
        }
    }
    

其中，使用 basicQos 方法，并将传递参数为 prefetchCount = 1。

    
    
    int prefetchCount = 1;
    channel.basicQos(prefetchCount) ;
    

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-action>

