package algo

import "sort"

type ListNode struct {
	Val  int
	Next *ListNode
}

type TreeNode struct {
	Val         int
	Left, Right *TreeNode
}

// SNIP:reverse_list
func ReverseList(head *ListNode) *ListNode {
	var prev *ListNode
	cur := head
	for cur != nil {
		nxt := cur.Next
		cur.Next = prev
		prev = cur
		cur = nxt
	}
	return prev
}

// END:reverse_list

// SNIP:has_cycle
func HasCycle(head *ListNode) bool {
	slow, fast := head, head
	for fast != nil && fast.Next != nil {
		slow = slow.Next
		fast = fast.Next.Next
		if slow == fast {
			return true
		}
	}
	return false
}

// END:has_cycle

// SNIP:merge_two_lists
func MergeTwoLists(left, right *ListNode) *ListNode {
	dummy := &ListNode{}
	cur := dummy
	for left != nil && right != nil {
		if left.Val <= right.Val {
			cur.Next = left
			left = left.Next
		} else {
			cur.Next = right
			right = right.Next
		}
		cur = cur.Next
	}
	if left != nil {
		cur.Next = left
	} else {
		cur.Next = right
	}
	return dummy.Next
}

// END:merge_two_lists

// SNIP:add_two_numbers
func AddTwoNumbers(left, right *ListNode) *ListNode {
	dummy := &ListNode{}
	cur := dummy
	carry := 0
	for left != nil || right != nil || carry != 0 {
		total := carry
		if left != nil {
			total += left.Val
			left = left.Next
		}
		if right != nil {
			total += right.Val
			right = right.Next
		}
		carry = total / 10
		cur.Next = &ListNode{Val: total % 10}
		cur = cur.Next
	}
	return dummy.Next
}

// END:add_two_numbers

// SNIP:reverse_k_group
func ReverseKGroup(head *ListNode, k int) *ListNode {
	dummy := &ListNode{Next: head}
	prev := dummy
	for {
		end := prev
		for i := 0; i < k; i++ {
			end = end.Next
			if end == nil {
				return dummy.Next
			}
		}
		start := prev.Next
		nxt := end.Next
		prev.Next = reverseRange(start, nxt)
		prev = start
	}
}

func reverseRange(start, stop *ListNode) *ListNode {
	prev := stop
	cur := start
	for cur != stop {
		nxt := cur.Next
		cur.Next = prev
		prev = cur
		cur = nxt
	}
	return prev
}

// END:reverse_k_group

// SNIP:merge_k_lists
func MergeKLists(lists []*ListNode) *ListNode {
	var nodes []*ListNode
	for _, node := range lists {
		if node != nil {
			nodes = append(nodes, node)
		}
	}
	dummy := &ListNode{}
	cur := dummy
	for len(nodes) > 0 {
		best := 0
		for i := 1; i < len(nodes); i++ {
			if nodes[i].Val < nodes[best].Val {
				best = i
			}
		}
		node := nodes[best]
		cur.Next = node
		cur = cur.Next
		if node.Next != nil {
			nodes[best] = node.Next
		} else {
			nodes = append(nodes[:best], nodes[best+1:]...)
		}
	}
	return dummy.Next
}

// END:merge_k_lists

// SNIP:level_order
func LevelOrder(root *TreeNode) [][]int {
	if root == nil {
		return nil
	}
	queue := []*TreeNode{root}
	var ans [][]int
	for len(queue) > 0 {
		size := len(queue)
		level := make([]int, 0, size)
		for i := 0; i < size; i++ {
			node := queue[0]
			queue = queue[1:]
			level = append(level, node.Val)
			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		ans = append(ans, level)
	}
	return ans
}

// END:level_order

// SNIP:lowest_common_ancestor
func LowestCommonAncestor(root, p, q *TreeNode) *TreeNode {
	if root == nil || root == p || root == q {
		return root
	}
	left := LowestCommonAncestor(root.Left, p, q)
	right := LowestCommonAncestor(root.Right, p, q)
	if left != nil && right != nil {
		return root
	}
	if left != nil {
		return left
	}
	return right
}

// END:lowest_common_ancestor

// SNIP:diameter
func Diameter(root *TreeNode) int {
	best := 0
	var height func(*TreeNode) int
	height = func(node *TreeNode) int {
		if node == nil {
			return 0
		}
		left := height(node.Left)
		right := height(node.Right)
		if left+right > best {
			best = left + right
		}
		if left > right {
			return left + 1
		}
		return right + 1
	}
	height(root)
	return best
}

// END:diameter

// SNIP:is_valid_bst
func IsValidBST(root *TreeNode) bool {
	var ok func(*TreeNode, int, int, bool, bool) bool
	ok = func(node *TreeNode, low, high int, hasLow, hasHigh bool) bool {
		if node == nil {
			return true
		}
		if hasLow && node.Val <= low || hasHigh && node.Val >= high {
			return false
		}
		return ok(node.Left, low, node.Val, hasLow, true) && ok(node.Right, node.Val, high, true, hasHigh)
	}
	return ok(root, 0, 0, false, false)
}

// END:is_valid_bst

// SNIP:max_path_sum
func MaxPathSum(root *TreeNode) int {
	best := root.Val
	var gain func(*TreeNode) int
	gain = func(node *TreeNode) int {
		if node == nil {
			return 0
		}
		left := gain(node.Left)
		if left < 0 {
			left = 0
		}
		right := gain(node.Right)
		if right < 0 {
			right = 0
		}
		if node.Val+left+right > best {
			best = node.Val + left + right
		}
		extra := left
		if right > extra {
			extra = right
		}
		return node.Val + extra
	}
	gain(root)
	return best
}

// END:max_path_sum

// SNIP:search_matrix
func SearchMatrix(matrix [][]int, target int) bool {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return false
	}
	row, col := 0, len(matrix[0])-1
	for row < len(matrix) && col >= 0 {
		value := matrix[row][col]
		if value == target {
			return true
		}
		if value > target {
			col--
		} else {
			row++
		}
	}
	return false
}

// END:search_matrix

// SNIP:kth_largest
func KthLargest(nums []int, k int) int {
	heap := append([]int(nil), nums[:k]...)
	for i := len(heap)/2 - 1; i >= 0; i-- {
		down(heap, i)
	}
	for _, value := range nums[k:] {
		if value > heap[0] {
			heap[0] = value
			down(heap, 0)
		}
	}
	return heap[0]
}

func down(heap []int, i int) {
	for {
		smallest := i
		left, right := i*2+1, i*2+2
		if left < len(heap) && heap[left] < heap[smallest] {
			smallest = left
		}
		if right < len(heap) && heap[right] < heap[smallest] {
			smallest = right
		}
		if smallest == i {
			return
		}
		heap[i], heap[smallest] = heap[smallest], heap[i]
		i = smallest
	}
}

// END:kth_largest

// SNIP:sort_colors
func SortColors(nums []int) {
	p0, i, p2 := 0, 0, len(nums)-1
	for i <= p2 {
		if nums[i] == 0 {
			nums[i], nums[p0] = nums[p0], nums[i]
			p0++
			i++
		} else if nums[i] == 2 {
			nums[i], nums[p2] = nums[p2], nums[i]
			p2--
		} else {
			i++
		}
	}
}

// END:sort_colors

// SNIP:sort_four
func SortFour(nums []int) {
	count := [4]int{}
	for _, value := range nums {
		count[value]++
	}
	index := 0
	for value, times := range count {
		for t := 0; t < times; t++ {
			nums[index] = value
			index++
		}
	}
}

// END:sort_four

// SNIP:lis_length
func LisLength(nums []int) int {
	tails := make([]int, 0, len(nums))
	for _, value := range nums {
		lo, hi := 0, len(tails)
		for lo < hi {
			mid := (lo + hi) / 2
			if tails[mid] < value {
				lo = mid + 1
			} else {
				hi = mid
			}
		}
		if lo == len(tails) {
			tails = append(tails, value)
		} else {
			tails[lo] = value
		}
	}
	return len(tails)
}

// END:lis_length

// SNIP:wiggle_length
func WiggleLength(nums []int) int {
	if len(nums) == 0 {
		return 0
	}
	up, down := 1, 1
	for i := 1; i < len(nums); i++ {
		if nums[i] > nums[i-1] {
			up = down + 1
		} else if nums[i] < nums[i-1] {
			down = up + 1
		}
	}
	if up > down {
		return up
	}
	return down
}

// END:wiggle_length

// SNIP:word_break
func WordBreak(s string, wordDict []string) bool {
	words := map[string]bool{}
	for _, word := range wordDict {
		words[word] = true
	}
	dp := make([]bool, len(s)+1)
	dp[0] = true
	for end := 1; end <= len(s); end++ {
		for start := 0; start < end; start++ {
			if dp[start] && words[s[start:end]] {
				dp[end] = true
				break
			}
		}
	}
	return dp[len(s)]
}

// END:word_break

// SNIP:maximal_square
func MaximalSquare(matrix [][]byte) int {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return 0
	}
	dp := make([]int, len(matrix[0])+1)
	best := 0
	for _, row := range matrix {
		prev := 0
		for c := 1; c <= len(row); c++ {
			saved := dp[c]
			if row[c-1] == '1' {
				dp[c] = min(dp[c], min(dp[c-1], prev)) + 1
				if dp[c] > best {
					best = dp[c]
				}
			} else {
				dp[c] = 0
			}
			prev = saved
		}
	}
	return best * best
}

// END:maximal_square

// SNIP:min_remove_valid
func MinRemoveValid(s string) string {
	stack := []int{}
	remove := map[int]bool{}
	for i := 0; i < len(s); i++ {
		switch s[i] {
		case '(':
			stack = append(stack, i)
		case ')':
			if len(stack) > 0 {
				stack = stack[:len(stack)-1]
			} else {
				remove[i] = true
			}
		}
	}
	for _, i := range stack {
		remove[i] = true
	}
	out := make([]byte, 0, len(s))
	for i := 0; i < len(s); i++ {
		if !remove[i] {
			out = append(out, s[i])
		}
	}
	return string(out)
}

// END:min_remove_valid

// SNIP:quick_sort
func QuickSort(nums []int) []int {
	var sort func(int, int)
	sort = func(lo, hi int) {
		if lo >= hi {
			return
		}
		pivot := nums[hi]
		store := lo
		for i := lo; i < hi; i++ {
			if nums[i] < pivot {
				nums[store], nums[i] = nums[i], nums[store]
				store++
			}
		}
		nums[store], nums[hi] = nums[hi], nums[store]
		sort(lo, store-1)
		sort(store+1, hi)
	}
	if len(nums) > 0 {
		sort(0, len(nums)-1)
	}
	return nums
}

// END:quick_sort

// SNIP:daily_temperatures
func DailyTemperatures(temps []int) []int {
	ans := make([]int, len(temps))
	stack := []int{}
	for i, value := range temps {
		for len(stack) > 0 && temps[stack[len(stack)-1]] < value {
			j := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			ans[j] = i - j
		}
		stack = append(stack, i)
	}
	return ans
}

// END:daily_temperatures

// SNIP:longest_consecutive
func LongestConsecutive(nums []int) int {
	pool := map[int]bool{}
	for _, value := range nums {
		pool[value] = true
	}
	best := 0
	for value := range pool {
		if pool[value-1] {
			continue
		}
		length := 1
		for pool[value+length] {
			length++
		}
		if length > best {
			best = length
		}
	}
	return best
}

// END:longest_consecutive

// SNIP:product_except_self
func ProductExceptSelf(nums []int) []int {
	ans := make([]int, len(nums))
	left := 1
	for i, value := range nums {
		ans[i] = left
		left *= value
	}
	right := 1
	for i := len(nums) - 1; i >= 0; i-- {
		ans[i] *= right
		right *= nums[i]
	}
	return ans
}

// END:product_except_self

// SNIP:median_sorted
func MedianSorted(left, right []int) float64 {
	if len(left) > len(right) {
		return MedianSorted(right, left)
	}
	m, n := len(left), len(right)
	half := (m + n + 1) / 2
	lo, hi := 0, m
	for lo <= hi {
		i := (lo + hi) / 2
		j := half - i
		leftMax, leftMin := -1<<31, 1<<31-1
		rightMax, rightMin := -1<<31, 1<<31-1
		if i > 0 {
			leftMax = left[i-1]
		}
		if i < m {
			leftMin = left[i]
		}
		if j > 0 {
			rightMax = right[j-1]
		}
		if j < n {
			rightMin = right[j]
		}
		if leftMax <= rightMin && rightMax <= leftMin {
			if (m+n)%2 == 1 {
				if leftMax > rightMax {
					return float64(leftMax)
				}
				return float64(rightMax)
			}
			high := leftMax
			if rightMax > high {
				high = rightMax
			}
			low := leftMin
			if rightMin < low {
				low = rightMin
			}
			return float64(high+low) / 2
		}
		if leftMax > rightMin {
			hi = i - 1
		} else {
			lo = i + 1
		}
	}
	return 0
}

// END:median_sorted

// SNIP:subarray_sum
func SubarraySum(nums []int, k int) int {
	seen := map[int]int{0: 1}
	total, ans := 0, 0
	for _, value := range nums {
		total += value
		ans += seen[total-k]
		seen[total]++
	}
	return ans
}

// END:subarray_sum

// SNIP:top_k_frequent
func TopKFrequent(nums []int, k int) []int {
	freq := map[int]int{}
	for _, value := range nums {
		freq[value]++
	}
	buckets := make([][]int, len(nums)+1)
	for value, count := range freq {
		buckets[count] = append(buckets[count], value)
	}
	ans := make([]int, 0, k)
	for count := len(buckets) - 1; count > 0 && len(ans) < k; count-- {
		for _, value := range buckets[count] {
			ans = append(ans, value)
			if len(ans) == k {
				return ans
			}
		}
	}
	return ans
}

// END:top_k_frequent

// SNIP:min_meeting_rooms
func MinMeetingRooms(intervals [][]int) int {
	starts := make([]int, len(intervals))
	ends := make([]int, len(intervals))
	for i, item := range intervals {
		starts[i] = item[0]
		ends[i] = item[1]
	}
	sort.Ints(starts)
	sort.Ints(ends)
	used, ans, j := 0, 0, 0
	for _, start := range starts {
		if start < ends[j] {
			used++
			if used > ans {
				ans = used
			}
		} else {
			j++
		}
	}
	return ans
}

// END:min_meeting_rooms

// SNIP:num_provinces
func NumProvinces(isConnected [][]int) int {
	n := len(isConnected)
	parent := make([]int, n)
	for i := range parent {
		parent[i] = i
	}
	var find func(int) int
	find = func(x int) int {
		for parent[x] != x {
			parent[x] = parent[parent[x]]
			x = parent[x]
		}
		return x
	}
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if isConnected[i][j] == 1 {
				parent[find(i)] = find(j)
			}
		}
	}
	roots := map[int]bool{}
	for i := 0; i < n; i++ {
		roots[find(i)] = true
	}
	return len(roots)
}

// END:num_provinces

// SNIP:search_rotated
func SearchRotated(nums []int, target int) int {
	lo, hi := 0, len(nums)-1
	for lo <= hi {
		mid := (lo + hi) / 2
		if nums[mid] == target {
			return mid
		}
		if nums[lo] <= nums[mid] {
			if nums[lo] <= target && target < nums[mid] {
				hi = mid - 1
			} else {
				lo = mid + 1
			}
		} else if nums[mid] < target && target <= nums[hi] {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return -1
}

// END:search_rotated

// SNIP:first_missing_positive
func FirstMissingPositive(nums []int) int {
	n := len(nums)
	for i := 0; i < n; i++ {
		for nums[i] >= 1 && nums[i] <= n && nums[nums[i]-1] != nums[i] {
			j := nums[i] - 1
			nums[i], nums[j] = nums[j], nums[i]
		}
	}
	for i, value := range nums {
		if value != i+1 {
			return i + 1
		}
	}
	return n + 1
}

// END:first_missing_positive

// SNIP:max_profit
func MaxProfit(prices []int) int {
	best := 0
	low := int(^uint(0) >> 1)
	for _, price := range prices {
		if price < low {
			low = price
		}
		if price-low > best {
			best = price - low
		}
	}
	return best
}

// END:max_profit

// SNIP:jump_game
func JumpGame(nums []int) bool {
	far := 0
	for i, step := range nums {
		if i > far {
			return false
		}
		if i+step > far {
			far = i + step
		}
	}
	return true
}

// END:jump_game

// SNIP:decode_string
func DecodeString(s string) string {
	type frame struct {
		text string
		num  int
	}
	stack := []frame{}
	cur := ""
	num := 0
	for i := 0; i < len(s); i++ {
		ch := s[i]
		switch {
		case ch >= '0' && ch <= '9':
			num = num*10 + int(ch-'0')
		case ch == '[':
			stack = append(stack, frame{cur, num})
			cur, num = "", 0
		case ch == ']':
			top := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			cur = top.text + repeat(cur, top.num)
		default:
			cur += string(ch)
		}
	}
	return cur
}

func repeat(s string, n int) string {
	out := ""
	for i := 0; i < n; i++ {
		out += s
	}
	return out
}

// END:decode_string

// SNIP:group_anagrams
func GroupAnagrams(words []string) [][]string {
	groups := map[string][]string{}
	for _, word := range words {
		chars := []byte(word)
		sort.Slice(chars, func(i, j int) bool { return chars[i] < chars[j] })
		key := string(chars)
		groups[key] = append(groups[key], word)
	}
	ans := make([][]string, 0, len(groups))
	for _, group := range groups {
		ans = append(ans, group)
	}
	return ans
}

// END:group_anagrams

// SNIP:valid_parentheses
func ValidParentheses(s string) bool {
	pair := map[byte]byte{')': '(', ']': '[', '}': '{'}
	stack := []byte{}
	for i := 0; i < len(s); i++ {
		ch := s[i]
		if ch == '(' || ch == '[' || ch == '{' {
			stack = append(stack, ch)
			continue
		}
		if len(stack) == 0 || stack[len(stack)-1] != pair[ch] {
			return false
		}
		stack = stack[:len(stack)-1]
	}
	return len(stack) == 0
}

// END:valid_parentheses

// SNIP:longest_palindrome
func LongestPalindrome(s string) string {
	if s == "" {
		return ""
	}
	start, end := 0, 0
	expand := func(left, right int) (int, int) {
		for left >= 0 && right < len(s) && s[left] == s[right] {
			left--
			right++
		}
		return left + 1, right - 1
	}
	for i := 0; i < len(s); i++ {
		for _, pair := range [][2]int{{i, i}, {i, i + 1}} {
			left, right := expand(pair[0], pair[1])
			if right-left > end-start {
				start, end = left, right
			}
		}
	}
	return s[start : end+1]
}

// END:longest_palindrome

// SNIP:container_water
func ContainerWater(height []int) int {
	lo, hi := 0, len(height)-1
	best := 0
	for lo < hi {
		h := height[lo]
		if height[hi] < h {
			h = height[hi]
		}
		area := h * (hi - lo)
		if area > best {
			best = area
		}
		if height[lo] <= height[hi] {
			lo++
		} else {
			hi--
		}
	}
	return best
}

// END:container_water

// SNIP:unique_paths
func UniquePaths(m, n int) int {
	dp := make([]int, n)
	for i := range dp {
		dp[i] = 1
	}
	for row := 1; row < m; row++ {
		for col := 1; col < n; col++ {
			dp[col] += dp[col-1]
		}
	}
	return dp[n-1]
}

// END:unique_paths

// SNIP:lcs_length
func LCSLength(text1, text2 string) int {
	dp := make([]int, len(text2)+1)
	for i := 0; i < len(text1); i++ {
		prev := 0
		for j := 1; j <= len(text2); j++ {
			saved := dp[j]
			if text1[i] == text2[j-1] {
				dp[j] = prev + 1
			} else if dp[j-1] > dp[j] {
				dp[j] = dp[j-1]
			}
			prev = saved
		}
	}
	return dp[len(text2)]
}

// END:lcs_length

// SNIP:subsets
func Subsets(nums []int) [][]int {
	ans := [][]int{}
	path := []int{}
	var dfs func(int)
	dfs = func(start int) {
		copyPath := append([]int(nil), path...)
		ans = append(ans, copyPath)
		for i := start; i < len(nums); i++ {
			path = append(path, nums[i])
			dfs(i + 1)
			path = path[:len(path)-1]
		}
	}
	dfs(0)
	return ans
}

// END:subsets

// SNIP:gas_station
func GasStation(gas, cost []int) int {
	total, tank, start := 0, 0, 0
	for i := range gas {
		gain := gas[i] - cost[i]
		total += gain
		tank += gain
		if tank < 0 {
			start = i + 1
			tank = 0
		}
	}
	if total < 0 {
		return -1
	}
	return start
}

// END:gas_station

// SNIP:task_scheduler
func TaskScheduler(tasks []byte, n int) int {
	freq := [26]int{}
	for _, task := range tasks {
		freq[task-'A']++
	}
	hottest := 0
	for _, value := range freq {
		if value > hottest {
			hottest = value
		}
	}
	same := 0
	for _, value := range freq {
		if value == hottest {
			same++
		}
	}
	need := (hottest-1)*(n+1) + same
	if len(tasks) > need {
		return len(tasks)
	}
	return need
}

// END:task_scheduler

// SNIP:can_partition
func CanPartition(nums []int) bool {
	total := 0
	for _, value := range nums {
		total += value
	}
	if total%2 == 1 {
		return false
	}
	target := total / 2
	dp := make([]bool, target+1)
	dp[0] = true
	for _, value := range nums {
		for cap := target; cap >= value; cap-- {
			dp[cap] = dp[cap] || dp[cap-value]
		}
	}
	return dp[target]
}

// END:can_partition

// SNIP:remove_k_digits
func RemoveKDigits(num string, k int) string {
	stack := make([]byte, 0, len(num))
	for i := 0; i < len(num); i++ {
		ch := num[i]
		for k > 0 && len(stack) > 0 && stack[len(stack)-1] > ch {
			stack = stack[:len(stack)-1]
			k--
		}
		stack = append(stack, ch)
	}
	stack = stack[:len(stack)-k]
	start := 0
	for start < len(stack) && stack[start] == '0' {
		start++
	}
	if start == len(stack) {
		return "0"
	}
	return string(stack[start:])
}

// END:remove_k_digits
