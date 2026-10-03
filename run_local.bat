@echo off
title Eventide Repair Engine - Local Environment
color 0A

echo ========================================================
echo             EVENTIDE REPAIR ENGINE - LOCAL
echo ========================================================
echo.
echo Выбери режим запуска:
echo [1] MODE 1: Только ремонт Eventide
echo [2] MODE 2: Ремонт + Перенос Genesis + Адаптация
echo [3] DRY-RUN: Тестовый прогон MODE 1 (без изменения файлов)
echo [4] Выход
echo.

set /p mode="Введи цифру (1-4): "

if "%mode%"=="4" goto end
if not "%mode%"=="1" if not "%mode%"=="2" if not "%mode%"=="3" (
    echo Неверный выбор.
    goto end
)

echo.
echo Введи путь к целевому проекту (project-eventide-14).
echo Оставь пустым и нажми Enter, чтобы использовать текущую папку.
set /p target_path="Путь: "

if "%target_path%"=="" set target_path=.

if "%mode%"=="1" goto mode1
if "%mode%"=="2" goto mode2
if "%mode%"=="3" goto dryrun

:mode1
echo.
echo [LOCAL] Запускаем MODE 1 (Repair Only)...
python local\run.py --mode 1 --target "%target_path%"
goto finish

:mode2
echo.
echo [LOCAL] Запускаем MODE 2 (Repair + Clone + Adapt)...
python local\run.py --mode 2 --target "%target_path%"
goto finish

:dryrun
echo.
echo [LOCAL] Запускаем тестовый прогон (Dry-Run)...
python local\run.py --mode 1 --dry-run --target "%target_path%"
goto finish

:finish
echo.
echo ========================================================
echo Выполнение завершено. Отчеты сохранены в папке reports/
echo ========================================================
pause
exit

:end
exit
