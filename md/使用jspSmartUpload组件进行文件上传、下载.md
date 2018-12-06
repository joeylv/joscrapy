##使用jspSmartUpload组件进行文件上传、下载

##
##jspSmartUpload组件是一个可以免费使用的文件上传与下载组件。用户可以把他安装在web服务器上，再进行使用。   jspSmartUpload组件使用非常简单。在jsp文件中仅需要写几行代码就可以实现文件的上传、下载。并能够全程控制上传。利用jspSmartUpload|组件提供的对象及其操作方法，可以获得全部上传、下载的信息，如文件名，大小，类型、扩展名。。。。以方便文件的存取；能对上传的文件在大小、类型等方面做出限制。这样就可以过滤掉不符合要求的文件；下载灵活。只须写很少的代码就能把web服务器变成文件服务器，不管文件在不在web服务器的目录下，都可以利用该组件进行下载。 在使用jspSmartUpload时，必须将该组件放在项目中相应的目录里,如:WebRoot/WEB-INF/lib一、文件上传   下面是一个jsp页面，表单中有4个文件输入文本框，可以同时上传4个文件：	1 <form action="file?file=upLoadByjs" method="post" ENCTYPE="multipart/form-data">2       <input type="file" name=file1" size="30"><Br>3       <input type="file" name=file2" size="30"><Br>4       <input type="file" name=file3" size="30"><Br>5       <input type="file" name=file4" size="30"><Br>6       <input type="submit" value="上传">7     </form>

##
## 当然可以设置同时上传更多的文件...... servlet处理程序：	 1 String path ="D:/work space/JSP workspace/jsp_servlet_upAndLoad/file/upLoad"; 2     //新建一个jsmartUpLoad对象 3     SmartUpload smartUpload = new SmartUpload(); 4     //上传初始化 5     smartUpload.initialize(this.getServletConfig(),request,response); 6     try { 7       //设定上传限制 8       //限制每个上传文件的最大长度;将最大设定为1024*1024*20 9       smartUpload.setMaxFileSize(1024*1024*10);   10       //限制总上传数据的长度11       smartUpload.setTotalMaxFileSize(1024*1024*20);12       //限制允许上传的文件类型、允许doc、txt、bat文件13       smartUpload.setAllowedFilesList("doc,txt,bat");14       //限制禁止上传的文件类型,禁止exe、jsp、和没有扩展名的文件15       smartUpload.setDeniedFilesList("exe,jsp,,");16       //上传文件17       smartUpload.upload();18       //将文件保存到指定的目录下19       smartUpload.save(path);20     	} catch (SQLException e) {21       e.printStackTrace();22     	} catch (SmartUploadException e) {23       e.printStackTrace();24     	}25     26     //逐一提取文件信息，同时输出上传文件的信息27     for (int i = 0; i < smartUpload.getFiles().getCount(); i++) {28       com.jspsmart.upload.File  myFile =smartUpload.getFiles().getFile(i);29       //若文件表单中的文件选项没有选择文件则继续30       if(myFile.isMissing())31         continue;32       //显示当前文件的信息33       response.setContentType("text/html;charset=utf-8");34       PrintWriter out = response.getWriter();35       out.println("<table border="1">");36       out.println("<tr><td>表单选项</td><td>"+myFile.getFieldName()+"</td></tr>");37       out.println("<tr><td>文件长度:</td><td>"+myFile.getSize()+"</td></tr>");38       out.println("<tr><td>文件名</td><td>"+myFile.getFileName()+"</td></tr>");39       out.println("<tr><td>文件扩展名</td><td>"+myFile.getFileExt()+"</td></tr>");40       out.println("<tr><td>文件全名</td><td>"+myFile.getFilePathName()+"</td></tr>");41       out.println("</table><br>");42     	}

##
##

##
##该程序直接使用SmartUploa对象来实现文件上传。在申请对象后，必须要对其进行初始化：smartUpload.initialize(this.getServletConfig(),request,response);二、文件下载 使用jspSmartUpload组件进行文件下载，可以非常简单：  jsp页面：	1    <a href="${pageContext.request.contextPath 	}/file1?file=downByJsmart&amp;name=user.txt">下载user</a>

##
## 处理程序：	 1 //获取下载文件名 2     String fileName = request.getParameter("name"); 3     //新建一个smartUpload对象 4     SmartUpload smartUpload = new SmartUpload(); 5     //初始化 6     smartUpload.initialize(this.getServletConfig(), request, response); 7     //设定contentDisposition为null以禁止浏览器自动打开文件 8     //保证单击链接后是下载文件。 9     smartUpload.setContentDisposition(null);10     //下载文件11     try {12       smartUpload.downloadFile("D:/work space/JSP workspace/jsp_servlet_upAndLoad/file/upLoad/"+fileName);13     	} catch (SmartUploadException e) {14       e.printStackTrace();15     	}

##
##