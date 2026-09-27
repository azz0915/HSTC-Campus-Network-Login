@echo off
chcp 65001 >nul
echo 正在移除开机自启动项...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$startup=[Environment]::GetFolderPath('Startup');$target=Join-Path $startup 'HSTC_Campus_Login.lnk';if(Test-Path $target){Remove-Item $target -Force;Write-Host '开机自启已成功移除！'}else{Write-Host '未找到已存在的开机自启快捷方式。'}"
pause

