from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QTimeEdit, QCheckBox, QMessageBox, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QTime, QSize
from qfluentwidgets import (MSFluentWindow, NavigationInterface, NavigationItemPosition, 
                          FluentIcon, ScrollArea, PushButton, TextEdit, CardWidget,
                          StrongBodyLabel, BodyLabel, InfoBar, InfoBarPosition, ComboBox,
                          LineEdit)
from core.multi_browser_executor import MultiBrowserExecutor
from core.task import Task
import os
import subprocess
import signal
import threading
from PyQt5.QtGui import QIcon, QFont

class TaskCard(CardWidget):
    """任务卡片组件"""
    task_selected = pyqtSignal(str)  # 任务选中信号

    def __init__(self, task_name, task_desc="", parent=None):
        super().__init__(parent)
        self.task_name = task_name
        self.is_selected = False
        self.setup_ui(task_name, task_desc)
        
    def setup_ui(self, task_name, task_desc):
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(0)  # 将标题和描述间距设置为0
        
        # 创建标签
        self.name_label = StrongBodyLabel(task_name, self)
        self.desc_label = BodyLabel(task_desc if task_desc else "暂无描述", self)
        
        # 设置字体大小和样式
        font = self.name_label.font()
        font.setPointSize(14)  # 标题字体
        self.name_label.setFont(font)
        
        font = self.desc_label.font()
        font.setPointSize(12)  # 描述字体
        self.desc_label.setFont(font)
        
        # 设置描述标签自动换行
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet('color: #666666; margin-top: -2px;')  # 添加负边距进一步减小间距
        
        # 添加到布局
        layout.addWidget(self.name_label)
        layout.addWidget(self.desc_label)
        
        # 设置卡片样式
        self.setObjectName('taskCard')
        self.setFixedHeight(90)  # 将卡片高度从100减小到90
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not self.is_selected:  # 只有在未选中状态下才发送信号
            self.is_selected = True
            self.update_style()
            self.task_selected.emit(self.task_name)
        
    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                #taskCard {
                    background-color: rgb(230, 242, 255);
                    border: 1px solid rgb(51, 153, 255);
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                #taskCard {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
            
    def deselect(self):
        if self.is_selected:
            self.is_selected = False
            self.update_style()

class TaskThread(QThread):
    """任务执行线程"""
    output_ready = pyqtSignal(str)  # 输出信号
    error_ready = pyqtSignal(str)   # 错误信号
    finished = pyqtSignal(int)      # 完成信号，携带返回码

    def __init__(self, task_path, env):
        super().__init__()
        self.task_path = task_path
        self.env = env
        self.process = None
        self._stop_event = threading.Event()

    def run(self):
        try:
            # 启动进程
            self.process = subprocess.Popen(
                ['python', self.task_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env,
                bufsize=1,  # 行缓冲
                universal_newlines=True  # 使用通用换行符
            )

            # 创建读取输出的线程
            stdout_thread = threading.Thread(target=self._read_output, args=(self.process.stdout, self.output_ready))
            stderr_thread = threading.Thread(target=self._read_output, args=(self.process.stderr, self.error_ready))
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()

            # 等待进程结束或停止信号
            while True:
                if self._stop_event.is_set():
                    # 在macOS上使用SIGTERM终止进程
                    try:
                        self.process.terminate()
                        # 等待一段时间后如果进程还在运行，则强制结束
                        try:
                            self.process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                    except:
                        # 如果terminate失败，直接使用kill
                        try:
                            self.process.kill()
                        except:
                            pass
                    break

                # 检查进程是否已结束
                if self.process.poll() is not None:
                    break
                    
                # 短暂休眠，避免CPU占用过高
                self.msleep(100)

            # 等待输出读取线程结束
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

            # 发送完成信号
            self.finished.emit(self.process.returncode if self.process.returncode is not None else -1)

        except Exception as e:
            self.error_ready.emit(str(e))
            self.finished.emit(-1)

    def _read_output(self, pipe, signal):
        """读取输出的线程函数"""
        try:
            for line in iter(pipe.readline, ''):
                if self._stop_event.is_set():
                    break
                if line:
                    signal.emit(line.strip())
        except:
            pass
        finally:
            pipe.close()

    def stop(self):
        """停止任务"""
        self._stop_event.set()

class TaskConfig:
    """任务配置类"""
    def __init__(self):
        self.scheduled_time = QTime.currentTime()  # 计划执行时间
        self.is_repeat_enabled = False  # 是否启用重复执行
        self.repeat_type = 'minutes'  # 重复类型：'minutes' 或 'days'
        self.repeat_interval = 60  # 重复间隔
        self.is_enabled = False  # 是否启用该任务

class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.executor = MultiBrowserExecutor()
        self.task = None
        self.task_cards = {}
        self.task_configs = {}  # 任务配置字典
        self.selected_task = None
        self.current_task = None
        self.task_thread = None  # 任务线程
        self.timer = QTimer()  # 定时器
        self.timer.timeout.connect(self.on_timer_timeout)
        
        # 设置应用名称
        self.app_name = "蓝精灵"
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            # 创建图标并设置多个尺寸
            icon = QIcon()
            # 增加更大的尺寸支持
            sizes = [16, 24, 32, 48, 64, 128, 256, 512, 1024, 2048]
            for size in sizes:
                icon.addFile(icon_path, QSize(size, size))
            
            # 设置窗口图标
            self.setWindowIcon(icon)
            # 设置应用程序图标
            from PyQt5.QtWidgets import QApplication
            QApplication.setWindowIcon(icon)
        
        # 设置窗口属性
        self.resize(1200, 800)
        self.setWindowTitle(self.app_name)
        
        # 初始化界面
        self.init_interface()
        
    def init_interface(self):
        # 创建任务界面
        self.init_task_interface()
        
        # 创建设置界面
        self.init_settings_interface()
        
        # 初始化导航栏
        self.init_navigation()
        
        # 设置窗口样式
        self.setStyleSheet("""
            MainWindow {
                background-color: white;
            }
            NavigationInterface {
                background-color: rgb(243, 243, 243);
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            /* 按钮图标颜色 */
            PushButton[class="success-button"] QIcon {
                fill: white;
            }
            PushButton[class="danger-button"] QIcon {
                fill: white;
            }
            
            /* 按钮禁用状态图标颜色 */
            PushButton:disabled QIcon {
                fill: #95a5a6;
            }
        """)

    def init_navigation(self):
        """初始化导航栏"""
        self.navigationInterface.setFixedWidth(64)  # 增加导航栏宽度到64
        
        # 添加导航按钮
        self.addSubInterface(
            self.task_interface,
            icon=FluentIcon.ROBOT,
            text='任务',
            position=NavigationItemPosition.TOP
        )
        
        self.addSubInterface(
            self.settings_interface,
            icon=FluentIcon.SETTING,
            text='设置',
            position=NavigationItemPosition.TOP
        )
        
        # 设置导航栏样式
        self.navigationInterface.setStyleSheet("""
            NavigationInterface {
                background-color: rgb(243, 243, 243);
                border: none;
                padding: 0;
            }
            NavigationInterface::item {
                height: 64px;
                width: 64px;
                padding: 0;
                margin: 0;
            }
            NavigationInterface::item:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            NavigationInterface::item:selected {
                background-color: rgba(0, 0, 0, 0.1);
            }
            NavigationInterface::item QToolButton {
                width: 64px;
                height: 64px;
                padding: 0;
                margin: 0;
                border: none;
                qproperty-toolButtonStyle: ToolButtonTextUnderIcon;
                qproperty-iconSize: QSize(36, 36);  /* 增加图标大小 */
            }
            NavigationInterface::item QToolButton QWidget {
                background: transparent;
            }
            NavigationInterface::item QToolButton QLabel {
                font-size: 14px;  /* 增加字体大小 */
                margin: 0;
                padding: 0;
                color: #666666;
            }
            NavigationInterface::item QToolButton > QWidget > QWidget:first {
                margin: 6px 0 2px 0;  /* 调整图标和文字的间距 */
            }
        """)
        
        # 设置默认选中的页面
        self.navigationInterface.setCurrentItem(self.task_interface.objectName())

    def init_task_interface(self):
        # 创建任务管理界面
        self.task_interface = QWidget()
        self.task_interface.setObjectName('taskInterface')
        
        # 创建主布局
        main_layout = QHBoxLayout(self.task_interface)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧任务列表区域
        task_list_container = QWidget()
        task_list_container.setObjectName('taskListContainer')
        task_list_container.setStyleSheet("""
            #taskListContainer {
                background-color: rgb(248, 249, 250);
                border-right: 1px solid #e0e0e0;
            }
        """)
        task_list_layout = QVBoxLayout(task_list_container)
        task_list_layout.setContentsMargins(16, 16, 16, 16)
        task_list_layout.setSpacing(16)
        
        # 创建滚动区域
        self.scroll = ScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName('taskScroll')
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建任务内容区域
        self.task_content = QWidget()
        self.task_content.setObjectName('taskContent')
        self.task_content.setStyleSheet("""
            #taskContent {
                background-color: rgb(248, 249, 250);
            }
        """)
        self.task_content_layout = QVBoxLayout(self.task_content)
        self.task_content_layout.setSpacing(16)  # 增加任务卡片之间的间距
        self.task_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.task_content)
        
        task_list_layout.addWidget(self.scroll)
        
        # 设置左侧区域的宽度
        task_list_container.setFixedWidth(350)  # 增加列表宽度
        
        # 创建右侧控制和日志区域
        control_container = QWidget()
        control_container.setObjectName('controlContainer')
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(24, 24, 24, 24)
        control_layout.setSpacing(16)
        
        # 添加标题
        control_title = StrongBodyLabel('任务控制', control_container)
        control_title.setObjectName('controlTitle')
        font = control_title.font()
        font.setPointSize(16)
        control_title.setFont(font)
        control_layout.addWidget(control_title)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.start_button = PushButton('开始任务', self)
        self.start_button.setEnabled(False)  # 初始状态禁用
        # 设置开始按钮的样式
        self.start_button.setStyleSheet("""
            PushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 15px;
                text-align: center;
                font-weight: 500;
            }
            PushButton:hover {
                background-color: #45a049;
            }
            PushButton:pressed {
                background-color: #3d8b40;
                margin: 1px 1px -1px -1px;
            }
            PushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        
        self.stop_button = PushButton('停止任务', self)
        self.stop_button.setEnabled(False)  # 初始状态禁用
        # 设置停止按钮的样式
        self.stop_button.setStyleSheet("""
            PushButton {
                background-color: #f44336;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 15px;
                text-align: center;
                font-weight: 500;
            }
            PushButton:hover {
                background-color: #e53935;
            }
            PushButton:pressed {
                background-color: #d32f2f;
                margin: 1px 1px -1px -1px;
            }
            PushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        
        # 设置按钮大小
        self.start_button.setFixedSize(120, 36)
        self.stop_button.setFixedSize(120, 36)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        # 创建日志区域
        log_title = StrongBodyLabel('执行日志', control_container)
        font = log_title.font()
        font.setPointSize(14)
        log_title.setFont(font)
        
        self.log_text = TextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            TextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                background-color: rgb(250, 250, 250);
            }
        """)
        
        # 添加到控制布局
        control_layout.addLayout(button_layout)
        control_layout.addSpacing(16)
        control_layout.addWidget(log_title)
        control_layout.addWidget(self.log_text)
        
        # 添加定时任务设置区域
        schedule_layout = QVBoxLayout()
        schedule_layout.setSpacing(8)
        
        # 启用任务复选框
        self.enable_task_checkbox = QCheckBox('启用任务', self)
        self.enable_task_checkbox.setEnabled(False)  # 初始状态禁用
        self.enable_task_checkbox.setVisible(False)  # 初始状态隐藏
        
        # 时间选择器
        time_container = QWidget()
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_label = QLabel('执行时间:', self)
        self.time_edit = QTimeEdit(self)
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setEnabled(False)  # 初始状态禁用
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        time_container.setVisible(False)  # 初始状态隐藏
        
        # 重复执行设置
        repeat_layout = QHBoxLayout()
        self.repeat_checkbox = QCheckBox('重复执行', self)
        self.repeat_checkbox.setEnabled(False)
        self.repeat_checkbox.setVisible(False)  # 初始状态隐藏
        
        # 重复类型选择
        self.repeat_type_minutes = QCheckBox('分钟', self)
        self.repeat_type_days = QCheckBox('天', self)
        self.repeat_type_minutes.setEnabled(False)
        self.repeat_type_days.setEnabled(False)
        self.repeat_type_minutes.setVisible(False)  # 初始状态隐藏
        self.repeat_type_days.setVisible(False)  # 初始状态隐藏
        
        # 间隔输入
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(1440)
        self.interval_spinbox.setValue(60)
        self.interval_spinbox.setSuffix(" 分钟")
        self.interval_spinbox.setEnabled(False)
        self.interval_spinbox.setVisible(False)  # 初始状态隐藏
        
        repeat_layout.addWidget(self.repeat_checkbox)
        repeat_layout.addWidget(self.repeat_type_minutes)
        repeat_layout.addWidget(self.repeat_type_days)
        repeat_layout.addWidget(self.interval_spinbox)
        repeat_layout.addStretch()
        
        # 添加到定时任务布局
        schedule_layout.addWidget(self.enable_task_checkbox)
        schedule_layout.addWidget(time_container)
        schedule_layout.addLayout(repeat_layout)
        
        # 添加到控制布局
        control_layout.addLayout(schedule_layout)
        control_layout.addLayout(button_layout)
        control_layout.addWidget(log_title)
        control_layout.addWidget(self.log_text)
        control_layout.addStretch()
        
        # 设置信号连接
        self.setup_schedule_signals()
        
        # 添加到主布局
        main_layout.addWidget(task_list_container)
        main_layout.addWidget(control_container)
        
        # 添加任务列表
        self.add_tasks()
        
        # 设置信号连接
        self.setup_signals()

    def init_settings_interface(self):
        """初始化设置界面"""
        self.settings_interface = QWidget()
        self.settings_interface.setObjectName('settingsInterface')
        
        # 创建主布局
        layout = QVBoxLayout(self.settings_interface)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 添加标题
        title = StrongBodyLabel('系统设置', self)
        title.setObjectName('settingsTitle')
        font = title.font()
        font.setPointSize(16)
        title.setFont(font)
        layout.addWidget(title)
        
        # 添加定时任务设置
        schedule_group = QWidget()
        schedule_layout = QVBoxLayout(schedule_group)
        schedule_layout.setContentsMargins(0, 0, 0, 16)
        schedule_layout.setSpacing(8)
        
        schedule_title = StrongBodyLabel('定时任务', self)
        schedule_title.setFont(QFont(schedule_title.font().family(), 14))
        schedule_layout.addWidget(schedule_title)
        
        self.enable_schedule_checkbox = QCheckBox('启用定时任务功能', self)
        self.enable_schedule_checkbox.setChecked(False)
        schedule_layout.addWidget(self.enable_schedule_checkbox)
        
        desc = BodyLabel('启用后，任务界面将显示定时任务相关的配置选项', self)
        desc.setStyleSheet('color: #666666;')
        schedule_layout.addWidget(desc)
        
        layout.addWidget(schedule_group)
        
        # 添加浏览器设置
        browser_group = QWidget()
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setContentsMargins(0, 0, 0, 16)
        browser_layout.setSpacing(8)
        
        browser_title = StrongBodyLabel('浏览器设置', self)
        browser_title.setFont(QFont(browser_title.font().family(), 14))
        browser_layout.addWidget(browser_title)
        
        # 浏览器选择
        browser_select_layout = QHBoxLayout()
        browser_label = BodyLabel('默认浏览器:', self)
        browser_select_layout.addWidget(browser_label)
        
        self.browser_combo = ComboBox(self)
        self.browser_combo.addItems(['ADS指纹浏览器', '比特浏览器', '本地谷歌'])
        self.browser_combo.setFixedWidth(200)
        browser_select_layout.addWidget(self.browser_combo)
        browser_select_layout.addStretch()
        
        browser_layout.addLayout(browser_select_layout)
        
        # 浏览器说明
        browser_desc = BodyLabel('选择任务执行时使用的默认浏览器', self)
        browser_desc.setStyleSheet('color: #666666;')
        browser_layout.addWidget(browser_desc)
        
        # 添加分隔线
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet('background-color: #e0e0e0;')
        browser_layout.addWidget(separator)
        browser_layout.addSpacing(8)
        
        # 任务浏览器分组设置
        group_select_layout = QHBoxLayout()
        group_label = BodyLabel('任务浏览器:', self)
        group_select_layout.addWidget(group_label)
        
        self.group_combo = ComboBox(self)
        self.group_combo.addItems(['全部', '指定分组'])
        self.group_combo.setFixedWidth(200)
        self.group_combo.currentTextChanged.connect(self.on_group_selection_changed)
        group_select_layout.addWidget(self.group_combo)
        
        # 分组名称输入框
        self.group_name_input = LineEdit(self)
        self.group_name_input.setPlaceholderText('请输入分组名称')
        self.group_name_input.setFixedWidth(200)
        self.group_name_input.setFixedHeight(32)
        self.group_name_input.setStyleSheet("""
            LineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px 12px;
                background-color: white;
                font-size: 13px;
            }
            LineEdit:hover {
                border-color: #bfdaf9;
                background-color: rgb(249, 252, 255);
            }
            LineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        self.group_name_input.setVisible(False)  # 初始隐藏
        group_select_layout.addWidget(self.group_name_input)
        group_select_layout.addStretch()
        
        browser_layout.addLayout(group_select_layout)
        
        # 分组说明
        group_desc = BodyLabel('选择任务执行时使用的浏览器分组，指定分组需要输入分组名称', self)
        group_desc.setStyleSheet('color: #666666;')
        browser_layout.addWidget(group_desc)
        
        layout.addWidget(browser_group)
        
        # 添加底部空白
        layout.addStretch()
        
        # 连接信号
        self.enable_schedule_checkbox.stateChanged.connect(self.on_schedule_enabled_changed)
        self.browser_combo.currentTextChanged.connect(self.on_browser_changed)
        self.group_name_input.textChanged.connect(self.on_group_name_changed)
        
    def on_schedule_enabled_changed(self, state):
        """定时任务功能启用状态改变"""
        is_enabled = state == Qt.Checked
        # 更新任务界面中定时任务相关控件的可见性
        self.enable_task_checkbox.setVisible(is_enabled)
        self.time_edit.setVisible(is_enabled)
        self.time_edit.parent().setVisible(is_enabled)  # 时间标签的父容器
        self.repeat_checkbox.setVisible(is_enabled)
        self.repeat_type_minutes.setVisible(is_enabled)
        self.repeat_type_days.setVisible(is_enabled)
        self.interval_spinbox.setVisible(is_enabled)
        
        if not is_enabled:
            # 如果禁用了定时任务功能，需要处理已启用的定时任务
            self.timer.stop()  # 停止定时器
            # 取消所有任务的定时执行
            for task_name, config in self.task_configs.items():
                if config.is_enabled:
                    config.is_enabled = False
                    self.add_log(f"任务 {task_name} 的定时执行已取消（定时任务功能已禁用）", 'system')
            
            # 如果当前有选中的任务，更新其复选框状态
            if self.selected_task:
                self.enable_task_checkbox.blockSignals(True)
                self.enable_task_checkbox.setChecked(False)
                self.enable_task_checkbox.blockSignals(False)
                # 如果当前没有任务在执行，启用开始按钮
                if not self.current_task:
                    self.start_button.setEnabled(True)
                    self.stop_button.setEnabled(False)

    def get_available_tasks(self):
        """获取可用的任务列表"""
        tasks = []
        try:
            examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
            if os.path.exists(examples_dir):
                for file in os.listdir(examples_dir):
                    if file.startswith('run_') and file.endswith('.py'):
                        task_name = file[4:-3].replace('_', ' ').title()
                        task_path = os.path.join(examples_dir, file)
                        
                        task_desc = ""
                        try:
                            with open(task_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                import re
                                match = re.search(r'task_desc\s*=\s*[\'"](.+?)[\'"]', content)
                                if match:
                                    task_desc = match.group(1)
                        except Exception as e:
                            self.add_log(f"读取任务描述失败: {str(e)}")
                        
                        tasks.append({
                            'name': task_name,
                            'file': file,
                            'path': task_path,
                            'desc': task_desc
                        })
            return tasks
        except Exception as e:
            self.add_log(f"获取任务列表失败: {str(e)}")
            return []

    def add_tasks(self):
        """添加任务卡片"""
        tasks = self.get_available_tasks()
        
        if not tasks:
            no_task_label = BodyLabel("没有找到可用的任务脚本")
            self.task_content_layout.addWidget(no_task_label)
            return
            
        for task in tasks:
            task_card = TaskCard(task['name'], task['desc'])
            task_card.task_selected.connect(self.on_task_selected)
            self.task_content_layout.addWidget(task_card)
            self.task_cards[task['name']] = task_card
            
        self.task_content_layout.addStretch()

    def on_task_selected(self, task_name):
        """处理任务选中事件"""
        # 更新选中状态
        self.selected_task = task_name
        # 启用开始按钮和定时任务控件
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.enable_task_checkbox.setEnabled(True)
        self.time_edit.setEnabled(True)
        self.repeat_checkbox.setEnabled(True)
        self.repeat_type_minutes.setEnabled(True)
        self.repeat_type_days.setEnabled(True)
        self.interval_spinbox.setEnabled(self.repeat_checkbox.isChecked())
        
        # 取消其他任务的选中状态
        for i in range(self.task_content_layout.count()):
            item = self.task_content_layout.itemAt(i)
            if item and item.widget():
                task_card = item.widget()
                if isinstance(task_card, TaskCard) and task_card.task_name != task_name:
                    task_card.deselect()
        
        # 加载任务配置
        if task_name not in self.task_configs:
            self.task_configs[task_name] = TaskConfig()
        
        config = self.task_configs[task_name]
        
        # 更新界面显示，但不触发状态改变事件
        self.enable_task_checkbox.blockSignals(True)
        self.enable_task_checkbox.setChecked(config.is_enabled)
        self.enable_task_checkbox.blockSignals(False)
        
        self.time_edit.setTime(config.scheduled_time)
        self.repeat_checkbox.setChecked(config.is_repeat_enabled)
        if config.repeat_type == 'minutes':
            self.repeat_type_minutes.setChecked(True)
            self.repeat_type_days.setChecked(False)
        else:
            self.repeat_type_minutes.setChecked(False)
            self.repeat_type_days.setChecked(True)
        self.interval_spinbox.setValue(config.repeat_interval)

    def setup_signals(self):
        """设置信号连接"""
        self.start_button.clicked.connect(self.start_task)
        self.stop_button.clicked.connect(self.stop_task)

    def setup_schedule_signals(self):
        """设置定时任务相关的信号连接"""
        self.enable_task_checkbox.stateChanged.connect(self.on_enable_task_changed)
        self.repeat_checkbox.stateChanged.connect(self.on_repeat_changed)
        self.repeat_type_minutes.stateChanged.connect(self.on_repeat_type_changed)
        self.repeat_type_days.stateChanged.connect(self.on_repeat_type_changed)
        self.time_edit.timeChanged.connect(self.on_time_changed)
        self.interval_spinbox.valueChanged.connect(lambda: self.save_current_config())

    def on_enable_task_changed(self, state):
        """启用任务状态改变"""
        if not self.selected_task:
            return
            
        config = self.task_configs[self.selected_task]
        config.is_enabled = state == Qt.Checked
        
        if config.is_enabled:
            # 保存当前配置
            self.save_current_config()
            
            # 获取定时设置
            scheduled_time = config.scheduled_time
            current_time = QTime.currentTime()
            
            # 计算延迟时间（毫秒）
            delay = current_time.msecsTo(scheduled_time)
            is_tomorrow = False
            if delay < 0:  # 如果是负数，说明是明天的时间
                delay += 24 * 60 * 60 * 1000  # 加上24小时
                is_tomorrow = True
            
            # 启动定时器
            self.add_log(f"任务 {self.selected_task} 已启用", 'system')
            if is_tomorrow:
                self.add_log(f"将在明天 {scheduled_time.toString('HH:mm')} 执行", 'system')
            else:
                self.add_log(f"将在今天 {scheduled_time.toString('HH:mm')} 执行", 'system')
                
            if config.is_repeat_enabled:
                if config.repeat_type == 'minutes':
                    self.add_log(f"每 {config.repeat_interval} 分钟重复执行一次", 'system')
                else:
                    self.add_log(f"每 {config.repeat_interval} 天重复执行一次", 'system')
            
            self.timer.start(delay)
            # 更新按钮状态
            self.start_button.setEnabled(False)  # 定时任务启用时，禁用手动启动
            self.stop_button.setEnabled(True)
        else:
            # 只停止定时器，不影响当前正在执行的任务
            self.timer.stop()
            self.add_log(f"任务 {self.selected_task} 定时执行已禁用", 'system')
            # 如果当前没有任务在执行，则启用开始按钮
            if not self.current_task:
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)

    def on_repeat_changed(self, state):
        """重复执行复选框状态改变"""
        is_checked = state == Qt.Checked
        self.interval_spinbox.setEnabled(is_checked)
        self.repeat_type_minutes.setEnabled(is_checked)
        self.repeat_type_days.setEnabled(is_checked)
        
        if self.selected_task:
            config = self.task_configs[self.selected_task]
            config.is_repeat_enabled = is_checked
            self.save_current_config()
            
    def on_repeat_type_changed(self, state):
        """重复类型改变"""
        if not self.sender() or not self.selected_task:
            return
            
        if state == Qt.Checked:
            if self.sender() == self.repeat_type_minutes:
                self.repeat_type_days.setChecked(False)
                self.interval_spinbox.setMaximum(1440)  # 24小时
                self.interval_spinbox.setValue(60)  # 默认1小时
                self.interval_spinbox.setSuffix(" 分钟")
                self.task_configs[self.selected_task].repeat_type = 'minutes'
            else:
                self.repeat_type_minutes.setChecked(False)
                self.interval_spinbox.setMaximum(365)  # 一年
                self.interval_spinbox.setValue(1)  # 默认1天
                self.interval_spinbox.setSuffix(" 天")
                self.task_configs[self.selected_task].repeat_type = 'days'
                
            self.save_current_config()

    def save_current_config(self):
        """保存当前任务的配置"""
        if not self.selected_task:
            return
            
        config = self.task_configs[self.selected_task]
        config.scheduled_time = self.time_edit.time()
        config.is_repeat_enabled = self.repeat_checkbox.isChecked()
        config.repeat_type = 'minutes' if self.repeat_type_minutes.isChecked() else 'days'
        config.repeat_interval = self.interval_spinbox.value()

    def start_task(self):
        """开始执行任务"""
        if not self.selected_task:
            QMessageBox.warning(self, '提示', '请先选择要执行的任务')
            return
            
        # 获取任务路径
        task_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'examples',
            f'run_{self.selected_task.lower()}.py'
        )
        
        if not os.path.exists(task_path):
            QMessageBox.warning(self, '错误', f'任务脚本不存在: {task_path}')
            return
            
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(__file__))
        
        # 创建并启动任务线程
        self.current_task = TaskThread(task_path, env)
        self.current_task.output_ready.connect(lambda msg: self.add_log(msg))  # 普通输出使用默认颜色
        self.current_task.error_ready.connect(lambda msg: self.add_log(msg, 'error'))  # 错误输出使用红色
        self.current_task.finished.connect(self.on_task_finished)
        self.current_task.start()
        
        # 更新按钮状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def on_task_finished(self, return_code):
        """任务完成回调"""
        # 如果是手动停止的任务（返回码-15），不显示错误提示
        if return_code == -15:
            return
            
        if return_code == 0:
            self.add_log("任务执行成功", 'system')
            InfoBar.success(
                title='成功',
                content='任务执行完成',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            self.add_log(f"任务执行失败，返回码: {return_code}", 'error')
            InfoBar.error(
                title='错误',
                content=f'任务执行失败，返回码: {return_code}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        
        # 清理任务线程
        self.task_thread = None
        
        # 恢复按钮状态
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def stop_task(self, task_name=None):
        """停止任务"""
        if task_name is None:
            task_name = self.selected_task
            
        try:
            # 停止定时器
            self.timer.stop()
            
            # 停止当前任务线程
            if self.current_task:
                self.add_log(f"正在停止任务: {task_name}", 'system')
                self.current_task.stop()
                self.current_task.wait()  # 等待线程结束
                self.current_task = None
            
            # 更新按钮状态
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # 更新任务配置
            if task_name in self.task_configs:
                self.task_configs[task_name].is_enabled = False
            
            self.add_log(f"任务 {task_name} 已停止", 'system')
            InfoBar.success(
                title='成功',
                content='任务已停止执行',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            self.add_log(f"停止任务失败: {str(e)}", 'error')
            InfoBar.error(
                title='错误',
                content=f'停止任务失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def add_log(self, message, log_type='info'):
        """添加日志"""
        current_time = QTime.currentTime().toString('HH:mm:ss')
        if log_type == 'error':
            message = f'<span style="color: red;">[{current_time}] {message}</span>'
        elif log_type == 'system':
            message = f'<span style="color: #2ecc71;">[{current_time}] {message}</span>'
        else:
            message = f'<span style="color: #666666;">[{current_time}] {message}</span>'  # 普通日志使用灰色
        self.log_text.append(message)

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 停止定时器
            self.timer.stop()
            
            # 停止任务线程
            if self.task_thread:
                self.task_thread.stop()
                self.task_thread.wait()  # 等待线程结束
        except Exception as e:
            print(f"关闭任务时发生错误: {str(e)}")
        event.accept()

    def on_timer_timeout(self):
        """定时器超时处理"""
        if self.selected_task:
            self.start_task()

    def on_time_changed(self):
        """时间改变处理"""
        if not self.selected_task:
            return
            
        self.save_current_config()
        
        # 如果任务已启用，则更新定时器
        if self.enable_task_checkbox.isChecked():
            config = self.task_configs[self.selected_task]
            scheduled_time = config.scheduled_time
            current_time = QTime.currentTime()
            
            # 计算延迟时间（毫秒）
            delay = current_time.msecsTo(scheduled_time)
            is_tomorrow = False
            if delay < 0:  # 如果是负数，说明是明天的时间
                delay += 24 * 60 * 60 * 1000  # 加上24小时
                is_tomorrow = True
            
            # 更新日志显示
            if is_tomorrow:
                self.add_log(f"任务时间已更新，将在明天 {scheduled_time.toString('HH:mm')} 执行", 'system')
            else:
                self.add_log(f"任务时间已更新，将在今天 {scheduled_time.toString('HH:mm')} 执行", 'system')
            
            # 重启定时器
            self.timer.stop()
            self.timer.start(delay) 

    def on_browser_changed(self, browser_name):
        """浏览器选择改变时的处理"""
        self.add_log(f"默认浏览器已更改为: {browser_name}", 'system') 

    def on_group_selection_changed(self, selection):
        """处理分组选择改变事件"""
        self.group_name_input.setVisible(selection == '指定分组')
        if selection == '全部':
            self.add_log("任务浏览器已设置为: 全部", 'system')
        
    def on_group_name_changed(self):
        """处理分组名称改变事件"""
        group_name = self.group_name_input.text().strip()
        if group_name:
            self.add_log(f"任务浏览器分组已设置为: {group_name}", 'system') 