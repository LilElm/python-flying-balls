'WScript.Echo "jflakjflka"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "makefile.bat" & Chr(34), 0
Set WshShell = Nothing