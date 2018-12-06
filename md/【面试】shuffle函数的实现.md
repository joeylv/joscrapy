##【面试】shuffle函数的实现

##
##一、前言

##
##　　有位同学面试的时候被问到shuffle函数的实现，他之后问我，我知道这个函数怎么用，知道是对数组（或集合）中的元素按随机顺序重新排列。但是没有深入研究这个是怎么实现的。现在直接进入JDK源码进行分析。

##
##二、源码分析

##
##　　shuffle函数的源码如下　　	    public static void shuffle(List<?> list, Random rnd) {        // 集合大小        int size = list.size();        if (size < SHUFFLE_THRESHOLD || list instanceof RandomAccess) { // 小于shuffle阈值或者可以随机访问(如ArrayList，访问效率很高)            // 从后往前遍历            for (int i=size; i>1; i--)                // 交换指定位置的两个元素                swap(list, i-1, rnd.nextInt(i));        	} else { // 如果大于阈值并且不支持随机访问，那么需要先转化为数组，再进行处理            Object arr[] = list.toArray(); // 该数组只是中间存储过程            // 从后往前遍历            for (int i=size; i>1; i--)                // 交换指定位置的两个元素                swap(arr, i-1, rnd.nextInt(i));            // 重新设置list的值            ListIterator it = list.listIterator();            // 遍历List            for (int i=0; i<arr.length; i++) {                it.next();                it.set(arr[i]);            	}        	}    	}

##
##　　说明：从源码可知，进行shuffle时候，是分成两种情况。

##
##　　1. 若集合元素个数小于shuffle阈值或者集合支持随机访问，那么从后往前遍历集合，交换元素。

##
##　　2. 否则，先将集合转化为数组（提高访问效率），再进行遍历，交换元素（在数组中进行），最后设置集合元素。

##
##　　其中涉及的swap函数如下，两个重载函数	    public static void swap(List<?> list, int i, int j) {        // 交换指定位置的两个元素        final List l = list;        l.set(i, l.set(j, l.get(i)));    	}    private static void swap(Object[] arr, int i, int j) {        Object tmp = arr[i];        arr[i] = arr[j];        arr[j] = tmp;    	}

##
##　　说明：两个重载函数很简单，不再累赘。

##
##三、总结

##
##　　多看源码，源码也是最直观的。平时多注意积累，水滴石穿。谢谢各位园友的观看~