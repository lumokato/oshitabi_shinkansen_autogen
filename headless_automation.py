#!/usr/bin/env python3
"""
无头浏览器自动化版本
基于成功的有头浏览器流程转换为无头模式
"""
import time
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class HeadlessAutomation:
    def __init__(self, username=None, password=None):
        self.driver = None
        self.temp_dir = None
        self.username = username
        self.password = password
        
        # URLs - 从环境变量读取
        self.jr_login_url = os.getenv('JR_LOGIN_URL', 'https://orange-system.jr-central.co.jp/user/login?redirect=true')
        self.voice_story_url = os.getenv('VOICE_STORY_URL', 'https://oshi-tabi.voistock.com/bang-dream-10th/voice/685b5e4be9c4185cba9c2a94')
    
    def setup_headless_browser(self):
        """设置无头浏览器"""
        try:
            print(f"🌐 设置无头浏览器...")
            
            # 创建临时用户数据目录
            self.temp_dir = tempfile.mkdtemp(prefix="selenium_headless_")
            
            options = Options()
            
            # 无头模式
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # 避免检测
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 独立环境
            options.add_argument(f"--user-data-dir={self.temp_dir}")
            options.add_argument("--remote-debugging-port=9225")
            
            # 启动Chromium浏览器（明确指定ChromeDriver路径）
            from selenium.webdriver.chrome.service import Service

            # 尝试不同的ChromeDriver路径
            chromedriver_paths = [
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                'chromedriver'
            ]

            service = None
            for path in chromedriver_paths:
                try:
                    service = Service(executable_path=path)
                    break
                except:
                    continue

            if service is None:
                # 如果找不到ChromeDriver，尝试使用系统默认
                service = Service()

            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ 使用 Chromium")

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"✅ 无头浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 无头浏览器设置失败: {e}")
            return False
    
    def perform_login(self):
        """执行登录"""
        try:
            print(f"🔑 执行JR Central登录...")
            
            self.driver.get(self.jr_login_url)
            time.sleep(3)
            
            # 填写登录信息
            username_field = self.driver.find_element("name", "login_id")
            password_field = self.driver.find_element("name", "password")
            
            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)
            
            # 提交登录
            login_button = self.driver.find_element("css selector", "button[type='submit'], input[type='submit']")
            login_button.click()
            
            time.sleep(5)
            print(f"✅ 登录完成")
            return True
            
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False
    
    def execute_complete_automation(self):
        """执行完整自动化（无头模式）"""
        try:
            print(f"🚀 执行完整自动化...")
            
            # 访问目标页面
            self.driver.get(self.voice_story_url)
            time.sleep(5)
            
            # 注入完整自动化脚本（简化版，避免jQuery依赖）
            automation_script = """
            console.log('🚀 无头模式自动化开始');
            
            // 设置绕过模式
            window.BYPASS_MODE = true;
            localStorage.setItem('speedFlag', 'true');
            localStorage.setItem('speed', '285');
            localStorage.setItem('flagRegistered', Date.now());
            localStorage.setItem('allowedItem', '685b5e4be9c4185cba9c2a94');
            
            sessionStorage.setItem('orangeLog_speed', '285');
            sessionStorage.setItem('orangeLog_lat', '35.6762');
            sessionStorage.setItem('orangeLog_lon', '139.7653');
            sessionStorage.setItem('orangeLog_direction', 'up');
            sessionStorage.setItem('orangeLog_uniqueId', 'bypass');
            
            // 显示播放器
            var overlayCard = document.getElementById('overlay-card');
            var waitingCard = document.getElementById('waiting-card');
            var voicePlayer = document.getElementById('voice-player');
            
            if (overlayCard) overlayCard.style.display = 'none';
            if (waitingCard) waitingCard.style.display = 'none';
            if (voicePlayer) {
                voicePlayer.style.display = 'flex';
                voicePlayer.style.flexDirection = 'column';
                voicePlayer.style.alignItems = 'center';
            }
            
            console.log('✅ 播放器已显示');
            
            // 触发问卷系统
            var surveyId = '686028a78a3e46623d889025';
            sessionStorage.setItem('openedSurvey', surveyId);
            
            if (typeof getSurvey === 'function') {
                getSurvey(surveyId);
            }
            
            console.log('📝 问卷系统已触发');
            
            return true;
            """
            
            self.driver.execute_script(automation_script)
            print(f"✅ 自动化脚本执行完成")
            
            # 等待问卷生成
            print(f"⏳ 等待问卷生成...")
            for i in range(10):
                time.sleep(1)
                
                survey_exists = self.driver.execute_script("""
                var surveyModal = document.getElementById('surveyModal');
                var surveyForm = document.getElementById('survey-form');
                return surveyModal && surveyForm && surveyModal.style.display !== 'none';
                """)
                
                if survey_exists:
                    print(f"✅ 问卷已生成")
                    break
                
                print(f"  等待问卷... ({i+1}/10)")
            
            if not survey_exists:
                print(f"⚠️ 问卷未生成，但继续执行填写脚本")
            
            # 执行问卷填写
            fill_script = """
            console.log('📝 开始填写问卷');
            
            var filled = 0;
            
            // 填写所有问题
            var questions = [
                {id: 'question-682657575eda8', value: '東京'},
                {id: 'question-682657575f052', value: '名古屋'},
                {id: 'question-682657575f1ab', value: '１'},
                {id: 'question-682657575f300', value: '１'},
                {id: 'question-682657575f450', value: 'はい'},
                {id: 'question-682657575f594', value: '推し旅公式Xまたは公式サイト'},
                {id: 'question-682657575f6df', value: 'いいえ'}
            ];
            
            questions.forEach(function(q) {
                var element = document.getElementById(q.id);
                if (element) {
                    element.value = q.value;
                    element.dispatchEvent(new Event('change'));
                    filled++;
                    console.log('✅ 填写:', q.id, '=', q.value);
                }
            });
            
            console.log('📊 填写完成，共', filled, '项');
            
            // 提交问卷
            setTimeout(function() {
                var submitButton = document.getElementById('survey-submit');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.click();
                    console.log('✅ 问卷已提交');
                } else {
                    console.log('❌ 未找到提交按钮');
                }
            }, 1000);
            
            return filled;
            """
            
            filled_count = self.driver.execute_script(fill_script)
            print(f"✅ 问卷填写完成，填写了 {filled_count} 项")
            
            # 等待提交完成
            time.sleep(3)
            
            # 检查最终状态
            final_status = self.driver.execute_script("""
            return {
                url: window.location.href,
                title: document.title,
                speedFlag: localStorage.getItem('speedFlag'),
                surveySubmitted: !document.getElementById('surveyModal') || 
                                document.getElementById('surveyModal').style.display === 'none'
            };
            """)
            
            print(f"📊 最终状态:")
            print(f"  URL: {final_status['url']}")
            print(f"  标题: {final_status['title']}")
            print(f"  速度标志: {final_status['speedFlag']}")
            print(f"  问卷已提交: {final_status['surveySubmitted']}")
            
            return final_status['surveySubmitted']
            
        except Exception as e:
            print(f"❌ 自动化执行失败: {e}")
            return False
    
    def run_headless_automation(self):
        """运行无头自动化"""
        try:
            print(f"🤖 开始无头自动化流程")
            print("=" * 60)
            
            # 1. 设置无头浏览器
            if not self.setup_headless_browser():
                return False
            
            # 2. 执行登录
            if not self.perform_login():
                return False
            
            # 3. 执行完整自动化
            success = self.execute_complete_automation()
            
            print(f"\n" + "=" * 60)
            print("无头自动化完成")
            print("=" * 60)
            
            if success:
                print(f"🎉 无头自动化成功完成！")
                print(f"💡 问卷已自动填写和提交")
            else:
                print(f"⚠️ 无头自动化部分成功")
            
            return success
            
        except Exception as e:
            print(f"❌ 无头自动化失败: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
            
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

def generate_riding_record(username, password):
    """
    生成乘车记录的公共接口

    Args:
        username (str): 用户名
        password (str): 密码

    Returns:
        dict: 包含成功状态和消息的字典
    """
    try:
        if not username or not password:
            return {
                'success': False,
                'message': '用户名和密码不能为空'
            }

        print(f"🚀 开始为用户 {username} 生成乘车记录...")

        automation = HeadlessAutomation(username, password)
        success = automation.run_headless_automation()

        if success:
            return {
                'success': True,
                'message': '乘车记录生成成功！'
            }
        else:
            return {
                'success': False,
                'message': '乘车记录生成失败，请检查账号信息或重试'
            }

    except Exception as e:
        print(f"❌ 生成乘车记录时发生错误: {e}")
        return {
            'success': False,
            'message': f'生成失败: {str(e)}'
        }

def main():
    """主函数"""
    print(f"🤖 无头浏览器自动化工具")
    print("=" * 60)
    
    automation = HeadlessAutomation()
    success = automation.run_headless_automation()
    
    print(f"\n🏁 无头自动化结果: {'成功' if success else '失败'}")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
