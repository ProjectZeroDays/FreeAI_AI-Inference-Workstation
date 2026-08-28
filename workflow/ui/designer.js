/**
 * Workflow Designer — standalone step manager
 *
 * This file provides a lightweight step-based workflow editor.
 * The rich canvas designer lives in designer.html (inline script).
 * This module is used by programmatic tests and headless consumers.
 */

let steps = [];
let selectedId = null;
let history = [];
let historyIdx = -1;

function esc(s) {
  return String(s).replace(/&/g, "&amp;")
    .replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function pushHistory() {
  history = history.slice(0, historyIdx + 1);
  history.push(JSON.stringify({ steps: steps.slice(), selectedId }));
  historyIdx = history.length - 1;
}

function undo() {
  if (historyIdx <= 0) return false;
  historyIdx--;
  const snap = JSON.parse(history[historyIdx]);
  steps = snap.steps;
  selectedId = snap.selectedId;
  renderCanvas();
  renderConfig();
  return true;
}

function redo() {
  if (historyIdx >= history.length - 1) return false;
  historyIdx++;
  const snap = JSON.parse(history[historyIdx]);
  steps = snap.steps;
  selectedId = snap.selectedId;
  renderCanvas();
  renderConfig();
  return true;
}

function renderCanvas() {
  const canvas = document.getElementById("canvas");
  if (!canvas) return;
  canvas.innerHTML = "";
  steps.forEach(step => {
    const div = document.createElement("div");
    div.className = "step" + (step.id === selectedId ? " active" : "");
    div.textContent = `${step.name} → agent: ${step.agent}`;
    div.draggable = true;
    div.addEventListener("dragstart", e => {
      e.dataTransfer.setData("text/plain", step.id);
      div.classList.add("dragging");
    });
    div.addEventListener("dragend", () => div.classList.remove("dragging"));
    div.addEventListener("drop", e => {
      e.preventDefault();
      const fromId = e.dataTransfer.getData("text/plain");
      const toId = step.id;
      if (fromId !== toId) reorderSteps(fromId, toId);
    });
    div.addEventListener("dragover", e => {
      e.preventDefault();
      div.classList.add("drag-over");
    });
    div.addEventListener("dragleave", () => div.classList.remove("drag-over"));
    div.onclick = () => {
      selectedId = step.id;
      renderCanvas();
      renderConfig();
    };
    canvas.appendChild(div);
  });
}

function reorderSteps(fromId, toId) {
  pushHistory();
  const fromIdx = steps.findIndex(s => s.id === fromId);
  const toIdx = steps.findIndex(s => s.id === toId);
  if (fromIdx < 0 || toIdx < 0) return;
  const [removed] = steps.splice(fromIdx, 1);
  steps.splice(toIdx, 0, removed);
  renderCanvas();
}

function renderConfig() {
  const panel = document.getElementById("config-panel");
  if (!panel) return;
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
  document.getElementById("cfg-name").oninput = e => {
    step.name = e.target.value;
    renderCanvas();
  };
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
  pushHistory();
}

document.addEventListener("DOMContentLoaded", () => {
  seedDemo();

  document.getElementById("add-step").onclick = () => {
    pushHistory();
    const id = Date.now().toString();
    steps.push({ id, name: `step_${steps.length + 1}`,
                 agent: "orchestrate", consumes: [] });
    selectedId = id;
    renderCanvas();
    renderConfig();
  };

  document.getElementById("delete-step").onclick = () => {
    if (!selectedId) return;
    pushHistory();
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

  // Keyboard shortcuts
  document.addEventListener("keydown", e => {
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key === "z") { e.preventDefault(); undo(); }
    if (ctrl && e.key === "y") { e.preventDefault(); redo(); }
    if (ctrl && e.key === "s") { e.preventDefault(); document.getElementById("save-workflow").click(); }
    if (ctrl && e.key === "n") {
      e.preventDefault();
      document.getElementById("add-step").click();
    }
    if (e.key === "Delete" && selectedId && document.activeElement.tagName !== "INPUT") {
      document.getElementById("delete-step").click();
    }
  });

  renderCanvas();
  renderConfig();
});
