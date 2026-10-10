@echo off
rem Play Generals Reforged (the same package your friend gets from GitHub) on the MOD copy of the game.
set "ZH_GAME_DIR=%~dp0Command Conquer Generals - Zero Hour\Command & Conquer(tm) Generals Zero Hour"
call "%~dp0release\GeneralsReforged\Play-Generals-Reforged.cmd" %*
