@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo     EPUB to PDF Converter
echo ========================================
echo.

if "%~1"=="" (
    echo [!] กรุณาลากไฟล์ EPUB มาวางที่ไฟล์นี้
    echo.
    pause
    exit /b 1
)

:loop
if "%~1"=="" goto end

set "input_file=%~1"
set "output_file=%~dpn1.pdf"

echo [*] กำลังแปลง: "%~nx1"
echo [*] ไปยัง: "%~nxn1.pdf"
echo.

python convertepub2pdf.py "%input_file%" -o "%output_file%" --delete-epub

if !errorlevel! equ 0 (
    echo [✓] แปลงสำเร็จ: "%~nxn1.pdf"
    echo [🗑️] กำลังลบไฟล์ EPUB ต้นฉบับ...
) else (
    echo [✗] แปลงล้มเหลว: "%~nx1"
)

echo.
shift
goto loop

:end
echo.
echo ========================================
echo     แปลงเสร็จสิ้น
echo ========================================
echo.
pause
