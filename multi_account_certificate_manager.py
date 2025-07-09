#!/usr/bin/env python3
"""
多账号乘车记录管理器
支持动态账号管理，外部配置文件，强制重新登录
"""
import requests
import json
import re
import time
import os
import base64
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保results目录存在
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

class MultiAccountRidingRecordManager:
    def __init__(self, config_file='accounts_config.json'):
        self.config_file = config_file
        self.accounts = {}

        # URLs - 从环境变量读取
        self.jr_login_url = os.getenv('JR_LOGIN_URL', 'https://orange-system.jr-central.co.jp/user/login?redirect=true')
        self.riding_record_url = os.getenv('RIDING_RECORD_URL', 'https://oshi-tabi.voistock.com/bang-dream-10th/mygo/certificate/data')
        self.oshitabi_login_url = os.getenv('OSHITABI_LOGIN_URL', 'https://oshi-tabi.voistock.com/orange/login.php')
        self.target_text = os.getenv('TARGET_TEXT', '新幹線乗車証明')

        # 加载配置
        self.load_accounts_config()
    
    def load_accounts_config(self):
        """加载账号配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    # 支持两种格式：数组格式和对象格式
                    if isinstance(config.get('accounts'), list):
                        # 数组格式：转换为以username为key的对象格式
                        accounts_list = config.get('accounts', [])
                        self.accounts = {}
                        for account in accounts_list:
                            username = account.get('username')
                            if username:
                                self.accounts[username] = {
                                    'username': username,
                                    'password': account.get('password'),
                                    'display_name': account.get('description', username),
                                    'enabled': account.get('active', True)
                                }
                    else:
                        # 对象格式：直接使用
                        self.accounts = config.get('accounts', {})

                print(f"✅ 加载了 {len(self.accounts)} 个账号配置")

                # 显示账号列表（不显示密码）
                for username, account in self.accounts.items():
                    status = "启用" if account.get('enabled', True) else "禁用"
                    print(f"  📋 {account.get('display_name', username)} ({username}) - {status}")

            else:
                print(f"⚠️ 配置文件 {self.config_file} 不存在")
                print(f"💡 请创建 {self.config_file} 文件并添加您的账号信息")
                print("📄 配置文件格式示例:")
                print("""
{
  "accounts": {
    "account1": {
      "username": "your_username",
      "password": "your_password",
      "display_name": "显示名称",
      "enabled": true
    }
  }
}""")
                return
        except Exception as e:
            print(f"❌ 加载账号配置失败: {e}")
            return
    


    
    def perform_login_and_get_cookie(self, username):
        """执行登录并获取cookie"""
        try:
            if username not in self.accounts:
                print(f"❌ 未找到账号 {username} 的配置")
                return None
            
            account = self.accounts[username]
            if not account.get('enabled', True):
                print(f"⚠️ 账号 {username} 已禁用")
                return None
            
            print(f"🔑 为 {account.get('display_name', username)} 执行登录...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': self.jr_login_url
            })
            
            # 1. 获取登录页面
            response = session.get(self.jr_login_url)
            if response.status_code != 200:
                print(f"❌ 获取登录页面失败: {response.status_code}")
                return None
            
            # 2. 提取CSRF令牌
            csrf_patterns = [
                r'name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']',
                r'value=["\']([^"\']+)["\'][^>]*name=["\']_token["\']',
            ]
            
            csrf_token = None
            for pattern in csrf_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    csrf_token = matches[0]
                    break
            
            if not csrf_token:
                print("❌ 未找到CSRF令牌")
                return None
            
            # 3. 提交登录表单
            form_data = {
                '_token': csrf_token,
                'redirect': 'true',
                'login_id': account['username'],
                'password': account['password']
            }
            
            login_response = session.post(
                self.jr_login_url,
                data=form_data,
                allow_redirects=True
            )
            
            # 4. 检查登录是否成功并处理重定向
            if "redirectForm" in login_response.text and "oshi-tabi.voistock.com" in login_response.text:
                print("🔄 执行oshi-tabi重定向...")
                
                # 提取重定向表单数据
                otp_match = re.search(r'name="otp" value="([^"]+)"', login_response.text)
                login_id_match = re.search(r'name="loginId" value="([^"]+)"', login_response.text)
                register_id_match = re.search(r'name="registerId" value="([^"]+)"', login_response.text)
                
                if otp_match and login_id_match and register_id_match:
                    oshitabi_login_data = {
                        'otp': otp_match.group(1),
                        'loginId': login_id_match.group(1),
                        'registerId': register_id_match.group(1)
                    }
                    
                    oshitabi_response = session.post(
                        self.oshitabi_login_url,
                        data=oshitabi_login_data,
                        allow_redirects=True
                    )
                    
                    # 5. 获取oshitabi cookie
                    oshitabi_cookie = None
                    for cookie in session.cookies:
                        if cookie.name == 'oshitabi':
                            oshitabi_cookie = cookie.value
                            break
                    
                    if oshitabi_cookie:
                        print(f"✅ 成功获得 {username} 的oshitabi cookie")
                        return oshitabi_cookie
                    else:
                        print(f"❌ 未获得 {username} 的oshitabi cookie")
                        return None
                else:
                    print("❌ 无法提取重定向表单数据")
                    return None
            else:
                print(f"❌ {username} 登录失败")
                return None
                
        except Exception as e:
            print(f"❌ {username} 登录失败: {e}")
            return None
    

    


    def extract_riding_record_details(self, content):
        """提取乘车记录详细信息"""
        try:
            details = {
                "riding_date": None,
                "expiry_date": None,
                "status": None,
                "expiry_status": None
            }
            
            # 提取有効期限
            expiry_patterns = [
                r'有効期限[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)まで',
                r'tillDate[^>]*>([^<]+)</div>'
            ]

            for pattern in expiry_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    expiry_date = matches[0].strip()
                    # 去掉"まで"后缀（如果存在）
                    if expiry_date.endswith('まで'):
                        expiry_date = expiry_date[:-2]
                    details["expiry_date"] = expiry_date
                    print(f"📅 有效期限: {details['expiry_date']}")
                    break
            
            # 提取乗車日
            riding_patterns = [
                r'乗車日[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',
                r'ridingDate[^>]*>([^<]+)</div>'
            ]
            
            for pattern in riding_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    details["riding_date"] = matches[0].strip()
                    print(f"🚄 乗車日: {details['riding_date']}")
                    break
            
            # 提取状态
            if re.search(r'CERTIFIED!', content, re.IGNORECASE):
                details["status"] = "CERTIFIED!"
                print(f"✅ 状态: CERTIFIED!")
            
            # 检查有效期状态
            if details["expiry_date"]:
                details["expiry_status"] = self.check_expiry_status(details["expiry_date"])
                print(f"⏰ 有效期状态: {details['expiry_status']}")
            
            return details
            
        except Exception as e:
            print(f"❌ 提取乘车记录详细信息失败: {e}")
            return {}
    
    def check_expiry_status(self, expiry_date_str):
        """检查有效期状态"""
        try:
            # 解析日期
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', expiry_date_str)
            if match:
                year, month, day = match.groups()
                expiry_date = datetime(int(year), int(month), int(day))
                current_date = datetime.now()
                
                if current_date <= expiry_date:
                    days_remaining = (expiry_date - current_date).days
                    return f"有效（还有{days_remaining}天）"
                else:
                    days_expired = (current_date - expiry_date).days
                    return f"已过期（过期{days_expired}天）"
            
            return "日期格式无法解析"
            
        except Exception as e:
            return f"检查失败: {str(e)}"
    


    def check_all_accounts_force_login(self):
        """检查所有账号的乘车记录（强制重新登录，不使用cookies缓存）"""
        try:
            print(f"🚄 多账号乘车记录管理器（强制重新登录）")
            print("=" * 60)

            if not self.accounts:
                print("❌ 没有配置任何账号")
                print(f"💡 请编辑 {self.config_file} 添加账号信息")
                return False

            results = {}
            all_have_records = True

            for username, account in self.accounts.items():
                if not account.get('enabled', True):
                    print(f"⏭️ 跳过已禁用的账号: {username}")
                    continue

                # 强制重新登录检查
                has_record, record_info = self.check_riding_record_for_user_force_login(username)
                results[username] = {
                    "has_riding_record": has_record,
                    "info": record_info
                }

                if not has_record:
                    all_have_records = False

            # 保存总体结果
            with open(os.path.join(RESULTS_DIR, 'multi_account_results.json'), 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\n" + "=" * 60)
            print("强制重新登录检查完成")
            print("=" * 60)

            # 统计
            total_accounts = len([a for a in self.accounts.values() if a.get('enabled', True)])
            accounts_with_records = sum(1 for r in results.values() if r["has_riding_record"])

            print(f"📊 统计:")
            print(f"  总账号数: {total_accounts}")
            print(f"  有乘车记录账号: {accounts_with_records}")
            print(f"  成功率: {accounts_with_records/total_accounts*100:.1f}%" if total_accounts > 0 else "  成功率: 0%")

            return all_have_records

        except Exception as e:
            print(f"❌ 强制重新登录检查失败: {e}")
            return False

    def check_riding_record_for_user_force_login(self, username):
        """检查指定用户的乘车记录（强制重新登录，不使用cookies缓存）"""
        try:
            if username not in self.accounts:
                return False, f"账号 {username} 不存在"

            account = self.accounts[username]
            display_name = account.get('display_name', username)

            print(f"\n📋 检查 {display_name} ({username}) 的乘车记录（强制重新登录）")
            print("-" * 50)

            # 强制重新登录获取新的cookie（不使用缓存）
            print(f"🔄 强制重新登录 {username}...")
            cookie = self.perform_login_and_get_cookie(username)
            if not cookie:
                return False, "重新登录失败，无法获取cookie"

            # 使用新获取的cookie访问证书页面
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })

            session.cookies.set('oshitabi', cookie, domain='.voistock.com')
            session.cookies.set('oshitabi', cookie, domain='oshi-tabi.voistock.com')

            # 访问乘车记录页面
            response = session.get(self.riding_record_url, timeout=15)

            if response.status_code != 200:
                return False, f"乘车记录页面访问失败: HTTP {response.status_code}"

            # 保存页面内容
            with open(os.path.join(RESULTS_DIR, f'{username}_riding_record_page.html'), 'w', encoding='utf-8') as f:
                f.write(response.text)

            # 检查乘车记录
            has_riding_record = self.target_text in response.text

            if has_riding_record:
                print(f"✅ {display_name} 已有乘车记录")

                # 提取详细信息
                details = self.extract_riding_record_details(response.text)

                result = {
                    "username": username,
                    "display_name": display_name,
                    "has_riding_record": True,
                    "riding_record_details": details,
                    "check_time": datetime.now().isoformat()
                }

                # 保存个人结果
                with open(os.path.join(RESULTS_DIR, f'{username}_riding_record_result.json'), 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                return True, result
            else:
                print(f"❌ {display_name} 暂无乘车记录")
                result = {
                    "username": username,
                    "display_name": display_name,
                    "has_riding_record": False,
                    "check_time": datetime.now().isoformat()
                }
                return False, result

        except Exception as e:
            print(f"❌ 强制重新登录检查 {username} 乘车记录失败: {e}")
            return False, str(e)

    def update_single_user_result(self, username, record_info):
        """
        更新单个用户的结果到multi_account_results.json文件

        Args:
            username (str): 用户名
            record_info (dict): 记录信息
        """
        try:
            results_file = os.path.join(RESULTS_DIR, 'multi_account_results.json')

            # 读取现有结果
            results = {}
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    results = {}

            # 更新单个用户的结果
            results[username] = {
                "has_riding_record": True,
                "info": record_info
            }

            # 保存更新后的结果
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"✅ 已更新 {username} 的查询结果到文件")

        except Exception as e:
            print(f"❌ 更新单个用户结果失败: {e}")

def main():
    """主函数"""
    manager = MultiAccountRidingRecordManager()
    success = manager.check_all_accounts_force_login()

    print(f"\n🏁 检查结果: {'所有账号都有乘车记录' if success else '部分账号无乘车记录或检查失败'}")
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
