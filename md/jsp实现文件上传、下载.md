一、文件上传

上传文件是Web开发中经常要用到的功能：例如在基于B/S的人事信息管理系统中上传照片，在新闻发布系统中上传图片等等。。。。。要实现文件上传功能，就需要综合利用java中的文件输入和输出相关的类。

在TCP/IP中，最早出现的文件上传机制是FTP。它是将文件由客服端发送到服务器的标准机制，能够考虑到跨平台的文本和二进制格式文件。但是在jsp编程中不能使用FTP方法来上传文件，这是由jsp
运行机制所决定的。

下面是上传文件的jsp页面：

    
    
    1 <form action="file?file=upload" method="post" enctype="multipart/form-data">
    2     请选择你要上传的文件：<input type="file" name="upload" siez="16"><br>
    3     <input type="submit" value="提交"> 
    4   </form>

对于文件上传表单处理其中method必须为post，也要增加类型enctype="multipart/form-
data"。这样就可以把文件中的数据作为流式数据上传。当然无论是什么文件格式，均可以。。。

下面是servlet 处理程序：

    
    
     1                 //接收上传文件内容中临时文件的文件名
     2         String tempFileName = new String("tempFileName");
     3         //tempfile 对象指向临时文件
     4         File tempFile = new File("D:/"+tempFileName);
     5         //outputfile 文件输出流指向这个临时文件
     6         FileOutputStream outputStream = new FileOutputStream(tempFile);
     7         //得到客服端提交的所有数据
     8         InputStream fileSourcel = request.getInputStream();
     9         //将得到的客服端数据写入临时文件
    10         byte b[] = new byte[1000];
    11         int n ;
    12         while ((n=fileSourcel.read(b))!=-1){
    13             outputStream.write(b,0,n);
    14         }
    15         
    16         //关闭输出流和输入流
    17         outputStream.close();
    18         fileSourcel.close();
    19          
    20         //randomFile对象指向临时文件
    21         RandomAccessFile randomFile = new RandomAccessFile(tempFile,"r");
    22         //读取临时文件的第一行数据
    23         randomFile.readLine();
    24         //读取临时文件的第二行数据，这行数据中包含了文件的路径和文件名
    25         String filePath = randomFile.readLine();
    26         //得到文件名
    27         int position = filePath.lastIndexOf("\\");
    28         CodeToString codeToString = new CodeToString();
    29         String filename = codeToString.codeString(filePath.substring(position,filePath.length()-1));
    30         //重新定位读取文件指针到文件头
    31         randomFile.seek(0);
    32         //得到第四行回车符的位置，这是上传文件数据的开始位置
    33         long  forthEnterPosition = 0;
    34         int forth = 1;
    35         while((n=randomFile.readByte())!=-1&&(forth<=4)){
    36             if(n=="\n"){
    37                 forthEnterPosition = randomFile.getFilePointer();
    38                 forth++;
    39             }
    40         }
    41         
    42         //生成上传文件的目录
    43         File fileupLoad = new File("D:/work space/JSP workspace/jsp_servlet_upAndLoad/file","upLoad");
    44         fileupLoad.mkdir();
    45         //saveFile 对象指向要保存的文件
    46         File saveFile = new File("D:/work space/JSP workspace/jsp_servlet_upAndLoad/file/upLoad",filename);
    47         RandomAccessFile randomAccessFile = new RandomAccessFile(saveFile,"rw");
    48         //找到上传文件数据的结束位置，即倒数第四行
    49         randomFile.seek(randomFile.length());
    50         long endPosition = randomFile.getFilePointer();
    51         int j = 1;
    52         while((endPosition>=0)&&(j<=4)){
    53             endPosition--;
    54             randomFile.seek(endPosition);
    55             if(randomFile.readByte()=="\n"){
    56                 j++;
    57             }
    58         }
    59         
    60         //从上传文件数据的开始位置到结束位置，把数据写入到要保存的文件中
    61         randomFile.seek(forthEnterPosition);
    62         long startPoint = randomFile.getFilePointer();
    63         while(startPoint<endPosition){
    64             randomAccessFile.write(randomFile.readByte());
    65             startPoint = randomFile.getFilePointer();
    66         }
    67         //关闭文件输入、输出
    68         randomAccessFile.close();
    69         randomFile.close();
    70         tempFile.delete();

其中CodeToString()方法是一个中文字符处理的方法。如果文件不进行编码转换，则上传后的文件名将会是乱码，接收的文件数据也会是乱码：

下面是CodeToString()源代码：

    
    
     1 //处理中文字符串的函数
     2     public String codeString(String str){
     3         String s = str;
     4         try {
     5             byte[] temp = s.getBytes("utf-8");
     6             s = new String(temp);
     7             return s ;
     8         } catch (UnsupportedEncodingException e) {
     9             e.printStackTrace();
    10             return s;
    11         }
    12     }

二：文件下载  
实现文件下载的最简单的方法就是使用超链接。假设在服务器上web目录下地upload子目录存在user.doc这个文档。如：

    
    
    <a href="http://localhost:8080/upload/user.doc">下载user.doc</a>

当单击这个超级链接时，将会在浏览器中直接打开这个文档，就像是把word软件嵌入在浏览器中一样。

打开文档后就可以实现另存为了。当然在web上，最常见的方式是单击链接后，出现“另存为”对话框：

    
    
     1 //获取要下载的文件名
     2         String filename = request.getParameter("name");
     3         //得到想客服端输出的输出流
     4         OutputStream outputStream = response.getOutputStream();
     5         //输出文件用的字节数组，每次向输出流发送600个字节
     6         byte b[] = new byte[600];
     7         //要下载的文件
     8         File fileload = new File("D:/work space/JSP workspace/jsp_servlet_upAndLoad/file/upLoad",filename);        
     9         //客服端使用保存文件的对话框
    10         response.setHeader("Content-disposition", "attachment;filename="+filename);
    11         //通知客服文件的MIME类型
    12         response.setContentType("application/msword");
    13         //通知客服文件的长度
    14         long fileLength = fileload.length();
    15         String length = String.valueOf(fileLength);
    16         response.setHeader("Content_length", length);
    17         //读取文件，并发送给客服端下载
    18         FileInputStream inputStream = new FileInputStream(fileload);
    19         int n = 0;
    20         while((n=inputStream.read(b))!=-1){
    21             outputStream.write(b,0,n);
    22         }

在该程序中，response对象的setContentType()用来定义服务器发送给客服端内容的MIME类型。这里对MIME就不特别介绍了。事实上，凡是浏览器能处理的所有资源都有对应的MIME资源类型。在与服务器的交互中，浏览器就是对html、jsp等文件浏览器直接将其打开。对于word、excel等浏览器自身不能打开的文件则调用相应的方法。对于没有标记MIME类型的文件。浏览器则根据其扩展名和文件内容猜测其类型。。。  
  

