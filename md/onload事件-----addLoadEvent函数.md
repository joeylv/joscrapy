
    1     window.onload = myfunction();

假如我们希望某个函数在网页加载完毕之后就立即执行。网页加载完毕时会触发一个onload事件，所以我们可以利用onload事件来加载这个函数。Onload事件与window对象相关联。如：

把myfunction函数绑定到这个事件上：

一个函数我们可以利用上面的解决,那两个、三个甚至更多呢？怎么解决？？

假如我们有firstFunction和secondFunction两个函数，是不是就是下面这样写呢：

    
    
    1     window.onload = firstFunction;
    2     window.onload = secondFunction;

但是每个处理函数只能绑定一条指令。所以上面的不行。因为secondFunction函数将会取代firstFunction函数。

有一种办法可以帮助我们解决上面问题：即我们先创建一个匿名函数来容纳这两个函数，然后把那个匿名函数绑定到onload事件上，如下：

    
    
    1     window.onload = function(){
    2         firstFunction();
    3         secondFunction();
    4     }

这确实是一个好的、简答的方法。

但是其实还存在一个最佳的解决方案——不管你打算在页面加载完毕后要执行多少个函数，利用该函数都可以轻松的实现。

该函数名为addLoadEvent。该函数仅一个参数：该参数指定了你打算在页面加载完毕后需要执行的函数的函数名。

addLoadEvent()函数代码如下：

    
    
     1     function addLoadEvent(func){
     2             var oldonLoad = window.onload;
     3             if(typeof window.onload!="function"){
     4                     window.onload = func;
     5             }
     6             else{
     7                 window.onload = function(){
     8                     oldonload();
     9                     func();
    10                 }
    11             }
    12     }

addLoadEvent函数主要是完成如下的操作：

1、把现有的window.onload事件处理函数的值存入到oldonload中。

2、如果在这个处理函数上还没有绑定任何函数，就将该函数添加给它。

3、如果在这个处理函数上已经绑定了一些函数，就把该函数追加到现有指定的末尾。

通过addLoadEvent函数，只需要调用该函数就可以进行绑定了。

    
    
    1 addLoadEvent(firestFunction);
    2 addLoadEvent(secondFunction);

所以这个函数非常有用，尤其当代码变得很复杂的时候。无论你打算在页面加载完毕时执行多少个函数，只需要多写几条这样的语句就可以解决了。方便、实用。

  

