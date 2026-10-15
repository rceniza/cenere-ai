use std::{env, fs, process};

fn main() {
    let Some(path) = env::args().nth(1) else {
        eprintln!("usage: parse-integers <file>");
        process::exit(2);
    };

    let contents = match fs::read_to_string(&path) {
        Ok(contents) => contents,
        Err(error) => {
            eprintln!("could not read {path}: {error}");
            process::exit(2);
        }
    };

    let mut invalid_count = 0;
    for (index, line) in contents.lines().enumerate() {
        match line.trim().parse::<i64>() {
            Ok(number) => println!("line {}: {number}", index + 1),
            Err(_) => {
                invalid_count += 1;
                eprintln!("line {}: invalid integer: {line}", index + 1);
            }
        }
    }

    if invalid_count > 0 {
        process::exit(1);
    }
}
