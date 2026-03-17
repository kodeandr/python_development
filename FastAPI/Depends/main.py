from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/messages")
async def all_messages(limit: int = 10, page: int = 1):
    return {"messages": [{'limit': limit, 'page': page}]}

@app.get("/comments")
async def all_comments(limit: int = 10, page: int = 1):
    return {"comments": [{'limit': limit, 'page': page}]}pip install fastapi uvicorn