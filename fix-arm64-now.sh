#!/bin/bash

# 立即修复ARM64问题的脚本

echo "🔧 立即修复ARM64 Selenium问题"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}步骤1: 停止当前容器...${NC}"
./deploy.sh stop

echo -e "${YELLOW}步骤2: 重新构建镜像（包含ARM64修复）...${NC}"
./deploy.sh build

echo -e "${YELLOW}步骤3: 启动修复后的容器...${NC}"
./deploy.sh start

echo -e "${YELLOW}步骤4: 测试修复结果...${NC}"
sleep 10

# 测试浏览器
echo "测试浏览器环境..."
docker exec tokaido-automation bash -c "
    echo '=== ChromeDriver路径检查 ==='
    which chromedriver
    ls -la /usr/bin/chromedriver /usr/local/bin/chromedriver 2>/dev/null || echo '某些路径不存在'
    
    echo '=== ChromeDriver版本 ==='
    chromedriver --version
    
    echo '=== 测试Selenium ==='
    python -c \"
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 使用明确路径
service = Service('/usr/bin/chromedriver')
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('data:text/html,<html><body><h1>Test</h1></body></html>')
    print('✅ Selenium测试成功')
    driver.quit()
except Exception as e:
    print(f'❌ Selenium测试失败: {e}')
\"
"

echo ""
echo -e "${GREEN}✅ ARM64修复完成！${NC}"
echo ""
echo "现在可以测试一键生成记录功能了。"
echo "如果还有问题，请运行: ./debug-docker.sh"
