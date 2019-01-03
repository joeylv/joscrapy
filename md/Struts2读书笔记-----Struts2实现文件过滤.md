通常对于Web应用，我们可以云寻浏览者上传图片、上传压缩文件等，但是除此之外，我们必须对浏览者上传的文件大小、类型进行限制。因此必须在文件上传中进行文件过滤。

一、手动实现文件过滤

如果需要手动实现文件过滤，可以按照如下步骤进行

1、在Action中定义一个专用于进行文件过滤的方法。方法名任意，该方法的逻辑判断上传文件的类型是否为允许类型。

    
    
     1 // 过滤文件类型
     2     public String filterType(String[] types) {
     3         // 获取希望上传的文件类型
     4         String fileType = getUploadContentType();
     5         for (String type : types) {
     6             if (type.equals(fileType)) {
     7                 return null;
     8             }
     9         }
    10         return ERROR;
    11     }
    
    
      
     

2、为了让应用程序可以动态配置允许上传的文件列表，为该Action增加一个allowTypes属性，该属性的值列为了所有允许上传的文件类型。为了可以在struts.xml文件中配置allowType属性的值，必须在Action类中提供如下代码：

    
    
     1 // 定义该Action允许上传的文件类型
     2     private String allowType;
     3 
     4     public String getAllowType() {
     5         return allowType;
     6     }
     7 
     8     public void setAllowType(String allowType) {
     9         this.allowType = allowType;
    10     }

3、利用Struts
2的输入校验来判断用户输入的文件是否符合要求，如果不符合要求，接下来就将错误提示添加到FieldError中。所以该Action中增加的validate()方法代码如下：

    
    
    1 //执行输入校验
    2     public void validate(){
    3         //将允许上传文件类型的字符串以英文逗号分解成字符串数组，从而判断当前文件类型是否允许上传
    4         String filterResult = filterType(getAllowType().split(","));
    5         //如果当前文件类型不允许上传，将错误信息提示添加到fieldError中
    6         if(filterResult!=null){
    7             addFieldError("upload", "你要上传的文件类型不正确");
    8         }
    9     }

对于上面的validate方法，它调用了filterTypes来判断浏览者所上传的文件是否符合要求，如果不是允许上传的文件类型，validate()方法就添加了FieldError，这样Struts
2将自动返回input逻辑视图；只有当该文件的类型是允许上传的文件类型时，才真正执行文件上传逻辑。

所以为了让文件类型检验失败时能够返回input逻辑视图，必须为该Action增加input逻辑视图。

    
    
    1 <action name="upload" class="com.app.action.UploadAction">
    2             <param name="savePath">/upload</param>
    3             <param name="allowTypes">image/png,image/gif,image/jpeg</param>
    4             <result name="input">/upload.jsp</result>
    5             <result name="success">/success.jsp</result>
    6 </action>

为了在页面中显示文件过滤失败的错误提示，我们可以在页面中输出错误提示：

    
    
    1 <s:fielderror />

  

二、拦截器实现文件过滤

Struts 2提供了一个文件上传的拦截器，通过配置该拦截器可以轻松的实现文件过滤。Struts
2中文件上传的拦截器是fielUpload，为了让该拦截器起作用，只需要在该Action中配置拦截器引用即可。

配置fielUpload拦截器，可以为其指定两个参数：

allowedTypes：该参数指定允许上传的文件类型，多个文件类型之间以英文逗号隔开

maximumSize：该参数指定允许上传的文件大小，单位是字节

    
    
    <package name="uploadaction" extends="struts-default">
            <action name="upload" class="com.app.action.UploadAction">
                <!-- 配置fileUpload的拦截器 -->
                <interceptor-ref name="fileUpload">
                    <!-- 配置允许上传的文件类型 -->
                    <param name="allowedTypes">image/png,image/gif,image/jpeg</param>
                    <!-- 配置允许上传的文件大小 -->
                    <param name="maximumSize">2000</param>
                </interceptor-ref>
                <!-- 配置系统默认的拦截器 -->
                <interceptor-ref name="defaultStack"></interceptor-ref>
                <!-- 动态设置Action的属性值 -->
                <param name="savePath">/upload</param>
                <result name="input">/upload.jsp</result>
                <result name="success">/success.jsp</result>
            </action>
        </package>

上面的拦截器过滤不仅过滤了文件的类型，也过滤了文件的大小  
  

