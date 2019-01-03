在上一篇是展示了showModelDialog的基本使用。当点击我要修改时，需要在后台生成excel文件，同时需要提供下载文件功能。

生成excel文件容易、弹出”文件下载”也容易：

点击按钮，跳转到action中，在该action中生成Excel文件，填充数据，保存到临时文件夹中，然后在按钮的Click事件中，根据模板生成Excel报表，填充数据，保存到临时文件夹，然后output.wirte()。一切看起来很顺利。

Action如下(弹出"文件下载"窗口)：

    
    
     1     /**
     2      * @param response
     3      * @param downloadFile
     4      */
     5     private void clientResponse(HttpServletResponse response,File downloadFile, String fileName){
     6         try {  
     7              response.reset();  
     8              response.setContentType("application/octet-stream");
     9              
    10             // 用来弹出保存窗口 ，设置 为attachment
    11             response.setHeader("Content-Disposition", "attachment; filename="+ new String(fileName.getBytes(),"ISO-8859-1"));
    12             InputStream  input=new FileInputStream(downloadFile);
    13             OutputStream output=response.getOutputStream();
    14             int c;
    15             // 读取流并写入到文件中
    16             while ((c = input.read()) != -1) {
    17               output.write(c);
    18             }
    19             output.flush();
    20             output.close();
    21             input.close();
    22         } catch (Exception e) {
    23         }
    24     }

但是当测试的时候，发现我点击”我要修改”按钮，总是会弹出一个新的窗口。百度一下，加了这段：<base
target="_self">，这个表示在当前页打开页面。

如下：

base: 为页面上的所有链接规定默认地址或默认目标

target: 跳转到的目标页

<base target=_blank><!-- 在空白页打开 -->

<base target=_parent> <!-- 在当前页的上一页(父类)打开 -->

<base target=_search> <!-- 在浏览器地址栏打开-->

<base target=_self> <!-- 在当前页打开-->

<base target=_top> <!-- 在最初(首页)页打开 -->

这个问题解决了，但是新的问题又来了，就是文件不可以下载。所以我有没有那种方法既可以在本页打开，又可以提供下载呢？想到了iframe框架。我们可以设置一个看不见的iframe框架，然后target=iframName就可以解决了。

    
    
    1 <iframe id="download" name="download" height="0px" width="0px"></iframe>
    2 
    3 <base target="download">

这<base...>位于<head></head>之间

