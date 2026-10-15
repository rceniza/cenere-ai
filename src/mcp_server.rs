//! Read-only MCP tools for Cenere's local notes and Skills.

use super::{skills, AppState};
use anyhow::Result;
use rmcp::{handler::server::wrapper::Parameters, schemars, tool, tool_router, ServiceExt};
use serde::Deserialize;
use std::path::PathBuf;

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub(crate) struct SearchMemoryInput {
    /// Words or phrases to find in saved local project notes.
    query: String,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub(crate) struct ListSkillsInput {
    /// Workspace root used to look for workspace Skills.
    #[serde(default = "default_workspace")]
    repo: String,
}

fn default_workspace() -> String {
    ".".into()
}

#[derive(Clone)]
pub(crate) struct CenereMcp {
    state: AppState,
}

#[tool_router(server_handler)]
impl CenereMcp {
    pub(crate) fn new(state: AppState) -> Self {
        Self { state }
    }

    /// Search Cenere's SQLite FTS5 project notes. This tool only reads saved notes.
    #[tool(
        name = "search_project_memory",
        description = "Search saved local Cenere project notes"
    )]
    async fn search_memory(&self, Parameters(input): Parameters<SearchMemoryInput>) -> String {
        match self.state.memories(&input.query, 8) {
            Ok(rows) if rows.is_empty() => "No matching saved notes.".into(),
            Ok(rows) => rows
                .into_iter()
                .map(|row| format!("- {row}"))
                .collect::<Vec<_>>()
                .join("\n"),
            Err(error) => format!("Memory search failed: {error}"),
        }
    }

    /// List available Cenere instruction Skills without executing their contents.
    #[tool(
        name = "list_skills",
        description = "List Cenere Skills available in a workspace and user profile"
    )]
    async fn list_skills(&self, Parameters(input): Parameters<ListSkillsInput>) -> String {
        match skills::discover(&PathBuf::from(input.repo)) {
            Ok(items) if items.is_empty() => "No Skills found.".into(),
            Ok(items) => items
                .into_iter()
                .map(|item| format!("{} — {}", item.name, item.description))
                .collect::<Vec<_>>()
                .join("\n"),
            Err(error) => format!("Skill listing failed: {error}"),
        }
    }
}

pub(crate) async fn serve(state: AppState) -> Result<()> {
    let server = CenereMcp::new(state)
        .serve(rmcp::transport::stdio())
        .await?;
    server.waiting().await?;
    Ok(())
}
