let steps = [];
let selectedId = null;

function esc(s) {
  return String(s).replace(/&/g, "&amp;")
    .replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCanvas() {
  const canvas = document.getElementById("canvas");
  canvas.innerHTML = "";
  steps.forEach(step => {
    const div = document.createElement("div");
    div.className = "step" + (step.id === selectedId ? " active" : "");
    div.textContent = `${step.name} \u2192 agent: ${step.agent}`;
    div.onclick = () => {
      selectedId = step.id;
      renderCanvas();
      renderConfig();
    };
    canvas.appendChild(div);
  });
}

function renderConfig() {
  const panel = document.getElementById("config-panel");
  const step = steps.find(s => s.id === selectedId);
  if (!step) {
    panel.innerHTML = "No step selected.";
    return;
  }
  panel.innerHTML = `
    <label>Name<br><input id="cfg-name" value="${esc(step.name)}"></label><br>
    <label>Agent<br><input id="cfg-agent" value="${esc(step.agent)}"></label><br>
    <label>Consumes (comma)<br><input id="cfg-consumes"
      value="${esc(step.consumes.join(","))}"></label><br>
  `;
  document.getElementById("cfg-name").oninput = e => step.name = e.target.value;
  document.getElementById("cfg-agent").oninput = e => step.agent = e.target.value;
  document.getElementById("cfg-consumes").oninput = e =>
    step.consumes = e.target.value.split(",").map(s => s.trim()).filter(Boolean);
}

function seedDemo() {
  if (steps.length) return;
  steps = [
    { id: "1", name: "architecture", agent: "analyze", consumes: [] },
    { id: "2", name: "codegen", agent: "orchestrate", consumes: ["architecture"] },
    { id: "3", name: "tests", agent: "orchestrate", consumes: ["codegen"] }
  ];
  selectedId = "2";
}

document.addEventListener("DOMContentLoaded", () => {
  seedDemo();
  document.getElementById("add-step").onclick = () => {
    const id = Date.now().toString();
    steps.push({ id, name: `step_${steps.length + 1}`,
                 agent: "orchestrate", consumes: [] });
    selectedId = id;
    renderCanvas();
    renderConfig();
  };

  document.getElementById("delete-step").onclick = () => {
    if (!selectedId) return;
    const removed = steps.find(s => s.id === selectedId);
    steps = steps.filter(s => s.id !== selectedId);
    steps.forEach(s =>
      s.consumes = s.consumes.filter(c => c !== (removed && removed.name)));
    selectedId = null;
    renderCanvas();
    renderConfig();
  };

  document.getElementById("save-workflow").onclick = async () => {
    const payload = {
      name: "designer_workflow",
      steps: steps.map(s => ({
        name: s.name,
        agent: s.agent,
        consumes: s.consumes
      }))
    };
    const json = JSON.stringify(payload, null, 2);
    console.log("Workflow JSON:", json);

    const blob = new Blob([json], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${payload.name}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  renderCanvas();
  renderConfig();
});
