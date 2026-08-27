from fastapi import FastAPI
from pydantic import BaseModel
from ingest import query

app = FastAPI()

class Q(BaseModel):
    q: str
    k: int = 5

@app.post("/query")
def q(p: Q):
    pts = query(p.q, top_k=p.k)
    return {"hits": [{"path": pt.payload["path"], "text": pt.payload["text"], "score": pt.score} for pt in pts]}

@app.get("/health")
def h():
    return {"ok": True}
