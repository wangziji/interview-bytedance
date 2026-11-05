import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

public class MoreLab {
    static class ListNode {
        int val;
        ListNode next;

        ListNode(int val) {
            this.val = val;
        }

        ListNode(int val, ListNode next) {
            this.val = val;
            this.next = next;
        }
    }

    static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;

        TreeNode(int val) {
            this.val = val;
        }
    }

    /* SNIP:reverse_list */
    public static ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode cur = head;
        while (cur != null) {
            ListNode nxt = cur.next;
            cur.next = prev;
            prev = cur;
            cur = nxt;
        }
        return prev;
    }
    /* END:reverse_list */

    /* SNIP:has_cycle */
    public static boolean hasCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                return true;
            }
        }
        return false;
    }
    /* END:has_cycle */

    /* SNIP:merge_two_lists */
    public static ListNode mergeTwoLists(ListNode left, ListNode right) {
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        while (left != null && right != null) {
            if (left.val <= right.val) {
                cur.next = left;
                left = left.next;
            } else {
                cur.next = right;
                right = right.next;
            }
            cur = cur.next;
        }
        cur.next = left != null ? left : right;
        return dummy.next;
    }
    /* END:merge_two_lists */

    /* SNIP:add_two_numbers */
    public static ListNode addTwoNumbers(ListNode left, ListNode right) {
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        int carry = 0;
        while (left != null || right != null || carry != 0) {
            int total = carry;
            if (left != null) {
                total += left.val;
                left = left.next;
            }
            if (right != null) {
                total += right.val;
                right = right.next;
            }
            carry = total / 10;
            cur.next = new ListNode(total % 10);
            cur = cur.next;
        }
        return dummy.next;
    }
    /* END:add_two_numbers */

    /* SNIP:reverse_k_group */
    public static ListNode reverseKGroup(ListNode head, int k) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;
        while (true) {
            ListNode end = prev;
            for (int i = 0; i < k; i++) {
                end = end.next;
                if (end == null) {
                    return dummy.next;
                }
            }
            ListNode start = prev.next;
            ListNode nxt = end.next;
            prev.next = reverseRange(start, nxt);
            prev = start;
        }
    }

    private static ListNode reverseRange(ListNode start, ListNode stop) {
        ListNode prev = stop;
        ListNode cur = start;
        while (cur != stop) {
            ListNode nxt = cur.next;
            cur.next = prev;
            prev = cur;
            cur = nxt;
        }
        return prev;
    }
    /* END:reverse_k_group */

    /* SNIP:merge_k_lists */
    public static ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> heap = new PriorityQueue<>((a, b) -> Integer.compare(a.val, b.val));
        for (ListNode node : lists) {
            if (node != null) {
                heap.offer(node);
            }
        }
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        while (!heap.isEmpty()) {
            ListNode node = heap.poll();
            cur.next = node;
            cur = cur.next;
            if (node.next != null) {
                heap.offer(node.next);
            }
        }
        return dummy.next;
    }
    /* END:merge_k_lists */

    /* SNIP:level_order */
    public static List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> ans = new ArrayList<>();
        if (root == null) {
            return ans;
        }
        ArrayDeque<TreeNode> queue = new ArrayDeque<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            List<Integer> level = new ArrayList<>();
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.removeFirst();
                level.add(node.val);
                if (node.left != null) {
                    queue.add(node.left);
                }
                if (node.right != null) {
                    queue.add(node.right);
                }
            }
            ans.add(level);
        }
        return ans;
    }
    /* END:level_order */

    /* SNIP:lowest_common_ancestor */
    public static TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) {
            return root;
        }
        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);
        if (left != null && right != null) {
            return root;
        }
        return left != null ? left : right;
    }
    /* END:lowest_common_ancestor */

    /* SNIP:diameter */
    public static int diameter(TreeNode root) {
        int[] best = new int[1];
        height(root, best);
        return best[0];
    }

    private static int height(TreeNode node, int[] best) {
        if (node == null) {
            return 0;
        }
        int left = height(node.left, best);
        int right = height(node.right, best);
        best[0] = Math.max(best[0], left + right);
        return Math.max(left, right) + 1;
    }
    /* END:diameter */

    /* SNIP:is_valid_bst */
    public static boolean isValidBST(TreeNode root) {
        return valid(root, Long.MIN_VALUE, Long.MAX_VALUE);
    }

    private static boolean valid(TreeNode node, long low, long high) {
        if (node == null) {
            return true;
        }
        if (node.val <= low || node.val >= high) {
            return false;
        }
        return valid(node.left, low, node.val) && valid(node.right, node.val, high);
    }
    /* END:is_valid_bst */

    /* SNIP:max_path_sum */
    public static int maxPathSum(TreeNode root) {
        int[] best = new int[] {Integer.MIN_VALUE};
        gain(root, best);
        return best[0];
    }

    private static int gain(TreeNode node, int[] best) {
        if (node == null) {
            return 0;
        }
        int left = Math.max(gain(node.left, best), 0);
        int right = Math.max(gain(node.right, best), 0);
        best[0] = Math.max(best[0], node.val + left + right);
        return node.val + Math.max(left, right);
    }
    /* END:max_path_sum */

    /* SNIP:search_matrix */
    public static boolean searchMatrix(int[][] matrix, int target) {
        if (matrix.length == 0 || matrix[0].length == 0) {
            return false;
        }
        int row = 0;
        int col = matrix[0].length - 1;
        while (row < matrix.length && col >= 0) {
            int value = matrix[row][col];
            if (value == target) {
                return true;
            }
            if (value > target) {
                col--;
            } else {
                row++;
            }
        }
        return false;
    }
    /* END:search_matrix */

    /* SNIP:kth_largest */
    public static int kthLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int value : nums) {
            heap.offer(value);
            if (heap.size() > k) {
                heap.poll();
            }
        }
        return heap.peek();
    }
    /* END:kth_largest */

    /* SNIP:sort_colors */
    public static void sortColors(int[] nums) {
        int p0 = 0;
        int i = 0;
        int p2 = nums.length - 1;
        while (i <= p2) {
            if (nums[i] == 0) {
                swap(nums, i, p0);
                p0++;
                i++;
            } else if (nums[i] == 2) {
                swap(nums, i, p2);
                p2--;
            } else {
                i++;
            }
        }
    }

    private static void swap(int[] nums, int i, int j) {
        int tmp = nums[i];
        nums[i] = nums[j];
        nums[j] = tmp;
    }
    /* END:sort_colors */

    /* SNIP:sort_four */
    public static void sortFour(int[] nums) {
        int[] count = new int[4];
        for (int value : nums) {
            count[value]++;
        }
        int index = 0;
        for (int value = 0; value < 4; value++) {
            for (int times = 0; times < count[value]; times++) {
                nums[index++] = value;
            }
        }
    }
    /* END:sort_four */

    /* SNIP:lis_length */
    public static int lisLength(int[] nums) {
        int[] tails = new int[nums.length];
        int size = 0;
        for (int value : nums) {
            int lo = 0;
            int hi = size;
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (tails[mid] < value) {
                    lo = mid + 1;
                } else {
                    hi = mid;
                }
            }
            tails[lo] = value;
            if (lo == size) {
                size++;
            }
        }
        return size;
    }
    /* END:lis_length */

    /* SNIP:wiggle_length */
    public static int wiggleLength(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        int up = 1;
        int down = 1;
        for (int i = 1; i < nums.length; i++) {
            if (nums[i] > nums[i - 1]) {
                up = down + 1;
            } else if (nums[i] < nums[i - 1]) {
                down = up + 1;
            }
        }
        return Math.max(up, down);
    }
    /* END:wiggle_length */

    /* SNIP:word_break */
    public static boolean wordBreak(String s, List<String> wordDict) {
        Set<String> words = new HashSet<>(wordDict);
        boolean[] dp = new boolean[s.length() + 1];
        dp[0] = true;
        for (int end = 1; end <= s.length(); end++) {
            for (int start = 0; start < end; start++) {
                if (dp[start] && words.contains(s.substring(start, end))) {
                    dp[end] = true;
                    break;
                }
            }
        }
        return dp[s.length()];
    }
    /* END:word_break */

    /* SNIP:maximal_square */
    public static int maximalSquare(char[][] matrix) {
        if (matrix.length == 0 || matrix[0].length == 0) {
            return 0;
        }
        int cols = matrix[0].length;
        int[] dp = new int[cols + 1];
        int best = 0;
        for (char[] row : matrix) {
            int prev = 0;
            for (int c = 1; c <= cols; c++) {
                int saved = dp[c];
                if (row[c - 1] == '1') {
                    dp[c] = Math.min(dp[c], Math.min(dp[c - 1], prev)) + 1;
                    best = Math.max(best, dp[c]);
                } else {
                    dp[c] = 0;
                }
                prev = saved;
            }
        }
        return best * best;
    }
    /* END:maximal_square */

    /* SNIP:min_remove_valid */
    public static String minRemoveValid(String s) {
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        boolean[] remove = new boolean[s.length()];
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '(') {
                stack.push(i);
            } else if (ch == ')') {
                if (!stack.isEmpty()) {
                    stack.pop();
                } else {
                    remove[i] = true;
                }
            }
        }
        while (!stack.isEmpty()) {
            remove[stack.pop()] = true;
        }
        StringBuilder ans = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (!remove[i]) {
                ans.append(s.charAt(i));
            }
        }
        return ans.toString();
    }
    /* END:min_remove_valid */

    /* SNIP:quick_sort */
    public static void quickSort(int[] nums) {
        sort(nums, 0, nums.length - 1);
    }

    private static void sort(int[] nums, int lo, int hi) {
        if (lo >= hi) {
            return;
        }
        int pivot = nums[hi];
        int store = lo;
        for (int i = lo; i < hi; i++) {
            if (nums[i] < pivot) {
                swap(nums, store, i);
                store++;
            }
        }
        swap(nums, store, hi);
        sort(nums, lo, store - 1);
        sort(nums, store + 1, hi);
    }
    /* END:quick_sort */

    /* SNIP:daily_temperatures */
    public static int[] dailyTemperatures(int[] temps) {
        int[] ans = new int[temps.length];
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < temps.length; i++) {
            while (!stack.isEmpty() && temps[stack.peek()] < temps[i]) {
                int j = stack.pop();
                ans[j] = i - j;
            }
            stack.push(i);
        }
        return ans;
    }
    /* END:daily_temperatures */

    /* SNIP:longest_consecutive */
    public static int longestConsecutive(int[] nums) {
        Set<Integer> pool = new HashSet<>();
        for (int value : nums) {
            pool.add(value);
        }
        int best = 0;
        for (int value : pool) {
            if (pool.contains(value - 1)) {
                continue;
            }
            int length = 1;
            while (pool.contains(value + length)) {
                length++;
            }
            best = Math.max(best, length);
        }
        return best;
    }
    /* END:longest_consecutive */

    /* SNIP:product_except_self */
    public static int[] productExceptSelf(int[] nums) {
        int n = nums.length;
        int[] ans = new int[n];
        Arrays.fill(ans, 1);
        int left = 1;
        for (int i = 0; i < n; i++) {
            ans[i] = left;
            left *= nums[i];
        }
        int right = 1;
        for (int i = n - 1; i >= 0; i--) {
            ans[i] *= right;
            right *= nums[i];
        }
        return ans;
    }
    /* END:product_except_self */

    /* SNIP:median_sorted */
    public static double medianSorted(int[] left, int[] right) {
        if (left.length > right.length) {
            return medianSorted(right, left);
        }
        int m = left.length;
        int n = right.length;
        int half = (m + n + 1) / 2;
        int lo = 0;
        int hi = m;
        while (lo <= hi) {
            int i = (lo + hi) >>> 1;
            int j = half - i;
            int leftMax = i == 0 ? Integer.MIN_VALUE : left[i - 1];
            int leftMin = i == m ? Integer.MAX_VALUE : left[i];
            int rightMax = j == 0 ? Integer.MIN_VALUE : right[j - 1];
            int rightMin = j == n ? Integer.MAX_VALUE : right[j];
            if (leftMax <= rightMin && rightMax <= leftMin) {
                if (((m + n) & 1) == 1) {
                    return Math.max(leftMax, rightMax);
                }
                return (Math.max(leftMax, rightMax) + Math.min(leftMin, rightMin)) / 2.0;
            }
            if (leftMax > rightMin) {
                hi = i - 1;
            } else {
                lo = i + 1;
            }
        }
        return 0;
    }
    /* END:median_sorted */

    /* SNIP:subarray_sum */
    public static int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> seen = new HashMap<>();
        seen.put(0, 1);
        int total = 0;
        int ans = 0;
        for (int value : nums) {
            total += value;
            ans += seen.getOrDefault(total - k, 0);
            seen.put(total, seen.getOrDefault(total, 0) + 1);
        }
        return ans;
    }
    /* END:subarray_sum */

    /* SNIP:top_k_frequent */
    public static int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int value : nums) {
            freq.merge(value, 1, Integer::sum);
        }
        List<Integer>[] buckets = new List[nums.length + 1];
        for (Map.Entry<Integer, Integer> entry : freq.entrySet()) {
            int count = entry.getValue();
            if (buckets[count] == null) {
                buckets[count] = new ArrayList<>();
            }
            buckets[count].add(entry.getKey());
        }
        int[] ans = new int[k];
        int filled = 0;
        for (int count = buckets.length - 1; count > 0 && filled < k; count--) {
            if (buckets[count] == null) {
                continue;
            }
            for (int value : buckets[count]) {
                ans[filled++] = value;
                if (filled == k) {
                    break;
                }
            }
        }
        return ans;
    }
    /* END:top_k_frequent */

    /* SNIP:min_meeting_rooms */
    public static int minMeetingRooms(int[][] intervals) {
        int[] starts = new int[intervals.length];
        int[] ends = new int[intervals.length];
        for (int i = 0; i < intervals.length; i++) {
            starts[i] = intervals[i][0];
            ends[i] = intervals[i][1];
        }
        Arrays.sort(starts);
        Arrays.sort(ends);
        int used = 0;
        int ans = 0;
        int j = 0;
        for (int start : starts) {
            if (start < ends[j]) {
                used++;
                ans = Math.max(ans, used);
            } else {
                j++;
            }
        }
        return ans;
    }
    /* END:min_meeting_rooms */

    /* SNIP:num_provinces */
    public static int numProvinces(int[][] isConnected) {
        int n = isConnected.length;
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (isConnected[i][j] == 1) {
                    parent[find(parent, i)] = find(parent, j);
                }
            }
        }
        Set<Integer> roots = new HashSet<>();
        for (int i = 0; i < n; i++) {
            roots.add(find(parent, i));
        }
        return roots.size();
    }

    private static int find(int[] parent, int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }
    /* END:num_provinces */

    /* SNIP:search_rotated */
    public static int searchRotated(int[] nums, int target) {
        int lo = 0;
        int hi = nums.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (nums[mid] == target) {
                return mid;
            }
            if (nums[lo] <= nums[mid]) {
                if (nums[lo] <= target && target < nums[mid]) {
                    hi = mid - 1;
                } else {
                    lo = mid + 1;
                }
            } else if (nums[mid] < target && target <= nums[hi]) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        return -1;
    }
    /* END:search_rotated */

    /* SNIP:first_missing_positive */
    public static int firstMissingPositive(int[] nums) {
        int n = nums.length;
        for (int i = 0; i < n; i++) {
            while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {
                int j = nums[i] - 1;
                int tmp = nums[i];
                nums[i] = nums[j];
                nums[j] = tmp;
            }
        }
        for (int i = 0; i < n; i++) {
            if (nums[i] != i + 1) {
                return i + 1;
            }
        }
        return n + 1;
    }
    /* END:first_missing_positive */

    /* SNIP:max_profit */
    public static int maxProfit(int[] prices) {
        int best = 0;
        int low = Integer.MAX_VALUE;
        for (int price : prices) {
            low = Math.min(low, price);
            best = Math.max(best, price - low);
        }
        return best;
    }
    /* END:max_profit */

    /* SNIP:jump_game */
    public static boolean jumpGame(int[] nums) {
        int far = 0;
        for (int i = 0; i < nums.length; i++) {
            if (i > far) {
                return false;
            }
            far = Math.max(far, i + nums[i]);
        }
        return true;
    }
    /* END:jump_game */

    /* SNIP:decode_string */
    public static String decodeString(String s) {
        ArrayDeque<StringBuilder> texts = new ArrayDeque<>();
        ArrayDeque<Integer> nums = new ArrayDeque<>();
        StringBuilder cur = new StringBuilder();
        int num = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isDigit(ch)) {
                num = num * 10 + (ch - '0');
            } else if (ch == '[') {
                texts.push(cur);
                nums.push(num);
                cur = new StringBuilder();
                num = 0;
            } else if (ch == ']') {
                StringBuilder prev = texts.pop();
                int times = nums.pop();
                for (int t = 0; t < times; t++) {
                    prev.append(cur);
                }
                cur = prev;
            } else {
                cur.append(ch);
            }
        }
        return cur.toString();
    }
    /* END:decode_string */

    /* SNIP:group_anagrams */
    public static List<List<String>> groupAnagrams(String[] words) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : words) {
            char[] chars = word.toCharArray();
            Arrays.sort(chars);
            groups.computeIfAbsent(new String(chars), key -> new ArrayList<>()).add(word);
        }
        return new ArrayList<>(groups.values());
    }
    /* END:group_anagrams */

    /* SNIP:valid_parentheses */
    public static boolean validParentheses(String s) {
        Map<Character, Character> pair = Map.of(')', '(', ']', '[', '}', '{');
        ArrayDeque<Character> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '(' || ch == '[' || ch == '{') {
                stack.push(ch);
            } else if (stack.isEmpty() || stack.pop() != pair.get(ch)) {
                return false;
            }
        }
        return stack.isEmpty();
    }
    /* END:valid_parentheses */

    /* SNIP:longest_palindrome */
    public static String longestPalindrome(String s) {
        if (s.isEmpty()) {
            return "";
        }
        int start = 0;
        int end = 0;
        for (int i = 0; i < s.length(); i++) {
            int[] odd = expand(s, i, i);
            int[] even = expand(s, i, i + 1);
            if (odd[1] - odd[0] > end - start) {
                start = odd[0];
                end = odd[1];
            }
            if (even[1] - even[0] > end - start) {
                start = even[0];
                end = even[1];
            }
        }
        return s.substring(start, end + 1);
    }

    private static int[] expand(String s, int left, int right) {
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        return new int[] {left + 1, right - 1};
    }
    /* END:longest_palindrome */

    /* SNIP:container_water */
    public static int containerWater(int[] height) {
        int lo = 0;
        int hi = height.length - 1;
        int best = 0;
        while (lo < hi) {
            best = Math.max(best, Math.min(height[lo], height[hi]) * (hi - lo));
            if (height[lo] <= height[hi]) {
                lo++;
            } else {
                hi--;
            }
        }
        return best;
    }
    /* END:container_water */

    /* SNIP:unique_paths */
    public static int uniquePaths(int m, int n) {
        int[] dp = new int[n];
        Arrays.fill(dp, 1);
        for (int row = 1; row < m; row++) {
            for (int col = 1; col < n; col++) {
                dp[col] += dp[col - 1];
            }
        }
        return dp[n - 1];
    }
    /* END:unique_paths */

    /* SNIP:lcs_length */
    public static int lcsLength(String text1, String text2) {
        int[] dp = new int[text2.length() + 1];
        for (int i = 0; i < text1.length(); i++) {
            int prev = 0;
            for (int j = 1; j <= text2.length(); j++) {
                int saved = dp[j];
                if (text1.charAt(i) == text2.charAt(j - 1)) {
                    dp[j] = prev + 1;
                } else {
                    dp[j] = Math.max(dp[j], dp[j - 1]);
                }
                prev = saved;
            }
        }
        return dp[text2.length()];
    }
    /* END:lcs_length */

    /* SNIP:subsets */
    public static List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> ans = new ArrayList<>();
        dfs(nums, 0, new ArrayList<>(), ans);
        return ans;
    }

    private static void dfs(int[] nums, int start, List<Integer> path, List<List<Integer>> ans) {
        ans.add(new ArrayList<>(path));
        for (int i = start; i < nums.length; i++) {
            path.add(nums[i]);
            dfs(nums, i + 1, path, ans);
            path.remove(path.size() - 1);
        }
    }
    /* END:subsets */

    /* SNIP:gas_station */
    public static int gasStation(int[] gas, int[] cost) {
        int total = 0;
        int tank = 0;
        int start = 0;
        for (int i = 0; i < gas.length; i++) {
            int gain = gas[i] - cost[i];
            total += gain;
            tank += gain;
            if (tank < 0) {
                start = i + 1;
                tank = 0;
            }
        }
        return total < 0 ? -1 : start;
    }
    /* END:gas_station */

    /* SNIP:task_scheduler */
    public static int taskScheduler(char[] tasks, int n) {
        int[] freq = new int[26];
        for (char task : tasks) {
            freq[task - 'A']++;
        }
        int hottest = 0;
        for (int value : freq) {
            hottest = Math.max(hottest, value);
        }
        int same = 0;
        for (int value : freq) {
            if (value == hottest) {
                same++;
            }
        }
        return Math.max(tasks.length, (hottest - 1) * (n + 1) + same);
    }
    /* END:task_scheduler */

    /* SNIP:can_partition */
    public static boolean canPartition(int[] nums) {
        int total = 0;
        for (int value : nums) {
            total += value;
        }
        if ((total & 1) == 1) {
            return false;
        }
        int target = total / 2;
        boolean[] dp = new boolean[target + 1];
        dp[0] = true;
        for (int value : nums) {
            for (int cap = target; cap >= value; cap--) {
                dp[cap] = dp[cap] || dp[cap - value];
            }
        }
        return dp[target];
    }
    /* END:can_partition */

    /* SNIP:remove_k_digits */
    public static String removeKDigits(String num, int k) {
        StringBuilder stack = new StringBuilder();
        for (int i = 0; i < num.length(); i++) {
            char ch = num.charAt(i);
            while (k > 0 && stack.length() > 0 && stack.charAt(stack.length() - 1) > ch) {
                stack.deleteCharAt(stack.length() - 1);
                k--;
            }
            stack.append(ch);
        }
        stack.setLength(stack.length() - k);
        int start = 0;
        while (start < stack.length() && stack.charAt(start) == '0') {
            start++;
        }
        String out = stack.substring(start);
        return out.isEmpty() ? "0" : out;
    }
    /* END:remove_k_digits */

    public static void main(String[] args) {
        check(dump(reverseList(list(1, 2, 3, 4))).equals("[4, 3, 2, 1]"), "reverse");
        ListNode cycle = list(1, 2, 3);
        cycle.next.next.next = cycle.next;
        check(hasCycle(cycle), "cycle");
        check(!hasCycle(list(1, 2)), "nocycle");
        check(dump(mergeTwoLists(list(1, 3), list(2, 4))).equals("[1, 2, 3, 4]"), "merge2");
        check(dump(addTwoNumbers(list(2, 4, 3), list(5, 6, 4))).equals("[7, 0, 8]"), "add");
        check(dump(reverseKGroup(list(1, 2, 3, 4, 5), 2)).equals("[2, 1, 4, 3, 5]"), "k2");
        check(dump(reverseKGroup(list(1, 2, 3, 4, 5), 3)).equals("[3, 2, 1, 4, 5]"), "k3");
        check(dump(mergeKLists(new ListNode[] {list(1, 4), list(1, 3), list(2, 6)})).equals("[1, 1, 2, 3, 4, 6]"), "mergek");
        check(levelOrder(tree(3, 9, 20, null, null, 15, 7)).toString().equals("[[3], [9, 20], [15, 7]]"), "level");
        TreeNode root = tree(3, 5, 1, 6, 2, 0, 8);
        check(lowestCommonAncestor(root, root.left, root.right) == root, "lca");
        check(lowestCommonAncestor(root, root.left, root.left.right) == root.left, "lca2");
        check(diameter(tree(1, 2, 3, 4, 5)) == 3, "dia");
        check(isValidBST(tree(2, 1, 3)), "bst");
        check(!isValidBST(tree(5, 1, 4, null, null, 3, 6)), "bstbad");
        check(maxPathSum(tree(-10, 9, 20, null, null, 15, 7)) == 42, "path");
        check(searchMatrix(new int[][] {{1, 4, 7}, {2, 5, 8}, {3, 6, 9}}, 5), "matrix");
        check(!searchMatrix(new int[][] {{1, 4, 7}, {2, 5, 8}, {3, 6, 9}}, 10), "matrixno");
        check(kthLargest(new int[] {3, 2, 1, 5, 6, 4}, 2) == 5, "kth");
        int[] colors = {2, 0, 2, 1, 1, 0};
        sortColors(colors);
        check(Arrays.equals(colors, new int[] {0, 0, 1, 1, 2, 2}), "colors");
        int[] four = {3, 1, 0, 2, 1, 3, 0};
        sortFour(four);
        check(Arrays.equals(four, new int[] {0, 0, 1, 1, 2, 3, 3}), "four");
        check(lisLength(new int[] {10, 9, 2, 5, 3, 7, 101, 18}) == 4, "lis");
        check(wiggleLength(new int[] {1, 17, 5, 10, 13, 15, 10, 5, 16, 8}) == 7, "wiggle");
        check(wordBreak("leetcode", Arrays.asList("leet", "code")), "break");
        check(!wordBreak("catsandog", Arrays.asList("cats", "dog", "sand", "and", "cat")), "breakno");
        char[][] square = {
            {'1', '0', '1', '0', '0'},
            {'1', '0', '1', '1', '1'},
            {'1', '1', '1', '1', '1'},
            {'1', '0', '0', '1', '0'}
        };
        check(maximalSquare(square) == 4, "square");
        check(minRemoveValid("lee(t(c)o)de)").equals("lee(t(c)o)de"), "remove");
        check(minRemoveValid("))((").isEmpty(), "removeempty");
        int[] qs = {3, 6, 8, 10, 1, 2, 1};
        quickSort(qs);
        check(Arrays.equals(qs, new int[] {1, 1, 2, 3, 6, 8, 10}), "quick");
        check(Arrays.equals(dailyTemperatures(new int[] {73, 74, 75, 71, 69, 72, 76, 73}), new int[] {1, 1, 4, 2, 1, 1, 0, 0}), "temp");
        check(longestConsecutive(new int[] {100, 4, 200, 1, 3, 2}) == 4, "consec");
        check(Arrays.equals(productExceptSelf(new int[] {1, 2, 3, 4}), new int[] {24, 12, 8, 6}), "product");
        check(medianSorted(new int[] {1, 3}, new int[] {2}) == 2, "med");
        check(medianSorted(new int[] {1, 2}, new int[] {3, 4}) == 2.5, "med2");
        check(subarraySum(new int[] {1, 1, 1}, 2) == 2, "sumk");
        check(subarraySum(new int[] {1, 2, 3}, 3) == 2, "sumk2");
        int[] top = topKFrequent(new int[] {1, 1, 1, 2, 2, 3}, 2);
        Arrays.sort(top);
        check(Arrays.equals(top, new int[] {1, 2}), "topk");
        check(minMeetingRooms(new int[][] {{0, 30}, {5, 10}, {15, 20}}) == 2, "rooms");
        check(numProvinces(new int[][] {{1, 1, 0}, {1, 1, 0}, {0, 0, 1}}) == 2, "prov");
        check(searchRotated(new int[] {4, 5, 6, 7, 0, 1, 2}, 0) == 4, "rot");
        check(searchRotated(new int[] {4, 5, 6, 7, 0, 1, 2}, 3) == -1, "rotno");
        check(firstMissingPositive(new int[] {3, 4, -1, 1}) == 2, "miss");
        check(firstMissingPositive(new int[] {1, 2, 0}) == 3, "miss2");
        check(maxProfit(new int[] {7, 1, 5, 3, 6, 4}) == 5, "profit");
        check(jumpGame(new int[] {2, 3, 1, 1, 4}), "jump");
        check(!jumpGame(new int[] {3, 2, 1, 0, 4}), "jumpno");
        check(decodeString("3[a2[c]]").equals("accaccacc"), "dec");
        check(decodeString("2[abc]3[cd]ef").equals("abcabccdcdcdef"), "dec2");
        check(validParentheses("()[]{}") && !validParentheses("(]"), "paren");
        String pal = longestPalindrome("babad");
        check(pal.equals("bab") || pal.equals("aba"), "pal " + pal);
        check(containerWater(new int[] {1, 8, 6, 2, 5, 4, 8, 3, 7}) == 49, "water");
        check(uniquePaths(3, 7) == 28, "paths");
        check(lcsLength("abcde", "ace") == 3, "lcs");
        check(subsets(new int[] {1, 2}).size() == 4, "sub");
        check(gasStation(new int[] {1, 2, 3, 4, 5}, new int[] {3, 4, 5, 1, 2}) == 3, "gas");
        check(taskScheduler(new char[] {'A', 'A', 'A', 'B', 'B', 'B'}, 2) == 8, "task");
        check(canPartition(new int[] {1, 5, 11, 5}), "part");
        check(!canPartition(new int[] {1, 2, 3, 5}), "partno");
        check(removeKDigits("1432219", 3).equals("1219"), "rmk");
        check(removeKDigits("10200", 1).equals("200"), "rmk2");
        System.out.println("more java ok");
    }

    private static void check(boolean cond, String name) {
        if (!cond) {
            throw new AssertionError(name);
        }
    }

    private static ListNode list(int... values) {
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        for (int value : values) {
            cur.next = new ListNode(value);
            cur = cur.next;
        }
        return dummy.next;
    }

    private static String dump(ListNode node) {
        List<Integer> out = new ArrayList<>();
        while (node != null) {
            out.add(node.val);
            node = node.next;
        }
        return out.toString();
    }

    private static TreeNode tree(Integer... level) {
        if (level.length == 0 || level[0] == null) {
            return null;
        }
        TreeNode root = new TreeNode(level[0]);
        ArrayDeque<TreeNode> queue = new ArrayDeque<>();
        queue.add(root);
        int i = 1;
        while (!queue.isEmpty() && i < level.length) {
            TreeNode node = queue.removeFirst();
            if (i < level.length && level[i] != null) {
                node.left = new TreeNode(level[i]);
                queue.add(node.left);
            }
            i++;
            if (i < level.length && level[i] != null) {
                node.right = new TreeNode(level[i]);
                queue.add(node.right);
            }
            i++;
        }
        return root;
    }
}
