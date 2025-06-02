FROM node:18

# 设置工作目录
WORKDIR /usr/src/app

# 设置npm镜像源
RUN npm config set registry https://registry.npmjs.org/

# 首先复制package.json和相关配置文件
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# 安装依赖，使用重试逻辑
RUN npm install --no-fund --no-audit || npm install --no-fund --no-audit || npm install --no-fund --no-audit

# 复制其余源代码
COPY . .

# 跳过构建，直接启动开发服务器
# RUN npm run build

# 启动应用
ENTRYPOINT ["npm", "run", "dev", "--", "--host"]
