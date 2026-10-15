package main

import (
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

func main() {
	data, err := io.ReadAll(os.Stdin)
	if err != nil {
		os.Exit(2)
	}
	parts := strings.Fields(string(data))
	if len(parts) != 2 {
		os.Exit(2)
	}
	a, errA := strconv.ParseInt(parts[0], 10, 32)
	b, errB := strconv.ParseInt(parts[1], 10, 32)
	if errA != nil || errB != nil {
		os.Exit(2)
	}
	sum := a + b
	if sum < -2147483648 || sum > 2147483647 {
		os.Exit(2)
	}
	fmt.Println(sum)
}
