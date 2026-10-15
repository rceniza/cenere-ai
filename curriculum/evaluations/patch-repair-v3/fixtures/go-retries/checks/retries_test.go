package main

import "testing"

func TestClampRetries(t *testing.T) {
	cases := map[int]int{-3: 1, 0: 1, 1: 1, 4: 4, 10: 10, 11: 10, 100: 10}
	for input, want := range cases {
		if got := clampRetries(input); got != want {
			t.Errorf("clampRetries(%d) = %d, want %d", input, got, want)
		}
	}
}
