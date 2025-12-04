"""
RAII包装文件写入 - 对应项目要求的LogWriter
构造打开、析构自动关闭
"""

import logging
import os


class LogWriter:
    """日志写入器 - RAII模式"""

    def __init__(self, log_file: str = "logs/scheduler.log"):
        self.log_file = log_file
        self.logger = logging.getLogger("TaskScheduler")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # 文件处理器
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)

        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log_info(self, message: str) -> None:
        """记录信息"""
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        """记录错误"""
        self.logger.error(message)

    def log_warning(self, message: str) -> None:
        """记录警告"""
        self.logger.warning(message)

    def __enter__(self):
        """上下文管理器入口 - RAII构造"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 - RAII析构自动关闭"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)