## 前言

>
版本上线时发现`fastjson`的`toString`方法的返回的字符串与与之前版本的`toString`方法返回的字符串不相同，这导致依赖`toString`进行`md5`计算所得到的结果不相同，更进一步导致其他依赖该`md5`值的插件发现和之前的`md5`值不相等而重启，导致数据存在丢失情况。

## 源码

> 从项目中抽取出该模块代码，并进行了适当修改，但未改变整个处理逻辑，源码如下。

    
    
    package main;
    
    
    import com.alibaba.fastjson.JSONObject;
    
    import java.security.MessageDigest;
    import java.security.NoSuchAlgorithmException;
    
    public class Main {
        public static void main(String[] args) {
            JSONObject obj = new JSONObject();
    
            obj.put("the_plugin_id", "the_plugin_id");
            obj.put("the_plugin_name", "the_plugin_name");
            obj.put("the_plugin_version", "the_plugin_version");
            obj.put("the_plugin_md5", "the_plugin_md5");
            obj.put("the_extend_info1", "the_extend_info1");
            obj.put("the_extend_info2", "the_extend_info2");
            obj.put("the_extend_info3", "the_extend_info3");
            obj.put("the_extend_info4", "the_extend_info4");
    
            System.out.println(obj.toString());
            System.out.println("md5 ==> " + getMD5String(obj.toString()));
        }
    
        private static final char hexDigits[] = {"0", "1", "2", "3", "4", "5",
                "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i",
                "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                "w", "x", "y", "z"};
    
        static public String getMD5String(String source) {
    
            String retString = null;
    
            if (source == null) {
                return retString;
            }
    
            try {
                StringBuffer sb = new StringBuffer();
                MessageDigest md = MessageDigest.getInstance("MD5");
                md.update(source.getBytes(), 0, source.length());
                byte[] retBytes = md.digest();
                for (byte b : retBytes) {
                    sb.append(hexDigits[(b >> 4) & 0x0f]);
                    sb.append(hexDigits[b & 0x0f]);
                }
    
                retString = sb.toString();
            } catch (NoSuchAlgorithmException e) {
                e.printStackTrace();
            }
    
            return retString;
        }
    }
    
    

## 原因猜想

  * 首先怀疑是由于`fastjson`版本不一致的问题导致`toString`方法返回的字符串不相同，待比对`jar`后发现均依赖`fastjson1.2.3`版本，排除由于`fastjson`版本问题导致。
  * 再者怀疑是由于上线时将`JDK`从`1.7`替换到`1.8`导致，即是由于`JDK`升级引起该问题，下面是验证过程。

## 分析验证

> 为验证是否是由于`JDK`升级导致该问题，分别使用不同`JDK`运行上述程序，得到结果如下。

  * JDK1.7运行结果

>
{"the_extend_info1":"the_extend_info1","the_plugin_version":"the_plugin_version","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_name":"the_plugin_name","the_plugin_id":"the_plugin_id","the_plugin_md5":"the_plugin_md5"}  
>  md5 ==> 87d74d87982fe1063a325c5aa97a9ef5

格式化`JSON`字符串如下

    
    
    {"the_extend_info1":"the_extend_info1","the_plugin_version":"the_plugin_version","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_name":"the_plugin_name","the_plugin_id":"the_plugin_id","the_plugin_md5":"the_plugin_md5"}
    
    

  * JDK1.8运行结果

>
{"the_plugin_md5":"the_plugin_md5","the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_version":"the_plugin_version"}  
>  md5 ==> fc8f7f526f5f37141f2fea3a03950f52

格式化`JSON`字符串如下

    
    
    {"the_plugin_md5":"the_plugin_md5","the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_version":"the_plugin_version"}
    

>
对比`JDK1.7`和`JDK1.8`下运行结果可知`toString`方法返回的结果并不相同，这也就导致`md5`计算的不相同，进一步导致其他依赖性的问题。

## 更进一步

> 当使用`JSONObject obj = new
JSONObject();`创建`JSONObject`时，跟踪源码可以看到其会调用`JSONObject(int,
boolean)`型构造函数，并且会使用`HashMap`维护插入的键值对，这是关键所在。

`HashMap`在`JDK1.7`和`JDK1.8`中底层有不同的逻辑，`JDK1.8`的桶中会维护`链表 +
红黑树`结构，该结果是对`JDK1.7`的优化，`JDK1.7`中维护`链表`结构，在桶中元素较多而未达到再哈希的条件时查找效率会比较低下，而`JDK1.8`当桶中元素个数达到一定数量时会将链表转化为红黑树，这样便能提高查询效率，有兴趣的读者可查阅`JDK1.7`和`JDK1.8`的源码，`JDK1.8`源码分析[传送门](http://www.cnblogs.com/leesf456/p/5242233.html)。

## 解决方案

> 由前面分析可知，直接使用`JSONObject obj = new
JSONObject()`的方法生成`JSONObject`对象时，其底层会使用`HashMap`维护键值对，而`HashMap`是和`JDK`版本相关的，所以最好的解决方案应该是能和`JDK`版本解耦的，而在`JSONObject`的构造函数中，可以自定义传入`Map`，这样就由指定`Map`维护插入的键值对。可使用`LinkedHashMap`来维护插入键值对，并且还会维护插入的顺序。这样便能保证在不同`JDK`版本下使用`toString`方法得到的字符串均相同。

## 方案验证

> 使用`JSONObject obj = new JSONObject(new LinkedHashMap<String,
Object>());`代替之前的`JSONObject obj = new JSONObject();`即可。

  * JDK1.7运行结果

>
{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"}  
>  md5 ==> 5c7725cd161d53f1e25a6a5c55b62c1f

格式化`JSON`字符串如下

    
    
    {"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"} 
    

  * JDK1.8运行结果

>
{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"}  
>  md5 ==> 5c7725cd161d53f1e25a6a5c55b62c1f

格式化`JSON`字符串如下

    
    
    {"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"} 
    

> 对比在不同`JDK`下运行的结果，可以发现`toString`方法获得的字符串是完全相同的，`md5`值也是完全相同的，即验证了方案的正确性。

## 总结

> 在遇到问题时，特别是现网问题时，需要冷静分析，大胆猜想，小心求证，一点点找到突破口，这次的排坑过程大致如上所记录。

