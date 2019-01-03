tr是html标签中行的标记，在web开发中，有时候我们为了美观需要修改行的属性。比如tr的边框。如果我们按照如下的形式修改tr的属性就大错特错了.

    
    
    1 tr{
    2 
    3    border:1px  solid #DDDDDD;
    4 
    5 }

这样是没有任何效果的。因为表格中的tr并非单一的边框，这样便需要属性border-collapse，border-collapse
属性设置表格的边框是否被合并为一个单一的边框，还是象在标准的 HTML 中那样分开显示。

实例：为表格设置合并边框模型：

    
    
    1    table{
    2 
    3       border-collapse:collapse;
    4    }

参数：

**separate** 默认值。边框会被分开。不会忽略border-spacing 和 empty-cells 属性。

**collapse** 如果可能，边框会合并为一个单一的边框。会忽略 border-spacing 和 empty-cells 属性。

**inherit** 规定应该从父元素继承border-collapse 属性的值。

