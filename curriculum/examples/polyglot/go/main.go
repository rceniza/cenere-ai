package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

func normalize(line string) ([]int64, error) {
	line = strings.TrimSpace(line)
	if line == "" { return []int64{}, nil }
	seen := map[int64]bool{}
	for _, part := range strings.Split(line, ",") {
		value, err := strconv.ParseInt(strings.TrimSpace(part), 10, 32)
		if err != nil { return nil, err }
		seen[value] = true
	}
	values := make([]int64, 0, len(seen))
	for value := range seen { values = append(values, value) }
	sort.Slice(values, func(i, j int) bool { return values[i] < values[j] })
	return values, nil
}

func main() {
	line, err := bufio.NewReader(os.Stdin).ReadString('\n')
	if err != nil && line == "" { os.Exit(2) }
	values, err := normalize(line)
	if err != nil { os.Exit(2) }
	fmt.Print("[")
	for i, value := range values { if i > 0 { fmt.Print(",") }; fmt.Print(value) }
	fmt.Println("]")
}
