@echo off
set "PYSIDE_DIR=C:\Users\Lenovo\anaconda3\Lib\site-packages\PySide6"
set "SHIBOKEN_DIR=C:\Users\Lenovo\anaconda3\Lib\site-packages\shiboken6"
set "PATH=%PYSIDE_DIR%;%SHIBOKEN_DIR%;%PATH%"
python -c "from PySide6.QtCore import QObject; print('IMPORT SUCCESS')"
