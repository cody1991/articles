#!/usr/bin/env python3
"""
生成 VuePress 侧边栏配置文件（按公众号分类）
"""
import json
import re
from pathlib import Path

def generate_sidebar_config():
    # 公众号映射
    authors = {
        '金渐层': 'docs/金渐层'
    }
    
    all_configs = {}
    
    # 处理每个公众号
    for author_name, author_dir in authors.items():
        articles_dir = Path(author_dir)
        if not articles_dir.exists():
            print(f'⚠️ 目录不存在: {author_dir}')
            continue
            
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
                    'path': f'/{author_name}/{name}',
                    'filename': name
                })
        
        # 按日期倒序排列（最新的在前）
        articles.sort(key=lambda x: (x['date'], x['num']), reverse=True)
        
        # 生成侧边栏配置
        sidebar = [
            {
                'text': f"{article['date']} - {article['title']}",
                'link': article['path']
            }
            for article in articles
        ]
        
        all_configs[author_name] = {
            'articles': sidebar,
            'count': len(articles)
        }
    
    # 生成完整的侧边栏配置文件
    sidebar_config = {
        '金渐层': {
            'text': '金渐层',
            'children': all_configs['金渐层']['articles']
        }
    }
    
    # 保存为 JSON
    with open('sidebar_config.json', 'w', encoding='utf-8') as f:
        json.dump(sidebar_config, f, ensure_ascii=False, indent=2)
    
    # 输出统计信息
    total = sum(cfg['count'] for cfg in all_configs.values())
    print(f'✅ 已生成侧边栏配置')
    for author, cfg in all_configs.items():
        print(f'  📖 {author}: {cfg["count"]} 篇文章')
    print(f'  📊 总计: {total} 篇文章')
    return all_configs

if __name__ == '__main__':
    generate_sidebar_config()

