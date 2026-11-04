package algo

import (
	"reflect"
	"testing"
)

func TestAlgo(t *testing.T) {
	if !reflect.DeepEqual(TwoSum([]int{2, 7, 11, 15}, 9), []int{0, 1}) {
		t.Fatal("twoSum")
	}
	if !reflect.DeepEqual(TwoSum([]int{3, 3}, 6), []int{0, 1}) {
		t.Fatal("twoSum2")
	}
	if LongestUnique("abcabcbb") != 3 || LongestUnique("bbbbb") != 1 || LongestUnique("") != 0 {
		t.Fatal("longest")
	}
	got3 := ThreeSum([]int{-1, 0, 1, 2, -1, -4})
	want3 := [][]int{{-1, -1, 2}, {-1, 0, 1}}
	if !reflect.DeepEqual(got3, want3) {
		t.Fatalf("three %#v", got3)
	}
	if Trap([]int{0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1}) != 6 || Trap(nil) != 0 {
		t.Fatal("trap")
	}
	merged := MergeIntervals([][]int{{1, 3}, {2, 6}, {8, 10}, {15, 18}})
	if !reflect.DeepEqual(merged, [][]int{{1, 6}, {8, 10}, {15, 18}}) {
		t.Fatalf("merge %#v", merged)
	}
	if !reflect.DeepEqual(MergeIntervals([][]int{{1, 4}, {4, 5}}), [][]int{{1, 5}}) {
		t.Fatal("mergeTouch")
	}

	cache := NewLRU(2)
	cache.Put(1, 1)
	cache.Put(2, 2)
	if cache.Get(1) != 1 {
		t.Fatal("lru1")
	}
	cache.Put(3, 3)
	if cache.Get(2) != -1 {
		t.Fatal("lru2")
	}
	cache.Put(4, 4)
	if cache.Get(1) != -1 || cache.Get(3) != 3 || cache.Get(4) != 4 {
		t.Fatal("lru3")
	}

	if !CanFinish(2, [][]int{{1, 0}}) || CanFinish(2, [][]int{{1, 0}, {0, 1}}) {
		t.Fatal("course")
	}
	grid := [][]byte{{'1', '1', '0'}, {'1', '0', '0'}, {'0', '0', '1'}}
	if NumIslands(grid) != 2 {
		t.Fatal("islands")
	}
	if !reflect.DeepEqual(WindowMax([]int{1, 3, -1, -3, 5, 3, 6, 7}, 3), []int{3, 3, 5, 5, 6, 7}) {
		t.Fatal("window")
	}
	if EditDistance("horse", "ros") != 3 || EditDistance("", "a") != 1 {
		t.Fatal("edit")
	}
	if CoinChange([]int{1, 2, 5}, 11) != 3 || CoinChange([]int{2}, 3) != -1 {
		t.Fatal("coin")
	}
	if MinWindow("ADOBECODEBANC", "ABC") != "BANC" || MinWindow("a", "aa") != "" {
		t.Fatal("minWindow")
	}
	med := NewMedian()
	med.AddNum(1)
	med.AddNum(2)
	if med.FindMedian() != 1.5 {
		t.Fatal("median")
	}
	med.AddNum(3)
	if med.FindMedian() != 2 {
		t.Fatal("median2")
	}
	if MinCost([][]int{{1, 3, 1}, {1, 5, 1}, {4, 2, 1}}) != 7 {
		t.Fatal("cost")
	}
	near := KNearest([]string{"c", "a", "b"}, []float64{31.2, 39.90, 40.00}, []float64{121.5, 116.40, 116.40}, 39.91, 116.41, 2)
	if !reflect.DeepEqual(near, []string{"a", "b"}) {
		t.Fatalf("near %#v", near)
	}
	square := [][2]float64{{0, 0}, {4, 0}, {4, 4}, {0, 4}}
	if !PointInPolygon(1, 1, square) || PointInPolygon(5, 5, square) {
		t.Fatal("pip")
	}
	if hash := GeohashEncode(57.64911, 10.40744, 11); hash != "u4pruydqqvj" {
		t.Fatal("geohash", hash)
	}
	if ShipWithinDays([]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 5) != 15 {
		t.Fatal("ship")
	}
}
