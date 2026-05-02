"""Tests for queue.py"""
import pytest
from cocapn_barracks.queue import TaskQueue
from cocapn_barracks.task import Task, TaskStatus


class TestTaskQueue:
    def test_queue_starts_empty(self):
        q = TaskQueue()
        assert q.is_empty() is True
        assert q.size() == 0

    def test_enqueue_adds_task(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        assert q.size() == 1
        assert q.is_empty() is False

    def test_dequeue_returns_and_removes_task(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        dequeued = q.dequeue()
        assert dequeued is task
        assert q.size() == 0
        assert q.running_count() == 1

    def test_dequeue_returns_none_when_empty(self):
        q = TaskQueue()
        result = q.dequeue()
        assert result is None

    def test_peek_shows_next_without_removing(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        peeked = q.peek()
        assert peeked is task
        assert q.size() == 1

    def test_peek_returns_none_when_empty(self):
        q = TaskQueue()
        assert q.peek() is None

    def test_requeue_puts_task_back(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        q.dequeue()
        q.requeue(task)
        assert q.size() == 1
        assert q.running_count() == 0

    def test_mark_completed_moves_to_completed_list(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        q.dequeue()
        q.mark_completed(task)
        assert q.running_count() == 0
        assert q.completed_count() == 1

    def test_mark_failed_moves_to_failed_list(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        q.dequeue()
        q.mark_failed(task)
        assert q.running_count() == 0
        assert q.failed_count() == 1

    def test_enqueue_many_adds_multiple_tasks(self):
        q = TaskQueue()
        tasks = [Task(name=f"job{i}") for i in range(5)]
        q.enqueue_many(tasks)
        assert q.size() == 5

    def test_get_task_finds_in_pending(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        found = q.get_task(task.id)
        assert found is task

    def test_get_task_finds_in_running(self):
        q = TaskQueue()
        task = Task(name="job1")
        q.enqueue(task)
        q.dequeue()
        found = q.get_task(task.id)
        assert found is task

    def test_get_task_returns_none_when_not_found(self):
        q = TaskQueue()
        found = q.get_task("nonexistent-id")
        assert found is None

    def test_clear_removes_all_tasks(self):
        q = TaskQueue()
        q.enqueue_many([Task(name=f"job{i}") for i in range(3)])
        q.clear()
        assert q.is_empty() is True

    def test_get_stats(self):
        q = TaskQueue()
        stats = q.get_stats()
        assert stats["pending"] == 0
        assert stats["total"] == 0

        q.enqueue(Task(name="j1"))
        q.enqueue(Task(name="j2"))
        t = q.dequeue()
        q.mark_completed(t)

        stats = q.get_stats()
        assert stats["pending"] == 1
        assert stats["completed"] == 1

    def test_filter_by_tag(self):
        q = TaskQueue()
        t1 = Task(name="t1", tags=["fast"])
        t2 = Task(name="t2", tags=["slow"])
        t3 = Task(name="t3", tags=["fast", "api"])
        q.enqueue_many([t1, t2, t3])

        fast_tasks = q.filter_by_tag("fast")
        assert len(fast_tasks) == 2

    def test_all_tasks_returns_all_states(self):
        q = TaskQueue()
        t1 = Task(name="j1")
        t2 = Task(name="j2")
        q.enqueue(t1)
        q.enqueue(t2)
        all_t = q.all_tasks()
        assert len(all_t) == 2
        assert t1 in all_t
        assert t2 in all_t