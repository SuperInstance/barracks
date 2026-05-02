"""Tests for task.py"""
import pytest
from cocapn_barracks.task import Task, TaskStatus, TaskResult


class TestTaskResult:
    def test_success_property_true_when_no_error(self):
        result = TaskResult(output={"data": 42})
        assert result.success is True

    def test_success_property_false_when_error(self):
        result = TaskResult(error="Something went wrong")
        assert result.success is False

    def test_result_with_duration(self):
        result = TaskResult(output="done", duration_ms=1500.5)
        assert result.duration_ms == 1500.5

    def test_result_metadata(self):
        result = TaskResult(output="ok", metadata={"key": "value"})
        assert result.metadata["key"] == "value"


class TestTask:
    def test_task_creation_assigns_uuid(self):
        task = Task(name="test")
        assert task.id is not None
        assert len(task.id) == 36

    def test_task_default_status_pending(self):
        task = Task(name="test")
        assert task.status == TaskStatus.PENDING

    def test_task_with_custom_id(self):
        task = Task(id="custom-id", name="test")
        assert task.id == "custom-id"

    def test_task_with_payload(self):
        task = Task(name="compute", payload={"x": 10, "y": 20})
        assert task.payload["x"] == 10

    def test_mark_running_sets_status_and_timestamp(self):
        task = Task(name="test")
        task.mark_running()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None

    def test_mark_completed_sets_output_and_duration(self):
        task = Task(name="test")
        task.mark_running()
        task.mark_completed(output="result", extra="info")
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.result.output == "result"
        assert task.result.metadata["extra"] == "info"

    def test_mark_failed_sets_error(self):
        task = Task(name="test")
        task.mark_running()
        task.mark_failed("division by zero")
        assert task.status == TaskStatus.FAILED
        assert "division by zero" in task.result.error

    def test_retry_increments_count_and_resets_status(self):
        task = Task(name="test", max_retries=3)
        assert task.retries == 0
        result = task.retry()
        assert result is True
        assert task.retries == 1
        assert task.status == TaskStatus.PENDING

    def test_retry_returns_false_when_max_exceeded(self):
        task = Task(name="test", max_retries=2)
        task.retry()
        task.retry()
        result = task.retry()
        assert result is False

    def test_duration_ms_calculated_when_complete(self):
        task = Task(name="test")
        task.mark_running()
        task.mark_completed()
        assert task.duration_ms > 0

    def test_duration_ms_zero_when_not_started(self):
        task = Task(name="test")
        assert task.duration_ms == 0

    def test_add_tag(self):
        task = Task(name="test")
        task.add_tag("important")
        assert "important" in task.tags

    def test_add_tag_no_duplicate(self):
        task = Task(name="test")
        task.add_tag("important")
        task.add_tag("important")
        assert len(task.tags) == 1

    def test_has_tag(self):
        task = Task(name="test", tags=["urgent", "api"])
        assert task.has_tag("urgent") is True
        assert task.has_tag("slow") is False

    def test_task_priority_default_zero(self):
        task = Task(name="test")
        assert task.priority == 0

    def test_task_created_at_timestamp(self):
        task = Task(name="test")
        assert task.created_at is not None