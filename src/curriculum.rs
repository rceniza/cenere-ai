//! Shared curriculum catalog and lookup logic used by the CLI and web API.
use anyhow::{Context, Result};

const DATA: &str = include_str!("../curriculum/catalog.json");

pub fn catalog() -> Result<serde_json::Value> {
    serde_json::from_str(DATA).context("parsing embedded curriculum catalog")
}

pub fn print(track_id: Option<&str>) -> Result<()> {
    let catalog = catalog()?;
    let tracks = catalog["tracks"]
        .as_array()
        .context("curriculum tracks missing")?;
    let Some(track_id) = track_id else {
        println!("Cenere learning tracks (beginner → intermediate → advanced):");
        for item in tracks {
            println!(
                "  {:<18} {}",
                item["id"].as_str().unwrap_or("?"),
                item["title"].as_str().unwrap_or("")
            );
        }
        println!("\nRun `cenere learn <track-id>` to see its sequence and practice tasks.");
        return Ok(());
    };
    let item = tracks
        .iter()
        .find(|item| item["id"] == track_id)
        .with_context(|| {
            format!("unknown track '{track_id}'; run `cenere learn` to list tracks")
        })?;
    println!(
        "{}\n{}",
        item["title"].as_str().unwrap_or(""),
        item["summary"].as_str().unwrap_or("")
    );
    for stage in item["stages"].as_array().context("track stages missing")? {
        println!(
            "\n{} — {}",
            stage["level"].as_str().unwrap_or(""),
            stage["goal"].as_str().unwrap_or("")
        );
        for lesson in stage["lessons"]
            .as_array()
            .context("stage lessons missing")?
        {
            println!(
                "  • {}: {}",
                lesson["title"].as_str().unwrap_or(""),
                lesson["practice"].as_str().unwrap_or("")
            );
        }
    }
    Ok(())
}

fn lookup_lesson<'a>(
    catalog: &'a serde_json::Value,
    track_id: &str,
    level: &str,
    lesson_number: usize,
) -> Result<(
    &'a serde_json::Value,
    &'a serde_json::Value,
    &'a serde_json::Value,
)> {
    anyhow::ensure!(lesson_number > 0, "lesson numbers start at 1");
    let track = catalog["tracks"]
        .as_array()
        .and_then(|tracks| tracks.iter().find(|item| item["id"] == track_id))
        .with_context(|| {
            format!("unknown track '{track_id}'; run `cenere learn` to list tracks")
        })?;
    let stage = track["stages"]
        .as_array()
        .and_then(|stages| stages.iter().find(|stage| stage["level"] == level))
        .with_context(|| {
            format!("unknown level '{level}'; use beginner, intermediate, or advanced")
        })?;
    let lesson = stage["lessons"]
        .as_array()
        .context("lesson list missing")?
        .get(lesson_number - 1)
        .with_context(|| format!("lesson {lesson_number} is not in the {level} stage"))?;
    Ok((track, stage, lesson))
}

fn reference_source(reference: &str) -> Result<&'static str> {
    match reference {
        "examples/rust/parse_integers.rs" => Ok(include_str!(
            "../curriculum/examples/rust/parse_integers.rs"
        )),
        "examples/polyglot/c/main.c" => {
            Ok(include_str!("../curriculum/examples/polyglot/c/main.c"))
        }
        "examples/polyglot/cpp/main.cpp" => {
            Ok(include_str!("../curriculum/examples/polyglot/cpp/main.cpp"))
        }
        "examples/polyglot/php/main.php" => {
            Ok(include_str!("../curriculum/examples/polyglot/php/main.php"))
        }
        "examples/polyglot/node/main.js" => {
            Ok(include_str!("../curriculum/examples/polyglot/node/main.js"))
        }
        "examples/polyglot/python/main.py" => Ok(include_str!(
            "../curriculum/examples/polyglot/python/main.py"
        )),
        "examples/polyglot/rust/main.rs" => {
            Ok(include_str!("../curriculum/examples/polyglot/rust/main.rs"))
        }
        "examples/polyglot/go/main.go" => {
            Ok(include_str!("../curriculum/examples/polyglot/go/main.go"))
        }
        _ => anyhow::bail!("unsupported curriculum reference '{reference}'"),
    }
}

pub fn reference_example(
    track_id: &str,
    level: &str,
    lesson_number: usize,
) -> Result<Option<&'static str>> {
    let catalog = catalog()?;
    let (_, _, lesson) = lookup_lesson(&catalog, track_id, level, lesson_number)?;
    lesson["reference"]
        .as_str()
        .map(reference_source)
        .transpose()
}

pub fn reference_language(
    track_id: &str,
    level: &str,
    lesson_number: usize,
) -> Result<Option<String>> {
    let catalog = catalog()?;
    let (_, _, lesson) = lookup_lesson(&catalog, track_id, level, lesson_number)?;
    Ok(lesson["language"].as_str().map(str::to_owned))
}

pub fn lesson_search_query(track_id: &str, level: &str, lesson_number: usize) -> Result<String> {
    let catalog = catalog()?;
    let (track, stage, lesson) = lookup_lesson(&catalog, track_id, level, lesson_number)?;
    let practice = lesson["practice"].as_str().unwrap_or("");
    let practice_excerpt: String = practice.chars().take(160).collect();
    Ok(format!(
        "{} {} {} {} official documentation",
        track["title"].as_str().unwrap_or(track_id),
        stage["level"].as_str().unwrap_or(level),
        lesson["title"].as_str().unwrap_or("programming lesson"),
        practice_excerpt
    ))
}

pub fn lesson_prompt(track_id: &str, level: &str, lesson_number: usize) -> Result<String> {
    let catalog = catalog()?;
    let (track, stage, lesson) = lookup_lesson(&catalog, track_id, level, lesson_number)?;
    let mut prompt = format!(
        "Teach this curriculum lesson as a patient programming tutor. Explain the key idea in small steps, show a short example, then give the learner a practice task and a way to verify it. Put hints and a sample solution under separate headings so the learner can stop before seeing them. Do not claim code was run. If the task requires a compiler, browser, cluster, or service that may not be installed, say how to check and offer a no-install alternative.\n\nTrack: {}\nStage: {}\nStage goal: {}\nLesson: {}\nPractice task: {}",
        track["title"].as_str().unwrap_or(track_id), level,
        stage["goal"].as_str().unwrap_or(""), lesson["title"].as_str().unwrap_or(""),
        lesson["practice"].as_str().unwrap_or("")
    );
    if let Some(steps) = lesson["steps"].as_array() {
        prompt.push_str("\n\nTeach the learner in this sequence; explain and check understanding at each step:\n");
        for (index, step) in steps.iter().enumerate() {
            prompt.push_str(&format!("{}. {}\n", index + 1, step.as_str().unwrap_or("")));
        }
    }
    if let Some(reference) = lesson["reference"].as_str() {
        let source = reference_source(reference)?;
        let language = lesson["language"].as_str().unwrap_or("text");
        prompt.push_str(&format!(
            "\n\nVerified reference implementation (use this exact implementation and behavior in your explanation):\n```{language}\n"
        ));
        prompt.push_str(source);
        prompt.push_str("\n```");
    }
    Ok(prompt)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tracks_are_unique_and_have_ordered_stages() {
        let catalog = catalog().unwrap();
        let tracks = catalog["tracks"].as_array().unwrap();
        assert!(tracks.len() >= 20);
        let mut ids = std::collections::HashSet::new();
        for track in tracks {
            assert!(ids.insert(track["id"].as_str().unwrap().to_owned()));
            let stages = track["stages"].as_array().unwrap();
            assert_eq!(stages.len(), 3);
            assert_eq!(stages[0]["level"], "beginner");
            assert_eq!(stages[1]["level"], "intermediate");
            assert_eq!(stages[2]["level"], "advanced");
            for stage in stages {
                let lessons = stage["lessons"].as_array().unwrap();
                assert!(
                    lessons.len() >= 3,
                    "{} / {} needs at least three lessons",
                    track["id"],
                    stage["level"]
                );
                for lesson in lessons {
                    assert!(!lesson["title"].as_str().unwrap_or("").trim().is_empty());
                    assert!(!lesson["practice"].as_str().unwrap_or("").trim().is_empty());
                }
            }
        }
    }

    #[test]
    fn lesson_lookup_validates_track_stage_and_number() {
        let prompt = lesson_prompt("rust", "beginner", 1).unwrap();
        assert!(prompt.contains("line.parse::<i64>()"));
        assert!(prompt.contains("Do not use a regex"));
        assert!(prompt.contains("Verified reference implementation"));
        assert!(prompt.contains("```rust"));
        assert!(reference_example("rust", "beginner", 1).unwrap().is_some());
        assert!(reference_example("rust", "intermediate", 1)
            .unwrap()
            .is_none());
        assert!(lesson_prompt("unknown", "beginner", 1).is_err());
        assert!(lesson_prompt("rust", "expert", 1).is_err());
        assert!(lesson_prompt("rust", "beginner", 0).is_err());
        assert!(lesson_prompt("rust", "beginner", 99).is_err());
        assert!(lesson_search_query("react", "advanced", 3)
            .unwrap()
            .contains("Rendering and hydration Profile a large list, compare rerender"));
        assert!(lesson_search_query("unknown", "beginner", 1).is_err());
    }

    #[test]
    fn polyglot_worked_lessons_include_the_matching_verified_reference() {
        let cases = [
            ("c", "c", "#include <stdio.h>"),
            ("cpp", "cpp", "#include <iostream>"),
            ("php", "php", "<?php"),
            ("javascript-typescript", "javascript", "node:readline"),
            ("nodejs", "javascript", "node:readline"),
            ("python", "python", "def normalize"),
            ("rust", "rust", "fn parse"),
            ("go-java", "go", "package main"),
        ];
        for (track, language, source_marker) in cases {
            let prompt = lesson_prompt(track, "beginner", 3).unwrap();
            assert!(prompt.contains(&format!("```{language}")), "{track}");
            assert!(prompt.contains(source_marker), "{track}");
            assert!(
                prompt.contains("1. Read one complete input line"),
                "{track}"
            );
        }
    }
}
