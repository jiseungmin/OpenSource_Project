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

    # 요청 데이터
    data = {
        "content": request.content
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        response_data = response.json()
        
        # 감정 분석 결과를 JSON 응답에서 가져오기
        if 'document' in response_data and 'sentiment' in response_data['document']:
            sentiment = response_data['document']['sentiment']
            print(sentiment)
            return {"sentiment": sentiment}
        else:
            raise HTTPException(status_code=500, detail="Invalid response structure")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

