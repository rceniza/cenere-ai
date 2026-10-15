//! Model-facing tool schemas and strict decoding of requested tool actions.

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub(crate) struct ToolCall {
    pub(crate) id: String,
    #[serde(rename = "type")]
    pub(crate) kind: String,
    pub(crate) function: ToolCallFunction,
}

#[derive(Serialize, Deserialize, Clone)]
pub(crate) struct ToolCallFunction {
    pub(crate) name: String,
    pub(crate) arguments: String,
}

#[derive(Serialize)]
pub(crate) struct ToolDefinition {
    #[serde(rename = "type")]
    kind: &'static str,
    function: ToolDefinitionFunction,
    strict: bool,
}

#[derive(Serialize)]
struct ToolDefinitionFunction {
    name: &'static str,
    description: &'static str,
    parameters: serde_json::Value,
}

pub(crate) enum AgentTool {
    Shell(String),
    Search(String),
    Browser(String),
}

pub(crate) fn definitions() -> Vec<ToolDefinition> {
    let schema =
        |name: &'static str, description: &'static str, property: &'static str| ToolDefinition {
            kind: "function",
            strict: true,
            function: ToolDefinitionFunction {
                name,
                description,
                parameters: serde_json::json!({
                    "type": "object",
                    "properties": { property: { "type": "string" } },
                    "required": [property],
                    "additionalProperties": false
                }),
            },
        };
    vec![
        schema(
            "run_shell",
            "Run one shell command after user approval",
            "command",
        ),
        schema("web_search", "Search the web after user approval", "query"),
        schema(
            "open_page",
            "Open a web page or local live test URL after user approval",
            "url",
        ),
    ]
}

pub(crate) fn web_search_definition() -> Vec<ToolDefinition> {
    definitions()
        .into_iter()
        .filter(|tool| tool.function.name == "web_search")
        .collect()
}

pub(crate) fn parse_structured(call: &ToolCall) -> Option<AgentTool> {
    if call.kind != "function" {
        return None;
    }
    let args: serde_json::Value = serde_json::from_str(&call.function.arguments).ok()?;
    match call.function.name.as_str() {
        "run_shell" => args
            .get("command")?
            .as_str()
            .filter(|s| !s.trim().is_empty())
            .map(|s| AgentTool::Shell(s.into())),
        "web_search" => args
            .get("query")?
            .as_str()
            .filter(|s| !s.trim().is_empty())
            .map(|s| AgentTool::Search(s.into())),
        "open_page" => args
            .get("url")?
            .as_str()
            .filter(|s| s.starts_with("http://") || s.starts_with("https://"))
            .map(|s| AgentTool::Browser(s.into())),
        _ => None,
    }
}

pub(crate) fn parse_legacy(response: &str) -> Option<AgentTool> {
    let text = response.trim();
    for (open, close, build) in [
        ("<shell>", "</shell>", 0),
        ("<web_search>", "</web_search>", 1),
        ("<browser>", "</browser>", 2),
    ] {
        if let Some(body) = text.strip_prefix(open).and_then(|s| s.strip_suffix(close)) {
            let value = body.trim().to_string();
            if value.is_empty() {
                return None;
            }
            return Some(match build {
                0 => AgentTool::Shell(value),
                1 => AgentTool::Search(value),
                _ => AgentTool::Browser(value),
            });
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    fn call(name: &str, arguments: &str) -> ToolCall {
        ToolCall {
            id: "call_1".into(),
            kind: "function".into(),
            function: ToolCallFunction {
                name: name.into(),
                arguments: arguments.into(),
            },
        }
    }

    #[test]
    fn emits_three_sequentially_approved_function_schemas() {
        let tools = definitions();
        assert_eq!(tools.len(), 3);
        let encoded = serde_json::to_value(tools).unwrap();
        assert_eq!(encoded[0]["function"]["name"], "run_shell");
        assert_eq!(
            encoded[0]["function"]["parameters"]["additionalProperties"],
            false
        );
    }

    #[test]
    fn parses_valid_calls_and_fails_closed_on_invalid_input() {
        assert!(
            matches!(parse_structured(&call("run_shell", r#"{"command":"cargo check"}"#)), Some(AgentTool::Shell(s)) if s == "cargo check")
        );
        assert!(
            matches!(parse_structured(&call("web_search", r#"{"query":"Rust docs"}"#)), Some(AgentTool::Search(s)) if s == "Rust docs")
        );
        assert!(
            matches!(parse_structured(&call("open_page", r#"{"url":"https://example.test"}"#)), Some(AgentTool::Browser(s)) if s == "https://example.test")
        );
        assert!(parse_structured(&call("run_shell", r#"{"command":" "}"#)).is_none());
        assert!(parse_structured(&call("open_page", r#"{"url":"file:///etc/passwd"}"#)).is_none());
        assert!(parse_structured(&call("unknown", "{}")).is_none());
        assert!(parse_structured(&call("run_shell", "{invalid")).is_none());
    }

    #[test]
    fn accepts_native_tool_call_assistant_message_with_null_content() {
        let message: ToolCall = serde_json::from_str(r#"{"id":"call_1","type":"function","function":{"name":"web_search","arguments":"{\"query\":\"Rust docs\"}"}}"#).unwrap();
        assert!(
            matches!(parse_structured(&message), Some(AgentTool::Search(q)) if q == "Rust docs")
        );
    }

    #[test]
    fn parses_only_exact_legacy_tool_tags() {
        assert!(
            matches!(parse_legacy("<shell>cargo check</shell>"), Some(AgentTool::Shell(s)) if s == "cargo check")
        );
        assert!(
            matches!(parse_legacy("<web_search>Rust docs</web_search>"), Some(AgentTool::Search(s)) if s == "Rust docs")
        );
        assert!(
            matches!(parse_legacy("<browser>http://localhost</browser>"), Some(AgentTool::Browser(s)) if s == "http://localhost")
        );
        assert!(parse_legacy("text <shell>cargo check</shell>").is_none());
        assert!(parse_legacy("<shell> </shell>").is_none());
    }
}
