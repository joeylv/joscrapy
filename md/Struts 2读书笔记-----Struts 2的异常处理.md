##Struts 2读书笔记-----Struts 2的异常处理

##
## 对于MVC框架而言。我们希望：当Action处理用户请求时。如果出现了异常1，则系统就会转入视图资源1，在该视图资源上输入服务器提示；如果出现了异常2，则系统会转入子图资源2，在该视图资源上输入服务器提示；。。。。。

##
## 为了满足上述要求，我们可以采用以下的处理方法：	 1 Public class XxxxAction{ 2     Public String execute(){ 3         try{ 4             ……. 5         	} 6         catch(异常1  e1){ 7             return 结果1; 8         	} 9         Catch(异常2  e2){10             return 结果2;11         	}12     	}13 	}

##
## 我们在Action的execute方法中使用try…..catch快来捕捉异常，当捕捉到指定的异常时，系统会返回对应的逻辑视图名----这种处理方式完全是手动处理异常，可维护性不好。

##
## 从上面我们可以看到，上面代码段的实质是完成异常类型和逻辑视图名之间的对应关系。既然如此，我们为什么不可以把这种对应关系推迟到struts.xml中进行管理呢？？

##
## 由于struts2支持声明式异常处理，所以我们只需要将所有的异常全部抛出，交给struts2来处理。然后根据struts.xml文件中配置的异常映射，转入到制定的视图资源。

##
##声明式异常捕捉

##
## exception:指定该异常映射所设置的异常类型

##
## result:指定Actin出现异常时，返回的逻辑视图名

##
## 

##
## 异常映射一般可以分为全局异常映射和局部异常映射

##
## 全局异常映射对所有的Action都有效，而局部异常映射仅仅只对该异常映射所在的Action内有效。

##
## 全局异常映射是将<exception-mapping...>元素作为<action.../>元素的子元素配置

##
## 全局异常映射是将<exception-mapping...>元素作为<global-exception-mapping.../>元素的子元素配置

##
## 

##
## 输出异常信息

##
## 当Struts2系统进入异常处理页面后，我们必须在对应的页面中输出指定异常信息

##
## 可以通过以下标签来输出异常信息	1              <.s:property value="exception"/>：输出异常对象本身2 3              <s:propertu value="exceptionStack"/>:输出异常堆栈信息

##
## 对于第一种我们可以使用表达式输出异常对象本身。对于第二种，由于exception提供了getMessage()方法，所以我们可以采用<s:propertuvalue="exception.messagge"/>来输出异常的message信息