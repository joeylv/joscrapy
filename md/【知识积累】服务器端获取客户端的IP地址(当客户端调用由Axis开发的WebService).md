##【知识积累】服务器端获取客户端的IP地址(当客户端调用由Axis开发的WebService)

##
##一、前言

##
##　　由于项目中一个小的模块需要获取客户端的IP地址以保证安全调用webservice接口，项目中客户端使用C#编写，服务器端使用Java编写，服务器端与客户端采用Axis开发的WebService进行通信。服务器端维护IP白名单列表，只有IP地址在白名单中的客户端才可以成功调用到接口，获得服务。

##
##二、代码清单

##
##　　若要成功获取客户端IP地址，需要如下Jar包的支持。

##
##　　servlet-api.jar

##
##　　axis.jar

##
##　　axis2-kernel-1.6.2.jar

##
##　　获取IP地址的具体代码如下： ![Alt text](../md/img/ContractedBlock.gif) ![Alt text](../md/img/ExpandedBlockStart.gif)	import org.apache.axis.MessageContext;import org.apache.axis.transport.http.HTTPConstants;public class MyWebService {    public String getIPs() throws IOException {        MessageContext mc = MessageContext.getCurrentContext();        HttpServletRequest request = (HttpServletRequest)mc.getProperty(HTTPConstants.MC_HTTP_SERVLETREQUEST);        String clientIP = request.getRemoteAddr();        return clientIP;    	}	}View Code

##
##　　具体的Jar下载链接如下：

##
##　　http://download.csdn.net/detail/leesf456/9443876

##
##　　一个小功能，希望对有需要的园友有所帮助。

##
##三、总结

##
##　　多思考，多查阅资料，总会有解决办法，多记录，利于自己，方便他人，谢谢各位园友观看~