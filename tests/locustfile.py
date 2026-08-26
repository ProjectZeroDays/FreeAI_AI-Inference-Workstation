"""Locust load test (ROADMAP 9)."""
from locust import HttpUser, task, between
class FreeAIUser(HttpUser):
    wait_time = between(1, 3)
    @task(3)
    def route(self):
        self.client.post("/route", json={"prompt": "refactor this function", "max_tokens": 128})
    @task(1)
    def health(self):
        self.client.get("/health")
# Run: locust -f tests/locustfile.py --host http://localhost:8010
