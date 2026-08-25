const AGENT_API = "http://localhost:8020";

const presets = [
  { id: "qwen3.6-12b", label: "Ultra Coder 12B", description: "Qwen3.6 12B - primary coder, architecture & full projects" },
  { id: "claude-code-9b", label: "CodeClawd 9B", description: "Qwen3.5 CodeClawd - Claude Code + Codex agent traces" },
  { id: "qwythos-v2", label: "Qwythos v2 9B", description: "Qwythos 9B v2 (FTPO loop-fix) - reasoning primary, 1M ctx" },
  { id: "qwythos-9b", label: "Qwythos 9B", description: "Qwythos 9B - Claude Mythos reasoning, 1M ctx" },
  { id: "qwable-9b", label: "Qwable 9B", description: "Qwable - Claude Fable 5 multimodal generalist" },
  { id: "qwen3.5-thinking", label: "Qwen THINKING 9B", description: "Claude HighIQ THINKING (i1) - reasoning fallback" },
  { id: "qwen3.5-9b", label: "Qwen HighIQ 9B", description: "Claude HighIQ Heretic - legacy" },
  { id: "moe-13b", label: "MOE 13.7B", description: "L3.1 MOE 2x8B - fast coder, refactor & debug" }
];

let selectedModel = "qwen3.6-12b";
let selectedAgent = "orchestrate";

function renderModels() {
  const container = document.getElementById("model-list");
  container.innerHTML = "";

  presets.forEach(p => {
    const btn = document.createElement("button");
    btn.textContent = p.label;
    btn.title = p.description;
    btn.className = "model-btn" + (p.id === selectedModel ? " active" : "");
    btn.onclick = () => {
      selectedModel = p.id;
      renderModels();
    };
    container.appendChild(btn);
  });
}

function bindAgents() {
  document.querySelectorAll(".agent-buttons button").forEach(btn => {
    btn.addEventListener("click", () => {
      selectedAgent = btn.dataset.agent;
      document.querySelectorAll(".agent-buttons button")
        .forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

async function sendRequest() {
  const prompt = document.getElementById("prompt").value;
  const output = document.getElementById("output");

  if (!prompt.trim()) {
    output.textContent = "Please enter a prompt.";
    return;
  }

  let url = `${AGENT_API}/agent/orchestrate`;
  let body = { prompt };

  if (selectedAgent === "project") {
    url = `${AGENT_API}/agent/project`;
    body = { spec: prompt };
  } else if (selectedAgent === "refactor") {
    url = `${AGENT_API}/agent/refactor`;
    body = { code: prompt };
  } else if (selectedAgent === "debug") {
    url = `${AGENT_API}/agent/debug`;
    body = { code: prompt, error: "Describe the error here" };
  } else if (selectedAgent === "analyze") {
    url = `${AGENT_API}/agent/analyze`;
    body = { context: prompt, question: "Describe what you want to know here" };
  }

  output.textContent = "Running...";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const json = await res.json();
    // structured header for router response fields
    const meta = document.createElement("div");
    meta.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px";
    const pill = (label, val, color) => {
      const s = document.createElement("span");
      s.textContent = `${label}: ${val}`;
      s.style.cssText = `padding:3px 8px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid ${color}30;background:${color}18;color:${color === "#22C55E" ? "#BBF7D0" : color === "#38BDF8" ? "#BAE6FD" : "#FDE68A"}`;
      return s;
    };
    if (json.model_used) meta.appendChild(pill("model", json.model_used, "#22C55E"));
    if (json.task_type) meta.appendChild(pill("task", json.task_type, "#38BDF8"));
    if (json.confidence != null) meta.appendChild(pill("confidence", json.confidence, "#F59E0B"));
    if (json.elapsed_ms != null) meta.appendChild(pill("elapsed", json.elapsed_ms + "ms", "#A78BFA"));
    output.innerHTML = "";
    if (meta.childNodes.length) output.appendChild(meta);
    const pre = document.createElement("pre");
    pre.style.cssText = "margin:0;white-space:pre-wrap;word-break:break-word";
    pre.textContent = JSON.stringify(json.response ?? json, null, 2);
    output.appendChild(pre);
  } catch (e) {
    output.textContent = "Error: " + e.message;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderModels();
  bindAgents();
  document.getElementById("send").addEventListener("click", sendRequest);
});
