# GitHub Pages 部署指南

## 快速部署

直接运行以下命令即可部署到 GitHub Pages：

```bash
npm run deploy
```

这个命令会：
1. 构建 VuePress 站点
2. 将构建结果推送到 `gh-pages` 分支

## 部署后的访问地址

部署完成后，你的站点将在以下地址可访问：

**https://cody1991.github.io/articles/**

## 注意事项

1. **首次部署**：需要确保 GitHub 仓库已启用 GitHub Pages，并设置为从 `gh-pages` 分支提供服务
   - 进入仓库 Settings → Pages
   - Source 选择 `gh-pages` 分支
   - 保存设置

2. **base 路径**：当前配置的 base 路径是 `/articles/`，与仓库名匹配
   - 如果仓库名改变，需要同步修改 `docs/.vuepress/config.js` 中的 `base` 配置

3. **本地开发**：本地开发时，base 路径仍然是 `/articles/`，确保与生产环境一致

## 更新部署

每次更新文章或配置后，只需再次运行：

```bash
npm run deploy
```

gh-pages 会自动更新站点内容。

## 自定义域名（可选）

如果想使用自定义域名：
1. 在仓库根目录创建 `CNAME` 文件，写入你的域名
2. 在域名 DNS 设置中添加 CNAME 记录指向 `cody1991.github.io`
3. 修改 `docs/.vuepress/config.js` 中的 `base` 为 `/`

