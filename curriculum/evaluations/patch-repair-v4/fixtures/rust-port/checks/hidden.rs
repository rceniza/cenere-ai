#[path = "../src/lib.rs"]
mod subject;

#[test]
fn accepts_only_nonzero_u16_ports() {
    assert_eq!(subject::parse_port("1"), Some(1));
    assert_eq!(subject::parse_port("65535"), Some(65535));
    for invalid in ["0", "65536", "-1", " 80", "80 ", "abc", ""] {
        assert_eq!(subject::parse_port(invalid), None, "input: {invalid:?}");
    }
}
