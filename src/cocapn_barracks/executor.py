"""Task executor for barracks."""
from typing import Callable, Optional
from .task import Task, TaskStatus


class Executor:
    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or "worker-1"
        self._handlers: dict[str, Callable] = {}
        self._tasks_executed = 0

    def register(self, task_type: str, handler: Callable) -> None:
        self._handlers[task_type] = handler

    def execute(self, task: Task) -> Task:
        task.mark_running()
        handler = self._handlers.get(task.name)
        if handler:
            try:
                result = handler(task.payload)
                task.mark_completed(output=result)
            except Exception as e:
                task.mark_failed(str(e))
        else:
            task.mark_completed(output={"status": "no handler", "worker": self.worker_id})
        self._tasks_executed += 1
        return task

    def execute_many(self, tasks: list[Task]) -> list[Task]:
        return [self.execute(task) for task in tasks]

    @property
    def tasks_executed(self) -> int:
        return self._tasks_executed

    def has_handler(self, task_name: str) -> bool:
        return task_name in self._handlers