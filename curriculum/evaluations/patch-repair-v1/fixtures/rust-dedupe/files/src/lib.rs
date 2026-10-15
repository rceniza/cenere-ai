pub fn unique_sorted(values: &[i32]) -> Vec<i32> {
    let mut result = values.to_vec();
    result.sort();
    result
}
