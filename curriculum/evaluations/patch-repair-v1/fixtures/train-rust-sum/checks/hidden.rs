#[path = "../src/lib.rs"]
mod lib;

#[test]
fn sums_values_and_handles_empty_input() {
    assert_eq!(lib::checked_sum(&[2, -1, 4]), Some(5));
    assert_eq!(lib::checked_sum(&[]), Some(0));
}

#[test]
fn returns_none_when_addition_overflows() {
    assert_eq!(lib::checked_sum(&[i32::MAX, 1]), None);
    assert_eq!(lib::checked_sum(&[i32::MIN, -1]), None);
}
