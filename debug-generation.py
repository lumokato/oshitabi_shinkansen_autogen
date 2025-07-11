#!/usr/bin/env python3
"""
生成功能调试脚本
用于在Docker容器内调试一键生成记录功能
"""

import sys
import os
import traceback
import time
from datetime import datetime

# 添加项目路径
sys.path.append('/app')

def test_imports():
    """测试导入模块"""
    print("🔍 测试模块导入...")
    
    try:
        from headless_automation import HeadlessAutomation
        print("✅ HeadlessAutomation 导入成功")
    except Exception as e:
        print(f"❌ HeadlessAutomation 导入失败: {e}")
        return False
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium 导入成功")
    except Exception as e:
        print(f"❌ Selenium 导入失败: {e}")
        return False
    
    return True

def test_browser_setup():
    """测试浏览器设置"""
    print("\n🌐 测试浏览器设置...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        print("正在启动浏览器...")
        driver = webdriver.Chrome(options=options)
        
        print("正在访问测试页面...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"✅ 浏览器测试成功，页面标题: {title}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ 浏览器测试失败: {e}")
        traceback.print_exc()
        return False

def test_headless_automation(username, password):
    """测试无头自动化功能"""
    print(f"\n🤖 测试无头自动化功能 (用户: {username})...")
    
    try:
        from headless_automation import HeadlessAutomation
        
        print("正在创建HeadlessAutomation实例...")
        automation = HeadlessAutomation(username, password)
        
        print("正在设置无头浏览器...")
        if not automation.setup_headless_browser():
            print("❌ 无头浏览器设置失败")
            return False
        
        print("✅ 无头浏览器设置成功")
        
        print("正在执行登录...")
        if not automation.perform_login():
            print("❌ 登录失败")
            return False
        
        print("✅ 登录成功")
        
        print("正在访问语音故事页面...")
        if not automation.access_voice_story():
            print("❌ 访问语音故事页面失败")
            return False
        
        print("✅ 访问语音故事页面成功")
        
        print("正在执行速度测试...")
        if not automation.perform_speed_test():
            print("❌ 速度测试失败")
            return False
        
        print("✅ 速度测试成功")
        
        print("正在清理资源...")
        automation.cleanup()
        
        print("✅ 无头自动化测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 无头自动化测试失败: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """测试环境变量"""
    print("\n🔧 测试环境变量...")
    
    env_vars = [
        'JR_LOGIN_URL',
        'VOICE_STORY_URL',
        'OSHITABI_LOGIN_URL',
        'RIDING_RECORD_URL',
        'TARGET_TEXT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: 未设置")

def debug_step_by_step(username, password):
    """分步调试"""
    print(f"\n🔍 分步调试 (用户: {username})...")
    
    try:
        from headless_automation import HeadlessAutomation
        
        automation = HeadlessAutomation(username, password)
        
        # 步骤1: 设置浏览器
        print("\n--- 步骤1: 设置浏览器 ---")
        if not automation.setup_headless_browser():
            print("❌ 步骤1失败")
            return
        print("✅ 步骤1成功")
        
        # 步骤2: 执行登录
        print("\n--- 步骤2: 执行登录 ---")
        try:
            result = automation.perform_login()
            if result:
                print("✅ 步骤2成功")
            else:
                print("❌ 步骤2失败")
                return
        except Exception as e:
            print(f"❌ 步骤2异常: {e}")
            traceback.print_exc()
            return
        
        # 步骤3: 访问语音故事
        print("\n--- 步骤3: 访问语音故事 ---")
        try:
            result = automation.access_voice_story()
            if result:
                print("✅ 步骤3成功")
            else:
                print("❌ 步骤3失败")
                return
        except Exception as e:
            print(f"❌ 步骤3异常: {e}")
            traceback.print_exc()
            return
        
        # 步骤4: 执行速度测试
        print("\n--- 步骤4: 执行速度测试 ---")
        try:
            result = automation.perform_speed_test()
            if result:
                print("✅ 步骤4成功")
            else:
                print("❌ 步骤4失败")
                return
        except Exception as e:
            print(f"❌ 步骤4异常: {e}")
            traceback.print_exc()
            return
        
        print("\n✅ 所有步骤完成")
        
        # 清理
        automation.cleanup()
        
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        traceback.print_exc()

def main():
    print("🐛 生成功能调试工具")
    print("=" * 50)
    
    # 基础测试
    if not test_imports():
        print("❌ 模块导入测试失败，无法继续")
        return
    
    test_environment()
    
    if not test_browser_setup():
        print("❌ 浏览器设置测试失败，无法继续")
        return
    
    # 获取用户输入
    print("\n" + "=" * 50)
    username = input("请输入测试用户名: ").strip()
    password = input("请输入测试密码: ").strip()
    
    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 完整测试")
    print("2. 分步调试")
    
    choice = input("请输入选择 (1-2): ").strip()
    
    if choice == "1":
        test_headless_automation(username, password)
    elif choice == "2":
        debug_step_by_step(username, password)
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
