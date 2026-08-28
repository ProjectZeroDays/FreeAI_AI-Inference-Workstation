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

// ── Sidebar Toggle ────────────────────────────────────────────────
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.querySelector('.sidebar');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebarToggle.classList.toggle('active');
    sidebar.classList.toggle('collapsed');
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

    // Browser settings
    const br = s.browser || {};
    const brStealth = br.stealth || {};
    const brAnon = br.anonymity || {};
    const brHeal = br.healing || {};
    const brMx = br.manifestx || {};
    const brCdp = br.cdp || {};
    const brObs = br.observability || {};
    const brVp = br.viewport || {};
    $("br-stealth").checked = brStealth.enable !== false;
    $("br-cdp").checked = brCdp.enabled !== false;
    $("br-healing").checked = brHeal.max_retries > 0;
    $("br-manifestx").checked = brMx.enabled !== false;
    $("br-mode").value = brAnon.mode || "none";
    $("br-headless").checked = br.headless !== false;
    $("br-retries").value = brHeal.max_retries || 5;
    $("br-backoff").value = brHeal.retry_backoff || 1.5;
    $("br-viewport-w").value = brVp.width || 1920;
    $("br-viewport-h").value = brVp.height || 1080;
    $("br-screenshot-fail").checked = brHeal.screenshot_on_fail !== false;
    $("br-scroll-view").checked = brHeal.scroll_into_view !== false;
    $("br-adaptive-sel").checked = brHeal.adaptive_selectors !== false;
    $("br-dom-mirror").checked = brObs.dom_mirror === true;
    $("br-port").value = br.api_port || 8180;

    $("current-mode").textContent =
      `current: ${data.current_power_mode}` +
      (s.auto_management ? " (auto)" : " (manual)");
    syncModeLock();

    if (data.version) {
      document.title = `FreeAI Dashboard v${data.version}`;
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
    max_concurrent_runs: parseInt($("max-runs").value, 10),
    // Knight-Shade browser settings
    browser: {
      stealth: {
        enable: $("br-stealth").checked,
        randomize_fingerprint: true,
        mask_webdriver: true,
        fake_headers: true,
        override_navigator: true,
        canvas_noise: true,
        webgl_noise: true,
        audio_noise: true,
      },
      anonymity: {
        mode: $("br-mode").value,
        tor_socks_port: 9150,
      },
      healing: {
        max_retries: parseInt($("br-retries").value, 10),
        retry_backoff: parseFloat($("br-backoff").value),
        adaptive_selectors: $("br-adaptive-sel").checked,
        screenshot_on_fail: $("br-screenshot-fail").checked,
        scroll_into_view: $("br-scroll-view").checked,
      },
      manifestx: {
        enabled: $("br-manifestx").checked,
        god_mode: true,
      },
      cdp: {
        enabled: $("br-cdp").checked,
      },
      observability: {
        dom_mirror: $("br-dom-mirror").checked,
      },
      viewport: {
        width: parseInt($("br-viewport-w").value, 10),
        height: parseInt($("br-viewport-h").value, 10),
      },
      headless: $("br-headless").checked,
      api_port: parseInt($("br-port").value, 10),
    }
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



/* ---------------- autonomous SDLC runs ---------------- */

const RUN_BADGE = { done: "ok", failed: "down", cancelled: "down" };

async function loadRuns() {
  const el = document.getElementById("runs-list");
  try {
    const res = await fetch("/api/runs");
    const d = await res.json();
    if (d.offline) {
      el.innerHTML = "<li class='muted'>autonomous service offline</li>";
      return;
    }
    if (!(d.runs || []).length) {
      el.innerHTML = "<li class='muted'>no runs yet - freeai.py auto-start &lt;spec&gt;</li>";
      return;
    }
    el.innerHTML = "";
    d.runs.slice(0, 8).forEach(r => {
      const li = document.createElement("li");
      const badge = document.createElement("span");
      badge.className = "badge " + (RUN_BADGE[r.status] ||
        (["done","failed","cancelled"].includes(r.status) ? "down" : "warn"));
      badge.textContent = r.status.toUpperCase();
      li.appendChild(badge);
      const spec = (r.spec || "").slice(0, 60);
      li.appendChild(document.createTextNode(" " + r.run_id + " - " + spec));
      el.appendChild(li);
    });
  } catch (e) { el.textContent = "runs unavailable"; }
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


/* ---------------- external providers ---------------- */

async function loadProviders() {
  const el = document.getElementById("providers-list");
  const sel = document.getElementById("prov-test-select");
  try {
    const res = await fetch("/api/providers");
    const d = await res.json();
    el.innerHTML = "";
    sel.innerHTML = "";
    (d.providers || []).forEach(p => {
      const li = document.createElement("li");
      const badge = document.createElement("span");
      badge.className = "badge " + (p.keyed ? "ok" : "down");
      badge.textContent = p.keyed ? "KEYED" : "NO KEY";
      li.appendChild(badge);
      li.appendChild(document.createTextNode(
        " " + p.name + " (" + p.style + ")" +
        (p.fallback ? " [fallback]" : "") +
        " - " + (p.description || "")));
      el.appendChild(li);

      if (p.keyed) {
        const o = document.createElement("option");
        o.value = p.name; o.textContent = p.name;
        sel.appendChild(o);
      }
    });
  } catch (e) { el.textContent = "providers unavailable"; }
}

async function testProvider() {
  const name = document.getElementById("prov-test-select").value;
  const st = document.getElementById("prov-status");
  if (!name) { st.textContent = "no keyed provider selected"; return; }
  st.textContent = "Testing " + name + "...";
  try {
    const res = await fetch("/api/providers/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });
    const d = await res.json();
    st.textContent = d.ok
      ? name + " OK: " + d.latency_ms + "ms - " + (d.reply || "")
      : name + " failed: " + (d.error || res.status);
  } catch (e) { st.textContent = "Error: " + e.message; }
}

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  loadProviders();
  loadRuns();
  loadUploads();
  loadSkillsSummary();
  document.getElementById("up-send").onclick = uploadFile;
  fetchStatus();
  setInterval(fetchStatus, 5000);
  setInterval(loadRuns, 15000);
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
  $("skills-scan-btn").onclick = () => scanSkills();

  /* ---------------- Shodan card ---------------- */
  async function refreshShodanBadge() {
    try {
      const r = await fetch("/api/shodan/key");
      const d = await r.json();
      const badge = $("shodan-status-badge");
      if (badge) badge.textContent = d.configured ? d.key_prefix || "key set" : "no key";
    } catch (_) { /* ignore */ }
  }

  $("shodan-search-btn").onclick = async () => {
    const q = $("shodan-query").value.trim();
    const status = $("shodan-search-status");
    const results = $("shodan-results");
    if (!q) { status.textContent = "enter a query"; return; }
    status.textContent = "searching...";
    results.textContent = "";
    try {
      const r = await fetch("/api/shodan/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, limit: 10 })
      });
      const d = await r.json();
      if (!r.ok) { status.textContent = "error: " + (d.error || r.status); return; }
      status.textContent = d.total + " results";
      if (!d.results.length) { results.textContent = "no results found."; return; }
      results.innerHTML = d.results.slice(0, 10).map(h =>
        `<div style="padding:4px 0;border-bottom:1px solid var(--border)">${h.ip_str} <span class="muted">- ${h.hostname || "(no hostname)"} <span class="muted">[${(h.tags||[]).join(",")||"no tags"}]</span></div>`
      ).join("");
    } catch (e) { status.textContent = "error: " + e.message; }
  };

  $("shodan-host-btn").onclick = async () => {
    const ip = $("shodan-host-ip").value.trim();
    const status = $("shodan-host-status");
    const results = $("shodan-host-results");
    if (!ip) { status.textContent = "enter an IP"; return; }
    status.textContent = "looking up...";
    results.textContent = "";
    try {
      const r = await fetch(`/api/shodan/host/${encodeURIComponent(ip)}`);
      const d = await r.json();
      if (!r.ok) { status.textContent = "error: " + (d.error || r.status); return; }
      const h = d.data || {};
      status.textContent = "found";
      results.innerHTML = [
        `<div><b>IP:</b> ${String(h.ip_str || ip).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Hostnames:</b> ${String((h.hostnames||[]).join(", ") || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Organization:</b> ${String(h.organization || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Operating System:</b> ${String(h.os || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Ports:</b> ${String((h.ports||[]).join(", ") || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Tags:</b> ${String((h.tags||[]).join(", ") || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>Country:</b> ${String(h.country_name || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
         <div><b>City:</b> ${String(h.city || "—").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>`,
      ].join("");
    } catch (e) { status.textContent = "error: " + e.message; }
  };

  $("shodan-save-key").onclick = async () => {
    const key = $("shodan-api-key").value.trim();
    const status = $("shodan-key-status");
    status.textContent = "saving...";
    try {
      const r = await fetch("/api/shodan/key", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key })
      });
      const d = await r.json();
      if (d.ok) {
        status.textContent = "saved — restart dashboard to apply";
        $("shodan-api-key").value = "";
        refreshShodanBadge();
      } else {
        status.textContent = "save failed";
      }
    } catch (e) { status.textContent = "error: " + e.message; }
  };

  refreshShodanBadge();
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

/* ---------------- skills summary ---------------- */

async function loadSkillsSummary() {
  try {
    const res = await fetch("/api/skills/aggregated");
    const d = await res.json();
    const skills = d.skills || [];
    const total = d.total || skills.length;
    const cats = {};
    let autoCount = 0;
    let enabledCount = 0;
    for (const s of skills) {
      const c = s.category || "general";
      cats[c] = (cats[c] || 0) + 1;
      if (s.auto_generated) autoCount++;
      if (s.enabled !== false) enabledCount++;
    }
    const elTotal = document.getElementById("skills-total");
    const elCats = document.getElementById("skills-categories");
    const elAuto = document.getElementById("skills-auto");
    const elEnabled = document.getElementById("skills-enabled");
    const elBadge = document.getElementById("skills-count-badge");
    const elBar = document.getElementById("skills-category-bar");
    if (elTotal) elTotal.textContent = total;
    if (elCats) elCats.textContent = Object.keys(cats).length;
    if (elAuto) elAuto.textContent = autoCount;
    if (elEnabled) elEnabled.textContent = enabledCount;
    if (elBadge) elBadge.textContent = total + " skills";
    if (elBar) {
      elBar.innerHTML = "";
      const colors = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6", "#14b8a6", "#f97316"];
      Object.entries(cats).forEach(([cat, count], i) => {
        const chip = document.createElement("span");
        chip.className = "pill";
        chip.style.cssText = `background:${colors[i % colors.length]}22;color:${colors[i % colors.length]};border:1px solid ${colors[i % colors.length]}44;font-size:11px;padding:2px 7px;`;
        chip.textContent = `${cat} (${count})`;
        elBar.appendChild(chip);
      });
    }
  } catch (e) {
    const el = document.getElementById("skills-total");
    if (el) el.textContent = "—";
  }
}

async function scanSkills() {
  const btn = document.getElementById("skills-scan-btn");
  if (!btn) return;
  btn.disabled = true;
  btn.textContent = "Scanning…";
  try {
    const res = await fetch("/api/skills/scan", { method: "POST" });
    const d = await res.json();
    btn.textContent = `Scan complete — ${d.count || 0} new`;
    loadSkillsSummary();
    setTimeout(() => { btn.textContent = "Scan for new skills"; btn.disabled = false; }, 3000);
  } catch (e) {
    btn.textContent = "Scan failed";
    setTimeout(() => { btn.textContent = "Scan for new skills"; btn.disabled = false; }, 3000);
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

/* ── JWT auth badge ───────────────────────────────────────────── */
(function updateAuthBadge() {
  var badge = document.getElementById("user-badge");
  var nameEl = document.getElementById("user-name");
  var roleEl = document.getElementById("user-role");
  if (!badge) return;
  if (typeof FreeAIAuth === "undefined" || !FreeAIAuth.isAuthenticated()) {
    badge.style.display = "none";
    return;
  }
  var user = FreeAIAuth.getUser();
  if (user) {
    badge.style.display = "";
    nameEl.textContent = user.username;
    roleEl.textContent = "[" + user.role + "]";
    badge.onclick = function () {
      if (confirm("Logout " + user.username + "?")) {
        FreeAIAuth.logout();
      }
    };
  } else {
    badge.style.display = "none";
  }
})();
