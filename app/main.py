from fastapi import FastAPI
from app.routers import news

app = FastAPI()

# news router 
app.include_router(news.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}