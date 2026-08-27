"""Scheduler API tests."""
import sys
import os

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    dash.app.config["TESTING"] = True
    # Clear scheduler jobs before each test
    with dash._scheduler_lock:
        dash._scheduler_jobs.clear()
    with dash.app.test_client() as c:
        yield c
    with dash._scheduler_lock:
        dash._scheduler_jobs.clear()


def test_scheduler_list_empty(client):
    res = client.get("/api/scheduler/jobs")
    assert res.status_code == 200
    assert res.get_json() == []


def test_scheduler_info(client):
    res = client.get("/api/scheduler")
    assert res.status_code == 200
    body = res.get_json()
    assert "config" in body
    assert "jobs" in body
    assert "running" in body
    assert body["running"] == 0


def test_create_job(client):
    res = client.post("/api/scheduler/jobs",
                      json={"name": "daily-report", "cron": "0 8 * * *",
                            "handler": "report.generate"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["job"]["name"] == "daily-report"
    assert body["job"]["cron"] == "0 8 * * *"
    assert body["job"]["enabled"] is True
    assert "id" in body["job"]


def test_create_job_defaults(client):
    res = client.post("/api/scheduler/jobs", json={})
    body = res.get_json()
    assert body["job"]["name"] == "untitled"
    assert body["job"]["cron"] == "0 0 * * *"


def test_list_jobs_after_create(client):
    client.post("/api/scheduler/jobs", json={"name": "job-a"})
    res = client.get("/api/scheduler/jobs")
    jobs = res.get_json()
    assert len(jobs) == 1
    assert jobs[0]["name"] == "job-a"


def test_toggle_job(client):
    create = client.post("/api/scheduler/jobs", json={"name": "togglable"})
    jid = create.get_json()["job"]["id"]
    res = client.post(f"/api/scheduler/jobs/{jid}/toggle")
    body = res.get_json()
    assert body["ok"] is True
    assert body["enabled"] is False
    # Toggle back
    res2 = client.post(f"/api/scheduler/jobs/{jid}/toggle")
    assert res2.get_json()["enabled"] is True


def test_toggle_unknown_job(client):
    res = client.post("/api/scheduler/jobs/fake-id/toggle")
    assert res.status_code == 404


def test_delete_job(client):
    create = client.post("/api/scheduler/jobs", json={"name": "delete-me"})
    jid = create.get_json()["job"]["id"]
    res = client.delete(f"/api/scheduler/jobs/{jid}")
    assert res.get_json()["deleted"] == 1
    res2 = client.get("/api/scheduler/jobs")
    assert res2.get_json() == []


def test_delete_unknown_job(client):
    res = client.delete("/api/scheduler/jobs/fake-id")
    assert res.get_json()["deleted"] == 0


def test_multiple_jobs(client):
    for i in range(3):
        client.post("/api/scheduler/jobs", json={"name": f"job-{i}"})
    res = client.get("/api/scheduler/jobs")
    assert len(res.get_json()) == 3


def test_scheduler_running_count(client):
    """running count reflects jobs with status=='running'."""
    with dash._scheduler_lock:
        dash._scheduler_jobs.extend(
            [{"id": "r1", "name": "r", "status": "running"},
             {"id": "r2", "name": "r2", "status": "running"},
             {"id": "q1", "name": "q", "status": "queued"}])
    res = client.get("/api/scheduler")
    body = res.get_json()
    assert body["running"] == 2
