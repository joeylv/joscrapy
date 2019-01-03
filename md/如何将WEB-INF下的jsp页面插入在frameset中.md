在做毕业设计中，我是将jsp页面全部放入WEB-INF文件夹中。但是这样就遇到了一个问题。WEB-
INF是受保护文件夹，我们不能通过常规的方法来访问里面的资源，也就是说如果我们在在frameset中写如下代码是访问不了的：

    
    
    1 <frame src="/WEB-INF/page/admin_righr.jsp" name="main" marginwidth="0" marginheight="0" frameborder="0" scrolling="auto"/>

  
上面的代码是会报404错误的。

那么该如何解决这个问题呢？这里有三种方法可以解决：

一、利用Struts框架

1、我们在frame中配置src时，将他指向一个action。

    
    
    1 <frame src="${pageContext.request.contextPath }/adminIndex/toAdmin_toAdminRight.action" name="main" marginwidth="0" marginheight="0" frameborder="0" scrolling="auto"/>

2、在该处理方法中返回一个字符串。然后在struts.xml中处理结果时指向需要加载的jsp文件即可。

    
    
    1     /**
    2      * admin_right.jsp
    3      */
    4     public String toAdminRight(){
    5         return "adminRight";
    6     }
    
    
    1 <package name="adminIndex" namespace="/adminIndex" extends="struts-default">
    2         <action name="toAdmin_*" class="adminIndexAction" method="{1}">
    3         <result name="adminRight">/WEB-INF/page/backstage/admin_right.jsp</result>
    4         </action>
    5     </package>

  
二、使用Servlet

    
    
    1 <servlet>
    2 　　<servlet-name>servletName</servlet-name>
    3 　　<jsp-file>/WEB-INF/admin_right.jsp>
    4 </servlet>
    5 <servlet-mapping>
    6 　　<servlet-name>servletName</servlet-name>
    7 　　<url-pattern>/.do</url-pattern>
    8 <servlet-mapping>

然后路劲指向该servlet即可。

三、用<jsp:forward page="WEB-INF/XXX">就直接可以访问web-inf目录下的jsp。

