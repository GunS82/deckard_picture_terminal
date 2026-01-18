import os
import sys
import subprocess
from pathlib import Path

def run_gui():
    # 1. Находим текущий venv
    venv_python = sys.executable
    venv_dir = str(Path(venv_python).parent.parent)
    
    # 2. Ищем, куда pip поставил PySide6
    # Обычно это venv/Lib/site-packages/PySide6
    site_packages = Path(venv_dir) / "Lib" / "site-packages"
    pyside_dir = site_packages / "PySide6"
    shiboken_dir = site_packages / "shiboken6"

    if not pyside_dir.exists():
        print(f"Error: Could not find PySide6 in {pyside_dir}")
        return

    print(f"Found PySide6 at: {pyside_dir}")

    # 3. Формируем "чистый" PATH
    # Оставляем только системные папки Windows + папки нашего venv
    # УБИРАЕМ всё лишнее (особенно Anaconda)
    
    original_path = os.environ["PATH"]
    
    # Список папок, которые мы хотим видеть в PATH
    clean_paths = [
        str(pyside_dir),          # DLL PySide (Qt)
        str(shiboken_dir),        # DLL оберток
        str(Path(venv_dir) / "Scripts"), # Скрипты venv
        r"C:\Windows\System32",   # Системные DLL
        r"C:\Windows"
    ]
    
    new_path = ";".join(clean_paths)
    
    # 4. Подготавливаем окружение для запуска
    env = os.environ.copy()
    env["PATH"] = new_path
    
    # Для отладки (если Qt ругается на плагины)
    env["QT_PLUGIN_PATH"] = str(pyside_dir / "plugins")

    print("Launching enhance_viewer.py with ISOLATED environment...")
    
    # 5. Запускаем viewer с новым окружением
    cmd = [venv_python, "enhance_viewer.py", "sample.png"]
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    run_gui()
