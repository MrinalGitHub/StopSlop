use serde_json::Value;
use tauri::AppHandle;
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn analyse_text(app: AppHandle, text: String) -> Result<Value, String> {
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
    let sidecar = app
        .shell()
        .sidecar("stopslop-analyse")
        .map_err(|_| "The bundled local analyzer is unavailable.".to_string())?;
    let (mut events, mut child) = sidecar
        .spawn()
        .map_err(|_| "The bundled local analyzer could not start.".to_string())?;

    child
        .write(serde_json::to_string(&request).unwrap_or_default().as_bytes())
        .map_err(|_| "The analysis request could not be sent.".to_string())?;
    child
        .write(b"\n")
        .map_err(|_| "The analysis request could not be completed.".to_string())?;

    let mut stdout = Vec::new();
    while let Some(event) = events.recv().await {
        match event {
            CommandEvent::Stdout(bytes) => stdout.extend(bytes),
            CommandEvent::Stderr(_) => {}
            CommandEvent::Terminated(_) => break,
            _ => {}
        }
    }

    let wrapper: Value = serde_json::from_slice(&stdout)
        .map_err(|_| "The local analyzer returned invalid output.".to_string())?;
    if wrapper.get("ok").and_then(Value::as_bool) != Some(true) {
        return Err("The local analysis could not be completed.".to_string());
    }
    wrapper
        .get("result")
        .cloned()
        .ok_or_else(|| "The local analyzer returned an incomplete result.".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![analyse_text])
        .run(tauri::generate_context!())
        .expect("error while running StopSlop");
}
