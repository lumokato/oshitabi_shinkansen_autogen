#!/bin/bash

# 乘车记录管理系统 Docker 部署脚本

set -e

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    # 检查Docker Compose版本并选择配置文件
    COMPOSE_VERSION=$(docker-compose version --short 2>/dev/null || echo "1.0.0")
    COMPOSE_FILE="docker-compose.yml"

    # 检查是否为已知的旧版本
    case "$COMPOSE_VERSION" in
        1.2[0-6].* | 1.1*.* | 1.0*.*)
            log_warning "检测到较旧的Docker Compose版本 ($COMPOSE_VERSION)，使用兼容配置"
            COMPOSE_FILE="docker-compose.legacy.yml"
            ;;
        *)
            log_info "使用标准配置文件 (Docker Compose版本: $COMPOSE_VERSION)"
            ;;
    esac

    export COMPOSE_FILE
    log_success "Docker 环境检查通过，使用配置文件: $COMPOSE_FILE"
}

# 创建必要的目录和文件
setup_environment() {
    log_info "设置环境..."
    
    # 创建结果目录
    mkdir -p results
    
    # 检查配置文件
    if [ ! -f "accounts_config.json" ]; then
        if [ -f "accounts_config_example.json" ]; then
            log_warning "accounts_config.json 不存在，从示例文件复制"
            cp accounts_config_example.json accounts_config.json
            log_warning "请编辑 accounts_config.json 文件设置您的真实账号信息"
        else
            log_warning "accounts_config.json 不存在，创建示例文件"
            cat > accounts_config.json << EOF
{
    "accounts": {
        "example_user": {
            "username": "example_user",
            "password": "example_password",
            "display_name": "示例用户",
            "enabled": false
        }
    }
}
EOF
        fi
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从 .env.example 复制"
        cp .env.example .env
        log_warning "请编辑 .env 文件设置您的配置"
    fi
    
    log_success "环境设置完成"
}

# 构建前端
build_frontend() {
    log_info "构建前端..."

    if [ -f "build-frontend.sh" ]; then
        ./build-frontend.sh
    else
        log_info "使用npm直接构建..."
        cd frontend
        npm ci
        npm run build
        cd ..
    fi

    log_success "前端构建完成"
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."

    # 检查前端是否已构建
    if [ ! -d "frontend/dist" ]; then
        log_error "前端未构建！请先构建前端："
        log_info "  1. 本地构建: ./build-frontend.sh"
        log_info "  2. 或手动构建: cd frontend && npm run build"
        exit 1
    fi

    log_success "前端已构建，继续Docker构建..."
    docker-compose -f "$COMPOSE_FILE" build
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose -f "$COMPOSE_FILE" up -d
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15

    # 检查容器状态
    log_info "检查容器状态..."
    docker-compose -f "$COMPOSE_FILE" ps

    # 多次尝试健康检查
    local max_attempts=6
    local attempt=1

    # 获取宿主机端口
    local host_port=${HOST_PORT:-8001}

    while [ $attempt -le $max_attempts ]; do
        log_info "健康检查尝试 $attempt/$max_attempts..."

        if curl -f http://localhost:$host_port/api/health > /dev/null 2>&1; then
            log_success "服务运行正常"
            log_info "访问地址: http://localhost:$host_port"
            return 0
        fi

        if [ $attempt -lt $max_attempts ]; then
            log_warning "健康检查失败，等待5秒后重试..."
            sleep 5
        fi

        attempt=$((attempt + 1))
    done

    log_error "服务启动失败，请检查日志"
    log_info "显示最近的日志："
    docker-compose -f "$COMPOSE_FILE" logs --tail=50
    exit 1
}

# 显示日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "服务已停止"
}

# 清理
cleanup() {
    log_info "清理资源..."
    docker-compose -f "$COMPOSE_FILE" down -v --rmi all
    log_success "清理完成"
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            check_docker
            setup_environment
            build_image
            start_services
            check_services
            ;;
        "stop")
            check_docker
            stop_services
            ;;
        "restart")
            check_docker
            stop_services
            start_services
            check_services
            ;;
        "logs")
            check_docker
            show_logs
            ;;
        "build")
            check_docker
            build_image
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "status")
            check_docker
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        *)
            echo "用法: $0 {start|stop|restart|logs|build|cleanup|status}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动服务（默认）"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  logs     - 查看日志"
            echo "  build    - 构建镜像"
            echo "  cleanup  - 清理所有资源"
            echo "  status   - 查看服务状态"
            exit 1
            ;;
    esac
}

main "$@"
