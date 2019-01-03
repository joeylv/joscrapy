StringTokenizer是一个用来分隔String的应用类，相当于VB的split函数。  
1.构造函数  
public StringTokenizer(String str)  
public StringTokenizer(String str, String delim)  
public StringTokenizer(String str, String delim, boolean returnDelims)  
第一个参数就是要分隔的String，第二个是分隔字符集合，第三个参数表示分隔符号是否作为标记返回，如果不指定分隔字符，默认的是：”\t\n\r\f”  
2.核心方法  
public boolean hasMoreTokens()  
public String nextToken()  
public String nextToken(String delim)  
public int countTokens()  
其实就是三个方法，返回分隔字符块的时候也可以指定分割符，而且以后都是采用最后一次指定的分隔符号。  
3.多余方法  
public boolean hasMoreElements()  
public boolean hasMoreElements()  
这个类实现了Enumeration接口，所以多了这么两个方法，其实根本没有必要实现这个接口  
它的名字就叫StringTokenizer，返回一个Object就没有什么意思了。

属于：java.util包。

１、构造函数。

1\. StringTokenizer(String
str)：构造一个用来解析str的StringTokenizer对象。java默认的分隔符是“空格”、“制表符(‘\t’)”、“换行符(‘\n’)”、“回车符(‘\r’)”。  
2\. StringTokenizer(String str, String
delim)：构造一个用来解析str的StringTokenizer对象，并提供一个指定的分隔符。  
3\. StringTokenizer(String str, String delim, boolean
returnDelims)：构造一个用来解析str的StringTokenizer对象，并提供一个指定的分隔符，同时，指定是否返回分隔符。

  
２、方法。  
说明：  
1\. 所有方法均为public；  
2\. 书写格式：［修饰符］ <返回类型><方法名（［参数列表］）>  
如：  
static int parseInt(String
s)表示：此方法（parseInt）为类方法（static），返回类型为（int），方法所需参数为String类型。

1\. int countTokens()：返回nextToken方法被调用的次数。如果采用构造函数1和2，返回的就是分隔符数量(例2)。  
2\. boolean hasMoreTokens() ：返回是否还有分隔符。  
3\. boolean hasMoreElements() ：结果同2。  
4\. String nextToken()：返回从当前位置到下一个分隔符的字符串。  
5\. Object nextElement() ：结果同4。  
6\. String nextToken(String delim)：与4类似，以指定的分隔符返回结果。

  
例子：  
代码:  
String s = new String("The Java platform is the ideal platform for network
computing");  
StringTokenizer st = new StringTokenizer(s);  
System.out.println( "Token Total: " + st.countTokens() );  
while( st.hasMoreElements() ){  
System.out.println( st.nextToken() );  
}  
结果为：  
Token Total: 10  
The  
Java  
platform  
is  
the  
ideal  
platform  
for  
network  
computing

