const vscode = require("vscode");
const http = require("http");

function getConfig() {
    const cfg = vscode.workspace.getConfiguration("bananalyzer");
    return {
        mcpUrl: cfg.get("mcpUrl", "http://127.0.0.1:8001/v1/context"),
        debounceMs: cfg.get("pushDebounceMs", 500),
    };
}

function postJson(path, payload) {
    const { mcpUrl } = getConfig();
    const baseUrl = mcpUrl.replace(/\/v1\/context$/, "").replace(/\/context$/, "");
    const url = new URL(baseUrl + path);
    const json = JSON.stringify(payload);
    const options = {
        hostname: url.hostname,
        port: url.port || 8001,
        path: url.pathname,
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": Buffer.byteLength(json),
        },
    };
    const req = http.request(options);
    req.on("error", () => { });
    req.write(json);
    req.end();
}

function pushContext(editor) {
    if (!editor || !editor.document) return;

    const doc = editor.document;
    const selection = editor.selection;
    const selectedText = selection && !selection.isEmpty
        ? doc.getText(selection)
        : doc.getText();

    const { mcpUrl } = getConfig();
    const url = new URL(mcpUrl);
    const payload = JSON.stringify({
        file: doc.fileName,
        language: doc.languageId,
        selection: selectedText,
    });
    const options = {
        hostname: url.hostname,
        port: url.port || 8001,
        path: url.pathname,
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": Buffer.byteLength(payload),
        },
    };

    const req = http.request(options);
    req.on("error", () => { });
    req.write(payload);
    req.end();
}

function pushWorkspace() {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0) return;
    postJson("/v1/workspace", { workspace_root: folders[0].uri.fsPath });
}

let debounceTimer = null;

function onEditorChanged(editor) {
    if (!editor || !editor.document) return;
    if (debounceTimer) clearTimeout(debounceTimer);

    pushContext(editor);
}

function onSelectionChanged(event) {
    const editor = event.textEditor;
    if (!editor || !editor.document) return;

    if (debounceTimer) clearTimeout(debounceTimer);
    const { debounceMs } = getConfig();
    debounceTimer = setTimeout(() => pushContext(editor), debounceMs);
}

function activate(context) {
    pushWorkspace();

    const editor = vscode.window.activeTextEditor;
    if (editor) {
        pushContext(editor);
    }

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(onEditorChanged),
        vscode.window.onDidChangeTextEditorSelection(onSelectionChanged),
        vscode.workspace.onDidChangeWorkspaceFolders(pushWorkspace),
    );
}

function deactivate() {
    if (debounceTimer) clearTimeout(debounceTimer);
}

module.exports = { activate, deactivate };
