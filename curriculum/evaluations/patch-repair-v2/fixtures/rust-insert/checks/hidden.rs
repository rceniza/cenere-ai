#[path = "../src/lib.rs"]
mod lib;

#[test]
fn inserts_in_order_without_duplicates() {
    assert_eq!(lib::insert_sorted_unique(&[1, 3, 8], 5), vec![1, 3, 5, 8]);
    assert_eq!(lib::insert_sorted_unique(&[1, 3, 8], 3), vec![1, 3, 8]);
    assert_eq!(lib::insert_sorted_unique(&[1, 3, 3, 8], 3), vec![1, 3, 8]);
}

#[test]
fn handles_empty_input() {
    assert_eq!(lib::insert_sorted_unique(&[], 9), vec![9]);
}
