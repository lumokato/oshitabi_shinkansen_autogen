# 配置文件说明

## 📋 配置文件概览

项目包含两个主要配置文件：

1. **`.env`** - 环境变量配置（系统设置）
2. **`accounts_config.json`** - 账号配置（用户信息）

## 🔧 环境变量配置 (.env)

### 创建配置文件

```bash
cp .env.example .env
```

### 配置项说明

```env
# 管理员密码 - 用于访问管理员模式
ADMIN_PASSWORD=your_secure_password_here

# 服务器配置
HOST=0.0.0.0          # 监听地址，0.0.0.0表示所有接口
PORT=8000             # 服务端口
DEBUG=false           # 调试模式，生产环境建议设为false

# 文件路径配置
CONFIG_FILE=accounts_config.json    # 账号配置文件路径
RESULTS_DIR=results                 # 结果文件存储目录
```

### 安全建议

- ✅ 使用强密码作为管理员密码
- ✅ 生产环境设置 `DEBUG=false`
- ✅ 定期更换管理员密码
- ❌ 不要将 `.env` 文件提交到版本控制

## 👥 账号配置 (accounts_config.json)

### 创建配置文件

```bash
cp accounts_config_example.json accounts_config.json
```

### 配置格式

```json
{
    "accounts": {
        "账号标识符": {
            "username": "实际登录用户名",
            "password": "实际登录密码",
            "display_name": "界面显示名称",
            "enabled": true
        }
    }
}
```

### 字段详解

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `username` | string | ✅ | 实际的登录用户名 |
| `password` | string | ✅ | 实际的登录密码 |
| `display_name` | string | ✅ | 在界面中显示的友好名称 |
| `enabled` | boolean | ✅ | 是否启用此账号（true/false） |

### 配置示例

```json
{
    "accounts": {
        "kanon": {
            "username": "kanon511",
            "password": "mySecurePassword123",
            "display_name": "Kanon",
            "enabled": true
        },
        "tomori": {
            "username": "tomori_user",
            "password": "anotherPassword456", 
            "display_name": "Tomori",
            "enabled": true
        },
        "test_user": {
            "username": "test_account",
            "password": "test_password",
            "display_name": "测试账号",
            "enabled": false
        }
    }
}
```

### 账号管理

#### 添加新账号

1. 在 `accounts` 对象中添加新的键值对
2. 设置 `enabled: true` 启用账号
3. 重启服务使配置生效

#### 禁用账号

1. 设置 `enabled: false`
2. 重启服务使配置生效

#### 删除账号

1. 从配置文件中删除对应条目
2. 重启服务使配置生效

### 安全建议

- ✅ 使用强密码
- ✅ 定期更换密码
- ✅ 妥善保管配置文件
- ✅ 限制文件访问权限
- ❌ 不要将配置文件提交到版本控制
- ❌ 不要在日志中输出密码

## 🔒 文件权限设置

### Linux/macOS

```bash
# 设置配置文件权限（仅所有者可读写）
chmod 600 .env
chmod 600 accounts_config.json

# 设置目录权限
chmod 700 results/
```

### Docker环境

配置文件通过卷挂载，确保宿主机文件权限正确：

```bash
# 设置宿主机文件权限
sudo chown $(id -u):$(id -g) accounts_config.json .env
chmod 600 accounts_config.json .env
```

## 🔄 配置更新

### 热更新

某些配置支持热更新（无需重启）：
- ❌ 环境变量（需要重启）
- ❌ 账号配置（需要重启）

### 重启服务

```bash
# Docker环境
./deploy.sh restart

# 本地开发
# 停止服务后重新启动
```

## 🐛 配置问题排查

### 常见错误

1. **配置文件不存在**
   ```
   ⚠️ 配置文件 accounts_config.json 不存在
   ```
   **解决方案**：复制示例文件并编辑

2. **JSON格式错误**
   ```
   ❌ JSON解析失败
   ```
   **解决方案**：检查JSON语法，使用在线JSON验证器

3. **权限错误**
   ```
   ❌ 无法读取配置文件
   ```
   **解决方案**：检查文件权限

### 验证配置

```bash
# 验证JSON格式
python -m json.tool accounts_config.json

# 测试环境变量
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Admin password set:', bool(os.getenv('ADMIN_PASSWORD')))"
```

## 📝 配置模板

### 最小配置

```json
{
    "accounts": {
        "user1": {
            "username": "your_username",
            "password": "your_password",
            "display_name": "Your Name",
            "enabled": true
        }
    }
}
```

### 多账号配置

```json
{
    "accounts": {
        "primary": {
            "username": "primary_user",
            "password": "primary_pass",
            "display_name": "主账号",
            "enabled": true
        },
        "secondary": {
            "username": "secondary_user", 
            "password": "secondary_pass",
            "display_name": "备用账号",
            "enabled": true
        },
        "testing": {
            "username": "test_user",
            "password": "test_pass",
            "display_name": "测试账号",
            "enabled": false
        }
    }
}
```
