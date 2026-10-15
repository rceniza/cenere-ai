use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    if io::stdin().read_to_string(&mut input).is_err() {
        std::process::exit(2);
    }
    let parts: Vec<&str> = input.split_whitespace().collect();
    if parts.len() != 2 {
        std::process::exit(2);
    }
    let a = parts[0].parse::<i32>().unwrap_or_else(|_| std::process::exit(2));
    let b = parts[1].parse::<i32>().unwrap_or_else(|_| std::process::exit(2));
    let sum = a.checked_add(b).unwrap_or_else(|| std::process::exit(2));
    println!("{sum}");
}
