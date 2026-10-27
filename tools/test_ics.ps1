$netShare = New-Object -ComObject HNetCfg.HNetShare.1
foreach ($conn in $netShare.EnumEveryConnection) {
    $props = $netShare.NetConnectionProps($conn)
    Write-Host "Name:" $props.Name "GUID:" $props.Guid
}
