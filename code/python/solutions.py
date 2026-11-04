"""Interview reference solutions. Snippets between SNIP/END are shown on the site."""

import heapq
import math


# SNIP:two_sum
def two_sum(nums, target):
    """一次哈希。边扫边查补数，保证返回的是更早出现的下标。"""
    seen = {}
    for i, x in enumerate(nums):
        j = seen.get(target - x)
        if j is not None:
            return [j, i]
        seen[x] = i
    return []
# END:two_sum


# SNIP:longest_unique
def longest_unique(s):
    """滑动窗口。last 记录字符上次出现的位置，左边界只前进不后退。"""
    last = {}
    left = best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = i
        best = max(best, i - left + 1)
    return best
# END:longest_unique


# SNIP:three_sum
def three_sum(nums):
    """排序后固定一个数，双指针找两数之和。跳过重复值，避免结果集重复。"""
    nums = sorted(nums)
    n = len(nums)
    ans = []
    for i in range(n):
        if nums[i] > 0:
            break
        if i and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                ans.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return ans
# END:three_sum


# SNIP:trap
def trap(height):
    """双指针。矮的一侧决定水位，哪侧更低就结算哪侧。"""
    left, right = 0, len(height) - 1
    left_max = right_max = water = 0
    while left < right:
        if height[left] <= height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
# END:trap


# SNIP:merge_intervals
def merge_intervals(intervals):
    """停留时间段合并。按开始时间排序，只和当前结果的最后一段比。"""
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda it: it[0])
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
# END:merge_intervals


# SNIP:lru
class _Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    """哈希表定位节点，双向链表维护使用顺序。头哨兵后是最新，尾哨兵前是最旧。"""

    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        node = self.map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._insert_front(node)
        return node.val

    def put(self, key, value):
        node = self.map.get(key)
        if node is not None:
            node.val = value
            self._remove(node)
            self._insert_front(node)
            return
        node = _Node(key, value)
        self.map[key] = node
        self._insert_front(node)
        if len(self.map) > self.cap:
            old = self.tail.prev
            self._remove(old)
            del self.map[old.key]
# END:lru


# SNIP:course_schedule
def can_finish(num_courses, prerequisites):
    """拓扑排序。入度为 0 的课先上，能上完则无环。"""
    graph = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for course, prev in prerequisites:
        graph[prev].append(course)
        indegree[course] += 1
    queue = [i for i in range(num_courses) if indegree[i] == 0]
    taken = 0
    while queue:
        cur = queue.pop()
        taken += 1
        for nxt in graph[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return taken == num_courses
# END:course_schedule


# SNIP:num_islands
def num_islands(grid):
    """网格 DFS。沉掉整座岛，避免重复计数。可类比商圈连通块。"""
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])

    def sink(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        sink(r + 1, c)
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count
# END:num_islands


# SNIP:window_max
def window_max(nums, k):
    """单调递减队列，存下标。队头永远是当前窗口最大值的下标。"""
    from collections import deque

    dq = deque()
    ans = []
    for i, value in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= value:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            ans.append(nums[dq[0]])
    return ans
# END:window_max


# SNIP:edit_distance
def edit_distance(word1, word2):
    """滚动数组。插入、删除、替换取最小，相同字符则沿对角线。"""
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            saved = dp[j]
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = saved
    return dp[n]
# END:edit_distance


# SNIP:coin_change
def coin_change(coins, amount):
    """完全背包。dp[a] 是凑出金额 a 的最少硬币数。"""
    inf = amount + 1
    dp = [0] + [inf] * amount
    for money in range(1, amount + 1):
        for coin in coins:
            if coin <= money:
                dp[money] = min(dp[money], dp[money - coin] + 1)
    return -1 if dp[amount] > amount else dp[amount]
# END:coin_change


# SNIP:min_window
def min_window(s, t):
    """欠账计数。missing 归零时窗口覆盖了 t，然后尽量收缩左边界。"""
    if not s or not t:
        return ""
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    missing = len(t)
    best_left, best_right = 0, len(s) + 1
    left = 0
    for right, ch in enumerate(s):
        if need.get(ch, 0) > 0:
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
        while missing == 0:
            if right - left < best_right - best_left:
                best_left, best_right = left, right
            left_ch = s[left]
            need[left_ch] += 1
            if need[left_ch] > 0:
                missing += 1
            left += 1
    if best_right == len(s) + 1:
        return ""
    return s[best_left : best_right + 1]
# END:min_window


# SNIP:median_finder
class MedianFinder:
    """大根堆放较小的一半，小根堆放较大的一半。大根堆数量不少于小根堆。"""

    def __init__(self):
        self.low = []
        self.high = []

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0
# END:median_finder


# SNIP:min_cost
def min_cost(grid):
    """带权网格最短路。边权非负，用 Dijkstra。代价定义为进入格子的成本。"""
    if not grid or not grid[0]:
        return -1
    rows, cols = len(grid), len(grid[0])
    dist = [[math.inf] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]
    while heap:
        cost, r, c = heapq.heappop(heap)
        if cost != dist[r][c]:
            continue
        if r == rows - 1 and c == cols - 1:
            return cost
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nxt = cost + grid[nr][nc]
                if nxt < dist[nr][nc]:
                    dist[nr][nc] = nxt
                    heapq.heappush(heap, (nxt, nr, nc))
    return -1
# END:min_cost


# SNIP:k_nearest
def haversine_m(lat1, lon1, lat2, lon2):
    """球面大圆距离，单位米。地球半径取 6371000，城市级业务够用。"""
    radius = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def k_nearest(points, qlat, qlon, k):
    """大小为 k 的大根堆。points 元素是 (id, lat, lon)。结果按距离、再按 id 排序。"""
    if k <= 0 or not points:
        return []
    heap = []
    for pid, lat, lon in points:
        dist = haversine_m(qlat, qlon, lat, lon)
        item = (-dist, pid)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif dist < -heap[0][0]:
            heapq.heapreplace(heap, item)
    ordered = sorted(((-neg, pid) for neg, pid in heap), key=lambda it: (it[0], it[1]))
    return [pid for _, pid in ordered]
# END:k_nearest


# SNIP:point_in_polygon
def point_in_polygon(x, y, polygon):
    """射线法。从点向右发出水平射线，与边相交次数为奇数则在内。
    水平边不计数；顶点只在「边跨过该 y」时计入，避免重复。
    落在边界上的结果不稳定，业务上要单独定义。
    """
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > y) != (yj > y):
            x_cross = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_cross:
                inside = not inside
        j = i
    return inside
# END:point_in_polygon


# SNIP:geohash_encode
_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(lat, lon, precision=8):
    """经纬度二分，先经度后纬度交错，每 5 位映射一个 base32 字符。"""
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    chars = []
    bit = value = 0
    even = True
    while len(chars) < precision:
        if even:
            mid = (lon_range[0] + lon_range[1]) / 2.0
            if lon >= mid:
                value = (value << 1) | 1
                lon_range[0] = mid
            else:
                value <<= 1
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2.0
            if lat >= mid:
                value = (value << 1) | 1
                lat_range[0] = mid
            else:
                value <<= 1
                lat_range[1] = mid
        even = not even
        bit += 1
        if bit == 5:
            chars.append(_BASE32[value])
            bit = value = 0
    return "".join(chars)
# END:geohash_encode


# SNIP:ship_days
def ship_within_days(weights, days):
    """二分运力。下界是最重的一件，上界是货物总重。判定函数单调。"""
    low, high = max(weights), sum(weights)

    def feasible(cap):
        used_days = 1
        load = 0
        for weight in weights:
            if load + weight > cap:
                used_days += 1
                load = 0
            load += weight
        return used_days <= days

    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1
    return low
# END:ship_days


def _run_tests():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 3], 6) == [0, 1]
    assert longest_unique("abcabcbb") == 3
    assert longest_unique("bbbbb") == 1
    assert longest_unique("") == 0
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum([0, 0, 0]) == [[0, 0, 0]]
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap([]) == 0
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]

    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)
    assert cache.get(2) == -1
    cache.put(4, 4)
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    assert can_finish(2, [[1, 0]]) is True
    assert can_finish(2, [[1, 0], [0, 1]]) is False
    grid = [["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]]
    assert num_islands(grid) == 2
    assert window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("", "a") == 1
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1
    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("a", "aa") == ""

    med = MedianFinder()
    med.add_num(1)
    med.add_num(2)
    assert med.find_median() == 1.5
    med.add_num(3)
    assert med.find_median() == 2.0

    assert min_cost([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    points = [("c", 31.2, 121.5), ("a", 39.90, 116.40), ("b", 40.00, 116.40)]
    assert k_nearest(points, 39.91, 116.41, 2) == ["a", "b"]
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert point_in_polygon(1, 1, square) is True
    assert point_in_polygon(5, 5, square) is False
    assert geohash_encode(57.64911, 10.40744, 11) == "u4pruydqqvj"
    assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    print("python ok")


if __name__ == "__main__":
    _run_tests()
