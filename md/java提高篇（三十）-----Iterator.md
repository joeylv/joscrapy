##java提高篇（三十）-----Iterator

##
##迭代对于我们搞Java的来说绝对不陌生。我们常常使用JDK提供的迭代接口进行Java集合的迭代。   	Iterator iterator = list.iterator();        while(iterator.hasNext()){            String string = iterator.next();            //do something        	}

##
##迭代其实我们可以简单地理解为遍历，是一个标准化遍历各类容器里面的所有对象的方法类，它是一个很典型的设计模式。Iterator模式是用于遍历集合类的标准访问方法。它可以把访问逻辑从不同类型的集合类中抽象出来，从而避免向客户端暴露集合的内部结构。 在没有迭代器时我们都是这么进行处理的。如下：

##
##对于数组我们是使用下标来进行处理的:  	int[] arrays = new int[10];   for(int i = 0 ; i < arrays.length ; i++){       int a = arrays[i];       //do something   	}

##
##对于ArrayList是这么处理的:  	List<String> list = new ArrayList<String>();   for(int i = 0 ; i < list.size() ;  i++){      String string = list.get(i);      //do something   	}

##
##对于这两种方式，我们总是都事先知道集合的内部结构，访问代码和集合本身是紧密耦合的，无法将访问逻辑从集合类和客户端代码中分离出来。同时每一种集合对应一种遍历方法，客户端代码无法复用。 在实际应用中如何需要将上面将两个集合进行整合是相当麻烦的。所以为了解决以上问题，Iterator模式腾空出世，它总是用同一种逻辑来遍历集合。使得客户端自身不需要来维护集合的内部结构，所有的内部状态都由Iterator来维护。客户端从不直接和集合类打交道，它总是控制Iterator，向它发送"向前"，"向后"，"取当前元素"的命令，就可以间接遍历整个集合。 

##
##上面只是对Iterator模式进行简单的说明，下面我们看看Java中Iterator接口，看他是如何来进行实现的。
##一、java.util.Iterator

##
##在Java中Iterator为一个接口，它只提供了迭代了基本规则，在JDK中他是这样定义的：对 collection 进行迭代的迭代器。迭代器取代了 Java Collections Framework 中的 Enumeration。迭代器与枚举有两点不同： 

##
##1、迭代器允许调用者利用定义良好的语义在迭代期间从迭代器所指向的 collection 移除元素。 

##
##2、方法名称得到了改进。 

##
##其接口定义如下：  	public interface Iterator {　　boolean hasNext();　　Object next();　　void remove();	}

##
##其中：

##
##Object next()：返回迭代器刚越过的元素的引用，返回值是Object，需要强制转换成自己需要的类型

##
##boolean hasNext()：判断容器内是否还有可供访问的元素

##
##void remove()：删除迭代器刚越过的元素

##
##对于我们而言，我们只一般只需使用next()、hasNext()两个方法即可完成迭代。如下：  	for(Iterator it = c.iterator(); it.hasNext(); ) {　　Object o = it.next();　　 //do something	}

##
##前面阐述了Iterator有一个很大的优点,就是我们不必知道集合的内部结果,集合的内部结构、状态由Iterator来维持，通过统一的方法hasNext()、next()来判断、获取下一个元素，至于具体的内部实现我们就不用关心了。但是作为一个合格的程序员我们非常有必要来弄清楚Iterator的实现。下面就ArrayList的源码进行分析分析。
##二、各个集合的Iterator的实现

##
##下面就ArrayList的Iterator实现来分析，其实如果我们理解了ArrayList、Hashset、TreeSet的数据结构，内部实现，对于他们是如何实现Iterator也会胸有成竹的。因为ArrayList的内部实现采用数组，所以我们只需要记录相应位置的索引即可，其方法的实现比较简单。2.1、ArrayList的Iterator实现

##
##在ArrayList内部首先是定义一个内部类Itr，该内部类实现Iterator接口，如下：  	private class Itr implements Iterator<E> {    //do something	}

##
##而ArrayList的iterator()方法实现：  	public Iterator<E> iterator() {        return new Itr();    	}

##
##所以通过使用ArrayList.iterator()方法返回的是Itr()内部类，所以现在我们需要关心的就是Itr()内部类的实现：

##
##在Itr内部定义了三个int型的变量：cursor、lastRet、expectedModCount。其中cursor表示下一个元素的索引位置，lastRet表示上一个元素的索引位置  	int cursor;                     int lastRet = -1;             int expectedModCount = modCount;

##
##从cursor、lastRet定义可以看出，lastRet一直比cursor少一所以hasNext()实现方法异常简单，只需要判断cursor和lastRet是否相等即可。  	public boolean hasNext() {            return cursor != size;        	}

##
##对于next()实现其实也是比较简单的，只要返回cursor索引位置处的元素即可，然后修改cursor、lastRet即可，  	public E next() {            checkForComodification();            int i = cursor;    //记录索引位置            if (i >= size)    //如果获取元素大于集合元素个数，则抛出异常                throw new NoSuchElementException();            Object[] elementData = ArrayList.this.elementData;            if (i >= elementData.length)                throw new ConcurrentModificationException();            cursor = i + 1;      //cursor + 1            return (E) elementData[lastRet = i];  //lastRet + 1 且返回cursor处元素        	}

##
##checkForComodification()主要用来判断集合的修改次数是否合法，即用来判断遍历过程中集合是否被修改过。在java提高篇（二一）-----ArrayList中已经阐述了。modCount用于记录ArrayList集合的修改次数，初始化为0，，每当集合被修改一次（结构上面的修改，内部update不算），如add、remove等方法，modCount + 1，所以如果modCount不变，则表示集合内容没有被修改。该机制主要是用于实现ArrayList集合的快速失败机制，在Java的集合中，较大一部分集合是存在快速失败机制的，这里就不多说，后面会讲到。所以要保证在遍历过程中不出错误，我们就应该保证在遍历过程中不会对集合产生结构上的修改（当然remove方法除外），出现了异常错误，我们就应该认真检查程序是否出错而不是catch后不做处理。  	final void checkForComodification() {            if (modCount != expectedModCount)                throw new ConcurrentModificationException();        	}

##
##对于remove()方法的是实现，它是调用ArrayList本身的remove()方法删除lastRet位置元素，然后修改modCount即可。  	public void remove() {            if (lastRet < 0)                throw new IllegalStateException();            checkForComodification();            try {                ArrayList.this.remove(lastRet);                cursor = lastRet;                lastRet = -1;                expectedModCount = modCount;            	} catch (IndexOutOfBoundsException ex) {                throw new ConcurrentModificationException();            	}        	}

##
##这里就对ArrayList的Iterator实现讲解到这里，对于Hashset、TreeSet等集合的Iterator实现，各位如果感兴趣可以继续研究，个人认为在研究这些集合的源码之前，有必要对该集合的数据结构有清晰的认识，这样会达到事半功倍的效果！！！！