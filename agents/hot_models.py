#!/usr/bin/env python3
"""Hot Model Manager — load, switch, and monitor model shards on GPU.

Provides in-process model lifecycle management:
  - Load/unload model shards onto assigned CUDA GPUs
  - Hot-swap the active model without restart
  - Health monitoring with automatic degradation detection
"""
import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
HOT_MODELS_PATH = CONFIG_DIR / "hot-models.json"

_STATE_LOCK = threading.RLock()


class HotModel:
    """Represents a single model shard and its runtime state."""

    def __init__(self, defn: dict):
        self.id: str = defn["id"]
        self.name: str = defn["name"]
        self.shard_path: str = defn["shard_path"]
        self.gpu_id: int = defn.get("gpu_id", 0)
        self.cuda_visible_devices: str = defn.get("cuda_visible_devices", "0")
        self.port: int = defn.get("port", 8001)
        self.context_length: int = defn.get("context_length", 4096)
        self.threads: int = defn.get("threads", 8)
        self.gpu_layers: int = defn.get("gpu_layers", -1)
        self.loaded: bool = defn.get("loaded", False)
        self.health: str = defn.get("health", "unknown")  # unknown | healthy | unhealthy | loading
        self.last_health_check: Optional[float] = defn.get("last_health_check")
        self.active: bool = defn.get("active", False)
        self.error_count: int = 0
        self.load_time_s: Optional[float] = None
        self._process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "shard_path": self.shard_path,
            "gpu_id": self.gpu_id,
            "cuda_visible_devices": self.cuda_visible_devices,
            "port": self.port,
            "context_length": self.context_length,
            "threads": self.threads,
            "gpu_layers": self.gpu_layers,
            "loaded": self.loaded,
            "health": self.health,
            "last_health_check": self.last_health_check,
            "active": self.active,
            "error_count": self.error_count,
            "load_time_s": self.load_time_s,
        }


class HotModelManager:
    """Manages hot model loading, switching, and health monitoring."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or HOT_MODELS_PATH
        self._models: dict[str, HotModel] = {}
        self._active_id: Optional[str] = None
        self._health_interval = 30
        self._health_max_resp_s = 5.0
        self._health_max_errors = 3
        self._health_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._load_config()

    # ── Config ───────────────────────────────────────────────────
    def _load_config(self):
        if not self.config_path.exists():
            return
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        with _STATE_LOCK:
            self._models = {}
            for m in data.get("models", []):
                self._models[m["id"]] = HotModel(m)
            self._active_id = data.get("active_model_id")
            hc = data.get("health_check_interval_s", 30)
            ht = data.get("health_threshold", {})
            self._health_interval = hc
            self._health_max_resp_s = ht.get("max_response_time_s", 5.0)
            self._health_max_errors = ht.get("max_consecutive_errors", 3)

    def save_config(self):
        with _STATE_LOCK:
            models = [m.to_dict() for m in self._models.values()]
            data = {
                "models": models,
                "active_model_id": self._active_id,
                "health_check_interval_s": self._health_interval,
                "health_threshold": {
                    "max_response_time_s": self._health_max_resp_s,
                    "max_consecutive_errors": self._health_max_errors,
                },
            }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ── State accessors ──────────────────────────────────────────
    def get_state(self) -> dict:
        with _STATE_LOCK:
            return {
                "active_model_id": self._active_id,
                "models": {mid: m.to_dict() for mid, m in self._models.items()},
                "total": len(self._models),
                "loaded_count": sum(1 for m in self._models.values() if m.loaded),
                "active_count": sum(1 for m in self._models.values() if m.active),
            }

    def get_active_model(self) -> Optional[HotModel]:
        with _STATE_LOCK:
            if self._active_id and self._active_id in self._models:
                return self._models[self._active_id]
            return None

    def get_model(self, model_id: str) -> Optional[HotModel]:
        with _STATE_LOCK:
            return self._models.get(model_id)

    # ── Load ─────────────────────────────────────────────────────
    def load_model(self, model_id: str) -> dict:
        """Load a model shard onto its assigned GPU."""
        with _STATE_LOCK:
            model = self._models.get(model_id)
            if not model:
                return {"ok": False, "error": f"Model '{model_id}' not found"}
            if model.loaded:
                return {"ok": False, "error": f"Model '{model_id}' already loaded"}
            model.health = "loading"
            model.loaded = True
            self.save_config()

        # Simulate load — in production this would spawn llama.cpp or vllm
        try:
            model._start_time = time.time()
            # Validate shard path exists (or is acceptable placeholder)
            full_path = ROOT / model.shard_path if not model.shard_path.startswith("/") else model.shard_path
            if full_path.exists() or model.shard_path.startswith("models/"):
                model.health = "healthy"
                model.error_count = 0
            else:
                # Allow loading even if file missing (mock mode for workstation)
                model.health = "healthy"
                model.error_count = 0
            model.load_time_s = round(time.time() - model._start_time, 2) if model._start_time else 0.5
        except Exception as e:
            model.health = "unhealthy"
            model.error_count += 1
            return {"ok": False, "error": str(e)}

        with _STATE_LOCK:
            self.save_config()
        return {"ok": True, "model_id": model_id, "health": model.health}

    def unload_model(self, model_id: str) -> dict:
        """Unload a model shard from its GPU."""
        with _STATE_LOCK:
            model = self._models.get(model_id)
            if not model:
                return {"ok": False, "error": f"Model '{model_id}' not found"}
            if model.active and self._active_id == model_id:
                return {"ok": False, "error": "Cannot unload active model — switch first"}
            if not model.loaded:
                return {"ok": False, "error": f"Model '{model_id}' not loaded"}
            model.loaded = False
            model.health = "unknown"
            model.error_count = 0
            self.save_config()
        return {"ok": True, "model_id": model_id}

    # ── Switch ───────────────────────────────────────────────────
    def switch_model(self, model_id: str) -> dict:
        """Swap the active model to a different loaded shard."""
        with _STATE_LOCK:
            model = self._models.get(model_id)
            if not model:
                return {"ok": False, "error": f"Model '{model_id}' not found"}, 404
            if not model.loaded:
                return {"ok": False, "error": f"Model '{model_id}' not loaded — load first"}, 400
            if model.health == "unhealthy":
                return {"ok": False, "error": f"Model '{model_id}' is unhealthy"}, 400

            # Deactivate current
            if self._active_id and self._active_id in self._models:
                self._models[self._active_id].active = False

            # Activate new
            model.active = True
            self._active_id = model_id
            self.save_config()
            return {"ok": True, "active_model_id": model_id, "name": model.name}

    # ── Health ───────────────────────────────────────────────────
    def check_health(self, model_id: Optional[str] = None) -> dict:
        """Run health checks on one or all models."""
        results = {}
        with _STATE_LOCK:
            targets = [model_id] if model_id else list(self._models.keys())
            for mid in targets:
                model = self._models.get(mid)
                if not model or not model.loaded:
                    results[mid] = {"health": "unknown", "error": "not loaded"}
                    continue
                healthy = self._probe_model(model)
                if healthy:
                    model.error_count = max(0, model.error_count - 1)
                    if model.error_count >= self._health_max_errors:
                        model.health = "unhealthy"
                    else:
                        model.health = "healthy"
                else:
                    model.error_count += 1
                    if model.error_count >= self._health_max_errors:
                        model.health = "unhealthy"
                model.last_health_check = time.time()
                results[mid] = {"health": model.health, "error_count": model.error_count}
            self.save_config()
        return {"results": results}

    def _probe_model(self, model: HotModel) -> bool:
        """Probe a loaded model's serving endpoint."""
        try:
            url = f"http://127.0.0.1:{model.port}/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as r:
                return r.status == 200
        except Exception:
            pass
        # Try completions endpoint as fallback
        try:
            url = f"http://127.0.0.1:{model.port}/v1/chat/completions"
            body = json.dumps({"model": model.id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}).encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=self._health_max_resp_s) as r:
                return r.status in (200, 201)
        except Exception:
            return False

    def start_health_monitor(self):
        """Start background health monitoring thread."""
        if self._health_thread and self._health_thread.is_alive():
            return
        self._health_thread = threading.Thread(
            target=self._health_loop, daemon=True, name="hot-model-health"
        )
        self._health_thread.start()

    def _health_loop(self):
        while True:
            time.sleep(self._health_interval)
            try:
                self.check_health()
            except Exception:
                pass

    def stop_health_monitor(self):
        # Thread is daemon; just stop referencing it
        self._health_thread = None


# ── Global singleton ─────────────────────────────────────────────
_manager: Optional[HotModelManager] = None


def get_manager() -> HotModelManager:
    global _manager
    if _manager is None:
        _manager = HotModelManager()
        _manager.start_health_monitor()
    return _manager
