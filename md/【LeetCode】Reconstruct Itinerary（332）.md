##【LeetCode】Reconstruct Itinerary（332）

##
##1. Description

##
##　　Given a list of airline tickets represented by pairs of departure and arrival airports [from, to], reconstruct the itinerary in order. All of the tickets belong to a man who departs from JFK. Thus, the itinerary must begin with JFK.

##
## Note:If there are multiple valid itineraries, you should return the itinerary that has the smallest lexical order when read as a single string. For example, the itinerary ["JFK", "LGA"] has a smaller lexical order than ["JFK", "LGB"].All airports are represented by three capital letters (IATA code).You may assume all tickets form at least one valid itinerary.

##
##    Example 1:    tickets = [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]    Return ["JFK", "MUC", "LHR", "SFO", "SJC"].

##
##    Example 2:    tickets = [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]    Return ["JFK","ATL","JFK","SFO","ATL","SFO"].    Another possible reconstruction is ["JFK","SFO","ATL","JFK","ATL","SFO"]. But it is larger in lexical order.

##
##2. Answer	import java.util.*;public class Solution {    public List<String> findItinerary(String[][] tickets) {        List<String> result = new ArrayList<String>();        if(tickets == null || tickets.length == 0){            return result;        	}        Map<String, ArrayList<String>> graph = new HashMap<String, ArrayList<String>>();        for(int i=0; i<tickets.length; i++){            if(!graph.containsKey(tickets[i][0])){                ArrayList<String> adj = new ArrayList<String>();                adj.add(tickets[i][1]);                graph.put(tickets[i][0], adj);            	}else{                ArrayList<String> newadj = graph.get(tickets[i][0]);                newadj.add(tickets[i][1]);                graph.put(tickets[i][0], newadj);            	}        	}        for(ArrayList<String> a : graph.values()){            Collections.sort(a);        	}        Stack<String> stack = new Stack<String>();        stack.push("JFK");        while(!stack.isEmpty()){            while(graph.containsKey(stack.peek()) &amp;&amp; !graph.get(stack.peek()).isEmpty()){                stack.push(graph.get(stack.peek()).remove(0));            	}            result.add(0,stack.pop());        	}        return result;    	}	}

##
##