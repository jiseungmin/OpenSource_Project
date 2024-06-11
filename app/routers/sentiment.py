import os
import sys
import json
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

# .env 파일 로드
load_dotenv()

router = APIRouter()

class SentimentRequest(BaseModel):
    content: str

def analyze_sentiment(content: str, headers: dict, api_url: str) -> str:
    data = {"content": content}
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
        response_data = response.json()
        
        if 'document' in response_data and 'sentiment' in response_data['document']:
            return response_data['document']['sentiment']
        else:
            raise HTTPException(status_code=500, detail="Invalid response structure")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

@router.post("/sentiment")
def collectnews(request: SentimentRequest):

    # 출력 인코딩 설정
    sys.stdout.reconfigure(encoding='utf-8')

    # 네이버 클로바 감정 분석 API 정보
    api_url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="API credentials are not set")

    # 헤더 설정
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }

    content = request.content
    try:
        # 첫 번째 시도
        sentiment = analyze_sentiment(content, headers, api_url)
        return {"sentiment": sentiment}
    except HTTPException as e:
            # 글을 반으로 나눔
            mid = len(content) // 2
            first_half = content[:mid]
            second_half = content[mid:]

            # 각각의 반에 대해 감정 분석 수행
            first_sentiment = analyze_sentiment(first_half, headers, api_url)
            second_sentiment = analyze_sentiment(second_half, headers, api_url)

            # 두 개의 결과를 결합하여 최종 감정 상태를 결정
            if first_sentiment == second_sentiment:
                return {"sentiment": first_sentiment}
            else:
                return {"sentiment": "neutral"}

