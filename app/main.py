from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.search_service import search_products
from services.chat_service import chat_with_openai, get_db

app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.get("/search")
async def search(query: str, filters: str = None):
    try:
        return await search_products(query, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        return await chat_with_openai(request.dict(), db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
