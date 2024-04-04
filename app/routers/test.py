import requests
import json

def fetch_news(api_key, country="kr", category="business", page_size=100):
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

    return news_data

def save_news_to_file(news_data, file_name="top_news_kr.json"):
    # 뉴스 데이터를 JSON 파일로 저장
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)

# 여기에 당신의 NewsAPI의 API 키를 입력해주세요
api_key = "ed9def0329da4d16b237507a98905ba8"

# 뉴스 데이터 가져오기
news_data = fetch_news(api_key)

# 뉴스 데이터를 파일에 저장
save_news_to_file(news_data)

print("뉴스 데이터를 파일에 저장했습니다.")
