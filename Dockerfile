# Python后端镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Chromium浏览器和ChromeDriver（支持所有架构）
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 确保ChromeDriver在标准路径
RUN ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver

# 验证安装
RUN echo "验证浏览器安装..." \
    && chromium --version \
    && chromedriver --version \
    && echo "ChromeDriver路径:" \
    && which chromedriver \
    && ls -la /usr/bin/chromedriver /usr/local/bin/chromedriver \
    && echo "浏览器验证完成"

# 复制Python依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY backend/ ./backend/
COPY *.py ./
COPY .env.example .env

# 复制预构建的前端文件
COPY frontend/dist ./frontend/dist

# 创建必要的目录
RUN mkdir -p results

# 设置环境变量
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["python", "backend/app.py"]
