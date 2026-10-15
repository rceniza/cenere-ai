#[path = "../src/lib.rs"]
mod lib;

#[test]
fn sorts_and_removes_duplicates() {
    assert_eq!(lib::unique_sorted(&[4, 1, 4, -2, 1]), vec![-2, 1, 4]);
}

#[test]
fn handles_empty_singleton_and_duplicate_only_inputs() {
    assert_eq!(lib::unique_sorted(&[]), Vec::<i32>::new());
    assert_eq!(lib::unique_sorted(&[7]), vec![7]);
    assert_eq!(lib::unique_sorted(&[3, 3, 3]), vec![3]);
}
