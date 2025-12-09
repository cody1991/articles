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

    def get_album_articles(self, count=10, begin_msgid=None, begin_itemidx=None, reverse=None, retry=3):
        """获取合集文章列表"""
        api_url = "https://mp.weixin.qq.com/mp/appmsgalbum"
        
        params = {
            '__biz': self.biz,
            'action': 'getalbum',
            'album_id': self.album_id,
            'count': count,
            'f': 'json',
        }
        
        # reverse=True 时加 is_reverse=1，reverse=False 时不加
        if reverse is True:
            params['is_reverse'] = 1
        
        if begin_msgid and begin_itemidx:
            params['begin_msgid'] = begin_msgid
            params['begin_itemidx'] = begin_itemidx
        
        for attempt in range(retry):
            try:
                response = self.session.get(api_url, params=params, headers=self.headers, timeout=60)
                response.raise_for_status()
                data = response.json()
                return data
            except Exception as e:
                if attempt < retry - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"    获取失败 ({attempt+1}/{retry}): {e}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"获取文章列表失败（已重试{retry}次）: {e}")
                    return None
        return None

    def get_all_articles(self, reverse=True):
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
        
        # 按时间排序
        if reverse:
            all_articles = sorted(all_articles, key=lambda x: self.parse_time(x.get('create_time', 0)), reverse=True)
        
        return all_articles

    def download_article_content(self, url, retry=2):
        """下载单篇文章内容"""
        for attempt in range(retry):
            try:
                response = self.session.get(url, headers=self.headers, timeout=60)
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
                if attempt < retry - 1:
                    print(f"    下载失败 ({attempt+1}/{retry})，2秒后重试...")
                    time.sleep(2)
                else:
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
                # 格式: YYYY-MM-DD_标题.md
                match = re.match(r'(\d{4}-\d{2}-\d{2})_(.+)\.md', filename)
                if match:
                    date, title = match.groups()
                    existing[filename] = {
                        'date': date,
                        'title': title
                    }
        return existing
    
    def get_latest_article(self):
        """获取线上最新的一篇文章，通过两次请求对比时间戳来判断真正最新的"""
        print("正在获取线上最新文章...")
        
        # 第一次请求（不加 is_reverse）
        data1 = self.get_album_articles(count=1, reverse=False)
        article1 = None
        
        if data1:
            article_list = data1.get('getalbum_resp', {}).get('article_list', [])
            if isinstance(article_list, dict):
                article1 = article_list if article_list else None
            elif isinstance(article_list, list):
                article1 = article_list[0] if article_list else None
        
        # 第二次请求（加 is_reverse=1）
        data2 = self.get_album_articles(count=1, reverse=True)
        article2 = None
        
        if data2:
            article_list = data2.get('getalbum_resp', {}).get('article_list', [])
            if isinstance(article_list, dict):
                article2 = article_list if article_list else None
            elif isinstance(article_list, list):
                article2 = article_list[0] if article_list else None
        
        # 对比时间戳，返回更新的那个
        if article1 and article2:
            time1 = self.parse_time(article1.get('create_time', 0))
            time2 = self.parse_time(article2.get('create_time', 0))
            return article1 if time1 >= time2 else article2
        elif article1:
            return article1
        elif article2:
            return article2
        
        return None
    
    def check_if_latest_exists(self):
        """检查本地是否已有最新文章，返回 (has_latest, latest_article, local_latest_date)"""
        latest_article = self.get_latest_article()
        if not latest_article:
            print("  ✗ 无法获取线上最新文章")
            return False, None, None
        
        # 用 API 返回的时间戳转换成日期
        create_time = self.parse_time(latest_article.get('create_time', 0))
        latest_date = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
        latest_title = latest_article.get('title', '无标题')
        
        print(f"  线上最新: {latest_date} - {latest_title}")
        
        # 获取本地已有的文章
        existing_articles = self.get_existing_articles()
        if not existing_articles:
            print(f"  本地无文章，需要下载")
            return False, latest_article, None
        
        # 获取本地最新日期（从文件名中提取）
        local_dates = [info['date'] for info in existing_articles.values()]
        local_latest_date = max(local_dates) if local_dates else None
        
        print(f"  本地最新: {local_latest_date}")
        
        # 对比日期，如果线上最新日期 > 本地最新日期，则需要下载
        if local_latest_date and latest_date <= local_latest_date:
            print(f"  ✓ 已有最新文章或更新的文章，无需下载")
            return True, latest_article, local_latest_date
        else:
            print(f"  ✗ 有新文章，需要下载")
            return False, latest_article, local_latest_date

    def download_all(self, reverse=True, download_content=True, skip_existing=False):
        """
        下载所有文章
        
        Args:
            reverse: True为倒序（从最新到最旧），False为正序
            download_content: 是否下载文章内容
            skip_existing: 是否跳过已下载的文章
        """
        articles = self.get_all_articles(reverse=reverse)
        
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
            filename = f"{date_str}_{safe_title}.md"
            
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


def download_account(account_name, skip_existing=False, check_only=False):
    """下载指定公众号的文章"""
    if account_name not in WECHAT_ACCOUNTS:
        print(f"未知公众号: {account_name}")
        print(f"可用的公众号: {', '.join(WECHAT_ACCOUNTS.keys())}")
        return
    
    config = WECHAT_ACCOUNTS[account_name]
    print(f"\n{'='*50}")
    print(f"处理: {account_name}")
    print(f"{'='*50}\n")
    
    downloader = WeChatAlbumDownloader(config['url'], output_dir=config['output_dir'])
    
    # 检查是否已有最新文章
    if check_only or skip_existing:
        has_latest, latest_article, local_latest = downloader.check_if_latest_exists()
        if has_latest and check_only:
            print()
            return
    
    if skip_existing:
        print("模式: 只下载新文章（跳过已存在的）")
    
    print()
    downloader.download_all(reverse=True, download_content=True, skip_existing=skip_existing)


def download_all_accounts(skip_existing=False, check_only=False):
    """下载所有公众号的文章"""
    for account_name in WECHAT_ACCOUNTS.keys():
        download_account(account_name, skip_existing=skip_existing, check_only=check_only)
        print("\n" + "="*50 + "\n")


def main():
    import sys
    
    # 处理参数
    skip_existing = True
    account_name = None
    check_only = False
    
    for arg in sys.argv[1:]:
        if arg == '--force' or arg == '-f':
            skip_existing = False
        elif arg == '--check' or arg == '-c':
            check_only = True
        else:
            account_name = arg
    
    if account_name:
        if account_name == 'all':
            download_all_accounts(skip_existing=skip_existing, check_only=check_only)
        else:
            download_account(account_name, skip_existing=skip_existing, check_only=check_only)
    else:
        print("用法:")
        print(f"  检查所有:     python3 download_wechat_articles.py all --check")
        print(f"  检查指定:     python3 download_wechat_articles.py <公众号名> --check")
        print(f"  下载所有:     python3 download_wechat_articles.py all")
        print(f"  下载指定:     python3 download_wechat_articles.py <公众号名>")
        print(f"  强制重新下载: python3 download_wechat_articles.py <公众号名> --force")
        print(f"\n参数说明:")
        print(f"  --check, -c: 只检查是否有新文章，不下载")
        print(f"  --force, -f: 强制重新下载，覆盖已有文件")
        print(f"\n默认行为: 检查线上最新文章，若本地已有则跳过，否则下载")
        print(f"\n可用的公众号:")
        for name in WECHAT_ACCOUNTS.keys():
            print(f"  - {name}")
        print(f"\n示例:")
        print(f"  python3 download_wechat_articles.py all --check")
        print(f"  python3 download_wechat_articles.py 金渐层")
        print(f"  python3 download_wechat_articles.py 只做主升不做调整 -f")


if __name__ == "__main__":
    main()
