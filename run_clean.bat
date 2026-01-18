@echo off
setlocal

:: Define paths
set "VENV_DIR=%~dp0venv"
set "PYSIDE_DIR=%VENV_DIR%\Lib\site-packages\PySide6"
set "SHIBOKEN_DIR=%VENV_DIR%\Lib\site-packages\shiboken6"

:: Construct a clean PATH with VENV and Windows System ONLY
:: This removes Anaconda and other polluters from the DLL search path
set "PATH=%PYSIDE_DIR%;%SHIBOKEN_DIR%;%VENV_DIR%\Scripts;C:\Windows\System32;C:\Windows"

:: Verify PATH (optional, for debug)
:: echo Clean PATH: %PATH%

:: Run the viewer using the venv python
"%VENV_DIR%\Scripts\python.exe" enhance_viewer.py %*

endlocal
