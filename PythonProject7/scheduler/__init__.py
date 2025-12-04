"""
轻量级多任务调度器
实现目标2-4：设计模式、代码审查、AI-log记录
"""

from .core import ITask, ScheduledTask
from .strategies import ExecutionStrategy, OnceStrategy, PeriodicStrategy
from .observers import TaskObserver, ConsoleObserver
from .factory import TaskFactory
from .scheduler import TaskScheduler
from .logger import LogWriter
from .tasks import (
    FileBackupTask,
    MatrixMultiplyTask,
    HttpGetTask,
    ReminderTask,
    RandomStatsTask
)

__all__ = [
    'ITask',
    'ScheduledTask',
    'ExecutionStrategy',
    'OnceStrategy',
    'PeriodicStrategy',
    'TaskObserver',
    'ConsoleObserver',
    'TaskFactory',
    'TaskScheduler',
    'LogWriter',
    'FileBackupTask',
    'MatrixMultiplyTask',
    'HttpGetTask',
    'ReminderTask',
    'RandomStatsTask',
]

__version__ = '1.0.0'