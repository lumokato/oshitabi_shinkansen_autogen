#!/bin/bash

# Docker调试脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Docker调试工具${NC}"
echo "================================"

# 加载环境变量
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

HOST_PORT=${HOST_PORT:-8001}

# 检查容器状态
check_container() {
    echo -e "${YELLOW}📊 检查容器状态...${NC}"
    
    if docker ps | grep tokaido-automation > /dev/null; then
        echo -e "${GREEN}✅ 容器正在运行${NC}"
        docker ps | grep tokaido-automation
    else
        echo -e "${RED}❌ 容器未运行${NC}"
        echo "请先启动容器: ./deploy.sh start"
        exit 1
    fi
}

# 查看实时日志
show_logs() {
    echo -e "${YELLOW}📋 显示实时日志...${NC}"
    echo "按 Ctrl+C 退出日志查看"
    echo ""
    docker logs -f tokaido-automation
}

# 进入容器调试
enter_container() {
    echo -e "${YELLOW}🔧 进入容器调试模式...${NC}"
    echo "在容器内可以执行以下调试命令："
    echo "  - python backend/app.py  # 手动启动服务"
    echo "  - python -c \"from headless_automation import HeadlessAutomation; ha = HeadlessAutomation('test', 'test'); print('OK')\"  # 测试浏览器"
    echo "  - chromium --version  # 检查浏览器版本"
    echo "  - chromedriver --version  # 检查驱动版本"
    echo "  - ps aux  # 查看进程"
    echo "  - exit  # 退出容器"
    echo ""
    docker exec -it tokaido-automation bash
}

# 测试生成功能
test_generation() {
    echo -e "${YELLOW}🧪 测试生成功能...${NC}"
    
    read -p "请输入测试用户名: " username
    read -s -p "请输入测试密码: " password
    echo ""
    
    echo "正在测试生成功能..."
    
    # 使用curl测试API
    response=$(curl -s -X POST http://localhost:$HOST_PORT/api/riding-record/generate \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\",\"password\":\"$password\"}" \
        -w "HTTP_STATUS:%{http_code}")
    
    http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    echo "HTTP状态码: $http_status"
    echo "响应内容: $response_body"
    
    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ API调用成功${NC}"
    else
        echo -e "${RED}❌ API调用失败${NC}"
    fi
}

# 检查浏览器环境
check_browser() {
    echo -e "${YELLOW}🌐 检查浏览器环境...${NC}"
    
    echo "检查容器内浏览器状态..."
    docker exec tokaido-automation bash -c "
        echo '=== 浏览器版本 ==='
        chromium --version 2>/dev/null || echo '❌ Chromium未安装'
        
        echo '=== ChromeDriver版本 ==='
        chromedriver --version 2>/dev/null || echo '❌ ChromeDriver未安装'
        
        echo '=== 显示环境 ==='
        echo \"DISPLAY: \$DISPLAY\"
        
        echo '=== 进程检查 ==='
        ps aux | grep -E '(chrome|chromium)' | grep -v grep || echo '无浏览器进程运行'
        
        echo '=== 测试无头浏览器启动 ==='
        timeout 10s chromium --headless --no-sandbox --disable-dev-shm-usage --dump-dom https://www.google.com > /dev/null 2>&1 && echo '✅ 无头浏览器测试成功' || echo '❌ 无头浏览器测试失败'
    "
}

# 查看错误日志
show_error_logs() {
    echo -e "${YELLOW}🔍 查看错误日志...${NC}"
    
    echo "=== 最近的容器日志 ==="
    docker logs --tail=50 tokaido-automation
    
    echo ""
    echo "=== 查找错误信息 ==="
    docker logs tokaido-automation 2>&1 | grep -i -E "(error|exception|failed|traceback)" | tail -20
}

# 监控资源使用
monitor_resources() {
    echo -e "${YELLOW}📈 监控资源使用...${NC}"
    echo "按 Ctrl+C 停止监控"
    echo ""
    
    while true; do
        clear
        echo "=== 容器资源使用情况 ==="
        docker stats tokaido-automation --no-stream
        
        echo ""
        echo "=== 容器内存使用详情 ==="
        docker exec tokaido-automation bash -c "
            echo '内存使用:'
            free -h
            echo ''
            echo '磁盘使用:'
            df -h
            echo ''
            echo '进程内存使用 (前10):'
            ps aux --sort=-%mem | head -11
        "
        
        sleep 5
    done
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${BLUE}请选择调试选项:${NC}"
    echo "1. 查看实时日志"
    echo "2. 进入容器调试"
    echo "3. 测试生成功能API"
    echo "4. 检查浏览器环境"
    echo "5. 查看错误日志"
    echo "6. 监控资源使用"
    echo "7. 修复ARM64 Selenium问题"
    echo "8. 重启容器"
    echo "9. 退出"
    echo ""
}

# 修复ARM64 Selenium问题
fix_arm64_selenium() {
    echo -e "${YELLOW}🔧 修复ARM64 Selenium问题...${NC}"

    echo "正在容器内运行ARM64修复脚本..."
    docker exec tokaido-automation python fix-arm64-selenium.py

    echo ""
    echo "正在测试修复结果..."
    docker exec tokaido-automation python debug-generation.py
}

# 重启容器
restart_container() {
    echo -e "${YELLOW}🔄 重启容器...${NC}"
    ./deploy.sh restart
}

# 主程序
main() {
    check_container
    
    while true; do
        show_menu
        read -p "请输入选项 (1-9): " choice
        
        case $choice in
            1)
                show_logs
                ;;
            2)
                enter_container
                ;;
            3)
                test_generation
                ;;
            4)
                check_browser
                ;;
            5)
                show_error_logs
                ;;
            6)
                monitor_resources
                ;;
            7)
                fix_arm64_selenium
                ;;
            8)
                restart_container
                ;;
            9)
                echo -e "${GREEN}👋 调试结束${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选项，请重新选择${NC}"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 如果有参数，直接执行对应功能
case "${1:-menu}" in
    "logs")
        check_container
        show_logs
        ;;
    "enter")
        check_container
        enter_container
        ;;
    "test")
        check_container
        test_generation
        ;;
    "browser")
        check_container
        check_browser
        ;;
    "errors")
        check_container
        show_error_logs
        ;;
    "monitor")
        check_container
        monitor_resources
        ;;
    "restart")
        restart_container
        ;;
    *)
        main
        ;;
esac
