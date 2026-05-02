"""Cocapn Barracks - Task execution and queue management for agent fleets."""

__version__ = "0.2.0"
__author__ = "Casey Digennaro"
__license__ = "MIT"

from .task import Task, TaskStatus, TaskResult
from .queue import TaskQueue
from .executor import Executor

__all__ = ["Task", "TaskStatus", "TaskResult", "TaskQueue", "Executor"]