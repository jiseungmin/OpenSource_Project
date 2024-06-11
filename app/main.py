from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import news,sentiment

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처에서의 요청을 허용합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용합니다.
    allow_headers=["*"],  # 모든 헤더를 허용합니다.
)
# news router 
app.include_router(news.router)

app.include_router(sentiment.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}