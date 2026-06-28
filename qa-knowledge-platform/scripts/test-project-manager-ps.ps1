$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptPath = Join-Path $PSScriptRoot 'project-manager.ps1'
$PowerShellExe = Join-Path $PSHOME 'powershell.exe'

function Assert-Contains {
    param(
        [string]$Text,
        [string]$Expected,
        [string]$Message
    )

    if (-not $Text.Contains($Expected)) {
        throw $Message
    }
}

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "Missing PowerShell project manager: $ScriptPath"
}

$helpOutput = & $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath help 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Help command failed with exit code $LASTEXITCODE"
}
Assert-Contains ($helpOutput -join "`n") 'QA知识协作平台项目管理脚本' 'Help output is missing the script title.'
Assert-Contains ($helpOutput -join "`n") 'project-manager.ps1 status' 'Help output is missing the PowerShell status example.'

$oldPath = $env:PATH
try {
    $env:PATH = $ProjectRoot
    $statusOutput = & $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath status 2>&1
    $statusText = $statusOutput -join "`n"
    if ($LASTEXITCODE -eq 0) {
        Assert-Contains $statusText '查看 dev 环境服务状态' 'Status output is missing the status title.'
    } else {
        Assert-Contains $statusText 'Docker 未安装或未加入 PATH' 'Status output should explain that Docker is missing.'
    }
} finally {
    $env:PATH = $oldPath
}

Write-Host 'PowerShell project manager checks passed.'
