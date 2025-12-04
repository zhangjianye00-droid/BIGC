"""
性能测试
"""

import time
import unittest
from scheduler import TaskScheduler, TaskFactory


class TestPerformance(unittest.TestCase):
    """测试调度器性能"""

    def test_many_tasks(self):
        """测试大量任务"""
        scheduler = TaskScheduler()

        # 添加100个任务
        for i in range(100):
            task = TaskFactory.create_random_stats_task(100)
            scheduler.add_one_time_task(task, delay=0.01 * i)

        scheduler.start()
        time.sleep(5)

        stats = scheduler.get_statistics()
        print(f"完成任务数: {stats['completed']}")

        scheduler.stop()

        # 验证大部分任务完成
        self.assertGreater(stats['completed'], 50)