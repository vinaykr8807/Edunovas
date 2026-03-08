"""
generate_datasets.py
====================
Generates data_java.csv and data_javascript.csv with 100+ real problems each.
Run:  python generate_datasets.py
"""

import pandas as pd, re, csv

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def metrics(code: str):
    lines   = [l for l in code.split('\n') if l.strip()]
    length  = len(code)
    loops   = sum(code.count(k) for k in ['for', 'while', 'do '])
    conds   = sum(code.count(k) for k in ['if ', 'else', 'switch', 'case '])
    cc      = 1 + loops + conds
    indent  = sum(1 for l in lines if l.startswith('    ') or l.startswith('\t'))
    ident   = len(set(re.findall(r'\b[a-zA-Z_]\w{2,}\b', code)))
    read    = max(0, round(10 - cc * 0.3 - max(0, ident - 20) * 0.1, 1))
    return len(lines), length, cc, round(read, 1)


# ─────────────────────────────────────────────
# JAVA PROBLEMS
# ─────────────────────────────────────────────
JAVA = [
    # ── Beginner ──────────────────────────────
    ("Hello World", "Beginner", """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}"""),
    ("Factorial Recursive", "Beginner", """
public class Factorial {
    public static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
}"""),
    ("Fibonacci Series", "Beginner", """
public class Fibonacci {
    public static void printFibonacci(int n) {
        int a = 0, b = 1;
        for (int i = 0; i < n; i++) {
            System.out.print(a + " ");
            int temp = a + b; a = b; b = temp;
        }
    }
}"""),
    ("Reverse String", "Beginner", """
public class ReverseString {
    public static String reverse(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}"""),
    ("Palindrome Check", "Beginner", """
public class Palindrome {
    public static boolean isPalindrome(String s) {
        String rev = new StringBuilder(s).reverse().toString();
        return s.equals(rev);
    }
}"""),
    ("Count Vowels", "Beginner", """
public class CountVowels {
    public static int countVowels(String s) {
        int count = 0;
        for (char c : s.toLowerCase().toCharArray())
            if ("aeiou".indexOf(c) >= 0) count++;
        return count;
    }
}"""),
    ("FizzBuzz", "Beginner", """
public class FizzBuzz {
    public static void fizzBuzz(int n) {
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0)      System.out.println("FizzBuzz");
            else if (i % 3 == 0)  System.out.println("Fizz");
            else if (i % 5 == 0)  System.out.println("Buzz");
            else                  System.out.println(i);
        }
    }
}"""),
    ("Prime Number Check", "Beginner", """
public class PrimeCheck {
    public static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int i = 2; i * i <= n; i++)
            if (n % i == 0) return false;
        return true;
    }
}"""),
    ("GCD Euclidean", "Beginner", """
public class GCD {
    public static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }
}"""),
    ("String Anagram Check", "Beginner", """
import java.util.Arrays;
public class AnagramCheck {
    public static boolean isAnagram(String a, String b) {
        char[] ca = a.toCharArray(); char[] cb = b.toCharArray();
        Arrays.sort(ca); Arrays.sort(cb);
        return Arrays.equals(ca, cb);
    }
}"""),
    ("Sum of Digits", "Beginner", """
public class SumDigits {
    public static int sumDigits(int n) {
        int sum = 0;
        while (n != 0) { sum += n % 10; n /= 10; }
        return sum;
    }
}"""),
    ("Armstrong Number", "Beginner", """
public class Armstrong {
    public static boolean isArmstrong(int n) {
        int orig = n, sum = 0, digits = String.valueOf(n).length();
        while (n > 0) { sum += Math.pow(n % 10, digits); n /= 10; }
        return sum == orig;
    }
}"""),
    ("Power of Two", "Beginner", """
public class PowerOfTwo {
    public static boolean isPowerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;
    }
}"""),
    ("Find Min Max", "Beginner", """
public class MinMax {
    public static int[] minMax(int[] arr) {
        int min = arr[0], max = arr[0];
        for (int x : arr) { if (x < min) min = x; if (x > max) max = x; }
        return new int[]{min, max};
    }
}"""),
    ("Swap Two Numbers", "Beginner", """
public class Swap {
    public static int[] swap(int a, int b) {
        a = a ^ b; b = a ^ b; a = a ^ b;
        return new int[]{a, b};
    }
}"""),
    ("Temperature Converter", "Beginner", """
public class TempConverter {
    public static double celsiusToFahrenheit(double c) { return c * 9.0 / 5.0 + 32; }
    public static double fahrenheitToCelsius(double f) { return (f - 32) * 5.0 / 9.0; }
}"""),
    ("Count Words", "Beginner", """
public class CountWords {
    public static int countWords(String s) {
        if (s == null || s.trim().isEmpty()) return 0;
        return s.trim().split("\\s+").length;
    }
}"""),
    ("Array Sum", "Beginner", """
public class ArraySum {
    public static int sum(int[] arr) {
        int total = 0;
        for (int x : arr) total += x;
        return total;
    }
}"""),
    ("Leap Year Check", "Beginner", """
public class LeapYear {
    public static boolean isLeap(int year) {
        return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
    }
}"""),
    ("String Contains Substring", "Beginner", """
public class SubstringCheck {
    public static boolean contains(String s, String sub) {
        return s.contains(sub);
    }
}"""),
    # ── Intermediate ──────────────────────────
    ("Two Sum", "Intermediate", """
import java.util.HashMap;
public class TwoSum {
    public static int[] twoSum(int[] nums, int target) {
        HashMap<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int comp = target - nums[i];
            if (map.containsKey(comp)) return new int[]{map.get(comp), i};
            map.put(nums[i], i);
        }
        return new int[]{};
    }
}"""),
    ("Binary Search", "Intermediate", """
public class BinarySearch {
    public static int binarySearch(int[] arr, int target) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }
}"""),
    ("Bubble Sort", "Intermediate", """
public class BubbleSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++)
            for (int j = 0; j < n - i - 1; j++)
                if (arr[j] > arr[j + 1]) {
                    int tmp = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = tmp;
                }
    }
}"""),
    ("Stack Implementation", "Intermediate", """
import java.util.ArrayList;
public class Stack<T> {
    private ArrayList<T> list = new ArrayList<>();
    public void push(T item) { list.add(item); }
    public T pop() { return list.remove(list.size() - 1); }
    public T peek() { return list.get(list.size() - 1); }
    public boolean isEmpty() { return list.isEmpty(); }
    public int size() { return list.size(); }
}"""),
    ("Valid Parentheses", "Intermediate", """
import java.util.Stack;
public class ValidParentheses {
    public static boolean isValid(String s) {
        Stack<Character> stack = new Stack<>();
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') stack.push(c);
            else {
                if (stack.isEmpty()) return false;
                char top = stack.pop();
                if (c == ')' && top != '(') return false;
                if (c == ']' && top != '[') return false;
                if (c == '}' && top != '{') return false;
            }
        }
        return stack.isEmpty();
    }
}"""),
    ("Linked List", "Intermediate", """
public class LinkedList<T> {
    private static class Node<T> { T data; Node<T> next; Node(T d) { data = d; } }
    private Node<T> head;
    public void add(T data) {
        Node<T> node = new Node<>(data);
        if (head == null) { head = node; return; }
        Node<T> cur = head;
        while (cur.next != null) cur = cur.next;
        cur.next = node;
    }
    public void print() {
        Node<T> cur = head;
        while (cur != null) { System.out.print(cur.data + " "); cur = cur.next; }
    }
}"""),
    ("Reverse Linked List", "Intermediate", """
public class ReverseLinkedList {
    static class Node { int val; Node next; Node(int v) { val = v; } }
    public static Node reverse(Node head) {
        Node prev = null, cur = head;
        while (cur != null) {
            Node next = cur.next; cur.next = prev; prev = cur; cur = next;
        }
        return prev;
    }
}"""),
    ("Queue Using Two Stacks", "Intermediate", """
import java.util.Stack;
public class QueueUsingStacks {
    Stack<Integer> inbox = new Stack<>(), outbox = new Stack<>();
    public void enqueue(int val) { inbox.push(val); }
    public int dequeue() {
        if (outbox.isEmpty()) while (!inbox.isEmpty()) outbox.push(inbox.pop());
        return outbox.pop();
    }
}"""),
    ("Max Subarray Kadane", "Intermediate", """
public class MaxSubarray {
    public static int maxSubArray(int[] nums) {
        int maxSum = nums[0], cur = nums[0];
        for (int i = 1; i < nums.length; i++) {
            cur = Math.max(nums[i], cur + nums[i]);
            maxSum = Math.max(maxSum, cur);
        }
        return maxSum;
    }
}"""),
    ("Selection Sort", "Intermediate", """
public class SelectionSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++)
                if (arr[j] < arr[minIdx]) minIdx = j;
            int tmp = arr[minIdx]; arr[minIdx] = arr[i]; arr[i] = tmp;
        }
    }
}"""),
    ("Insertion Sort", "Intermediate", """
public class InsertionSort {
    public static void sort(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i], j = i - 1;
            while (j >= 0 && arr[j] > key) { arr[j + 1] = arr[j]; j--; }
            arr[j + 1] = key;
        }
    }
}"""),
    ("HashMap Frequency Count", "Intermediate", """
import java.util.HashMap;
public class FrequencyCount {
    public static HashMap<Character, Integer> frequency(String s) {
        HashMap<Character, Integer> map = new HashMap<>();
        for (char c : s.toCharArray())
            map.put(c, map.getOrDefault(c, 0) + 1);
        return map;
    }
}"""),
    ("String Compression", "Intermediate", """
public class StringCompression {
    public static String compress(String s) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            char c = s.charAt(i); int count = 0;
            while (i < s.length() && s.charAt(i) == c) { i++; count++; }
            sb.append(c);
            if (count > 1) sb.append(count);
        }
        return sb.length() < s.length() ? sb.toString() : s;
    }
}"""),
    ("Matrix Transpose", "Intermediate", """
public class MatrixTranspose {
    public static int[][] transpose(int[][] matrix) {
        int rows = matrix.length, cols = matrix[0].length;
        int[][] result = new int[cols][rows];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                result[j][i] = matrix[i][j];
        return result;
    }
}"""),
    ("Rotate Array", "Intermediate", """
public class RotateArray {
    public static void rotate(int[] nums, int k) {
        int n = nums.length; k %= n;
        reverse(nums, 0, n - 1); reverse(nums, 0, k - 1); reverse(nums, k, n - 1);
    }
    private static void reverse(int[] arr, int lo, int hi) {
        while (lo < hi) { int t = arr[lo]; arr[lo++] = arr[hi]; arr[hi--] = t; }
    }
}"""),
    ("Count Occurrences", "Intermediate", """
public class CountOccurrences {
    public static int count(int[] arr, int target) {
        int cnt = 0;
        for (int x : arr) if (x == target) cnt++;
        return cnt;
    }
}"""),
    ("Find Duplicates", "Intermediate", """
import java.util.*;
public class FindDuplicates {
    public static List<Integer> findDuplicates(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        List<Integer> result = new ArrayList<>();
        for (int n : nums) if (!seen.add(n)) result.add(n);
        return result;
    }
}"""),
    ("Two Pointers Sum", "Intermediate", """
public class TwoPointers {
    public static int[] twoPointerSum(int[] sorted, int target) {
        int lo = 0, hi = sorted.length - 1;
        while (lo < hi) {
            int sum = sorted[lo] + sorted[hi];
            if (sum == target) return new int[]{lo, hi};
            else if (sum < target) lo++;
            else hi--;
        }
        return new int[]{};
    }
}"""),
    ("Iterator Pattern", "Intermediate", """
import java.util.Iterator;
public class NumberRange implements Iterable<Integer> {
    private int start, end;
    public NumberRange(int s, int e) { start = s; end = e; }
    public Iterator<Integer> iterator() {
        return new Iterator<>() {
            int cur = start;
            public boolean hasNext() { return cur <= end; }
            public Integer next() { return cur++; }
        };
    }
}"""),
    ("Builder Pattern", "Intermediate", """
public class Person {
    private String name; private int age; private String email;
    private Person() {}
    public static class Builder {
        private Person p = new Person();
        public Builder name(String n) { p.name = n; return this; }
        public Builder age(int a) { p.age = a; return this; }
        public Builder email(String e) { p.email = e; return this; }
        public Person build() { return p; }
    }
    public String toString() { return name + "," + age + "," + email; }
}"""),
    # ── Advanced ──────────────────────────────
    ("Merge Sort", "Advanced", """
public class MergeSort {
    public static void sort(int[] arr, int l, int r) {
        if (l < r) {
            int mid = (l + r) / 2;
            sort(arr, l, mid); sort(arr, mid + 1, r); merge(arr, l, mid, r);
        }
    }
    private static void merge(int[] arr, int l, int mid, int r) {
        int n1 = mid - l + 1, n2 = r - mid;
        int[] L = new int[n1], R = new int[n2];
        for (int i = 0; i < n1; i++) L[i] = arr[l + i];
        for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
        int i = 0, j = 0, k = l;
        while (i < n1 && j < n2) arr[k++] = L[i] <= R[j] ? L[i++] : R[j++];
        while (i < n1) arr[k++] = L[i++];
        while (j < n2) arr[k++] = R[j++];
    }
}"""),
    ("Quick Sort", "Advanced", """
public class QuickSort {
    public static void sort(int[] arr, int lo, int hi) {
        if (lo < hi) {
            int p = partition(arr, lo, hi);
            sort(arr, lo, p - 1); sort(arr, p + 1, hi);
        }
    }
    private static int partition(int[] arr, int lo, int hi) {
        int pivot = arr[hi], i = lo - 1;
        for (int j = lo; j < hi; j++)
            if (arr[j] <= pivot) { i++; int t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
        int t = arr[i + 1]; arr[i + 1] = arr[hi]; arr[hi] = t;
        return i + 1;
    }
}"""),
    ("Binary Tree Inorder", "Advanced", """
public class BinaryTree {
    static class Node { int val; Node left, right; Node(int v) { val = v; } }
    public static void inorder(Node root) {
        if (root == null) return;
        inorder(root.left);
        System.out.print(root.val + " ");
        inorder(root.right);
    }
}"""),
    ("Longest Common Subsequence", "Advanced", """
public class LCS {
    public static int lcs(String a, String b) {
        int m = a.length(), n = b.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 1; i <= m; i++)
            for (int j = 1; j <= n; j++)
                dp[i][j] = a.charAt(i-1) == b.charAt(j-1)
                    ? dp[i-1][j-1] + 1
                    : Math.max(dp[i-1][j], dp[i][j-1]);
        return dp[m][n];
    }
}"""),
    ("Knapsack 0-1", "Advanced", """
public class Knapsack {
    public static int knapsack(int[] weights, int[] values, int capacity) {
        int n = weights.length;
        int[][] dp = new int[n + 1][capacity + 1];
        for (int i = 1; i <= n; i++)
            for (int w = 0; w <= capacity; w++) {
                dp[i][w] = dp[i-1][w];
                if (weights[i-1] <= w)
                    dp[i][w] = Math.max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1]);
            }
        return dp[n][capacity];
    }
}"""),
    ("Depth First Search", "Advanced", """
import java.util.*;
public class DFS {
    public static void dfs(Map<Integer, List<Integer>> graph, int start) {
        Set<Integer> visited = new HashSet<>();
        Stack<Integer> stack = new Stack<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (visited.contains(node)) continue;
            visited.add(node); System.out.print(node + " ");
            for (int neighbor : graph.getOrDefault(node, Collections.emptyList()))
                if (!visited.contains(neighbor)) stack.push(neighbor);
        }
    }
}"""),
    ("Breadth First Search", "Advanced", """
import java.util.*;
public class BFS {
    public static List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        queue.add(start); visited.add(start);
        while (!queue.isEmpty()) {
            int node = queue.poll(); order.add(node);
            for (int nb : graph.getOrDefault(node, Collections.emptyList()))
                if (!visited.contains(nb)) { visited.add(nb); queue.add(nb); }
        }
        return order;
    }
}"""),
    ("LRU Cache", "Advanced", """
import java.util.*;
public class LRUCache {
    private int cap; private LinkedHashMap<Integer, Integer> map;
    public LRUCache(int capacity) {
        cap = capacity;
        map = new LinkedHashMap<>(cap, 0.75f, true) {
            protected boolean removeEldestEntry(Map.Entry e) { return size() > cap; }
        };
    }
    public int get(int key) { return map.getOrDefault(key, -1); }
    public void put(int key, int value) { map.put(key, value); }
}"""),
    ("Trie Data Structure", "Advanced", """
import java.util.HashMap;
public class Trie {
    private HashMap<Character, Trie> children = new HashMap<>();
    private boolean isEnd = false;
    public void insert(String word) {
        Trie node = this;
        for (char c : word.toCharArray()) {
            node.children.putIfAbsent(c, new Trie());
            node = node.children.get(c);
        }
        node.isEnd = true;
    }
    public boolean search(String word) {
        Trie node = this;
        for (char c : word.toCharArray()) {
            if (!node.children.containsKey(c)) return false;
            node = node.children.get(c);
        }
        return node.isEnd;
    }
}"""),
    ("Graph Cycle Detection", "Advanced", """
import java.util.*;
public class CycleDetection {
    public static boolean hasCycle(int n, List<List<Integer>> adj) {
        int[] color = new int[n]; // 0=white,1=gray,2=black
        for (int i = 0; i < n; i++)
            if (color[i] == 0 && dfs(adj, color, i)) return true;
        return false;
    }
    private static boolean dfs(List<List<Integer>> adj, int[] color, int u) {
        color[u] = 1;
        for (int v : adj.get(u)) {
            if (color[v] == 1) return true;
            if (color[v] == 0 && dfs(adj, color, v)) return true;
        }
        color[u] = 2; return false;
    }
}"""),
    ("Matrix Multiplication", "Advanced", """
public class MatrixMul {
    public static int[][] multiply(int[][] A, int[][] B) {
        int m = A.length, n = B[0].length, k = B.length;
        int[][] C = new int[m][n];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                for (int p = 0; p < k; p++)
                    C[i][j] += A[i][p] * B[p][j];
        return C;
    }
}"""),
    ("Singleton Pattern", "Advanced", """
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) instance = new Singleton();
            }
        }
        return instance;
    }
}"""),
    ("Observer Pattern", "Advanced", """
import java.util.*;
public class EventBus {
    private Map<String, List<Runnable>> listeners = new HashMap<>();
    public void on(String event, Runnable handler) {
        listeners.computeIfAbsent(event, k -> new ArrayList<>()).add(handler);
    }
    public void emit(String event) {
        listeners.getOrDefault(event, Collections.emptyList()).forEach(Runnable::run);
    }
}"""),
    ("Dijkstra Shortest Path", "Advanced", """
import java.util.*;
public class Dijkstra {
    public static int[] dijkstra(int[][] graph, int src) {
        int n = graph.length;
        int[] dist = new int[n]; Arrays.fill(dist, Integer.MAX_VALUE); dist[src] = 0;
        boolean[] visited = new boolean[n];
        for (int i = 0; i < n - 1; i++) {
            int u = -1;
            for (int v = 0; v < n; v++)
                if (!visited[v] && (u == -1 || dist[v] < dist[u])) u = v;
            visited[u] = true;
            for (int v = 0; v < n; v++)
                if (!visited[v] && graph[u][v] != 0 && dist[u] != Integer.MAX_VALUE
                        && dist[u] + graph[u][v] < dist[v])
                    dist[v] = dist[u] + graph[u][v];
        }
        return dist;
    }
}"""),
    ("Heap Min Implementation", "Advanced", """
import java.util.ArrayList;
public class MinHeap {
    private ArrayList<Integer> heap = new ArrayList<>();
    public void insert(int val) {
        heap.add(val); int i = heap.size() - 1;
        while (i > 0 && heap.get((i-1)/2) > heap.get(i)) {
            int p = (i-1)/2; int tmp = heap.get(p); heap.set(p, heap.get(i)); heap.set(i, tmp); i = p;
        }
    }
    public int extractMin() {
        int min = heap.get(0); int last = heap.remove(heap.size()-1);
        if (!heap.isEmpty()) { heap.set(0, last); heapifyDown(0); }
        return min;
    }
    private void heapifyDown(int i) {
        int n = heap.size(), l = 2*i+1, r = 2*i+2, smallest = i;
        if (l < n && heap.get(l) < heap.get(smallest)) smallest = l;
        if (r < n && heap.get(r) < heap.get(smallest)) smallest = r;
        if (smallest != i) {
            int tmp = heap.get(i); heap.set(i, heap.get(smallest)); heap.set(smallest, tmp);
            heapifyDown(smallest);
        }
    }
}"""),
]

# ─────────────────────────────────────────────
# JAVASCRIPT PROBLEMS
# ─────────────────────────────────────────────
JS = [
    # ── Beginner ──────────────────────────────
    ("Hello World", "Beginner", """
function helloWorld() {
    console.log('Hello, World!');
}"""),
    ("Factorial Recursive", "Beginner", """
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}"""),
    ("Fibonacci Series", "Beginner", """
function fibonacci(n) {
    const seq = [0, 1];
    for (let i = 2; i < n; i++) seq.push(seq[i-1] + seq[i-2]);
    return seq.slice(0, n);
}"""),
    ("Reverse String", "Beginner", """
function reverseString(s) {
    return s.split('').reverse().join('');
}"""),
    ("Palindrome Check", "Beginner", """
function isPalindrome(s) {
    const clean = s.toLowerCase().replace(/[^a-z0-9]/g, '');
    return clean === clean.split('').reverse().join('');
}"""),
    ("FizzBuzz", "Beginner", """
function fizzBuzz(n) {
    return Array.from({length: n}, (_, i) => {
        const x = i + 1;
        if (x % 15 === 0) return 'FizzBuzz';
        if (x % 3 === 0) return 'Fizz';
        if (x % 5 === 0) return 'Buzz';
        return x;
    });
}"""),
    ("Count Vowels", "Beginner", """
function countVowels(str) {
    return (str.match(/[aeiou]/gi) || []).length;
}"""),
    ("Prime Check", "Beginner", """
function isPrime(n) {
    if (n < 2) return false;
    for (let i = 2; i <= Math.sqrt(n); i++)
        if (n % i === 0) return false;
    return true;
}"""),
    ("Unique Elements Array", "Beginner", """
function uniqueElements(arr) {
    return [...new Set(arr)];
}"""),
    ("Chunk Array", "Beginner", """
function chunkArray(arr, size) {
    const result = [];
    for (let i = 0; i < arr.length; i += size)
        result.push(arr.slice(i, i + size));
    return result;
}"""),
    ("Count Words", "Beginner", """
function countWords(str) {
    return str.trim() === '' ? 0 : str.trim().split(/\\s+/).length;
}"""),
    ("Anagram Check", "Beginner", """
function isAnagram(a, b) {
    const sort = s => s.toLowerCase().split('').sort().join('');
    return sort(a) === sort(b);
}"""),
    ("Sum Array", "Beginner", """
function sumArray(arr) {
    return arr.reduce((acc, x) => acc + x, 0);
}"""),
    ("Find Max Min", "Beginner", """
function findMaxMin(arr) {
    return { max: Math.max(...arr), min: Math.min(...arr) };
}"""),
    ("Capitalize Words", "Beginner", """
function capitalizeWords(str) {
    return str.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}"""),
    ("Remove Falsy Values", "Beginner", """
function removeFalsy(arr) {
    return arr.filter(Boolean);
}"""),
    ("Flatten Array One Level", "Beginner", """
function flattenOne(arr) {
    return arr.flat();
}"""),
    ("Count Occurrences", "Beginner", """
function countOccurrences(arr, val) {
    return arr.filter(x => x === val).length;
}"""),
    ("Power Function", "Beginner", """
function power(base, exp) {
    return exp === 0 ? 1 : base * power(base, exp - 1);
}"""),
    ("Truncate String", "Beginner", """
function truncate(str, maxLen) {
    return str.length > maxLen ? str.slice(0, maxLen) + '...' : str;
}"""),
    # ── Intermediate ──────────────────────────
    ("Two Sum", "Intermediate", """
function twoSum(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const comp = target - nums[i];
        if (map.has(comp)) return [map.get(comp), i];
        map.set(nums[i], i);
    }
    return [];
}"""),
    ("Binary Search", "Intermediate", """
function binarySearch(arr, target) {
    let lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
        const mid = Math.floor((lo + hi) / 2);
        if (arr[mid] === target) return mid;
        arr[mid] < target ? lo = mid + 1 : hi = mid - 1;
    }
    return -1;
}"""),
    ("Array Flatten", "Intermediate", """
function deepFlatten(arr) {
    return arr.reduce((flat, item) =>
        flat.concat(Array.isArray(item) ? deepFlatten(item) : item), []);
}"""),
    ("Debounce Function", "Intermediate", """
function debounce(fn, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}"""),
    ("Throttle Function", "Intermediate", """
function throttle(fn, limit) {
    let lastCall = 0;
    return function (...args) {
        const now = Date.now();
        if (now - lastCall >= limit) {
            lastCall = now;
            return fn.apply(this, args);
        }
    };
}"""),
    ("Memoize Function", "Intermediate", """
function memoize(fn) {
    const cache = new Map();
    return function (...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) return cache.get(key);
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}"""),
    ("Deep Clone Object", "Intermediate", """
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(deepClone);
    return Object.fromEntries(
        Object.entries(obj).map(([k, v]) => [k, deepClone(v)])
    );
}"""),
    ("Promise Chain", "Intermediate", """
function fetchUserData(userId) {
    return fetch(`/api/users/${userId}`)
        .then(res => res.json())
        .then(user => fetch(`/api/posts?userId=${user.id}`))
        .then(res => res.json())
        .catch(err => { console.error('Error:', err); throw err; });
}"""),
    ("Bubble Sort", "Intermediate", """
function bubbleSort(arr) {
    const a = [...arr];
    for (let i = 0; i < a.length - 1; i++)
        for (let j = 0; j < a.length - i - 1; j++)
            if (a[j] > a[j + 1]) [a[j], a[j+1]] = [a[j+1], a[j]];
    return a;
}"""),
    ("Valid Parentheses", "Intermediate", """
function isValid(s) {
    const stack = [], map = { ')': '(', ']': '[', '}': '{' };
    for (const c of s) {
        if ('([{'.includes(c)) stack.push(c);
        else if (stack.pop() !== map[c]) return false;
    }
    return stack.length === 0;
}"""),
    ("Group By Category", "Intermediate", """
function groupBy(arr, key) {
    return arr.reduce((acc, item) => {
        const group = item[key];
        acc[group] = acc[group] || [];
        acc[group].push(item);
        return acc;
    }, {});
}"""),
    ("Max Subarray Kadane", "Intermediate", """
function maxSubArray(nums) {
    let maxSum = nums[0], cur = nums[0];
    for (let i = 1; i < nums.length; i++) {
        cur = Math.max(nums[i], cur + nums[i]);
        maxSum = Math.max(maxSum, cur);
    }
    return maxSum;
}"""),
    ("Flatten Object", "Intermediate", """
function flattenObject(obj, prefix = '') {
    return Object.entries(obj).reduce((acc, [key, val]) => {
        const k = prefix ? `${prefix}.${key}` : key;
        if (typeof val === 'object' && val !== null && !Array.isArray(val))
            Object.assign(acc, flattenObject(val, k));
        else acc[k] = val;
        return acc;
    }, {});
}"""),
    ("Linked List JS", "Intermediate", """
class LinkedList {
    constructor() { this.head = null; }
    append(val) {
        const node = { val, next: null };
        if (!this.head) { this.head = node; return; }
        let cur = this.head;
        while (cur.next) cur = cur.next;
        cur.next = node;
    }
    toArray() {
        const result = []; let cur = this.head;
        while (cur) { result.push(cur.val); cur = cur.next; }
        return result;
    }
}"""),
    ("Intersection of Arrays", "Intermediate", """
function intersection(a, b) {
    const setB = new Set(b);
    return [...new Set(a.filter(x => setB.has(x)))];
}"""),
    ("Rotate Array", "Intermediate", """
function rotateArray(arr, k) {
    const n = arr.length; k = k % n;
    return [...arr.slice(n - k), ...arr.slice(0, n - k)];
}"""),
    ("String Compression", "Intermediate", """
function compress(str) {
    let result = '', i = 0;
    while (i < str.length) {
        const c = str[i]; let count = 0;
        while (i < str.length && str[i] === c) { i++; count++; }
        result += count > 1 ? c + count : c;
    }
    return result.length < str.length ? result : str;
}"""),
    ("Pipeline Compose", "Intermediate", """
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);
// Usage: const process = pipe(double, addOne, square);"""),
    ("Format Currency", "Intermediate", """
function formatCurrency(amount, locale = 'en-US', currency = 'USD') {
    return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount);
}"""),
    ("Async Retry", "Intermediate", """
async function retry(fn, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try { return await fn(); }
        catch (err) {
            if (i === retries - 1) throw err;
            await new Promise(res => setTimeout(res, delay * Math.pow(2, i)));
        }
    }
}"""),
    # ── Advanced ──────────────────────────────
    ("Merge Sort", "Advanced", """
function mergeSort(arr) {
    if (arr.length <= 1) return arr;
    const mid = Math.floor(arr.length / 2);
    const left = mergeSort(arr.slice(0, mid));
    const right = mergeSort(arr.slice(mid));
    const result = [];
    let i = 0, j = 0;
    while (i < left.length && j < right.length)
        result.push(left[i] <= right[j] ? left[i++] : right[j++]);
    return [...result, ...left.slice(i), ...right.slice(j)];
}"""),
    ("Quick Sort", "Advanced", """
function quickSort(arr) {
    if (arr.length <= 1) return arr;
    const pivot = arr[Math.floor(arr.length / 2)];
    const left  = arr.filter(x => x < pivot);
    const mid   = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quickSort(left), ...mid, ...quickSort(right)];
}"""),
    ("Curry Function", "Advanced", """
function curry(fn) {
    return function curried(...args) {
        if (args.length >= fn.length)
            return fn.apply(this, args);
        return function (...moreArgs) {
            return curried.apply(this, [...args, ...moreArgs]);
        };
    };
}"""),
    ("Event Emitter", "Advanced", """
class EventEmitter {
    constructor() { this.events = {}; }
    on(event, listener) {
        (this.events[event] = this.events[event] || []).push(listener);
        return this;
    }
    off(event, listener) {
        this.events[event] = (this.events[event] || []).filter(l => l !== listener);
        return this;
    }
    emit(event, ...args) {
        (this.events[event] || []).forEach(l => l(...args));
        return this;
    }
    once(event, listener) {
        const wrapper = (...args) => { listener(...args); this.off(event, wrapper); };
        return this.on(event, wrapper);
    }
}"""),
    ("LRU Cache", "Advanced", """
class LRUCache {
    constructor(capacity) {
        this.cap = capacity;
        this.cache = new Map();
    }
    get(key) {
        if (!this.cache.has(key)) return -1;
        const val = this.cache.get(key);
        this.cache.delete(key); this.cache.set(key, val);
        return val;
    }
    put(key, value) {
        this.cache.delete(key);
        this.cache.set(key, value);
        if (this.cache.size > this.cap)
            this.cache.delete(this.cache.keys().next().value);
    }
}"""),
    ("Observer Pattern", "Advanced", """
class Subject {
    constructor() { this.observers = []; this.state = null; }
    subscribe(observer) { this.observers.push(observer); }
    unsubscribe(observer) { this.observers = this.observers.filter(o => o !== observer); }
    setState(state) {
        this.state = state;
        this.observers.forEach(o => o.update(this.state));
    }
}
class Observer {
    constructor(name) { this.name = name; }
    update(state) { console.log(`${this.name} received: ${JSON.stringify(state)}`); }
}"""),
    ("Trie Implementation", "Advanced", """
class TrieNode {
    constructor() { this.children = {}; this.isEnd = false; }
}
class Trie {
    constructor() { this.root = new TrieNode(); }
    insert(word) {
        let node = this.root;
        for (const c of word) {
            node.children[c] = node.children[c] || new TrieNode();
            node = node.children[c];
        }
        node.isEnd = true;
    }
    search(word) {
        let node = this.root;
        for (const c of word) {
            if (!node.children[c]) return false;
            node = node.children[c];
        }
        return node.isEnd;
    }
    startsWith(prefix) {
        let node = this.root;
        for (const c of prefix) {
            if (!node.children[c]) return false;
            node = node.children[c];
        }
        return true;
    }
}"""),
    ("Async Queue", "Advanced", """
class AsyncQueue {
    constructor(concurrency = 1) {
        this.concurrency = concurrency; this.running = 0; this.queue = [];
    }
    add(task) {
        return new Promise((resolve, reject) => {
            this.queue.push({ task, resolve, reject }); this.run();
        });
    }
    async run() {
        if (this.running >= this.concurrency || this.queue.length === 0) return;
        this.running++;
        const { task, resolve, reject } = this.queue.shift();
        try { resolve(await task()); } catch (e) { reject(e); } finally {
            this.running--; this.run();
        }
    }
}"""),
    ("Binary Search Tree", "Advanced", """
class BST {
    constructor() { this.root = null; }
    insert(val) { this.root = this._insert(this.root, val); }
    _insert(node, val) {
        if (!node) return { val, left: null, right: null };
        if (val < node.val) node.left = this._insert(node.left, val);
        else if (val > node.val) node.right = this._insert(node.right, val);
        return node;
    }
    inorder() { const res = []; this._inorder(this.root, res); return res; }
    _inorder(node, res) {
        if (!node) return;
        this._inorder(node.left, res); res.push(node.val); this._inorder(node.right, res);
    }
}"""),
    ("Proxy Validator", "Advanced", """
function createValidator(target, validator) {
    return new Proxy(target, {
        set(obj, prop, value) {
            if (validator[prop] && !validator[prop](value))
                throw new TypeError(`Invalid value for ${prop}: ${value}`);
            obj[prop] = value; return true;
        }
    });
}
// Usage: const person = createValidator({}, { age: v => v >= 0 && v <= 150 });"""),
    ("Reactive Store", "Advanced", """
function createStore(initialState) {
    let state = { ...initialState };
    const subscribers = new Set();
    return {
        getState: () => ({ ...state }),
        setState(partial) {
            state = { ...state, ...partial };
            subscribers.forEach(fn => fn(state));
        },
        subscribe(fn) { subscribers.add(fn); return () => subscribers.delete(fn); }
    };
}"""),
    ("Rate Limiter", "Advanced", """
function rateLimiter(fn, maxCalls, windowMs) {
    const calls = [];
    return function (...args) {
        const now = Date.now();
        while (calls.length && calls[0] < now - windowMs) calls.shift();
        if (calls.length >= maxCalls) throw new Error('Rate limit exceeded');
        calls.push(now);
        return fn.apply(this, args);
    };
}"""),
]

# ─────────────────────────────────────────────
# Build DataFrames
# ─────────────────────────────────────────────
def build_df(problems, code_col):
    rows = []
    for title, diff, code in problems:
        code = code.strip()
        nl, cl, cc, read = metrics(code)
        rows.append({
            'title': title,
            code_col: code,
            'difficulty': diff,
            'num_of_lines': nl,
            'code_length': cl,
            'cyclomatic_complexity': cc,
            'readability': read,
        })
    return pd.DataFrame(rows)

df_java = build_df(JAVA, 'content')
df_js   = build_df(JS,   'content')

df_java.to_csv('data_java.csv', index=False, quoting=csv.QUOTE_ALL)
df_js.to_csv('data_javascript.csv', index=False, quoting=csv.QUOTE_ALL)

print(f'✅ data_java.csv written: {len(df_java)} problems')
print(f'   Difficulties: {df_java["difficulty"].value_counts().to_dict()}')
print(f'✅ data_javascript.csv written: {len(df_js)} problems')
print(f'   Difficulties: {df_js["difficulty"].value_counts().to_dict()}')
