@echo off
rem Launch the WIDESCREEN 16:9 build (Hor+ camera, centered UI) against the MOD game data.
rem The exe is a backup copy in builds\, so rebuilding the engine does not touch it.
rem -setCwd is required: this engine otherwise looks for game data next to the exe.
set "GAME=%~dp0Command Conquer Generals - Zero Hour\Command & Conquer(tm) Generals Zero Hour"
start "" /D "%GAME%" "%~dp0builds\generalszh-widescreen-16x9.exe" -setCwd "%GAME%" -quickstart
