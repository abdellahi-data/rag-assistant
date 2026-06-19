# http api over the rag pipeline. run: uvicorn api:app --reload
# endpoints: POST /ask (question in, answer + sources out), GET /health (liveness check)
from fastapi import FastAPI
from pydantic import BaseModel

from rag import RagPipeline

app = FastAPI(title="RAG Assistant")

# build the pipeline once at startup, reused across requests
pipe = RagPipeline()


# request/response shapes (pydantic validates and documents them)
class AskRequest(BaseModel):
    question: str


class Source(BaseModel):
    source: str
    page: int


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    # simple liveness check; aws load balancers / ecs ping this
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    answer, chunks = pipe.answer(req.question)
    # dedupe sources by (file, page) so we don't repeat the same page
    seen = {}
    for c in chunks:
        seen[(c.source, c.page)] = Source(source=c.source, page=c.page)
    return AskResponse(answer=answer, sources=list(seen.values()))

