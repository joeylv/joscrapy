验证码在网站中是一个非常常用的，主要用于有效防止对某一个特定注册用户用特定程序暴力破解方式进行不断的登陆尝试。

此演示代码主要包括以下三部分：

1.checkCode.java :用于生成验证码

2.checkCodeServler

3.check.jsp 验证

下面是checkCode.java的内容:

    
    
     1 //用于获取四位随机数
     2      private char mapTable[] = {"0","1","2","3","4","5","6","7","8","9"};
     3 
     4      //生成验证码,并返回随机生成的数字
     5      public String getEnsure(int width, int height, OutputStream os){
     6          if (width <= 0)
     7              width = 60;
     8          if (height <= 0)
     9              height = 20;
    10 
    11          BufferedImage image = new BufferedImage(width, height,BufferedImage.TYPE_INT_RGB);
    12 
    13          // 获取图形上下文
    14          Graphics g = image.getGraphics();
    15 
    16          // 设定背景色
    17          g.setColor(new Color(0xDCCCCC));
    18          g.fillRect(0, 0, width, height);
    19 
    20          // 画边框
    21          g.setColor(Color.black);
    22          g.drawRect(0, 0, width - 1, height - 1);
    23 
    24          // 取随机产生的认证码
    25          String strEnsure = "";
    26 
    27          // 4代表4位验证码
    28          for (int i = 0; i < 4; ++i){
    29              strEnsure += mapTable[(int) (mapTable.length * Math.random())];
    30          }
    31 
    32          // 将认证码显示到图象中
    33          g.setColor(Color.red);
    34          g.setFont(new Font("Atlantic Inline", Font.PLAIN, 14));
    35 
    36          // 画的具体坐标
    37          String str = strEnsure.substring(0, 1);
    38          g.drawString(str, 8, 14);
    39          str = strEnsure.substring(1, 2);
    40          g.drawString(str, 20, 15);
    41          str = strEnsure.substring(2, 3);
    42          g.drawString(str, 35, 18);
    43          str = strEnsure.substring(3, 4);
    44          g.drawString(str, 45, 15);
    45 
    46          // 释放图形上下文
    47          g.dispose();
    48 
    49          try{
    50              // 输出图象到页面
    51              ImageIO.write(image, "JPEG", os);
    52          } catch (IOException e){
    53              return "";
    54          }
    55          
    56          return strEnsure;          //返回生成的随机数
    57      }

  
再是checkCodeServlet的内容

    
    
     1     public void doGet(HttpServletRequest request, HttpServletResponse response)
     2             throws ServletException, IOException {
     3         doPost(request, response);
     4     }
     5 
     6     public void doPost(HttpServletRequest request, HttpServletResponse response)
     7             throws ServletException, IOException {
     8         //禁用缓存，每次访问此页面，都重新生成
     9         response.setHeader("Pragma","No-cache"); 
    10         response.setHeader("Cache-Control","no-cache"); 
    11         response.setDateHeader("Expires", 0); 
    12 
    13         //生成验证码的实例对象
    14         CheckCode ie = new CheckCode();
    15 
    16         //调用里面的方法，返回的是生成的验证码中的字符串
    17         String str = ie.getEnsure(0,0,response.getOutputStream());
    18 
    19         //获得session，并把字符串保存在session中，为后面的对比做基础
    20         HttpSession session = request.getSession();
    21         session.setAttribute("strEnsure", str);      
    22         
    23     }

然后是web.xml对servlet的配置

    
    
    1 <servlet>
    2      <servlet-name>CheckServlet</servlet-name>
    3      <servlet-class>com.blog.servlet.CheckServlet</servlet-class>
    4  </servlet>
    5 <servlet-mapping>    
    6     <servlet-name>CheckServlet</servlet-name>    
    7     <url-pattern>/check</url-pattern> 
    8  </servlet-mapping>

最后是jsp页面的引用

    
    
     1 <html>
     2   <head>
     3     <title>验证码</title>
     4     <script type="text/javascript" language="javascript">
     5     //重新获取验证字符
     6     function changeImage()
     7     {
     8     //单击触发图片重载事件，完成图片验证码的更换
     9         document.getElementById("imgRandom").src = document.getElementById("imgRandom").src + "?";
    10     }
    11 </script>
    12     
    13   </head>
    14           
    15   <body>
    16         <img alt= "看不清楚?点击更换验证码 " src= "check"   width= "100"   height= "50" id="imgRandom" onclick="changeImage()"/>   
    17           <a href="javascript:changeImage();">看不清?</a>
    18   </body>
    19 </html>

在jsp页面中，只需要将img的src的属性指向生成验证码的servlet就可以了，指向servle在web.xmlt映射的url（这里我纠结了好久...）

  

