  * 1 1\. 背景
  * 2 2\. 选择数字31的原因
  * 3 3\. 实验及数据可视化
    * 3.1 3.1 哈希值冲突率计算
    * 3.2 3.2 哈希值分布可视化
  * 4 4.写在最后

> 作者：田小波  
>  原文链接：<https://www.cnblogs.com/nullllun/p/8350178.html>

## 1\. 背景

某天，我在写代码的时候，无意中点开了 String hashCode 方法。然后大致看了一下 hashCode
的实现，发现并不是很复杂。但是我从源码中发现了一个奇怪的数字，也就是本文的主角31。这个数字居然不是用常量声明的，所以没法从字面意思上推断这个数字的用途。后来带着疑问和好奇心，到网上去找资料查询一下。在看完资料后，默默的感叹了一句，原来是这样啊。那么到底是哪样呢？在接下来章节里，请大家带着好奇心和我揭开数字31的用途之谜。

## 2\. 选择数字31的原因

在详细说明 String hashCode 方法选择数字31的作为乘子的原因之前，我们先来看看 String hashCode 方法是怎样实现的，如下：

    
    
    public int hashCode() {
        int h = hash;
        if (h == 0 && value.length > 0) {
            char val[] = value;
            for (int i = 0; i < value.length; i++) {
                h = 31 * h + val[i];
            }
            hash = h;
        }
        return h;
    }
    

上面的代码就是 String hashCode 方法的实现，是不是很简单。实际上 hashCode 方法核心的计算逻辑只有三行，也就是代码中的 for
循环。我们可以由上面的 for 循环推导出一个计算公式，hashCode 方法注释中已经给出。如下：

    
    
    s[0]*31^(n-1) + s[1]*31^(n-2) + ... + s[n-1]
    

这里说明一下，上面的 s 数组即源码中的 val 数组，是 String 内部维护的一个 char 类型数组。这里我来简单推导一下这个公式：

    
    
    假设 n=3
    i=0 -> h = 31 * 0 + val[0]
    i=1 -> h = 31 * (31 * 0 + val[0]) + val[1]
    i=2 -> h = 31 * (31 * (31 * 0 + val[0]) + val[1]) + val[2]
           h = 31*31*31*0 + 31*31*val[0] + 31*val[1] + val[2]
           h = 31^(n-1)*val[0] + 31^(n-2)*val[1] + val[2]
    

上面的公式包括公式的推导并不是本文的重点，大家了解了解即可。接下来来说说本文的重点，即选择31的理由。从网上的资料来看，一般有如下两个原因：

第一，31是一个不大不小的质数，是作为 hashCode
乘子的优选质数之一。另外一些相近的质数，比如37、41、43等等，也都是不错的选择。那么为啥偏偏选中了31呢？请看第二个原因。

第二、31可以被 JVM 优化，31 * i = (i << 5) – i。

上面两个原因中，第一个需要解释一下，第二个比较简单，就不说了。下面我来解释第一个理由。一般在设计哈希算法时，会选择一个特殊的质数。至于为啥选择质数，我想应该是可以降低哈希算法的冲突率。至于原因，这个就要问数学家了，我几乎可以忽略的数学水平解释不了这个原因。上面说到，31是一个不大不小的质数，是优选乘子。那为啥同是质数的2和101（或者更大的质数）就不是优选乘子呢，分析如下。

这里先分析质数2。首先，假设 n = 6，然后把质数2和 n 带入上面的计算公式。并仅计算公式中次数最高的那一项，结果是2^5 =
32，是不是很小。所以这里可以断定，当字符串长度不是很长时，用质数2做为乘子算出的哈希值，数值不会很大。也就是说，哈希值会分布在一个较小的数值区间内，分布性不佳，最终可能会导致冲突率上升。

上面说了，质数2做为乘子会导致哈希值分布在一个较小区间内，那么如果用一个较大的大质数101会产生什么样的结果呢？根据上面的分析，我想大家应该可以猜出结果了。就是不用再担心哈希值会分布在一个小的区间内了，因为101^5
= 10,510,100,501。但是要注意的是，这个计算结果太大了。如果用 int
类型表示哈希值，结果会溢出，最终导致数值信息丢失。尽管数值信息丢失并不一定会导致冲突率上升，但是我们暂且先认为质数101（或者更大的质数）也不是很好的选择。最后，我们再来看看质数31的计算结果：31^5
= 28629151，结果值相对于32和10,510,100,501来说。是不是很nice，不大不小。

上面用了比较简陋的数学手段证明了数字31是一个不大不小的质数，是作为 hashCode
乘子的优选质数之一。接下来我会用详细的实验来验证上面的结论，不过在验证前，我们先看看 Stack Overflow 上关于这个问题的讨论，Why does
Java’s hashCode() in String use 31 as a multiplier?。其中排名第一的答案引用了《Effective
Java》中的一段话，这里也引用一下：

> The value 31 was chosen because it is an odd prime. If it were even and the
multiplication overflowed, information would be lost, as multiplication by 2
is equivalent to shifting. The advantage of using a prime is less clear, but
it is traditional. A nice property of 31 is that the multiplication can be
replaced by a shift and a subtraction for better performance: `31 * i == (i <<
5) – i“ . Modern VMs do this sort of optimization automatically.

简单翻译一下：

>
选择数字31是因为它是一个奇质数，如果选择一个偶数会在乘法运算中产生溢出，导致数值信息丢失，因为乘二相当于移位运算。选择质数的优势并不是特别的明显，但这是一个传统。同时，数字31有一个很好的特性，即乘法运算可以被移位和减法运算取代，来获取更好的性能：31
* i == (i << 5) – i，现代的 Java 虚拟机可以自动的完成这个优化。

排名第二的答案设这样说的：

> As Goodrich and Tamassia point out, If you take over 50,000 English words
(formed as the union of the word lists provided in two variants of Unix),
using the constants 31, 33, 37, 39, and 41 will produce less than 7 collisions
in each case. Knowing this, it should come as no surprise that many Java
implementations choose one of these constants.

这段话也翻译一下：

> 正如 Goodrich 和 Tamassia 指出的那样，如果你对超过 50,000 个英文单词（由两个不同版本的 Unix 字典合并而成）进行
hash code 运算，并使用常数 31, 33, 37, 39 和 41 作为乘子，每个常数算出的哈希值冲突数都小于7个，所以在上面几个常数中，常数
31 被 Java 实现所选用也就不足为奇了。

上面的两个答案完美的解释了 Java 源码中选用数字 31 的原因。接下来，我将针对第二个答案就行验证，请大家继续往下看。

## 3\. 实验及数据可视化

本节，我将使用不同的数字作为乘子，对超过23万个英文单词进行哈希运算，并计算哈希算法的冲突率。同时，我也将针对不同乘子算出的哈希值分布情况进行可视化处理，让大家可以直观的看到数据分布情况。本次实验所使用的数据是
Unix/Linux 平台中的英文字典文件，文件路径为 /usr/share/dict/words。

### 3.1 哈希值冲突率计算

计算哈希算法冲突率并不难，比如可以一次性将所有单词的 hash code 算出，并放入 Set 中去除重复值。之后拿单词数减去 set.size()
即可得出冲突数，有了冲突数，冲突率就可以算出来了。当然，如果使用 JDK8 提供的流式计算 API，则可更方便算出，代码片段如下：

    
    
    public static Integer hashCode(String str, Integer multiplier) {
        int hash = 0;
        for (int i = 0; i < str.length(); i++) {
          hash = multiplier * hash + str.charAt(i);
        }
        return hash;
    }
    
    
    /**
     * 计算 hash code 冲突率，顺便分析一下 hash code 最大值和最小值，并输出
     */
    
    public static void calculateConflictRate(Integer multiplier, List<Integer> hashs) {
        Comparator<Integer> cp = (x, y) -> x > y ? 1 : (x < y ? -1 : 0);
        int maxHash = hashs.stream().max(cp).get();
        int minHash = hashs.stream().min(cp).get();
    
        // 计算冲突数及冲突率
        int uniqueHashNum = (int) hashs.stream().distinct().count();
        int conflictNum = hashs.size() - uniqueHashNum;
        double conflictRate = (conflictNum * 1.0) / hashs.size();
    
        System.out.println(String.format("multiplier=%4d, minHash=%11d, maxHash=%10d, conflictNum=%6d, conflictRate=%.4f%%",
                    multiplier, minHash, maxHash, conflictNum, conflictRate * 100));
    }
    

结果如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071001.png)

从上图可以看出，使用较小的质数做为乘子时，冲突率会很高。尤其是质数2，冲突率达到了
55.14%。同时我们注意观察质数2作为乘子时，哈希值的分布情况。可以看得出来，哈希值分布并不是很广，仅仅分布在了整个哈希空间的正半轴部分，即 0 ~
231-1。而负半轴 -231 ~
-1，则无分布。这也证明了我们上面断言，即质数2作为乘子时，对于短字符串，生成的哈希值分布性不佳。然后再来看看我们之前所说的 31、37、41
这三个不大不小的质数，表现都不错，冲突数都低于7个。而质数 101 和 199
表现的也很不错，冲突率很低，这也说明哈希值溢出并不一定会导致冲突率上升。但是这两个家伙一言不合就溢出，我们认为他们不是哈希算法的优选乘子。最后我们再来看看
32 和 36 这两个偶数的表现，结果并不好，尤其是 32，冲突率超过了了50%。尽管 36 表现的要好一点，不过和
31，37相比，冲突率还是比较高的。当然并非所有的偶数作为乘子时，冲突率都会比较高，大家有兴趣可以自己验证。

### 3.2 哈希值分布可视化

上一节分析了不同数字作为乘子时的冲突率情况，这一节来分析一下不同数字作为乘子时，哈希值的分布情况。在详细分析之前，我先说说哈希值可视化的过程。我原本是打算将所有的哈希值用一维散点图进行可视化，但是后来找了一圈，也没找到合适的画图工具。加之后来想了想，一维散点图可能不合适做哈希值可视化，因为这里有超过23万个哈希值。也就意味着会在图上显示超过23万个散点，如果不出意外的话，这23万个散点会聚集的很密，有可能会变成一个大黑块，就失去了可视化的意义了。所以这里选择了另一种可视化效果更好的图表，也就是
excel
中的平滑曲线的二维散点图（下面简称散点曲线图）。当然这里同样没有把23万散点都显示在图表上，太多了。所以在实际绘图过程中，我将哈希空间等分成了64个子区间，并统计每个区间内的哈希值数量。最后将分区编号做为X轴，哈希值数量为Y轴，就绘制出了我想要的二维散点曲线图了。这里举个例子说明一下吧，以第0分区为例。第0分区数值区间是[-2147483648,
-2080374784)，我们统计落在该数值区间内哈希值的数量，得到 <分区编号, 哈希值数量> 数值对，这样就可以绘图了。分区代码如下：

    
    
    /**
    * 将整个哈希空间等分成64份，统计每个空间内的哈希值数量
    * @param hashs
    */
    public static Map<Integer, Integer> partition(List<Integer> hashs) {
       // step = 2^32 / 64 = 2^26
       final int step = 67108864;
       List<Integer> nums = new ArrayList<>();
       Map<Integer, Integer> statistics = new LinkedHashMap<>();
       int start = 0;
       for (long i = Integer.MIN_VALUE; i <= Integer.MAX_VALUE; i += step) {
           final long min = i;
           final long max = min + step;
           int num = (int) hashs.parallelStream()
                   .filter(x -> x >= min && x < max).count();
    
           statistics.put(start++, num);
           nums.add(num);
       }
    
       // 为了防止计算出错，这里验证一下
       int hashNum = nums.stream().reduce((x, y) -> x + y).get();
       assert hashNum == hashs.size();
       return statistics;
    
    }
    

本文中的哈希值是用整形表示的，整形的数值区间是 [-2147483648, 2147483647]，区间大小为
2^32。所以这里可以将区间等分成64个子区间，每个自子区间大小为 2^26。详细的分区对照表如下：  
  
<table>  
<tr>  
<th>

分区编号

</th>  
<th>

分区下限

</th>  
<th>

分区上限

</th>  
<th>

分区编号

</th>  
<th>

分区下限

</th>  
<th>

分区上限

</th> </tr>  
<tr>  
<td>

0

</td>  
<td>

-2147483648
</td>  
<td>

-2080374784
</td>  
<td>

32

</td>  
<td>

0

</td>  
<td>

67108864

</td> </tr>  
<tr>  
<td>

1

</td>  
<td>

-2080374784
</td>  
<td>

-2013265920
</td>  
<td>

33

</td>  
<td>

67108864

</td>  
<td>

134217728

</td> </tr>  
<tr>  
<td>

2

</td>  
<td>

-2013265920
</td>  
<td>

-1946157056
</td>  
<td>

34

</td>  
<td>

134217728

</td>  
<td>

201326592

</td> </tr>  
<tr>  
<td>

3

</td>  
<td>

-1946157056
</td>  
<td>

-1879048192
</td>  
<td>

35

</td>  
<td>

201326592

</td>  
<td>

268435456

</td> </tr>  
<tr>  
<td>

4

</td>  
<td>

-1879048192
</td>  
<td>

-1811939328
</td>  
<td>

36

</td>  
<td>

268435456

</td>  
<td>

335544320

</td> </tr>  
<tr>  
<td>

5

</td>  
<td>

-1811939328
</td>  
<td>

-1744830464
</td>  
<td>

37

</td>  
<td>

335544320

</td>  
<td>

402653184

</td> </tr>  
<tr>  
<td>

6

</td>  
<td>

-1744830464
</td>  
<td>

-1677721600
</td>  
<td>

38

</td>  
<td>

402653184

</td>  
<td>

469762048

</td> </tr>  
<tr>  
<td>

7

</td>  
<td>

-1677721600
</td>  
<td>

-1610612736
</td>  
<td>

39

</td>  
<td>

469762048

</td>  
<td>

536870912

</td> </tr>  
<tr>  
<td>

8

</td>  
<td>

-1610612736
</td>  
<td>

-1543503872
</td>  
<td>

40

</td>  
<td>

536870912

</td>  
<td>

603979776

</td> </tr>  
<tr>  
<td>

9

</td>  
<td>

-1543503872
</td>  
<td>

-1476395008
</td>  
<td>

41

</td>  
<td>

603979776

</td>  
<td>

671088640

</td> </tr>  
<tr>  
<td>

10

</td>  
<td>

-1476395008
</td>  
<td>

-1409286144
</td>  
<td>

42

</td>  
<td>

671088640

</td>  
<td>

738197504

</td> </tr>  
<tr>  
<td>

11

</td>  
<td>

-1409286144
</td>  
<td>

-1342177280
</td>  
<td>

43

</td>  
<td>

738197504

</td>  
<td>

805306368

</td> </tr>  
<tr>  
<td>

12

</td>  
<td>

-1342177280
</td>  
<td>

-1275068416
</td>  
<td>

44

</td>  
<td>

805306368

</td>  
<td>

872415232

</td> </tr>  
<tr>  
<td>

13

</td>  
<td>

-1275068416
</td>  
<td>

-1207959552
</td>  
<td>

45

</td>  
<td>

872415232

</td>  
<td>

939524096

</td> </tr>  
<tr>  
<td>

14

</td>  
<td>

-1207959552
</td>  
<td>

-1140850688
</td>  
<td>

46

</td>  
<td>

939524096

</td>  
<td>

1006632960

</td> </tr>  
<tr>  
<td>

15

</td>  
<td>

-1140850688
</td>  
<td>

-1073741824
</td>  
<td>

47

</td>  
<td>

1006632960

</td>  
<td>

1073741824

</td> </tr>  
<tr>  
<td>

16

</td>  
<td>

-1073741824
</td>  
<td>

-1006632960
</td>  
<td>

48

</td>  
<td>

1073741824

</td>  
<td>

1140850688

</td> </tr>  
<tr>  
<td>

17

</td>  
<td>

-1006632960
</td>  
<td>

-939524096
</td>  
<td>

49

</td>  
<td>

1140850688

</td>  
<td>

1207959552

</td> </tr>  
<tr>  
<td>

18

</td>  
<td>

-939524096
</td>  
<td>

-872415232
</td>  
<td>

50

</td>  
<td>

1207959552

</td>  
<td>

1275068416

</td> </tr>  
<tr>  
<td>

19

</td>  
<td>

-872415232
</td>  
<td>

-805306368
</td>  
<td>

51

</td>  
<td>

1275068416

</td>  
<td>

1342177280

</td> </tr>  
<tr>  
<td>

20

</td>  
<td>

-805306368
</td>  
<td>

-738197504
</td>  
<td>

52

</td>  
<td>

1342177280

</td>  
<td>

1409286144

</td> </tr>  
<tr>  
<td>

21

</td>  
<td>

-738197504
</td>  
<td>

-671088640
</td>  
<td>

53

</td>  
<td>

1409286144

</td>  
<td>

1476395008

</td> </tr>  
<tr>  
<td>

22

</td>  
<td>

-671088640
</td>  
<td>

-603979776
</td>  
<td>

54

</td>  
<td>

1476395008

</td>  
<td>

1543503872

</td> </tr>  
<tr>  
<td>

23

</td>  
<td>

-603979776
</td>  
<td>

-536870912
</td>  
<td>

55

</td>  
<td>

1543503872

</td>  
<td>

1610612736

</td> </tr>  
<tr>  
<td>

24

</td>  
<td>

-536870912
</td>  
<td>

-469762048
</td>  
<td>

56

</td>  
<td>

1610612736

</td>  
<td>

1677721600

</td> </tr>  
<tr>  
<td>

25

</td>  
<td>

-469762048
</td>  
<td>

-402653184
</td>  
<td>

57

</td>  
<td>

1677721600

</td>  
<td>

1744830464

</td> </tr>  
<tr>  
<td>

26

</td>  
<td>

-402653184
</td>  
<td>

-335544320
</td>  
<td>

58

</td>  
<td>

1744830464

</td>  
<td>

1811939328

</td> </tr>  
<tr>  
<td>

27

</td>  
<td>

-335544320
</td>  
<td>

-268435456
</td>  
<td>

59

</td>  
<td>

1811939328

</td>  
<td>

1879048192

</td> </tr>  
<tr>  
<td>

28

</td>  
<td>

-268435456
</td>  
<td>

-201326592
</td>  
<td>

60

</td>  
<td>

1879048192

</td>  
<td>

1946157056

</td> </tr>  
<tr>  
<td>

29

</td>  
<td>

-201326592
</td>  
<td>

-134217728
</td>  
<td>

61

</td>  
<td>

1946157056

</td>  
<td>

2013265920

</td> </tr>  
<tr>  
<td>

30

</td>  
<td>

-134217728
</td>  
<td>

-67108864
</td>  
<td>

62

</td>  
<td>

2013265920

</td>  
<td>

2080374784

</td> </tr>  
<tr>  
<td>

31

</td>  
<td>

-67108864
</td>  
<td>

0

</td>  
<td>

63

</td>  
<td>

2080374784

</td>  
<td>

2147483648

</td> </tr> </table>

接下来，让我们对照上面的分区表，对数字2、3、17、31、101的散点曲线图进行简单的分析。先从数字2开始，数字2对于的散点曲线图如下：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071002.png)

上面的图还是很一幕了然的，乘子2算出的哈希值几乎全部落在第32分区，也就是 [0,
67108864)数值区间内，落在其他区间内的哈希值数量几乎可以忽略不计。这也就不难解释为什么数字2作为乘子时，算出哈希值的冲突率如此之高的原因了。所以这样的哈希算法要它有何用啊，拖出去斩了吧。接下来看看数字3作为乘子时的表现：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071003.png)

3作为乘子时，算出的哈希值分布情况和2很像，只不过稍微好了那么一点点。从图中可以看出绝大部分的哈希值最终都落在了第32分区里，哈希值的分布性很差。这个也没啥用，拖出去枪毙5分钟吧。在看看数字17的情况怎么样：

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071004.png)

数字17作为乘子时的表现，明显比上面两个数字好点了。虽然哈希值在第32分区和第34分区有一定的聚集，但是相比较上面2和3，情况明显好好了很多。除此之外，17作为乘子算出的哈希值在其他区也均有分布，且较为均匀，还算是一个不错的乘子吧。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071005.png)

接下来来看看我们本文的主角31了，31作为乘子算出的哈希值在第33分区有一定的小聚集。不过相比于数字17，主角31的表现又好了一些。首先是哈希值的聚集程度没有17那么严重，其次哈希值在其他区分布的情况也要好于17。总之，选31，准没错啊。

![](https://gitee.com/chenssy/blog-
home/raw/master/image/201811/201811071006.png)

最后再来看看大质数101的表现，不难看出，质数101作为乘子时，算出的哈希值分布情况要好于主角31，有点喧宾夺主的意思。不过不可否认的是，质数101的作为乘子时，哈希值的分布性确实更加均匀。所以如果不在意质数101容易导致数据信息丢失问题，或许其是一个更好的选择。

## 4.写在最后

经过上面的分析与实践，我想大家应该明白了 String hashCode
方法中选择使用数字31作为乘子的原因了。本文本质是一篇简单的科普文而已，并没有银弹。如果大家读完后觉得又涨知识了，那这篇文章的目的就达到了。最后，本篇文章的配图画的还是很辛苦的，所以如果大家觉得文章不错，不妨就给个赞吧，就当是对我的鼓励了。另外，如果文章中有不妥或者错误的地方，也欢迎指出来。如果能不吝赐教，那就更好了。最后祝大家生活愉快，再见。

