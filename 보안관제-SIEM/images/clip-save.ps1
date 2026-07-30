Add-Type -AssemblyName System.Windows.Forms

$savePath = "C:\Users\SBA_USER\Desktop\SESAC\보안관제-SIEM\images"
$lastHash = ""

Write-Host "클립보드 이미지 자동 저장 실행 중... (종료: Ctrl+C)"
Write-Host "저장 경로: $savePath"
Write-Host ""

while ($true) {
    if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
        $img = [System.Windows.Forms.Clipboard]::GetImage()
        if ($img -ne $null) {
            $ms = New-Object System.IO.MemoryStream
            $img.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $hash = [BitConverter]::ToString($ms.ToArray(), 0, 64)

            if ($hash -ne $lastHash) {
                $lastHash = $hash
                $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                $fileName = "capture_$timestamp.png"
                $fullPath = Join-Path $savePath $fileName
                $img.Save($fullPath, [System.Drawing.Imaging.ImageFormat]::Png)
                Write-Host "저장됨: $fileName"
            }
            $ms.Dispose()
            $img.Dispose()
        }
    }
    Start-Sleep -Milliseconds 500
}
