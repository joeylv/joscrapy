为了能够上传文件，我们必须将表单的method设置为POST，将entype设置为multipart/form-
data，只有在这种情况下，浏览器才会把用户选择文件的二进制数据发送给服务器。

一旦我们设置了enctype为multipart/form-data，此时浏览器将采用二进制流的方式来处理表单数据。但是Struts
2并没有提供自己的请求解析器，也就是说Struts 2不会自己去处理multipart/form-
data的请求，他需要调用其他上传框架来解析二进制请求数据。

在Struts 2的struts.properties配置文件中，我们可以看到如下配置代码，它主要用于配置Struts 2上传文件时的上传解析器

    
    
        #指定使用cos的文件上传解析器
    
        struts.multipart.parser=cos
    
        #指定使用Pell的文件上传解析器
    
        struts.multipart.parser=pell
    
       #Struts 2默认使用Jakarta的common-FileUpload的文件上传解析器
    
        struts.multipart.parser=jakarta
    
    
    

下面将以Struts 2默认的文件上传支持为例：

对于上传页面，为了完成文件上传，我们应该讲这个表单域的enctype属性设置为“multipart/form-data”，method属性设置为“POST”

如下：

    
    
    1     <s:form action="upload" enctype="multipart/form-data" method="post">
    2         <s:textfield name="title" label="文件标题"></s:textfield><br/>
    3         <s:file name="upload" label="选择文件"></s:file>
    4         <s:submit value="上传"></s:submit>
    5     </s:form>

当该页面提交请求时，请求发送到upload.action。这是Struts 2的一个Action。

实现文件上传的Action

Struts 2的Action无须负责处理HttpServletRequest请求。Struts
2框架负责解析HttpServletRequest请求中的参数，包括文件域，Struts 2使用File类型来封装文件域。

处理上传请求的Action类代码：

    
    
     1 public class UploadAction extends ActionSupport {
     2 
     3     private String title;                     // 封装文件标题请求参数
     4     private File upload;                      // 上传文件域
     5     private String uploadContentType;         // 上传文件的类型
     6     private String uploadFileName;             // 上传文件名的属性
     7 
     8     // 直接在struts.xml文件中配置的属性
     9     private String savePath;
    10 
    11     // 接受struts.xml文件配置值的方法
    12 
    13     public void setSavePath(String savePath) {
    14         this.savePath = savePath;
    15     }
    16 
    17     // 返回上传文件的保存位置
    18     private String getSavePath() throws Exception {
    19         return ServletActionContext.getServletContext().getRealPath(savePath);
    20     }
    21 
    22     // 文章标题的setter和getter方法
    23     public String getTitle() {
    24         return title;
    25     }
    26 
    27     public void setTitle(String title) {
    28         this.title = title;
    29     }
    30 
    31     //上传文件对应文件内容的setter和getter方法
    32     public File getUpload() {
    33         return upload;
    34     }
    35 
    36     public void setUpload(File upload) {
    37         this.upload = upload;
    38     }
    39 
    40     //上传文件的文件类型的setter和getter方法
    41     public String getUploadContentType() {
    42         return uploadContentType;
    43     }
    44 
    45     public void setUploadContentType(String uploadContentType) {
    46         this.uploadContentType = uploadContentType;
    47     }
    48 
    49     //上传文件的文件名的setter和getter方法
    50     public String getUploadFileName() {
    51         return uploadFileName;
    52     }
    53 
    54     public void setUploadFileName(String uploadFileName) {
    55         this.uploadFileName = uploadFileName;
    56     }
    57 
    58     @Override
    59     public String execute() throws Exception {
    60 
    61         //以服务器的文件保存地址和原文件名建立上传文件输出流
    62         FileOutputStream fos = new FileOutputStream(getSavePath()+"\\"+getUploadFileName());
    63         FileInputStream fis = new FileInputStream(getUpload());
    64         byte[] buffer = new byte[1024];
    65         int len = 0;
    66         while ((len = fis.read(buffer))>0) {
    67             fos.write(buffer,0,len);
    68             
    69         }
    70         return SUCCESS  ;
    71     }
    72 }

  
上面的Action提供了两个属性：uploadFileName和uploadContentType，这个两个属性分别用于封转上传文件的文件名、上传文件的文件类型。Action类直接通过File类型属性直接封装了上传文件的文件内容，但是这个File属性无法获取上传文件的文件名和类型，所以Struts
2直接将文件域中包含的上传文件名和文件类型的信息封装到uploadFileName和uploadContentType属性中，。可以认为：如果表单中包含一个name属性为XXX的文件域，则对应Action需要使用三个属性来封装该文件域的信息

1、类型为File的xxx属性封装另外该文件域对应的文件内容。

2、类型为String的xxxFileName属性封装了该文件域对应的文件名。

3、类型为String的xxxContentType属性封装了该文件域对应的文件的文件类型。

通过上面的3个属性，可以更简单地实现文件属性，所以在execute方法中，可以直接通过调用getXxx()方法来获取上传文件的文件名、文件类型和文件内容。

配置文件上传的Action

配置该Action时，还需要配置一个<param.../>元素，该元素用于为该Action的属性动态分配属性值：

    
    
    1         <package name="uploadaction" extends="struts-default">
    2         <action name="upload" class="com.app.action.UploadAction">
    3             <!-- 动态设置Action的属性值 -->
    4             <param name="savePath">/upload</param>
    5             <result name="success">/success.jsp</result>
    6         </action>
    7     </package>

  
配置了改Action应用后，我们就可以上传文件了。该上传请求将会被UploadAction处理，处理结束后会转入到success.jsp页面中，该页面主要是用于显示上传的图片，来验证是否上传成功

    
    
    上传成功!!<br />
        文件标题:<s:property value="+title"/>
        文件为:<img src="<s:property value=""upload/"+uploadFileName"/>"><Br />

  
如果上传成功就可以看到如许页面：

![](../md/img/chenssy/0_1331448327H8N8.gif)

  

