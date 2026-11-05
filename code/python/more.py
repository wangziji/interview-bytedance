"""Additional ByteDance-style solutions. Snippets between SNIP/END are shown on the site."""

import heapq
from collections import Counter, defaultdict, deque


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def _list(values):
    dummy = ListNode()
    cur = dummy
    for value in values:
        cur.next = ListNode(value)
        cur = cur.next
    return dummy.next


def _dump(node):
    out = []
    while node:
        out.append(node.val)
        node = node.next
    return out


def _tree(level):
    if not level:
        return None
    root = TreeNode(level[0])
    queue = deque([root])
    i = 1
    while queue and i < len(level):
        node = queue.popleft()
        if i < len(level) and level[i] is not None:
            node.left = TreeNode(level[i])
            queue.append(node.left)
        i += 1
        if i < len(level) and level[i] is not None:
            node.right = TreeNode(level[i])
            queue.append(node.right)
        i += 1
    return root


# SNIP:reverse_list
def reverse_list(head):
    """迭代反转。prev 是已经反转好的前缀。"""
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
# END:reverse_list


# SNIP:has_cycle
def has_cycle(head):
    """快慢指针。有环则快指针一定会追上慢指针。"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
# END:has_cycle


# SNIP:merge_two_lists
def merge_two_lists(left, right):
    """双指针归并。哨兵头避免单独处理空表。"""
    dummy = ListNode()
    cur = dummy
    while left and right:
        if left.val <= right.val:
            cur.next = left
            left = left.next
        else:
            cur.next = right
            right = right.next
        cur = cur.next
    cur.next = left or right
    return dummy.next
# END:merge_two_lists


# SNIP:add_two_numbers
def add_two_numbers(left, right):
    """链表表示的大数相加，低位在前。进位单独保留。"""
    dummy = ListNode()
    cur = dummy
    carry = 0
    while left or right or carry:
        total = carry
        if left:
            total += left.val
            left = left.next
        if right:
            total += right.val
            right = right.next
        carry, digit = divmod(total, 10)
        cur.next = ListNode(digit)
        cur = cur.next
    return dummy.next
# END:add_two_numbers


# SNIP:reverse_k_group
def reverse_k_group(head, k):
    """每 k 个一组反转。不足 k 个的尾部保持原样。"""

    def reverse_range(start, stop):
        prev = stop
        cur = start
        while cur is not stop:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev

    dummy = ListNode(0, head)
    prev = dummy
    while True:
        end = prev
        for _ in range(k):
            end = end.next
            if end is None:
                return dummy.next
        start = prev.next
        nxt = end.next
        prev.next = reverse_range(start, nxt)
        prev = start
# END:reverse_k_group


# SNIP:merge_k_lists
def merge_k_lists(lists):
    """小根堆。堆里放 (值, 链表编号, 节点)，编号用来打破相等值无法比较节点的问题。"""
    heap = []
    for index, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, index, node))
    dummy = ListNode()
    cur = dummy
    while heap:
        _, index, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, index, node.next))
    return dummy.next
# END:merge_k_lists


# SNIP:level_order
def level_order(root):
    """队列按层弹出。进队前记下本层节点数。"""
    if root is None:
        return []
    queue = deque([root])
    ans = []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        ans.append(level)
    return ans
# END:level_order


# SNIP:lowest_common_ancestor
def lowest_common_ancestor(root, p, q):
    """后序。左右都找到说明当前点是分岔，否则把找到的那一侧传上去。"""
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root
    return left or right
# END:lowest_common_ancestor


# SNIP:diameter
def diameter(root):
    """直径是左右高度之和的最大值，不必经过根。"""
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        left = height(node.left)
        right = height(node.right)
        best = max(best, left + right)
        return max(left, right) + 1

    height(root)
    return best
# END:diameter


# SNIP:is_valid_bst
def is_valid_bst(root):
    """带上下界。只和父节点比会漏掉祖先约束。"""

    def ok(node, low, high):
        if node is None:
            return True
        if not low < node.val < high:
            return False
        return ok(node.left, low, node.val) and ok(node.right, node.val, high)

    return ok(root, float("-inf"), float("inf"))
# END:is_valid_bst


# SNIP:max_path_sum
def max_path_sum(root):
    """节点贡献给父亲的是单边最大增益。路径可以在当前节点拐弯，拐弯值只更新答案。"""
    best = float("-inf")

    def gain(node):
        nonlocal best
        if node is None:
            return 0
        left = max(gain(node.left), 0)
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)

    gain(root)
    return best
# END:max_path_sum


# SNIP:search_matrix
def search_matrix(matrix, target):
    """从右上角出发。当前值太大就左移，太小就下移。每行每列都递增时成立。"""
    if not matrix or not matrix[0]:
        return False
    row, col = 0, len(matrix[0]) - 1
    while row < len(matrix) and col >= 0:
        value = matrix[row][col]
        if value == target:
            return True
        if value > target:
            col -= 1
        else:
            row += 1
    return False
# END:search_matrix


# SNIP:kth_largest
def kth_largest(nums, k):
    """大小为 k 的小根堆，堆顶是第 k 大。数据量大时用快排划分。"""
    heap = nums[:k]
    heapq.heapify(heap)
    for value in nums[k:]:
        if value > heap[0]:
            heapq.heapreplace(heap, value)
    return heap[0]
# END:kth_largest


# SNIP:sort_colors
def sort_colors(nums):
    """荷兰国旗。p0 左边是 0，p2 右边是 2，中间待扫描。"""
    p0 = i = 0
    p2 = len(nums) - 1
    while i <= p2:
        if nums[i] == 0:
            nums[i], nums[p0] = nums[p0], nums[i]
            p0 += 1
            i += 1
        elif nums[i] == 2:
            nums[i], nums[p2] = nums[p2], nums[i]
            p2 -= 1
        else:
            i += 1
    return nums
# END:sort_colors


# SNIP:sort_four
def sort_four(nums):
    """值域只有 0 到 3。计数后回填，时间 O(n)，额外空间 O(1)。"""
    count = [0, 0, 0, 0]
    for value in nums:
        count[value] += 1
    index = 0
    for value, times in enumerate(count):
        for _ in range(times):
            nums[index] = value
            index += 1
    return nums
# END:sort_four


# SNIP:lis_length
def lis_length(nums):
    """耐心排序。tails[i] 是长度为 i+1 的递增子序列的最小结尾。"""
    tails = []
    for value in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < value:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(value)
        else:
            tails[lo] = value
    return len(tails)
# END:lis_length


# SNIP:wiggle_length
def wiggle_length(nums):
    """上升结尾和下降结尾各维护一个长度。相等时两条都不延长。"""
    if not nums:
        return 0
    up = down = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            up = down + 1
        elif nums[i] < nums[i - 1]:
            down = up + 1
    return max(up, down)
# END:wiggle_length


# SNIP:word_break
def word_break(s, word_dict):
    """dp[i] 表示前 i 个字符能否被词典拼出。"""
    words = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for end in range(1, len(s) + 1):
        for start in range(end):
            if dp[start] and s[start:end] in words:
                dp[end] = True
                break
    return dp[-1]
# END:word_break


# SNIP:maximal_square
def maximal_square(matrix):
    """dp[i][j] 是以 (i,j) 为右下角的最大正方形边长。"""
    if not matrix or not matrix[0]:
        return 0
    rows, cols = len(matrix), len(matrix[0])
    dp = [0] * (cols + 1)
    best = prev = 0
    for r in range(1, rows + 1):
        prev = 0
        for c in range(1, cols + 1):
            saved = dp[c]
            if matrix[r - 1][c - 1] == "1":
                dp[c] = min(dp[c], dp[c - 1], prev) + 1
                best = max(best, dp[c])
            else:
                dp[c] = 0
            prev = saved
    return best * best
# END:maximal_square


# SNIP:min_remove_valid
def min_remove_valid(s):
    """栈里留未匹配的左括号下标。右括号落空时记下标。最后删掉这些下标。"""
    stack = []
    remove = set()
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if stack:
                stack.pop()
            else:
                remove.add(i)
    remove.update(stack)
    return "".join(ch for i, ch in enumerate(s) if i not in remove)
# END:min_remove_valid


# SNIP:quick_sort
def quick_sort(nums):
    """手写快排。分区把小于基准的放左边。面试要主动说最坏 O(n²) 和随机基准。"""

    def sort(lo, hi):
        if lo >= hi:
            return
        pivot = nums[hi]
        store = lo
        for i in range(lo, hi):
            if nums[i] < pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[hi] = nums[hi], nums[store]
        sort(lo, store - 1)
        sort(store + 1, hi)

    sort(0, len(nums) - 1)
    return nums
# END:quick_sort


# SNIP:daily_temperatures
def daily_temperatures(temps):
    """单调递减栈，存下标。弹出时说明右边出现了更高的温度。"""
    ans = [0] * len(temps)
    stack = []
    for i, value in enumerate(temps):
        while stack and temps[stack[-1]] < value:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans
# END:daily_temperatures


# SNIP:longest_consecutive
def longest_consecutive(nums):
    """只从连续段的起点开始数。哈希集合把查找变成 O(1)。"""
    pool = set(nums)
    best = 0
    for value in pool:
        if value - 1 in pool:
            continue
        length = 1
        while value + length in pool:
            length += 1
        best = max(best, length)
    return best
# END:longest_consecutive


# SNIP:product_except_self
def product_except_self(nums):
    """左右前缀积。除自身以外的乘积不使用除法。"""
    n = len(nums)
    ans = [1] * n
    left = 1
    for i in range(n):
        ans[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= right
        right *= nums[i]
    return ans
# END:product_except_self


# SNIP:median_sorted
def median_sorted(left, right):
    """在较短数组上二分切割。切割左边的最大值不大于右边的最小值。"""
    if len(left) > len(right):
        left, right = right, left
    m, n = len(left), len(right)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        left_max = left[i - 1] if i else float("-inf")
        left_min = left[i] if i < m else float("inf")
        right_max = right[j - 1] if j else float("-inf")
        right_min = right[j] if j < n else float("inf")
        if left_max <= right_min and right_max <= left_min:
            if (m + n) % 2:
                return float(max(left_max, right_max))
            return (max(left_max, right_max) + min(left_min, right_min)) / 2
        if left_max > right_min:
            hi = i - 1
        else:
            lo = i + 1
    return 0.0
# END:median_sorted


# SNIP:subarray_sum
def subarray_sum(nums, k):
    """前缀和。看到 sum 时，之前出现过 sum-k 的次数就是以当前位置结尾的答案。"""
    seen = {0: 1}
    total = ans = 0
    for value in nums:
        total += value
        ans += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return ans
# END:subarray_sum


# SNIP:top_k_frequent
def top_k_frequent(nums, k):
    """桶排序。频率最高是 n，桶下标就是频率。"""
    freq = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, count in freq.items():
        buckets[count].append(value)
    ans = []
    for count in range(len(buckets) - 1, 0, -1):
        for value in buckets[count]:
            ans.append(value)
            if len(ans) == k:
                return ans
    return ans
# END:top_k_frequent


# SNIP:min_meeting_rooms
def min_meeting_rooms(intervals):
    """开始时间加一间，结束时间还一间。扫描时结束优先。"""
    starts = sorted(item[0] for item in intervals)
    ends = sorted(item[1] for item in intervals)
    used = ans = j = 0
    for start in starts:
        if start < ends[j]:
            used += 1
            ans = max(ans, used)
        else:
            j += 1
    return ans
# END:min_meeting_rooms


# SNIP:num_provinces
def num_provinces(is_connected):
    """并查集。城市连通块个数就是省份数。"""
    n = len(is_connected)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                parent[find(i)] = find(j)
    return len({find(i) for i in range(n)})
# END:num_provinces


# SNIP:search_rotated
def search_rotated(nums, target):
    """旋转数组二分。至少有一半是有序的，先判断目标在不在有序的那一半。"""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        elif nums[mid] < target <= nums[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# END:search_rotated


# SNIP:first_missing_positive
def first_missing_positive(nums):
    """把 x 放到下标 x-1。再扫描第一个不在自己位置上的数。"""
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i, value in enumerate(nums):
        if value != i + 1:
            return i + 1
    return n + 1
# END:first_missing_positive


# SNIP:max_profit
def max_profit(prices):
    """一次交易。记录历史最低买入价，用当天价格更新利润。"""
    best = 0
    low = float("inf")
    for price in prices:
        low = min(low, price)
        best = max(best, price - low)
    return best
# END:max_profit


# SNIP:jump_game
def jump_game(nums):
    """维护当前能到达的最远下标。走不到的位置出现在最远距离之前就失败。"""
    far = 0
    for i, step in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + step)
    return True
# END:jump_game


# SNIP:decode_string
def decode_string(s):
    """栈里保存进入括号前的字符串和倍数。数字可能不止一位。"""
    stack = []
    cur = []
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))
            cur, num = [], 0
        elif ch == "]":
            prev, times = stack.pop()
            cur = prev + cur * times
        else:
            cur.append(ch)
    return "".join(cur)
# END:decode_string


# SNIP:group_anagrams
def group_anagrams(words):
    """排序后的字符串当键。返回分组，组内顺序不要求。"""
    groups = defaultdict(list)
    for word in words:
        groups["".join(sorted(word))].append(word)
    return list(groups.values())
# END:group_anagrams


# SNIP:valid_parentheses
def valid_parentheses(s):
    """栈。右括号必须匹配栈顶。"""
    pair = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pair[ch]:
            return False
    return not stack
# END:valid_parentheses


# SNIP:longest_palindrome
def longest_palindrome(s):
    """中心扩展。奇数长度和偶数长度的中心都要试。"""
    if not s:
        return ""
    start = end = 0

    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1

    for i in range(len(s)):
        for left, right in (expand(i, i), expand(i, i + 1)):
            if right - left > end - start:
                start, end = left, right
    return s[start : end + 1]
# END:longest_palindrome


# SNIP:container_water
def container_water(height):
    """两边较矮的一边决定面积。矮的一侧内移才可能变大。"""
    lo, hi = 0, len(height) - 1
    best = 0
    while lo < hi:
        best = max(best, min(height[lo], height[hi]) * (hi - lo))
        if height[lo] <= height[hi]:
            lo += 1
        else:
            hi -= 1
    return best
# END:container_water


# SNIP:unique_paths
def unique_paths(m, n):
    """只能向右或向下。滚动数组保存上一行的路径数。"""
    dp = [1] * n
    for _ in range(1, m):
        for col in range(1, n):
            dp[col] += dp[col - 1]
    return dp[-1]
# END:unique_paths


# SNIP:lcs_length
def lcs_length(text1, text2):
    """最长公共子序列。字符相等则对角线加一，否则取上方或左方。"""
    dp = [0] * (len(text2) + 1)
    for ch1 in text1:
        prev = 0
        for j, ch2 in enumerate(text2, 1):
            saved = dp[j]
            if ch1 == ch2:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = saved
    return dp[-1]
# END:lcs_length


# SNIP:subsets
def subsets(nums):
    """每个元素选或不选。回溯树的每个节点都是一个子集。"""
    ans = []
    path = []

    def dfs(start):
        ans.append(path.copy())
        for i in range(start, len(nums)):
            path.append(nums[i])
            dfs(i + 1)
            path.pop()

    dfs(0)
    return ans
# END:subsets


# SNIP:gas_station
def gas_station(gas, cost):
    """总油量不够就无解。从第一个把油箱跑成负数的下一站重新开始。"""
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i, (got, need) in enumerate(zip(gas, cost)):
        tank += got - need
        if tank < 0:
            start = i + 1
            tank = 0
    return start
# END:gas_station


# SNIP:task_scheduler
def task_scheduler(tasks, n):
    """冷却由最高频率决定。公式和任务总数取最大。"""
    freq = Counter(tasks)
    hottest = max(freq.values())
    same = sum(1 for value in freq.values() if value == hottest)
    return max(len(tasks), (hottest - 1) * (n + 1) + same)
# END:task_scheduler


# SNIP:can_partition
def can_partition(nums):
    """总和为奇数则不可能。否则做容量为总和一半的 0-1 背包。"""
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    for value in nums:
        for cap in range(target, value - 1, -1):
            dp[cap] = dp[cap] or dp[cap - value]
    return dp[target]
# END:can_partition


# SNIP:remove_k_digits
def remove_k_digits(num, k):
    """单调递增栈。当前数字更小就删掉栈顶更大的高位。"""
    stack = []
    for ch in num:
        while k and stack and stack[-1] > ch:
            stack.pop()
            k -= 1
        stack.append(ch)
    if k:
        stack = stack[:-k]
    out = "".join(stack).lstrip("0")
    return out or "0"
# END:remove_k_digits


def _run_tests():
    assert _dump(reverse_list(_list([1, 2, 3, 4]))) == [4, 3, 2, 1]
    cycle = _list([1, 2, 3])
    cycle.next.next.next = cycle.next
    assert has_cycle(cycle) is True
    assert has_cycle(_list([1, 2])) is False
    assert _dump(merge_two_lists(_list([1, 3]), _list([2, 4]))) == [1, 2, 3, 4]
    assert _dump(add_two_numbers(_list([2, 4, 3]), _list([5, 6, 4]))) == [7, 0, 8]
    assert _dump(reverse_k_group(_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert _dump(reverse_k_group(_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    merged = merge_k_lists([_list([1, 4]), _list([1, 3]), _list([2, 6])])
    assert _dump(merged) == [1, 1, 2, 3, 4, 6]
    assert level_order(_tree([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
    root = _tree([3, 5, 1, 6, 2, 0, 8])
    p, q = root.left, root.right
    assert lowest_common_ancestor(root, p, q) is root
    assert lowest_common_ancestor(root, root.left, root.left.right) is root.left
    assert diameter(_tree([1, 2, 3, 4, 5])) == 3
    assert is_valid_bst(_tree([2, 1, 3])) is True
    assert is_valid_bst(_tree([5, 1, 4, None, None, 3, 6])) is False
    assert max_path_sum(_tree([-10, 9, 20, None, None, 15, 7])) == 42
    matrix = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    assert search_matrix(matrix, 5) is True
    assert search_matrix(matrix, 10) is False
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert sort_colors([2, 0, 2, 1, 1, 0]) == [0, 0, 1, 1, 2, 2]
    assert sort_four([3, 1, 0, 2, 1, 3, 0]) == [0, 0, 1, 1, 2, 3, 3]
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert wiggle_length([1, 17, 5, 10, 13, 15, 10, 5, 16, 8]) == 7
    assert wiggle_length([1, 2, 3, 4]) == 2
    assert word_break("leetcode", ["leet", "code"]) is True
    assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
    square = [["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]]
    assert maximal_square(square) == 4
    assert min_remove_valid("lee(t(c)o)de)") == "lee(t(c)o)de"
    assert min_remove_valid("))((") == ""
    assert quick_sort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10]
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert median_sorted([1, 3], [2]) == 2
    assert median_sorted([1, 2], [3, 4]) == 2.5
    assert subarray_sum([1, 1, 1], 2) == 2
    assert subarray_sum([1, 2, 3], 3) == 2
    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
    assert num_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert first_missing_positive([3, 4, -1, 1]) == 2
    assert first_missing_positive([1, 2, 0]) == 3
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5
    assert jump_game([2, 3, 1, 1, 4]) is True
    assert jump_game([3, 2, 1, 0, 4]) is False
    assert decode_string("3[a2[c]]") == "accaccacc"
    assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
    groups = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert sorted(sorted(group) for group in groups) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert valid_parentheses("()[]{}") is True
    assert valid_parentheses("(]") is False
    assert longest_palindrome("babad") in {"bab", "aba"}
    assert container_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert unique_paths(3, 7) == 28
    assert lcs_length("abcde", "ace") == 3
    subset = subsets([1, 2])
    assert sorted(subset) == [[], [1], [1, 2], [2]]
    assert gas_station([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert task_scheduler(["A", "A", "A", "B", "B", "B"], 2) == 8
    assert can_partition([1, 5, 11, 5]) is True
    assert can_partition([1, 2, 3, 5]) is False
    assert remove_k_digits("1432219", 3) == "1219"
    assert remove_k_digits("10200", 1) == "200"
    print("more python ok")


if __name__ == "__main__":
    _run_tests()
