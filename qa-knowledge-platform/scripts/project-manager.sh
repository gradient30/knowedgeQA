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

COMPOSE_COMMAND=()

detect_compose() {
    if [ ${#COMPOSE_COMMAND[@]} -gt 0 ]; then
        return
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装或未加入 PATH，请先安装 Docker Desktop"
        exit 1
    fi

    if docker compose version &> /dev/null; then
        COMPOSE_COMMAND=(docker compose)
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

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 后端测试
    log_info "运行后端测试..."
    run_compose -f docker-compose.dev.yml exec backend poetry run pytest tests/ --cov=app
    
    # 前端测试
    log_info "运行前端测试..."
    run_compose -f docker-compose.dev.yml exec frontend pnpm test --run
    
    log_success "测试完成"
}

# 清理环境
clean_environment() {
    log_info "清理环境..."
    
    # 停止并删除容器
    run_compose -f docker-compose.dev.yml down -v --remove-orphans
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的卷
    docker volume prune -f
    
    log_success "环境清理完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 确保数据库服务运行
    run_compose -f docker-compose.dev.yml up -d db redis
    
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
