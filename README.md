# 🚄 乘车记录管理系统

一个自动化的乘车记录管理系统，支持多账号管理、自动生成和查询乘车记录。

## ✨ 功能特性

- 🔐 **多账号管理** - 支持批量管理多个用户账号
- 🤖 **自动化生成** - 无头浏览器自动生成乘车记录
- 📊 **实时查询** - 强制重新登录获取最新数据
- 🌐 **Web界面** - 现代化的前端管理界面
- 🐳 **Docker支持** - 完整的容器化部署方案
- 🔒 **安全配置** - 环境变量管理敏感信息
- ⚙️ **灵活配置** - 所有URL和文本都可通过环境变量配置

## 🚀 快速开始

### 方式一：Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/tokaido-automation.git
   cd tokaido-automation
   ```

2. **配置环境**
   ```bash
   # 复制环境变量文件
   cp .env.example .env

   # 复制账号配置文件
   cp accounts_config_example.json accounts_config.json

   # 编辑配置（设置管理员密码等）
   nano .env

   # 编辑账号配置（设置真实账号信息）
   nano accounts_config.json
   ```

3. **启动服务**
   ```bash
   # 使用部署脚本
   ./deploy.sh start
   
   # 或手动启动
   docker-compose up -d
   ```

4. **访问系统**
   - 前端界面: http://localhost:8001 (默认端口，可在.env中修改HOST_PORT)
   - API文档: http://localhost:8001/api/health

### 方式二：本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置文件**
   ```bash
   # 复制配置文件
   cp .env.example .env
   cp accounts_config_example.json accounts_config.json

   # 编辑配置文件
   nano .env
   nano accounts_config.json
   ```

3. **启动后端**
   ```bash
   cd backend
   python app.py
   ```

4. **启动前端**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📋 环境要求

### Docker部署
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 内存
- 支持 AMD64/ARM64 架构

### 本地开发
- Python 3.11+
- Node.js 18+
- Chromium浏览器
- 2GB+ 内存

## ⚙️ 配置说明

### 环境变量 (.env)

```env
# 管理员密码
ADMIN_PASSWORD=your_secure_password

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 文件路径
CONFIG_FILE=accounts_config.json
RESULTS_DIR=results
```

### 账号配置 (accounts_config.json)

从示例文件复制并编辑：
```bash
cp accounts_config_example.json accounts_config.json
```

配置格式：
```json
{
    "accounts": {
        "user1": {
            "username": "your_actual_username",
            "password": "your_actual_password",
            "display_name": "用户显示名称",
            "enabled": true
        },
        "user2": {
            "username": "another_username",
            "password": "another_password",
            "display_name": "另一个用户",
            "enabled": false
        }
    }
}
```

**字段说明：**
- `username`: 实际的登录用户名
- `password`: 实际的登录密码
- `display_name`: 在界面中显示的友好名称
- `enabled`: 是否启用此账号（true/false）

## 🌐 GitHub Container Registry

### 使用预构建镜像

```bash
# 拉取镜像
docker pull ghcr.io/your-username/tokaido-automation:latest

# 运行容器
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/accounts_config.json:/app/accounts_config.json:ro \
  -v $(pwd)/results:/app/results \
  ghcr.io/your-username/tokaido-automation:latest
```

### 手动构建

可以手动构建Docker镜像：
```bash
# 本地构建
./deploy.sh build

# 或使用docker-compose
docker-compose build
```

## 📖 API文档

### 用户模式API

- `POST /api/riding-record/check` - 查询乘车记录
- `POST /api/riding-record/generate` - 生成乘车记录

### 管理员模式API

- `GET /api/admin/accounts` - 获取账号列表（缓存）
- `POST /api/admin/check-all` - 检查所有账号（强制重新登录）

### 系统API

- `GET /api/health` - 健康检查

## 🛠️ 开发指南

### 项目结构

```
tokaido-automation/
├── backend/                 # 后端API服务
├── frontend/               # 前端Vue.js应用
├── backup_files/           # 备份文件
├── results/               # 结果文件
├── Dockerfile             # Docker镜像构建
├── docker-compose.yml     # Docker编排
├── deploy.sh             # 部署脚本
└── requirements.txt      # Python依赖
```

### 核心组件

- **multi_account_certificate_manager.py** - 多账号管理核心
- **headless_automation.py** - 无头浏览器自动化
- **backend/app.py** - Flask API服务器
- **frontend/** - Vue.js前端应用

## 🔧 常用命令

```bash
# Docker部署
./deploy.sh start          # 启动服务
./deploy.sh stop           # 停止服务
./deploy.sh logs           # 查看日志
./deploy.sh status         # 查看状态

# 开发调试
python multi_account_certificate_manager.py  # 直接运行管理器
python backend/app.py                        # 启动API服务
```

## 🛡️ 安全建议

- 修改默认管理员密码
- 使用强密码策略
- 定期更新依赖
- 监控系统日志
- 限制网络访问

## 📊 监控

### 健康检查
```bash
curl http://localhost:8000/api/health
```

### 资源监控
```bash
docker stats tokaido-automation
```

## 🐛 故障排除

详见 [Docker部署指南](DOCKER_DEPLOYMENT.md)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请创建Issue或联系维护者。
