# 公众号文章管理流程

## 📋 配置检查清单

**⚠️ 重要：添加新公众号时，需要同步更新以下文件**（AI 助手会检查这些）：

1. ✅ `download_wechat_articles.py` → `WECHAT_ACCOUNTS` 字典
2. ✅ `generate_sidebar.py` → `authors` 字典
3. ✅ `docs/README.md` → 公众号导航部分
4. ✅ `docs/公众号名字/README.md` → 新建首页
5. ✅ `PROMPT_FOR_NEW_SESSION.md` → 更新此清单

**提示**：如果某个公众号在某个文件中漏掉了，网站可能无法正常显示！

---

## 快速操作

### 检查增量（推荐）- 默认行为
直接运行下载脚本，会自动跳过已存在的文件，只下载新文章：
```bash
python3 download_wechat_articles.py 公众号名字
```

### 强制重新下载 - 覆盖已有文件
如果需要重新下载某个公众号的所有文章（覆盖本地文件）：
```bash
python3 download_wechat_articles.py 公众号名字 --force
# 或简写
python3 download_wechat_articles.py 公众号名字 -f
```

### 检查所有公众号是否有新文章
```bash
python3 download_wechat_articles.py all --check
```

---

## 详细步骤 - 新增公众号

### 步骤 1️⃣：在 download_wechat_articles.py 中添加配置
编辑 `WECHAT_ACCOUNTS` 字典，添加新条目：
```python
WECHAT_ACCOUNTS = {
    '金渐层': { ... },
    '只做主升不做调整': { ... },
    '新公众号': {
        'url': '公众号合集地址（从微信复制）',
        'output_dir': 'docs/新公众号'
    }
}
```

### 步骤 2️⃣：在 generate_sidebar.py 中添加映射
编辑 `authors` 字典，添加相同条目：
```python
authors = {
    '金渐层': 'docs/金渐层',
    '只做主升不做调整': 'docs/只做主升不做调整',
    '新公众号': 'docs/新公众号'  # ← 添加这行
}
```

### 步骤 3️⃣：下载文章
```bash
python3 download_wechat_articles.py 新公众号
```
**文件格式**：`YYYY-MM-DD_标题.md` （自动按日期排序）

### 步骤 4️⃣：生成侧边栏
```bash
python3 generate_sidebar.py
```

### 步骤 5️⃣：创建公众号首页
在 `docs/新公众号/` 创建 `README.md`（参考其他公众号格式）

### 步骤 6️⃣：更新主页导航
编辑 `docs/README.md`，在公众号导航部分添加新条目

### 步骤 7️⃣：更新此 Prompt
在本文件顶部的清单中记录新公众号

---

## ✨ 当前可用公众号

| 公众号 | 文章数 | 状态 |
|------|------|-----|
| 金渐层 | 327 篇 | ✅ |
| 只做主升不做调整 | 170 篇 | ✅ |
| 口罩哥 | 28 篇 | ✅ |

---

## 🔍 验证清单

新增公众号后，请检查：
- [ ] `sidebar_config.json` 是否包含新公众号的所有文章
- [ ] `docs/新公众号/` 目录是否存在并包含 `.md` 文件
- [ ] `docs/README.md` 的导航栏是否显示新公众号
- [ ] VuePress 网站左侧侧边栏是否显示新公众号及其文章列表
