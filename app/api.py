from __future__ import annotations

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from rag.embedding import GeminiEmbedder
from rag.retriever import Retriever
from rag.context_builder import ContextBuilder
from rag.generator import Generator
from rag.citation import CitationMapper
from rag.token_manager import TokenManager
from app.service.rebuild import rebuild_rag_database
from app.service.ingest import save_upload_file

from pathlib import Path


app = FastAPI(title="DocRAG API", version="1.0.0")

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw" / "document" / "pdf"


# Request/Response Models
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    citations: list[str] = []


class UploadResponse(BaseModel):
    status: str
    message: str
    file: str


class RebuildResponse(BaseModel):
    message: str
    status: str
    files: int = 0
    chunks: int = 0


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


@app.post("/upload-document", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...)):
    """Chỉ lưu file PDF vào thư mục server (không chunk, không embed, không populate)"""
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400, 
                detail="Chỉ chấp nhận file PDF"
            )
        
        saved_path = save_upload_file(file, DATA_DIR)
        
        return UploadResponse(
            status="success",
            message="File đã được lưu. Gọi /populate-db để xử lý.",
            file=saved_path.name,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi upload: {str(e)}"
        )


@app.post("/populate-db", response_model=RebuildResponse)
def populate_db():
    """Đọc toàn bộ file trong thư mục, chunk, embed, build lại DB"""
    try:
        result = rebuild_rag_database()
        return RebuildResponse(
            message=result.get("message", "Populate DB thành công"),
            status=result.get("status", "success"),
            files=result.get("files", 0),
            chunks=result.get("chunks", 0),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi populate: {str(e)}"
        )