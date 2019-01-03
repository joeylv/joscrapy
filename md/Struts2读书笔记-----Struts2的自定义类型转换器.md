大部分时候，我们使用Struts
2内建的类型转换器就可以满足大部分类型转换需求了。但是在有些特殊的情况下，如：需要把一个字符串转换成一个复合对象时，这个时候就需要使用自定义类型转换器了。

实现自定义类型转换器一般需要实现以下两步：

1、编写自己的类型转换器

2、注册类型转换器

1、自定义类型转换器

编写自定义类型转换器一般都要实现一个类：DefaultTypeConverter。实现自定义转换器需要重写该类的convertValue方法。

convertValue方法负责完成类型的转换。但是这种转换是双向的，即如当需要把字符串转换成User实例时，是通过该方法实现的；当需要把User实例转换成字符串是，也是通过该方法实现的。

为了让该方法实现双向转换，是通过判断toType的类型即可判断转换的方向。toType类型是需要转换的目标类型，当toType类型是User类型时，表面需要将字符串转换成User实例；当toType类型是String类型时，表明需要把User实例转换为字符串类型。

2、注册类型转换器

注册类型转换器，就是讲类型转换器注册在Web应用中，告诉Struts 2如何使用这些类型转换器。

Struts 2提供了三种类型转换器：

注册局部类型转换器：该转换器仅仅对某个Action的属性起作用

注册全局类型转换器：该转换器对所有的Action的特定类型的属性都会生效。

使用JDK 的注释来注册类型转换器：通过注释方式来注册类型转换器。

1）、局部类型转换器

注册局部类型转换器使用局部类型转换文件指定。只要在该转换文件中增加一行即可：

<propName>=<converterClass>

将<propName>替换成需要进行转换的属性。将<converterClass>替换成类型转换器的实现类即可。

一般来说，局部类型转换器具有很大的局限性。所以一般都会将类型转换器注册成全局类型转换器。

２）、全局类型转换器

全局类型转换器不是对指定的Action的指定属性起作用，而是对指定的类型起作用。

注册全局类型转换器应该提供一个xwork-conversion.properties文件，该文件时全局类型转换文件。

注册全局类型转换器只需在全局类型转换文件中添加一行即可：

<propType>=<ConvertClass>

将<propType>替换成需要进行类型转换的类型，将<ConvertClass>替换成类型转换器的实现类即可。

例题：

类型转换器：

    
    
     1 public class UserConverter extends DefaultTypeConverter{
     2 
     3     //重写convertvalue方法,该方法需要完成双向转换
     4     public Object convertValue(Map context, Object value,Class toType) {
     5         //当需要将字符串向User类型转换时
     6         if(toType == UserBean.class){
     7             //系统的请求参数是一个字符串数组
     8             String[] params = (String[]) value;
     9             for (int i = 0; i < params.length; i++) {
    10                 System.out.println(params[i]);
    11             }
    12             //创建一个User实例
    13             UserBean user = new UserBean();
    14             //只处理请求参数数组第一个数组元素，并将该字符串以英文逗号分割成两个字符串
    15             String[] userValue = params[0].split(",");
    16             //为user实例赋值
    17             user.setName(userValue[0]);
    18             user.setPassword(userValue[1]);
    19             
    20             return user;
    21         }
    22         if(toType == String.class){
    23             //将需要转换的值强制类型转换成User类型
    24             UserBean user = (UserBean) value;
    25             return "<" +user.getName()+","+user.getPassword()+">";
    26         }
    27         return null;
    28     }
    29     
    30 }

  
注册类型转换器：

    
    
    1 com.app.entity.UserBean=com.app.converter.UserConverter

jsp文件：

    
    
    1 <s:form action="RegisterLogin">
    2       <s:textfield name="user.name" label="用户名"></s:textfield>
    3        <s:submit value="登陆"></s:submit>
    4    </s:form>

  
当在jsp页面的文本框中输入：chenssy,chentmt即可登录成功

其实Struts
2提供了一个StrutsTypeConverter抽象类，实现这个抽象类可以简化类型转换器的实现。该类实现了DefaultTypeConverter的convertValue方法，实现该方法时，它将两个不同转换方法替换成不同方法—当需要把字符串转换成复合类型时，调用convertFromString抽象方法;当需要把复合类型转换成字符串时，调用convertToString抽象方法。

由上面可以知道：我们只需要继承StrutsTypeConmverter抽象类，并且重写convertFromString
方法和convertToString方法，我们就可以简单实现自己的类型转换器。

    
    
        public class UserConverter extends StrutsTypeConverter{
        //实现将字符串类型转换成复合类型的方法
        public Object convertFormString (Map context,String[] values,Class toClass){
        ......
        } 
        
        //实现将复合类型转换成字符串类型的方法
            Public String convertToString (Map context,Object o){
        .........
        }
    }  

