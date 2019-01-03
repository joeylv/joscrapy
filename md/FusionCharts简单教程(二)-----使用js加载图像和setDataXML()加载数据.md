前面一篇对FusionCharts进行了一个简单的介绍，而且建立了我们第一个图形，但是那个是在HTML中使用<OBJECT>和<EMBED>标记来加载图形的，但是这样做是非常不“理智”的。这样做除了代码量比较大外，还有并不是所有的人能够看懂上面的代码。但是使用JS后就可以避免上面几个问题了。

# 一、使用JS加载FusionCharts图形

下面就分五个步骤讲解如何使用js来加载FusionCharts图形。

第一步：导入FusionCharts.js文件

    
    
    <script language="JavaScript" src="../FusionCharts/FusionCharts.js"></script>

  
第二步：定义一个DIV，它必须具备一个元素：id

    
    
    <div id="chartdiv_01" align="center"></div>

第三步：建立一个FusionCharts对象

    
    
     var myChart = new FusionCharts("para1", "para2", "para3", "para4");  

Para1：表示的是SWF文件的地址

Para2：该图形的ID，这个可以随便命名，但是需要保证它的唯一性  
para3：图形的高度。

Para4：图形的长度。

    
    
     var myChart = new FusionCharts("../FusionCharts/Doughnut3D.swf", "myChartId_02", "600", "500");  

第四步：设置数据文件

    
    
    myChart.setDataURL("Data.xml");

第五步：指定图形渲染的位置。

    
    
    myChart.render("chartdiv_01");

通过上面五个步骤就是完成js加载FusionCharts图形。如果需要加载多个图形，只需要重复第二步—第五步，但是需要确保DIV和FusionCharts对象的id的唯一性。如：

    
    
                 <div id="chartdiv_02" align="center"></div>
    		<script type="text/javascript">   
    	        var myChart = new FusionCharts("../FusionCharts/Doughnut3D.swf", "myChartId_02", "600", "500");    
    		myChart.setDataURL("Data.xml");    
    		myChart.render("chartdiv_02");

# 二、使用dataXML加载数据

前面所讲的xml数据文件都是一个单独的xml文件，这个文件可能会被一个或者多个程序使用，同时这个文件也是静态的。但是我们在实际需求中可能不许哟啊单独的文件且数据是动态的，这时我们就可以使用dataXML方法来进行调用。注：dataURL也可以使用动态的数据文件。

dataXML和dataURL都可以提供数据，只不过dataURL是将数据文件以URL地址的形式，而dataXML则是以XML文本的形式。说的直白点就是dataURL将xml文件的地址告知FCF，而dataXML是将XML数据文件里的内容告知FCF。

下面的实例是使用dataXML加载数据文件。其中setDataXML()方面的参数是一个完整的XML字符串。

    
    
    myChart.setDataURL(<graph caption="每月销售额柱形图" xAxisName="月份" yAxisName="Units" showNames="1" decimalPrecision="0" formatNumberScale="0">
    	<set name="一月" value="100" color="AFD8F8" />
    	<set name="二月" value="200" color="F6BD0F" />
    	<set name="三月" value="300" color="8BBA00" />
    	<set name="四月" value="120" color="FF8E46" />
    	<set name="五月" value="220" color="008E8E" />
    	<set name="六月" value="330" color="D64646" />
    	<set name="七月" value="210" color="8E468E" />
    	<set name="八月" value="544" color="588526" />
    	<set name="九月" value="565" color="B3AA00" />
    	<set name="十月" value="754" color="008ED6" />
    	<set name="十一月" value="441" color="9D080D" />
    	<set name="十二月" value="654" color="A186BE" />
    </graph>");    

# 三、setDataXML()的问题

我们知道浏览器对参数的获取一般都有一个长度的限制，如果XML字符串数据过大，可能会导致问题，貌似下钻到时候如果有中文会出现问题(在这次项目中，下钻中文总是传递不过去，不知道各位有没有遇到过这样的问题，求解！！)。

所以在实际的应用中一般都是推荐这种方式：setDataURL()方法，使用javascript来加载图形。不过在使用setDataURL时，如果地址里面包含有”?”、”&”等字符时，需要进行转码操作。对于java而言推荐使用URLEncoder.encode()来进行编码。

