import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def get_article_content_and_image(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기사 본문을 추출하는 로직 (웹사이트마다 다를 수 있음)
        content = ""
        image_url = ""
        
        if 'news1.kr' in url:
            content_tag = soup.select_one('#articles_detail')
            image_tag = soup.select_one('.news1_photo')
        elif 'newsis.com' in url:
            content_tag = soup.select_one('#textBody')
            text_list = []
            for element in content_tag.find_all('br'):
                next_element = element.next_sibling
                if next_element and isinstance(next_element, str):
                    text_list.append(next_element.strip())
            content = "\n".join(text_list)
            image_tag = soup.select_one('.article_photo img')
        elif 'fetv.co.kr' in url:
            content_tag = soup.select_one('.content')
            image_tag = soup.select_one('.photo')
        elif 'shinailbo.co.kr' in url:
            content_tag = soup.select_one('.article-content')
            image_tag = soup.select_one('.article-image')
        elif 'viva100.com' in url:
            content_tag = soup.select_one('.article-body')
            image_tag = soup.select_one('.article-image')
        elif 'edaily.co.kr' in url:
            content_tag = soup.select_one('.newsView')
            image_tag = soup.select_one('.img')
        elif 'fnnews.com' in url:
            content_tag = soup.select_one('.article')
            image_tag = soup.select_one('.article_photo')
        else:
            content_tag = soup.get_text(strip=True)
            image_tag = None
        
        if content_tag and not content:
            content = content_tag.get_text(strip=True)
        
        if image_tag and image_tag.get('src'):
            image_url = image_tag['src']
        
        return content, image_url
    except Exception as e:
        return str(e), ""

def get_naver_news(query, sort='1', start_page=1, end_page=2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    articles = []
    now = datetime.now()

    for page in range(start_page, end_page + 1):
        if len(articles) >= 10:
            break

        url = f"https://search.naver.com/search.naver?where=news&query={query}&sm=tab_opt&sort={sort}&start={page*10-9}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select('.news_wrap'):
            if len(articles) >= 10:
                break
            
            title_tag = item.select_one('.news_tit')
            title = title_tag.get_text() if title_tag else "No title"
            link = title_tag['href'] if title_tag else "No link"
            source = item.select_one('.info_group .press').get_text() if item.select_one('.info_group .press') else "No source"
            date_text = item.select_one('.info_group span.info').get_text() if item.select_one('.info_group span.info') else "No date"
            summary = item.select_one('.news_dsc').get_text() if item.select_one('.news_dsc') else "No summary"
            
            # 상대적인 시간을 절대적인 시간으로 변환
            date_time = None
            if '분 전' in date_text:
                minutes = int(date_text.replace('분 전', '').strip())
                date_time = now - timedelta(minutes=minutes)
            elif '시간 전' in date_text:
                hours = int(date_text.replace('시간 전', '').strip())
                date_time = now - timedelta(hours=hours)
            elif '일 전' in date_text:
                days = int(date_text.replace('일 전', '').strip())
                date_time = now - timedelta(days=days)
            elif '주 전' in date_text:
                weeks = int(date_text.replace('주 전', '').strip())
                date_time = now - timedelta(weeks=weeks)
            else:
                # 절대적 날짜 형식 처리 (YYYY.MM.DD)
                try:
                    date_time = datetime.strptime(date_text, '%Y.%m.%d.')
                except ValueError:
                    pass
            
            # 5시간 이전의 데이터만 포함
            if date_time and (now - date_time).total_seconds() / 3600 <= 5:
                article_content, image_url = get_article_content_and_image(link)
                articles.append({
                    'title': title,
                    'link': link,
                    'source': source,
                    'date': date_text,
                    'summary': summary,
                    'content': article_content,
                    'image_url': image_url
                })
    
    return articles

query = ""
articles = get_naver_news(query, start_page=1, end_page=2)

# JSON 파일로 저장
with open('naver_news.json', 'w', encoding='utf-8') as json_file:
    json.dump(articles, json_file, ensure_ascii=False, indent=4)

print("JSON 파일로 저장되었습니다.")
