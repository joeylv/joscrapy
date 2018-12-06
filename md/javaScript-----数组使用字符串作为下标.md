##javaScript-----数组使用字符串作为下标

##
## 今天在看javascript的时候，突然发现数组array竟然可以利用字符串做为其下标，这个以前我还真的不知道，在我的印象当中数组用来遍历，怎么可以用字符串呢？哎。。孤陋寡闻啊.....

##
## 首先Array是从Object那里继承下。它具备Object所有的功能和特性。下面是Object的情况：	新建： var  object  =   new  Object();	增加： object[strIndex ]  =  value; (strIndex 为string)	删除： delete  object[strIndex ];	遍历： for  (  var  strObjIndex  in  object ) object[strObjIndex ];  

##
## 如下：

##
##	1     var obj = new Object();2     obj["first"] = "my";3     obj["second"] = "name";4     obj["third"] = "is";5     obj["fourth"] = "chenssy";

##
##

##
## 因为Array继承Object，那么Array也是可以用字符串作为数组下标的：

##
## 如下

##
##	1     var array = new Array();2     array["first"] = "my";3     array["second"] = "name";4     array["third"] = "is";5     array["fourth"] = "chenssy";

##
##

##
##对于array数字的遍历，我们采用for循环语句。但是这个for循环并不是这个形式：	1 for(int i =  0;i<arrray.length;i++)

##
##我们可以利用for/in循环把该数组进行遍历。for/in循环把某个数组的下标临时赋给一个变量：	1 for(variable in array)

##
##在第一个循环时，变量variable将被赋值为数组array的第一个元素的下标值；在第二次循环时，变量variable将被赋值为数组array的第二个元素的下标值；依次类推.......

##
##对于上面的array数组，利用for/in循环遍历：	1 for(key in array)

##
##

##
##

##
##