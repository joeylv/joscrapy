1\. Description

Given an unsorted array return whether an increasing subsequence of length 3
exists or not in the array.

Formally the function should:  

> Return true if there exists _i, j, k_  
>  such that _arr[i]_ < _arr[j]_ < _arr[k]_ given 0 ≤ _i_ < _j_ < _k_ ≤ _n_ -1
else return false.

Your algorithm should run in O( _n_ ) time complexity and O( _1_ ) space
complexity.

**Examples:**  
Given `[1, 2, 3, 4, 5]`,  
return `true`.

Given `[5, 4, 3, 2, 1]`,  
return `false`.

2\. Answer

solution1 :

    
    
    public class Solution {
        public boolean increasingTriplet(int[] nums) {
            for (int i = 0; i < nums.length - 2; i++) {
                for (int j = i + 1; j < nums.length - 1; j++) {
                    if (nums[j] > nums[i]) {
                        for (int k = j + 1; k < nums.length; k++) {
                            if (nums[k] > nums[j])
                                return true;
                        }
                    }
                }
            }
            
            return false;
        }
    }

solution2：

    
    
    public class Solution {
        public boolean increasingTriplet(int[] nums) {
            int min = Integer.MAX_VALUE;
            int secondMin = Integer.MAX_VALUE;
    
            for (int i = 0; i < nums.length; i++){
                if (nums[i] <= min){
                    min = nums[i];
                }
                else if (nums[i] <= secondMin){
                    secondMin = nums[i];
                }
                else {
                    return true;
                }
            }
            return false;
        }
    } 

solution2 has a better time complexity, it is a better way.

