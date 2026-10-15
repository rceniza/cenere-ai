package merge

func mergeSortedUnique(left, right []int) []int {
	result := make([]int, 0, len(left)+len(right))
	i, j := 0, 0
	for i < len(left) || j < len(right) {
		var value int
		switch {
		case j == len(right) || (i < len(left) && left[i] < right[j]):
			value = left[i]
			i++
		case i == len(left) || right[j] < left[i]:
			value = right[j]
			j++
		default:
			value = left[i]
			i++
			j++
		}
		if len(result) == 0 || result[len(result)-1] != value {
			result = append(result, value)
		}
	}
	return result
}
