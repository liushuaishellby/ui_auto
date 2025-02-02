import sys
import platform
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from qfluentwidgets import setTheme, Theme, FluentStyleSheet, StyleSheetBase
from qfluentwidgets.common.style_sheet import StyleSheetBase

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 自定义样式表
CUSTOM_STYLE = """
QListView {
    outline: none;
    border: none;
    background: transparent;
    selection-background-color: transparent;
    font-size: 13px;
    line-height: 30px;
    selection-color: black;
}

QListView::item {
    height: 30px;
    padding: 0px;
    margin: 0px;
    border: none;
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    background: transparent;
    color: black;
    line-height: 30px;
    text-align: left;
    padding-left: 5px;
}

QListView::item:hover {
    height: 30px;
    padding: 0px;
    margin: 0px;
    border: none;
    background: transparent;
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    color: black;
    line-height: 30px;
    text-align: left;
    padding-left: 5px;
}

QListView::item:selected {
    height: 30px;
    padding: 0px;
    margin: 0px;
    border: none;
    background: transparent;
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    color: black;
    line-height: 30px;
    text-align: left;
    padding-left: 5px;
}

QListView::item:selected:active {
    background: transparent;
    color: black;
    font-size: 13px;
}

QListView::item:selected:!active {
    background: transparent;
    color: black;
    font-size: 13px;
}

QListView::item:pressed {
    background: transparent;
    color: black;
    font-size: 13px;
    height: 30px;
    min-height: 30px;
    max-height: 30px;
    line-height: 30px;
    padding-left: 5px;
}

QListView::item:focus {
    background: transparent;
    color: black;
    font-size: 13px;
    height: 30px;
    min-height: 30px;
    max-height: 30px;
    line-height: 30px;
    padding-left: 5px;
}

QMenu {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 5px 0px;
}

QMenu::item {
    padding: 8px 25px;
    border: none;
    background: transparent;
    border-radius: 5px;
    margin: 2px 5px;
    color: #2c3e50;
    font-size: 13px;
    min-width: 120px;
}

QMenu::item:selected {
    background-color: #f0f0f0;
    color: #2c3e50;
}

QMenu::item:pressed {
    background-color: #e8e8e8;
    color: #2c3e50;
}

QMenu::separator {
    height: 1px;
    background: #e0e0e0;
    margin: 5px 0px;
}

QMenu::indicator {
    width: 16px;
    height: 16px;
    margin-left: 5px;
}

NavigationInterface {
    background-color: rgb(243, 243, 243);
    border: none;
    padding: 0;
}

NavigationInterface QWidget {
    background-color: transparent;
}

NavigationInterface QPushButton {
    padding: 8px 16px;
    margin: 2px 4px;
    border: none;
    border-radius: 6px;
    color: #1f1f1f;
    background: transparent;
    font-size: 13px;
    text-align: left;
}

NavigationInterface QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

NavigationInterface QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.1);
}

NavigationInterface QPushButton:checked {
    background-color: rgba(0, 0, 0, 0.1);
    color: #0078d4;
}

NavigationInterface QPushButton:disabled {
    color: rgba(0, 0, 0, 0.36);
}

/* 汉堡菜单按钮样式 */
#menuButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    margin: 6px;
    padding: 4px;
}

#menuButton:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

#menuButton:pressed {
    background-color: rgba(0, 0, 0, 0.1);
}

#menuButton::menu-indicator {
    width: 0px;
}

/* 标题栏样式 */
TitleBar {
    background-color: rgb(243, 243, 243);
    border: none;
}

TitleBar QLabel {
    color: black;
    font-size: 13px;
}

TitleBar QPushButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    margin: 6px;
    padding: 4px;
}

TitleBar QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

TitleBar QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.1);
}
"""

def setup_font():
    """设置应用程序字体"""
    if platform.system() == 'Darwin':  # macOS
        default_font = ".AppleSystemUIFont"
    else:
        default_font = "Microsoft YaHei UI"

    # 设置 QFluentWidgets 的默认字体
    StyleSheetBase.DEFAULT_FONT = default_font
    
    # 创建字体对象
    font = QFont(default_font)
    font.setPixelSize(13)
    font.setStyleStrategy(QFont.PreferAntialias)
    
    # 添加字体映射
    QFontDatabase.addApplicationFont(":/qfluentwidgets/fonts/Segoe_Fluent_Icons.ttf")
    QFontDatabase.addApplicationFont(":/qfluentwidgets/fonts/Segoe_MDL2_Assets.ttf")
    
    # 添加字体替换规则
    QFont.insertSubstitution("Segoe UI", default_font)
    QFont.insertSubstitution("Segoe UI Symbol", default_font)
    
    return font

def run():
    app = QApplication(sys.argv)
    
    # 设置字体
    app.setFont(setup_font())
    
    # 设置主题
    setTheme(Theme.AUTO)
    
    # 导入并显示主窗口
    from ui.main_window import MainWindow
    window = MainWindow()
    
    # 应用自定义样式表
    window.setStyleSheet(CUSTOM_STYLE)
    
    window.show()
    
    app.exec_()

if __name__ == '__main__':
    run() 