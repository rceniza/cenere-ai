pub fn insert_sorted_unique(values: &[i32], value: i32) -> Vec<i32> {
    let mut result = values.to_vec();
    result.push(value);
    result.sort();
    result
}
