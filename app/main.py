from fastapi import FastAPI
from app.routers import news,sentiment

app = FastAPI()

# news router 
app.include_router(news.router)

app.include_router(sentiment.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}