##【问题排查】fastjson线上排坑记前言

##
##版本上线时发现fastjson的toString方法的返回的字符串与与之前版本的toString方法返回的字符串不相同，这导致依赖toString进行md5计算所得到的结果不相同，更进一步导致其他依赖该md5值的插件发现和之前的md5值不相等而重启，导致数据存在丢失情况。源码

##
##从项目中抽取出该模块代码，并进行了适当修改，但未改变整个处理逻辑，源码如下。package main;import com.alibaba.fastjson.JSONObject;import java.security.MessageDigest;import java.security.NoSuchAlgorithmException;public class Main {    public static void main(String[] args) {        JSONObject obj = new JSONObject();        obj.put("the_plugin_id", "the_plugin_id");        obj.put("the_plugin_name", "the_plugin_name");        obj.put("the_plugin_version", "the_plugin_version");        obj.put("the_plugin_md5", "the_plugin_md5");        obj.put("the_extend_info1", "the_extend_info1");        obj.put("the_extend_info2", "the_extend_info2");        obj.put("the_extend_info3", "the_extend_info3");        obj.put("the_extend_info4", "the_extend_info4");        System.out.println(obj.toString());        System.out.println("md5 ==> " + getMD5String(obj.toString()));    	}    private static final char hexDigits[] = {"0", "1", "2", "3", "4", "5",            "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i",            "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",            "w", "x", "y", "z"	};    static public String getMD5String(String source) {        String retString = null;        if (source == null) {            return retString;        	}        try {            StringBuffer sb = new StringBuffer();            MessageDigest md = MessageDigest.getInstance("MD5");            md.update(source.getBytes(), 0, source.length());            byte[] retBytes = md.digest();            for (byte b : retBytes) {                sb.append(hexDigits[(b >> 4) &amp; 0x0f]);                sb.append(hexDigits[b &amp; 0x0f]);            	}            retString = sb.toString();        	} catch (NoSuchAlgorithmException e) {            e.printStackTrace();        	}        return retString;    	}	}原因猜想首先怀疑是由于fastjson版本不一致的问题导致toString方法返回的字符串不相同，待比对jar后发现均依赖fastjson1.2.3版本，排除由于fastjson版本问题导致。再者怀疑是由于上线时将JDK从1.7替换到1.8导致，即是由于JDK升级引起该问题，下面是验证过程。分析验证

##
##为验证是否是由于JDK升级导致该问题，分别使用不同JDK运行上述程序，得到结果如下。JDK1.7运行结果

##
##{"the_extend_info1":"the_extend_info1","the_plugin_version":"the_plugin_version","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_name":"the_plugin_name","the_plugin_id":"the_plugin_id","the_plugin_md5":"the_plugin_md5"	}md5 ==> 87d74d87982fe1063a325c5aa97a9ef5

##
##格式化JSON字符串如下{"the_extend_info1":"the_extend_info1","the_plugin_version":"the_plugin_version","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_name":"the_plugin_name","the_plugin_id":"the_plugin_id","the_plugin_md5":"the_plugin_md5"	}JDK1.8运行结果

##
##{"the_plugin_md5":"the_plugin_md5","the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_version":"the_plugin_version"	}md5 ==> fc8f7f526f5f37141f2fea3a03950f52

##
##格式化JSON字符串如下{"the_plugin_md5":"the_plugin_md5","the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4","the_plugin_version":"the_plugin_version"	}

##
##对比JDK1.7和JDK1.8下运行结果可知toString方法返回的结果并不相同，这也就导致md5计算的不相同，进一步导致其他依赖性的问题。更进一步

##
##当使用JSONObject obj = new JSONObject();创建JSONObject时，跟踪源码可以看到其会调用JSONObject(int, boolean)型构造函数，并且会使用HashMap维护插入的键值对，这是关键所在。

##
##HashMap在JDK1.7和JDK1.8中底层有不同的逻辑，JDK1.8的桶中会维护链表 + 红黑树结构，该结果是对JDK1.7的优化，JDK1.7中维护链表结构，在桶中元素较多而未达到再哈希的条件时查找效率会比较低下，而JDK1.8当桶中元素个数达到一定数量时会将链表转化为红黑树，这样便能提高查询效率，有兴趣的读者可查阅JDK1.7和JDK1.8的源码，JDK1.8源码分析传送门。解决方案

##
##由前面分析可知，直接使用JSONObject obj = new JSONObject()的方法生成JSONObject对象时，其底层会使用HashMap维护键值对，而HashMap是和JDK版本相关的，所以最好的解决方案应该是能和JDK版本解耦的，而在JSONObject的构造函数中，可以自定义传入Map，这样就由指定Map维护插入的键值对。可使用LinkedHashMap来维护插入键值对，并且还会维护插入的顺序。这样便能保证在不同JDK版本下使用toString方法得到的字符串均相同。方案验证

##
##使用JSONObject obj = new JSONObject(new LinkedHashMap<String, Object>());代替之前的JSONObject obj = new JSONObject();即可。JDK1.7运行结果

##
##{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"	}md5 ==> 5c7725cd161d53f1e25a6a5c55b62c1f

##
##格式化JSON字符串如下{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"	} JDK1.8运行结果

##
##{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"	}md5 ==> 5c7725cd161d53f1e25a6a5c55b62c1f

##
##格式化JSON字符串如下{"the_plugin_id":"the_plugin_id","the_plugin_name":"the_plugin_name","the_plugin_version":"the_plugin_version","the_plugin_md5":"the_plugin_md5","the_extend_info1":"the_extend_info1","the_extend_info2":"the_extend_info2","the_extend_info3":"the_extend_info3","the_extend_info4":"the_extend_info4"	} 

##
##对比在不同JDK下运行的结果，可以发现toString方法获得的字符串是完全相同的，md5值也是完全相同的，即验证了方案的正确性。总结

##
##在遇到问题时，特别是现网问题时，需要冷静分析，大胆猜想，小心求证，一点点找到突破口，这次的排坑过程大致如上所记录。