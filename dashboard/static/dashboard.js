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

async function fetchStatus() {
  const gpuUtil = document.getElementById("gpu-util");
  const gpuMem = document.getElementById("gpu-mem");
  const servicesList = document.getElementById("services-list");
  const ts = document.getElementById("timestamp");

  try {
    const res = await fetch("/api/status");
    const json = await res.json();

    gpuUtil.textContent = `Utilization: ${json.gpu.utilization}%`;
    updateChart(json.gpu.utilization);
    gpuMem.textContent =
      `Memory: ${json.gpu.memory_used} / ${json.gpu.memory_total} MiB`;

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

document.addEventListener("DOMContentLoaded", () => {
  fetchStatus();
  setInterval(fetchStatus, 5000);
});
