from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import law_graph

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "RAG 서버 실행 성공!"}

@app.post("/chat")
def chat(request: QuestionRequest):
    result = law_graph.invoke({
        "question": request.question
    })

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }