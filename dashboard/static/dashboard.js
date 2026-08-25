const ctx = document.getElementById("gpuChart").getContext("2d");
const gpuChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [{
      label: "GPU Utilization (%)",
      data: [],
      borderColor: "#22c55e",
      backgroundColor: "rgba(34, 197, 94, 0.2)",
      tension: 0.3
    }]
  },
  options: {
    scales: {
      y: { beginAtZero: true, max: 100 }
    }
  }
});

function updateChart(util) {
  gpuChart.data.labels.push("");
  gpuChart.data.datasets[0].data.push(util);

  if (gpuChart.data.labels.length > 50) {
    gpuChart.data.labels.shift();
    gpuChart.data.datasets[0].data.shift();
  }

  gpuChart.update();
}

function renderAlerts(alerts) {
  const list = document.getElementById("alerts-list");
  if (!alerts || !alerts.length) {
    list.innerHTML = '<li class="muted">No alerts.</li>';
    return;
  }
  list.innerHTML = "";
  alerts.forEach(a => {
    const li = document.createElement("li");
    const badge = document.createElement("span");
    badge.className = "badge " + (a.level === "critical" ? "down" : "warn");
    badge.textContent = a.level.toUpperCase();
    li.appendChild(badge);
    li.appendChild(document.createTextNode(" " + a.message));
    list.appendChild(li);
  });
}

/* ---------------- settings panel ---------------- */

const $ = id => document.getElementById(id);

async function loadSettings() {
  try {
    const res = await fetch("/api/settings");
    const data = await res.json();
    const s = data.settings;

    $("opt-auto").checked = !!s.auto_management;
    $("opt-mode").value = s.forced_mode;
    $("gpu-pl").value = s.power_limit_w;
    $("gpu-clk").value = s.locked_clock_mhz;
    $("rpen").value = s.repeat_penalty;
    $("rlastn").value = s.repeat_last_n;
    $("ctx").value = s.llama_ctx;
    $("max-runs").value = s.max_concurrent_runs;

    $("current-mode").textContent =
      `current: ${data.current_power_mode}` +
      (s.auto_management ? " (auto)" : " (manual)");
    syncModeLock();

    if (data.version) {
      document.title = `Tokugawa Dashboard v${data.version}`;
    }

    updateIdleBanner(s.idle);
    if (data.llama_restart_pending) {
      $("settings-status").textContent =
        "sampling changes pending llama restart";
    }
  } catch (e) {
    $("settings-status").textContent = "failed to load settings";
  }
}

function updateIdleBanner(idle) {
  const banner = $("idle-banner");
  if (!idle || !idle.active) {
    banner.classList.add("hidden");
    return;
  }
  const remainMin = Math.max(0,
    Math.round((idle.until_epoch * 1000 - Date.now()) / 60000));
  banner.textContent =
    `Idle window active — eco enforced, auto-restore in ~${remainMin} min`;
  banner.classList.remove("hidden");
}

/* ---------------- presets ---------------- */

async function loadPresets() {
  try {
    const res = await fetch("/api/presets");
    const data = await res.json();
    const sel = $("preset-select");
    sel.innerHTML = "";

    const groupB = document.createElement("optgroup");
    groupB.label = "Recommended";
    data.builtins.forEach(p => {
      const o = document.createElement("option");
      o.value = p.name;
      o.textContent = p.name + " — " + (p.description || "");
      groupB.appendChild(o);
    });
    sel.appendChild(groupB);

    if (data.customs.length) {
      const groupC = document.createElement("optgroup");
      groupC.label = "Custom";
      data.customs.forEach(p => {
        const o = document.createElement("option");
        o.value = p.name;
        o.textContent = p.name + (p.description ? " — " + p.description : "");
        groupC.appendChild(o);
      });
      sel.appendChild(groupC);
    }

    // mark the timed-idle builtin so the idle box prefills
    const idlePreset = data.builtins.find(
      p => p.idle_default_minutes);
    if (idlePreset && !$("idle-min").dataset.touched) {
      $("idle-min").value = idlePreset.idle_default_minutes;
    }
  } catch (e) { /* non-fatal */ }
}

async function applySelectedPreset() {
  const name = $("preset-select").value;
  const isIdle = name === "Idle (timed)";
  const body = {};
  if (isIdle) body.duration_min = parseInt($("idle-min").value, 10);

  const statusEl = $("settings-status");
  statusEl.textContent = `Applying ${name}...`;
  try {
    const res = await fetch(`/api/presets/${encodeURIComponent(name)}/apply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const out = await res.json();
    if (!res.ok) {
      statusEl.textContent = "Error: " + (out.error || res.status);
      return;
    }
    statusEl.textContent = isIdle
      ? `Idle window started (${out.idle_minutes} min)`
      : `Preset "${name}" applied`;
    loadSettings();
    fetchStatus();
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
  }
}

async function saveCustomPreset() {
  const name = $("preset-name").value.trim();
  const statusEl = $("settings-status");
  if (!name) {
    statusEl.textContent = "Enter a name for the custom preset";
    return;
  }
  try {
    const res = await fetch("/api/presets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, settings: collectSettings() })
    });
    const out = await res.json();
    if (!res.ok) {
      statusEl.textContent = "Error: " + (out.error || res.status);
      return;
    }
    statusEl.textContent = `Preset "${name}" saved`;
    $("preset-name").value = "";
    await loadPresets();
    $("preset-select").value = name;
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
  }
}

async function deleteSelectedPreset() {
  const name = $("preset-select").value;
  if (!confirm(`Delete custom preset "${name}"?`)) return;
  try {
    const res = await fetch(`/api/presets/${encodeURIComponent(name)}`,
                            { method: "DELETE" });
    const out = await res.json();
    $("settings-status").textContent = res.ok
      ? `Deleted "${name}"` : "Error: " + (out.error || res.status);
    loadPresets();
  } catch (e) {
    $("settings-status").textContent = "Error: " + e.message;
  }
}

async function startIdleWindow() {
  const minutes = parseInt($("idle-min").value, 10);
  $("preset-select").value = "Idle (timed)";
  await applySelectedPresetWithMinutes(minutes);
}

async function applySelectedPresetWithMinutes(minutes) {
  const body = { duration_min: minutes };
  const statusEl = $("settings-status");
  try {
    const res = await fetch("/api/presets/Idle%20(timed)/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const out = await res.json();
    statusEl.textContent = res.ok
      ? `Idle window started (${minutes} min)`
      : "Error: " + (out.error || res.status);
    loadSettings();
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
  }
}

function syncModeLock() {
  const auto = $("opt-auto").checked;
  $("opt-mode").disabled = auto;   // optimizer owns mode when auto is on
}

function collectSettings() {
  return {
    auto_management: $("opt-auto").checked,
    forced_mode: $("opt-mode").value,
    power_limit_w: parseInt($("gpu-pl").value, 10),
    locked_clock_mhz: parseInt($("gpu-clk").value, 10),
    repeat_penalty: parseFloat($("rpen").value),
    repeat_last_n: parseInt($("rlastn").value, 10),
    llama_ctx: parseInt($("ctx").value, 10),
    max_concurrent_runs: parseInt($("max-runs").value, 10)
  };
}

async function saveSettings(restartLlama) {
  const statusEl = $("settings-status");
  statusEl.textContent = "Saving...";

  try {
    const body = collectSettings();
    const url = restartLlama
      ? "/api/settings/llama-restart"
      : "/api/settings";

    // always persist first via POST /api/settings
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const out = await res.json();
    if (!res.ok) {
      statusEl.textContent = "Error: " + (out.error || res.status);
      return;
    }

    let methodNote = "";
    if (!body.auto_management && !out.gpu_applied) {
      statusEl.textContent =
        "Saved, but GPU tune failed: " + (out.gpu_error || "?");
      return;
    }

    if (restartLlama) {
      const r2 = await fetch("/api/settings/llama-restart",
                             { method: "POST" });
      const o2 = await r2.json();
      methodNote = ` | llama restarting via ${o2.method}`;
    }

    statusEl.textContent = "Saved" +
      (body.auto_management ? " (optimizer will apply caps)" : "") +
      methodNote;
    loadSettings();   // refresh current-mode display
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
  }
}


/* ---------------- clients switchboard + uploads ---------------- */

async function loadClients() {
  const el = document.getElementById("clients-list");
  try {
    const res = await fetch("/api/clients");
    const d = await res.json();
    el.innerHTML = "";
    (d.clients || []).forEach(c => {
      const li = document.createElement("li");
      const badge = document.createElement("span");
      badge.className = "badge " + (c.enabled ? "ok" : "down");
      badge.textContent = c.enabled ? "ON" : "OFF";
      li.appendChild(badge);
      li.appendChild(document.createTextNode(
        " " + (c.name || c.id) + (c.port ? " :" + c.port : "")));
      el.appendChild(li);
    });
  } catch (e) { el.textContent = "switchboard unavailable"; }
}

async function loadUploads() {
  const el = document.getElementById("uploads-list");
  try {
    const res = await fetch("/api/uploads");
    const d = await res.json();
    el.innerHTML = (d.uploads || []).map(u =>
      "<li>" + u.name + " <span class='muted'>(" +
      (u.bytes / 1024).toFixed(1) + " KB)</span></li>").join("")
      || "<li class='muted'>no uploads</li>";
  } catch (e) { el.textContent = ""; }
}

async function uploadFile() {
  const inp = document.getElementById("up-file");
  const st = document.getElementById("up-status");
  if (!inp.files.length) { st.textContent = "choose a file first"; return; }
  const fd = new FormData();
  fd.append("file", inp.files[0]);
  st.textContent = "Uploading...";
  try {
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    const d = await res.json();
    st.textContent = res.ok ? "Saved " + d.name : "Error: " + (d.error || res.status);
    loadUploads();
  } catch (e) { st.textContent = "Error: " + e.message; }
}

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  loadUploads();
  document.getElementById("up-send").onclick = uploadFile;
  fetchStatus();
  setInterval(fetchStatus, 5000);
  loadSettings();
  loadPresets();
  loadModelShelf();
  setInterval(() => {           // keep idle countdown fresh
    fetch("/api/settings").then(r => r.json())
      .then(d => updateIdleBanner(d.settings.idle))
      .catch(() => {});
  }, 30000);

  // live push: any settings/preset write anywhere reloads this panel
  if (window.EventSource) {
    const es = new EventSource("/api/events");
    es.onmessage = ev => {
      try {
        const d = JSON.parse(ev.data);
        if (d.type === "settings-changed") {
          loadSettings();
          fetchStatus();
        }
      } catch (_) { /* ignore malformed frames */ }
    };
  }

  $("opt-auto").addEventListener("change", syncModeLock);
  $("idle-min").addEventListener("input",
    e => e.target.dataset.touched = "1");
  $("save-settings").onclick = () => saveSettings(false);
  $("apply-llama").onclick = () => saveSettings(true);
  $("apply-preset").onclick = applySelectedPreset;
  $("save-preset").onclick = saveCustomPreset;
  $("delete-preset").onclick = deleteSelectedPreset;
  $("start-idle").onclick = startIdleWindow;
});

/* ---------------- model shelf ---------------- */

async function loadModelShelf() {
  const el = $("model-shelf");
  if (!el) return;
  try {
    const res = await fetch("/api/models-status");
    const d = await res.json();
    if (d.error) { el.textContent = "model shelf: " + d.error; return; }
    const lines = d.models.map(m =>
      `${m.present ? "●" : "○"} ${m.name || m.id}` +
      (m.present && m.size_bytes
        ? ` (${(m.size_bytes / 1e9).toFixed(1)}GB)` : ""));
    el.innerHTML =
      `<strong>Models</strong> <span class="muted">` +
      `${d.disk_free_gb}GB free</span><br>` +
      lines.join("<br>") +
      `<br><span class="muted">missing → bash models/auto-download-models.sh</span>`;
  } catch (e) {
    el.textContent = "model shelf unavailable";
  }
}

async function fetchStatus() {
  const gpuUtil = document.getElementById("gpu-util");
  const gpuMem = document.getElementById("gpu-mem");
  const gpuExtra = document.getElementById("gpu-extra");
  const servicesList = document.getElementById("services-list");
  const ts = document.getElementById("timestamp");

  try {
    const res = await fetch("/api/status");
    const json = await res.json();

    renderAlerts(json.alerts);

    gpuUtil.textContent = `Utilization: ${json.gpu.utilization}%`;
    updateChart(json.gpu.utilization);
    gpuMem.textContent =
      `Memory: ${json.gpu.memory_used} / ${json.gpu.memory_total} MiB`;
    gpuExtra.textContent =
      `Mode: ${json.power_mode || "balanced"} | ` +
      `Temp: ${json.gpu.temperature}C | Power: ${json.gpu.power_watts}W` +
      ` | Clock: ${json.gpu.clock_mhz}MHz`;

    servicesList.innerHTML = "";
    Object.entries(json.services).forEach(([name, ok]) => {
      const li = document.createElement("li");
      const badge = document.createElement("span");
      badge.className = "badge " + (ok ? "ok" : "down");
      badge.textContent = ok ? "UP" : "DOWN";
      li.textContent = name + " ";
      li.appendChild(badge);
      servicesList.appendChild(li);
    });

    ts.textContent = new Date(json.timestamp * 1000).toLocaleString();
  } catch (e) {
    gpuUtil.textContent = "Error fetching status";
    gpuMem.textContent = "";
    servicesList.innerHTML = "";
    ts.textContent = "";
  }
}
