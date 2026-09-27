Set ws = CreateObject("WScript.Shell")
currentPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
ws.Run "pythonw """ & currentPath & "\hstc_campus_login.py""", 0, False
