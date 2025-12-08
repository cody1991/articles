import { defineUserConfig } from 'vuepress'
import { defaultTheme } from '@vuepress/theme-default'
import { viteBundler } from '@vuepress/bundler-vite'
import { getDirname, path } from '@vuepress/utils'
import { readFileSync } from 'fs'

const __dirname = getDirname(import.meta.url)

// 读取侧边栏配置
const sidebarConfig = JSON.parse(
  readFileSync(path.resolve(__dirname, '../../sidebar_config.json'), 'utf-8')
)

export default defineUserConfig({
  lang: 'zh-CN',
  title: '微信文章集',
  description: '微信文章收藏与阅读',
  
  // 设置基础路径
  base: '/',
  
  // 使用 Vite 作为打包工具
  bundler: viteBundler(),
  
  // 配置主题
  theme: defaultTheme({
    // 导航栏配置
    navbar: [
      {
        text: '首页',
        link: '/',
      },
      {
        text: '文章列表',
        link: '/articles/',
      },
    ],
    
    // 侧边栏配置
    sidebar: {
      '/articles/': [
        {
          text: '所有文章',
          children: sidebarConfig,
        },
      ],
      '/': [
        {
          text: '最新文章',
          children: sidebarConfig.slice(0, 20),
        },
      ],
    },
    
    // 显示所有页面的标题
    sidebarDepth: 2,
    
    // 编辑链接
    editLink: false,
    
    // 最后更新时间
    lastUpdated: true,
    lastUpdatedText: '最后更新',
    
    // 贡献者
    contributors: false,
  }),
  
  // 配置目录别名
  alias: {
    '@': path.resolve(__dirname, '../'),
  },
  
  // 配置 Markdown
  // 注意：code.lineNumbers 选项已移除，如需代码行号请使用插件
  
  // 开发服务器配置
  port: 8080,
  
  // 构建配置
  dest: 'dist',
})

