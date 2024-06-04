import requests

def fetch_news():
    api_key = "ed9def0329da4d16b237507a98905ba8"
    country="kr"
    category="business"
    page_size=10

    # NewsAPI의 엔드포인트 URL
    url = "https://newsapi.org/v2/top-headlines"

    # 요청 파라미터
    params = {
        "apiKey": api_key,
        "country": country,
        "category": category,
        "pageSize": page_size,
    }

    # API 요청 보내기
    response = requests.get(url, params=params)

    # JSON 형식으로 응답 가져오기
    news_data = response.json()

    parsed_news = []
    for article in news_data.get("articles", []):
        parsed_article = {
            "name": article.get("source", {}).get("name"),
            "author": article.get("author"),
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "urltoimage": article.get("urlToImage"),
            "publishedAt": article.get("publishedAt")
        }
        parsed_news.append(parsed_article)

    return parsed_news


