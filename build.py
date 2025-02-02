import os
import sys
import shutil
import subprocess

def clean_build():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    for pattern in files_to_clean:
        for file in os.listdir('.'):
            if file.endswith('.spec') and file != 'build_app.spec':
                print(f"删除文件: {file}")
                os.remove(file)

def install_requirements():
    """安装必要的依赖"""
    print("安装依赖...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def build_app():
    """构建应用程序"""
    print("开始构建应用程序...")
    
    # 使用PyInstaller构建
    subprocess.check_call([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build_app.spec'
    ])

def main():
    """主函数"""
    try:
        # 清理旧的构建文件
        clean_build()
        
        # 安装依赖
        install_requirements()
        
        # 构建应用程序
        build_app()
        
        print("\n构建完成！")
        print("可执行文件位于 dist/TaskManager 目录中")
        
    except Exception as e:
        print(f"构建失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 