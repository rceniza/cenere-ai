package patchtrain

import "testing"

func TestFirstNonEmpty(t *testing.T) {
	if got := firstNonEmpty([]string{"", "  ", " value ", "later"}); got != "value" {
		t.Fatalf("got %q, want %q", got, "value")
	}
	if got := firstNonEmpty([]string{"", "  "}); got != "" {
		t.Fatalf("got %q, want empty", got)
	}
}
