#!/usr/bin/env python3
"""
单篇微信文章下载器

用法示例：
  python3 single_article_import.py <文章链接> --dir docs/美投investing
  python3 single_article_import.py <文章链接> --dir docs/美投investing --date 2025-12-26 --title 自定义标题

依赖：requests、html2text，并复用 download_wechat_articles.WeChatAlbumDownloader 的解析与图片下载能力。
"""

import argparse
import os
import re
from datetime import datetime
from typing import Optional

import requests

from download_wechat_articles import WeChatAlbumDownloader




def fetch_article_html(session: requests.Session, url: str, headers: dict[str, str]) -> str:
    resp = session.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.text


def extract_title(html: str) -> str:
    patterns = [
        r"msg_title\s*=\s*\"([^\"]+)\"",
        r"<meta[^>]+property=['\"]og:title['\"][^>]+content=['\"]([^'\"]+)['\"]",
    ]
    for pattern in patterns:
        m = re.search(pattern, html)
        if m:
            return m.group(1).strip()
    return "未命名文章"


def extract_publish_datetime(html: str) -> datetime:
    # 优先使用 publish_time 字符串
    m = re.search(r"publish_time\s*=\s*\"([^\"]+)\"", html)
    if m:
        try:
            return datetime.strptime(m.group(1).strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    # 其次尝试 ct 时间戳（秒）
    m = re.search(r"var\s+ct\s*=\s*\"?(\d{10})", html)
    if m:
        try:
            ts = int(m.group(1))
            return datetime.fromtimestamp(ts)
        except Exception:
            pass
    # 兜底当前时间
    return datetime.now()


def download_single_article(url: str, output_dir: str, override_title: Optional[str], override_date: Optional[str]):
    downloader = WeChatAlbumDownloader(url, output_dir=output_dir)

    # 获取 HTML
    html = fetch_article_html(downloader.session, url, downloader.headers)

    # 标题与时间
    title = override_title or extract_title(html)
    publish_dt = extract_publish_datetime(html)
    if override_date:
        publish_dt = datetime.strptime(override_date, "%Y-%m-%d")

    date_str = publish_dt.strftime("%Y-%m-%d")
    time_str = publish_dt.strftime("%Y-%m-%d %H:%M:%S")
    safe_title = downloader.sanitize_filename(title)
    filename = f"{date_str}_{safe_title}.md"

    os.makedirs(output_dir, exist_ok=True)

    # 下载正文（含图片）
    content_md = downloader.download_article_content(url, date_str, safe_title)

    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**发布时间**: {time_str}\n\n")
        f.write(f"**原文链接**: [{url}]({url})\n\n")
        f.write("---\n\n")
        if content_md:
            f.write(content_md)
        else:
            f.write("*内容获取失败，请访问原文链接查看*")

    print(f"✅ 已保存: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="单篇微信文章下载")
    parser.add_argument("url", help="微信文章链接")
    parser.add_argument("--dir", dest="output_dir", default="docs/单篇文章", help="输出目录，默认 docs/单篇文章")
    parser.add_argument("--date", dest="date", help="自定义发布日期，格式 YYYY-MM-DD，可选")
    parser.add_argument("--title", dest="title", help="自定义标题，可选")
    args = parser.parse_args()

    download_single_article(args.url, args.output_dir, args.title, args.date)


if __name__ == "__main__":
    main()
