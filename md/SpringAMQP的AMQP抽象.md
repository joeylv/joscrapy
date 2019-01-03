  * 1 介绍
  * 2 消息
  * 3 交换器
  * 4 队列
  * 5 绑定

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

## 介绍

Spring AMQP 由几个模块组成，这些模块有：spring-amqp 和 spring-rabbit。spring-amqp 模块包含
org.springframework.amqp.core 包。在这个包中，你将找到代表核心 AMQP
“模式”的类。其目的是提供不依赖的泛型抽象的任何特定的 AMQP broker 实现或客户端库。这些抽象由特定的模块实现，例如 spring-
rabbit。目前，只有一个 RabbitMQ 实现。

## 消息

在 0-8 和 0-9-1 AMQP 规范不定义 Message 类或接口。相反地，当执行如 basicPublish()
方法时，其内容将作为二进制数组传递，并附加消息的其他属性作为单独的参数。Spring AMQP 将 Message 类定义为更共通的 AMQP
域模型的一部分表示。Message 类的目的是简单地将内容和属性封装在一个单一的实例中，以便 AMQP API 的其余部分可以简单地调用。

    
    
    public class Message {
        private final MessageProperties messageProperties;
        private final byte[] body;
        public Message(byte[] body, MessageProperties messageProperties) {
            this.body = body;
            this.messageProperties = messageProperties;
        }
        public byte[] getBody() {
            return this.body;
        }
        public MessageProperties getMessageProperties() {
            return this.messageProperties;
        }
    }
    

MessageProperties 接口定义了几个常见的属性，如 messageId， timestamp， contentType
等等。这些属性也可以用通过调用 setHeader（String key，Object value） 方法来扩展。

## 交换器

在虚拟主机中，每个交换器将具有唯一的名称以及一些其他属性。

    
    
    public interface Exchange {
        String getName();
        String getExchangeType();
        boolean isDurable();
        boolean isAutoDelete();
        Map<String, Object> getArguments();
    }
    

它有许多子类：AbstractExchange, CustomExchange, DirectExchange, FanoutExchange,
HeadersExchange, TopicExchange。

## 队列

Queue 类表示消费者从消息队列接收消息的组件。

    
    
    public class Queue {
        private final String name;
        private volatile boolean durable;
        private volatile boolean exclusive;
        private volatile boolean autoDelete;
        private volatile Map<String, Object> arguments;
        /**
         * The queue is durable, non-exclusive and non auto-delete.
         *
         * @param name the name of the queue.
         */
        public Queue(String name) {
            this(name, true, false, false);
        }
    // Getters and Setters omitted for brevity
    }
    

## 绑定

假设一个生产者发送到一个交换器，而一个消费者从一个队列接收消息。此时，将队列绑定到交换器对于连接这些生产者和消费者至关重要。在 Spring AMQP
中，我们定义一个 Binding 类来表示这些连接。

你可以使用 DirectExchange 绑定一个队列。

    
    
    new Binding(someQueue, someDirectExchange, "foo.bar")
    

你可以使用 TopicExchange 绑定一个队列。

    
    
    new Binding(someQueue, someTopicExchange, "foo.*")
    

你可以使用 FanoutExchange 绑定一个队列。

    
    
    new Binding(someQueue, someFanoutExchange)
    

同时，也提供了 BindingBuilder 来构建 “流式的 API” 风格。

    
    
    Binding b = BindingBuilder.bind(someQueue).to(someTopicExchange).with("foo.*");
    

