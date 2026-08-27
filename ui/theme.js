// Theme toggle (ROADMAP 5) — persists to localStorage, respects prefers-color-scheme
export function initTheme() {
  const saved = localStorage.getItem("freeai-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  const btn = document.getElementById("theme-toggle");
  if (btn) btn.onclick = () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("freeai-theme", next);
  };
}
