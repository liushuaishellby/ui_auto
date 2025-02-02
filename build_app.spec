# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    ['run_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('examples', 'examples'),
        ('core', 'core'),
        ('ui', 'ui'),
        ('shared', 'shared'),
        ('scripts', 'scripts'),
        ('projects', 'projects'),
    ],
    hiddenimports=[
        'PyQt5',
        'qfluentwidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        'PyQt5.QtSvg',
        'PyQt5.QtXml',
        'darkdetect',
        'DrissionPage',
        'DrissionPage.common',
        'selenium',
        'selenium.webdriver',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == 'darwin':  # macOS
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='蓝精灵',
        debug=True,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        icon='resources/icons/app_icon.png'
    )
    
    app = BUNDLE(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='蓝精灵.app',
        icon='resources/icons/app_icon.png',
        bundle_identifier='com.blueelf.app',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'NSPrincipalClass': 'NSApplication',
            'CFBundleName': '蓝精灵',
            'CFBundleDisplayName': '蓝精灵',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'LSApplicationCategoryType': 'public.app-category.developer-tools',
            'NSRequiresAquaSystemAppearance': False,
            'LSMinimumSystemVersion': '10.13.0',
            'LSEnvironment': {
                'PYTHONPATH': '@executable_path/../Resources/lib/python3.9/site-packages',
                'QT_PLUGIN_PATH': '@executable_path/../Resources/plugins',
                'QT_QPA_PLATFORM_PLUGIN_PATH': '@executable_path/../Resources/plugins/platforms',
                'QT_QPA_PLATFORM': 'cocoa'
            },
        }
    )
else:  # Windows 和 Linux
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='蓝精灵',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon='resources/icons/app_icon.png'
    )