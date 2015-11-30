rd /S /Q build
rd /S /Q dist
del /S GoLucky.spec

C:\Python34\Scripts\pyinstaller.exe -F -w bin\GoLucky.py
pause