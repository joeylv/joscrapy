在做java课程设计的时候，需要一个做许多的表格，由于数据量比较，所以决定给JTable增加个Jcollpan滑动窗口。

可是在我给表格设定的大小超过了Jscollpan，它只会出现垂直滑动条。对于这个我很蛋疼很纠结！！

当我查看帮助文档后，发现了一个这样的方法：setAutoResizeMode(JTable.AUTO_RESIZE_OFF);这个方法用于关闭表格的自动调整，也就是表格大小并不会随框架的变化而变化，根据自身的大小来调整。添加这个方法后的效果是依然没有水平滑动条。这又要纠结了！！

最后实在是解决不了，在百度上面找了解决方案：

最终代码如下：

    
    
    1 JScrollPane jScrollPane = new JScrollPane(table);
    2 jPanel2.setLayout(new BorderLayout());
    3 jPanel2.add(jScrollPane,BorderLayout.CENTER);
    4 jScrollPane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS);
    5 jScrollPane.setPreferredSize(new Dimension(700,600));
    6 table.setPreferredSize(new Dimension(1000,590));
    7 table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);       //关闭表格列自动调整

