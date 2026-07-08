# Phase 15: Evaluation, Telemetry & RAG Fine-Tuning

## 1. Context & Objective
Currently, AIEKP retrieves context from Neo4j and Qdrant to generate answers via the Reasoning Engine. However, there is no automated way to measure the accuracy of these answers, the latency of the retrieval pipelines, or token consumption. 
Furthermore, continuous improvement requires a feedback loop where users can rate AI responses, which can then be exported as datasets for fine-tuning.

**Mục tiêu (Objectives):**
1. **Telemetry & Observability:** Track every AI reasoning request (latency, tokens, steps) using standard tracing patterns.
2. **User Feedback Loop:** Allow users to rate answers on the UI and persist this feedback.
3. **Automated RAG Evaluation:** Integrate a framework (like `ragas` or `trulens`) to programmatically calculate precision, recall, and faithfulness of the RAG pipeline.
4. **Data Export:** Export high-quality interactions into JSONL for future LLM fine-tuning.

---

## 2. Core Features & Requirements

### 2.1. Telemetry & Tracing (Backend)
- **Trace ID Injection:** Every request to `POST /reason` or `POST /reason/stream` will generate a unique `trace_id`.
- **Instrumentation:** Trace sub-steps such as:
  1. Intent Analysis
  2. Context Retrieval (Neo4j, Qdrant)
  3. Response Generation (LLM)
- **Storage Strategy (Hybrid):** 
  - **Mặc định:** Sử dụng một SQLite Database (`telemetry.db`) nội bộ để lưu trữ Traces và Feedback. Đảm bảo nhẹ, nhanh và private.
  - **Mở rộng (Future-proof):** Để lại kiến trúc adapter (OpenTelemetry/Langchain Callbacks) để có thể chuyển sang kết nối trực tiếp với **Langfuse** hoặc **Phoenix** trong tương lai (thông qua biến môi trường `LANGFUSE_PUBLIC_KEY`).

### 2.2. User Feedback System
- **API Endpoint:** `POST /feedback` 
  - Payload: `{ "trace_id": "uuid", "score": 1, "comment": "Tốt" }` (Score là 1/-1).
  - Backend sẽ ghi nhận vào bảng `feedbacks` trong `telemetry.db`.
- **Frontend Integration:** 
  - AI Chat Message component cần hiển thị nút Thumbs Up / Thumbs Down.
  - Khi click, gọi API `/feedback` kèm theo `trace_id` của message đó (trace_id được trả về từ SSE stream lúc sinh câu trả lời).

### 2.3. RAG Evaluation CLI
- **Framework:** `ragas` (Retrieval Augmented Generation Assessment).
- **Test Suite:** Tạo một file `eval_dataset.json` chứa các câu hỏi mẫu (Question) và câu trả lời chuẩn (Ground Truth).
- **CLI Command:** Bổ sung command `aiekp eval run --dataset eval_dataset.json` vào CLI của AIEKP.
- **Output:** Tính toán 4 chỉ số chính:
  - *Context Precision / Recall* (Chất lượng truy xuất từ Vector/Graph DB).
  - *Faithfulness* (Answer không bịa đặt, dựa hoàn toàn vào context).
  - *Answer Relevancy* (Trả lời đúng trọng tâm câu hỏi).

### 2.4. Data Export cho Fine-Tuning
- **CLI Command:** Bổ sung command `aiekp eval export --min-score 1 --output dataset.jsonl`.
- Trích xuất các logs có điểm feedback tích cực từ DB `telemetry.db` ra định dạng JSONL (chuẩn OpenAI Chat format) để sẵn sàng fine-tune LLM hoặc Embedding models sau này.

---

## 3. Architecture Design

### Backend Changes (`apps/api`)
- **Telemetry Package:** Bổ sung module `src.telemetry` (hoặc `packages/telemetry`) chứa các logic:
  - SQLite Database setup (SQLAlchemy).
  - Tracing Decorators/Callbacks (cho LangChain/LLM calls).
- **Feedback Endpoint:** Thêm file `routers/feedback.py`.
- **Reasoning Update:** `routers/reason.py` và `ReasoningService` phải sinh ra `trace_id` từ đầu, gắn vào SSE response và log lại quá trình chạy.

### Frontend Changes (`apps/web`)
- **Chat State:** Cập nhật model `Message` trong store để nhận trường `trace_id`.
- **UI Components:** `ChatMessage.tsx` có thêm 2 nút Thumbs Up/Down (chỉ hiện khi là AI Message và đã render xong).
- **API Call:** Hàm `sendFeedback(traceId, score, comment)` bằng RTK Query hoặc fetch.

### CLI Changes (`apps/cli`)
- **Commands:** Tạo file `aiekp/cli/commands/eval.py` bằng `typer` chứa subcommands:
  - `aiekp eval run`
  - `aiekp eval export`

---

## 4. Implementation Stages

### Giai đoạn 1: Telemetry & Tracing Backend (3-4 ngày)
- Setup SQLAlchemy + SQLite cho `telemetry.db`.
- Viết `TelemetryCallbackHandler` (hoặc middleware) để ghi log các bước (Retrieval, Generation) kèm `trace_id`.
- Cập nhật `POST /reason/stream` để trả về `trace_id` ngay dòng đầu tiên hoặc chunk cuối cùng.

### Giai đoạn 2: User Feedback API & Frontend (2-3 ngày)
- Viết API `POST /feedback` insert vào DB.
- Viết UI Thumbs Up/Down trên `ChatMessage.tsx` ở Next.js Dashboard.
- Gọi API khi người dùng click (xử lý state đã vote).

### Giai đoạn 3: RAG Evaluation & Fine-Tuning CLI (3-4 ngày)
- Add `ragas` (hoặc logic tương tự) vào `packages/reasoning-engine` hoặc `apps/cli`.
- Viết lệnh CLI `aiekp eval run` để chạy bộ test tự động.
- Viết lệnh CLI `aiekp eval export` truy xuất bảng `traces` & `feedbacks` ra `.jsonl`.
- Viết Unit Tests cho các lệnh này.

### Giai đoạn 4: Integration & QA (1-2 ngày)
- Test toàn bộ luồng: Hỏi đáp trên web -> nhận trace_id -> rate thumbs up -> chạy CLI export ra jsonl thành công.
- Cập nhật tài liệu và chuẩn bị Release.
