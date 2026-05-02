"""Task model for barracks."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    payload: Any = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    priority: int = 0
    retries: int = 0
    max_retries: int = 3
    tags: list = field(default_factory=list)

    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def mark_completed(self, output: Any = None, **metadata) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        duration = (self.completed_at - self.started_at).total_seconds() * 1000 if self.started_at else 0
        self.result = TaskResult(output=output, duration_ms=duration, metadata=metadata)

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        duration = (self.completed_at - self.started_at).total_seconds() * 1000 if self.started_at else 0
        self.result = TaskResult(error=error, duration_ms=duration)

    def retry(self) -> bool:
        if self.retries < self.max_retries:
            self.retries += 1
            self.status = TaskStatus.PENDING
            self.result = None
            return True
        return False

    @property
    def duration_ms(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return 0.0

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags