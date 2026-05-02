"""Tests for executor.py"""
import pytest
from cocapn_barracks.executor import Executor
from cocapn_barracks.task import Task, TaskStatus


class TestExecutor:
    def test_executor_has_default_worker_id(self):
        ex = Executor()
        assert ex.worker_id == "worker-1"

    def test_executor_custom_worker_id(self):
        ex = Executor(worker_id="my-worker")
        assert ex.worker_id == "my-worker"

    def test_register_adds_handler(self):
        ex = Executor()
        ex.register("echo", lambda x: x)
        assert ex.has_handler("echo") is True

    def test_has_handler_false_for_unregistered(self):
        ex = Executor()
        assert ex.has_handler("unknown") is False

    def test_execute_runs_handler_and_marks_completed(self):
        ex = Executor()
        ex.register("double", lambda x: x * 2)

        task = Task(name="double", payload=21)
        result = ex.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result.output == 42

    def test_execute_without_handler_marks_completed(self):
        ex = Executor()
        task = Task(name="unknown_task")
        result = ex.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result.output["worker"] == "worker-1"

    def test_execute_catches_exception_and_marks_failed(self):
        ex = Executor()
        ex.register("fail", lambda x: 1/0)

        task = Task(name="fail", payload=0)
        result = ex.execute(task)

        assert result.status == TaskStatus.FAILED
        assert "division by zero" in result.result.error

    def test_execute_many_processes_all_tasks(self):
        ex = Executor()
        ex.register("add", lambda x: x + 1)

        tasks = [Task(name="add", payload=i) for i in range(3)]
        results = ex.execute_many(tasks)

        assert len(results) == 3
        assert results[0].result.output == 1
        assert results[1].result.output == 2
        assert results[2].result.output == 3

    def test_tasks_executed_counter(self):
        ex = Executor()
        assert ex.tasks_executed == 0

        task = Task(name="test")
        ex.execute(task)
        assert ex.tasks_executed == 1

        ex.execute(Task(name="test2"))
        assert ex.tasks_executed == 2

    def test_execute_sets_started_at(self):
        ex = Executor()
        task = Task(name="test")
        ex.execute(task)
        assert task.started_at is not None

    def test_execute_sets_duration(self):
        ex = Executor()
        task = Task(name="test")
        ex.execute(task)
        assert task.result.duration_ms > 0

    def test_execute_with_dict_payload(self):
        ex = Executor()
        ex.register("process", lambda x: x["value"] * 3)

        task = Task(name="process", payload={"value": 10})
        result = ex.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result.output == 30

    def test_execute_with_string_payload(self):
        ex = Executor()
        ex.register("upper", lambda x: x.upper())

        task = Task(name="upper", payload="hello")
        result = ex.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result.output == "HELLO"

    def test_multiple_handlers_different_types(self):
        ex = Executor()
        ex.register("add", lambda x: x + 1)
        ex.register("multiply", lambda x: x * 2)

        t1 = Task(name="add", payload=5)
        t2 = Task(name="multiply", payload=5)

        r1 = ex.execute(t1)
        r2 = ex.execute(t2)

        assert r1.result.output == 6
        assert r2.result.output == 10