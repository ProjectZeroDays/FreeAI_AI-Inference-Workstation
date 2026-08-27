import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("MOCK_LLM", "1")
os.environ.setdefault("CACHE_ENABLED", "1")
os.environ.pop("ROUTER_API_KEY", None)

sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "router"))
sys.path.insert(0, os.path.join(ROOT, "workflow"))
