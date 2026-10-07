Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\ConversorTV"
WshShell.Run Chr(34) & "C:\ConversorTV\start.bat" & Chr(34), 0, False
Set WshShell = Nothing