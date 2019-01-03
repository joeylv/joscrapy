有时候我需要在几个包下都需要进行同一个权限控制。如在购物网站中，我们需要进入个人中心、下订单、评价商品等等都需要进行登录权限控制，但是这几个模块并不是位于同一个package下。Struts提供的拦截器，我们可以实现action下拦截，我们虽然可以在每一个package都配置这个拦截器，但是是相当的麻烦。这个时候我们可以利用拦截器实现拦击package。将需要进行权限控制package放入拦截器中就可以实现了。

首先我们需要在struts.xml下进行拦截器的配置。

    
    
     1 <package name="main" extends="struts-default">
     2         <interceptors>
     3             <interceptor name="authorizationInterceptor" class="syxh.common.aop.SystemInterceptor"></interceptor>
     4             <interceptor-stack name="jwzhptStack">
     5                 <interceptor-ref name="defaultStack"></interceptor-ref>
     6                 <interceptor-ref name="authorizationInterceptor"></interceptor-ref>
     7             </interceptor-stack>
     8         </interceptors>  
     9 
    10         <default-interceptor-ref name="jwzhptStack" />
    11 
    12         <global-results>
    13             <result name="loginfailure" type="redirectAction">
    14                 <param name="namespace">/index</param>
    15                 <param name="actionName">index</param>
    16             </result>
    17         </global-results>
    18 
    19         <global-exception-mappings>
    20             <exception-mapping result="input" exception="*">/login.jsp</exception-mapping>
    21         </global-exception-mappings>
    22     </package>

上面配置的main ，所以的package都要继承main，即：extends=”main”，否则实现不了。

在struts.xml中，使用了拦截器栈，里面包含两个拦截器，一个是默认的defaultStack，一个是进行权限控制的authorizationInterceptor。

拦截器实现类：SystemInterceptor.java

    
    
     1 public class SystemInterceptor extends AbstractInterceptor{
     2 
     3     private static final long serialVersionUID = -1819593755738908387L;
     4     private static final String WITHOUT = "/index, /author, /common, /indexzp";   //不需要进行权限控制的namespace
     5 
     6     public void destroy(){
     7     }
     8 
     9     public void init(){
    10     }
    11 
    12     public String intercept(ActionInvocation invocation) throws Exception{
    13         String namespace = invocation.getProxy().getNamespace();       //获取namespace
    14         if (WITHOUT.indexOf(namespace) >= 0){
    15             return invocation.invoke();
    16         }
    17 
    18         Map<?, ?> session = invocation.getInvocationContext().getSession();
    19         UserBean user = (UserBean) session.get("currentUser");
    20         if (user == null){           //没有登录
    21             return "loginfailure";
    22         } 
    23         return invocation.invoke();   //已登录
    24     }
    25 }

上面的拦截器实现类，指定了几个namespace是不需要进行权限控制的，除此之外其他的namespace都要进行

权限控制。

其他package只需要继承main既可实现权限控制。

    
    
    1 <package name="user" namespace="/user" extends="main">
    2         <action name="userCenter_*" class="syxh.grzx.action.UserCenterAction" method="{1}">
    3             <result name="updatePasswordUI">/jsp/grzx/updatePassword.jsp</result>
    4             <result name="updateError">/jsp/grzx/updatePassword.jsp</result>
    5             <result name="updateSuccess" type="redirect">/zp/myWorksHome.action</result>
    6             <result name="updatePhoteUI">/jsp/grzx/updatePhoto.jsp</result>
    7             <result name="updateInfoUI">/jsp/grzx/updateInfo.jsp</result>
    8         </action>
    9     </package>

注：由于这个拦截器主要是根据namespace来进行控制的，所以在配置package，要添加namespace。

