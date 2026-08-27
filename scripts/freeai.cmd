@echo off
REM freeai.cmd - Windows wrapper for freeai-cli
REM Place this script in a directory on your PATH, or add scripts\ to PATH.
set "ROOT=%~dp0.."
set "PYTHON=%~f0"
python "%ROOT%\scripts\freeai.py" %*
