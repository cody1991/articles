#!/usr/bin/env python3
"""
生成 VuePress 侧边栏配置文件
"""
import json
import re
from pathlib import Path

def generate_sidebar_config():
    # 读取文章列表
    articles_dir = Path('wechat_articles')
    md_files = sorted([
        f for f in articles_dir.glob('*.md') 
        if f.name not in ['index.md', '投资与人生建议总结.md', 'README.md']
    ])
    
    # 解析文件名获取信息
    articles = []
    for md_file in md_files:
        name = md_file.name
        # 格式: 001_2025-12-08_我们不能再摔倒了~.md
        match = re.match(r'(\d+)_(\d{4}-\d{2}-\d{2})_(.+)\.md', name)
        if match:
            num, date, title = match.groups()
            articles.append({
                'num': int(num),
                'date': date,
                'title': title,
                'path': f'/articles/{name}',
                'filename': name
            })
    
    # 按日期倒序排列（最新的在前）
    articles.sort(key=lambda x: (x['date'], x['num']), reverse=True)
    
    # 生成侧边栏配置 - 包含文本和链接
    sidebar = [
        {
            'text': f"{article['date']} - {article['title']}",
            'link': article['path']
        }
        for article in articles
    ]
    
    # 保存为 JSON
    with open('sidebar_config.json', 'w', encoding='utf-8') as f:
        json.dump(sidebar, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 已生成侧边栏配置，共 {len(articles)} 篇文章')
    return len(articles)

if __name__ == '__main__':
    generate_sidebar_config()

