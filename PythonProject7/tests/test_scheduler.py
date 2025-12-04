"""
测试所有设计模式
"""

import unittest
import time
from scheduler import (
    TaskScheduler,
    TaskFactory,
    ConsoleObserver,
    OnceStrategy,
    PeriodicStrategy
)


class TestDesignPatterns(unittest.TestCase):
    """测试四种设计模式"""

    def setUp(self):
        self.scheduler = TaskScheduler()

    def tearDown(self):
        if self.scheduler.running:
            self.scheduler.stop()

    def test_factory_pattern(self):
        """测试工厂模式"""
        # 工厂创建不同类型的任务
        task1 = TaskFactory.create_file_backup_task("src", "dest")
        task2 = TaskFactory.create_http_get_task("url", "output")

        self.assertEqual(task1.get_name(), "文件备份任务")
        self.assertEqual(task2.get_name(), "HTTP GET任务")

    def test_strategy_pattern(self):
        """测试策略模式"""
        # OnceStrategy：只执行一次
        once = OnceStrategy()
        # PeriodicStrategy：周期执行
        periodic = PeriodicStrategy(1.0)

        self.assertIsNotNone(once)
        self.assertIsNotNone(periodic)
        self.assertEqual(periodic.interval, 1.0)

    def test_observer_pattern(self):
        """测试观察者模式"""
        observer = ConsoleObserver()

        # 添加观察者
        self.scheduler.add_observer(observer)
        self.assertIn(observer, self.scheduler.observers)

        # 移除观察者
        self.scheduler.remove_observer(observer)
        self.assertNotIn(observer, self.scheduler.observers)

    def test_command_pattern(self):
        """测试命令模式"""
        task = TaskFactory.create_random_stats_task(100)

        # 添加任务（命令封装）
        task_id = self.scheduler.add_one_time_task(task, delay=0.1)
        self.scheduler.start()
        time.sleep(0.5)

        # 验证任务执行
        scheduled_task = self.scheduler.tasks[task_id]
        self.assertEqual(scheduled_task.status, "COMPLETED")


if __name__ == '__main__':
    unittest.main()