# GitHub Pages 部署指南

## 自动部署（推荐）

项目已配置 GitHub Actions，当你推送代码到 `master` 分支时，会自动构建并部署到 GitHub Pages。

**访问地址：** https://cody1991.github.io/articles/

## 手动部署

如果你想手动部署，可以运行：

```bash
npm run deploy
```

这个命令会：
1. 构建 VuePress 站点
2. 将构建结果推送到 `gh-pages` 分支

## 首次部署设置

1. **启用 GitHub Pages**：
   - 进入仓库 Settings → Pages
   - Source 选择 `gh-pages` 分支
   - 保存设置

2. **等待 Actions 完成**：
   - 推送代码后，GitHub Actions 会自动运行
   - 可以在仓库的 Actions 标签页查看构建状态
   - 构建完成后，站点会在几分钟内上线

## 注意事项

1. **base 路径**：当前配置的 base 路径是 `/articles/`，与仓库名匹配
   - 如果仓库名改变，需要同步修改 `docs/.vuepress/config.js` 中的 `base` 配置

2. **软链接问题**：GitHub Actions 会自动将 `wechat_articles` 复制到 `docs/articles`，避免软链接问题

3. **Jekyll 禁用**：项目包含 `.nojekyll` 文件，确保 GitHub Pages 不使用 Jekyll 处理

## 更新部署

每次更新文章或配置后：
- **自动部署**：直接推送代码到 `master` 分支即可
- **手动部署**：运行 `npm run deploy`

## 自定义域名（可选）

如果想使用自定义域名：
1. 在仓库根目录创建 `CNAME` 文件，写入你的域名
2. 在域名 DNS 设置中添加 CNAME 记录指向 `cody1991.github.io`
3. 修改 `docs/.vuepress/config.js` 中的 `base` 为 `/`
