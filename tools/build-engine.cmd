@echo off
rem Build Zero Hour (generalszh.exe) from MOD\engine with VS 2022 Build Tools, 32-bit Release.
rem Usage: tools\build-engine.cmd [extra cmake --build args]
rem Needs VS 2022 Build Tools with: Workload.VCTools, Component.VC.Tools.x86.x64,
rem Component.VC.CMake.Project, a Windows SDK, Component.VC.ATL (atlbase.h) and
rem Component.VC.ATLMFC (afxres.h, used by Main\RTS.RC).
setlocal
rem vcvarsall.bat runs a bare "vswhere.exe" from the Installer folder. With the
rem NoDefaultCurrentDirectoryInExePath hardening set, cmd won't search the current
rem folder, so put the Installer folder on PATH instead.
set "PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer;%PATH%"
for /f "usebackq delims=" %%i in (`vswhere.exe -products * -latest -property installationPath`) do set "VS=%%i"
if not defined VS (echo Visual Studio Build Tools not found & exit /b 1)
call "%VS%\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul || exit /b 1

cd /d "%~dp0..\engine" || exit /b 1
if not exist build\win32\CMakeCache.txt (
    cmake --preset win32 || exit /b 1
)
cmake --build build\win32 --config Release --target z_generals %* || exit /b 1
echo.
echo Built: %CD%\build\win32\GeneralsMD\Release\generalszh.exe
