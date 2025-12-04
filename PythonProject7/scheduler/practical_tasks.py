"""
实用任务实现 - 有实际意义的任务示例
将此文件保存为：scheduler/practical_tasks.py
"""

import time
import os
import psutil  # 需要安装: pip install psutil
import json
from datetime import datetime
from pathlib import Path
from .core import ITask


class SystemMonitorTask(ITask):
    """
    系统监控任务 - 实际意义：监控服务器性能
    应用场景：
    - 服务器监控
    - 性能分析
    - 资源预警
    """

    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
        """
        参数：
        - cpu_threshold: CPU使用率阈值（超过此值会警告）
        - memory_threshold: 内存使用率阈值
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def get_name(self) -> str:
        return "系统性能监控"

    def execute(self) -> None:
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # 格式化输出
        print(f"\n{'=' * 50}")
        print(f"📊 系统监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")
        print(f"CPU使用率: {cpu_percent}%", end="")
        if cpu_percent > self.cpu_threshold:
            print(f" ⚠️ 警告：超过阈值 {self.cpu_threshold}%")
        else:
            print(f" ✅ 正常")

        print(f"内存使用率: {memory.percent}%", end="")
        if memory.percent > self.memory_threshold:
            print(f" ⚠️ 警告：超过阈值 {self.memory_threshold}%")
        else:
            print(f" ✅ 正常")

        print(f"内存详情: 已用 {memory.used / (1024 ** 3):.2f}GB / 总计 {memory.total / (1024 ** 3):.2f}GB")
        print(f"磁盘使用率: {disk.percent}% (剩余 {disk.free / (1024 ** 3):.2f}GB)")
        print(f"{'=' * 50}\n")

        # 保存到日志文件
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu_percent,
            "memory": memory.percent,
            "disk": disk.percent
        }

        log_file = Path("logs/system_monitor.json")
        log_file.parent.mkdir(exist_ok=True)

        # 追加日志
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_data)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)


class DatabaseBackupTask(ITask):
    """
    数据库备份任务 - 实际意义：定期备份数据防止丢失
    应用场景：
    - 数据库备份
    - 重要文件备份
    - 灾难恢复
    """

    def __init__(self, db_name: str, backup_dir: str):
        """
        参数：
        - db_name: 数据库名称
        - backup_dir: 备份目录
        """
        self.db_name = db_name
        self.backup_dir = Path(backup_dir)

    def get_name(self) -> str:
        return f"数据库备份-{self.db_name}"

    def execute(self) -> None:
        # 创建备份目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{self.db_name}_backup_{timestamp}.sql"

        print(f"\n🗄️  开始备份数据库: {self.db_name}")
        print(f"备份文件: {backup_file}")

        # 模拟备份过程（实际项目中使用 mysqldump 或 pg_dump）
        time.sleep(2)  # 模拟耗时操作

        # 创建模拟备份文件
        with open(backup_file, 'w') as f:
            f.write(f"-- Database backup for {self.db_name}\n")
            f.write(f"-- Created at: {datetime.now()}\n")
            f.write(f"-- This is a simulated backup file\n")
            f.write(f"-- In production, use: mysqldump -u user -p {self.db_name} > {backup_file}\n")

        # 清理旧备份（保留最近7天）
        self._cleanup_old_backups()

        print(f"✅ 备份完成！文件大小: {backup_file.stat().st_size} bytes")
        print(f"备份位置: {backup_file.absolute()}\n")

    def _cleanup_old_backups(self, keep_days: int = 7):
        """清理超过指定天数的旧备份"""
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        deleted_count = 0

        for backup_file in self.backup_dir.glob(f"{self.db_name}_backup_*.sql"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                deleted_count += 1

        if deleted_count > 0:
            print(f"🗑️  清理了 {deleted_count} 个旧备份文件")


class EmailSenderTask(ITask):
    """
    邮件发送任务 - 实际意义：延迟发送通知邮件
    应用场景：
    - 用户注册确认邮件
    - 定时报告发送
    - 系统告警通知
    """

    def __init__(self, to: str, subject: str, body: str):
        """
        参数：
        - to: 收件人
        - subject: 邮件主题
        - body: 邮件内容
        """
        self.to = to
        self.subject = subject
        self.body = body

    def get_name(self) -> str:
        return f"发送邮件给{self.to}"

    def execute(self) -> None:
        print(f"\n📧 准备发送邮件...")
        print(f"收件人: {self.to}")
        print(f"主题: {self.subject}")
        print(f"内容预览: {self.body[:50]}...")

        # 模拟发送邮件（实际项目中使用 smtplib）
        time.sleep(1)

        # 记录到发送日志
        log_file = Path("logs/email_sent.log")
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] 发送邮件给 {self.to}\n")
            f.write(f"  主题: {self.subject}\n")
            f.write(f"  状态: ✅ 发送成功\n\n")

        print(f"✅ 邮件发送成功！")
        print(f"日志已保存到: {log_file.absolute()}\n")


class WebsiteHealthCheckTask(ITask):
    """
    网站健康检查任务 - 实际意义：监控网站可用性
    应用场景：
    - 网站监控
    - API健康检查
    - 服务可用性监控
    """

    def __init__(self, url: str, timeout: int = 10):
        """
        参数：
        - url: 要检查的网址
        - timeout: 超时时间（秒）
        """
        self.url = url
        self.timeout = timeout

    def get_name(self) -> str:
        return f"网站检查-{self.url}"

    def execute(self) -> None:
        print(f"\n🌐 检查网站健康状况: {self.url}")

        try:
            # 模拟HTTP请求（实际项目中使用 requests 库）
            import random
            time.sleep(0.5)

            # 模拟响应
            status_code = random.choice([200, 200, 200, 500, 503])  # 大部分时候是正常的
            response_time = random.uniform(0.1, 2.0)

            if status_code == 200:
                print(f"✅ 网站正常")
                print(f"   响应时间: {response_time:.3f}秒")
                status = "正常"
            else:
                print(f"❌ 网站异常！")
                print(f"   HTTP状态码: {status_code}")
                status = "异常"

            # 记录检查结果
            log_file = Path("logs/health_check.json")
            log_file.parent.mkdir(exist_ok=True)

            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append({
                "timestamp": datetime.now().isoformat(),
                "url": self.url,
                "status_code": status_code,
                "response_time": response_time,
                "status": status
            })

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            print(f"   日志已保存\n")

        except Exception as e:
            print(f"❌ 检查失败: {e}\n")


class TempFileCleanupTask(ITask):
    """
    临时文件清理任务 - 实际意义：释放磁盘空间
    应用场景：
    - 清理临时文件
    - 日志轮转
    - 缓存清理
    """

    def __init__(self, temp_dir: str, max_age_days: int = 7):
        """
        参数：
        - temp_dir: 临时文件目录
        - max_age_days: 文件最大保留天数
        """
        self.temp_dir = Path(temp_dir)
        self.max_age_days = max_age_days

    def get_name(self) -> str:
        return "临时文件清理"

    def execute(self) -> None:
        print(f"\n🗑️  开始清理临时文件...")
        print(f"目录: {self.temp_dir}")
        print(f"清理超过 {self.max_age_days} 天的文件")

        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            print(f"目录不存在，已创建\n")
            return

        cutoff_time = time.time() - (self.max_age_days * 24 * 3600)
        deleted_count = 0
        freed_space = 0

        for file_path in self.temp_dir.rglob('*'):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    freed_space += file_size

        print(f"✅ 清理完成！")
        print(f"   删除文件: {deleted_count} 个")
        print(f"   释放空间: {freed_space / (1024 ** 2):.2f} MB\n")


class ReportGeneratorTask(ITask):
    """
    报表生成任务 - 实际意义：定期生成业务报表
    应用场景：
    - 销售报表
    - 用户统计
    - 性能分析报告
    """

    def __init__(self, report_type: str, output_dir: str):
        """
        参数：
        - report_type: 报表类型（daily/weekly/monthly）
        - output_dir: 报表输出目录
        """
        self.report_type = report_type
        self.output_dir = Path(output_dir)

    def get_name(self) -> str:
        return f"生成{self.report_type}报表"

    def execute(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📈 生成报表: {self.report_type}")

        # 生成报表文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"report_{self.report_type}_{timestamp}.html"

        # 模拟数据收集
        time.sleep(1)

        # 生成HTML报表
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.report_type}报表</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
    </style>
</head>
<body>
    <h1>📊 {self.report_type.upper()} 报表</h1>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>系统统计</h2>
    <table>
        <tr>
            <th>指标</th>
            <th>数值</th>
        </tr>
        <tr>
            <td>总任务数</td>
            <td>127</td>
        </tr>
        <tr>
            <td>完成任务</td>
            <td>98</td>
        </tr>
        <tr>
            <td>成功率</td>
            <td>77%</td>
        </tr>
    </table>

    <h2>性能指标</h2>
    <table>
        <tr>
            <th>CPU平均使用率</th>
            <td>45%</td>
        </tr>
        <tr>
            <th>内存平均使用率</th>
            <td>62%</td>
        </tr>
    </table>
</body>
</html>
        """

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 报表生成完成！")
        print(f"文件位置: {report_file.absolute()}")
        print(f"可以用浏览器打开查看\n")


# 工厂方法扩展
def create_system_monitor_task(cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
    """创建系统监控任务"""
    return SystemMonitorTask(cpu_threshold, memory_threshold)


def create_database_backup_task(db_name: str, backup_dir: str = "backups"):
    """创建数据库备份任务"""
    return DatabaseBackupTask(db_name, backup_dir)


def create_email_sender_task(to: str, subject: str, body: str):
    """创建邮件发送任务"""
    return EmailSenderTask(to, subject, body)


def create_website_health_check_task(url: str, timeout: int = 10):
    """创建网站健康检查任务"""
    return WebsiteHealthCheckTask(url, timeout)


def create_temp_cleanup_task(temp_dir: str = "temp", max_age_days: int = 7):
    """创建临时文件清理任务"""
    return TempFileCleanupTask(temp_dir, max_age_days)


def create_report_generator_task(report_type: str = "daily", output_dir: str = "reports"):
    """创建报表生成任务"""
    return ReportGeneratorTask(report_type, output_dir)