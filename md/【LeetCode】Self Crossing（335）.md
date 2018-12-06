##【LeetCode】Self Crossing（335）

##
##1. Description

##
##　　You are given an array x of n positive numbers. You start at point (0,0) and moves x[0] metres to the north, then x[1] metres to the west, x[2] metres to the south, x[3] metres to the east and so on. In other words, after each move your direction changes counter-clockwise.

##
##　　Write a one-pass algorithm with O(1) extra space to determine, if your path crosses itself, or not.

##
## 　　Example 1:	Given x = [2, 1, 1, 2],┌───┐│   │└───┼──>    │Return true (self crossing)

##
## 　　Example 2:	Given x = [1, 2, 3, 4],┌──────┐│      │││└────────────>Return false (not self crossing)

##
## 　　Example 3:	Given x = [1, 1, 1, 1],┌───┐│   │└───┼>Return true (self crossing)2. Answer	public class Solution {    public boolean isSelfCrossing(int[] x) {        // Check for initial four values manually.        if (x.length < 4) {            for (int el : x) {                if (el == 0)                    return true;            	}            return false;        	}        for (int i = 3; i < x.length; i++) {            int cur = x[i];            if (cur == 0)                return true;            // At any point of time, i-1 has to be less than i-3 in order to            // intersect. Draw few figures to realize this.            if (x[i - 1] <= x[i - 3]) {                // Basic case. Straight forward intersection.                //            ___                //           |___|__                  //               |                //                if (cur >= x[i - 2]) {                    return true;                	}                // Special case.                if (i >= 5) {                    // if i-2 edge is less than i-4 th edge then it cannot                    // intersect no matter what if i < i-2 th edge.                    //            ____                    //           | _  |                     //           |__| |                    //                |                    if (x[i - 2] < x[i - 4])                        continue;                    // the intersecting case.                    //                ____                    //             ___|   |                    //            |   |   |                    //            |   |   |                     //            |_______|                    //                    if ((x[i] + x[i - 4] >= x[i - 2])                            &amp;&amp; (x[i - 1] + x[i - 5] >= x[i - 3]))                        return true;                	}            	}            // equals case            //                 ___            //                |   |            //                |___|            //            if (i >= 4)                if (x[i - 1] == x[i - 3] &amp;&amp; cur + x[i - 4] == x[i - 2])                    return true;        	}        return false;    	}	}

##
##	