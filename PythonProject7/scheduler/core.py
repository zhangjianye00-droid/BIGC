"""
核心接口和数据类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class ITask(ABC):
    """
    任务接口 - 对应项目要求的ITask
    提供GetName(), Execute()
    """

    @abstractmethod
    def get_name(self) -> str:
        """获取任务名称"""
        pass

    @abstractmethod
    def execute(self) -> None:
        """执行任务"""
        pass


@dataclass
class ScheduledTask:
    """
    调度任务 - 对应项目要求的ScheduledTask
    包装std::shared_ptr<ITask>，保存执行时间、是否周期、间隔
    """
    task_id: str
    task: ITask
    run_time: float
    is_periodic: bool
    interval: float
    strategy: 'ExecutionStrategy'
    executed: bool = False
    status: str = "PENDING"
    error_message: Optional[str] = None
    execution_count: int = 0

    def __lt__(self, other):
        """用于优先队列排序"""
        return self.run_time < other.run_time

    def get_name(self) -> str:
        return self.task.get_name()

    def execute(self) -> None:
        """Command模式的Execute()"""
        self.task.execute()