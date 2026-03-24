from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag.embedding import GeminiEmbedder
from rag.retriever import Retriever
from rag.context_builder import ContextBuilder
from rag.generator import Generator
from rag.citation import CitationMapper
from rag.token_manager import TokenManager
from populate_db import main as rebuild_rag_db


app = FastAPI(title="DocRAG API", version="1.0.0")


# Câu hỏi của user
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    citations: list[str] = []

class RebuildResponse(BaseModel):
    message: str
    status: str


def build_citation_list(metadatas: list[dict]) -> list[str]:
    results = []
    for meta in metadatas:
        source = meta.get("source", "unknown")
        page = meta.get("page", "N/A")
        section = meta.get("raw_section_heading") or meta.get("section_heading") or ""
        item = f"{source}, trang {page}"
        if section:
            item += f", section={section}"
        results.append(item)
    return results


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    try:
        embedder = GeminiEmbedder()
        retriever = Retriever()
        context_builder = ContextBuilder()
        generator = Generator()
        token_manager = TokenManager()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"init error: {e}")

    try:
        query_embedding = embedder.embed_text(question)
        if not query_embedding:
            raise ValueError("empty embedding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"embedding error: {e}")

    try:
        retrieved_docs = retriever.retrieve(query_embedding, k=8)
        documents = retrieved_docs.get("documents", [[]])[0]
        metadatas = retrieved_docs.get("metadatas", [[]])[0]

        if not documents:
            return AskResponse(
                question=question,
                answer="Không tìm thấy thông tin liên quan trong tài liệu.",
                model="N/A",
                citations=[],
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"retrieve error: {e}")

    try:
        context = context_builder.build(retrieved_docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"context build error: {e}")

    try:
        selected_model, _ = token_manager.select_model(question)
        generated_response, token_info = generator.generate(
            query=question,
            context=context,
            model_name=selected_model,
        )
        raw_answer = generated_response.get(
            "answer",
            "Xin lỗi, tôi không thể tạo câu trả lời.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"generation error: {e}")

    try:
        mapper = CitationMapper(metadatas)
        final_answer = mapper.replace(raw_answer)
        citations = build_citation_list(metadatas)
    except Exception:
        final_answer = raw_answer
        citations = []

    return AskResponse(
        question=question,
        answer=final_answer,
        model=selected_model,
        citations=citations,
    )


@app.post("/rebuild-rag", response_model=RebuildResponse)
def rebuild_rag():
    try:
        rebuild_rag_db()
        return RebuildResponse(
            message="Đã chạy lại populate DB thành công.",
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"rebuild error: {e}")