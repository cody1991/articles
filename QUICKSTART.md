# 快速开始指南

## 1. 安装依赖

```bash
npm install
```

## 2. 启动开发服务器

```bash
npm run docs:dev
```

然后在浏览器中打开 http://localhost:8080

## 3. 构建生产版本

```bash
npm run docs:build
```

构建后的文件会在 `dist` 目录中。

## 4. 更新文章列表

如果添加了新文章，运行以下命令重新生成侧边栏：

```bash
python3 generate_sidebar.py
```

或者：

```bash
./generate_sidebar.py
```

## 项目结构说明

- `docs/` - VuePress 文档目录
  - `docs/.vuepress/config.js` - VuePress 配置文件
  - `docs/articles/` - 文章目录（软链接到 `wechat_articles`）
  - `docs/README.md` - 首页
- `wechat_articles/` - 原始文章目录
- `sidebar_config.json` - 侧边栏配置（自动生成）
- `generate_sidebar.py` - 侧边栏生成脚本

## 注意事项

- 确保 Node.js 版本 >= 16
- 文章文件命名格式：`序号_日期_标题.md`
- 侧边栏会自动按日期倒序排列

