# 公众号文章管理流程

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

---

## 详细步骤 - 新增公众号

### 1. 检查现有配置
首先检查 `download_wechat_articles.py` 中的 `WECHAT_ACCOUNTS` 配置，看看是否需要下载新的文章或更新现有内容。

**当前可用的公众号**：
- 金渐层
- 只做主升不做调整
- 口罩哥

### 2. 添加新公众号
如果需要新增公众号，请在 `download_wechat_articles.py` 的 `WECHAT_ACCOUNTS` 字典中添加新条目：

```python
WECHAT_ACCOUNTS = {
    '公众号名字': {
        'url': '公众号合集地址',
        'output_dir': 'docs/公众号名字'
    },
    # ... 其他公众号
}
```

### 3. 下载文章
运行下载脚本：
```bash
python3 download_wechat_articles.py 公众号名字
```

**文件命名格式**：`YYYY-MM-DD_标题.md`
- 日期作为主键，新增文章自动按日期排序
- 新文章会自动插入到正确的位置，无需编号

### 4. 生成侧边栏配置
下载完成后，运行生成脚本来更新网站侧边栏：
```bash
python3 generate_sidebar.py
```

### 5. 创建 README.md
在新公众号目录下创建 `docs/公众号名字/README.md` 来提供公众号首页介绍（参考其他公众号的格式）

### 6. 更新主页
更新 `docs/README.md` 中的公众号导航部分，添加新公众号的链接和文章数

## 完成后验证
- 检查 `sidebar_config.json` 是否包含新的公众号文章
- 验证 `docs/` 下有新公众号的目录和文章
