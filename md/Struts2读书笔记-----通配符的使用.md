
      在我们配置Action时，发现struts.xml中的<action…/>的绝大部分都相同。这时我们可以通过使用struts 2 提供的通配符映射机制来处理这个问题。

我们在配置<action
…./>时，允许在指定name属性时使用模式字符串（即用“*”来代替一个或多个任意字符），接下来就可以再class、method属性和<result…/>中使用{N}的形式来代表前面第几个*所代表是字符。

1、 当我们在Action的name属性中使用通配符后，可以用一个<action../>元素代替多个逻辑Action。

    
    
    1 <action name="*action" class="com.app.action.LoginAction" method="{1}">

上面定义了一个一系列的逻辑Action。即只要用户请求的URL=*Action模式，都可以使用该Action。对于method属性，使用的是：{1}。表示该表达式的值就是name属性值中的第一个*的值。如用户请求的URL为RegistAction。则调用RegistAction类中的regist方法。

2、 <action .../>的class属性也可以使用{N}表达式。即struts 2允许将一系列的Action配置成一个<action
.../>元素。相当于一个<action .../>元素配置了多个逻辑Action

    
    
    1 <action name="*Action" class="com.app.action.{1}Action">

上面的struts.xml中
class属性值使用了{N}形式的表达式。这个表达式表示了：如果RUL为LoginAction的请求，其中第一个*为Login，即这个Action的处理类为LoginAction。指定处理方法为默认的execute()方法

根据上面的描述：可以判断下面的struts.xml的配置

    
    
    1 <actiion name="*_*" method="{1}" class="com.app.actions.{2}" >
    
    
      上面的Action模式为**_*，所以只要匹配了这个模式的请求，都可以被该Action处理。如果有一个URL为Regist_Login.action。因为匹配了*_*请求，而且第一个*为Regist，第二个为Login。则意味着调用com.app.action.Login处理类的Regist方法来处理这个请求。

读李刚《轻量级java EE企业应用实战（第三版）—struts 2+Spring 3+Hibernate整合开发》  

