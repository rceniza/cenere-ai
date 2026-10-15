use std::io::{self, Read};

fn parse(input: &str) -> Result<Vec<i32>, String> {
    let line = input.trim();
    if line.is_empty() {
        return Ok(Vec::new());
    }
    let mut values = Vec::new();
    for token in line.split(',') {
        let value = token.trim().parse::<i32>().map_err(|_| format!("invalid integer: {token}"))?;
        values.push(value);
    }
    values.sort_unstable();
    values.dedup();
    Ok(values)
}

fn main() {
    let mut input = String::new();
    if io::stdin().read_to_string(&mut input).is_err() {
        std::process::exit(2);
    }
    match parse(&input) {
        Ok(values) => println!("[{}]", values.iter().map(i32::to_string).collect::<Vec<_>>().join(",")),
        Err(_) => std::process::exit(2),
    }
}
