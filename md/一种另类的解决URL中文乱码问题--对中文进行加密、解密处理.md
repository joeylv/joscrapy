##一种另类的解决URL中文乱码问题--对中文进行加密、解密处理

##
##情景：在资源调度中，首先用户需要选择工作目标，然后跟据选择的工作目标不同而选择不同的账号和代理ip。处理过程如下：点击选择账号，在js中获取工作目标对工作目标进行两次编码(encodeURI(encodeURI(gzmb)))，在后台，对工作目标进行解码，然后构建URL。

##
##如下：	1 String gzmb = URLDecoder.decode(request.getParameter("gzmb"), "UTF-8");2 Stringurl = "/wlzh/queryPageList.action?accountO.zt=1&amp;accountO.gzmb="+gzmbJiami+"&amp;accountO.accountIsYx=1";

##
##如图

##
##

##
##可知解码是成功的。但是最后得到的结果却是将所有的账号全部选择出来，并没有选择对应工作目标的账号。查看后台。URL跳转得到的工作目标值如下所示的：

##
##

##
##在这里我立马想到URL中文乱码，于是我在后台进行解码操作。但是不知道为什么，换了几种办法都不可以。在这里我想到了以前的办法，通过js两次编码，重构URL。所以在后台我将工作目标传递出来，然后通过js两次编码，重新构建URL。做到这里时我发现，这不就是一开始的么？既然这样，第一步为什么需要解码呢，直接传递过来不就可以了么？将第一步的解码去掉，还真的可以。在进行测试，ie7以上的、火狐、谷歌，唯独ie6不可以（这个原因不知道为什么？求解释）。在这里我只能想到一种解决办法了，使用form表单来进行处理。虽然可以成功，但是这是万不得已的办法。

##
##“有些东西只要你放在心上，过段时间后你一定可以想到一种解决办法”。下班后在车上突然想到了一种另类的办法—在后台对工作目标进行加密操作，赋值给url，然后在另外一边进行解密操作不就可以了。如下	1 //构建账号选择条件2 3         String gzmb= URLDecoder.decode(request.getParameter("gzmb") == null ? "" : request.getParameter("gzmb"), "utf-8");4        String gzmbJiami = DecodeUtils.getJiamiData(gzmb);5        Stringurl = "/wlzh/queryPageList.action?accountO.zt=1&amp;accountO.gzmb="+gzmbJiami+"&amp;accountO.accountIsYx=1";

##
##URL如下所示：

##
##

##
##在那边进行解密操作	1 String gzmbJiemi = DecodeUtils.getJiemiData(accountO.getGzmb());2 accountO.setGzmb(gzmbJiemi);3 PageResultInfo<Account_Bean>pageResultInfo = service.queryAccountPageResultBy(accountO , pageInfo,user);

##
##得到gzmb值如下所示

##
##

##
##注：DecodeUtils是一个功能非常强大的加密解密的工具类。

##
##这里所提供的并不是什么高深的技术，只是提供一种另类的解决方法。这个事情告诉了我，没有做不到的事情，只有想不到的办法。

##
##