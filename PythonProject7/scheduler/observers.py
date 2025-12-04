"""
观察者模式 - UI层订阅任务状态变化，实现解耦通信
"""

from abc import ABC, abstractmethod


class TaskObserver(ABC):
    """任务观察者抽象基类"""

    @abstractmethod
    def on_task_created(self, task_id: str, task_name: str) -> None:
        """任务创建通知"""
        pass

    @abstractmethod
    def on_task_started(self, task_id: str, task_name: str) -> None:
        """任务开始通知"""
        pass

    @abstractmethod
    def on_task_completed(self, task_id: str, task_name: str, duration: float) -> None:
        """任务完成通知"""
        pass

    @abstractmethod
    def on_task_failed(self, task_id: str, task_name: str, error: str) -> None:
        """任务失败通知"""
        pass


class ConsoleObserver(TaskObserver):
    """控制台观察者 - 模拟UI层"""

    def on_task_created(self, task_id: str, task_name: str) -> None:
        print(f"[UI通知] 任务已创建: {task_name} ({task_id})")

    def on_task_started(self, task_id: str, task_name: str) -> None:
        print(f"[UI通知] 任务开始执行: {task_name} ({task_id})")

    def on_task_completed(self, task_id: str, task_name: str, duration: float) -> None:
        print(f"[UI通知] 任务完成: {task_name}, 耗时: {duration:.3f}秒")

    def on_task_failed(self, task_id: str, task_name: str, error: str) -> None:
        print(f"[UI通知] 任务失败: {task_name}, 错误: {error}")