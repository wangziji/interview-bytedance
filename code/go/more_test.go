package algo

import (
	"reflect"
	"sort"
	"testing"
)

func listOf(values ...int) *ListNode {
	dummy := &ListNode{}
	cur := dummy
	for _, value := range values {
		cur.Next = &ListNode{Val: value}
		cur = cur.Next
	}
	return dummy.Next
}

func dumpList(node *ListNode) []int {
	var out []int
	for node != nil {
		out = append(out, node.Val)
		node = node.Next
	}
	return out
}

func treeOf(level []*int) *TreeNode {
	if len(level) == 0 || level[0] == nil {
		return nil
	}
	root := &TreeNode{Val: *level[0]}
	queue := []*TreeNode{root}
	i := 1
	for len(queue) > 0 && i < len(level) {
		node := queue[0]
		queue = queue[1:]
		if i < len(level) && level[i] != nil {
			node.Left = &TreeNode{Val: *level[i]}
			queue = append(queue, node.Left)
		}
		i++
		if i < len(level) && level[i] != nil {
			node.Right = &TreeNode{Val: *level[i]}
			queue = append(queue, node.Right)
		}
		i++
	}
	return root
}

func n(v int) *int { return &v }

func TestMore(t *testing.T) {
	if !reflect.DeepEqual(dumpList(ReverseList(listOf(1, 2, 3, 4))), []int{4, 3, 2, 1}) {
		t.Fatal("reverse")
	}
	cycle := listOf(1, 2, 3)
	cycle.Next.Next.Next = cycle.Next
	if !HasCycle(cycle) || HasCycle(listOf(1, 2)) {
		t.Fatal("cycle")
	}
	if !reflect.DeepEqual(dumpList(MergeTwoLists(listOf(1, 3), listOf(2, 4))), []int{1, 2, 3, 4}) {
		t.Fatal("merge2")
	}
	if !reflect.DeepEqual(dumpList(AddTwoNumbers(listOf(2, 4, 3), listOf(5, 6, 4))), []int{7, 0, 8}) {
		t.Fatal("add")
	}
	if !reflect.DeepEqual(dumpList(ReverseKGroup(listOf(1, 2, 3, 4, 5), 2)), []int{2, 1, 4, 3, 5}) {
		t.Fatal("k2")
	}
	if !reflect.DeepEqual(dumpList(ReverseKGroup(listOf(1, 2, 3, 4, 5), 3)), []int{3, 2, 1, 4, 5}) {
		t.Fatal("k3")
	}
	merged := MergeKLists([]*ListNode{listOf(1, 4), listOf(1, 3), listOf(2, 6)})
	if !reflect.DeepEqual(dumpList(merged), []int{1, 1, 2, 3, 4, 6}) {
		t.Fatal("mergek", dumpList(merged))
	}
	if !reflect.DeepEqual(LevelOrder(treeOf([]*int{n(3), n(9), n(20), nil, nil, n(15), n(7)})), [][]int{{3}, {9, 20}, {15, 7}}) {
		t.Fatal("level")
	}
	root := treeOf([]*int{n(3), n(5), n(1), n(6), n(2), n(0), n(8)})
	if LowestCommonAncestor(root, root.Left, root.Right) != root || LowestCommonAncestor(root, root.Left, root.Left.Right) != root.Left {
		t.Fatal("lca")
	}
	if Diameter(treeOf([]*int{n(1), n(2), n(3), n(4), n(5)})) != 3 {
		t.Fatal("dia")
	}
	if !IsValidBST(treeOf([]*int{n(2), n(1), n(3)})) || IsValidBST(treeOf([]*int{n(5), n(1), n(4), nil, nil, n(3), n(6)})) {
		t.Fatal("bst")
	}
	if MaxPathSum(treeOf([]*int{n(-10), n(9), n(20), nil, nil, n(15), n(7)})) != 42 {
		t.Fatal("path")
	}
	matrix := [][]int{{1, 4, 7}, {2, 5, 8}, {3, 6, 9}}
	if !SearchMatrix(matrix, 5) || SearchMatrix(matrix, 10) {
		t.Fatal("matrix")
	}
	if KthLargest([]int{3, 2, 1, 5, 6, 4}, 2) != 5 {
		t.Fatal("kth")
	}
	colors := []int{2, 0, 2, 1, 1, 0}
	SortColors(colors)
	if !reflect.DeepEqual(colors, []int{0, 0, 1, 1, 2, 2}) {
		t.Fatal("colors")
	}
	four := []int{3, 1, 0, 2, 1, 3, 0}
	SortFour(four)
	if !reflect.DeepEqual(four, []int{0, 0, 1, 1, 2, 3, 3}) {
		t.Fatal("four", four)
	}
	if LisLength([]int{10, 9, 2, 5, 3, 7, 101, 18}) != 4 || WiggleLength([]int{1, 17, 5, 10, 13, 15, 10, 5, 16, 8}) != 7 {
		t.Fatal("lis")
	}
	if !WordBreak("leetcode", []string{"leet", "code"}) || WordBreak("catsandog", []string{"cats", "dog", "sand", "and", "cat"}) {
		t.Fatal("break")
	}
	square := [][]byte{{'1', '0', '1', '0', '0'}, {'1', '0', '1', '1', '1'}, {'1', '1', '1', '1', '1'}, {'1', '0', '0', '1', '0'}}
	if MaximalSquare(square) != 4 || MinRemoveValid("lee(t(c)o)de)") != "lee(t(c)o)de" || MinRemoveValid("))((") != "" {
		t.Fatal("square")
	}
	qs := []int{3, 6, 8, 10, 1, 2, 1}
	if !reflect.DeepEqual(QuickSort(qs), []int{1, 1, 2, 3, 6, 8, 10}) {
		t.Fatal("quick")
	}
	if !reflect.DeepEqual(DailyTemperatures([]int{73, 74, 75, 71, 69, 72, 76, 73}), []int{1, 1, 4, 2, 1, 1, 0, 0}) {
		t.Fatal("temp")
	}
	if LongestConsecutive([]int{100, 4, 200, 1, 3, 2}) != 4 {
		t.Fatal("consec")
	}
	if !reflect.DeepEqual(ProductExceptSelf([]int{1, 2, 3, 4}), []int{24, 12, 8, 6}) {
		t.Fatal("product")
	}
	if MedianSorted([]int{1, 3}, []int{2}) != 2 || MedianSorted([]int{1, 2}, []int{3, 4}) != 2.5 {
		t.Fatal("median", MedianSorted([]int{1, 2}, []int{3, 4}))
	}
	if SubarraySum([]int{1, 1, 1}, 2) != 2 || SubarraySum([]int{1, 2, 3}, 3) != 2 {
		t.Fatal("sum")
	}
	top := TopKFrequent([]int{1, 1, 1, 2, 2, 3}, 2)
	sort.Ints(top)
	if !reflect.DeepEqual(top, []int{1, 2}) {
		t.Fatal("topk")
	}
	if MinMeetingRooms([][]int{{0, 30}, {5, 10}, {15, 20}}) != 2 || NumProvinces([][]int{{1, 1, 0}, {1, 1, 0}, {0, 0, 1}}) != 2 {
		t.Fatal("rooms")
	}
	if SearchRotated([]int{4, 5, 6, 7, 0, 1, 2}, 0) != 4 || SearchRotated([]int{4, 5, 6, 7, 0, 1, 2}, 3) != -1 {
		t.Fatal("rot")
	}
	if FirstMissingPositive([]int{3, 4, -1, 1}) != 2 || FirstMissingPositive([]int{1, 2, 0}) != 3 {
		t.Fatal("miss")
	}
	if MaxProfit([]int{7, 1, 5, 3, 6, 4}) != 5 || !JumpGame([]int{2, 3, 1, 1, 4}) || JumpGame([]int{3, 2, 1, 0, 4}) {
		t.Fatal("profit")
	}
	if DecodeString("3[a2[c]]") != "accaccacc" || DecodeString("2[abc]3[cd]ef") != "abcabccdcdcdef" {
		t.Fatal("decode", DecodeString("3[a2[c]]"))
	}
	if !ValidParentheses("()[]{}") || ValidParentheses("(]") {
		t.Fatal("paren")
	}
	pal := LongestPalindrome("babad")
	if pal != "bab" && pal != "aba" {
		t.Fatal("pal", pal)
	}
	if ContainerWater([]int{1, 8, 6, 2, 5, 4, 8, 3, 7}) != 49 || UniquePaths(3, 7) != 28 || LCSLength("abcde", "ace") != 3 {
		t.Fatal("misc")
	}
	if len(Subsets([]int{1, 2})) != 4 || GasStation([]int{1, 2, 3, 4, 5}, []int{3, 4, 5, 1, 2}) != 3 {
		t.Fatal("sub")
	}
	if TaskScheduler([]byte{'A', 'A', 'A', 'B', 'B', 'B'}, 2) != 8 || !CanPartition([]int{1, 5, 11, 5}) || CanPartition([]int{1, 2, 3, 5}) {
		t.Fatal("task")
	}
	if RemoveKDigits("1432219", 3) != "1219" || RemoveKDigits("10200", 1) != "200" {
		t.Fatal("rmk", RemoveKDigits("10200", 1))
	}
}
