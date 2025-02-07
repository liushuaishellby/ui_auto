"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import os

def find_data_files(src_dir):
    data_files = []
    for root, dirs, files in os.walk(src_dir):
        if files:
            files_list = [os.path.join(root, f) for f in files]
            data_files.append((root, files_list))
    return data_files

APP = ['run_ui.py']

# Dynamically collect all data files
DATA_FILES = []
for directory in ['resources', 'examples', 'core', 'ui', 'shared', 'scripts', 'projects']:
    if os.path.exists(directory):
        DATA_FILES.extend(find_data_files(directory))

OPTIONS = {
    'argv_emulation': False,
    'strip': True,
    'packages': ['selenium', 'pkg_resources', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtNetwork', 'PyQt5.sip'],
    'includes': ['PyQt5.QtCore'],
    'excludes': ['PIL'],
    'qt_plugins': ['platforms', 'platformthemes', 'styles', 'imageformats'],
    'plist': {
        'CFBundleGetInfoString': "Blue Elf",
        'CFBundleIdentifier': "com.blueelf.app",
        'NSHighResolutionCapable': True,
        'LSEnvironment': {
            'PYTHONPATH': '@executable_path/../Resources/lib/python3.9',
            'QT_PLUGIN_PATH': '@executable_path/../Resources/lib/python3.9/PyQt5/Qt5/plugins'
        }
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 