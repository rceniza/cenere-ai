//! Small, file-based Skills registry. Skills provide instructions only; they
//! never execute scripts implicitly.

use anyhow::{Context, Result};
use std::{
    fs,
    path::{Path, PathBuf},
};

const MAX_SKILL_BYTES: u64 = 12 * 1024;
const MAX_CONTEXT_BYTES: usize = 24 * 1024;
const MAX_MATCHES: usize = 4;

#[derive(Debug, Clone)]
pub(crate) struct Skill {
    pub(crate) name: String,
    pub(crate) description: String,
    instructions: String,
}

fn skill_roots(repo: &Path) -> Vec<PathBuf> {
    let mut roots = vec![repo.join(".cenere/skills")];
    if let Some(home) = std::env::var_os("HOME") {
        roots.push(PathBuf::from(home).join(".cenere/skills"));
    }
    roots
}

pub(crate) fn discover(repo: &Path) -> Result<Vec<Skill>> {
    let mut skills = Vec::new();
    for root in skill_roots(repo) {
        let Ok(entries) = fs::read_dir(&root) else {
            continue;
        };
        for entry in entries.flatten() {
            let path = entry.path().join("SKILL.md");
            let Ok(metadata) = fs::metadata(&path) else {
                continue;
            };
            if !metadata.is_file() || metadata.len() > MAX_SKILL_BYTES {
                continue;
            }
            let text = fs::read_to_string(&path)
                .with_context(|| format!("read Skill {}", path.display()))?;
            let (name, description, instructions) =
                parse(&text, entry.file_name().to_string_lossy().as_ref());
            if !instructions.trim().is_empty() {
                skills.push(Skill {
                    name,
                    description,
                    instructions,
                });
            }
        }
    }
    skills.sort_by(|a, b| a.name.cmp(&b.name));
    skills.dedup_by(|a, b| a.name.eq_ignore_ascii_case(&b.name));
    Ok(skills)
}

fn parse(text: &str, fallback: &str) -> (String, String, String) {
    let mut name = fallback.to_string();
    let mut description = String::new();
    let body = if let Some(rest) = text.strip_prefix("---\n") {
        if let Some(end) = rest.find("\n---\n") {
            for line in rest[..end].lines() {
                if let Some((key, value)) = line.split_once(':') {
                    let value = value.trim().trim_matches(['"', '\'']);
                    match key.trim() {
                        "name" if !value.is_empty() => name = value.to_string(),
                        "description" => description = value.to_string(),
                        _ => {}
                    }
                }
            }
            &rest[end + 5..]
        } else {
            text
        }
    } else {
        text
    };
    (name, description, body.trim().to_string())
}

pub(crate) fn matching_context(repo: &Path, task: &str) -> Result<String> {
    let lower_task = task.to_lowercase();
    let mut selected = discover(repo)?
        .into_iter()
        .filter(|skill| {
            let searchable = format!("{} {}", skill.name, skill.description).to_lowercase();
            searchable
                .split(|c: char| !c.is_alphanumeric())
                .filter(|w| w.len() >= 3)
                .any(|word| lower_task.contains(word))
        })
        .take(MAX_MATCHES);
    let mut result = String::new();
    for skill in &mut selected {
        let section = format!("### {}\n{}\n", skill.name, skill.instructions);
        if result.len() + section.len() > MAX_CONTEXT_BYTES {
            break;
        }
        result.push_str(&section);
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_frontmatter_and_body() {
        let (name, description, body) = parse(
            "---\nname: Rust\ndescription: Rust coding\n---\nPrefer idiomatic Rust.",
            "fallback",
        );
        assert_eq!(name, "Rust");
        assert_eq!(description, "Rust coding");
        assert_eq!(body, "Prefer idiomatic Rust.");
    }

    #[test]
    fn malformed_frontmatter_remains_in_body() {
        let (name, _, body) = parse("---\nname: broken\nbody", "fallback");
        assert_eq!(name, "fallback");
        assert!(body.contains("name: broken"));
    }
}
