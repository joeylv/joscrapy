今天做项目遇到这样一个奇葩问题：我们先看如下代码：

    
    
    int ftcs = dealFtcs(ftcs);
            if(ftcs % 2 == 1){   //奇数
                /*
                 * 处理.....
                 */
            } 
            else{        　　　//偶数
                /*
                 * 处理......
                 */
            }

这个ftcs是需要经过一系列的运算得到的结果，然后再做奇偶判断，为奇数做相应处理，否则做偶数处理，开始测试还好，但是突然心血来潮输入一个负数,得到ftcs
=
-11，但是结果确实转到偶数处理。我就郁闷了，连续测试了好几个负数，发现只要是负数就跑到偶数处理去了。通过查找资料发现，java的取余算法如下,模拟算法：

    
    
    /**
         * @desc 取余模拟算法
         * @param dividend 被除数
         * @param divisor 除数
         * @return
         * @return int
         */
        public static int remainder(int dividend,int divisor){
            return dividend - dividend / divisor * divisor;
        }

看到这个我笑了，怪不得所有负数都往偶数处理那里跑。

当ftcs = -11时， -11 – (-11 / 2 * 2) = -1;

当ftcs = -10时， -10 – (-10 / 2 * 2) = 0;

……

所以对于上面的问题，非常简单修正，改正如下：

    
    
    int ftcs = dealFtcs(ftcs);
            if(ftcs % 2 == 0){   //偶数
                /*
                 * 处理.....
                 */
            } 
            else{        　　　//奇数
                /*
                 * 处理......
                 */
            }

所以

> 1、对于判断奇偶数，推荐用偶数判断，不要用奇数判断。

>

> 2、对于简单的基础知识，我们也不能忽略，做到知其然且知其所以然。

