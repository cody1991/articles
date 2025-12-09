#!/usr/bin/env python3
"""
生成 VuePress 侧边栏配置文件（按公众号分类）
"""
import json
import re
from pathlib import Path

def generate_sidebar_config():
    # 公众号映射 - 支持多个源目录
    authors = {
        '金渐层': ['docs/金渐层', 'wechat_articles/金渐层'],
        '只做主升不做调整': ['docs/只做主升不做调整', 'wechat_articles/只做主升不做调整']
    }
    
    all_configs = {}
    
    # 处理每个公众号
    for author_name, source_dirs in authors.items():
        articles = []
        
        # 尝试从配置的目录中读取文章
        for source_dir in source_dirs:
            articles_dir = Path(source_dir)
            if not articles_dir.exists():
                continue
                
            md_files = sorted([
                f for f in articles_dir.glob('*.md') 
                if f.name not in ['index.md', 'README.md', '投资与人生建议总结.md']
            ])
            
            # 解析文件名获取信息
            for md_file in md_files:
                name = md_file.name
                # 格式: 001_2025-12-08_我们不能再摔倒了~.md
                match = re.match(r'(\d+)_(\d{4}-\d{2}-\d{2})_(.+)\.md', name)
                if match:
                    num, date, title = match.groups()
                    article_info = {
                        'num': int(num),
                        'date': date,
                        'title': title,
                        'path': f'/{author_name}/{name}',
                        'filename': name
                    }
                    
                    # 避免重复（根据日期和标题去重）
                    if not any(a['date'] == date and a['title'] == title for a in articles):
                        articles.append(article_info)
            
            # 如果在这个目录找到了文章，就不再尝试后续目录
            if articles:
                break
        
        if not articles:
            print(f'⚠️ 目录不存在或为空: {source_dirs}')
            continue
        
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
    sidebar_config = {}
    for author_name in all_configs.keys():
        sidebar_config[author_name] = {
            'text': author_name,
            'children': all_configs[author_name]['articles']
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

