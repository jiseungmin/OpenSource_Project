import requests
import json

def search_naver_news(keyword, client_id, client_secret, display=100, start=1000):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query":keyword,  # 빈 검색어로 모든 뉴스 검색
        "display": display,
        "start": start,
        "sort": "date"  # or "sim" for similarity
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error Code: {response.status_code}")
        return None

# Example usage
client_id = "aEIaskenkMe8Rgib2U3M"  # Replace with your actual Client ID
client_secret = "uEsEVcfCNH"  # Replace with your actual Client Secret
keyword = "뉴스"

result = search_naver_news(keyword, client_id, client_secret)

if result:
    for i, item in enumerate(result['items'], 1):
        print(f"{i}. {item['title']} - {item['pubDate']}")
        print(f"   Link: {item['link']}")
        print(f"   Description: {item['description']}\n")
        print(f"   pubDate: {item['pubDate']}\n")
        
        
