package merge

func mergeSortedUnique(left, right []int) []int {
	return append(left, right...)
}
