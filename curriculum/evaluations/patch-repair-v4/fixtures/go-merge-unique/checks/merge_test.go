package merge

import (
	"reflect"
	"testing"
)

func TestMergeSortedUnique(t *testing.T) {
	left := []int{-4, 1, 1, 8}
	right := []int{-4, 0, 8, 9}
	got := mergeSortedUnique(left, right)
	want := []int{-4, 0, 1, 8, 9}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v, want %v", got, want)
	}
	if !reflect.DeepEqual(left, []int{-4, 1, 1, 8}) || !reflect.DeepEqual(right, []int{-4, 0, 8, 9}) {
		t.Fatalf("inputs were mutated: left=%v right=%v", left, right)
	}
	if got := mergeSortedUnique(nil, nil); got == nil || len(got) != 0 {
		t.Fatalf("empty result must be non-nil and empty, got %#v", got)
	}
}
