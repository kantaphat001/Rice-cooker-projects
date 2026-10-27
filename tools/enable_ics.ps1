# enable_ics.ps1 - Automated Internet Connection Sharing (ICS) from Wi-Fi to Ethernet
param (
    [string]$PublicName = "Wi-Fi",
    [string]$PrivateName = "Ethernet"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   เปิดระบบแชร์เน็ตจาก Wi-Fi ไปยังสายแลน (Internet Connection Sharing) " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# Check Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[*] กำลังขอสิทธิ์ผู้ดูแลระบบ (Administrator)..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

try {
    # Ensure SharedAccess service is running
    Set-Service -Name SharedAccess -StartupType Automatic
    Start-Service -Name SharedAccess -ErrorAction SilentlyContinue

    $netShare = New-Object -ComObject HNetCfg.HNetShare.1
    $publicConn = $null
    $privateConn = $null

    foreach ($c in $netShare.EnumEveryConnection) {
        $props = $netShare.NetConnectionProps($c)
        if ($props.Name -like "*$PublicName*" -or $props.Name -like "*Wireless*") {
            $publicConn = $c
        }
        if ($props.Name -like "*$PrivateName*" -or $props.Name -like "*LAN*") {
            $privateConn = $c
        }
    }

    if (-not $publicConn) {
        Write-Host "[-] ไม่พบการ์ดเครือข่าย Wi-Fi" -ForegroundColor Red
        pause
        exit
    }
    if (-not $privateConn) {
        Write-Host "[-] ไม่พบการ์ดเครือข่าย Ethernet" -ForegroundColor Red
        pause
        exit
    }

    $pubProps = $netShare.NetConnectionProps($publicConn)
    $privProps = $netShare.NetConnectionProps($privateConn)

    Write-Host "[+] พบการ์ดเน็ตภายนอก (Public): $($pubProps.Name)" -ForegroundColor Green
    Write-Host "[+] พบการ์ดเน็ตสายแลน (Private): $($privProps.Name)" -ForegroundColor Green

    $pubConfig = $netShare.INetSharingConfigurationForINetConnection($publicConn)
    $privConfig = $netShare.INetSharingConfigurationForINetConnection($privateConn)

    # Disable first if any
    if ($pubConfig.SharingEnabled) { $pubConfig.DisableSharing() }
    if ($privConfig.SharingEnabled) { $privConfig.DisableSharing() }

    # Enable public sharing (0 = public / ICS_TARGET_INTERNET)
    $pubConfig.EnableSharing(0)
    # Enable private sharing (1 = private / ICS_TARGET_HOME)
    $privConfig.EnableSharing(1)

    Write-Host "`n🎉 เปิดระบบแชร์เน็ตจาก $($pubProps.Name) ไปยังสายแลนสำเร็จเรียบร้อยแล้ว!" -ForegroundColor Green
    Write-Host "คอมพิวเตอร์กำลังทำหน้าที่เป็นเราเตอร์แจก IP (192.168.137.x) ให้บอร์ด Raspberry Pi" -ForegroundColor Yellow
    Write-Host "`nคำแนะนำ: กรุณาถอดสายแลนแล้วเสียบใหม่ 1 ครั้ง เพื่อให้บอร์ดรับ IP ทันที`n" -ForegroundColor Cyan
} catch {
    Write-Host "[-] เกิดข้อผิดพลาด: $_" -ForegroundColor Red
}

Write-Host "กด Enter เพื่อเสร็จสิ้น..."
Read-Host
