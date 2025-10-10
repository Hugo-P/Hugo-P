import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re
import os
from googletrans import Translator

def translate_to_traditional_chinese(text):
    try:
        translator = Translator()
        # 先翻譯成簡體中文
        result = translator.translate(text, dest='zh-tw')
        return result.text
    except Exception as e:
        print(f"翻譯時發生錯誤: {e}")
        return text  # 如果翻譯失敗，返回原文

def fetch_github_trending():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get('https://github.com/trending', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    trending_repos = []
    for idx, article in enumerate(soup.select('article.Box-row')[:10], 1):
        try:
            # 獲取倉庫資訊
            repo_link = article.select_one('h2 a')
            repo_path = repo_link['href'].strip('/')
            repo_url = f'https://github.com/{repo_path}'
            
            # 獲取描述並翻譯
            description = article.select_one('p')
            description = description.text.strip() if description else '無描述'
            if description and description != '無描述':
                description = translate_to_traditional_chinese(description)
            
            # 獲取程式語言
            language = article.select_one('[itemprop="programmingLanguage"]')
            language = language.text.strip() if language else '-'
            
            # 獲取星標數
            stars = article.select_one('a.Link--muted')
            stars = stars.text.strip() if stars else '0'
            stars = f'⭐ {stars}'
            
            trending_repos.append({
                'rank': idx,
                'name': repo_path,
                'url': repo_url,
                'description': description,
                'stars': stars,
                'language': language
            })
        except Exception as e:
            print(f"處理倉庫 {idx} 時發生錯誤: {e}")
            
    return trending_repos

def generate_trending_table(repos):
    table_rows = []
    for repo in repos:
        row = f"| {repo['rank']} | [{repo['name']}]({repo['url']}) | {repo['description']} | {repo['stars']} | {repo['language']} |"
        table_rows.append(row)
    return '\n'.join(table_rows)

def update_readme():
    # 獲取趨勢倉庫
    trending_repos = fetch_github_trending()
    
    # 生成表格內容
    table_content = generate_trending_table(trending_repos)
    
    # 讀取模板
    with open('.github/templates/README.md.tpl', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 獲取當前時間（使用台北時區）
    tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tz).strftime('%Y年%m月%d日 %H:%M:%S %Z')
    
    # 替換內容
    content = template.replace('{{TRENDING_TABLE}}', table_content)
    content = content.replace('{{LAST_UPDATED}}', current_time)
    
    # 寫入 README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_readme()