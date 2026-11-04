import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

public class AlgoLab {
    /* SNIP:two_sum */
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            Integer j = seen.get(target - nums[i]);
            if (j != null) {
                return new int[] {j, i};
            }
            seen.put(nums[i], i);
        }
        return new int[0];
    }
    /* END:two_sum */

    /* SNIP:longest_unique */
    public static int longestUnique(String s) {
        Map<Character, Integer> last = new HashMap<>();
        int left = 0;
        int best = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (last.containsKey(ch) && last.get(ch) >= left) {
                left = last.get(ch) + 1;
            }
            last.put(ch, i);
            best = Math.max(best, i - left + 1);
        }
        return best;
    }
    /* END:longest_unique */

    /* SNIP:three_sum */
    public static List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> ans = new ArrayList<>();
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] > 0) {
                break;
            }
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            int left = i + 1;
            int right = nums.length - 1;
            while (left < right) {
                int total = nums[i] + nums[left] + nums[right];
                if (total == 0) {
                    ans.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    left++;
                    right--;
                    while (left < right && nums[left] == nums[left - 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right + 1]) {
                        right--;
                    }
                } else if (total < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return ans;
    }
    /* END:three_sum */

    /* SNIP:trap */
    public static int trap(int[] height) {
        int left = 0;
        int right = height.length - 1;
        int leftMax = 0;
        int rightMax = 0;
        int water = 0;
        while (left < right) {
            if (height[left] <= height[right]) {
                leftMax = Math.max(leftMax, height[left]);
                water += leftMax - height[left];
                left++;
            } else {
                rightMax = Math.max(rightMax, height[right]);
                water += rightMax - height[right];
                right--;
            }
        }
        return water;
    }
    /* END:trap */

    /* SNIP:merge_intervals */
    public static int[][] mergeIntervals(int[][] intervals) {
        if (intervals.length == 0) {
            return new int[0][];
        }
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> merged = new ArrayList<>();
        merged.add(new int[] {intervals[0][0], intervals[0][1]});
        for (int i = 1; i < intervals.length; i++) {
            int[] last = merged.get(merged.size() - 1);
            if (intervals[i][0] <= last[1]) {
                last[1] = Math.max(last[1], intervals[i][1]);
            } else {
                merged.add(new int[] {intervals[i][0], intervals[i][1]});
            }
        }
        return merged.toArray(new int[0][]);
    }
    /* END:merge_intervals */

    /* SNIP:lru */
    public static class LRUCache {
        static class Node {
            int key;
            int val;
            Node prev;
            Node next;

            Node(int key, int val) {
                this.key = key;
                this.val = val;
            }
        }

        private final int cap;
        private final Map<Integer, Node> map = new HashMap<>();
        private final Node head = new Node(0, 0);
        private final Node tail = new Node(0, 0);

        public LRUCache(int capacity) {
            this.cap = capacity;
            head.next = tail;
            tail.prev = head;
        }

        private void remove(Node node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }

        private void insertFront(Node node) {
            node.next = head.next;
            node.prev = head;
            head.next.prev = node;
            head.next = node;
        }

        public int get(int key) {
            Node node = map.get(key);
            if (node == null) {
                return -1;
            }
            remove(node);
            insertFront(node);
            return node.val;
        }

        public void put(int key, int value) {
            Node node = map.get(key);
            if (node != null) {
                node.val = value;
                remove(node);
                insertFront(node);
                return;
            }
            node = new Node(key, value);
            map.put(key, node);
            insertFront(node);
            if (map.size() > cap) {
                Node old = tail.prev;
                remove(old);
                map.remove(old.key);
            }
        }
    }
    /* END:lru */

    /* SNIP:course_schedule */
    public static boolean canFinish(int numCourses, int[][] prerequisites) {
        List<List<Integer>> graph = new ArrayList<>();
        int[] indegree = new int[numCourses];
        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] edge : prerequisites) {
            graph.get(edge[1]).add(edge[0]);
            indegree[edge[0]]++;
        }
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                queue.add(i);
            }
        }
        int taken = 0;
        while (!queue.isEmpty()) {
            int cur = queue.removeFirst();
            taken++;
            for (int next : graph.get(cur)) {
                indegree[next]--;
                if (indegree[next] == 0) {
                    queue.add(next);
                }
            }
        }
        return taken == numCourses;
    }
    /* END:course_schedule */

    /* SNIP:num_islands */
    public static int numIslands(char[][] grid) {
        if (grid.length == 0 || grid[0].length == 0) {
            return 0;
        }
        int count = 0;
        for (int r = 0; r < grid.length; r++) {
            for (int c = 0; c < grid[0].length; c++) {
                if (grid[r][c] == '1') {
                    count++;
                    sink(grid, r, c);
                }
            }
        }
        return count;
    }

    private static void sink(char[][] grid, int r, int c) {
        if (r < 0 || c < 0 || r >= grid.length || c >= grid[0].length || grid[r][c] != '1') {
            return;
        }
        grid[r][c] = '0';
        sink(grid, r + 1, c);
        sink(grid, r - 1, c);
        sink(grid, r, c + 1);
        sink(grid, r, c - 1);
    }
    /* END:num_islands */

    /* SNIP:window_max */
    public static int[] windowMax(int[] nums, int k) {
        ArrayDeque<Integer> dq = new ArrayDeque<>();
        int[] ans = new int[nums.length - k + 1];
        int pos = 0;
        for (int i = 0; i < nums.length; i++) {
            while (!dq.isEmpty() && dq.peekFirst() <= i - k) {
                dq.removeFirst();
            }
            while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[i]) {
                dq.removeLast();
            }
            dq.addLast(i);
            if (i >= k - 1) {
                ans[pos++] = nums[dq.peekFirst()];
            }
        }
        return ans;
    }
    /* END:window_max */

    /* SNIP:edit_distance */
    public static int editDistance(String word1, String word2) {
        int m = word1.length();
        int n = word2.length();
        int[] dp = new int[n + 1];
        for (int j = 0; j <= n; j++) {
            dp[j] = j;
        }
        for (int i = 1; i <= m; i++) {
            int prev = dp[0];
            dp[0] = i;
            for (int j = 1; j <= n; j++) {
                int saved = dp[j];
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    dp[j] = prev;
                } else {
                    dp[j] = 1 + Math.min(prev, Math.min(dp[j], dp[j - 1]));
                }
                prev = saved;
            }
        }
        return dp[n];
    }
    /* END:edit_distance */

    /* SNIP:coin_change */
    public static int coinChange(int[] coins, int amount) {
        int inf = amount + 1;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, inf);
        dp[0] = 0;
        for (int money = 1; money <= amount; money++) {
            for (int coin : coins) {
                if (coin <= money) {
                    dp[money] = Math.min(dp[money], dp[money - coin] + 1);
                }
            }
        }
        return dp[amount] > amount ? -1 : dp[amount];
    }
    /* END:coin_change */

    /* SNIP:min_window */
    public static String minWindow(String s, String t) {
        if (s.isEmpty() || t.isEmpty()) {
            return "";
        }
        Map<Character, Integer> need = new HashMap<>();
        for (int i = 0; i < t.length(); i++) {
            need.merge(t.charAt(i), 1, Integer::sum);
        }
        int missing = t.length();
        int bestLeft = 0;
        int bestRight = s.length() + 1;
        int left = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            if (need.getOrDefault(ch, 0) > 0) {
                missing--;
            }
            need.put(ch, need.getOrDefault(ch, 0) - 1);
            while (missing == 0) {
                if (right - left < bestRight - bestLeft) {
                    bestLeft = left;
                    bestRight = right;
                }
                char leftCh = s.charAt(left);
                need.put(leftCh, need.get(leftCh) + 1);
                if (need.get(leftCh) > 0) {
                    missing++;
                }
                left++;
            }
        }
        if (bestRight == s.length() + 1) {
            return "";
        }
        return s.substring(bestLeft, bestRight + 1);
    }
    /* END:min_window */

    /* SNIP:median_finder */
    public static class MedianFinder {
        private final PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());
        private final PriorityQueue<Integer> high = new PriorityQueue<>();

        public void addNum(int num) {
            low.offer(num);
            high.offer(low.poll());
            if (high.size() > low.size()) {
                low.offer(high.poll());
            }
        }

        public double findMedian() {
            if (low.size() > high.size()) {
                return low.peek();
            }
            return (low.peek() + high.peek()) / 2.0;
        }
    }
    /* END:median_finder */

    /* SNIP:min_cost */
    public static int minCost(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        int[][] dist = new int[rows][cols];
        for (int[] row : dist) {
            Arrays.fill(row, Integer.MAX_VALUE);
        }
        dist[0][0] = grid[0][0];
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        heap.offer(new int[] {grid[0][0], 0, 0});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!heap.isEmpty()) {
            int[] cur = heap.poll();
            int cost = cur[0];
            int r = cur[1];
            int c = cur[2];
            if (cost != dist[r][c]) {
                continue;
            }
            if (r == rows - 1 && c == cols - 1) {
                return cost;
            }
            for (int[] d : dirs) {
                int nr = r + d[0];
                int nc = c + d[1];
                if (nr < 0 || nc < 0 || nr >= rows || nc >= cols) {
                    continue;
                }
                int next = cost + grid[nr][nc];
                if (next < dist[nr][nc]) {
                    dist[nr][nc] = next;
                    heap.offer(new int[] {next, nr, nc});
                }
            }
        }
        return -1;
    }
    /* END:min_cost */

    /* SNIP:k_nearest */
    public static double haversineM(double lat1, double lon1, double lat2, double lon2) {
        double radius = 6_371_000.0;
        double phi1 = Math.toRadians(lat1);
        double phi2 = Math.toRadians(lat2);
        double dPhi = Math.toRadians(lat2 - lat1);
        double dLam = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dPhi / 2) * Math.sin(dPhi / 2)
                + Math.cos(phi1) * Math.cos(phi2) * Math.sin(dLam / 2) * Math.sin(dLam / 2);
        return 2 * radius * Math.asin(Math.min(1.0, Math.sqrt(a)));
    }

    public static List<String> kNearest(String[] ids, double[] lats, double[] lons, double qlat, double qlon, int k) {
        class Near implements Comparable<Near> {
            final double dist;
            final String id;

            Near(double dist, String id) {
                this.dist = dist;
                this.id = id;
            }

            @Override
            public int compareTo(Near other) {
                return Double.compare(other.dist, this.dist);
            }
        }
        PriorityQueue<Near> heap = new PriorityQueue<>();
        for (int i = 0; i < ids.length; i++) {
            double dist = haversineM(qlat, qlon, lats[i], lons[i]);
            if (heap.size() < k) {
                heap.offer(new Near(dist, ids[i]));
            } else if (dist < heap.peek().dist) {
                heap.poll();
                heap.offer(new Near(dist, ids[i]));
            }
        }
        List<Near> found = new ArrayList<>(heap);
        found.sort((a, b) -> {
            int cmp = Double.compare(a.dist, b.dist);
            return cmp != 0 ? cmp : a.id.compareTo(b.id);
        });
        List<String> ans = new ArrayList<>();
        for (Near near : found) {
            ans.add(near.id);
        }
        return ans;
    }
    /* END:k_nearest */

    /* SNIP:point_in_polygon */
    public static boolean pointInPolygon(double x, double y, double[][] polygon) {
        boolean inside = false;
        int j = polygon.length - 1;
        for (int i = 0; i < polygon.length; i++) {
            double xi = polygon[i][0];
            double yi = polygon[i][1];
            double xj = polygon[j][0];
            double yj = polygon[j][1];
            if ((yi > y) != (yj > y)) {
                double xCross = (xj - xi) * (y - yi) / (yj - yi) + xi;
                if (x < xCross) {
                    inside = !inside;
                }
            }
            j = i;
        }
        return inside;
    }
    /* END:point_in_polygon */

    /* SNIP:geohash_encode */
    private static final String BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";

    public static String geohashEncode(double lat, double lon, int precision) {
        double[] latRange = {-90.0, 90.0};
        double[] lonRange = {-180.0, 180.0};
        StringBuilder hash = new StringBuilder();
        int bit = 0;
        int value = 0;
        boolean even = true;
        while (hash.length() < precision) {
            if (even) {
                double mid = (lonRange[0] + lonRange[1]) / 2.0;
                if (lon >= mid) {
                    value = (value << 1) | 1;
                    lonRange[0] = mid;
                } else {
                    value <<= 1;
                    lonRange[1] = mid;
                }
            } else {
                double mid = (latRange[0] + latRange[1]) / 2.0;
                if (lat >= mid) {
                    value = (value << 1) | 1;
                    latRange[0] = mid;
                } else {
                    value <<= 1;
                    latRange[1] = mid;
                }
            }
            even = !even;
            bit++;
            if (bit == 5) {
                hash.append(BASE32.charAt(value));
                bit = 0;
                value = 0;
            }
        }
        return hash.toString();
    }
    /* END:geohash_encode */

    /* SNIP:ship_days */
    public static int shipWithinDays(int[] weights, int days) {
        int low = 0;
        int high = 0;
        for (int weight : weights) {
            low = Math.max(low, weight);
            high += weight;
        }
        while (low < high) {
            int mid = (low + high) >>> 1;
            if (feasible(weights, days, mid)) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }
        return low;
    }

    private static boolean feasible(int[] weights, int days, int cap) {
        int used = 1;
        int load = 0;
        for (int weight : weights) {
            if (load + weight > cap) {
                used++;
                load = 0;
            }
            load += weight;
        }
        return used <= days;
    }
    /* END:ship_days */

    public static void main(String[] args) {
        check(Arrays.equals(twoSum(new int[] {2, 7, 11, 15}, 9), new int[] {0, 1}), "twoSum");
        check(Arrays.equals(twoSum(new int[] {3, 3}, 6), new int[] {0, 1}), "twoSum2");
        check(longestUnique("abcabcbb") == 3, "longest");
        check(longestUnique("bbbbb") == 1, "longest2");
        check(longestUnique("") == 0, "longest3");
        check(threeSum(new int[] {-1, 0, 1, 2, -1, -4}).toString().equals("[[-1, -1, 2], [-1, 0, 1]]"), "three");
        check(trap(new int[] {0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1}) == 6, "trap");
        check(trap(new int[0]) == 0, "trap0");
        int[][] merged = mergeIntervals(new int[][] {{1, 3}, {2, 6}, {8, 10}, {15, 18}});
        check(merged.length == 3 && merged[0][0] == 1 && merged[0][1] == 6 && merged[2][0] == 15, "merge");
        check(mergeIntervals(new int[][] {{1, 4}, {4, 5}})[0][1] == 5, "mergeTouch");

        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        check(cache.get(1) == 1, "lru1");
        cache.put(3, 3);
        check(cache.get(2) == -1, "lru2");
        cache.put(4, 4);
        check(cache.get(1) == -1, "lru3");
        check(cache.get(3) == 3 && cache.get(4) == 4, "lru4");

        check(canFinish(2, new int[][] {{1, 0}}), "course");
        check(!canFinish(2, new int[][] {{1, 0}, {0, 1}}), "courseCycle");
        char[][] grid = {{'1', '1', '0'}, {'1', '0', '0'}, {'0', '0', '1'}};
        check(numIslands(grid) == 2, "islands");
        check(Arrays.equals(windowMax(new int[] {1, 3, -1, -3, 5, 3, 6, 7}, 3), new int[] {3, 3, 5, 5, 6, 7}), "window");
        check(editDistance("horse", "ros") == 3, "edit");
        check(editDistance("", "a") == 1, "editEmpty");
        check(coinChange(new int[] {1, 2, 5}, 11) == 3, "coin");
        check(coinChange(new int[] {2}, 3) == -1, "coinImpossible");
        check(minWindow("ADOBECODEBANC", "ABC").equals("BANC"), "windowStr");
        check(minWindow("a", "aa").isEmpty(), "windowEmpty");

        MedianFinder med = new MedianFinder();
        med.addNum(1);
        med.addNum(2);
        check(med.findMedian() == 1.5, "median");
        med.addNum(3);
        check(med.findMedian() == 2.0, "median2");
        check(minCost(new int[][] {{1, 3, 1}, {1, 5, 1}, {4, 2, 1}}) == 7, "cost");
        List<String> near = kNearest(
                new String[] {"c", "a", "b"},
                new double[] {31.2, 39.90, 40.00},
                new double[] {121.5, 116.40, 116.40},
                39.91,
                116.41,
                2);
        check(near.equals(Arrays.asList("a", "b")), "near " + near);
        double[][] square = {{0, 0}, {4, 0}, {4, 4}, {0, 4}};
        check(pointInPolygon(1, 1, square), "pipIn");
        check(!pointInPolygon(5, 5, square), "pipOut");
        String hash = geohashEncode(57.64911, 10.40744, 11);
        check(hash.equals("u4pruydqqvj"), "geohash " + hash);
        check(shipWithinDays(new int[] {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 5) == 15, "ship");
        System.out.println("java ok");
    }

    private static void check(boolean cond, String name) {
        if (!cond) {
            throw new AssertionError(name);
        }
    }
}
