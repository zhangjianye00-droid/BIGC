"""
任务调度器 - 对应项目要求的TaskScheduler
单例，内部使用priority_queue(heapq), mutex, condition_variable
"""

import time
import threading
import heapq
from typing import Dict, List, Optional, Set

from .core import ITask, ScheduledTask
from .strategies import OnceStrategy, PeriodicStrategy
from .observers import TaskObserver
from .logger import LogWriter
from .factory import TaskFactory


class TaskScheduler:
    """
    任务调度器 - 单例模式
    对应项目要求：priority_queue, mutex, condition_variable
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_heap: List[ScheduledTask] = []  # priority_queue
        self.log_writer = LogWriter()
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.mutex = threading.Lock()  # mutex
        self.condition = threading.Condition(self.mutex)  # condition_variable
        self.observers: Set[TaskObserver] = set()

    def add_observer(self, observer: TaskObserver) -> None:
        """添加观察者 - Observer模式"""
        with self.mutex:
            self.observers.add(observer)

    def remove_observer(self, observer: TaskObserver) -> None:
        """移除观察者"""
        with self.mutex:
            self.observers.discard(observer)

    def _notify_created(self, task_id: str, task_name: str) -> None:
        """通知任务创建"""
        for observer in self.observers:
            try:
                observer.on_task_created(task_id, task_name)
            except Exception as e:
                self.log_writer.log_error(f"观察者通知失败: {e}")

    def _notify_started(self, task_id: str, task_name: str) -> None:
        """通知任务开始"""
        for observer in self.observers:
            try:
                observer.on_task_started(task_id, task_name)
            except Exception as e:
                self.log_writer.log_error(f"观察者通知失败: {e}")

    def _notify_completed(self, task_id: str, task_name: str, duration: float) -> None:
        """通知任务完成"""
        for observer in self.observers:
            try:
                observer.on_task_completed(task_id, task_name, duration)
            except Exception as e:
                self.log_writer.log_error(f"观察者通知失败: {e}")

    def _notify_failed(self, task_id: str, task_name: str, error: str) -> None:
        """通知任务失败"""
        for observer in self.observers:
            try:
                observer.on_task_failed(task_id, task_name, error)
            except Exception as e:
                self.log_writer.log_error(f"观察者通知失败: {e}")

    def add_one_time_task(self, task: ITask, delay: float = 0.0) -> str:
        """
        添加一次性任务
        对应：UI调用TaskScheduler::AddOneTimeTask(...)
        任务加入优先队列，工作线程根据runTime触发
        """
        task_id = TaskFactory._generate_task_id()
        run_time = time.time() + delay
        strategy = OnceStrategy()

        scheduled_task = ScheduledTask(
            task_id=task_id,
            task=task,
            run_time=run_time,
            is_periodic=False,
            interval=0.0,
            strategy=strategy
        )

        with self.condition:
            self.tasks[task_id] = scheduled_task
            heapq.heappush(self.task_heap, scheduled_task)
            self.condition.notify()

        self.log_writer.log_info(f"📝 任务创建: {task.get_name()} ({task_id}), 延迟: {delay}秒")
        self._notify_created(task_id, task.get_name())

        return task_id

    def add_periodic_task(self, task: ITask, interval: float) -> str:
        """添加周期性任务"""
        if interval <= 0:
            raise ValueError("周期间隔必须大于0")

        task_id = TaskFactory._generate_task_id()
        run_time = time.time() + interval
        strategy = PeriodicStrategy(interval)

        scheduled_task = ScheduledTask(
            task_id=task_id,
            task=task,
            run_time=run_time,
            is_periodic=True,
            interval=interval,
            strategy=strategy
        )

        with self.condition:
            self.tasks[task_id] = scheduled_task
            heapq.heappush(self.task_heap, scheduled_task)
            self.condition.notify()

        self.log_writer.log_info(f"📝 周期任务创建: {task.get_name()} ({task_id}), 间隔: {interval}秒")
        self._notify_created(task_id, task.get_name())

        return task_id

    def _execute_task(self, scheduled_task: ScheduledTask) -> None:
        """
        执行任务
        任务执行期间捕获异常，写入LogWriter
        完成后通过Observer通知UI更新状态
        """
        scheduled_task.status = "RUNNING"
        scheduled_task.execution_count += 1

        self.log_writer.log_info(
            f"▶️  任务开始: {scheduled_task.get_name()} ({scheduled_task.task_id}), "
            f"执行次数: {scheduled_task.execution_count}"
        )
        self._notify_started(scheduled_task.task_id, scheduled_task.get_name())

        start_time = time.time()

        try:
            scheduled_task.execute()
            duration = time.time() - start_time

            scheduled_task.strategy.update_next_run(scheduled_task)

            if scheduled_task.is_periodic:
                scheduled_task.status = "PENDING"
                with self.condition:
                    heapq.heappush(self.task_heap, scheduled_task)
            else:
                scheduled_task.status = "COMPLETED"

            self.log_writer.log_info(
                f"✅ 任务完成: {scheduled_task.get_name()} ({scheduled_task.task_id}), "
                f"耗时: {duration:.3f}秒"
            )
            self._notify_completed(scheduled_task.task_id, scheduled_task.get_name(), duration)

        except Exception as e:
            scheduled_task.status = "FAILED"
            scheduled_task.error_message = str(e)

            self.log_writer.log_error(
                f"❌ 任务失败: {scheduled_task.get_name()} ({scheduled_task.task_id}), "
                f"错误: {str(e)}"
            )
            self._notify_failed(scheduled_task.task_id, scheduled_task.get_name(), str(e))

    def _worker(self) -> None:
        """工作线程 - 根据runTime触发任务"""
        while self.running:
            with self.condition:
                while self.running and not self.task_heap:
                    self.condition.wait(timeout=0.1)

                if not self.running:
                    break

                if not self.task_heap:
                    continue

                next_task = self.task_heap[0]
                wait_time = next_task.run_time - time.time()

                if wait_time > 0:
                    self.condition.wait(timeout=min(wait_time, 0.1))
                    continue

                scheduled_task = heapq.heappop(self.task_heap)

            if scheduled_task.strategy.should_execute(scheduled_task):
                self._execute_task(scheduled_task)

    def start(self) -> None:
        """启动调度器"""
        with self.mutex:
            if self.running:
                raise RuntimeError("调度器已在运行")

            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()

        self.log_writer.log_info("🚀 调度器启动")

    def stop(self) -> None:
        """停止调度器"""
        with self.mutex:
            if not self.running:
                return

            self.running = False
            self.condition.notify()

        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

        self.log_writer.log_info("🛑 调度器停止")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.mutex:
            return {
                "total_tasks": len(self.tasks),
                "pending": sum(1 for t in self.tasks.values() if t.status == "PENDING"),
                "running": sum(1 for t in self.tasks.values() if t.status == "RUNNING"),
                "completed": sum(1 for t in self.tasks.values() if t.status == "COMPLETED"),
                "failed": sum(1 for t in self.tasks.values() if t.status == "FAILED"),
            }