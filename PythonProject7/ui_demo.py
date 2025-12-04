"""
交互式UI演示
运行此文件启动图形界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from scheduler import (
    TaskScheduler,
    TaskFactory,
    TaskObserver,
    ITask
)


class CustomTask(ITask):
    """自定义任务 - 用于UI创建"""

    def __init__(self, name: str, duration: float):
        self.task_name = name
        self.duration = duration

    def get_name(self) -> str:
        return self.task_name

    def execute(self) -> None:
        time.sleep(self.duration)


class UIObserver(TaskObserver):
    """UI观察者 - 更新界面"""

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


class SchedulerUI:
    """调度器图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("轻量级多任务调度器 - 交互式演示")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

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

        # 标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            title_frame,
            text="🚀 轻量级多任务调度器",
            font=("Arial", 24, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)

        # 主容器
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧面板 - 控制区
        left_panel = tk.Frame(main_container, bg='white', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5), pady=5)

        # 控制按钮区
        control_frame = tk.LabelFrame(left_panel, text="📋 调度器控制", font=("Arial", 12, "bold"), bg='white', padx=10,
                                      pady=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # 启动/停止按钮
        self.start_button = tk.Button(
            control_frame,
            text="▶️  启动调度器",
            command=self.start_scheduler,
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            width=20,
            height=2,
            cursor='hand2'
        )
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(
            control_frame,
            text="⏸️  停止调度器",
            command=self.stop_scheduler,
            font=("Arial", 11, "bold"),
            bg='#e74c3c',
            fg='white',
            width=20,
            height=2,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=5)

        # 快速任务按钮区
        quick_task_frame = tk.LabelFrame(left_panel, text="⚡ 快速添加任务", font=("Arial", 12, "bold"), bg='white',
                                         padx=10, pady=10)
        quick_task_frame.pack(fill=tk.X, padx=10, pady=10)

        tasks_info = [
            ("文件备份", "create_file_backup_task", "#3498db"),
            ("矩阵乘法", "create_matrix_multiply_task", "#9b59b6"),
            ("HTTP请求", "create_http_get_task", "#1abc9c"),
            ("课堂提醒", "create_reminder_task", "#f39c12"),
            ("随机统计", "create_random_stats_task", "#e67e22")
        ]

        for task_name, factory_method, color in tasks_info:
            btn = tk.Button(
                quick_task_frame,
                text=f"➕ {task_name}",
                command=lambda m=factory_method: self.add_quick_task(m),
                font=("Arial", 10),
                bg=color,
                fg='white',
                width=18,
                cursor='hand2'
            )
            btn.pack(pady=3)

        # 自定义任务区
        custom_frame = tk.LabelFrame(left_panel, text="🎨 自定义任务", font=("Arial", 12, "bold"), bg='white', padx=10,
                                     pady=10)
        custom_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(custom_frame, text="任务名称:", bg='white', font=("Arial", 10)).pack(anchor=tk.W)
        self.task_name_entry = tk.Entry(custom_frame, font=("Arial", 10))
        self.task_name_entry.pack(fill=tk.X, pady=(0, 5))
        self.task_name_entry.insert(0, "我的任务")

        tk.Label(custom_frame, text="执行时长(秒):", bg='white', font=("Arial", 10)).pack(anchor=tk.W)
        self.duration_entry = tk.Entry(custom_frame, font=("Arial", 10))
        self.duration_entry.pack(fill=tk.X, pady=(0, 5))
        self.duration_entry.insert(0, "1.0")

        tk.Label(custom_frame, text="延迟(秒):", bg='white', font=("Arial", 10)).pack(anchor=tk.W)
        self.delay_entry = tk.Entry(custom_frame, font=("Arial", 10))
        self.delay_entry.pack(fill=tk.X, pady=(0, 5))
        self.delay_entry.insert(0, "0")

        tk.Label(custom_frame, text="任务类型:", bg='white', font=("Arial", 10)).pack(anchor=tk.W)
        self.task_type_var = tk.StringVar(value="一次性")
        task_type_combo = ttk.Combobox(
            custom_frame,
            textvariable=self.task_type_var,
            values=["一次性", "周期性"],
            state="readonly",
            font=("Arial", 10)
        )
        task_type_combo.pack(fill=tk.X, pady=(0, 5))

        tk.Label(custom_frame, text="周期间隔(秒):", bg='white', font=("Arial", 10)).pack(anchor=tk.W)
        self.interval_entry = tk.Entry(custom_frame, font=("Arial", 10))
        self.interval_entry.pack(fill=tk.X, pady=(0, 10))
        self.interval_entry.insert(0, "5")

        tk.Button(
            custom_frame,
            text="➕ 添加自定义任务",
            command=self.add_custom_task,
            font=("Arial", 10, "bold"),
            bg='#34495e',
            fg='white',
            cursor='hand2'
        ).pack(fill=tk.X)

        # 统计信息区
        stats_frame = tk.LabelFrame(left_panel, text="📊 统计信息", font=("Arial", 12, "bold"), bg='white', padx=10,
                                    pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.stats_labels = {}
        stats_keys = ["total_tasks", "pending", "running", "completed", "failed"]
        stats_names = ["总任务数", "待执行", "执行中", "已完成", "失败"]

        for key, name in zip(stats_keys, stats_names):
            frame = tk.Frame(stats_frame, bg='white')
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"{name}:", bg='white', font=("Arial", 10), width=10, anchor=tk.W).pack(side=tk.LEFT)
            label = tk.Label(frame, text="0", bg='white', font=("Arial", 10, "bold"), fg='#2c3e50')
            label.pack(side=tk.LEFT)
            self.stats_labels[key] = label

        # 右侧面板 - 任务列表和日志
        right_panel = tk.Frame(main_container, bg='white')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        # 任务列表
        task_list_frame = tk.LabelFrame(right_panel, text="📝 任务列表", font=("Arial", 12, "bold"), bg='white', padx=5,
                                        pady=5)
        task_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Treeview
        columns = ("ID", "任务名称", "类型", "状态", "执行次数", "详情")
        self.task_tree = ttk.Treeview(task_list_frame, columns=columns, show='headings', height=15)

        # 列宽和标题
        widths = [120, 150, 100, 80, 80, 200]
        for col, width in zip(columns, widths):
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=width, anchor=tk.CENTER if col != "详情" else tk.W)

        # 滚动条
        task_scrollbar = ttk.Scrollbar(task_list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=task_scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 日志区
        log_frame = tk.LabelFrame(right_panel, text="📄 运行日志", font=("Arial", 12, "bold"), bg='white', padx=5,
                                  pady=5)
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

        # 添加欢迎消息
        self.log_message("系统", "欢迎使用轻量级多任务调度器！")
        self.log_message("提示", "点击'启动调度器'开始，然后添加任务观察执行过程")

    def log_message(self, level, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "系统": "#3498db",
            "创建": "#9b59b6",
            "开始": "#f39c12",
            "完成": "#27ae60",
            "失败": "#e74c3c",
            "提示": "#1abc9c"
        }

        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"[{level}] ", level)
        self.log_text.insert(tk.END, f"{message}\n")

        # 配置标签颜色
        self.log_text.tag_config("timestamp", foreground="#95a5a6")
        self.log_text.tag_config(level, foreground=colors.get(level, "#ecf0f1"), font=("Consolas", 9, "bold"))

        self.log_text.see(tk.END)

    def start_scheduler(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("系统", "调度器已启动 🚀")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")

    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("系统", "调度器已停止 ⏸️")

    def add_quick_task(self, factory_method):
        """添加快速任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        try:
            if factory_method == "create_file_backup_task":
                task = TaskFactory.create_file_backup_task("C:\\Data", "D:\\Backup")
                self.scheduler.add_one_time_task(task, delay=2.0)
            elif factory_method == "create_matrix_multiply_task":
                task = TaskFactory.create_matrix_multiply_task(size=50)
                self.scheduler.add_periodic_task(task, interval=5.0)
            elif factory_method == "create_http_get_task":
                task = TaskFactory.create_http_get_task("https://i.chaoxing.com/base?t=1686812306230", "xuexitongtxt")
                self.scheduler.add_one_time_task(task, delay=0.0)
            elif factory_method == "create_reminder_task":
                task = TaskFactory.create_reminder_task("休息5分钟")
                self.scheduler.add_periodic_task(task, interval=15.0)
            elif factory_method == "create_random_stats_task":
                task = TaskFactory.create_random_stats_task(count=1000)
                self.scheduler.add_one_time_task(task, delay=3.0)

        except Exception as e:
            messagebox.showerror("错误", f"添加任务失败: {e}")

    def add_custom_task(self):
        """添加自定义任务"""
        if not self.scheduler.running:
            messagebox.showwarning("警告", "请先启动调度器！")
            return

        try:
            name = self.task_name_entry.get()
            duration = float(self.duration_entry.get())
            delay = float(self.delay_entry.get())
            task_type = self.task_type_var.get()

            task = CustomTask(name, duration)

            if task_type == "一次性":
                self.scheduler.add_one_time_task(task, delay=delay)
            else:
                interval = float(self.interval_entry.get())
                self.scheduler.add_periodic_task(task, interval=interval)

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("错误", f"添加任务失败: {e}")

    def update_task_status(self, event_type, task_id, task_name, details):
        """更新任务状态"""
        self.root.after(0, self._update_task_status_ui, event_type, task_id, task_name, details)

    def _update_task_status_ui(self, event_type, task_id, task_name, details):
        """在主线程中更新UI"""
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
    app = SchedulerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()