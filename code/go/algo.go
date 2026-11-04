package algo

import (
	"container/heap"
	"math"
	"sort"
)

// SNIP:two_sum
func TwoSum(nums []int, target int) []int {
	seen := make(map[int]int, len(nums))
	for i, x := range nums {
		if j, ok := seen[target-x]; ok {
			return []int{j, i}
		}
		seen[x] = i
	}
	return nil
}

// END:two_sum

// SNIP:longest_unique
func LongestUnique(s string) int {
	last := map[byte]int{}
	left, best := 0, 0
	for i := 0; i < len(s); i++ {
		ch := s[i]
		if pos, ok := last[ch]; ok && pos >= left {
			left = pos + 1
		}
		last[ch] = i
		if i-left+1 > best {
			best = i - left + 1
		}
	}
	return best
}

// END:longest_unique

// SNIP:three_sum
func ThreeSum(nums []int) [][]int {
	sort.Ints(nums)
	ans := [][]int{}
	for i := 0; i < len(nums); i++ {
		if nums[i] > 0 {
			break
		}
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}
		left, right := i+1, len(nums)-1
		for left < right {
			total := nums[i] + nums[left] + nums[right]
			if total == 0 {
				ans = append(ans, []int{nums[i], nums[left], nums[right]})
				left++
				right--
				for left < right && nums[left] == nums[left-1] {
					left++
				}
				for left < right && nums[right] == nums[right+1] {
					right--
				}
			} else if total < 0 {
				left++
			} else {
				right--
			}
		}
	}
	return ans
}

// END:three_sum

// SNIP:trap
func Trap(height []int) int {
	left, right := 0, len(height)-1
	leftMax, rightMax, water := 0, 0, 0
	for left < right {
		if height[left] <= height[right] {
			if height[left] > leftMax {
				leftMax = height[left]
			}
			water += leftMax - height[left]
			left++
		} else {
			if height[right] > rightMax {
				rightMax = height[right]
			}
			water += rightMax - height[right]
			right--
		}
	}
	return water
}

// END:trap

// SNIP:merge_intervals
func MergeIntervals(intervals [][]int) [][]int {
	if len(intervals) == 0 {
		return nil
	}
	sort.Slice(intervals, func(i, j int) bool { return intervals[i][0] < intervals[j][0] })
	merged := [][]int{{intervals[0][0], intervals[0][1]}}
	for _, it := range intervals[1:] {
		last := merged[len(merged)-1]
		if it[0] <= last[1] {
			if it[1] > last[1] {
				last[1] = it[1]
			}
		} else {
			merged = append(merged, []int{it[0], it[1]})
		}
	}
	return merged
}

// END:merge_intervals

// SNIP:lru
type lruNode struct {
	key, val   int
	prev, next *lruNode
}

type LRUCache struct {
	cap        int
	m          map[int]*lruNode
	head, tail *lruNode
}

func NewLRU(capacity int) *LRUCache {
	head, tail := &lruNode{}, &lruNode{}
	head.next = tail
	tail.prev = head
	return &LRUCache{cap: capacity, m: map[int]*lruNode{}, head: head, tail: tail}
}

func (c *LRUCache) remove(node *lruNode) {
	node.prev.next = node.next
	node.next.prev = node.prev
}

func (c *LRUCache) insertFront(node *lruNode) {
	node.next = c.head.next
	node.prev = c.head
	c.head.next.prev = node
	c.head.next = node
}

func (c *LRUCache) Get(key int) int {
	node, ok := c.m[key]
	if !ok {
		return -1
	}
	c.remove(node)
	c.insertFront(node)
	return node.val
}

func (c *LRUCache) Put(key, value int) {
	if node, ok := c.m[key]; ok {
		node.val = value
		c.remove(node)
		c.insertFront(node)
		return
	}
	node := &lruNode{key: key, val: value}
	c.m[key] = node
	c.insertFront(node)
	if len(c.m) > c.cap {
		old := c.tail.prev
		c.remove(old)
		delete(c.m, old.key)
	}
}

// END:lru

// SNIP:course_schedule
func CanFinish(numCourses int, prerequisites [][]int) bool {
	graph := make([][]int, numCourses)
	indegree := make([]int, numCourses)
	for _, edge := range prerequisites {
		graph[edge[1]] = append(graph[edge[1]], edge[0])
		indegree[edge[0]]++
	}
	queue := make([]int, 0)
	for i, d := range indegree {
		if d == 0 {
			queue = append(queue, i)
		}
	}
	taken := 0
	for len(queue) > 0 {
		cur := queue[len(queue)-1]
		queue = queue[:len(queue)-1]
		taken++
		for _, nxt := range graph[cur] {
			indegree[nxt]--
			if indegree[nxt] == 0 {
				queue = append(queue, nxt)
			}
		}
	}
	return taken == numCourses
}

// END:course_schedule

// SNIP:num_islands
func NumIslands(grid [][]byte) int {
	if len(grid) == 0 || len(grid[0]) == 0 {
		return 0
	}
	rows, cols := len(grid), len(grid[0])
	var sink func(int, int)
	sink = func(r, c int) {
		if r < 0 || c < 0 || r >= rows || c >= cols || grid[r][c] != '1' {
			return
		}
		grid[r][c] = '0'
		sink(r+1, c)
		sink(r-1, c)
		sink(r, c+1)
		sink(r, c-1)
	}
	count := 0
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] == '1' {
				count++
				sink(r, c)
			}
		}
	}
	return count
}

// END:num_islands

// SNIP:window_max
func WindowMax(nums []int, k int) []int {
	dq := make([]int, 0)
	ans := make([]int, 0, len(nums)-k+1)
	for i, value := range nums {
		for len(dq) > 0 && dq[0] <= i-k {
			dq = dq[1:]
		}
		for len(dq) > 0 && nums[dq[len(dq)-1]] <= value {
			dq = dq[:len(dq)-1]
		}
		dq = append(dq, i)
		if i >= k-1 {
			ans = append(ans, nums[dq[0]])
		}
	}
	return ans
}

// END:window_max

// SNIP:edit_distance
func EditDistance(word1, word2 string) int {
	m, n := len(word1), len(word2)
	dp := make([]int, n+1)
	for j := 0; j <= n; j++ {
		dp[j] = j
	}
	for i := 1; i <= m; i++ {
		prev := dp[0]
		dp[0] = i
		for j := 1; j <= n; j++ {
			saved := dp[j]
			if word1[i-1] == word2[j-1] {
				dp[j] = prev
			} else {
				dp[j] = 1 + min(prev, min(dp[j], dp[j-1]))
			}
			prev = saved
		}
	}
	return dp[n]
}

// END:edit_distance

// SNIP:coin_change
func CoinChange(coins []int, amount int) int {
	inf := amount + 1
	dp := make([]int, amount+1)
	for i := 1; i <= amount; i++ {
		dp[i] = inf
	}
	for money := 1; money <= amount; money++ {
		for _, coin := range coins {
			if coin <= money && dp[money-coin]+1 < dp[money] {
				dp[money] = dp[money-coin] + 1
			}
		}
	}
	if dp[amount] > amount {
		return -1
	}
	return dp[amount]
}

// END:coin_change

// SNIP:min_window
func MinWindow(s, t string) string {
	if s == "" || t == "" {
		return ""
	}
	need := map[byte]int{}
	for i := 0; i < len(t); i++ {
		need[t[i]]++
	}
	missing := len(t)
	bestLeft, bestRight := 0, len(s)+1
	left := 0
	for right := 0; right < len(s); right++ {
		ch := s[right]
		if need[ch] > 0 {
			missing--
		}
		need[ch]--
		for missing == 0 {
			if right-left < bestRight-bestLeft {
				bestLeft, bestRight = left, right
			}
			leftCh := s[left]
			need[leftCh]++
			if need[leftCh] > 0 {
				missing++
			}
			left++
		}
	}
	if bestRight == len(s)+1 {
		return ""
	}
	return s[bestLeft : bestRight+1]
}

// END:min_window

// SNIP:median_finder
type MedianFinder struct {
	low  maxHeap
	high minHeap
}

func NewMedian() *MedianFinder { return &MedianFinder{} }

func (m *MedianFinder) AddNum(num int) {
	heap.Push(&m.low, num)
	heap.Push(&m.high, heap.Pop(&m.low))
	if m.high.Len() > m.low.Len() {
		heap.Push(&m.low, heap.Pop(&m.high))
	}
}

func (m *MedianFinder) FindMedian() float64 {
	if m.low.Len() > m.high.Len() {
		return float64(m.low[0])
	}
	return float64(m.low[0]+m.high[0]) / 2
}

type minHeap []int

func (h minHeap) Len() int            { return len(h) }
func (h minHeap) Less(i, j int) bool  { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *minHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

type maxHeap []int

func (h maxHeap) Len() int            { return len(h) }
func (h maxHeap) Less(i, j int) bool  { return h[i] > h[j] }
func (h maxHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *maxHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *maxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

// END:median_finder

// SNIP:min_cost
func MinCost(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	dist := make([][]int, rows)
	for i := range dist {
		dist[i] = make([]int, cols)
		for j := range dist[i] {
			dist[i][j] = math.MaxInt32
		}
	}
	dist[0][0] = grid[0][0]
	pq := &costHeap{}
	heap.Init(pq)
	heap.Push(pq, costNode{grid[0][0], 0, 0})
	dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	for pq.Len() > 0 {
		cur := heap.Pop(pq).(costNode)
		if cur.cost != dist[cur.r][cur.c] {
			continue
		}
		if cur.r == rows-1 && cur.c == cols-1 {
			return cur.cost
		}
		for _, d := range dirs {
			nr, nc := cur.r+d[0], cur.c+d[1]
			if nr < 0 || nc < 0 || nr >= rows || nc >= cols {
				continue
			}
			next := cur.cost + grid[nr][nc]
			if next < dist[nr][nc] {
				dist[nr][nc] = next
				heap.Push(pq, costNode{next, nr, nc})
			}
		}
	}
	return -1
}

type costNode struct{ cost, r, c int }
type costHeap []costNode

func (h costHeap) Len() int            { return len(h) }
func (h costHeap) Less(i, j int) bool  { return h[i].cost < h[j].cost }
func (h costHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *costHeap) Push(x interface{}) { *h = append(*h, x.(costNode)) }
func (h *costHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

// END:min_cost

// SNIP:k_nearest
func HaversineM(lat1, lon1, lat2, lon2 float64) float64 {
	const radius = 6371000.0
	phi1 := lat1 * math.Pi / 180
	phi2 := lat2 * math.Pi / 180
	dPhi := (lat2 - lat1) * math.Pi / 180
	dLam := (lon2 - lon1) * math.Pi / 180
	a := math.Sin(dPhi/2)*math.Sin(dPhi/2) + math.Cos(phi1)*math.Cos(phi2)*math.Sin(dLam/2)*math.Sin(dLam/2)
	if a > 1 {
		a = 1
	}
	return 2 * radius * math.Asin(math.Sqrt(a))
}

type nearItem struct {
	dist float64
	id   string
}

func KNearest(ids []string, lats, lons []float64, qlat, qlon float64, k int) []string {
	if k <= 0 || len(ids) == 0 {
		return nil
	}
	h := &nearHeap{}
	for i, id := range ids {
		dist := HaversineM(qlat, qlon, lats[i], lons[i])
		if h.Len() < k {
			heap.Push(h, nearItem{dist, id})
		} else if dist < (*h)[0].dist {
			heap.Pop(h)
			heap.Push(h, nearItem{dist, id})
		}
	}
	found := append([]nearItem(nil), (*h)...)
	sort.Slice(found, func(i, j int) bool {
		if found[i].dist == found[j].dist {
			return found[i].id < found[j].id
		}
		return found[i].dist < found[j].dist
	})
	ans := make([]string, len(found))
	for i, it := range found {
		ans[i] = it.id
	}
	return ans
}

type nearHeap []nearItem

func (h nearHeap) Len() int            { return len(h) }
func (h nearHeap) Less(i, j int) bool  { return h[i].dist > h[j].dist }
func (h nearHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *nearHeap) Push(x interface{}) { *h = append(*h, x.(nearItem)) }
func (h *nearHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

// END:k_nearest

// SNIP:point_in_polygon
func PointInPolygon(x, y float64, polygon [][2]float64) bool {
	inside := false
	j := len(polygon) - 1
	for i := 0; i < len(polygon); i++ {
		xi, yi := polygon[i][0], polygon[i][1]
		xj, yj := polygon[j][0], polygon[j][1]
		if (yi > y) != (yj > y) {
			xCross := (xj-xi)*(y-yi)/(yj-yi) + xi
			if x < xCross {
				inside = !inside
			}
		}
		j = i
	}
	return inside
}

// END:point_in_polygon

// SNIP:geohash_encode
const base32 = "0123456789bcdefghjkmnpqrstuvwxyz"

func GeohashEncode(lat, lon float64, precision int) string {
	latRange := [2]float64{-90, 90}
	lonRange := [2]float64{-180, 180}
	hash := make([]byte, 0, precision)
	bit, value := 0, 0
	even := true
	for len(hash) < precision {
		if even {
			mid := (lonRange[0] + lonRange[1]) / 2
			if lon >= mid {
				value = (value << 1) | 1
				lonRange[0] = mid
			} else {
				value <<= 1
				lonRange[1] = mid
			}
		} else {
			mid := (latRange[0] + latRange[1]) / 2
			if lat >= mid {
				value = (value << 1) | 1
				latRange[0] = mid
			} else {
				value <<= 1
				latRange[1] = mid
			}
		}
		even = !even
		bit++
		if bit == 5 {
			hash = append(hash, base32[value])
			bit, value = 0, 0
		}
	}
	return string(hash)
}

// END:geohash_encode

// SNIP:ship_days
func ShipWithinDays(weights []int, days int) int {
	low, high := 0, 0
	for _, w := range weights {
		if w > low {
			low = w
		}
		high += w
	}
	for low < high {
		mid := (low + high) / 2
		if shipFeasible(weights, days, mid) {
			high = mid
		} else {
			low = mid + 1
		}
	}
	return low
}

func shipFeasible(weights []int, days, cap int) bool {
	used, load := 1, 0
	for _, w := range weights {
		if load+w > cap {
			used++
			load = 0
		}
		load += w
	}
	return used <= days
}

// END:ship_days
