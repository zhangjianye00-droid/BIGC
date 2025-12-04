"""
具体任务实现 - 项目要求的5个任务示例
"""

import time
import os
from datetime import datetime
from .core import ITask


class FileBackupTask(ITask):
    """
    Task A - 文件备份（一次性延迟）
    压缩C:\Data为backup_YYYYMMDD.zip，保存至D:\Backup
    """

    def __init__(self, source_dir: str, backup_dir: str):
        self.source_dir = source_dir
        self.backup_dir = backup_dir

    def get_name(self) -> str:
        return "文件备份任务"

    def execute(self) -> None:
        date_str = datetime.now().strftime("%Y%m%d")
        backup_file = os.path.join(self.backup_dir, f"backup_{date_str}.zip")

        print(f"正在备份 {self.source_dir} 到 {backup_file}...")
        time.sleep(1)
        print(f"备份完成: {backup_file}")


class MatrixMultiplyTask(ITask):
    """
    Task B - 矩阵乘法（周期，每5s）
    计算200×200随机矩阵乘积，记录运算时间
    """

    def __init__(self, matrix_size: int = 200):
        self.size = matrix_size

    def get_name(self) -> str:
        return "矩阵乘法任务"

    def execute(self) -> None:
        import random

        start = time.time()

        # 生成随机矩阵
        matrix_a = [[random.random() for _ in range(self.size)] for _ in range(self.size)]
        matrix_b = [[random.random() for _ in range(self.size)] for _ in range(self.size)]

        # 矩阵乘法
        result = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]

        duration = time.time() - start
        print(f"矩阵乘法完成 ({self.size}x{self.size}), 耗时: {duration:.3f}秒")


class HttpGetTask(ITask):
    """
    Task C - HTTP GET（立即）
    请求https://api.github.com/zen，写入zen.txt
    """

    def __init__(self, url: str, output_file: str):
        self.url = url
        self.output_file = output_file

    def get_name(self) -> str:
        return "HTTP GET任务"

    def execute(self) -> None:
        print(f"正在请求 {self.url}...")
        time.sleep(0.5)

        content = "Keep it logically awesome."

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"响应已写入 {self.output_file}")


class ReminderTask(ITask):
    """
    Task D - 课堂提醒（周期，每1min）
    弹出"休息5分钟"对话框（跨线程UI更新）
    """

    def __init__(self, message: str):
        self.message = message

    def get_name(self) -> str:
        return "课堂提醒任务"

    def execute(self) -> None:
        print(f"\n{'=' * 50}")
        print(f"⏰ 提醒: {self.message}")
        print(f"{'=' * 50}\n")


class RandomStatsTask(ITask):
    """
    Task E - 随机数统计（延迟10s）
    产生1000个0-100随机数，计算均值/方差写入日志
    """

    def __init__(self, count: int = 1000):
        self.count = count

    def get_name(self) -> str:
        return "随机数统计任务"

    def execute(self) -> None:
        import random

        numbers = [random.randint(0, 100) for _ in range(self.count)]

        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)

        print(f"随机数统计 (n={self.count}):")
        print(f"  均值: {mean:.2f}")
        print(f"  方差: {variance:.2f}")