"""
主入口 - 演示项目3的所有要求
"""

import time
from scheduler import TaskScheduler, TaskFactory, ConsoleObserver


def main():
    """演示所有任务"""
    print("=" * 70)
    print("轻量级多任务调度器 - 项目3演示")
    print("包含：Factory、Command、Strategy、Observer四种设计模式")
    print("=" * 70)

    # 获取调度器单例
    scheduler = TaskScheduler()

    # 添加UI观察者（模拟UI层订阅任务状态）
    ui_observer = ConsoleObserver()
    scheduler.add_observer(ui_observer)

    try:
        # Task A - 文件备份（一次性延迟2秒）
        task_a = TaskFactory.create_file_backup_task("C:\\Data", "D:\\Backup")
        scheduler.add_one_time_task(task_a, delay=2.0)

        # Task B - 矩阵乘法（周期，每5秒）
        task_b = TaskFactory.create_matrix_multiply_task(size=50)  # 小矩阵演示
        scheduler.add_periodic_task(task_b, interval=5.0)

        # Task C - HTTP GET（立即执行）
        task_c = TaskFactory.create_http_get_task("https://api.github.com/zen", "zen.txt")
        scheduler.add_one_time_task(task_c, delay=0.0)

        # Task D - 课堂提醒（周期，演示用15秒）
        task_d = TaskFactory.create_reminder_task("休息5分钟")
        scheduler.add_periodic_task(task_d, interval=15.0)

        # Task E - 随机数统计（延迟3秒）
        task_e = TaskFactory.create_random_stats_task(count=1000)
        scheduler.add_one_time_task(task_e, delay=3.0)

        # 启动调度器
        scheduler.start()

        print("\n调度器运行中，按 Ctrl+C 停止...\n")

        # 运行20秒
        time.sleep(20)

        # 打印统计信息
        print("\n" + "=" * 70)
        print("统计信息:")
        stats = scheduler.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()