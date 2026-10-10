@echo off
rem Launch the latest Reforged dev build (widescreen, abreast group moves, formations) against the MOD game data.
rem The exe is a copy in builds\, so rebuilding the engine does not touch it.
rem -setCwd is required: this engine otherwise looks for game data next to the exe.
set "GAME=%~dp0Command Conquer Generals - Zero Hour\Command & Conquer(tm) Generals Zero Hour"
start "" /D "%GAME%" "%~dp0builds\generalszh-reforged-dev.exe" -setCwd "%GAME%" -nologo
