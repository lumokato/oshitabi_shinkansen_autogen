#!/usr/bin/env python3
"""
ARM64架构Selenium修复脚本
解决ARM64环境下ChromeDriver路径问题
"""

import os
import sys
import subprocess

def check_architecture():
    """检查系统架构"""
    import platform
    arch = platform.machine()
    print(f"系统架构: {arch}")
    return arch

def find_chromedriver():
    """查找ChromeDriver路径"""
    possible_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/snap/bin/chromium.chromedriver',
        'chromedriver'
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"✅ 找到ChromeDriver: {path}")
        else:
            print(f"❌ 未找到: {path}")
    
    return found_paths

def test_chromedriver(path):
    """测试ChromeDriver是否可用"""
    try:
        result = subprocess.run([path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {path} 可用: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {path} 不可用: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {path} 测试失败: {e}")
        return False

def test_selenium_with_path(chromedriver_path):
    """使用指定路径测试Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        service = Service(executable_path=chromedriver_path)
        
        print(f"正在测试Selenium with ChromeDriver: {chromedriver_path}")
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
        title = driver.title
        
        driver.quit()
        
        print(f"✅ Selenium测试成功，页面标题: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Selenium测试失败: {e}")
        return False

def create_selenium_wrapper():
    """创建Selenium包装器"""
    wrapper_code = '''
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def create_chrome_driver(options=None):
    """创建Chrome WebDriver实例，自动处理ARM64架构问题"""
    if options is None:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
    
    # ARM64架构下的ChromeDriver路径
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/snap/bin/chromium.chromedriver'
    ]
    
    for path in chromedriver_paths:
        if os.path.exists(path):
            try:
                service = Service(executable_path=path)
                return webdriver.Chrome(service=service, options=options)
            except Exception:
                continue
    
    # 如果都失败，尝试默认方式
    try:
        return webdriver.Chrome(options=options)
    except Exception as e:
        raise Exception(f"无法创建Chrome WebDriver: {e}")

# 使用示例:
# from selenium_wrapper import create_chrome_driver
# driver = create_chrome_driver()
'''
    
    with open('/app/selenium_wrapper.py', 'w') as f:
        f.write(wrapper_code)
    
    print("✅ 创建了Selenium包装器: /app/selenium_wrapper.py")

def main():
    print("🔧 ARM64架构Selenium修复工具")
    print("=" * 50)
    
    # 检查架构
    arch = check_architecture()
    
    # 查找ChromeDriver
    print("\n🔍 查找ChromeDriver...")
    chromedriver_paths = find_chromedriver()
    
    if not chromedriver_paths:
        print("❌ 未找到任何ChromeDriver")
        return
    
    # 测试每个ChromeDriver
    print("\n🧪 测试ChromeDriver...")
    working_paths = []
    for path in chromedriver_paths:
        if test_chromedriver(path):
            working_paths.append(path)
    
    if not working_paths:
        print("❌ 没有可用的ChromeDriver")
        return
    
    # 测试Selenium
    print("\n🌐 测试Selenium...")
    for path in working_paths:
        if test_selenium_with_path(path):
            print(f"✅ 推荐使用: {path}")
            break
    
    # 创建包装器
    print("\n📦 创建Selenium包装器...")
    create_selenium_wrapper()
    
    print("\n✅ 修复完成！")
    print("\n使用建议:")
    print("1. 在代码中使用明确的ChromeDriver路径")
    print("2. 使用创建的selenium_wrapper.py")
    print("3. 确保使用正确的Selenium版本")

if __name__ == "__main__":
    main()
