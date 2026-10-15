pub fn parse_port(value: &str) -> Option<u16> {
    value.parse::<u16>().ok().filter(|port| *port != 0)
}
