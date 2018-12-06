##【LeetCode】Palindrome Pairs（336）

##
##1. Description

##
##　　Given a list of unique words. Find all pairs of distinct indices (i, j) in the given list, so that the concatenation of the two words, i.e. words[i] + words[j] is a 　　palindrome.

##
## 　　Example 1:    　　Given words = ["bat", "tab", "cat"]    　　Return [[0, 1], [1, 0]]    　　The palindromes are ["battab", "tabbat"]

##
##    　　Example 2:    　　Given words = ["abcd", "dcba", "lls", "s", "sssll"]    　　Return [[0, 1], [1, 0], [3, 2], [2, 4]]    　　The palindromes are ["dcbaabcd", "abcddcba", "slls", "llssssll"]

##
##2. Answer　　	public class Solution {    public List<List<Integer>> palindromePairs(String[] words) {        List<List<Integer>> res = new ArrayList<List<Integer>>();        if(words == null || words.length == 0){          return res;        	}        //build the map save the key-val pairs: String - idx        HashMap<String, Integer> map = new HashMap<>();        for(int i = 0; i < words.length; i++){            map.put(words[i], i);        	}        //special cases: "" can be combine with any palindrome string        if(map.containsKey("")) {            int blankIdx = map.get("");            for(int i = 0; i < words.length; i++) {                if(isPalindrome(words[i])) {                    if(i == blankIdx)                         continue;                    res.add(Arrays.asList(blankIdx, i));                    res.add(Arrays.asList(i, blankIdx));                	}            	}        	}        //find all string and reverse string pairs        for(int i = 0; i < words.length; i++) {            String cur_r = reverseStr(words[i]);            if(map.containsKey(cur_r)) {              int found = map.get(cur_r);              if(found == i) continue;              res.add(Arrays.asList(i, found));           	}        	}        //find the pair s1, s2 that         //case1 : s1[0:cut] is palindrome and s1[cut+1:] = reverse(s2) => (s2, s1)        //case2 : s1[cut+1:] is palindrome and s1[0:cut] = reverse(s2) => (s1, s2)        for(int i = 0; i < words.length; i++) {            String cur = words[i];            for(int cut = 1; cut < cur.length(); cut++) {                if(isPalindrome(cur.substring(0, cut))) {                    String cut_r = reverseStr(cur.substring(cut));                    if(map.containsKey(cut_r)) {                        int found = map.get(cut_r);                        if(found == i) continue;                        res.add(Arrays.asList(found, i));                    	}                	}                if(isPalindrome(cur.substring(cut))) {                    String cut_r = reverseStr(cur.substring(0, cut));                    if(map.containsKey(cut_r)){                        int found = map.get(cut_r);                        if(found == i) continue;                        res.add(Arrays.asList(i, found));                    	}                	}            	}        	}           return res;    	}    public String reverseStr(String str) {        StringBuilder sb = new StringBuilder(str);        return sb.reverse().toString();    	}    public boolean isPalindrome(String s) {        int i = 0;        int j = s.length() - 1;        while(i <= j){            if(s.charAt(i) != s.charAt(j)) {                return false;            	}            i++;            j--;        	}     return true;    	} 	}

##
##