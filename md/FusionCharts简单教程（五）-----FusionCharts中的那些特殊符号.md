在FusionCharts中有些特殊字符，我们需要进行编码操作才能够使用，否则就无法正常显示。

# 欧元符号

在FusionCharts里显示“€”，你需要用“%80”来替换它。如下：

    
    
    <graph decimalPrecision="0" numberPrefix="%80 ">
    
         <set name="John" value="420" color="AFD8F8" />
    
         <set name="Mary" value="295" color="F6BD0F" />
    
          <set name="Tom" value="523" color="8BBA00" />
    
     </graph>

上面的代码会在数字前面都加上“€”。

# 英镑符号

在FusionCharts里显示“￡”，你需要用“%A3”来替换它。如下：

    
    
    <graph decimalPrecision="0" numberPrefix="%A3 ">
    
         <set name="John" value="420" color="AFD8F8" />
    
         <set name="Mary" value="295" color="F6BD0F" />
    
        <set name="Tom" value="523" color="8BBA00" />
    
    </graph>

上面的代码会在数字前面都加上“￡”。

# 人民币符号

在FusionCharts里显示“￥”，你需要用“%A5”来替换它。如下：

    
    
    <graph decimalPrecision="0" numberPrefix="%A5 " >
    
         <set name="John" value="420" color="AFD8F8" />
    
         <set name="Mary" value="295" color="F6BD0F" />
    
         <set name="Tom" value="523" color="8BBA00" />
    
    </graph>

上面的代码会在数字前面都加上“￥”。

# 分符号

在FusionCharts里显示“￠”，你需要用“%A2”来替换它。如下：

    
    
    <graph decimalPrecision="0" numberSuffix="%A2 ">
    
          <set name="John" value="420" color="AFD8F8" />
    
          <set name="Mary" value="295" color="F6BD0F" /> 
    
          <set name="Tom" value="523" color="8BBA00" /> 
    
    </graph>

上面的代码会在数字后面都加上“￠”。

# 百分号

在FusionCharts里显示“%”，你需要用“%25”来替换它。如下：

    
    
    <graph decimalPrecision="0" numberSuffix="%25 ">
    
        <set name="John" value="42" color="AFD8F8" />
    
        <set name="Mary" value="29" color="F6BD0F" />
    
        <set name="Tom" value="52" color="8BBA00" />
    
    </graph>

上面的代码会在数字后面都加上“%”。

# &符号

在FusionCharts里显示“&”，你需要用“&”来替换它。如下：

    
    
    <graph caption="Total of 2003 & 2004" decimalPrecision="0" >
    
        <set name="John" value="420" color="AFD8F8" />
    
        <set name="Mary" value="295" color="F6BD0F" />
    
        <set name="Tom" value="523" color="8BBA00" />
    
    </graph>

上面的代码标题显示为“Total of 2003 & 2004”。

# >符号

在FusionCharts里显示“>”，你需要用“>”来替换它。如下：

    
    
    <graph decimalprecision="0" >
    
         <set name="0" value="420" color="AFD8F8" />
    
        <set name="0-10" value="295" color="F6BD0F" />
    
        <set name="> 10" value="523" color="8BBA00" />
    
     </graph>

上面的代码最后一个数字显示为“>10”。  
如果要显示“<”，你可能以为用“<”就可以了，事实是不可能的。我还没试验出怎么才能显示“<”，也许没有这个必要。

# 单引号

在FusionCharts里显示“"”，你需要用“"”来替换它。如下：

    
    
    <graph decimalPrecision="0" >
    
        <set name="John"s Count" value="420" color="AFD8F8" />
    
        <set name="Mary"s Count" value="295" color="F6BD0F" />
    
        <set name="Tom"s Count" value="523" color="8BBA00" />
    
    </graph>

上面的代码显示为“John"s Count”。  
如果你想要显示双引号，直接使用就可以了，前提是你的属性值是用单引号括起来的。如果你的属性值是用双引号括起来的，你要显示单引号，也可以直接使用，而不必用“"”来替换它。

