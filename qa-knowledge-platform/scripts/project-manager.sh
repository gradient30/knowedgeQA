#!/bin/bash

# QA知识协作平台项目管理脚本

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

DOCKER_COMMAND=()
COMPOSE_COMMAND=()
NODE_COMMAND=()
NPX_COMMAND=()

detect_docker() {
    if [ ${#DOCKER_COMMAND[@]} -gt 0 ]; then
        return
    fi

    if command -v docker &> /dev/null; then
        DOCKER_COMMAND=(docker)
        return
    fi

    local windows_user="${WINUSER:-${USER:-}}"
    local docker_candidates=(
        "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
        "/mnt/c/Users/${windows_user}/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe"
    )

    for candidate in "${docker_candidates[@]}"; do
        if [ -x "$candidate" ]; then
            local docker_bin
            docker_bin="$(dirname "$candidate")"
            case ":$PATH:" in
                *":$docker_bin:"*) ;;
                *) export PATH="$docker_bin:$PATH" ;;
            esac
            DOCKER_COMMAND=("$candidate")
            log_warning "Docker 未加入 WSL PATH，改用: $candidate"
            return
        fi
    done

    log_error "Docker 未安装或未加入 PATH，请先安装 Docker Desktop"
    exit 1
}

detect_compose() {
    if [ ${#COMPOSE_COMMAND[@]} -gt 0 ]; then
        return
    fi

    detect_docker

    if "${DOCKER_COMMAND[@]}" compose version &> /dev/null; then
        COMPOSE_COMMAND=("${DOCKER_COMMAND[@]}" compose)
        return
    fi

    if command -v docker-compose &> /dev/null; then
        COMPOSE_COMMAND=(docker-compose)
        return
    fi

    log_error "Docker Compose 不可用。Docker Desktop 新版本通常提供 'docker compose'；旧版本需要 'docker-compose'"
    exit 1
}

run_compose() {
    detect_compose
    "${COMPOSE_COMMAND[@]}" "$@"
}

run_docker() {
    detect_docker
    "${DOCKER_COMMAND[@]}" "$@"
}

detect_node() {
    if [ ${#NODE_COMMAND[@]} -gt 0 ]; then
        return
    fi

    if command -v node &> /dev/null; then
        NODE_COMMAND=(node)
        return
    fi

    local node_candidates=(
        "/mnt/c/nvm4w/nodejs/node.exe"
        "/mnt/c/Program Files/nodejs/node.exe"
    )

    for candidate in "${node_candidates[@]}"; do
        if [ -x "$candidate" ]; then
            NODE_COMMAND=("$candidate")
            log_warning "Node 未加入 WSL PATH，改用: $candidate"
            return
        fi
    done

    log_error "Node.js 不可用。请安装 Node.js，或将 Windows node.exe 加入 WSL PATH。"
    exit 1
}

detect_npx() {
    if [ ${#NPX_COMMAND[@]} -gt 0 ]; then
        return
    fi

    if command -v npx &> /dev/null; then
        NPX_COMMAND=(npx)
        return
    fi

    local npx_candidates=(
        "/mnt/c/nvm4w/nodejs/npx.cmd"
        "/mnt/c/Program Files/nodejs/npx.cmd"
    )

    for candidate in "${npx_candidates[@]}"; do
        if [ -f "$candidate" ]; then
            NPX_COMMAND=("$candidate")
            log_warning "npx 未加入 WSL PATH，改用: $candidate"
            return
        fi
    done

    log_error "npx 不可用。请安装 Node.js/npm。"
    exit 1
}

run_node() {
    detect_node
    "${NODE_COMMAND[@]}" "$@"
}

run_npx() {
    detect_npx
    "${NPX_COMMAND[@]}" "$@"
}

# 显示帮助信息
show_help() {
    cat << EOF
QA知识协作平台项目管理脚本

用法: $0 <命令> [选项]

PowerShell:
  .\\scripts\\project-manager.ps1 <命令> [选项]

Bash/WSL:
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
  --env <env>           指定环境 (dev|staging|prod)，默认: dev
  --service <service>   指定服务名称
  --follow              跟踪日志输出

示例:
  $0 setup                    # 初始化项目
  $0 start --env dev          # 启动开发环境
  $0 logs --service backend   # 查看后端日志
  $0 test                     # 运行测试
EOF
}

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查依赖..."

    detect_compose
    
    log_success "依赖检查完成"
}

# 项目初始化
setup_project() {
    log_info "开始项目初始化..."
    
    check_dependencies
    
    # 创建必要的目录
    mkdir -p backend/uploads/{images,documents,thumbnails}
    mkdir -p backend/logs
    mkdir -p frontend/.next
    
    # 复制环境配置文件
    if [ ! -f .env ]; then
        cp .env.dev .env
        log_info "已创建 .env 文件"
    fi
    
    # 构建Docker镜像
    log_info "构建Docker镜像..."
    run_compose -f docker-compose.dev.yml build
    
    log_success "项目初始化完成"
}

# 启动服务
start_services() {
    local env=${1:-dev}
    log_info "启动 $env 环境服务..."
    
    case $env in
        dev)
            run_compose -f docker-compose.dev.yml up -d
            ;;
        staging)
            run_compose -f docker-compose.staging.yml up -d
            ;;
        prod)
            run_compose -f docker-compose.prod.yml up -d
            ;;
        *)
            log_error "不支持的环境: $env"
            exit 1
            ;;
    esac

    if [ "$env" = "dev" ]; then
        log_info "初始化 dev 数据库基线数据..."
        sleep 8
        run_compose -f docker-compose.dev.yml exec backend python scripts/init_db.py
    fi
    
    log_success "服务启动完成"
    log_info "前端地址: http://localhost:3000"
    log_info "后端API: http://localhost:8000"
    log_info "API文档: http://localhost:8000/docs"
}

# 停止服务
stop_services() {
    local env=${1:-dev}
    log_info "停止 $env 环境服务..."
    
    case $env in
        dev)
            run_compose -f docker-compose.dev.yml down
            ;;
        staging)
            run_compose -f docker-compose.staging.yml down
            ;;
        prod)
            run_compose -f docker-compose.prod.yml down
            ;;
        *)
            log_error "不支持的环境: $env"
            exit 1
            ;;
    esac
    
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    local env=${1:-dev}
    log_info "重启 $env 环境服务..."
    
    stop_services $env
    start_services $env
}

# 查看服务状态
show_status() {
    local env=${1:-dev}
    log_info "查看 $env 环境服务状态..."
    
    case $env in
        dev)
            run_compose -f docker-compose.dev.yml ps
            ;;
        staging)
            run_compose -f docker-compose.staging.yml ps
            ;;
        prod)
            run_compose -f docker-compose.prod.yml ps
            ;;
        *)
            log_error "不支持的环境: $env"
            exit 1
            ;;
    esac
}

# 查看日志
show_logs() {
    local env=${1:-dev}
    local service=${2:-}
    local follow=${3:-false}
    
    local compose_file="docker-compose.${env}.yml"
    local args=(-f "$compose_file" logs)
    
    if [ "$follow" = "true" ]; then
        args+=(-f)
    fi
    
    if [ -n "$service" ]; then
        args+=("$service")
    fi
    
    log_info "查看日志: ${COMPOSE_COMMAND[*]:-docker compose} ${args[*]}"
    run_compose "${args[@]}"
}

# 构建项目
build_project() {
    local env=${1:-dev}
    log_info "构建 $env 环境项目..."
    
    case $env in
        dev)
            run_compose -f docker-compose.dev.yml build
            ;;
        staging)
            run_compose -f docker-compose.staging.yml build
            ;;
        prod)
            run_compose -f docker-compose.prod.yml build
            ;;
        *)
            log_error "不支持的环境: $env"
            exit 1
            ;;
    esac
    
    log_success "项目构建完成"
}

verify_database_migrations() {
    local database_name="qa_migration_acceptance"
    local database_url="postgresql+asyncpg://qa_user:qa_password@db:5432/${database_name}"

    log_info "验证数据库迁移图..."
    run_compose -f docker-compose.dev.yml exec backend poetry run alembic heads

    log_info "验证 fresh empty database upgrade..."
    run_compose -f docker-compose.dev.yml exec -T db psql -U qa_user -d postgres -c "DROP DATABASE IF EXISTS ${database_name}"
    run_compose -f docker-compose.dev.yml exec -T db psql -U qa_user -d postgres -c "CREATE DATABASE ${database_name}"

    set +e
    run_compose -f docker-compose.dev.yml exec -T -e "DATABASE_URL=${database_url}" backend poetry run alembic upgrade head
    local upgrade_status=$?
    run_compose -f docker-compose.dev.yml exec -T db psql -U qa_user -d postgres -c "DROP DATABASE IF EXISTS ${database_name}"
    local cleanup_status=$?
    set -e

    if [ "$cleanup_status" -ne 0 ]; then
        exit "$cleanup_status"
    fi
    if [ "$upgrade_status" -ne 0 ]; then
        exit "$upgrade_status"
    fi
}

wait_http_ready() {
    local url="$1"
    local timeout_seconds="${2:-90}"
    local deadline=$((SECONDS + timeout_seconds))

    while [ "$SECONDS" -lt "$deadline" ]; do
        if run_node -e "fetch(process.argv[1]).then((response) => process.exit(response.status < 500 ? 0 : 1)).catch(() => process.exit(1))" "$url"; then
            return
        fi
        sleep 2
    done

    log_error "等待服务就绪超时: $url"
    exit 1
}

restore_frontend_dev_server() {
    log_info "恢复 frontend dev server，避免生产构建清理 .next 后影响 UI 验收..."
    run_compose -f docker-compose.dev.yml up -d --force-recreate frontend
    wait_http_ready "http://localhost:3000/knowledge"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 后端测试
    log_info "运行后端测试..."
    run_compose -f docker-compose.dev.yml exec backend poetry run pytest tests/ --cov=app

    verify_database_migrations

    # 前端静态验证
    log_info "运行前端类型检查..."
    run_compose -f docker-compose.dev.yml exec frontend pnpm type-check

    log_info "运行前端 lint..."
    run_compose -f docker-compose.dev.yml exec frontend pnpm lint

    log_info "同步 dev 数据库结构..."
    run_compose -f docker-compose.dev.yml exec backend python scripts/init_db.py

    log_info "运行SaaS/Game运行态验收..."
    run_node scripts/verify-runtime-acceptance.js

    restore_frontend_dev_server

    log_info "运行SaaS/Game UI验收..."
    run_npx --yes --package playwright node scripts/verify-ui-acceptance.js

    log_info "运行验收文档门禁..."
    run_node scripts/verify-core-pages.js
    run_node scripts/verify-project-manager-scripts.js
    run_node scripts/verify-acceptance-docs.js
    
    log_success "测试完成"
}

# 清理环境
clean_environment() {
    log_info "清理环境..."
    
    # 停止并删除容器
    run_compose -f docker-compose.dev.yml down -v --remove-orphans
    
    # 删除未使用的镜像
    run_docker image prune -f

    # 删除未使用的卷
    run_docker volume prune -f
    
    log_success "环境清理完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 确保数据库服务运行
    run_compose -f docker-compose.dev.yml up -d db redis backend
    
    # 等待数据库启动
    sleep 5
    
    # 运行数据库初始化脚本
    run_compose -f docker-compose.dev.yml exec backend python scripts/init_db.py
    
    log_success "数据库初始化完成"
}

# 主函数
main() {
    local command=${1:-help}
    local env="dev"
    local service=""
    local follow=false
    
    # 解析参数
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                env="$2"
                shift 2
                ;;
            --service)
                service="$2"
                shift 2
                ;;
            --follow)
                follow=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行命令
    case $command in
        setup)
            setup_project
            ;;
        start)
            start_services $env
            ;;
        stop)
            stop_services $env
            ;;
        restart)
            restart_services $env
            ;;
        status)
            show_status $env
            ;;
        logs)
            show_logs $env $service $follow
            ;;
        build)
            build_project $env
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_environment
            ;;
        init-db)
            init_database
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
