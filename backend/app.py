#!/usr/bin/env python3
"""
乘车记录管理系统后端API
基于Flask的RESTful API服务
"""
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os
import sys
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加父目录到Python路径以导入乘车记录管理器
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from multi_account_certificate_manager import MultiAccountRidingRecordManager
except ImportError as e:
    print(f"❌ 无法导入乘车记录管理器: {e}")
    print("请确保 multi_account_certificate_manager.py 文件存在")
    sys.exit(1)

# 尝试导入生成功能（可选）
GENERATION_AVAILABLE = False
generate_riding_record = None

try:
    from headless_automation import generate_riding_record
    GENERATION_AVAILABLE = True
    print("✅ 生成功能可用")
except ImportError as e:
    print(f"⚠️ 生成功能不可用: {e}")
    print("💡 如需使用生成功能，请安装 selenium: pip install selenium")
    GENERATION_AVAILABLE = False

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'tokaido-automation'
    })

# 静态文件服务（用于Docker部署）
@app.route('/')
def serve_index():
    """提供前端主页"""
    try:
        return send_file('../frontend/dist/index.html')
    except FileNotFoundError:
        return jsonify({
            'error': 'Frontend not built',
            'message': 'Please build the frontend first or use development mode'
        }), 404

@app.route('/<path:path>')
def serve_static(path):
    """提供前端静态文件"""
    try:
        return send_from_directory('../frontend/dist', path)
    except FileNotFoundError:
        # 对于SPA路由，返回index.html
        try:
            return send_file('../frontend/dist/index.html')
        except FileNotFoundError:
            return jsonify({
                'error': 'Frontend not built',
                'message': 'Please build the frontend first or use development mode'
            }), 404  # 允许跨域请求

# 配置 - 从环境变量读取
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'PASSWD')
CONFIG_FILE = os.getenv('CONFIG_FILE', '../accounts_config.json')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 全局管理器实例
manager = None
manager_lock = threading.Lock()

def get_manager():
    """获取管理器实例（线程安全）"""
    global manager
    with manager_lock:
        if manager is None:
            manager = MultiAccountRidingRecordManager(CONFIG_FILE)
        return manager

@app.route('/api/riding-record/check', methods=['POST'])
def check_riding_record():
    """检查单个账号的乘车记录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 获取管理器实例
        manager = get_manager()

        # 检查用户是否已在配置中
        user_exists = username in manager.accounts

        # 如果用户不存在，添加到配置中
        if not user_exists:
            print(f"🔍 用户 {username} 不在配置中，准备添加...")
            manager.add_account(username, password, username, True)
        else:
            # 如果用户存在，更新密码（可能已更改）
            manager.accounts[username]['password'] = password
            print(f"🔄 更新用户 {username} 的密码")

        has_record, record_info = manager.check_riding_record_for_user_force_login(username)

        # 更新结果到文件
        if has_record and isinstance(record_info, dict):
            manager.update_single_user_result(username, record_info)

        result = {
            'hasRecord': has_record,
            'message': '查询成功' if has_record else '暂无乘车记录',
            'userSaved': not user_exists  # 标识是否为新保存的用户
        }

        if has_record and isinstance(record_info, dict) and 'riding_record_details' in record_info:
            result['details'] = record_info['riding_record_details']

        # 如果是新用户，添加提示信息
        if not user_exists:
            result['message'] += f' (用户 {username} 已保存到配置文件)'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"检查乘车记录失败: {e}")
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@app.route('/api/riding-record/generate', methods=['POST'])
def generate_riding_record_api():
    """生成单个账号的乘车记录"""
    try:
        print(f"📥 收到生成请求")
        data = request.get_json()
        print(f"📋 请求数据: {data}")

        if data is None:
            print("❌ 请求数据为空")
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        username = data.get('username')
        password = data.get('password')
        print(f"👤 用户名: {username}, 密码长度: {len(password) if password else 0}")

        if not username or not password:
            print(f"❌ 用户名或密码为空: username={username}, password={'有' if password else '无'}")
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 调用headless_automation.py中的生成功能
        print(f"🚀 开始为用户 {username} 生成乘车记录...")
        print(f"🔧 生成功能状态: GENERATION_AVAILABLE={GENERATION_AVAILABLE}, generate_riding_record={generate_riding_record is not None}")

        if GENERATION_AVAILABLE and generate_riding_record:
            result = generate_riding_record(username, password)

            # 如果生成成功，立即查询并更新结果文件
            if result.get('success'):
                try:
                    temp_manager = MultiAccountRidingRecordManager(CONFIG_FILE)
                    temp_manager.accounts = {
                        username: {
                            'username': username,
                            'password': password,
                            'display_name': username,
                            'enabled': True
                        }
                    }

                    has_record, record_info = temp_manager.check_riding_record_for_user_force_login(username)
                    if has_record and isinstance(record_info, dict):
                        temp_manager.update_single_user_result(username, record_info)
                        print(f"✅ 生成成功后已更新 {username} 的记录到文件")
                except Exception as e:
                    print(f"⚠️ 生成成功但更新文件失败: {e}")
        else:
            result = {
                'success': False,
                'message': '生成功能不可用，请安装 selenium 模块'
            }

        return jsonify(result)
        
    except Exception as e:
        print(f"生成乘车记录失败: {e}")
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}'
        }), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if password == ADMIN_PASSWORD:
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '密码错误'
            }), 401
            
    except Exception as e:
        print(f"管理员登录失败: {e}")
        return jsonify({
            'success': False,
            'message': '登录失败'
        }), 500

@app.route('/api/admin/accounts', methods=['GET'])
def get_accounts():
    """获取所有账号信息（从缓存加载，快速显示）"""
    try:
        mgr = get_manager()

        # 读取缓存的结果文件
        results_file = os.path.join('results', 'multi_account_results.json')
        cached_results = {}

        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    cached_results = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                cached_results = {}

        accounts = []
        total_accounts = 0
        enabled_accounts = 0
        accounts_with_records = 0

        for username, account in mgr.accounts.items():
            if not account.get('enabled', True):
                continue

            # 从缓存中获取记录信息
            cached_info = cached_results.get(username, {})
            has_record = cached_info.get('has_riding_record', None)
            record_details = cached_info.get('info', {}).get('riding_record_details', {})
            last_check = cached_info.get('info', {}).get('check_time', None)

            # 构建详细的记录信息
            detailed_record_info = None
            if record_details:
                detailed_record_info = {
                    'boardingDate': record_details.get('riding_date'),
                    'expiryDate': record_details.get('expiry_date'),
                    'status': record_details.get('status'),
                    'validityStatus': record_details.get('expiry_status')
                }

            account_info = {
                'username': username,
                'password': account.get('password', ''),  # 添加密码字段用于生成功能
                'displayName': account.get('display_name', username),
                'enabled': account.get('enabled', True),
                'hasRecord': has_record,
                'recordDetails': detailed_record_info,
                'lastCheck': last_check
            }
            accounts.append(account_info)

            total_accounts += 1
            enabled_accounts += 1
            if has_record:
                accounts_with_records += 1

        # 计算统计信息
        success_rate = round((accounts_with_records / enabled_accounts) * 100, 1) if enabled_accounts > 0 else 0

        statistics = {
            'totalAccounts': total_accounts,
            'enabledAccounts': enabled_accounts,
            'accountsWithRecords': accounts_with_records,
            'successRate': success_rate
        }

        return jsonify({
            'accounts': accounts,
            'statistics': statistics
        })
        
    except Exception as e:
        print(f"获取账号信息失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取账号信息失败: {str(e)}'
        }), 500


@app.route('/api/admin/check-all', methods=['POST'])
def check_all_accounts():
    """检查所有账号的乘车记录（重新登录网站查询最新信息）"""
    try:
        print("🚀 开始检查所有账号的乘车记录...")
        mgr = get_manager()

        # 执行实时检查（强制重新登录，不使用cookies缓存）
        mgr.check_all_accounts_force_login()

        # 读取最新的结果文件
        results_file = os.path.join('..', 'results', 'multi_account_results.json')
        results = {}

        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                results = {}

        # 构建账号列表信息（包含最新的检查结果）
        accounts_list = []
        total_accounts = 0
        enabled_accounts = 0
        accounts_with_records = 0

        for username, account_config in mgr.accounts.items():
            if not account_config.get('enabled', True):
                continue

            account_result = results.get(username, {})
            has_record = account_result.get('has_riding_record', None)
            record_details = account_result.get('info', {}).get('riding_record_details', {})
            last_check = account_result.get('info', {}).get('check_time', None)

            # 构建详细的记录信息
            detailed_record_info = None
            if record_details:
                detailed_record_info = {
                    'boardingDate': record_details.get('riding_date'),
                    'expiryDate': record_details.get('expiry_date'),
                    'status': record_details.get('status'),
                    'validityStatus': record_details.get('expiry_status')
                }

            account_info = {
                'username': username,
                'displayName': account_config.get('display_name', username),
                'enabled': account_config.get('enabled', True),
                'hasRecord': has_record,
                'recordDetails': detailed_record_info,
                'lastCheck': last_check or datetime.now().isoformat()
            }
            accounts_list.append(account_info)

            total_accounts += 1
            enabled_accounts += 1
            if has_record:
                accounts_with_records += 1

        # 计算统计信息
        success_rate = round((accounts_with_records / enabled_accounts) * 100, 1) if enabled_accounts > 0 else 0

        statistics = {
            'totalAccounts': total_accounts,
            'enabledAccounts': enabled_accounts,
            'accountsWithRecords': accounts_with_records,
            'successRate': success_rate
        }

        print(f"✅ 检查完成，共 {enabled_accounts} 个账号，{accounts_with_records} 个有记录")

        return jsonify({
            'success': True,
            'statistics': statistics,
            'accounts': accounts_list
        })

    except Exception as e:
        print(f"检查所有账号失败: {e}")
        return jsonify({
            'success': False,
            'message': f'检查失败: {str(e)}'
        }), 500



if __name__ == '__main__':
    print("🚀 启动乘车记录管理系统后端服务...")
    print(f"📁 配置文件: {CONFIG_FILE}")
    print(f"🔐 管理员密码: {'*' * len(ADMIN_PASSWORD)}")  # 隐藏密码显示
    print(f"🌐 服务地址: http://{HOST}:{PORT}")
    print(f"🐛 调试模式: {'开启' if DEBUG else '关闭'}")
    print("=" * 50)

    app.run(host=HOST, port=PORT, debug=DEBUG)
