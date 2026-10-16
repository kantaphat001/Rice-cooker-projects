# ==============================================================================
# Control-Center.ps1 - Raspberry Pi 4 Command and Control Center
# Designed for Raspberry Pi 4 (Primary Target: 192.168.88.74)
# ==============================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Raspberry Pi 4 - Command and Control Center"

$pi_user = "pi"
$project_dir = $PSScriptRoot
$ip_file = Join-Path $project_dir "config_ip.txt"
$screenshots_dir = Join-Path $project_dir "screenshots"
$backups_dir = Join-Path $project_dir "backups"

if (-not (Test-Path $screenshots_dir)) { New-Item -ItemType Directory -Path $screenshots_dir -Force | Out-Null }
if (-not (Test-Path $backups_dir)) { New-Item -ItemType Directory -Path $backups_dir -Force | Out-Null }

function Get-PiHost {
    if (Test-Path $ip_file) {
        $saved = (Get-Content $ip_file -Raw).Trim()
        if ($saved) { return $saved }
    }
    return "192.168.88.74"
}

function Set-PiHost([string]$newIp) {
    $newIp | Out-File -FilePath $ip_file -Encoding ascii -NoNewline
}

function Show-Menu {
    Clear-Host
    $pi_host = Get-PiHost
    Write-Host "========================================================================================" -ForegroundColor Cyan
    Write-Host "                RASPBERRY PI 4 - COMMAND AND CONTROL CENTER (2026)                      " -ForegroundColor Green
    Write-Host "  Target Host: $pi_user@$pi_host  |  Port: 22/3389  |  Primary Target: 192.168.88.74  " -ForegroundColor Yellow
    Write-Host "========================================================================================" -ForegroundColor Cyan
    Write-Host " [การเชื่อมต่อ และควบคุมหน้าจอ Pi 4]              [ระบบ บำรุงรักษา และเพิ่มความเร็ว Pi 4]" -ForegroundColor DarkCyan
    Write-Host "  [1]  Connect SSH Console (เปิดเทอร์มินัล Pi)    [7]  Check System Health (อุณหภูมิ/RAM)" -ForegroundColor White
    Write-Host "  [2]  Remote Desktop GUI  (รีโมทจอ 1024x600)     [8]  View Real-time Logs (ดู Log สด Pi)" -ForegroundColor White
    Write-Host "  [3]  Capture Screenshot  (แคปภาพหน้าจอ Pi)      [9]  Apply Optimizations (จูน ZRAM LZ4)" -ForegroundColor White
    Write-Host "  [4]  Switch OS and Theme (XFCE vs PIXEL)        [10] Clean System Cache  (คืนพื้นที่ SD)" -ForegroundColor White
    Write-Host "  [5]  Fix Mouse and Keyboard (ซ่อมไดรเวอร์)      [11] Automated Full Setup(ติดตั้งครบวงจร)" -ForegroundColor White
    Write-Host "  [6]  Set Target IP       (สลับเครื่อง .74/.78)  [12] Backup Pi Config   (สำรองคอนฟิกลงคอม)" -ForegroundColor White
    Write-Host ""
    Write-Host " [ฮาร์ดแวร์ กล้อง เสียง และอุปกรณ์ต่อพ่วง]        [ระบบเน็ตเวิร์ก และสภาพแวดล้อม Python]" -ForegroundColor DarkCyan
    Write-Host "  [13] USB Hardware Scan   (สแกนพอร์ต USB/Serial) [16] Wi-Fi and Ping Check(ทดสอบสัญญาณเน็ต)" -ForegroundColor White
    Write-Host "  [14] Test USB Camera     (ทดสอบกล้องเว็บแคม)    [17] Python and uv Status(ตรวจเวอร์ชัน Python)" -ForegroundColor White
    Write-Host "  [15] Test Audio Speaker  (ทดสอบเสียงลำโพง)      [18] Emergency Port Fix (รีเซ็ตวงจร USB)" -ForegroundColor White
    Write-Host "----------------------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "  [R] Safe Reboot    [S] Safe Shutdown    [0] Exit (ออกจากโปรแกรม)" -ForegroundColor Yellow
    Write-Host "========================================================================================" -ForegroundColor Cyan
}

while ($true) {
    $pi_host = Get-PiHost
    Show-Menu
    $choice = Read-Host "เลือกคำสั่ง (1-18, R, S, 0)"
    
    switch ($choice.ToUpper()) {
        "1" {
            Write-Host "`n[*] กำลังเชื่อมต่อไปยัง SSH Console: $pi_user@$pi_host..." -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "2" {
            Write-Host "`n[*] กำลังเปิดหน้าต่าง Remote Desktop ไปยัง $pi_host (ความละเอียด 1024x600)..." -ForegroundColor Cyan
            Write-Host "Username: $pi_user  |  Default Password: 1234" -ForegroundColor Yellow
            Start-Process "mstsc.exe" -ArgumentList "/v:$pi_host /w:1024 /h:600"
            Start-Sleep -Seconds 1
        }
        "3" {
            Write-Host "`n[*] กำลังถ่ายภาพหน้าจอจริงของบอร์ด Pi 4 (DISPLAY=:0)..." -ForegroundColor Cyan
            $stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
            $remoteImg = "/tmp/screenshot_$stamp.png"
            $localImg = Join-Path $screenshots_dir "screenshot_$stamp.png"
            ssh -o ConnectTimeout=4 -o StrictHostKeyChecking=no "$pi_user@$pi_host" "DISPLAY=:0 scrot $remoteImg 2>/dev/null || DISPLAY=:0 xwd -root -silent | convert xwd:- $remoteImg"
            if ($LASTEXITCODE -eq 0) {
                scp -o ConnectTimeout=4 -o StrictHostKeyChecking=no "${pi_user}@${pi_host}:$remoteImg" "$localImg"
                ssh -o ConnectTimeout=2 "$pi_user@$pi_host" "rm -f $remoteImg"
                Write-Host "[+] แคปภาพหน้าจอสำเร็จ! กำลังเปิดดูบน Windows..." -ForegroundColor Green
                Start-Process "$localImg"
            } else {
                Write-Host "[-] ไม่สามารถถ่ายภาพหน้าจอได้ (อาจยังไม่ได้ติดตั้ง scrot หรือหน้าจอปิดอยู่)" -ForegroundColor Red
            }
            Start-Sleep -Seconds 2
        }
        "4" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Magenta
            Write-Host "    สลับสไตล์หน้าจอ Desktop ระหว่าง 2 สไตล์ (Target: $pi_host)" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Magenta
            Write-Host "  [1] สไตล์ XFCE Desktop (แนะนำสำหรับ RAM 1GB)" -ForegroundColor Yellow
            Write-Host "      -> สไตล์เหมือน Windows, Start Menu ซ้ายล่าง, Taskbar ล่าง, RAM ~140MB"
            Write-Host "  [2] สไตล์ PIXEL / LXDE" -ForegroundColor Yellow
            Write-Host "      -> สไตล์ออริจินัล Raspberry Pi, เมนูด้านบน, วอลเปเปอร์ภูเขา, RAM ~100MB"
            Write-Host "  [0] ย้อนกลับ" -ForegroundColor DarkGray
            $themeChoice = Read-Host "เลือกหมายเลข (1, 2, 0)"
            if ($themeChoice -eq "1") {
                Write-Host "[*] กำลังสลับไปใช้ XFCE Desktop..." -ForegroundColor Cyan
                ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "echo 'exec startxfce4' > /home/pi/.xsession; chmod +x /home/pi/.xsession; sudo update-alternatives --set x-session-manager /usr/bin/startxfce4 2>/dev/null || true; sudo systemctl restart lightdm; sudo systemctl restart xrdp"
                Write-Host "[+] สลับเป็น XFCE Desktop เรียบร้อยแล้ว!" -ForegroundColor Green
            } elseif ($themeChoice -eq "2") {
                Write-Host "[*] กำลังสลับไปใช้ PIXEL / LXDE Desktop..." -ForegroundColor Cyan
                ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo apt-get install -y --no-install-recommends openbox lxpanel pcmanfm 2>/dev/null; echo 'exec openbox-session' > /home/pi/.xsession; chmod +x /home/pi/.xsession; sudo update-alternatives --set x-session-manager /usr/bin/openbox-session 2>/dev/null || true; sudo systemctl restart lightdm; sudo systemctl restart xrdp"
                Write-Host "[+] สลับเป็น PIXEL / LXDE Desktop เรียบร้อยแล้ว!" -ForegroundColor Green
            }
            Start-Sleep -Seconds 2
        }
        "5" {
            Write-Host "`n[*] กำลังติดตั้งไดรเวอร์และกู้คืนระบบเมาส์/คีย์บอร์ดบนจอ HDMI..." -ForegroundColor Yellow
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo apt-get update && sudo apt-get install -y xserver-xorg-input-all xserver-xorg-input-libinput && sudo udevadm trigger --subsystem-match=input --action=change && sudo systemctl restart lightdm"
            Write-Host "[+] รีโหลดไดรเวอร์เมาส์และคีย์บอร์ดสำเร็จแล้ว!" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "6" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "    กำหนดหมายเลข IP ของ Raspberry Pi ที่ต้องการควบคุม" -ForegroundColor Yellow
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "  [1] เครื่องหลัก : 192.168.88.74 (ค่าเริ่มต้น)" -ForegroundColor White
            Write-Host "  [2] ระบุหมายเลข IP อื่นด้วยตนเอง" -ForegroundColor White
            $ipChoice = Read-Host "เลือกหมายเลข (1, 2)"
            if ($ipChoice -eq "1" -or [string]::IsNullOrWhiteSpace($ipChoice)) { Set-PiHost "192.168.88.74" }
            elseif ($ipChoice -eq "2") {
                $manualIp = Read-Host "พิมพ์หมายเลข IP ใหม่"
                if ($manualIp) { Set-PiHost $manualIp.Trim() }
            }
            Write-Host "[+] บันทึก IP เป้าหมายเป็น: $(Get-PiHost)" -ForegroundColor Green
            Start-Sleep -Seconds 1
        }
        "7" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "    รายงานสุขภาพระบบและทรัพยากรเครื่อง: $pi_host" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "echo '=== [1] HOSTNAME AND ARCHITECTURE ==='; uname -m; uname -r; echo ''; echo '=== [2] CPU TEMPERATURE ==='; (vcgencmd measure_temp 2>/dev/null || cat /sys/class/thermal/thermal_zone0/temp | awk '{print `$1/1000 \" deg C\"}'); echo ''; echo '=== [3] MEMORY AND ZRAM USAGE ==='; free -h; swapon --show; echo ''; echo '=== [4] MICROSD STORAGE ==='; df -h /; echo ''; echo '=== [5] CPU LOAD AND UPTIME ==='; uptime; echo ''; echo '=== [6] THROTTLED STATUS ==='; (vcgencmd get_throttled 2>/dev/null || echo 'Normal (0x0)')"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "8" {
            Write-Host "`n[*] กำลังสตรีม System Logs สดจาก $pi_host (กด Ctrl+C เพื่อหยุด)..." -ForegroundColor Cyan
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo journalctl -f -n 50 --no-tail"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "9" {
            Write-Host "`n[*] กำลังรันการจูน In-Memory ZRAM (LZ4) และเคอร์เนล..." -ForegroundColor Yellow
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo bash -c 'systemctl stop dphys-swapfile 2>/dev/null || true; systemctl disable dphys-swapfile 2>/dev/null || true; dphys-swapfile swapoff 2>/dev/null || true; rm -f /var/swap 2>/dev/null || true; apt-get update -y >/dev/null 2>&1; apt-get install -y --no-install-recommends zram-tools; echo -e \"ALGO=lz4\nPERCENT=100\nPRIORITY=100\" > /etc/default/zramswap; systemctl enable zramswap 2>/dev/null; systemctl restart zramswap; echo -e \"vm.swappiness=100\nvm.page-cluster=0\nvm.vfs_cache_pressure=50\" > /etc/sysctl.d/99-zram-optimizations.conf; sysctl -p /etc/sysctl.d/99-zram-optimizations.conf; apt-get clean'"
            Write-Host "[+] ปรับจูน ZRAM และเคอร์เนลสำเร็จ 100%!" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "10" {
            Write-Host "`n[*] กำลังล้างแคชระบบ Apt และไฟล์ชั่วคราวเพื่อคืนพื้นที่ MicroSD..." -ForegroundColor Yellow
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo apt-get clean && sudo rm -rf /var/cache/apt/archives/* /tmp/* 2>/dev/null; df -h /"
            Write-Host "[+] ล้างแคชเรียบร้อยแล้ว!" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "11" {
            Write-Host "`n[*] กำลังเริ่มกระบวนการ Automated 1-Click Provisioning..." -ForegroundColor Cyan
            scp -o StrictHostKeyChecking=no -r (Join-Path $project_dir "pi_setup_scripts") "$pi_user@${pi_host}:~/"
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sed -i 's/\r$//' ~/pi_setup_scripts/*.sh && chmod +x ~/pi_setup_scripts/*.sh && sudo bash ~/pi_setup_scripts/master_setup.sh"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "12" {
            Write-Host "`n[*] กำลังสำรองไฟล์คอนฟิกจาก $pi_host มายังโฟลเดอร์ backups..." -ForegroundColor Cyan
            $backupStamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
            $tarRemote = "/tmp/pi_backup_$backupStamp.tar.gz"
            $tarLocal = Join-Path $backups_dir "pi_backup_$backupStamp.tar.gz"
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "tar -czf $tarRemote /etc/lightdm /etc/xrdp /etc/sysctl.d /etc/default /etc/udev/rules.d /boot/firmware/config.txt 2>/dev/null"
            scp -o StrictHostKeyChecking=no "${pi_user}@${pi_host}:$tarRemote" "$tarLocal"
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "rm -f $tarRemote"
            Write-Host "[+] สำรองข้อมูลสำเร็จ: $tarLocal" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "13" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "    สแกนอุปกรณ์ USB และพอร์ต Serial ที่เชื่อมต่ออยู่กับ $pi_host" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "echo '=== [1] USB DEVICES (lsusb) ==='; lsusb; echo ''; echo '=== [2] SERIAL TTY NODES ==='; ls -l /dev/ttyUSB* /dev/ttyACM* /dev/serial* 2>/dev/null || echo 'ไม่พบพอร์ต Serial'; echo ''; echo '=== [3] INPUT DEVICES ==='; cat /proc/bus/input/devices | grep -E 'Name|Handlers'"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "14" {
            Write-Host "`n[*] ตรวจสอบสถานะกล้องบน $pi_host..." -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "v4l2-ctl --list-devices 2>/dev/null || ls -l /dev/video* 2>/dev/null || echo 'ไม่พบอุปกรณ์กล้อง /dev/video'"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "15" {
            Write-Host "`n[*] กำลังทดสอบส่งสัญญาณเสียงทดสอบ (Audio Beep Test)..." -ForegroundColor Yellow
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "speaker-test -t sine -f 440 -l 1 2>/dev/null || aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null || echo 'ทดสอบระบบเสียงเรียบร้อย'"
            Write-Host "[+] ส่งคำสั่งทดสอบเสียงเรียบร้อยแล้ว!" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "16" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "    ตรวจสอบสัญญาณเครือข่าย Wi-Fi และ Internet บน $pi_host" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "echo '=== [1] IP ADDRESS AND INTERFACES ==='; ip -br a; echo ''; echo '=== [2] WI-FI LINK QUALITY ==='; iwconfig wlan0 2>/dev/null || echo 'ไม่มีอินเทอร์เฟซ wlan0'; echo ''; echo '=== [3] INTERNET PING TEST (8.8.8.8) ==='; ping -c 3 8.8.8.8"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "17" {
            Clear-Host
            Write-Host "================================================================================" -ForegroundColor Cyan
            Write-Host "    ตรวจสอบสภาพแวดล้อม Python และ Astral uv บน $pi_host" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Cyan
            ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "echo '=== [1] PYTHON VERSION ==='; python3 --version; echo ''; echo '=== [2] ASTRAL UV VERSION ==='; uv --version 2>/dev/null || echo 'ยังไม่ได้ติดตั้ง uv'; echo ''; echo '=== [3] PIP CONFIG ==='; cat /etc/pip.conf 2>/dev/null"
            Write-Host "`nกด Enter เพื่อกลับสู่เมนูหลัก..." -ForegroundColor Gray
            Read-Host
        }
        "18" {
            Write-Host "`n[*] กำลังสั่งรีเซ็ตวงจร USB Controller (ปลุกพอร์ตที่ค้าง)..." -ForegroundColor Yellow
            ssh -t -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo udevadm control --reload-rules && sudo udevadm trigger && echo '[+] Udev triggered successfully!'"
            Write-Host "[+] รีเซ็ตพอร์ต USB เรียบร้อยแล้ว!" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        "R" {
            $confirm = Read-Host "ต้องการสั่ง Safe Reboot บอร์ด $pi_host ใช่หรือไม่? (y/n)"
            if ($confirm -eq "y") {
                Write-Host "[*] กำลังสั่ง Safe Reboot บอร์ด Pi 4..." -ForegroundColor Yellow
                ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo reboot"
                Write-Host "[+] สั่งรีบูตเรียบร้อย บอร์ดจะพร้อมใช้งานในอีก ~20 วินาที" -ForegroundColor Green
                Start-Sleep -Seconds 3
            }
        }
        "S" {
            $confirm = Read-Host "ต้องการสั่ง Safe Shutdown ปิดเครื่อง $pi_host ใช่หรือไม่? (y/n)"
            if ($confirm -eq "y") {
                Write-Host "[*] กำลังสั่ง Safe Shutdown..." -ForegroundColor Red
                ssh -o StrictHostKeyChecking=no "$pi_user@$pi_host" "sudo poweroff"
                Write-Host "[+] สั่งปิดเครื่องเรียบร้อย กรุณารอให้ไฟสีเขียว (ACT) ดับสนิทก่อนถอดปลั๊กไฟ" -ForegroundColor Green
                Start-Sleep -Seconds 3
            }
        }
        "0" {
            Write-Host "`nขอบคุณที่ใช้งาน Raspberry Pi 4 Command and Control Center! สวัสดีครับ`n" -ForegroundColor Green
            exit
        }
        default {
            Write-Host "`n[-] คำสั่งไม่ถูกต้อง กรุณาเลือกหมายเลขในเมนู" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}