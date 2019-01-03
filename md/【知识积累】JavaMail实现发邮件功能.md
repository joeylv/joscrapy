**一、前言**

今天闲来没事，想着通过程序来给别人发邮件。于是，上网搜了一下，相应的资料也很多，刚开始完成了邮件的简单发送，后来想如何能发送附件，继续寻找
答案，但是遇到了一个问题是当我使用txt类型作为附件时，附件里的内容总是会显示在正文里面，并且还会出现正文乱码的现象，之后经过不断的查阅资料，终
于解决了问题，实现了我自己想要的功能。

**二、准备工作**

需要的jar包下载地址：https://java.net/projects/javamail/pages/Home

**三、源代码**

主要的类有三个，代码分别如下。

3.1 MailSenderInfo

MailSenderInfo封装了邮件的基本信息。

    
    
    package com.leesf.util;
    
    import java.util.Properties;  
    
    public class MailSenderInfo {    
        // 发送邮件的服务器的IP和端口    
        private String mailServerHost;    
        private String mailServerPort = "25";    
        // 邮件发送者的地址    
        private String fromAddress;    
        // 邮件接收者的地址    
        private String toAddress;    
        // 登陆邮件发送服务器的用户名和密码    
        private String userName;    
        private String password;    
        // 是否需要身份验证    
        private boolean validate = false;    
        // 邮件主题    
        private String subject;    
        // 邮件的文本内容    
        private String content;    
        // 邮件附件的文件名    
        private String[] attachFileNames;      
        /**   
          * 获得邮件会话属性   
          */    
        public Properties getProperties(){    
          Properties p = new Properties();    
          p.put("mail.smtp.host", this.mailServerHost);    
          p.put("mail.smtp.port", this.mailServerPort);    
          p.put("mail.smtp.auth", validate ? "true" : "false");    
          return p;    
        }    
        public String getMailServerHost() {    
          return mailServerHost;    
        }    
        public void setMailServerHost(String mailServerHost) {    
          this.mailServerHost = mailServerHost;    
        }   
        public String getMailServerPort() {    
          return mailServerPort;    
        }   
        public void setMailServerPort(String mailServerPort) {    
          this.mailServerPort = mailServerPort;    
        }   
        public boolean isValidate() {    
          return validate;    
        }   
        public void setValidate(boolean validate) {    
          this.validate = validate;    
        }   
        public String[] getAttachFileNames() {    
          return attachFileNames;    
        }   
        public void setAttachFileNames(String[] fileNames) {    
          this.attachFileNames = fileNames;    
        }   
        public String getFromAddress() {    
          return fromAddress;    
        }    
        public void setFromAddress(String fromAddress) {    
          this.fromAddress = fromAddress;    
        }   
        public String getPassword() {    
          return password;    
        }   
        public void setPassword(String password) {    
          this.password = password;    
        }   
        public String getToAddress() {    
          return toAddress;    
        }    
        public void setToAddress(String toAddress) {    
          this.toAddress = toAddress;    
        }    
        public String getUserName() {    
          return userName;    
        }   
        public void setUserName(String userName) {    
          this.userName = userName;    
        }   
        public String getSubject() {    
          return subject;    
        }   
        public void setSubject(String subject) {    
          this.subject = subject;    
        }   
        public String getContent() {    
          return content;    
        }   
        public void setContent(String textContent) {    
          this.content = textContent;    
        }    
    }   

3.2 SimpleMailSender

SimpleMailSender 实现发送邮件的功能。

    
    
    package com.leesf.util;
    
    import java.io.File;
    import java.io.UnsupportedEncodingException;
    import java.util.Date;    
    import java.util.Properties;   
    import javax.activation.DataHandler;
    import javax.activation.DataSource;
    import javax.activation.FileDataSource;
    import javax.mail.Address;    
    import javax.mail.BodyPart;    
    import javax.mail.Message;    
    import javax.mail.MessagingException;    
    import javax.mail.Multipart;    
    import javax.mail.Session;    
    import javax.mail.Transport;    
    import javax.mail.internet.InternetAddress;    
    import javax.mail.internet.MimeBodyPart;    
    import javax.mail.internet.MimeMessage;    
    import javax.mail.internet.MimeMultipart;    
    import javax.mail.internet.MimeUtility;
     
    public class SimpleMailSender  {    
        
        /**   
         * 以文本格式发送邮件   
         * @param mailInfo 待发送的邮件的信息   
         * @throws UnsupportedEncodingException
         */    
        public boolean sendTextMail(MailSenderInfo mailInfo) {    
          // 判断是否需要身份认证    
          MyAuthenticator authenticator = null;    
          Properties pro = mailInfo.getProperties();   
          if (mailInfo.isValidate()) {    
          // 如果需要身份认证，则创建一个密码验证器    
            authenticator = new MyAuthenticator(mailInfo.getUserName(), mailInfo.getPassword());    
          }   
          // 根据邮件会话属性和密码验证器构造一个发送邮件的session    
          Session sendMailSession = Session.getDefaultInstance(pro, authenticator);    
          try {    
              // 根据session创建一个邮件消息    
              Message mailMessage = new MimeMessage(sendMailSession);    
              // 创建邮件发送者地址    
              Address from = new InternetAddress(mailInfo.getFromAddress());    
              // 设置邮件消息的发送者    
              mailMessage.setFrom(from);    
              // 创建邮件的接收者地址，并设置到邮件消息中    
              Address to = new InternetAddress(mailInfo.getToAddress());    
              mailMessage.setRecipient(Message.RecipientType.TO, to);    
              // 设置邮件消息的主题    
              mailMessage.setSubject(mailInfo.getSubject());    
              // 设置邮件消息发送的时间    
              mailMessage.setSentDate(new Date());    
              // 设置邮件消息的主要内容    
              String mailContent = mailInfo.getContent();    
              mailMessage.setText(mailContent);
              // 发送邮件    
              Transport.send(mailMessage);   
              return true;    
          } catch (MessagingException ex) {    
              ex.printStackTrace();    
          }    
          return false;    
        }    
           
        /**   
          * 以HTML格式发送邮件   
          * @param mailInfo 待发送的邮件信息   
          */    
        public boolean sendHtmlMail(MailSenderInfo mailInfo) {    
          // 判断是否需要身份认证    
          MyAuthenticator authenticator = null;   
          Properties pro = mailInfo.getProperties();   
          //如果需要身份认证，则创建一个密码验证器     
          if (mailInfo.isValidate()) {    
            authenticator = new MyAuthenticator(mailInfo.getUserName(), mailInfo.getPassword());   
          }    
          // 根据邮件会话属性和密码验证器构造一个发送邮件的session    
          Session sendMailSession = Session.getDefaultInstance(pro, authenticator);    
          try {    
              // 根据session创建一个邮件消息    
              Message mailMessage = new MimeMessage(sendMailSession);    
              // 创建邮件发送者地址    
              Address from = new InternetAddress(mailInfo.getFromAddress());    
              // 设置邮件消息的发送者    
              mailMessage.setFrom(from);    
              // 创建邮件的接收者地址，并设置到邮件消息中    
              Address to = new InternetAddress(mailInfo.getToAddress());    
              // Message.RecipientType.TO属性表示接收者的类型为TO    
              mailMessage.setRecipient(Message.RecipientType.TO,to);    
              // 设置邮件消息的主题    
              mailMessage.setSubject(mailInfo.getSubject());    
              // 设置邮件消息发送的时间    
              mailMessage.setSentDate(new Date());    
              // MiniMultipart类是一个容器类，包含MimeBodyPart类型的对象    
              Multipart mainPart = new MimeMultipart();    
              // 创建一个包含HTML内容的MimeBodyPart    
              BodyPart html = new MimeBodyPart();    
              // 设置HTML内容    
              html.setContent(mailInfo.getContent(), "text/html; charset=utf-8");    
              mainPart.addBodyPart(html);    
              // 将MiniMultipart对象设置为邮件内容    
              mailMessage.setContent(mainPart);    
              // 发送邮件    
              Transport.send(mailMessage);    
              return true;    
          } catch (MessagingException ex) {    
              ex.printStackTrace();    
          }    
          return false;    
        }  
        
        /**   
          * 以HTML格式发送邮件   
          * 并且添加附件格式
          * @param mailInfo 待发送的邮件信息   
          */  
        
        public boolean sendAttachMail(MailSenderInfo mailInfo) throws UnsupportedEncodingException {    
            // 判断是否需要身份认证    
            MyAuthenticator authenticator = null;    
            Properties pro = mailInfo.getProperties();
            if (mailInfo.isValidate()) {    
                // 如果需要身份认证，则创建一个密码验证器    
                authenticator = new MyAuthenticator(mailInfo.getUserName(), mailInfo.getPassword());    
            }   
            // 根据邮件会话属性和密码验证器构造一个发送邮件的session    
            Session sendMailSession = Session.getDefaultInstance(pro, authenticator);    
            try {    
                    // 根据session创建一个邮件消息    
                Message mailMessage = new MimeMessage(sendMailSession);    
                  // 创建邮件发送者地址    
                  Address from = new InternetAddress(mailInfo.getFromAddress());    
                  // 设置邮件消息的发送者    
                  mailMessage.setFrom(from);    
                  // 创建邮件的接收者地址，并设置到邮件消息中    
                  Address to = new InternetAddress(mailInfo.getToAddress());    
                  mailMessage.setRecipient(Message.RecipientType.TO, to);    
                  // 设置邮件消息的主题    
                  mailMessage.setSubject(mailInfo.getSubject());
                  
                  // 设置邮件消息发送的时间    
                  mailMessage.setSentDate(new Date());  
                
                  //设置带附件的格式
                  Multipart multipart = new MimeMultipart();  
                  //设置正文
                  MimeBodyPart textBodyPart = new MimeBodyPart();   
                  textBodyPart.setText(mailInfo.getContent());  
                  multipart.addBodyPart(textBodyPart);   
                  
                  //设置附件  
                  MimeBodyPart attrBodyPart = new MimeBodyPart();
                  DataSource dataSource = new FileDataSource(new File("C:\\Users\\LEESF\\Desktop\\test.txt"));  
                  attrBodyPart.setDataHandler(new DataHandler(dataSource));  
                  // 设置编码格式，使附件能正常显示中文名  
                  attrBodyPart.setFileName(MimeUtility.encodeText("test.txt", "gbk", "B"));   
                  multipart.addBodyPart(attrBodyPart);  
                  
                  mailMessage.setContent(multipart, "text/html;charset=gbk");  
                  Transport.send(mailMessage); // 发送邮件  
                  
                  return true;    
            } catch (MessagingException ex) {    
                ex.printStackTrace();    
            }    
            return false;    
        }    
    }   

3.3 MyAuthenticator

MyAuthenticator类主要实现邮箱的认证。

    
    
    package com.leesf.util;
    
    import javax.mail.*;   
    
    public class MyAuthenticator extends Authenticator {   
        String userName=null;   
        String password=null;   
            
        public MyAuthenticator() {   
            
        }
        
        public MyAuthenticator(String username, String password) {    
            this.userName = username;    
            this.password = password;    
        }  
        
        protected PasswordAuthentication getPasswordAuthentication() {   
            return new PasswordAuthentication(userName, password);   
        }   
    }

3.4 Main

用作测试使用。

    
    
    package com.leesf.Main;
    
    import java.io.UnsupportedEncodingException;
    import com.leesf.util.MailSenderInfo;
    import com.leesf.util.SimpleMailSender;
    public class Main {
        public static void main(String[] args) throws UnsupportedEncodingException {   
         //这个类主要是设置邮件   
         MailSenderInfo mailInfo = new MailSenderInfo();   
         //服务器端口
         mailInfo.setMailServerHost("smtp.126.com");   
         //或者是通过qq邮箱发送
         //mailInfo.setMailServerHost("smtp.qq.com");
         mailInfo.setMailServerPort("25");    
         mailInfo.setValidate(true);    
         //您的邮箱用户名
         mailInfo.setUserName("leesf456@126.com");  
         //您的邮箱密码   
         mailInfo.setPassword("**********");
         //发送邮件源地址
         mailInfo.setFromAddress("leesf456@126.com");   
         //发送邮件目的地址
         mailInfo.setToAddress("********@126.com");   
         //主题
         mailInfo.setSubject("设置邮箱标题 如:http://www.cnblogs.com/leesf456/ 我的博客园");  
         //内容
         mailInfo.setContent("设置邮箱内容 如:http://www.cnblogs.com/leesf456/ 我的博客园");    
         //这个类主要来发送邮件   
         SimpleMailSender sms = new SimpleMailSender();   
         sms.sendTextMail(mailInfo);//发送文体格式    
         sms.sendHtmlMail(mailInfo);//发送html格式
         sms.sendAttachMail(mailInfo);//发送带附件格式
       }  
    }

**四、总结**

整个发送邮件的流程就完成了，如果按照上文来，应该是不会出现什么问题，源代码已经上传至[github](https://github.com/leesf/SendMail)，欢迎fork，谢谢各位园友的观看~

参考的链接如下：

http://akanairen.iteye.com/blog/1171713  
http://www.blogjava.net/wangfun/archive/2009/04/15/265748.html

**如果转载，请注明出处：http://www.cnblogs.com/leesf456/**

