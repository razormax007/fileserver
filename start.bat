@echo off
set PYTHON=%~dp0%venv\Scripts\python.exe
if not exist venv (
    py -m venv venv
    %PYTHON% -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
)
%PYTHON% server.py
pause
exit /b