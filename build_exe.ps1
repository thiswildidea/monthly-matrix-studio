# 编译 EXE 并打包成可分发的 ZIP。
# 用的是 Windows 自带的 .NET Framework 编译器，不需要安装任何东西。
# 改完 monthly_matrix_studio.html 后重新跑一次本脚本即可。
#
# 注意：本脚本含中文，必须存成 UTF-8 with BOM。PowerShell 5.1 会把无 BOM 的
# 脚本按 ANSI 读，中文全变乱码、解析直接失败。

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) { throw "找不到 C# 编译器：$csc" }

$html = "monthly_matrix_studio.html"
$exe  = "月度矩阵工作室.exe"
if (-not (Test-Path $html)) { throw "找不到应用本体：$html" }

if (-not (Test-Path "app.ico")) { python gen_icon.py }

& $csc `
  /nologo /target:winexe /optimize+ /codepage:65001 `
  /out:$exe `
  /resource:"$html,APPHTML" `
  /win32icon:app.ico `
  /win32manifest:app.manifest `
  /reference:System.dll /reference:System.Windows.Forms.dll `
  MonthlyMatrixStudio.cs

if ($LASTEXITCODE -ne 0) { throw "编译失败" }
Write-Host ("编译完成: {0}  ({1:N0} KB)" -f $exe, ((Get-Item $exe).Length / 1KB))

$dist = "dist"
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }
New-Item -ItemType Directory -Path $dist | Out-Null

Copy-Item $exe $dist
Copy-Item $html $dist
Copy-Item "启动-月度矩阵工作室.cmd" $dist
Copy-Item "使用说明.txt" $dist

$zip = "月度矩阵工作室_v1.0.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$dist\*" -DestinationPath $zip

Write-Host ("分发包: {0}  ({1:N0} KB)" -f $zip, ((Get-Item $zip).Length / 1KB))
Get-ChildItem $dist | Select-Object Name, @{n = 'KB'; e = { [math]::Round($_.Length / 1KB, 1) } } | Format-Table -AutoSize
