/* ── Notification system ────────────────────────────────────────── */

const NOTIF_WS_URL = `ws://${location.hostname}:8765`;
const NOTIF_AUTO_DISMISS = 10000;

let _notifSettings = { enabled_types: ["error","warning","info","success"], sound: true };
let _notifWs = null;
let _toastEls = [];

// ── Icons per level ────────────────────────────────────────────────
const NOTIF_ICONS = { error: "✕", warning: "⚠", info: "ℹ", success: "✓" };
const NOTIF_LABELS = { error: "Error", warning: "Warning", info: "Info", success: "Success" };

// ── WebSocket connection ───────────────────────────────────────────
function connectNotifWs() {
  if (_notifWs) { _notifWs.close(); _notifWs = null; }
  const ws = new WebSocket(NOTIF_WS_URL);
  ws.onopen = () => {
    console.log("[notif] WS connected");
    _notifWs = ws;
    refreshNotifLog();
  };
  ws.onmessage = (ev) => {
    try {
      const n = JSON.parse(ev.data);
      pushNotification(n);
    } catch (_) { /* ignore */ }
  };
  ws.onclose = () => {
    _notifWs = null;
    setTimeout(connectNotifWs, 3000);
  };
}

// ── Toast popup ────────────────────────────────────────────────────
function pushNotification(n) {
  const types = _notifSettings.enabled_types || ["error","warning","info","success"];
  if (!types.includes(n.level)) return;

  // Play sound
  if (_notifSettings.sound && n.level !== "info") {
    try { playNotifSound(n.level); } catch (_) {}
  }

  // Create toast element
  const container = document.getElementById("notif-toasts");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast level-${n.level}`;
  const icon = NOTIF_ICONS[n.level] || "●";
  toast.innerHTML = `
    <span class="toast-icon ${n.level}">${icon}</span>
    <div class="toast-body">
      <div class="toast-title">${escHtml(n.title)}</div>
      <div class="toast-msg">${escHtml(n.message)}</div>
    </div>
    <button class="toast-close" title="Dismiss">✕</button>
  `;
  container.appendChild(toast);

  // Dismiss button
  toast.querySelector(".toast-close").onclick = () => dismissToast(toast, n);

  // Auto-dismiss for info/warning
  if (n.level === "info" || n.level === "warning") {
    const prog = document.createElement("div");
    prog.className = "toast-progress";
    const bar = document.createElement("div");
    bar.className = "toast-progress-bar";
    bar.style.cssText = `color:var(--${n.level === "info" ? "accent-2" : "warn"}); animation-duration:${NOTIF_AUTO_DISMISS}ms;`;
    prog.appendChild(bar);
    toast.querySelector(".toast-body").appendChild(prog);
    setTimeout(() => dismissToast(toast, n), NOTIF_AUTO_DISMISS);
  }

  _toastEls.push(toast);
  updateNotifBadge();
}

function dismissToast(toast, n) {
  toast.classList.add("removing");
  setTimeout(() => toast.remove(), 260);
  if (n && n.id) markRead(n.id);
}

function playNotifSound(level) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    if (level === "error") {
      osc.frequency.value = 220; gain.gain.value = 0.15;
      osc.start(); osc.stop(ctx.currentTime + 0.2);
      setTimeout(() => {
        const o2 = ctx.createOscillator(); const g2 = ctx.createGain();
        o2.connect(g2); g2.connect(ctx.destination);
        o2.frequency.value = 180; g2.gain.value = 0.15;
        o2.start(); o2.stop(ctx.currentTime + 0.25);
      }, 220);
    } else if (level === "warning") {
      osc.frequency.value = 440; gain.gain.value = 0.1;
      osc.start(); osc.stop(ctx.currentTime + 0.15);
    } else if (level === "success") {
      osc.frequency.value = 523; gain.gain.value = 0.1;
      osc.start();
      setTimeout(() => { osc.frequency.value = 659; }, 120);
      osc.stop(ctx.currentTime + 0.3);
    }
  } catch (_) { /* silent */ }
}

// ── Panel ──────────────────────────────────────────────────────────
function toggleNotifPanel() {
  const panel = document.getElementById("notif-panel");
  const overlay = document.getElementById("notif-overlay");
  if (!panel) return;
  const isOpen = panel.classList.toggle("open");
  if (overlay) overlay.classList.toggle("open", isOpen);
  if (isOpen) refreshNotifLog();
}

function closeNotifPanel() {
  const panel = document.getElementById("notif-panel");
  const overlay = document.getElementById("notif-overlay");
  if (panel) panel.classList.remove("open");
  if (overlay) overlay.classList.remove("open");
}

async function refreshNotifLog() {
  try {
    const res = await fetch("/api/notifications");
    const data = await res.json();
    _notifSettings = data.settings || _notifSettings;
    renderNotifLog(data.log || []);
    updateNotifBadge();
  } catch (_) { /* non-fatal */ }
}

function renderNotifLog(log) {
  const body = document.getElementById("notif-log-body");
  if (!body) return;
  if (!log.length) {
    body.innerHTML = '<div class="notif-empty">No notifications yet.</div>';
    return;
  }
  body.innerHTML = "";
  log.forEach(n => {
    const el = document.createElement("div");
    el.className = `notif-item level-${n.level}${n.read ? "" : " unread"}`;
    const icon = NOTIF_ICONS[n.level] || "●";
    const time = n.ts ? new Date(n.ts * 1000).toLocaleTimeString() : "";
    const src = n.source ? ` · ${escHtml(n.source)}` : "";
    el.innerHTML = `
      <div class="notif-icon ${n.level}">${icon}</div>
      <div class="notif-content">
        <div class="notif-title">${escHtml(n.title)}</div>
        <div class="notif-msg">${escHtml(n.message)}</div>
        <div class="notif-meta">${time}${src}</div>
      </div>
      ${n.level !== "info" ? `<button class="notif-dismiss" data-id="${escHtml(n.id)}" title="Dismiss">✕</button>` : ""}
    `;
    const dbtn = el.querySelector(".notif-dismiss");
    if (dbtn) {
      dbtn.onclick = () => {
        dbtn.parentElement.remove();
        markRead(n.id);
      };
    }
    body.appendChild(el);
  });
}

function markRead(id) {
  if (!_notifWs) return;
  try { _notifWs.send(JSON.stringify({ action: "mark_read", id })); } catch (_) {}
  updateNotifBadge();
}

function updateNotifBadge() {
  const badge = document.getElementById("notif-badge");
  const count = document.getElementById("notif-unread-count");
  if (!badge) return;
  const unread = (document.getElementById("notif-log-body")?.querySelectorAll(".unread")?.length) || 0;
  if (unread > 0) {
    badge.textContent = unread > 9 ? "+9" : unread;
    badge.style.display = "flex";
  } else {
    badge.style.display = "none";
  }
}

// ── Settings modal ─────────────────────────────────────────────────
async function openNotifSettings() {
  try {
    const res = await fetch("/api/notifications/settings");
    _notifSettings = await res.json();
  } catch (_) {}
  renderSettingsModal();
  document.getElementById("notif-settings-modal")?.classList.add("open");
}

function renderSettingsModal() {
  const box = document.getElementById("notif-settings-body");
  if (!box) return;
  const types = ["error","warning","info","success"];
  box.innerHTML = `
    <div class="setting-row">
      <span class="setting-label">Sound effects</span>
      <div class="toggle ${_notifSettings.sound ? "on" : ""}" data-key="sound"></div>
    </div>
    <div class="setting-row" style="flex-direction:column;align-items:flex-start;gap:8px;">
      <span class="setting-label">Notification types</span>
      <div class="type-chips">
        ${types.map(t => `<span class="type-chip ${(_notifSettings.enabled_types||[]).includes(t)?'active-'+t:''}" data-type="${t}">${NOTIF_LABELS[t]}</span>`).join("")}
      </div>
    </div>
    <div class="modal-btn-row">
      <button id="notif-settings-cancel">Cancel</button>
      <button id="notif-settings-save" style="background:var(--accent);color:#020617;border-color:var(--accent);">Save</button>
    </div>
  `;
  box.querySelector('[data-key="sound"]').onclick = function() {
    this.classList.toggle("on");
    _notifSettings.sound = this.classList.contains("on");
  };
  box.querySelectorAll(".type-chip").forEach(chip => {
    chip.onclick = function() {
      const t = this.dataset.type;
      const arr = _notifSettings.enabled_types || [];
      if (arr.includes(t)) {
        this.classList.remove("active-"+t);
        _notifSettings.enabled_types = arr.filter(x => x !== t);
      } else {
        this.classList.add("active-"+t);
        _notifSettings.enabled_types = [...arr, t];
      }
    };
  });
  const saveBtn = document.getElementById("notif-settings-save");
  if (saveBtn) saveBtn.onclick = saveNotifSettings;
  const cancelBtn = document.getElementById("notif-settings-cancel");
  if (cancelBtn) cancelBtn.onclick = () => document.getElementById("notif-settings-modal")?.classList.remove("open");
}

async function saveNotifSettings() {
  try {
    await fetch("/api/notifications/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(_notifSettings),
    });
  } catch (_) {}
  document.getElementById("notif-settings-modal")?.classList.remove("open");
}

function clearAllNotifications() {
  fetch("/api/notifications/clear", { method: "POST" }).then(() => refreshNotifLog()).catch(() => {});
}

function escHtml(s) {
  return String(s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Init ───────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  connectNotifWs();
  refreshNotifLog();

  const bell = document.getElementById("notif-bell");
  if (bell) bell.onclick = toggleNotifPanel;

  const overlay = document.getElementById("notif-overlay");
  if (overlay) overlay.onclick = closeNotifPanel;

  const closeBtn = document.getElementById("notif-panel-close");
  if (closeBtn) closeBtn.onclick = closeNotifPanel;

  const settingsBtn = document.getElementById("notif-settings-btn");
  if (settingsBtn) settingsBtn.onclick = openNotifSettings;

  const clearBtn = document.getElementById("notif-clear-btn");
  if (clearBtn) clearBtn.onclick = clearAllNotifications;

  const modal = document.getElementById("notif-settings-modal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal || e.target.id === "notif-settings-backdrop") {
        modal.classList.remove("open");
      }
    });
  }

  // Keyboard: Escape closes panel/modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeNotifPanel();
      const sm = document.getElementById("notif-settings-modal");
      if (sm) sm.classList.remove("open");
    }
  });
});
