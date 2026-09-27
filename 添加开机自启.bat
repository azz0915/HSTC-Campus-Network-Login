@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在添加开机自启动项...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell;$startup=[Environment]::GetFolderPath('Startup');$target=Join-Path $startup 'HSTC_Campus_Login.lnk';$sc=$ws.CreateShortcut($target);$sc.TargetPath='wscript.exe';$sc.Arguments='"""' + (Join-Path (Get-Location) 'silent_login.vbs') + '"""';$sc.WorkingDirectory=(Get-Location).Path;$sc.Description='HSTC Campus Network Auto Login';$sc.Save();Write-Host '开机自启添加成功！快捷方式位置：'$target"
pause

