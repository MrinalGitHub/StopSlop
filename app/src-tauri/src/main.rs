use serde_json::Value;
use std::env;
use std::io::Write;
use std::process::{Command, Stdio};
use tauri::State;

struct AnalyzerCommand {
    executable: String,
    arguments: Vec<String>,
}

fn analyzer_command() -> AnalyzerCommand {
    if let Ok(value) = env::var("STOPSLOP_ANALYZER_COMMAND") {
        return AnalyzerCommand {
            executable: value,
            arguments: Vec::new(),
        };
    }

    AnalyzerCommand {
        executable: "stopslop-analyse".to_string(),
        arguments: Vec::new(),
    }
}

#[tauri::command]
fn analyse_text(text: String, command: State<'_, AnalyzerCommand>) -> Result<Value, String> {
    if text.trim().len() < 20 {
        return Err("Please provide at least 20 characters of prose.".to_string());
    }
    if text.len() > 50000 {
        return Err("Please keep the text below 50,000 characters.".to_string());
    }

    let request = serde_json::json!({
        "text": text,
        "include_findings": true
    });

    let mut child = Command::new(&command.executable)
        .args(&command.arguments)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|_| "The local analysis bridge is unavailable.".to_string())?;

    if let Some(stdin) = child.stdin.as_mut() {
        let bytes = serde_json::to_vec(&request)
            .map_err(|_| "The analysis request could not be prepared.".to_string())?;
        stdin
            .write_all(&bytes)
            .map_err(|_| "The analysis request could not be sent.".to_string())?;
    }

    let output = child
        .wait_with_output()
        .map_err(|_| "The local analysis could not be completed.".to_string())?;

    let wrapper: Value = serde_json::from_slice(&output.stdout)
        .map_err(|_| "The local detector returned invalid output.".to_string())?;

    if wrapper.get("ok").and_then(Value::as_bool) != Some(true) {
        return Err("The local analysis could not be completed.".to_string());
    }

    wrapper
        .get("result")
        .cloned()
        .ok_or_else(|| "The local detector returned an incomplete result.".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(analyzer_command())
        .invoke_handler(tauri::generate_handler![analyse_text])
        .run(tauri::generate_context!())
        .expect("error while running StopSlop");
}

fn main() {
    run();
}
