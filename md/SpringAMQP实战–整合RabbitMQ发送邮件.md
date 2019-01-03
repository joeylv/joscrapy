  * 1 介绍
  * 2 准备
  * 3 实战旅程
    * 3.1 准备工作
    * 3.2 构建消息生产者
    * 3.3 构建消息消费者
  * 4 源代码

> 原文出处：[梁桂钊的博客](http://blog.720ui.com/)

这篇文章，我们开始 Spring AMQP 项目实战旅程。

## 介绍

通过这个项目实战旅程，你会学习到如何使用 Spring Boot 整合 Spring AMQP，并且使用 RabbitMQ
的消息队列机制发送邮件。其中，消息生产者负责将用户的邮件消息发送至消息队列，而消息消费者从消息队列中获取邮件消息进行发送。这个过程，你可以理解成邮局：当你将要发布的邮件放在邮箱中时，您可以确信邮差最终会将邮件发送给收件人。

## 准备

本教程假定 RabbitMQ 已在标准端口（5672） 的 localhost 上安装并运行。如果使用不同的主机，端口，连接设置将需要调整。

    
    
    host = localhost
    ·
    password = guest
    port = 5672
    vhost = /
    

## 实战旅程

### 准备工作

这个实战教程会构建两个工程项目：email-server-producer 与 email-server-consumer。其中，email-server-
producer 是消息生产者工程，email-server-consumer 是消息消费者工程。

**在教程的最后，我会将完整的代码提交至 github 上面，你可以结合源码来阅读这个教程，会有更好的效果。**

现在开始旅程吧。我们使用 Spring Boot 整合 Spring AMQP，并通过 Maven 构建依赖关系。（由于篇幅的问题，我并不会粘贴完整的
pom.xml 配置信息，你可以在 github 源码中查看完整的配置文件）

    
    
    <dependencies>
        <!-- spring boot-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
            <exclusions>
                <exclusion>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-starter-logging</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-amqp</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-context-support</artifactId>
        </dependency>
    
        <dependency>
            <groupId>javax.mail</groupId>
            <artifactId>mail</artifactId>
            <version>${javax.mail.version}</version>
        </dependency>
    
    </dependencies>
    

### 构建消息生产者

![](https://gitee.com/chenssy/blog-home/raw/master/image/201810/spring-amqp-
email-list1.PNG)

我们使用 Java Config 的方式配置消息生产者。

    
    
    @Configuration
    @ComponentScan(basePackages = {"com.lianggzone.rabbitmq"})
    @PropertySource(value = {"classpath:application.properties"})
    public class RabbitMQConfig {
        @Autowired
        private Environment env;
    
        @Bean
        public ConnectionFactory connectionFactory() throws Exception {
            ConnectionFactory connectionFactory = new ConnectionFactory();
            connectionFactory.setHost(env.getProperty("mq.host").trim());
            connectionFactory.setPort(Integer.parseInt(env.getProperty("mq.port").trim()));
            connectionFactory.setVirtualHost(env.getProperty("mq.vhost").trim());
            connectionFactory.setUsername(env.getProperty("mq.username").trim());
            connectionFactory.setPassword(env.getProperty("mq.password").trim());
            return connectionFactory;
        }
    
        @Bean
        public CachingConnectionFactory cachingConnectionFactory() throws Exception {
            return new CachingConnectionFactory(connectionFactory());
        }
    
        @Bean
        public RabbitTemplate rabbitTemplate() throws Exception {
            RabbitTemplate rabbitTemplate = new RabbitTemplate(cachingConnectionFactory());
            rabbitTemplate.setChannelTransacted(true);
            return rabbitTemplate;
        }
    
        @Bean
        public AmqpAdmin amqpAdmin() throws Exception {
            return new RabbitAdmin(cachingConnectionFactory());
        }
    
        @Bean
        Queue queue() {
            String name = env.getProperty("mq.queue").trim();
            // 是否持久化
            boolean durable = StringUtils.isNotBlank(env.getProperty("mq.queue.durable").trim())?
                    Boolean.valueOf(env.getProperty("mq.queue.durable").trim()) : true;
            // 仅创建者可以使用的私有队列，断开后自动删除
            boolean exclusive = StringUtils.isNotBlank(env.getProperty("mq.queue.exclusive").trim())?
                    Boolean.valueOf(env.getProperty("mq.queue.exclusive").trim()) : false;
            // 当所有消费客户端连接断开后，是否自动删除队列
            boolean autoDelete = StringUtils.isNotBlank(env.getProperty("mq.queue.autoDelete").trim())?
                    Boolean.valueOf(env.getProperty("mq.queue.autoDelete").trim()) : false;
            return new Queue(name, durable, exclusive, autoDelete);
        }
    
        @Bean
        TopicExchange exchange() {
            String name = env.getProperty("mq.exchange").trim();
            // 是否持久化
            boolean durable = StringUtils.isNotBlank(env.getProperty("mq.exchange.durable").trim())?
                    Boolean.valueOf(env.getProperty("mq.exchange.durable").trim()) : true;
            // 当所有消费客户端连接断开后，是否自动删除队列
            boolean autoDelete = StringUtils.isNotBlank(env.getProperty("mq.exchange.autoDelete").trim())?
                    Boolean.valueOf(env.getProperty("mq.exchange.autoDelete").trim()) : false;
            return new TopicExchange(name, durable, autoDelete);
        }
    
        @Bean
        Binding binding() {
            String routekey = env.getProperty("mq.routekey").trim();
            return BindingBuilder.bind(queue()).to(exchange()).with(routekey);
        }
    }
    

其中，定义了队列、交换器，以及绑定。事实上，通过这种方式当队列或交换器不存在的时候，Spring AMQP 会自动创建它。（如果你不希望自动创建，可以在
RabbitMQ 的管理后台开通队列和交换器，并注释掉 queue() 方法和 exchange()
方法）。此外，我们为了更好地扩展，将创建队列或交换器的配置信息抽离到了配置文件 application.properties。其中，还包括 RabbitMQ
的配置信息。

    
    
    mq.host=localhost
    mq.username=guest
    mq.password=guest
    mq.port=5672
    mq.vhost=/
    
    mq.exchange=email_exchange
    mq.exchange.durable=true
    mq.exchange.autoDelete=false
    
    mq.queue=email_queue
    mq.queue.durable=true
    mq.queue.exclusive=false
    mq.queue.autoDelete=false
    
    mq.routekey=email_routekey
    

此外，假设一个生产者发送到一个交换器，而一个消费者从一个队列接收消息。此时，将队列绑定到交换器对于连接这些生产者和消费者至关重要。在 Spring AMQP
中，我们定义一个 Binding 类来表示这些连接。我们使用 BindingBuilder 来构建 “流式的 API” 风格。

    
    
    BindingBuilder.bind(queue()).to(exchange()).with(routekey);
    

现在，我们离大功告成已经很近了,需要再定义一个发送邮件任务存入消息队列的方法。此时，为了更好地扩展，我们定义一个接口和一个实现类，基于接口编程嘛。

    
    
    public interface EmailService {
        /**
         * 发送邮件任务存入消息队列
         * @param message
         * @throws Exception
         */
        void sendEmail(String message) throws Exception;
    }
    

它的实现类中重写 sendEmail() 方法，将消息转码并写入到消息队列中。

    
    
    @Service
    public class EmailServiceImpl implements EmailService{
        private static Logger logger = LoggerFactory.getLogger(EmailServiceImpl.class);
    
        @Resource( name = "rabbitTemplate" )
        private RabbitTemplate rabbitTemplate;
    
        @Value("${mq.exchange}")
        private String exchange;
    
        @Value("${mq.routekey}")
        private String routeKey;
    
        @Override
        public void sendEmail(String message) throws Exception {
            try {
                rabbitTemplate.convertAndSend(exchange, routeKey, message);
            }catch (Exception e){
                logger.error("EmailServiceImpl.sendEmail", ExceptionUtils.getMessage(e));
            }
        }
    }
    

那么，我们再模拟一个 RESTful API 接口调用的场景，来模拟真实的场景。

    
    
    @RestController()
    @RequestMapping(value = "/v1/emails")
    public class EmailController {
    
        @Resource
        private EmailService emailService;
    
        @RequestMapping(method = RequestMethod.POST)
        public JSONObject add(@RequestBody JSONObject jsonObject) throws Exception {
            emailService.sendEmail(jsonObject.toJSONString());
            return jsonObject;
        }
    }
    

最后，再写一个 main 方法，将 Spring Boot 服务运行起来吧。

    
    
    @RestController
    @EnableAutoConfiguration
    @ComponentScan(basePackages = {"com.lianggzone.rabbitmq"})
    public class WebMain {
    
        public static void main(String[] args) throws Exception {
            SpringApplication.run(WebMain.class, args);
        }
    }
    

至此，已经大功告成了。我们可以通过 Postman 发送一个 HTTP
请求。（Postman是一款功能强大的网页调试与发送网页HTTP请求的Chrome插件。）

    
    
    {
        "to":"lianggzone@163.com",
        "subject":"email-server-producer",
        "text":"<html><head></head><body><h1>邮件测试</h1><p>hello!this is mail test。</p></body></html>"
    }
    

请参见图示。

![](https://gitee.com/chenssy/blog-home/raw/master/image/201810/spring-amqp-
email.PNG)

来看看 RabbitMQ 的管理后台吧，它会出现一个未处理的消息。（地址：http://localhost:15672/#/queues）

![](https://gitee.com/chenssy/blog-home/raw/master/image/201810/spring-amqp-
email-admin.PNG)

注意的是，千万别向我的邮箱发测试消息哟，不然我的邮箱会邮件爆炸的/(ㄒoㄒ)/ ~~。~~

###  构建消息消费者

![](https://gitee.com/chenssy/blog-home/raw/master/image/201810/spring-amqp-
email-list2.PNG)

完成消息生产者之后，我们再来构建一个消息消费者的工程。同样地，我们使用 Java Config 的方式配置消息消费者。

    
    
    @Configuration
    @ComponentScan(basePackages = {"com.lianggzone.rabbitmq"})
    @PropertySource(value = {"classpath:application.properties"})
    public class RabbitMQConfig {
        @Autowired
        private Environment env;
    
        @Bean
        public ConnectionFactory connectionFactory() throws Exception {
            ConnectionFactory connectionFactory = new ConnectionFactory();
            connectionFactory.setHost(env.getProperty("mq.host").trim());
            connectionFactory.setPort(Integer.parseInt(env.getProperty("mq.port").trim()));
            connectionFactory.setVirtualHost(env.getProperty("mq.vhost").trim());
            connectionFactory.setUsername(env.getProperty("mq.username").trim());
            connectionFactory.setPassword(env.getProperty("mq.password").trim());
            return connectionFactory;
        }
    
        @Bean
        public CachingConnectionFactory cachingConnectionFactory() throws Exception {
            return new CachingConnectionFactory(connectionFactory());
        }
    
        @Bean
        public RabbitTemplate rabbitTemplate() throws Exception {
            RabbitTemplate rabbitTemplate = new RabbitTemplate(cachingConnectionFactory());
            rabbitTemplate.setChannelTransacted(true);
            return rabbitTemplate;
        }
    
        @Bean
        public AmqpAdmin amqpAdmin() throws Exception {
            return new RabbitAdmin(cachingConnectionFactory());
        }
    
        @Bean
        public SimpleMessageListenerContainer listenerContainer(
                @Qualifier("mailMessageListenerAdapter") MailMessageListenerAdapter mailMessageListenerAdapter) throws Exception {
            String queueName = env.getProperty("mq.queue").trim();
    
            SimpleMessageListenerContainer simpleMessageListenerContainer =
                    new SimpleMessageListenerContainer(cachingConnectionFactory());
            simpleMessageListenerContainer.setQueueNames(queueName);
            simpleMessageListenerContainer.setMessageListener(mailMessageListenerAdapter);
            // 设置手动 ACK
            simpleMessageListenerContainer.setAcknowledgeMode(AcknowledgeMode.MANUAL);
            return simpleMessageListenerContainer;
        }
    }
    

聪明的你，应该发现了其中的不同。这个代码中多了一个 listenerContainer()
方法。是的，它是一个监听器容器，用来监听消息队列进行消息处理的。注意的是，我们这里设置手动 ACK
的方式。默认的情况下，它采用自动应答，这种方式中消息队列会发送消息后立即从消息队列中删除该消息。此时，我们通过手动 ACK
方式，如果消费者因宕机或链接失败等原因没有发送 ACK，RabbitMQ 会将消息重新发送给其他监听在队列的下一个消费者，保证消息的可靠性。

当然，我们也定义 application.properties 配置文件。

    
    
    mq.host=localhost
    mq.username=guest
    mq.password=guest
    mq.port=5672
    mq.vhost=/
    
    mq.queue=email_queue
    

此外，我们创建了一个 MailMessageListenerAdapter 类来消费消息。

    
    
    @Component("mailMessageListenerAdapter")
    public class MailMessageListenerAdapter extends MessageListenerAdapter {
    
        @Resource
        private JavaMailSender mailSender;
    
        @Value("${mail.username}")
        private String mailUsername;
    
        @Override
        public void onMessage(Message message, Channel channel) throws Exception {
            try {
                // 解析RabbitMQ消息体
                String messageBody = new String(message.getBody());
                MailMessageModel mailMessageModel = JSONObject.toJavaObject(JSONObject.parseObject(messageBody), MailMessageModel.class);
                // 发送邮件
                String to =  mailMessageModel.getTo();
                String subject = mailMessageModel.getSubject();
                String text = mailMessageModel.getText();
                sendHtmlMail(to, subject, text);
                // 手动ACK
                channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    
        /**
         * 发送邮件
         * @param to
         * @param subject
         * @param text
         * @throws Exception
         */
        private void sendHtmlMail(String to, String subject, String text) throws Exception {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper mimeMessageHelper = new MimeMessageHelper(mimeMessage);
            mimeMessageHelper.setFrom(mailUsername);
            mimeMessageHelper.setTo(to);
            mimeMessageHelper.setSubject(subject);
            mimeMessageHelper.setText(text, true);
            // 发送邮件
            mailSender.send(mimeMessage);
        }
    }
    

在 onMessage() 方法中，我们完成了三件事情：  
1\. 从 RabbitMQ 的消息队列中解析消息体。  
1\. 根据消息体的内容，发送邮件给目标的邮箱。  
1\. 手动应答 ACK，让消息队列删除该消息。

这里，JSONObject.toJavaObject() 方法使用 fastjson 将 json 字符串转换成实体对象
MailMessageModel。注意的是，@Data 是 lombok 类库的一个注解。

    
    
    @Data
    public class MailMessageModel {
        @JSONField(name = "from")
        private String from;
    
        @JSONField(name = "to")
        private String to;
    
        @JSONField(name = "subject")
        private String subject;
    
        @JSONField(name = "text")
        private String text;
    
        @Override
        public String toString() {
            StringBuffer sb = new StringBuffer();
            sb.append("Email{from:").append(this.from).append(", ");
            sb.append("to:").append(this.to).append(", ");
            sb.append("subject:").append(this.subject).append(", ");
            sb.append("text:").append(this.text).append("}");
            return sb.toString();
        }
    }
    

Spring 对 Java Mail 有很好的支持。其中，邮件包括几种类型：简单文本的邮件、 HTML 文本的邮件、 内嵌图片的邮件、
包含附件的邮件。这里，我们封装了一个简单的 sendHtmlMail() 进行邮件发送。

对了，我们还少了一个邮件的配置类。

    
    
    @Configuration
    @PropertySource(value = {"classpath:mail.properties"})
    @ComponentScan(basePackages = {"com.lianggzone.rabbitmq"})
    public class EmailConfig {
        @Autowired
        private Environment env;
    
        @Bean(name = "mailSender")
        public JavaMailSender mailSender() {
            // 创建邮件发送器, 主要提供了邮件发送接口、透明创建Java Mail的MimeMessage、及邮件发送的配置
            JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
            // 如果为普通邮箱, 非ssl认证等
            mailSender.setHost(env.getProperty("mail.host").trim());
            mailSender.setPort(Integer.parseInt(env.getProperty("mail.port").trim()));
            mailSender.setUsername(env.getProperty("mail.username").trim());
            mailSender.setPassword(env.getProperty("mail.password").trim());
            mailSender.setDefaultEncoding("utf-8");
            // 配置邮件服务器
            Properties props = new Properties();
            // 让服务器进行认证,认证用户名和密码是否正确  
            props.put("mail.smtp.auth", "true");
            props.put("mail.smtp.timeout", "25000");
            mailSender.setJavaMailProperties(props);
            return mailSender;
        }
    }
    

这些配置信息，我们在配置文件 mail.properties 中维护。

    
    
    mail.host=smtp.163.com
    mail.port=25
    mail.username=用户名
    mail.password=密码
    

最后，我们写一个 main 方法，将 Spring Boot 服务运行起来吧。

至此，我们也完成了一个消息消费者的工程，它将不断地从消息队列中处理邮件消息。

## 源代码

> 相关示例完整代码： <https://github.com/lianggzone/rabbitmq-server>

