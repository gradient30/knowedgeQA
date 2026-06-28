param(
    [Parameter(Position = 0)]
    [ValidateSet('setup', 'start', 'stop', 'restart', 'status', 'logs', 'build', 'test', 'clean', 'init-db', 'help')]
    [string]$Command = 'help',

    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Env = 'dev',

    [string]$Service = '',

    [switch]$Follow
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$script:DockerCommand = $null

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    @"
QA知识协作平台项目管理脚本

PowerShell 用法:
  .\scripts\project-manager.ps1 <命令> [选项]

Bash/WSL 用法:
  bash ./scripts/project-manager.sh <命令> [选项]

命令:
  setup                 初始化项目环境
  start                 启动开发环境
  stop                  停止所有服务
  restart               重启服务
  status                查看服务状态
  logs                  查看服务日志
  build                 构建项目
  test                  运行测试
  clean                 清理环境
  init-db               初始化数据库
  help                  显示帮助信息

选项:
  -Env <env>            指定环境 (dev|staging|prod)，默认: dev
  -Service <service>    指定服务名称
  -Follow               跟踪日志输出

示例:
  .\scripts\project-manager.ps1 setup
  .\scripts\project-manager.ps1 start -Env dev
  .\scripts\project-manager.ps1 status
  .\scripts\project-manager.ps1 logs -Service backend -Follow
  .\scripts\project-manager.ps1 test
"@
}

function Get-ComposeFile {
    param([string]$TargetEnv)

    $composeFile = "docker-compose.$TargetEnv.yml"
    if (-not (Test-Path -LiteralPath $composeFile)) {
        throw "Compose 文件不存在: $composeFile"
    }

    return $composeFile
}

function Resolve-DockerCommand {
    if ($script:DockerCommand) {
        return $script:DockerCommand
    }

    $pathCommand = Get-Command docker -ErrorAction SilentlyContinue
    if ($pathCommand) {
        $script:DockerCommand = $pathCommand.Source
        return $script:DockerCommand
    }

    $candidatePaths = @(
        (Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin\docker.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe')
    )

    foreach ($candidate in $candidatePaths) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            $script:DockerCommand = $candidate
            $dockerBin = Split-Path -Parent $candidate
            if (($env:PATH -split ';') -notcontains $dockerBin) {
                $env:PATH = "$dockerBin;$env:PATH"
            }
            Write-WarningMessage "Docker 未加入 PATH，改用: $candidate"
            return $script:DockerCommand
        }
    }

    return $null
}

function Invoke-Docker {
    param([string[]]$DockerArgs)

    $docker = Resolve-DockerCommand
    if (-not $docker) {
        Write-ErrorMessage 'Docker 未安装或未加入 PATH。请安装 Docker Desktop，或安装后重新打开 PowerShell。'
        exit 1
    }

    & $docker @DockerArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-Compose {
    param(
        [string]$ComposeFile,
        [string[]]$ComposeArgs
    )

    $docker = Resolve-DockerCommand
    if (-not $docker) {
        Write-ErrorMessage 'Docker 未安装或未加入 PATH。请安装 Docker Desktop，或安装后重新打开 PowerShell。'
        exit 1
    }

    & $docker compose version *> $null
    if ($LASTEXITCODE -eq 0) {
        & $docker compose -f $ComposeFile @ComposeArgs
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        return
    }

    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        & docker-compose -f $ComposeFile @ComposeArgs
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        return
    }

    Write-ErrorMessage 'Docker Compose 不可用。Docker Desktop 新版本通常提供 `docker compose`；旧版本需要 `docker-compose`。'
    exit 1
}

function Test-Dependencies {
    Write-Info '检查依赖...'

    $docker = Resolve-DockerCommand
    if (-not $docker) {
        Write-ErrorMessage 'Docker 未安装或未加入 PATH。请先安装 Docker Desktop。'
        exit 1
    }

    & $docker compose version *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Success '依赖检查完成'
        return
    }

    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        Write-Success '依赖检查完成'
        return
    }

    Write-ErrorMessage 'Docker Compose 不可用。请启用 Docker Desktop Compose V2，或安装 docker-compose。'
    exit 1
}

function Setup-Project {
    Write-Info '开始项目初始化...'
    Test-Dependencies

    New-Item -ItemType Directory -Force -Path 'backend/uploads/images', 'backend/uploads/documents', 'backend/uploads/thumbnails', 'backend/logs', 'frontend/.next' | Out-Null

    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.dev' -Destination '.env'
        Write-Info '已创建 .env 文件'
    }

    Write-Info '构建Docker镜像...'
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('build')
    Write-Success '项目初始化完成'
}

function Start-Services {
    Write-Info "启动 $Env 环境服务..."
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('up', '-d')
    if ($Env -eq 'dev') {
        Write-Info '初始化 dev 数据库基线数据...'
        Start-Sleep -Seconds 8
        Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('exec', 'backend', 'python', 'scripts/init_db.py')
    }
    Write-Success '服务启动完成'
    Write-Info '前端地址: http://localhost:3000'
    Write-Info '后端API: http://localhost:8000'
    Write-Info 'API文档: http://localhost:8000/docs'
}

function Stop-Services {
    Write-Info "停止 $Env 环境服务..."
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('down')
    Write-Success '服务停止完成'
}

function Show-Status {
    Write-Info "查看 $Env 环境服务状态..."
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('ps')
}

function Show-Logs {
    Write-Info "查看 $Env 环境日志..."
    $args = @('logs')
    if ($Follow) {
        $args += '-f'
    }
    if ($Service) {
        $args += $Service
    }
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs $args
}

function Build-Project {
    Write-Info "构建 $Env 环境项目..."
    Invoke-Compose -ComposeFile (Get-ComposeFile $Env) -ComposeArgs @('build')
    Write-Success '项目构建完成'
}

function Verify-DatabaseMigrations {
    $composeFile = 'docker-compose.dev.yml'
    $databaseName = 'qa_migration_acceptance'
    $databaseUrl = "postgresql+asyncpg://qa_user:qa_password@db:5432/$databaseName"
    $docker = Resolve-DockerCommand
    if (-not $docker) {
        Write-ErrorMessage 'Docker 未安装或未加入 PATH。请安装 Docker Desktop，或安装后重新打开 PowerShell。'
        exit 1
    }

    Write-Info '验证数据库迁移图...'
    Invoke-Compose -ComposeFile $composeFile -ComposeArgs @('exec', 'backend', 'poetry', 'run', 'alembic', 'heads')

    Write-Info '验证 fresh empty database upgrade...'
    Invoke-Compose -ComposeFile $composeFile -ComposeArgs @('exec', '-T', 'db', 'psql', '-U', 'qa_user', '-d', 'postgres', '-c', "DROP DATABASE IF EXISTS $databaseName")
    Invoke-Compose -ComposeFile $composeFile -ComposeArgs @('exec', '-T', 'db', 'psql', '-U', 'qa_user', '-d', 'postgres', '-c', "CREATE DATABASE $databaseName")

    & $docker compose -f $composeFile exec -T -e "DATABASE_URL=$databaseUrl" backend poetry run alembic upgrade head
    $upgradeExitCode = $LASTEXITCODE

    & $docker compose -f $composeFile exec -T db psql -U qa_user -d postgres -c "DROP DATABASE IF EXISTS $databaseName"
    $cleanupExitCode = $LASTEXITCODE

    if ($cleanupExitCode -ne 0) {
        exit $cleanupExitCode
    }
    if ($upgradeExitCode -ne 0) {
        exit $upgradeExitCode
    }
}

function Run-Tests {
    Write-Info '运行后端测试...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('exec', 'backend', 'poetry', 'run', 'pytest', 'tests/', '--cov=app')

    Verify-DatabaseMigrations

    Write-Info '运行前端类型检查...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('exec', 'frontend', 'pnpm', 'type-check')

    Write-Info '运行前端 lint...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('exec', 'frontend', 'pnpm', 'lint')

    Write-Info '同步 dev 数据库结构...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('exec', 'backend', 'python', 'scripts/init_db.py')

    Write-Info '运行SaaS/Game运行态验收...'
    node scripts/verify-runtime-acceptance.js
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Write-Info '运行SaaS/Game UI验收...'
    npx --yes --package playwright node scripts/verify-ui-acceptance.js
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Write-Info '运行验收文档门禁...'
    node scripts/verify-core-pages.js
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    node scripts/verify-acceptance-docs.js
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Write-Success '测试完成'
}

function Clean-Environment {
    Write-Info '清理环境...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('down', '-v', '--remove-orphans')
    Invoke-Docker -DockerArgs @('image', 'prune', '-f')
    Invoke-Docker -DockerArgs @('volume', 'prune', '-f')
    Write-Success '环境清理完成'
}

function Initialize-Database {
    Write-Info '初始化数据库...'
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('up', '-d', 'db', 'redis', 'backend')
    Start-Sleep -Seconds 5
    Invoke-Compose -ComposeFile 'docker-compose.dev.yml' -ComposeArgs @('exec', 'backend', 'python', 'scripts/init_db.py')
    Write-Success '数据库初始化完成'
}

switch ($Command) {
    'setup' { Setup-Project }
    'start' { Start-Services }
    'stop' { Stop-Services }
    'restart' { Stop-Services; Start-Services }
    'status' { Show-Status }
    'logs' { Show-Logs }
    'build' { Build-Project }
    'test' { Run-Tests }
    'clean' { Clean-Environment }
    'init-db' { Initialize-Database }
    'help' { Show-Help }
}
