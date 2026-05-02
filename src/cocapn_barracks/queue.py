"""Task queue management for barracks."""
from collections import deque
from typing import List, Optional
from .task import Task, TaskStatus


class TaskQueue:
    def __init__(self):
        self._pending: deque[Task] = deque()
        self._running: List[Task] = []
        self._completed: List[Task] = []
        self._failed: List[Task] = []

    def enqueue(self, task: Task) -> None:
        self._pending.append(task)

    def enqueue_many(self, tasks: List[Task]) -> None:
        for task in tasks:
            self.enqueue(task)

    def dequeue(self) -> Optional[Task]:
        if self._pending:
            task = self._pending.popleft()
            self._running.append(task)
            return task
        return None

    def requeue(self, task: Task) -> None:
        if task in self._running:
            self._running.remove(task)
        task.status = TaskStatus.PENDING
        self._pending.append(task)

    def mark_completed(self, task: Task) -> None:
        if task in self._running:
            self._running.remove(task)
        self._completed.append(task)

    def mark_failed(self, task: Task) -> None:
        if task in self._running:
            self._running.remove(task)
        self._failed.append(task)

    def peek(self) -> Optional[Task]:
        return self._pending[0] if self._pending else None

    def size(self) -> int:
        return len(self._pending)

    def running_count(self) -> int:
        return len(self._running)

    def completed_count(self) -> int:
        return len(self._completed)

    def failed_count(self) -> int:
        return len(self._failed)

    def is_empty(self) -> bool:
        return len(self._pending) == 0 and len(self._running) == 0

    def get_task(self, task_id: str) -> Optional[Task]:
        for task in list(self._pending) + self._running + self._completed + self._failed:
            if task.id == task_id:
                return task
        return None

    def clear(self) -> None:
        self._pending.clear()
        self._running.clear()
        self._completed.clear()
        self._failed.clear()

    def get_stats(self) -> dict:
        return {
            "pending": len(self._pending),
            "running": len(self._running),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "total": len(self._pending) + len(self._running) + len(self._completed) + len(self._failed),
        }

    def filter_by_tag(self, tag: str) -> List[Task]:
        return [t for t in self.all_tasks() if t.has_tag(tag)]

    def all_tasks(self) -> List[Task]:
        return list(self._pending) + list(self._running) + list(self._completed) + list(self._failed)