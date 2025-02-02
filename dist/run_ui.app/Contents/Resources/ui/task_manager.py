from PyQt5.QtCore import QObject, pyqtSignal, QThread
import importlib.util
import sys
import os
import traceback
from datetime import datetime

class TaskThread(QThread):
    """任务执行线程"""
    log_signal = pyqtSignal(str)  # 日志信号
    finished_signal = pyqtSignal(str)  # 完成信号
    error_signal = pyqtSignal(str, str)  # 错误信号，传递任务名和错误信息
    stop_finished = pyqtSignal(str)  # 添加停止完成信号

    def __init__(self, task_name, task_module):
        super().__init__()
        self.task_name = task_name
        self.task_module = task_module
        self._stop_flag = False
        self._original_stdout = None
        self._original_stderr = None
        self._log_handler = None
        self._force_stop = False

    def run(self):
        """运行任务"""
        try:
            # 保存原始的标准输出和错误输出
            self._original_stdout = sys.stdout
            self._original_stderr = sys.stderr
            
            # 创建日志处理器
            self._log_handler = self.LogHandler(self.log_signal, self)
            sys.stdout = self._log_handler
            sys.stderr = self._log_handler

            # 执行任务
            if hasattr(self.task_module, 'main'):
                # 注入停止检查函数到任务模块
                def should_stop():
                    if self._force_stop:
                        raise SystemExit("Task forcefully stopped")
                    return self._stop_flag

                setattr(self.task_module, 'should_stop', should_stop)
                
                try:
                    if hasattr(self.task_module, 'is_continuous') and self.task_module.is_continuous:
                        while not should_stop():
                            self.task_module.main()
                            if should_stop():
                                break
                    else:
                        if not should_stop():
                            self.task_module.main()
                except (SystemExit, KeyboardInterrupt):
                    self.log_signal.emit("任务被强制停止")
                except AttributeError:
                    # 如果没有is_continuous属性，默认执行一次
                    if not should_stop():
                        self.task_module.main()
            else:
                self.log_signal.emit(f"错误：{self.task_name} 任务模块中未找到 main 函数")

        except Exception as e:
            if not self._stop_flag:  # 只在非停止状态下报告错误
                error_msg = f"任务执行出错: {str(e)}\n{traceback.format_exc()}"
                self.log_signal.emit(error_msg)
                if '连接已断开' in str(e) or '连接已断开' in traceback.format_exc():
                    self.error_signal.emit(self.task_name, error_msg)
        finally:
            self._restore_stdout()
            if not self._stop_flag:  # 只在非停止状态下发送完成信号
                self.finished_signal.emit(self.task_name)
            else:
                self.stop_finished.emit(self.task_name)

    def _restore_stdout(self):
        """恢复标准输出"""
        if self._original_stdout:
            sys.stdout = self._original_stdout
            self._original_stdout = None
        if self._original_stderr:
            sys.stderr = self._original_stderr
            self._original_stderr = None
        if self._log_handler:
            self._log_handler.flush()
            self._log_handler = None

    def stop(self):
        """停止任务"""
        self._stop_flag = True
        self.log_signal.emit("正在停止任务...")
        self._restore_stdout()

    def force_stop(self):
        """强制停止任务"""
        self._force_stop = True
        self._stop_flag = True
        self.log_signal.emit("正在强制停止任务...")
        self._restore_stdout()

    class LogHandler:
        def __init__(self, signal, thread):
            self.signal = signal
            self.thread = thread
            self.buffer = ""

        def write(self, text):
            if text.strip():
                self.buffer += text
                if '\n' in self.buffer or len(self.buffer) > 1024:
                    self.flush()

        def flush(self):
            if self.buffer.strip():
                text = self.buffer.strip()
                self.signal.emit(text)
                # 检查是否包含连接断开的错误
                if '连接已断开' in text:
                    self.thread.error_signal.emit(self.thread.task_name, text)
            self.buffer = ""

class MonitorThread(QThread):
    """监视任务停止的线程"""
    def __init__(self, task_manager, task_name, task_thread):
        super().__init__()
        self.task_manager = task_manager
        self.task_name = task_name
        self.task_thread = task_thread
        # 保持对监视线程的引用
        if not hasattr(task_manager, '_monitors'):
            task_manager._monitors = {}
        task_manager._monitors[task_name] = self

    def run(self):
        try:
            # 发送停止信号
            self.task_thread.stop()
            
            # 等待任务结束
            if not self.task_thread.wait(3000):  # 等待3秒
                self.task_manager.log_signal.emit("正在强制终止任务...")
                self.task_thread.force_stop()
                if not self.task_thread.wait(2000):  # 再等待2秒
                    self.task_thread.terminate()
                    if not self.task_thread.wait(1000):  # 最后等待1秒
                        self.task_manager.log_signal.emit("任务终止超时")
            
            # 断开信号连接
            try:
                self.task_thread.log_signal.disconnect()
                self.task_thread.finished_signal.disconnect()
                self.task_thread.error_signal.disconnect()
                self.task_thread.stop_finished.disconnect()
            except Exception:
                pass  # 忽略断开连接时的错误
            
            # 从任务列表中移除
            if self.task_name in self.task_manager.tasks:
                del self.task_manager.tasks[self.task_name]
            
            # 安全清理任务线程
            self.task_thread.deleteLater()
            self.task_manager.log_signal.emit(f"任务 {self.task_name} 已停止")
            
        except Exception as e:
            error_msg = f"停止任务监视器出错: {str(e)}\n{traceback.format_exc()}"
            self.task_manager.log_signal.emit(error_msg)
        finally:
            # 从监视器列表中移除
            if hasattr(self.task_manager, '_monitors') and self.task_name in self.task_manager._monitors:
                del self.task_manager._monitors[self.task_name]
            # 确保监视器线程自己也被清理
            self.deleteLater()

class TaskManager(QObject):
    """任务管理器"""
    log_signal = pyqtSignal(str)  # 日志信号
    task_finished = pyqtSignal(str)  # 任务完成信号

    def __init__(self):
        super().__init__()
        self.tasks = {}  # 存储正在运行的任务线程
        self._monitors = {}  # 存储监视线程

    def start_task(self, task_name, task_file):
        """启动任务"""
        if task_name in self.tasks and self.tasks[task_name].isRunning():
            self.log_signal.emit(f"任务 {task_name} 已在运行中")
            return False

        try:
            # 获取任务文件的完整路径
            examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
            task_path = os.path.join(examples_dir, task_file)

            # 动态导入任务模块
            spec = importlib.util.spec_from_file_location(task_name, task_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 创建并启动任务线程
            thread = TaskThread(task_name, module)
            thread.log_signal.connect(self.log_signal.emit)  # 连接日志信号
            thread.finished_signal.connect(self.on_task_finished)  # 连接完成信号
            thread.error_signal.connect(self.on_task_error)  # 连接错误信号
            thread.stop_finished.connect(self.on_task_finished)  # 连接停止完成信号
            thread.start()

            # 保存任务线程
            self.tasks[task_name] = thread
            self.log_signal.emit(f"任务 {task_name} 已启动")
            return True

        except Exception as e:
            error_msg = f"启动任务失败: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(error_msg)
            return False

    def stop_task(self, task_name):
        """停止任务"""
        try:
            if task_name in self.tasks:
                thread = self.tasks[task_name]
                if thread.isRunning():
                    self.log_signal.emit(f"正在停止任务: {task_name}")
                    
                    # 创建监视线程来处理停止过程
                    monitor = MonitorThread(self, task_name, thread)
                    monitor.start()
                    return True
                else:
                    self.log_signal.emit(f"任务 {task_name} 未在运行")
                    if task_name in self.tasks:
                        del self.tasks[task_name]
                    return True
            return False
        except Exception as e:
            error_msg = f"停止任务失败: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(error_msg)
            return False

    def on_task_error(self, task_name, error_msg):
        """处理任务错误"""
        self.log_signal.emit(f"任务错误: {error_msg}")
        if '连接已断开' in error_msg:
            self.stop_task(task_name)

    def on_task_finished(self, task_name):
        """任务完成处理"""
        try:
            if task_name in self.tasks:
                thread = self.tasks[task_name]
                thread.deleteLater()
                del self.tasks[task_name]
            self.task_finished.emit(task_name)
        except Exception as e:
            self.log_signal.emit(f"处理任务完成事件失败: {str(e)}")

    def __del__(self):
        """析构函数，确保所有任务都被正确停止"""
        try:
            # 停止所有任务
            for task_name in list(self.tasks.keys()):
                self.stop_task(task_name)
            
            # 等待所有监视器完成
            for monitor in list(self._monitors.values()):
                monitor.wait()
        except Exception:
            pass  # 忽略清理过程中的错误 