##Java邮件开发-----JavaMail（二）

##
## 这篇博客主要是介绍如何实现将邮件发送给多个收件人和如何利用Authenticators对象实现用户验证。 

##
##在指定收件人的时候，我们可以有两种方法来指定。上篇博客是在发送邮件的时候临时指定收件人，其实还可以在Message对象中指定。

##
##	1 message.addRecipient(Message.RecipientType.TO,new InternetAddress(” 995812509@99.com ”));

##
##

##
##

##
##这个只是发送给一个收件人而言，但是有多个收件人如何处理？同样有两种方法来处理。

##
## 1、在发送邮件时Transport的sendMessage()方法指定收件人时是使用数组来指定收件人的，这个时候我们只需要多添加收件人地址即可完成。

##
## 2、在使用Message对象来添加收件人我们可以使用InternetAddress对象的parse(String string)方法，该方法返回的是InternetAddress数组，这样同样可以实现发送给多个收件人。

##
##

##
##我们知道在进行JavaMail开发时我们必须要进行授权校验，授权校验目的是阻止他人任意乱发邮件，减少垃圾邮件的产生。前篇博客中我是是用的Transport的connect(host,port,username,password)方法来进行校验的，其实我们还可以在获取Session对象的时候进行校验。在Session对象中有这两个方法：getDefaultInstance(prop,authenticator),getInstance(prop,authenticator),这两个方法都有一个共同的参数authenticator，该参数是一个Authenticator对象。Authenticator对象就是帮助用户进行信息验证的，完成授权校验。Authenticator对象中有getPasswordAuthentication()方法，该方法返回返回一个PasswordAuthentication对象，PasswordAuthentication对象中有两个方法：getPassword()、getUserName()也就说我们将password、userName封装在PasswordAuthentication对象，通过这两个方法就可以获取用户名和密码了。即可完成用户信息验证。

##
## 实例如下：	 1 public class JavaMail_02 { 2     public static void main(String[] args) throws Exception { 3         Properties  props = new Properties(); 4         props.setProperty("mail.smtp.auth", "true"); 5         props.setProperty("mail.transport.protocol", "smtp"); 6         props.setProperty("mail.host", "smtp.163.com"); 7          8         Session session = Session.getInstance(props, 9                 new Authenticator(){10                     protected PasswordAuthentication getPasswordAuthentication(){11                         return new PasswordAuthentication("********","*********");12                     	}13         	});14         session.setDebug(true);15         16         Message msg = new MimeMessage(session);17         msg.setFrom(new InternetAddress("chenssy995812509@163.com"));18         19         msg.setSubject("JavaMail测试程序...");20         msg.setContent("<span style="color:red">这是我的第二个javaMail测试程序....</span>", "text/html;charset=gbk");21         //msg.setRecipients(RecipientType.TO, new Address[]{new InternetAddress("1111@@qq.com"),new InternetAddress("2222@qq.cpm")	});22         msg.setRecipients(RecipientType.TO, InternetAddress.parse("995812509@qq.com,1247723213@qq.com"));23         24         Transport.send(msg);25     	}26 27 	}

##
##

##
##