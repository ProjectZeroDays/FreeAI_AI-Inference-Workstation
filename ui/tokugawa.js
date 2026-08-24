const AGENT_API = "http://localhost:8020";

const presets = [
  {
    id: "qwen3.6-12b",
    label: "\uD83E\uDDE0 Ultra Coder (12B IQ Ultra)",
    description: "Full projects, production code, architecture"
  },
  {
    id: "moe-13b",
    label: "\u26A1 MOE Fast Coder (13.7B)",
    description: "Refactoring, debugging, patching"
  },
  {
    id: "qwen3.5-9b",
    label: "\uD83D\uDD0D Reasoning Specialist (Claude-style)",
    description: "Analysis, planning, decomposition"
  }
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
    output.textContent = JSON.stringify(json, null, 2);
  } catch (e) {
    output.textContent = "Error: " + e.message;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderModels();
  bindAgents();
  document.getElementById("send").addEventListener("click", sendRequest);
});
