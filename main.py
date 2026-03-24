from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from rag.embedding import GeminiEmbedder
from rag.retriever import Retriever
from rag.context_builder import ContextBuilder
from rag.generator import Generator
from rag.citation import CitationMapper
from rag.token_manager import TokenManager


def main() -> None:

    try:
        embedder = GeminiEmbedder()
        retriever = Retriever()
        context_builder = ContextBuilder()
        generator = Generator()
        token_manager = TokenManager()
    except Exception as e:
        if "does not exist" in str(e):
            print("\n[LỖI] Collection 'rag_documents' chưa tồn tại.")
            print(">>> Chạy lại populate_db.py")
        else:
            print(f"[INIT ERROR] {e}")
        return

    print("--- RAG Chatbot sẵn sàng | 'Ctrl + c' để thoát ---")

    while True:
        query = input("\nHãy đặt câu hỏi cho tôi tại đây: ").strip()

        if query.lower() in ["quit", "exit"]:
            print("Pái Paiiiii!")
            break

        if not query:
            continue

        print("Đang xử lý...")

        try:
            query_embedding = embedder.embed_text(query)
            if not query_embedding or sum(query_embedding) == 0:
                raise ValueError("Embedding không hợp lệ")
        except Exception as e:
            print(f"Lỗi embedding: {e}")
            continue

        try:
            retrieved_docs = retriever.retrieve(query_embedding, k=8)
            documents = retrieved_docs.get("documents")

            if not documents or not documents[0]:
                print("AI: Không tìm thấy thông tin liên quan.")
                continue
        except Exception as e:
            print(f"Lỗi Retrieve: {e}")
            continue

        try:
            context = context_builder.build(retrieved_docs)
        except Exception as e:
            print(f"Lỗi Context build: {e}")
            continue

        selected_model, selection_reason = token_manager.select_model(query)
        print(f"[Model Selection] {selection_reason}")

        try:
            generated_response, token_info = generator.generate(
                query,
                context,
                model_name=selected_model,
            )
            raw_answer = generated_response.get(
                "answer",
                "Xin lỗi, tôi không thể tạo câu trả lời.",
            )
        except Exception as e:
            print(f"Lỗi Generate: {e}")
            continue

        try:
            metadatas = retrieved_docs.get("metadatas", [[]])[0]
            mapper = CitationMapper(metadatas)
            final_answer = mapper.replace(raw_answer)
        except Exception as e:
            print(f"Lỗi Citation mapping: {e}")
            final_answer = raw_answer
            mapper = None

        print("\nAI:\n", final_answer)

        if mapper:
            try:
                mapper.print_citations()
            except Exception:
                pass

        if token_info and token_info.get("total_tokens", 0) > 0:
            query_log = token_manager.log_query(
                query=query,
                model_used=token_info.get("model", selected_model),
                prompt_tokens=token_info.get("prompt_tokens", 0),
                output_tokens=token_info.get("response_tokens", 0),
                answer_preview=raw_answer,
            )

            print("-" * 50)
            print(f"[Token Usage] Model: {query_log['model']}")
            print(
                f"  Prompt: {query_log['prompt_tokens']:,} | "
                f"Output: {query_log['output_tokens']:,} | "
                f"Total: {query_log['total_tokens']:,}"
            )
            print(f"  Cost: ${query_log['cost_usd']:.6f}")
            print(f"  Session Cost: ${token_manager.session_stats['total_cost']:.6f}")
            print("-" * 50)
        else:
            print("[Token Info] Could not retrieve token usage from API")

    token_manager.print_session_summary()
    try:
        token_manager.save_session_log()
    except Exception as e:
        print(f"[Warning] Could not save session log: {e}")


if __name__ == "__main__":
    main()