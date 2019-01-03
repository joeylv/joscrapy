一般来span标记的样式设定width属性，会发现不会产生效果。但是有时我们因为某种应用而需要来设置span的width属性。这个时候我们就要用到display属性了。

对于display属性而言他有四个属性值：block、inline、inline-block、none。他们的详细说明如下：

block：块对象的默认值。将对象强制作为块对象呈递，为对象之后添加新行。

inline：内联对象的默认值。将对象强制作为内联对象呈递，从对象中删除行。

inline-block：将对象呈递为内联对象，但是对象的内容作为块对象呈递。旁边的内联对象会被呈递在同一行内。

none：隐藏对象。与 visibility 属性的hidden值不同，其不为被隐藏的对象保留其物理空间。

如果设置display:block，width属性生效，但是此时的span跟div一样了。

如果设置display:inline-block，则span并列在同行，而且width属性生效。

