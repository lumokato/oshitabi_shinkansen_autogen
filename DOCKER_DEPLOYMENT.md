# Docker 部署指南

## 🚀 快速开始

### 1. 使用部署脚本（推荐）

```bash
# 启动服务
./deploy.sh start

# 查看日志
./deploy.sh logs

# 停止服务
./deploy.sh stop
```

### 2. 手动部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

## 📋 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 内存
- 至少 1GB 磁盘空间


## ⚙️ 配置

### 环境变量

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

主要配置项：

```env
ADMIN_PASSWORD=your_secure_password
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 账号配置

1. 复制示例配置文件：
```bash
cp accounts_config_example.json accounts_config.json
```

2. 编辑配置文件添加您的真实账号信息：
```bash
nano accounts_config.json
```

3. 配置格式说明：
```json
{
    "accounts": {
        "your_key": {
            "username": "实际用户名",
            "password": "实际密码",
            "display_name": "显示名称",
            "enabled": true
        }
    }
}
```

**重要提醒：**
- 请使用真实的用户名和密码
- `enabled: false` 的账号将被跳过
- 配置文件包含敏感信息，请妥善保管

## 🌐 GitHub Container Registry

### 本地构建和使用

项目使用本地构建方式，无需外部镜像仓库：

```bash
# 构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start
```

### Docker调试方案

当一键生成记录功能出现问题时，可以使用以下调试工具：

#### 1. 交互式调试工具

```bash
# 启动调试菜单
./debug-docker.sh

# 或直接执行特定调试功能
./debug-docker.sh logs      # 查看实时日志
./debug-docker.sh enter     # 进入容器调试
./debug-docker.sh test      # 测试生成API
./debug-docker.sh browser   # 检查浏览器环境
./debug-docker.sh errors    # 查看错误日志
```

#### 2. 进入容器手动调试

```bash
# 进入容器
docker exec -it tokaido-automation bash

# 在容器内运行调试脚本
python debug-generation.py

# 或手动测试各个组件
chromium --version
chromedriver --version
python -c "from headless_automation import HeadlessAutomation; print('OK')"
```

#### 3. 常见问题排查

**浏览器问题：**
```bash
# 检查浏览器是否正常
docker exec tokaido-automation chromium --headless --no-sandbox --dump-dom https://www.google.com

# 检查ChromeDriver
docker exec tokaido-automation chromedriver --version
```

**内存问题：**
```bash
# 监控资源使用
./debug-docker.sh monitor

# 检查内存使用
docker stats tokaido-automation
```

**网络问题：**
```bash
# 测试网络连接
docker exec tokaido-automation curl -I https://orange-system.jr-central.co.jp

# 检查DNS解析
docker exec tokaido-automation nslookup oshi-tabi.voistock.com
```

## 🔧 常用命令

```bash
# 查看服务状态
./deploy.sh status

# 重启服务
./deploy.sh restart

# 查看实时日志
./deploy.sh logs

# 清理所有资源
./deploy.sh cleanup

# 进入容器
docker-compose exec tokaido-automation bash

# 查看容器资源使用
docker stats tokaido-automation
```

## 🛡️ 生产环境部署

### 使用 Nginx 反向代理

启用 nginx 服务：

```bash
docker-compose --profile production up -d
```

### SSL 证书配置

1. 将 SSL 证书放在 `ssl/` 目录
2. 修改 `nginx.conf` 添加 HTTPS 配置

### 安全建议

- 修改默认管理员密码
- 使用强密码
- 定期更新镜像
- 监控日志文件
- 限制网络访问

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口使用
   netstat -tulpn | grep :8000
   
   # 修改端口
   # 编辑 docker-compose.yml 中的端口映射
   ```

2. **内存不足**
   ```bash
   # 检查内存使用
   docker stats
   
   # 调整资源限制
   # 编辑 docker-compose.yml 中的 deploy.resources
   ```

3. **Chrome 启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs tokaido-automation

   # 可能需要增加共享内存
   # 在 docker-compose.yml 中添加：
   # shm_size: 2gb
   ```

4. **前端构建失败**
   ```bash
   # 如果遇到 terser 相关错误
   # 检查 vite.config.js 中的 minify 设置
   # 应该使用 'esbuild' 而不是 'terser'

   # 查看构建日志
   docker-compose build --no-cache
   ```

### 日志查看

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs tokaido-automation

# 实时跟踪日志
docker-compose logs -f tokaido-automation
```

## 📊 监控

### 健康检查

访问健康检查端点：
```
http://localhost:8000/api/health
```

### 资源监控

```bash
# 查看容器资源使用
docker stats tokaido-automation

# 查看磁盘使用
docker system df
```

## 🔄 更新

### 更新镜像

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
./deploy.sh restart
```

### 备份数据

```bash
# 备份配置和结果
tar -czf backup-$(date +%Y%m%d).tar.gz accounts_config.json results/
```
