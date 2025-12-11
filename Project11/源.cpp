// ============================================================================
// 任务调度器系统 - 中文版本（使用 Unicode 避免乱码）
// 保存为 main.cpp
// ============================================================================

#include <Windows.h>
#include <CommCtrl.h>
#include <string>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <vector>
#include <functional>
#include <chrono>
#include <fstream>
#include <random>
#include <sstream>
#include <iomanip>

#pragma comment(lib, "comctl32.lib")
#pragma comment(linker, "/SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup")

// 字符串转换工具
std::wstring StringToWString(const std::string& str) {
    if (str.empty()) return std::wstring();
    int size = MultiByteToWideChar(CP_ACP, 0, str.c_str(), -1, NULL, 0);
    std::wstring wstr(size, 0);
    MultiByteToWideChar(CP_ACP, 0, str.c_str(), -1, &wstr[0], size);
    return wstr;
}

std::string WStringToString(const std::wstring& wstr) {
    if (wstr.empty()) return std::string();
    int size = WideCharToMultiByte(CP_ACP, 0, wstr.c_str(), -1, NULL, 0, NULL, NULL);
    std::string str(size, 0);
    WideCharToMultiByte(CP_ACP, 0, wstr.c_str(), -1, &str[0], size, NULL, NULL);
    return str;
}

// ============================================================================
// 1. 任务接口和工具类
// ============================================================================

class ITask {
public:
    virtual ~ITask() = default;
    virtual std::string GetName() const = 0;
    virtual void Execute() = 0;
};

class LogWriter {
private:
    std::ofstream logFile;
    static std::mutex logMutex;

public:
    LogWriter(const std::string& filename) {
        std::string fullPath = "D:\\project\\" + filename;
        logFile.open(fullPath, std::ios::app);
    }

    ~LogWriter() {
        if (logFile.is_open()) {
            logFile.close();
        }
    }

    void Write(const std::string& message) {
        std::lock_guard<std::mutex> lock(logMutex);
        if (logFile.is_open()) {
            auto now = std::chrono::system_clock::now();
            auto time = std::chrono::system_clock::to_time_t(now);
            struct tm timeinfo;
            localtime_s(&timeinfo, &time);

            char timeStr[32];
            strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);

            logFile << "[" << timeStr << "] " << message << std::endl;
        }
    }
};

std::mutex LogWriter::logMutex;

// ============================================================================
// 2. 具体任务实现
// ============================================================================

// Task A - 文件备份
class FileBackupTask : public ITask {
public:
    std::string GetName() const override {
        return "Task A - 文件备份";
    }

    void Execute() override {
        LogWriter log("task_log.txt");

        try {
            auto now = std::chrono::system_clock::now();
            auto time = std::chrono::system_clock::to_time_t(now);
            struct tm timeinfo;
            localtime_s(&timeinfo, &time);

            char dateStr[32];
            strftime(dateStr, sizeof(dateStr), "%Y%m%d_%H%M%S", &timeinfo);

            CreateDirectoryA("D:\\project", NULL);

            std::string backupName = "D:\\project\\backup_" + std::string(dateStr) + ".txt";

            std::ofstream backup(backupName);
            backup << "============ 文件备份记录 ============" << std::endl;
            backup << "备份时间: " << dateStr << std::endl;
            backup << "源目录: C:\\Data (模拟)" << std::endl;
            backup << "状态: 备份成功" << std::endl;
            backup << "====================================" << std::endl;
            backup.close();

            std::string msg = "Task A 执行成功！\n备份文件: " + backupName;
            log.Write("Task A 成功 - 备份: " + backupName);
            MessageBoxW(NULL, StringToWString(msg).c_str(), L"Task A - 文件备份", MB_OK | MB_ICONINFORMATION);
        }
        catch (const std::exception& e) {
            log.Write("Task A 失败: " + std::string(e.what()));
        }
    }
};

// Task B - 矩阵乘法（在窗口显示结果）
class MatrixMultiplyTask : public ITask {
public:
    std::string GetName() const override {
        return "Task B - 矩阵乘法";
    }

    void Execute() override {
        LogWriter log("task_log.txt");

        try {
            const int SIZE = 200;
            std::vector<std::vector<double>> A(SIZE, std::vector<double>(SIZE));
            std::vector<std::vector<double>> B(SIZE, std::vector<double>(SIZE));
            std::vector<std::vector<double>> C(SIZE, std::vector<double>(SIZE, 0));

            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(0.0, 1.0);

            // 生成随机矩阵
            for (int i = 0; i < SIZE; i++) {
                for (int j = 0; j < SIZE; j++) {
                    A[i][j] = dis(gen);
                    B[i][j] = dis(gen);
                }
            }

            auto start = std::chrono::high_resolution_clock::now();

            // 矩阵乘法计算
            for (int i = 0; i < SIZE; i++) {
                for (int j = 0; j < SIZE; j++) {
                    for (int k = 0; k < SIZE; k++) {
                        C[i][j] += A[i][k] * B[k][j];
                    }
                }
            }

            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

            // 显示部分结果矩阵（左上角 3x3）
            std::ostringstream oss;
            oss << std::fixed << std::setprecision(2);
            oss << "Task B - 矩阵乘法计算完成\n\n";
            oss << "矩阵规模: 200 x 200\n";
            oss << "计算耗时: " << duration.count() << " 毫秒\n\n";
            oss << "结果矩阵 C (左上角 3x3 部分):\n";
            for (int i = 0; i < 3; i++) {
                oss << "[ ";
                for (int j = 0; j < 3; j++) {
                    oss << std::setw(8) << C[i][j] << " ";
                }
                oss << "]\n";
            }

            std::string logMsg = "Task B 完成 - 200x200 矩阵乘法，耗时: " + std::to_string(duration.count()) + " ms";
            log.Write(logMsg);

            MessageBoxW(NULL, StringToWString(oss.str()).c_str(), L"Task B - 矩阵乘法结果", MB_OK | MB_ICONINFORMATION);
        }
        catch (const std::exception& e) {
            log.Write("Task B 失败: " + std::string(e.what()));
        }
    }
};

// Task C - HTTP GET（访问超星学习通）
class HttpGetTask : public ITask {
public:
    std::string GetName() const override {
        return "Task C - HTTP GET";
    }

    void Execute() override {
        LogWriter log("task_log.txt");

        try {
            std::string url = "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https%3A%2F%2Fi.chaoxing.com";

            std::ofstream outFile("D:\\project\\http_result.txt");
            outFile << "============ HTTP 请求记录 ============" << std::endl;
            outFile << "请求 URL: " << url << std::endl;
            outFile << "目标: 超星学习通登录页面" << std::endl;
            outFile << "状态: 访问受限（模拟）" << std::endl;
            outFile << "错误代码: 403 Forbidden" << std::endl;
            outFile << "说明: 模拟访问登录页面受限的情况" << std::endl;
            outFile << "=====================================" << std::endl;
            outFile.close();

            std::string msg = "Task C 完成！\n尝试访问超星学习通登录页面\n\n结果已保存到: D:\\project\\http_result.txt";
            log.Write("Task C 成功 - 访问: " + url);
            MessageBoxW(NULL, StringToWString(msg).c_str(), L"Task C - HTTP GET", MB_OK | MB_ICONWARNING);
        }
        catch (const std::exception& e) {
            log.Write("Task C 失败: " + std::string(e.what()));
        }
    }
};

// Task D - 课堂提醒
class ClassReminderTask : public ITask {
public:
    std::string GetName() const override {
        return "Task D - 课堂提醒";
    }

    void Execute() override {
        LogWriter log("task_log.txt");

        try {
            log.Write("Task D - 课堂提醒已触发");
            MessageBoxW(NULL, L"休息 5 分钟！\n\n保护眼睛，适当休息。",
                L"课堂提醒", MB_OK | MB_ICONINFORMATION);
        }
        catch (const std::exception& e) {
            log.Write("Task D 失败: " + std::string(e.what()));
        }
    }
};

// Task E - 随机数统计
class RandomStatsTask : public ITask {
public:
    std::string GetName() const override {
        return "Task E - 随机数统计";
    }

    void Execute() override {
        LogWriter log("task_log.txt");

        try {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution<> dis(0, 100);

            std::vector<int> numbers(1000);
            double sum = 0;

            for (int i = 0; i < 1000; i++) {
                numbers[i] = dis(gen);
                sum += numbers[i];
            }

            double mean = sum / 1000.0;

            double variance = 0;
            for (int num : numbers) {
                variance += (num - mean) * (num - mean);
            }
            variance /= 1000.0;

            std::ostringstream oss;
            oss << std::fixed << std::setprecision(2);
            oss << "Task E - 随机数统计结果\n\n";
            oss << "样本数量: 1000\n";
            oss << "取值范围: 0-100\n";
            oss << "均值: " << mean << "\n";
            oss << "方差: " << variance;

            log.Write("Task E 成功 - 均值: " + std::to_string(mean) +
                ", 方差: " + std::to_string(variance));

            MessageBoxW(NULL, StringToWString(oss.str()).c_str(), L"Task E - 随机数统计", MB_OK);
        }
        catch (const std::exception& e) {
            log.Write("Task E 失败: " + std::string(e.what()));
        }
    }
};

// ============================================================================
// 3. 工厂模式
// ============================================================================

class TaskFactory {
public:
    static const int FILE_BACKUP = 0;
    static const int MATRIX_MULTIPLY = 1;
    static const int HTTP_GET = 2;
    static const int CLASS_REMINDER = 3;
    static const int RANDOM_STATS = 4;

    static std::shared_ptr<ITask> CreateTask(int type) {
        switch (type) {
        case 0: return std::make_shared<FileBackupTask>();
        case 1: return std::make_shared<MatrixMultiplyTask>();
        case 2: return std::make_shared<HttpGetTask>();
        case 3: return std::make_shared<ClassReminderTask>();
        case 4: return std::make_shared<RandomStatsTask>();
        default: return nullptr;
        }
    }
};

// ============================================================================
// 4. 计划任务包装
// ============================================================================

class ScheduledTask {
public:
    std::shared_ptr<ITask> task;
    std::chrono::system_clock::time_point runTime;
    bool isPeriodic;
    int intervalSeconds;

    ScheduledTask(std::shared_ptr<ITask> t,
        std::chrono::system_clock::time_point rt,
        bool periodic = false,
        int interval = 0)
        : task(t), runTime(rt), isPeriodic(periodic), intervalSeconds(interval) {}

    bool operator>(const ScheduledTask& other) const {
        return runTime > other.runTime;
    }
};

// ============================================================================
// 5. 任务调度器
// ============================================================================

class TaskScheduler {
private:
    std::priority_queue<ScheduledTask, std::vector<ScheduledTask>, std::greater<ScheduledTask>> taskQueue;
    std::mutex queueMutex;
    std::condition_variable cv;
    bool stopFlag;
    std::thread workerThread;
    std::vector<std::function<void(std::string)>> observers;

    TaskScheduler() : stopFlag(false) {
        workerThread = std::thread(&TaskScheduler::WorkerLoop, this);
    }

    void WorkerLoop() {
        while (!stopFlag) {
            std::unique_lock<std::mutex> lock(queueMutex);

            if (taskQueue.empty()) {
                cv.wait(lock);
                continue;
            }

            auto now = std::chrono::system_clock::now();
            auto nextTask = taskQueue.top();

            if (nextTask.runTime <= now) {
                taskQueue.pop();
                lock.unlock();

                try {
                    NotifyObservers("开始执行: " + nextTask.task->GetName());
                    nextTask.task->Execute();
                    NotifyObservers("完成执行: " + nextTask.task->GetName());

                    if (nextTask.isPeriodic) {
                        nextTask.runTime = std::chrono::system_clock::now() +
                            std::chrono::seconds(nextTask.intervalSeconds);
                        AddTask(nextTask);
                    }
                }
                catch (const std::exception& e) {
                    LogWriter log("task_log.txt");
                    log.Write("任务执行异常: " + std::string(e.what()));
                    NotifyObservers("执行失败: " + nextTask.task->GetName());
                }
            }
            else {
                auto waitTime = nextTask.runTime - now;
                cv.wait_for(lock, waitTime);
            }
        }
    }

    void NotifyObservers(const std::string& message) {
        for (auto& observer : observers) {
            observer(message);
        }
    }

public:
    static TaskScheduler& Instance() {
        static TaskScheduler instance;
        return instance;
    }

    void AddTask(const ScheduledTask& task) {
        std::lock_guard<std::mutex> lock(queueMutex);
        taskQueue.push(task);
        cv.notify_one();
    }

    void AddObserver(std::function<void(std::string)> observer) {
        observers.push_back(observer);
    }

    ~TaskScheduler() {
        stopFlag = true;
        cv.notify_all();
        if (workerThread.joinable()) {
            workerThread.join();
        }
    }
};

// ============================================================================
// 6. 主窗口界面
// ============================================================================

#define ID_BTN_TASK_A    1001
#define ID_BTN_TASK_B    1002
#define ID_BTN_TASK_C    1003
#define ID_BTN_TASK_D    1004
#define ID_BTN_TASK_E    1005
#define ID_LIST_LOG      1006
#define ID_BTN_CLEAR_LOG 1007
#define ID_BTN_VIEW_LOG  1008

class MainDialog {
private:
    HWND hwnd;
    HWND listLog;

    void AddLogMessage(const std::string& message) {
        if (listLog) {
            SendMessageW(listLog, LB_ADDSTRING, 0, (LPARAM)StringToWString(message).c_str());
            int count = SendMessage(listLog, LB_GETCOUNT, 0, 0);
            SendMessage(listLog, LB_SETTOPINDEX, count - 1, 0);
        }
    }

public:
    void Create(HINSTANCE hInstance) {
        WNDCLASSEXW wc = { 0 };
        wc.cbSize = sizeof(WNDCLASSEXW);
        wc.lpfnWndProc = StaticWndProc;
        wc.hInstance = hInstance;
        wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
        wc.lpszClassName = L"TaskSchedulerClass";
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        RegisterClassExW(&wc);

        hwnd = CreateWindowExW(
            0, L"TaskSchedulerClass", L"轻量级任务调度器",
            WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, 750, 600,
            NULL, NULL, hInstance, this);

        HFONT hFont = CreateFontW(16, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            GB2312_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"微软雅黑");

        HWND hTitle = CreateWindowW(L"STATIC", L"任务调度系统",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            20, 15, 300, 25, hwnd, NULL, hInstance, NULL);
        SendMessage(hTitle, WM_SETFONT, (WPARAM)hFont, TRUE);

        CreateWindowW(L"BUTTON", L"Task A - 文件备份\n(延迟 5 秒)",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_MULTILINE,
            20, 50, 140, 50, hwnd, (HMENU)ID_BTN_TASK_A, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"Task B - 矩阵乘法\n(周期 5 秒)",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_MULTILINE,
            170, 50, 140, 50, hwnd, (HMENU)ID_BTN_TASK_B, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"Task C - HTTP GET\n(立即执行)",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_MULTILINE,
            320, 50, 140, 50, hwnd, (HMENU)ID_BTN_TASK_C, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"Task D - 课堂提醒\n(周期 1 分钟)",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_MULTILINE,
            470, 50, 140, 50, hwnd, (HMENU)ID_BTN_TASK_D, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"Task E - 随机统计\n(延迟 10 秒)",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_MULTILINE,
            20, 110, 140, 50, hwnd, (HMENU)ID_BTN_TASK_E, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"清空日志",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            320, 110, 140, 50, hwnd, (HMENU)ID_BTN_CLEAR_LOG, hInstance, NULL);

        CreateWindowW(L"BUTTON", L"查看日志文件",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            470, 110, 140, 50, hwnd, (HMENU)ID_BTN_VIEW_LOG, hInstance, NULL);

        CreateWindowW(L"STATIC", L"执行日志（实时更新）：",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            20, 175, 300, 20, hwnd, NULL, hInstance, NULL);

        listLog = CreateWindowExW(
            WS_EX_CLIENTEDGE, L"LISTBOX", L"",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY,
            20, 200, 690, 330, hwnd, (HMENU)ID_LIST_LOG, hInstance, NULL);

        TaskScheduler::Instance().AddObserver([this](std::string msg) {
            PostMessageA(hwnd, WM_USER + 1, 0, (LPARAM)new std::string(msg));
            });

        AddLogMessage("系统已启动，等待任务调度...");
        AddLogMessage("提示：点击上方按钮添加任务");

        ShowWindow(hwnd, SW_SHOW);
        UpdateWindow(hwnd);
    }

    static LRESULT CALLBACK StaticWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
        MainDialog* pThis = nullptr;

        if (msg == WM_NCCREATE) {
            CREATESTRUCT* pCreate = (CREATESTRUCT*)lParam;
            pThis = (MainDialog*)pCreate->lpCreateParams;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)pThis);
            pThis->hwnd = hwnd;
        }
        else {
            pThis = (MainDialog*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
        }

        if (pThis) {
            return pThis->WndProc(msg, wParam, lParam);
        }
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }

    LRESULT WndProc(UINT msg, WPARAM wParam, LPARAM lParam) {
        switch (msg) {
        case WM_COMMAND: {
            int id = LOWORD(wParam);
            switch (id) {
            case ID_BTN_TASK_A: {
                auto task = TaskFactory::CreateTask(TaskFactory::FILE_BACKUP);
                auto runTime = std::chrono::system_clock::now() + std::chrono::seconds(5);
                TaskScheduler::Instance().AddTask(ScheduledTask(task, runTime));
                AddLogMessage("已添加 Task A - 将在 5 秒后执行");
                break;
            }
            case ID_BTN_TASK_B: {
                auto task = TaskFactory::CreateTask(TaskFactory::MATRIX_MULTIPLY);
                auto runTime = std::chrono::system_clock::now();
                TaskScheduler::Instance().AddTask(ScheduledTask(task, runTime, true, 5));
                AddLogMessage("已添加 Task B - 每 5 秒执行一次（周期任务）");
                break;
            }
            case ID_BTN_TASK_C: {
                auto task = TaskFactory::CreateTask(TaskFactory::HTTP_GET);
                auto runTime = std::chrono::system_clock::now();
                TaskScheduler::Instance().AddTask(ScheduledTask(task, runTime));
                AddLogMessage("已添加 Task C - 立即执行");
                break;
            }
            case ID_BTN_TASK_D: {
                auto task = TaskFactory::CreateTask(TaskFactory::CLASS_REMINDER);
                auto runTime = std::chrono::system_clock::now();
                TaskScheduler::Instance().AddTask(ScheduledTask(task, runTime, true, 60));
                AddLogMessage("已添加 Task D - 每 1 分钟执行一次（周期任务）");
                break;
            }
            case ID_BTN_TASK_E: {
                auto task = TaskFactory::CreateTask(TaskFactory::RANDOM_STATS);
                auto runTime = std::chrono::system_clock::now() + std::chrono::seconds(10);
                TaskScheduler::Instance().AddTask(ScheduledTask(task, runTime));
                AddLogMessage("已添加 Task E - 将在 10 秒后执行");
                break;
            }
            case ID_BTN_CLEAR_LOG: {
                SendMessage(listLog, LB_RESETCONTENT, 0, 0);
                AddLogMessage("日志已清空");
                break;
            }
            case ID_BTN_VIEW_LOG: {
                ShellExecuteA(NULL, "open", "D:\\project\\task_log.txt", NULL, NULL, SW_SHOW);
                break;
            }
            }
            break;
        }
        case WM_USER + 1: {
            std::string* msg = (std::string*)lParam;
            AddLogMessage(*msg);
            delete msg;
            break;
        }
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
        }
        return 0;
    }
};

// ============================================================================
// 7. 程序入口
// ============================================================================

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    CreateDirectoryA("D:\\project", NULL);

    MainDialog dialog;
    dialog.Create(hInstance);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}

int main() {
    return WinMain(GetModuleHandle(NULL), NULL, GetCommandLineA(), SW_SHOW);
}