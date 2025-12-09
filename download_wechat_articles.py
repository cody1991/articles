#!/usr/bin/env python3
"""
微信公众号合集文章下载器
支持多个公众号合集的下载
"""

import requests
import json
import time
import os
import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from html import unescape
import html2text

class WeChatAlbumDownloader:
    def __init__(self, album_url, output_dir="articles"):
        self.album_url = album_url
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # 解析URL参数
        parsed = urlparse(album_url)
        params = parse_qs(parsed.query)
        self.biz = params.get('__biz', [''])[0]
        self.album_id = params.get('album_id', [''])[0]
        
        # 设置请求头，模拟微信浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)',
            'Referer': 'https://mp.weixin.qq.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # HTML转Markdown转换器
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # 不换行

    def get_album_articles(self, count=10, begin_msgid=None, begin_itemidx=None):
        """获取合集文章列表"""
        api_url = "https://mp.weixin.qq.com/mp/appmsgalbum"
        
        params = {
            '__biz': self.biz,
            'action': 'getalbum',
            'album_id': self.album_id,
            'count': count,
            'f': 'json',
        }
        
        if begin_msgid and begin_itemidx:
            params['begin_msgid'] = begin_msgid
            params['begin_itemidx'] = begin_itemidx
        
        try:
            response = self.session.get(api_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"获取文章列表失败: {e}")
            return None

    def get_all_articles(self):
        """获取所有文章列表"""
        all_articles = []
        begin_msgid = None
        begin_itemidx = None
        page = 1
        
        print("正在获取文章列表...")
        
        while True:
            print(f"  获取第 {page} 页...")
            data = self.get_album_articles(count=20, begin_msgid=begin_msgid, begin_itemidx=begin_itemidx)
            
            if not data:
                break
            
            article_list = data.get('getalbum_resp', {}).get('article_list', [])
            
            if not article_list:
                break
            
            all_articles.extend(article_list)
            print(f"  已获取 {len(all_articles)} 篇文章")
            
            # 检查是否还有更多
            continue_flag = data.get('getalbum_resp', {}).get('continue_flag', 0)
            if continue_flag == 0:
                break
            
            # 获取下一页的起始位置
            last_article = article_list[-1]
            begin_msgid = last_article.get('msgid')
            begin_itemidx = last_article.get('itemidx')
            
            page += 1
            time.sleep(1)  # 避免请求过快
        
        print(f"\n共获取 {len(all_articles)} 篇文章")
        return all_articles

    def download_article_content(self, url):
        """下载单篇文章内容"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            # 提取文章正文
            # 尝试提取 js_content 区域
            content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', html_content, re.DOTALL)
            if content_match:
                content_html = content_match.group(1)
            else:
                # 备选：提取整个 rich_media_content
                content_match = re.search(r'<div[^>]*class="rich_media_content[^"]*"[^>]*>(.*?)</div>\s*(?:<div|<script)', html_content, re.DOTALL)
                if content_match:
                    content_html = content_match.group(1)
                else:
                    content_html = ""
            
            # 转换为Markdown
            if content_html:
                markdown_content = self.h2t.handle(content_html)
                # 清理多余空行
                markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
                return markdown_content.strip()
            
            return ""
        except Exception as e:
            print(f"    下载文章内容失败: {e}")
            return ""

    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', ' ', filename)
        filename = filename.strip()
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        return filename

    def parse_time(self, create_time):
        """解析时间戳，支持字符串和整数"""
        if isinstance(create_time, str):
            create_time = int(create_time)
        return create_time

    def get_existing_articles(self):
        """获取已下载的文章信息"""
        existing = {}
        if not os.path.exists(self.output_dir):
            return existing
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.md') and filename != 'index.md' and filename != 'README.md':
                # 格式: 001_2025-12-09_标题.md
                match = re.match(r'(\d+)_(\d{4}-\d{2}-\d{2})_(.+)\.md', filename)
                if match:
                    num, date, title = match.groups()
                    existing[filename] = {
                        'num': int(num),
                        'date': date,
                        'title': title
                    }
        return existing

    def download_all(self, reverse=True, download_content=True, skip_existing=False):
        """
        下载所有文章
        
        Args:
            reverse: True为倒序（从最新到最旧），False为正序
            download_content: 是否下载文章内容
            skip_existing: 是否跳过已下载的文章
        """
        articles = self.get_all_articles()
        
        if not articles:
            print("没有获取到文章")
            return
        
        # 获取已下载的文章
        existing_articles = self.get_existing_articles() if skip_existing else {}
        if existing_articles:
            print(f"检测到已下载的文章 {len(existing_articles)} 篇")
        
        # 按时间排序
        if reverse:
            articles = sorted(articles, key=lambda x: self.parse_time(x.get('create_time', 0)), reverse=True)
            print("\n按倒序（从新到旧）下载文章...")
        else:
            articles = sorted(articles, key=lambda x: self.parse_time(x.get('create_time', 0)))
            print("\n按正序（从旧到新）下载文章...")
        
        # 保存文章列表
        list_file = os.path.join(self.output_dir, "article_list.json")
        with open(list_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"文章列表已保存到: {list_file}")
        
        # 创建索引文件
        index_file = os.path.join(self.output_dir, "index.md")
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# 文章合集索引\n\n")
            f.write(f"共 {len(articles)} 篇文章\n\n")
            f.write("| 序号 | 标题 | 发布时间 |\n")
            f.write("|------|------|----------|\n")
            
            for idx, article in enumerate(articles, 1):
                title = article.get('title', '无标题')
                create_time = self.parse_time(article.get('create_time', 0))
                date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M')
                f.write(f"| {idx} | {title} | {date_str} |\n")
        
        print(f"索引文件已保存到: {index_file}")
        
        if not download_content:
            print("\n跳过文章内容下载")
            return
        
        # 下载每篇文章
        print("\n开始下载文章内容...")
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        for idx, article in enumerate(articles, 1):
            title = article.get('title', '无标题')
            url = article.get('url', '')
            create_time = self.parse_time(article.get('create_time', 0))
            date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
            
            # 检查是否已存在
            safe_title = self.sanitize_filename(title)
            filename = f"{idx:03d}_{date_str}_{safe_title}.md"
            
            if skip_existing and filename in existing_articles:
                print(f"[{idx}/{len(articles)}] 跳过（已存在）: {title}")
                skip_count += 1
                continue
            
            print(f"[{idx}/{len(articles)}] 下载: {title}")
            
            if not url:
                print("    跳过：无URL")
                fail_count += 1
                continue
            
            # 下载内容
            content = self.download_article_content(url)
            
            # 保存文件
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**发布时间**: {datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**原文链接**: [{url}]({url})\n\n")
                f.write("---\n\n")
                if content:
                    f.write(content)
                else:
                    f.write("*内容获取失败，请访问原文链接查看*")
            
            success_count += 1
            time.sleep(2)  # 避免请求过快被封
        
        print(f"\n下载完成！成功: {success_count}, 失败: {fail_count}, 跳过: {skip_count}")
        print(f"文章保存在: {os.path.abspath(self.output_dir)}")


# 公众号配置
WECHAT_ACCOUNTS = {
    '金渐层': {
        'url': 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg2NTkwNTM4MA==&action=getalbum&album_id=3896715541905326087',
        'output_dir': 'docs/金渐层'
    },
    '只做主升不做调整': {
        'url': 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzI2NzA2Mzg3MQ==&action=getalbum&album_id=3822716899375087617',
        'output_dir': 'docs/只做主升不做调整'
    }
}


def download_account(account_name, skip_existing=False):
    """下载指定公众号的文章"""
    if account_name not in WECHAT_ACCOUNTS:
        print(f"未知公众号: {account_name}")
        print(f"可用的公众号: {', '.join(WECHAT_ACCOUNTS.keys())}")
        return
    
    config = WECHAT_ACCOUNTS[account_name]
    print(f"\n{'='*50}")
    print(f"开始下载: {account_name}")
    if skip_existing:
        print("模式: 只下载新文章（跳过已存在的）")
    print(f"{'='*50}\n")
    
    downloader = WeChatAlbumDownloader(config['url'], output_dir=config['output_dir'])
    downloader.download_all(reverse=True, download_content=True, skip_existing=skip_existing)


def download_all_accounts(skip_existing=False):
    """下载所有公众号的文章"""
    for account_name in WECHAT_ACCOUNTS.keys():
        download_account(account_name, skip_existing=skip_existing)
        print("\n" + "="*50 + "\n")


def main():
    import sys
    
    # 检查参数
    skip_existing = False
    account_name = None
    
    for arg in sys.argv[1:]:
        if arg == '--skip-existing' or arg == '-s':
            skip_existing = True
        else:
            account_name = arg
    
    if account_name:
        if account_name == 'all':
            download_all_accounts(skip_existing=skip_existing)
        else:
            download_account(account_name, skip_existing=skip_existing)
    else:
        print("用法:")
        print(f"  下载所有: python3 download_wechat_articles.py all")
        print(f"  下载指定: python3 download_wechat_articles.py <公众号名>")
        print(f"  只下载新: python3 download_wechat_articles.py <公众号名> --skip-existing")
        print(f"  或简写:   python3 download_wechat_articles.py <公众号名> -s")
        print(f"\n可用的公众号:")
        for name in WECHAT_ACCOUNTS.keys():
            print(f"  - {name}")
        print(f"\n示例:")
        print(f"  python3 download_wechat_articles.py 金渐层 -s")
        print(f"  python3 download_wechat_articles.py all -s")


if __name__ == "__main__":
    main()
