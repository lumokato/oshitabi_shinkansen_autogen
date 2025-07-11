#!/bin/bash

# 快速诊断脚本 - 专门用于生成功能问题

echo "🚀 快速诊断：一键生成记录问题"
echo "================================"

# 加载环境变量
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

HOST_PORT=${HOST_PORT:-8001}

# 1. 检查容器状态
echo "1️⃣ 检查容器状态..."
if docker ps | grep tokaido-automation > /dev/null; then
    echo "✅ 容器正在运行"
else
    echo "❌ 容器未运行，请先启动: ./deploy.sh start"
    exit 1
fi

# 2. 检查服务健康状态
echo ""
echo "2️⃣ 检查服务健康状态..."
if curl -f http://localhost:$HOST_PORT/api/health > /dev/null 2>&1; then
    echo "✅ 服务健康检查通过"
else
    echo "❌ 服务健康检查失败"
fi

# 3. 检查浏览器环境
echo ""
echo "3️⃣ 检查浏览器环境..."
docker exec tokaido-automation bash -c "
    if chromium --version > /dev/null 2>&1; then
        echo '✅ Chromium 可用'
    else
        echo '❌ Chromium 不可用'
    fi
    
    if chromedriver --version > /dev/null 2>&1; then
        echo '✅ ChromeDriver 可用'
    else
        echo '❌ ChromeDriver 不可用'
    fi
"

# 4. 检查Python模块
echo ""
echo "4️⃣ 检查Python模块..."
docker exec tokaido-automation python -c "
try:
    from headless_automation import HeadlessAutomation
    print('✅ HeadlessAutomation 模块可用')
except Exception as e:
    print(f'❌ HeadlessAutomation 模块错误: {e}')

try:
    from selenium import webdriver
    print('✅ Selenium 模块可用')
except Exception as e:
    print(f'❌ Selenium 模块错误: {e}')
"

# 5. 检查最近的错误日志
echo ""
echo "5️⃣ 检查最近的错误日志..."
echo "--- 最近10条错误信息 ---"
docker logs tokaido-automation 2>&1 | grep -i -E "(error|exception|failed|traceback)" | tail -10

# 6. 测试无头浏览器
echo ""
echo "6️⃣ 测试无头浏览器启动..."
docker exec tokaido-automation bash -c "
    timeout 15s chromium --headless --no-sandbox --disable-dev-shm-usage --disable-gpu --dump-dom https://www.google.com > /dev/null 2>&1
    if [ \$? -eq 0 ]; then
        echo '✅ 无头浏览器测试成功'
    else
        echo '❌ 无头浏览器测试失败'
    fi
"

# 7. 检查内存使用
echo ""
echo "7️⃣ 检查内存使用..."
docker exec tokaido-automation bash -c "
    echo '容器内存使用:'
    free -h | head -2
    echo ''
    echo '磁盘使用:'
    df -h / | tail -1
"

echo ""
echo "🔍 诊断完成！"
echo ""
echo "如果发现问题，可以使用以下命令进一步调试："
echo "  ./debug-docker.sh enter    # 进入容器详细调试"
echo "  ./debug-docker.sh logs     # 查看实时日志"
echo "  ./debug-docker.sh test     # 测试生成API"
echo ""
echo "在容器内可以运行："
echo "  python debug-generation.py  # 详细的生成功能调试"
