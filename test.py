import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def search_naver_news(session, keyword, client_id, client_secret, display=100, start=1):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": display,
        "start": start,
        "sort": "date"
    }
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error Code: {response.status}")
            return None

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def parse_article(html, url, category_mapping):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 분야 추출
    category_tag = soup.select_one('em.media_end_categorize_item')
    category = category_tag.get_text().strip() if category_tag else '기타'
    
    # 카테고리 영어로 변환
    category_en = category_mapping.get(category, 'Others')
    
    # 제목 추출
    title_tag = soup.select_one('h3#articleTitle') or soup.select_one('h2.media_end_head_headline')
    title = title_tag.get_text().strip() if title_tag else '제목 없음'
    
    # 작성자 추출
    author_tag = soup.select_one('.byline_s') or soup.select_one('.journalistcard_summary_name') or soup.select_one('.press_logo img')
    author = author_tag.get_text().strip() if author_tag else '작성자 없음'
    
    # 이미지 추출
    image_url = '이미지 없음'
    end_photo_div = soup.select_one('span.end_photo_org')
    if end_photo_div:
        image_tag = end_photo_div.find('img', class_='_LAZY_LOADING _LAZY_LOADING_INIT_HIDE')
        if image_tag:
            image_url = image_tag.get('data-src') or image_tag.get('src', '이미지 없음')
    else:
        vod_player_wrap = soup.select_one('div._VOD_PLAYER_WRAP')
        if vod_player_wrap:
            image_url = vod_player_wrap.get('data-cover-image-url', '이미지 없음')

    
    # 본문 추출
    content_tag = soup.select_one('#articleBodyContents') or soup.select_one('.go_trans._article_content') or soup.select_one('.news_end_content')
    if content_tag:
        # 불필요한 태그 제거
        for tag in content_tag.find_all(['script', 'style']):
            tag.decompose()
        content = ' '.join(content_tag.get_text().split()).strip()
    else:
        content = '본문 없음'

    # 발행일 추출
    published_at_tag = soup.select_one('.t11') or soup.select_one('.media_end_head_info_datestamp_time')
    published_at = published_at_tag.get_text().strip() if published_at_tag else '발행일 없음'
    
    try:
        # 발행일을 표준 형식으로 변환 시도
        published_at = datetime.strptime(published_at, "%Y.%m.%d. %H:%M").isoformat()
    except ValueError:
        pass  # 변환 실패 시 원래 문자열 유지

    return {
        'category': category_en,
        'author': author,
        'title': title,
        'content': content,
        'url': url,
        'urlToImage': image_url,
        'publishedAt': published_at
    }

async def main(client_id, client_secret, db, keyword, total_results, interval):
    async with aiohttp.ClientSession() as session:
        category_mapping = {
            '경제': 'Economy',
            '사회': 'Society',
            '생활': 'Lifestyle',
            '세계': 'World',
            '오피니언': 'Opinion',
            '정치': 'Politics',
            'IT': 'IT',
            '기타': 'Others'
        }   
        seen_urls = set()
        seen_authors = set()
        
        while True:
            all_articles = []
            start = 1

            # 원하는 기사 수를 얻을 때까지 반복하여 검색 결과 가져오기
            while len(all_articles) < total_results * 2:
                initial_result = await search_naver_news(session, keyword, client_id, client_secret, display=100, start=start)

                if initial_result and 'items' in initial_result:
                    all_articles.extend(initial_result['items'])
                    start += 100
                    if len(initial_result['items']) < 100:
                        break
                else:
                    break

            if len(all_articles) < total_results:
                print(f"원하는 기사 수: {total_results}개, 추출된 기사 수: {len(all_articles)}개")
                print("검색된 기사가 부족합니다.")

            valid_articles = []

            for article in all_articles:
                if "news.naver.com" in article['link'] and article['link'] not in seen_urls:
                    seen_urls.add(article['link'])
                    html = await fetch(session, article['link'])
                    parsed_article = parse_article(html, article['link'], category_mapping)
                    if parsed_article['author'] not in seen_authors:
                        seen_authors.add(parsed_article['author'])
                        valid_articles.append(parsed_article)
                        if len(valid_articles) >= total_results:
                            break

            # MongoDB에 데이터 저장
            for article in valid_articles:
                collection_name = article['category']
                collection = db[collection_name]
                await collection.insert_one(article)

            # 콘솔에 출력
            for article in valid_articles:
                print(f"Category: {article['category']}")
                print(f"Author: {article['author']}")
                print(f"Title: {article['title']}")
                print(f"Content: {article['content']}")
                print(f"URL: {article['url']}")
                print(f"URL to Image: {article['urlToImage']}")
                print(f"Published At: {article['publishedAt']}\n")

            # 각 카테고리별 문서 수 출력
            for category in category_mapping.values():
                collection = db[category]
                count = await collection.count_documents({})
                print(f"{category} category documents count: {count}")

            # 7분 간격 대기
            await asyncio.sleep(interval)

if __name__ == "__main__":
    client_id = "aEIaskenkMe8Rgib2U3M"
    client_secret = "uEsEVcfCNH"
    keyword = "뉴스"
    total_results = 100
    interval = 420  # 7분 간격

    mongo_uri = "mongodb+srv://theBuleocean:opensource418@newssun.ts97rhi.mongodb.net/?retryWrites=true&w=majority"
    client = AsyncIOMotorClient(mongo_uri)
    db = client['news_database']

    asyncio.run(main(client_id, client_secret, db, keyword, total_results, interval))
