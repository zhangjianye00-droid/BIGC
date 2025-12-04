"""
实用任务调度器UI - 有实际意义的版本
将此文件保存为：ui_practical.py

"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
from datetime import datetime
from scheduler import TaskScheduler, TaskObserver, ITask
from scheduler.practical_tasks import (
    create_system_monitor_task,
    create_database_backup_task,
    create_email_sender_task,
    create_website_health_check_task,
    create_temp_cleanup_task,
    create_report_generator_task
)


class UIObserver(TaskObserver):
    """UI观察者"""

    def __init__(self, ui_callback):
        self.ui_callback = ui_callback

    def on_task_created(self, task_id: str, task_name: str) -> None:
        self.ui_callback("创建", task_id, task_name, "")

    def on_task_started(self, task_id: str, task_name: str) -> None:
        self.ui_callback("开始", task_id, task_name, "")

    def on_task_completed(self, task_id: str, task_name: str, duration: float) -> None:
        self.ui_callback("完成", task_id, task_name, f"耗时: {duration:.3f}秒")

    def on_task_failed(self, task_id: str, task_name: str, error: str) -> None:
        self.ui_callback("失败", task_id, task_name, f"错误: {error}")


class PracticalSchedulerUI:
    """实用任务调度器UI"""

    def __init__(self, root):
        self.root = root
        self.root.title("轻量级任务调度器 - 实用版")
        self.root.geometry("1500x900")
        self.root.configure(bg='#ecf0f1')

        # 调度器
        self.scheduler = TaskScheduler()
        self.ui_observer = UIObserver(self.update_task_status)
        self.scheduler.add_observer(self.ui_observer)

        # 任务列表
        self.task_items = {}

        # 创建UI
        self.create_widgets()

        # 启动状态更新
        self.update_statistics()

    def create_widgets(self):
        """创建界面组件"""

        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#34495e', height=100)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="🚀 企业级任务调度系统",
            font=("Microsoft YaHei", 26, "bold"),
            bg='#34495e',
            fg='white'
        )
        title_label.pack(pady=25)

        # 主容器
        main_container = tk.Frame(self.root, bg='#ecf0f1')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # 左侧控制面板
        left_panel = tk.Frame(main_container, bg='white', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        self.create_control_panel(left_panel)

        # 右侧显示区域
        right_panel = tk.Frame(main_container, bg='white')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_display_panel(right_panel)

    def create_control_panel(self, parent):
        """创建控制面板"""

        # 调度器控制
        control_frame = tk.LabelFrame(
            parent,
            text="🎛️ 调度器控制",
            font=("Microsoft YaHei", 11, "bold"),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        control_frame.pack(fill=tk.X, padx=15, pady=15)

        self.start_button = tk.Button(
            control_frame,
            text="▶️ 启动调度器",
            command=self.start_scheduler,
            font=("Microsoft YaHei", 11, "bold"),
            bg='#27ae60',
            fg='white',
            width=25,
            height=2,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(
            control_frame,
            text="⏸️ 停止调度器",
            command=self.stop_scheduler,
            font=("Microsoft YaHei", 11, "bold"),
            bg='#e74c3c',
            fg='white',
            width=25,
            height=2,
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=5)

        # 实用任务区
        task_frame = tk.LabelFrame(
            parent,
            text="💼 实用任务",
            font=("Microsoft YaHei", 11, "bold"),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        task_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # 任务类别标签
        category_label = tk.Label(
            task_frame,
            text="📊 监控类任务",
            font=("Microsoft YaHei", 10, "bold"),
            bg='white',
            fg='#7f8c8d'
        )
        category_label.pack(anchor=tk.W, pady=(0, 5))

        # 系统监控
        btn1 = tk.Button(
            task_frame,
            text="💻 系统性能监控（周期5秒）",
            command=self.add_system_monitor,
            font=("Microsoft YaHei", 9),
            bg='#3498db',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn1.pack(pady=3, fill=tk.X)

        # 网站健康检查
        btn2 = tk.Button(
            task_frame,
            text="🌐 网站健康检查（周期10秒）",
            command=self.add_health_check,
            font=("Microsoft YaHei", 9),
            bg='#1abc9c',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn2.pack(pady=3, fill=tk.X)

        # 备份类
        category_label2 = tk.Label(
            task_frame,
            text="💾 备份类任务",
            font=("Microsoft YaHei", 10, "bold"),
            bg='white',
            fg='#7f8c8d'
        )
        category_label2.pack(anchor=tk.W, pady=(10, 5))

        # 数据库备份
        btn3 = tk.Button(
            task_frame,
            text="🗄️ 数据库备份（延迟5秒）",
            command=self.add_database_backup,
            font=("Microsoft YaHei", 9),
            bg='#9b59b6',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn3.pack(pady=3, fill=tk.X)

        # 维护类
        category_label3 = tk.Label(
            task_frame,
            text="🔧 维护类任务",
            font=("Microsoft YaHei", 10, "bold"),
            bg='white',
            fg='#7f8c8d'
        )
        category_label3.pack(anchor=tk.W, pady=(10, 5))

        # 临时文件清理
        btn4 = tk.Button(
            task_frame,
            text="🗑️ 临时文件清理（延迟3秒）",
            command=self.add_temp_cleanup,
            font=("Microsoft YaHei", 9),
            bg='#e67e22',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn4.pack(pady=3, fill=tk.X)

        # 通知类
        category_label4 = tk.Label(
            task_frame,
            text="📧 通知类任务",
            font=("Microsoft YaHei", 10, "bold"),
            bg='white',
            fg='#7f8c8d'
        )
        category_label4.pack(anchor=tk.W, pady=(10, 5))

        # 邮件发送
        btn5 = tk.Button(
            task_frame,
            text="📨 发送通知邮件（立即）",
            command=self.add_email_sender,
            font=("Microsoft YaHei", 9),
            bg='#e74c3c',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn5.pack(pady=3, fill=tk.X)

        # 报表类
        category_label5 = tk.Label(
            task_frame,
            text="📈 报表类任务",
            font=("Microsoft YaHei", 10, "bold"),
            bg='white',
            fg='#7f8c8d'
        )
        category_label5.pack(anchor=tk.W, pady=(10, 5))

        # 报表生成
        btn6 = tk.Button(
            task_frame,
            text="📊 生成每日报表（延迟2秒）",
            command=self.add_report_generator,
            font=("Microsoft YaHei", 9),
            bg='#f39c12',
            fg='white',
            width=30,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn6.pack(pady=3, fill=tk.X)

        # 统计信息
        stats_frame = tk.LabelFrame(
            parent,
            text="📊 运行统计",
            font=("Microsoft YaHei", 11, "bold"),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        stats_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.stats_labels = {}
        stats_info = [
            ("total_tasks", "总任务数", "#3498db"),
            ("pending", "待执行", "#f39c12"),
            ("running", "执行中", "#27ae60"),
            ("completed", "已完成", "#9b59b6"),
            ("failed", "失败", "#e74c3c")
        ]

        for key, name, color in stats_info:
            frame = tk.Frame(stats_frame, bg='white')
            frame.pack(fill=tk.X, pady=3)

            tk.Label(
                frame,
                text=f"{name}:",
                bg='white',
                font=("Microsoft YaHei", 9),
                width=8,
                anchor=tk.W
            ).pack(side=tk.LEFT)

            label = tk.Label(
                frame,
                text="0",
                bg='white',
                font=("Microsoft YaHei", 10, "bold"),
                fg=color
            )
            label.pack(side=tk.LEFT)
            self.stats_labels[key] = label

    def create_display_panel(self, parent):
        """创建显示面板"""

        # 任务列表区
        task_frame = tk.LabelFrame(
            parent,
            text="📋 任务列表",
            font=("Microsoft YaHei", 11, "bold"),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建Treeview
        columns = ("ID", "任务名称", "类型", "状态", "执行次数", "详细信息")
        self.task_tree = ttk.Treeview(
            task_frame,
            columns=columns,
            show='headings',
            height=18
        )

        # 设置列
        widths = [120, 200, 100, 80, 80, 350]
        for col, width in zip(columns, widths):
            self.task_tree.heading(col, text=col)
            self.task_tree.column(
                col,
                width=width,
                anchor=tk.CENTER if col != "详细信息" else tk.W
            )

        # 滚动条
        scrollbar = ttk.Scrollbar(
            task_frame,
            orient=tk.VERTICAL,
            command=self.task_tree.yview
        )
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 日志区
        log_frame = tk.LabelFrame(
            parent,
            text="📄 运行日志",
            font=("Microsoft YaHei", 11, "bold"),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            wrap=tk.WORD,
            height=12
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 欢迎消息
        self.log_message("系统", "✨ 欢迎使用企业级任务调度系统")
        self.log_message("提示", "💡 点击'启动调度器'开始使用")
        self.log_message("说明", "📚 左侧按钮可添加各类实用任务")

    def log_message(self, level, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)

    def start_scheduler(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("系统", "🚀 调度器已启动！")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")

    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("系统", "⏸️ 调度器已停止")

    def add_system_monitor(self):
        """添加系统监控任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_system_monitor_task(cpu_threshold=80.0, memory_threshold=80.0)
        self.scheduler.add_periodic_task(task, interval=5.0)
        self.log_message("创建", "已添加系统监控任务（每5秒检查一次）")

    def add_health_check(self):
        """添加健康检查任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_website_health_check_task("https://v8.chaoxing.com/")
        self.scheduler.add_periodic_task(task, interval=10.0)
        self.log_message("创建", "已添加网站健康检查任务（每10秒检查一次）")

    def add_database_backup(self):
        """添加数据库备份任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_database_backup_task("my_database", "backups")
        self.scheduler.add_one_time_task(task, delay=5.0)
        self.log_message("创建", "已添加数据库备份任务（5秒后执行）")

    def add_temp_cleanup(self):
        """添加临时文件清理任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_temp_cleanup_task("temp", max_age_days=7)
        self.scheduler.add_one_time_task(task, delay=3.0)
        self.log_message("创建", "已添加临时文件清理任务（3秒后执行）")

    def add_email_sender(self):
        """添加邮件发送任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_email_sender_task(
            to="2270732901@qq.com",
            subject="系统运行报告",
            body="系统运行正常，所有服务正常运行中。"
        )
        self.scheduler.add_one_time_task(task, delay=0.0)
        self.log_message("创建", "已添加邮件发送任务（立即执行）")

    def add_report_generator(self):
        """添加报表生成任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        task = create_report_generator_task("daily", "reports")
        self.scheduler.add_one_time_task(task, delay=2.0)
        self.log_message("创建", "已添加报表生成任务（2秒后执行）")

    def update_task_status(self, event_type, task_id, task_name, details):
        """更新任务状态"""
        self.root.after(0, self._update_ui, event_type, task_id, task_name, details)

    def _update_ui(self, event_type, task_id, task_name, details):
        """更新UI"""
        self.log_message(event_type, f"{task_name} ({task_id}) {details}")

        if event_type == "创建":
            task = self.scheduler.tasks.get(task_id)
            if task:
                task_type = "周期性" if task.is_periodic else "一次性"
                item = self.task_tree.insert("", tk.END, values=(
                    task_id,
                    task_name,
                    task_type,
                    "待执行",
                    0,
                    ""
                ))
                self.task_items[task_id] = item

        elif task_id in self.task_items:
            item = self.task_items[task_id]
            task = self.scheduler.tasks.get(task_id)

            if task:
                task_type = "周期性" if task.is_periodic else "一次性"
                status_map = {
                    "开始": "执行中",
                    "完成": "已完成" if not task.is_periodic else "待执行",
                    "失败": "失败"
                }
                status = status_map.get(event_type, task.status)

                self.task_tree.item(item, values=(
                    task_id,
                    task_name,
                    task_type,
                    status,
                    task.execution_count,
                    details
                ))

    def update_statistics(self):
        """更新统计信息"""
        if self.scheduler.running:
            stats = self.scheduler.get_statistics()
            for key, label in self.stats_labels.items():
                label.config(text=str(stats.get(key, 0)))

        self.root.after(500, self.update_statistics)


def main():
    """主函数"""
    root = tk.Tk()
    app = PracticalSchedulerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()