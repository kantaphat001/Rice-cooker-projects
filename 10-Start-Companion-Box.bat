@echo off
chcp 65001 >nul
title Smart Rice Cooker Companion Box - Real System Runner (2026 Edition)
color 0A
cls
echo ================================================================================
echo    🏥 SMART RICE COOKER COMPANION BOX - REAL SYSTEM RUNNER (2026 EDITION)
echo    ระบบกล่องแจ้งเตือนการทานยาอัจฉริยะ (ตรวจจับใบหน้า AI + ขานเตือนยาภาษาไทย)
echo ================================================================================
echo.
echo  เลือกโหมดที่ต้องการทดสอบใช้งานจริง:
echo.
echo   [1] รันระบบตรวจจับยาจริงบนคอมพิวเตอร์นี้ (PC Mode - ใช้กล้องโน้ตบุ๊ก + AI สแกนหน้า + ลำโพงคอม)
echo       * กด Enter ได้ทันที เพื่อทดสอบระบบ AI สแกนใบหน้าและเสียงพูดภาษาไทย *
echo.
echo   [2] รันและสั่งงานฮาร์ดแวร์จริงบน Raspberry Pi (Hardware Mode - ไฟ LED + อัลตราโซนิก)
echo.
set RUN_MODE=1
set /p RUN_MODE="เลือกหมายเลข (1 หรือ 2, ค่าเริ่มต้น [1]): "

if "%RUN_MODE%"=="2" (
    python "%~dp0run_companion_box.py" --full-hardware
) else (
    echo.
    echo [*] กำลังเริ่มต้นระบบตรวจจับยาจริงบนคอมพิวเตอร์...
    echo     - กล้องเว็บแคมจะเปิดขึ้นมาเพื่อตรวจจับใบหน้า
    echo     - ระบบ AI YuNet + SFace จะสแกนและระบุตัวตนบุคคล
    echo     - ลำโพงคอมพิวเตอร์จะขานชื่อและเตือนยาภาษาไทยตามตารางเวลา
    echo     กดปุ่ม Ctrl + C บนหน้าต่างนี้เพื่อหยุดการทำงาน
    echo --------------------------------------------------------------------------------
    python -m smart_rice_cooker.main --camera-only
)
pause
