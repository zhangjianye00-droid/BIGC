"""
策略模式 - 各种ITask实现，运行时切换具体任务行为
"""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import ScheduledTask


class ExecutionStrategy(ABC):
    """执行策略抽象基类"""

    @abstractmethod
    def should_execute(self, scheduled_task: 'ScheduledTask') -> bool:
        """判断任务是否应该执行"""
        pass

    @abstractmethod
    def update_next_run(self, scheduled_task: 'ScheduledTask') -> None:
        """更新下次执行时间"""
        pass


class OnceStrategy(ExecutionStrategy):
    """一次性执行策略"""

    def should_execute(self, scheduled_task: 'ScheduledTask') -> bool:
        return not scheduled_task.executed and time.time() >= scheduled_task.run_time

    def update_next_run(self, scheduled_task: 'ScheduledTask') -> None:
        scheduled_task.executed = True


class PeriodicStrategy(ExecutionStrategy):
    """周期性执行策略"""

    def __init__(self, interval: float):
        self.interval = interval

    def should_execute(self, scheduled_task: 'ScheduledTask') -> bool:
        return time.time() >= scheduled_task.run_time

    def update_next_run(self, scheduled_task: 'ScheduledTask') -> None:
        scheduled_task.run_time = time.time() + self.interval
        scheduled_task.is_periodic = True