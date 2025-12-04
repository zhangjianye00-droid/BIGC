"""
工厂模式 - 创建不同ITask实例，将任务实例化与调度解耦
"""

import threading
from .core import ITask
from .tasks import (
    FileBackupTask,
    MatrixMultiplyTask,
    HttpGetTask,
    ReminderTask,
    RandomStatsTask
)


class TaskFactory:
    """任务工厂 - 对应项目要求的TaskFactory"""

    _task_counter = 0
    _lock = threading.Lock()

    @classmethod
    def _generate_task_id(cls) -> str:
        """生成唯一任务ID"""
        with cls._lock:
            cls._task_counter += 1
            return f"TASK_{cls._task_counter:06d}"

    @classmethod
    def create_file_backup_task(cls, source: str, dest: str) -> ITask:
        """创建文件备份任务"""
        return FileBackupTask(source, dest)

    @classmethod
    def create_matrix_multiply_task(cls, size: int = 200) -> ITask:
        """创建矩阵乘法任务"""
        return MatrixMultiplyTask(size)

    @classmethod
    def create_http_get_task(cls, url: str, output: str) -> ITask:
        """创建HTTP GET任务"""
        return HttpGetTask(url, output)

    @classmethod
    def create_reminder_task(cls, message: str) -> ITask:
        """创建提醒任务"""
        return ReminderTask(message)

    @classmethod
    def create_random_stats_task(cls, count: int = 1000) -> ITask:
        """创建随机数统计任务"""
        return RandomStatsTask(count)