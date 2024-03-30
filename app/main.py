from fastapi import FastAPI
from app.routers import items, test


app = FastAPI()

# itmes router
app.include_router(items.router)

# test router 
app.include_router(test.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}