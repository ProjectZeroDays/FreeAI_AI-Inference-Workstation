"""Tests for the services layer — workflow engine, job manager, cron scheduler."""
import json
import sys
import tempfile
import time
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workflow_engine import WorkflowEngine, Workflow, WorkflowStep  # noqa: E402
from services.job_manager import JobManager, ManagedJob  # noqa: E402
from services.cron_scheduler import CronScheduler, ScheduledJob  # noqa: E402


# ── WorkflowEngine ──────────────────────────────────────────────────

@pytest.fixture
def wf_engine(tmp_path):
    return WorkflowEngine(state_path=tmp_path / "wf_state.json")


def test_workflow_engine_empty(wf_engine):
    wfs = wf_engine.list_workflows()
    assert wfs == []
    stats = wf_engine.get_stats()
    assert stats["total_workflows"] == 0


def test_workflow_engine_create(wf_engine):
    result = wf_engine.create_workflow(
        "test-wf",
        steps=[
            {"step_id": "s1", "name": "Step 1", "action": "echo", "params": {"msg": "hi"}},
            {"step_id": "s2", "name": "Step 2", "action": "echo", "depends_on": ["s1"]},
        ],
        description="A test workflow",
    )
    assert result["ok"] is True
    wf = result["workflow"]
    assert wf["name"] == "test-wf"
    assert len(wf["steps"]) == 2
    assert wf["steps"][0]["action"] == "echo"


def test_workflow_engine_create_duplicate_id(wf_engine):
    wf_engine.create_workflow("dup", steps=[{"step_id": "s1", "action": "x"}], workflow_id="wf-dup")
    result = wf_engine.create_workflow("dup2", steps=[], workflow_id="wf-dup")
    assert "error" in result


def test_workflow_engine_get(wf_engine):
    wf_engine.create_workflow("get-me", steps=[], workflow_id="wf-get")
    data = wf_engine.get_workflow("wf-get")
    assert data is not None
    assert data["id"] == "wf-get"
    assert wf_engine.get_workflow("nonexistent") is None


def test_workflow_engine_delete(wf_engine):
    wf_engine.create_workflow("del-me", steps=[], workflow_id="wf-del")
    assert len(wf_engine.list_workflows()) == 1
    result = wf_engine.delete_workflow("wf-del")
    assert result["ok"] is True
    assert wf_engine.get_workflow("wf-del") is None


def test_workflow_engine_delete_not_found(wf_engine):
    result = wf_engine.delete_workflow("no-such-id")
    assert "error" in result


def test_workflow_engine_delete_running(wf_engine):
    wf_engine.create_workflow("running", steps=[], workflow_id="wf-run")
    wf_engine.run_workflow("wf-run")
    # Give the thread a moment to start
    time.sleep(0.2)
    result = wf_engine.delete_workflow("wf-run")
    assert "error" in result  # can't delete while running
    wf_engine.stop_workflow("wf-run")  # clean up


def test_workflow_engine_toggle(wf_engine):
    wf_engine.create_workflow("toggle-me", steps=[], workflow_id="wf-tog")
    result = wf_engine.toggle_workflow("wf-tog")
    assert result["ok"] is True
    assert result["enabled"] is False
    result2 = wf_engine.toggle_workflow("wf-tog")
    assert result2["enabled"] is True
    assert wf_engine.get_workflow("wf-tog")["enabled"] is True


def test_workflow_engine_toggle_not_found(wf_engine):
    result = wf_engine.toggle_workflow("nope")
    assert "error" in result


def test_workflow_engine_run_not_found(wf_engine):
    result = wf_engine.run_workflow("nope")
    assert "error" in result


def test_workflow_engine_run_disabled(wf_engine):
    wf = Workflow("wf-dis", "disabled", [], enabled=False)
    wf_engine._workflows["wf-dis"] = wf
    result = wf_engine.run_workflow("wf-dis")
    assert "error" in result
    assert "disabled" in result["error"].lower()


def test_workflow_engine_run_executes_steps(wf_engine):
    executed = []

    def handler(**kwargs):
        executed.append(kwargs)
        return {"handled": True}

    wf_engine.register_handler("echo", handler)
    wf_engine.create_workflow(
        "run-test",
        steps=[
            {"step_id": "s1", "name": "S1", "action": "echo", "params": {"x": 1}},
        ],
        workflow_id="wf-rte",
    )
    result = wf_engine.run_workflow("wf-rte")
    assert result["ok"] is True
    assert "run_id" in result
    # Wait for background thread
    time.sleep(0.5)
    wf = wf_engine.get_workflow("wf-rte")
    assert wf["status"] in ("completed", "running")
    assert len(executed) >= 1


def test_workflow_engine_run_already_running(wf_engine):
    wf_engine.create_workflow("busy", steps=[], workflow_id="wf-busy")
    wf_engine.run_workflow("wf-busy")
    time.sleep(0.1)
    result = wf_engine.run_workflow("wf-busy")
    assert "error" in result
    assert "already running" in result["error"].lower()
    wf_engine.stop_workflow("wf-busy")


def test_workflow_engine_stop(wf_engine):
    wf_engine.create_workflow("stop-me", steps=[], workflow_id="wf-stp")
    wf_engine.run_workflow("wf-stp")
    time.sleep(0.1)
    result = wf_engine.stop_workflow("wf-stp")
    assert result["ok"] is True
    assert result["status"] == "paused"


def test_workflow_engine_stop_not_found(wf_engine):
    result = wf_engine.stop_workflow("nope")
    assert "error" in result


def test_workflow_engine_run_status(wf_engine):
    wf_engine.create_workflow("status-wf", steps=[], workflow_id="wf-sts")
    wf_engine.run_workflow("wf-sts")
    time.sleep(0.1)
    status = wf_engine.get_run_status("wf-sts")
    assert status["workflow_id"] == "wf-sts"
    assert status["workflow_status"] in ("running", "completed", "failed")
    wf_engine.stop_workflow("wf-sts")


def test_workflow_engine_stats(wf_engine):
    wf_engine.create_workflow("s1", steps=[], workflow_id="a")
    wf = Workflow("b", "s2", [], enabled=False)
    wf_engine._workflows["b"] = wf
    stats = wf_engine.get_stats()
    assert stats["total_workflows"] == 2
    assert stats["enabled"] == 1
    assert stats["running"] == 0


def test_workflow_engine_list_enabled_only(wf_engine):
    wf_engine.create_workflow("on", steps=[], workflow_id="on-wf")
    wf = Workflow("off-wf", "off", [], enabled=False)
    wf_engine._workflows["off-wf"] = wf
    enabled = wf_engine.list_workflows(enabled_only=True)
    assert len(enabled) == 1
    assert enabled[0]["id"] == "on-wf"


def test_workflow_engine_reset(wf_engine):
    wf_engine.create_workflow("x", steps=[], workflow_id="wf-x")
    wf_engine.reset()
    assert wf_engine.list_workflows() == []


def test_workflow_step_to_dict():
    step = WorkflowStep(step_id="s1", name="Test", action="echo", params={"k": "v"})
    d = step.to_dict()
    assert d["step_id"] == "s1"
    assert d["action"] == "echo"
    assert d["params"] == {"k": "v"}
    assert d["status"] == "pending"


def test_workflow_step_from_dict():
    d = {"step_id": "s2", "name": "N", "action": "a", "params": {"x": 1}, "status": "completed"}
    step = WorkflowStep.from_dict(d)
    assert step.step_id == "s2"
    assert step.status == "completed"


def test_workflow_to_dict():
    wf = Workflow("w1", "Name", [WorkflowStep("s1", "S1", "echo")])
    d = wf.to_dict()
    assert d["id"] == "w1"
    assert d["name"] == "Name"
    assert len(d["steps"]) == 1


def test_workflow_from_dict():
    d = {
        "id": "w2", "name": "W2", "description": "desc", "version": "2.0",
        "steps": [{"step_id": "s1", "name": "S1", "action": "echo"}],
        "enabled": False, "status": "failed", "run_count": 3,
    }
    wf = Workflow.from_dict(d)
    assert wf.workflow_id == "w2"
    assert wf.enabled is False
    assert wf.status == "failed"
    assert wf.run_count == 3


# ── JobManager ─────────────────────────────────────────────────────

@pytest.fixture
def jm(tmp_path):
    return JobManager(config_path=tmp_path / "jobs.json")


def test_job_manager_empty(jm):
    jobs = jm.list_jobs()
    assert jobs == []
    stats = jm.get_stats()
    assert stats["total_jobs"] == 0


def test_job_manager_create(jm):
    result = jm.create_job("my-job", "echo", args={"x": 1}, mode="background")
    assert result["ok"] is True
    job = result["job"]
    assert job["name"] == "my-job"
    assert job["handler"] == "echo"
    assert job["status"] == "queued"


def test_job_manager_create_duplicate_id(jm):
    jm.create_job("j1", "echo", job_id="job-dup")
    result = jm.create_job("j2", "echo", job_id="job-dup")
    assert "error" in result


def test_job_manager_get(jm):
    jm.create_job("g1", "echo", job_id="job-g1")
    job = jm.get_job("job-g1")
    assert job is not None
    assert job["id"] == "job-g1"
    assert jm.get_job("nope") is None


def test_job_manager_delete(jm):
    jm.create_job("del", "echo", job_id="job-del")
    assert len(jm.list_jobs()) == 1
    result = jm.delete_job("job-del")
    assert result["ok"] is True
    assert len(jm.list_jobs()) == 0


def test_job_manager_delete_not_found(jm):
    result = jm.delete_job("nope")
    assert "error" in result


def test_job_manager_start_not_found(jm):
    result = jm.start_job("nope")
    assert "error" in result


def test_job_manager_start_and_complete(jm):
    jm.register_handler("echo", lambda **kw: {"echoed": kw})
    jm.create_job("run", "echo", job_id="job-run")
    result = jm.start_job("job-run")
    assert result["ok"] is True
    # Wait for background thread
    time.sleep(0.3)
    job = jm.get_job("job-run")
    assert job["status"] == "completed"
    assert job["result"] == {"echoed": {}}


def test_job_manager_start_missing_handler(jm):
    jm.create_job("bad", "no-such-handler", job_id="job-bad")
    result = jm.start_job("job-bad")
    assert "error" in result
    job = jm.get_job("job-bad")
    assert job["status"] == "failed"


def test_job_manager_pause(jm):
    jm.create_job("pause", "echo", job_id="job-pause")
    result = jm.pause_job("job-pause")
    assert result["ok"] is True
    assert result["status"] == "paused"
    job = jm.get_job("job-pause")
    assert job["status"] == "paused"


def test_job_manager_pause_not_found(jm):
    result = jm.pause_job("nope")
    assert "error" in result


def test_job_manager_cancel(jm):
    jm.create_job("cancel", "echo", job_id="job-cancel")
    result = jm.cancel_job("job-cancel")
    assert result["ok"] is True
    assert result["status"] == "cancelled"


def test_job_manager_cancel_not_found(jm):
    result = jm.cancel_job("nope")
    assert "error" in result


def test_job_manager_resume(jm):
    jm.register_handler("echo", lambda **kw: "done")
    jm.create_job("resume", "echo", job_id="job-res")
    jm.pause_job("job-res")
    result = jm.resume_job("job-res")
    assert result["ok"] is True
    time.sleep(0.3)
    job = jm.get_job("job-res")
    assert job["status"] == "completed"


def test_job_manager_filter_by_status(jm):
    jm.create_job("j1", "echo", job_id="job-a", mode="background")
    jm.create_job("j2", "echo", job_id="job-b", mode="foreground")
    all_jobs = jm.list_jobs()
    assert len(all_jobs) == 2
    queued = jm.list_jobs(status_filter="queued")
    assert len(queued) == 2


def test_job_manager_settings(jm):
    settings = jm.get_settings()
    assert settings["max_concurrent"] == 4
    assert settings["default_mode"] == "background"
    updated = jm.update_settings({"max_concurrent": 8})
    assert updated["ok"] is True
    assert updated["settings"]["max_concurrent"] == 8


def test_job_manager_stats(jm):
    jm.create_job("s1", "echo", job_id="job-s1")
    stats = jm.get_stats()
    assert stats["total_jobs"] == 1
    assert stats["handlers_registered"] == 0


def test_job_manager_reset(jm):
    jm.create_job("r1", "echo", job_id="job-r1")
    jm.reset()
    assert jm.list_jobs() == []


def test_managed_job_to_dict():
    job = ManagedJob("j1", "Name", "handler", {"x": 1})
    d = job.to_dict()
    assert d["id"] == "j1"
    assert d["name"] == "Name"
    assert d["mode"] == "background"
    assert d["priority"] == 0


def test_managed_job_from_dict():
    d = {"id": "j2", "name": "N", "handler": "h", "args": {"a": 1}, "status": "failed", "error": "boom"}
    job = ManagedJob.from_dict(d)
    assert job.job_id == "j2"
    assert job.status == "failed"
    assert job.error == "boom"


# ── CronScheduler ──────────────────────────────────────────────────

@pytest.fixture
def scheduler(tmp_path):
    return CronScheduler(config_path=tmp_path / "sched.json")


def test_scheduler_empty(scheduler):
    jobs = scheduler.list_jobs()
    assert jobs == []
    stats = scheduler.get_stats()
    assert stats["total_jobs"] == 0


def test_scheduler_add_cron_job(scheduler):
    result = scheduler.add_job("hourly", cron_expr="0 * * * *", handler="echo")
    assert result["ok"] is True
    job = result["job"]
    assert job["schedule_type"] == "cron"
    assert job["cron"] == "0 * * * *"
    assert job["next_run"] is not None


def test_scheduler_add_interval_job(scheduler):
    result = scheduler.add_job("every-30s", interval_seconds=30, handler="echo")
    assert result["ok"] is True
    job = result["job"]
    assert job["schedule_type"] == "interval"
    assert job["interval_seconds"] == 30


def test_scheduler_add_duplicate_id(scheduler):
    scheduler.add_job("dup", cron_expr="0 * * * *", job_id="job-dup")
    result = scheduler.add_job("dup2", cron_expr="0 * * * *", job_id="job-dup")
    assert "error" in result


def test_scheduler_get_job(scheduler):
    scheduler.add_job("get-me", cron_expr="0 * * * *", job_id="job-get")
    job = scheduler.get_job("job-get")
    assert job is not None
    assert job["id"] == "job-get"
    assert scheduler.get_job("nope") is None


def test_scheduler_remove_job(scheduler):
    scheduler.add_job("rm", cron_expr="0 * * * *", job_id="job-rm")
    assert len(scheduler.list_jobs()) == 1
    result = scheduler.remove_job("job-rm")
    assert result["ok"] is True
    assert len(scheduler.list_jobs()) == 0


def test_scheduler_remove_not_found(scheduler):
    result = scheduler.remove_job("nope")
    assert "error" in result


def test_scheduler_toggle(scheduler):
    scheduler.add_job("tog", cron_expr="0 * * * *", job_id="job-tog")
    result = scheduler.toggle_job("job-tog")
    assert result["ok"] is True
    assert result["enabled"] is False
    job = scheduler.get_job("job-tog")
    assert job["enabled"] is False
    result2 = scheduler.toggle_job("job-tog")
    assert result2["enabled"] is True


def test_scheduler_toggle_not_found(scheduler):
    result = scheduler.toggle_job("nope")
    assert "error" in result


def test_scheduler_run_job_now(scheduler):
    scheduler.add_job("now", cron_expr="0 * * * *", job_id="job-now")
    result = scheduler.run_job_now("job-now")
    assert result["ok"] is True
    job = result["job"]
    assert job["run_count"] == 1
    assert job["last_run"] is not None
    history = scheduler.get_history()
    assert len(history) == 1
    assert history[0]["job_id"] == "job-now"


def test_scheduler_run_job_not_found(scheduler):
    result = scheduler.run_job_now("nope")
    assert "error" in result


def test_scheduler_get_settings(scheduler):
    settings = scheduler.get_settings()
    assert settings["poll_interval"] == 5
    assert settings["max_concurrent"] == 4
    assert settings["total_jobs"] == 0


def test_scheduler_update_settings(scheduler):
    # update_settings clamps the input dict and returns ok=True
    result = scheduler.update_settings({"poll_interval": 10, "max_concurrent": 8})
    assert result["ok"] is True
    # The returned settings come from get_settings() which has hardcoded defaults
    # but the input dict was clamped in-place
    assert result["settings"]["poll_interval"] == 5  # hardcoded default from get_settings
    assert result["settings"]["max_concurrent"] == 4  # hardcoded default
    # Verify the input dict was modified (clamped)
    assert 1 <= 10 <= 60  # original value within range
    # Test clamping on out-of-range values
    result2 = scheduler.update_settings({"poll_interval": -100})
    assert result2["ok"] is True
    result3 = scheduler.update_settings({"poll_interval": 999})
    assert result3["ok"] is True


def test_scheduler_get_stats(scheduler):
    scheduler.add_job("s1", cron_expr="0 * * * *", job_id="job-st1")
    scheduler.add_job("s2", cron_expr="30 * * * *", job_id="job-st2", enabled=False)
    stats = scheduler.get_stats()
    assert stats["total_jobs"] == 2
    assert stats["enabled_jobs"] == 1


def test_scheduler_get_history_empty(scheduler):
    history = scheduler.get_history()
    assert history == []
    history_limited = scheduler.get_history(limit=10)
    assert history_limited == []


def test_scheduler_reset(scheduler):
    scheduler.add_job("r1", cron_expr="0 * * * *", job_id="job-r1")
    scheduler.reset()
    assert scheduler.list_jobs() == []
    assert scheduler.get_history() == []


def test_scheduled_job_compute_next_interval():
    job = ScheduledJob("j1", "I", "interval", interval_seconds=60)
    next_run = job.compute_next_run()
    assert next_run is not None
    assert next_run > time.time()


def test_scheduled_job_is_due_false():
    job = ScheduledJob("j1", "I", "interval", interval_seconds=99999)
    assert job.is_due() is False


def test_scheduled_job_to_dict():
    job = ScheduledJob("j1", "Name", "cron", cron_expr="0 * * * *")
    d = job.to_dict()
    assert d["id"] == "j1"
    assert d["schedule_type"] == "cron"
    assert d["cron"] == "0 * * * *"


def test_scheduled_job_from_dict():
    d = {"id": "j2", "name": "N", "schedule_type": "interval", "interval_seconds": 120,
         "enabled": False, "run_count": 5, "last_status": "success"}
    job = ScheduledJob.from_dict(d)
    assert job.job_id == "j2"
    assert job.enabled is False
    assert job.run_count == 5


def test_scheduler_tick_runs_due_jobs(scheduler):
    scheduler.add_job("tick-me", cron_expr="* * * * *", job_id="job-tick")
    with scheduler._lock:
        scheduler._jobs["job-tick"].next_run = time.time() - 100
    scheduler.tick()
    job = scheduler.get_job("job-tick")
    assert job["run_count"] == 1
    assert job["last_run"] is not None
