##【知识积累】使用Httpclient实现网页的爬取并保存至本地

##
##程序功能实现了爬取网页页面并且将结果保存到本地，通过以爬取页面出发，做一个小的爬虫，分析出有利于自己的信息，做定制化的处理。

##
##其中需要的http*的jar文件，可以在网上自行下载	import java.io.DataOutputStream;import java.io.File;import java.io.FileOutputStream;import java.io.IOException;import java.io.InputStream;import org.apache.http.HttpEntity;import org.apache.http.HttpResponse;import org.apache.http.client.methods.HttpGet;import org.apache.http.impl.client.DefaultHttpClient;public class CrawlPage {    private static String filePath = "F:\\01_Code\\01_Eclipse\\AnalogLogin\\crawData\\";    private static String url = "http://www.huxiu.com/";    private static void saveToLocal(InputStream in, String filePath, String filename) throws IOException {        File file = new File(filePath);        if(!file.exists())            file.mkdirs();        DataOutputStream out = new DataOutputStream(new FileOutputStream(                new File(filePath + filename)));        int result;        while((result=in.read())!=-1){            out.write(result);        	}        out.flush();        out.close();    	}        public static void crawlPage() throws IOException {         DefaultHttpClient client = new DefaultHttpClient();         HttpGet get = new HttpGet(url);         HttpResponse response = client.execute(get);         HttpEntity entity = response.getEntity();         InputStream in = entity.getContent();         String fileName = "crawlPage.html";         //保存到本地         saveToLocal(in, filePath + url.substring(5) + "\\", fileName);    	}        public static void main(String[] args) throws IOException {        crawlPage();    	}	}

##
##