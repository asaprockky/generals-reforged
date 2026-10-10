# Launch a Zero Hour build windowed, wait, and capture only that game window to PNG.
# Used to compare camera framing and menu layout between builds without driving input.
#
# Usage: powershell -File tools\capture-window.ps1 -Exe <generalszh.exe> -Width 1920 -Height 1080 -Out shot.png [-Wait 40]
#        [-ExtraArgs '-loadreplay','00000000.rep']   (replay name is looked up in the user's Replays folder)
param(
    [Parameter(Mandatory)] [string]$Exe,
    [Parameter(Mandatory)] [int]$Width,
    [Parameter(Mandatory)] [int]$Height,
    [Parameter(Mandatory)] [string]$Out,
    [int]$Wait = 40,
    [string[]]$ExtraArgs = @(),
    [switch]$ShellMap,   # launch normally (live 3D menu map) instead of -quickstart
    [int]$Shots = 1,
    [int]$IntervalMs = 1000,
    [string]$GameDir = "C:\projects\Generals\MOD\Command Conquer Generals - Zero Hour\Command & Conquer(tm) Generals Zero Hour"
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class GameWin {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int Left, Top, Right, Bottom; }
    public struct POINT { public int X, Y; }
}
"@

$gameArgs = @('-setCwd', "`"$GameDir`"", '-win', '-xres', "$Width", '-yres', "$Height")
if ($ShellMap) { $gameArgs += '-nologo' } else { $gameArgs += '-quickstart' }
$gameArgs += $ExtraArgs
$p = Start-Process -FilePath $Exe -ArgumentList $gameArgs -WorkingDirectory $GameDir -PassThru
try {
    Start-Sleep -Seconds $Wait
    $p.Refresh()
    if ($p.HasExited) { throw "game exited early with code $($p.ExitCode)" }
    $h = $p.MainWindowHandle
    $c = New-Object GameWin+RECT; [GameWin]::GetClientRect($h, [ref]$c) | Out-Null
    $w = New-Object GameWin+RECT; [GameWin]::GetWindowRect($h, [ref]$w) | Out-Null
    $origin = New-Object GameWin+POINT; [GameWin]::ClientToScreen($h, [ref]$origin) | Out-Null

    # -Shots N takes N captures IntervalMs apart, saved as <Out>_<k>.png with the wall-clock ms.
    $clock = [Diagnostics.Stopwatch]::StartNew()
    for ($k = 0; $k -lt $Shots; $k++) {
        if ($k -gt 0) { Start-Sleep -Milliseconds $IntervalMs }
        # PrintWindow renders the whole window (frame included); crop to the client area.
        $full = New-Object Drawing.Bitmap ($w.Right - $w.Left), ($w.Bottom - $w.Top)
        $g = [Drawing.Graphics]::FromImage($full)
        $dc = $g.GetHdc(); $ok = [GameWin]::PrintWindow($h, $dc, 2); $g.ReleaseHdc($dc); $g.Dispose()
        $ms = $clock.ElapsedMilliseconds
        $crop = New-Object Drawing.Rectangle ($origin.X - $w.Left), ($origin.Y - $w.Top), $c.Right, $c.Bottom
        $client = $full.Clone($crop, $full.PixelFormat)
        $file = if ($Shots -gt 1) { $Out -replace '\.png$', "_$k.png" } else { $Out }
        $client.Save($file, [Drawing.Imaging.ImageFormat]::Png)
        "captured=$ok t=${ms}ms client=$($c.Right)x$($c.Bottom) responding=$($p.Responding) -> $file"
    }
}
finally {
    if (-not $p.HasExited) { Stop-Process -Id $p.Id -Confirm:$false }
}
