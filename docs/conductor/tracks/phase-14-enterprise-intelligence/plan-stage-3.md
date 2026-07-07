# Phase 14 — Giai đoạn 3: Automated Onboarding Doc Generator
## Implementation Plan

> **Spec**: `docs/conductor/tracks/phase-14-enterprise-intelligence/spec.md` §3.3
> **Branch**: `feat/phase-14-doc-generator`
> **Estimated**: 3-4 ngày

---

## Audit Trạng Thái Hiện Tại (As-Is)

Sau khi đọc codebase, các thành phần sau đã có sẵn và sẽ được tái sử dụng:

| Hạng mục | Trạng thái | File |
|---|---|---|
| SSE streaming infrastructure | ✅ Đã có | `apps/api/src/routers/reason.py` — `/reason/stream` |
| SSE consumer pattern ở Frontend | ✅ Đã có | `apps/dashboard/src/components/chat/ChatBox.tsx` |
| Reasoning Service (LangGraph orchestrator) | ✅ Đã có | `packages/reasoning-engine/src/reasoning_engine/services/` |
| Graph stats query (hotspots, nodes by label) | ✅ Đã có | `apps/api/src/routers/stats.py` |
| Graph nodes/edges query | ✅ Đã có | `apps/api/src/routers/graph.py` |
| `react-markdown` / Markdown render | ❌ Chưa có | Cần cài thêm dependency |
| `POST /docs/generate` endpoint | ❌ Chưa có | Cần tạo mới `apps/api/src/routers/docs.py` |
| Context assembly từ Knowledge Graph | ❌ Chưa có | Logic mới trong `docs.py` |
| `DocGenerator.tsx` component | ❌ Chưa có | Cần tạo mới |
| Trang `/docs` | ❌ Chưa có | Cần tạo mới |
| Link sidebar `/docs` | ❌ Chưa có | Cần update `Sidebar.tsx` |

---

## Tasks (To-Do List)

### Task 3.1 — Backend: Context Assembler (Knowledge Graph → Prompt Context)

**File**: `apps/api/src/routers/docs.py` [NEW]

Đây là phần phức tạp nhất. Trước khi gọi LLM, backend phải thu thập **context có cấu trúc** từ Knowledge Graph để đưa vào prompt. Nếu không grounding theo graph thực tế, LLM sẽ hallucinate.

**Context queries cần thực hiện:**

| Loại tài liệu | Context cần thu thập từ Neo4j |
|---|---|
| `architecture_overview` | Top 15 files/modules có nhiều edge nhất, toàn bộ edge CONTAINS/DEFINES, các label node và count |
| `onboarding_guide` | Top 5 entry points (fan-in cao nhất), top 10 files quan trọng, toàn bộ edge giữa top nodes |
| `key_entry_points` | Top 10 nodes có incoming edges nhiều nhất (high fan-in) |
| `module_dependencies` | Toàn bộ DEFINES/CONTAINS edges giữa File nodes — dùng làm Mermaid diagram |

**Hàm `_assemble_context(doc_type, graph_manager) → str`:**
```python
# Pseudo-code:
async def _assemble_context(doc_type, driver):
    nodes_by_label = query_label_counts()
    hotspots = query_top_nodes_by_connections(limit=10)
    
    if doc_type == "architecture_overview":
        edges = query_top_file_edges(limit=50)
        return format_as_structured_text(nodes_by_label, hotspots, edges)
    
    elif doc_type == "onboarding_guide":
        entry_points = query_high_fan_in_nodes(limit=5)
        return format_entry_points_context(entry_points, hotspots)
    
    elif doc_type == "module_dependencies":
        file_edges = query_file_to_file_edges(limit=100)
        return format_as_mermaid_input(file_edges)
```

---

### Task 3.2 — Backend: Prompt Templates

**File**: `apps/api/src/routers/docs.py` [trong cùng file]

Thiết kế prompt cho từng loại tài liệu, được grounded chặt chẽ với context từ graph:

```python
PROMPT_TEMPLATES = {
    "architecture_overview": """
You are a senior software architect. Based on the actual codebase analysis below,
write a concise Architecture Overview document in Markdown.

## Codebase Statistics:
{context}

Instructions:
- Describe the main layers/modules you can infer from the node types and counts.
- Identify 3-5 key architectural patterns visible in the data.
- DO NOT invent information not present in the statistics above.
- Output ONLY valid Markdown, starting with # Architecture Overview.
""",

    "onboarding_guide": """
You are a senior developer writing a Getting Started guide for a new team member.
Based on the actual codebase data below, write a practical Onboarding Guide in Markdown.

## Codebase Analysis:
{context}

Instructions:
- Identify the most important entry points and explain what they do.
- Suggest a reading order for understanding the codebase.
- Highlight any critical files with high connectivity.
- Output ONLY valid Markdown, starting with # Developer Onboarding Guide.
""",

    "key_entry_points": """
You are documenting the entry points of a software project.
Based on the codebase metrics below, list and explain the key entry points.

## Entry Point Analysis:
{context}

Instructions:
- List each entry point with its purpose inferred from its name and connectivity.
- Explain why each is important (high fan-in = many dependents).
- Output ONLY valid Markdown, starting with # Key Entry Points.
""",

    "module_dependencies": """
You are creating a Module Dependencies document.
Based on the relationship data below, write a dependencies overview with a Mermaid diagram.

## Dependency Data:
{context}

Instructions:
- Generate a Mermaid `graph TD` diagram showing the top module dependencies.
- Add a brief explanation of the dependency structure.
- Output ONLY valid Markdown with a valid ```mermaid code block.
""",
}
```

---

### Task 3.3 — Backend: `POST /docs/generate` Streaming Endpoint

**File**: `apps/api/src/routers/docs.py` [NEW]
**File**: `apps/api/src/main.py` [MODIFY — include docs router]

**Request schema:**
```python
class DocGenerateRequest(BaseModel):
    doc_type: Literal[
        "architecture_overview",
        "onboarding_guide",
        "key_entry_points",
        "module_dependencies",
    ]
    session_id: str = "doc-gen"
```

**Endpoint logic (SSE streaming — tái dụng pattern của `/reason/stream`):**
```python
@router.post("/generate")
async def generate_doc(request, graph_manager, reasoning_service):
    async def sse_generator():
        yield sse_event("status", "Assembling context from Knowledge Graph...")
        context = await _assemble_context(request.doc_type, graph_manager.driver)
        
        yield sse_event("status", "Generating document with AI...")
        prompt = PROMPT_TEMPLATES[request.doc_type].format(context=context)
        
        # Reuse reasoning_service.stream_process_query với custom query
        reasoning_request = ReasoningRequest(query=prompt, session_id=request.session_id)
        async for chunk in reasoning_service.stream_process_query(reasoning_request):
            yield sse_event_from_chunk(chunk)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(sse_generator(), media_type="text/event-stream")
```

> **Note quan trọng**: Tái dụng `reasoning_service` (LangGraph orchestrator) — không tạo LLM call mới. Prompt được inject vào làm `query` trong `ReasoningRequest`. Điều này đảm bảo context từ graph được grounded trước khi LLM generate.

---

### Task 3.4 — Frontend: Cài đặt `react-markdown`

```bash
npm install react-markdown remark-gfm
```

> **`remark-gfm`** cần thiết để render bảng, code blocks, và Mermaid syntax trong Markdown output của LLM.

---

### Task 3.5 — Frontend: Khai báo API types

**File**: `apps/dashboard/src/lib/api-types.ts` [MODIFY]

```typescript
export type DocType =
  | 'architecture_overview'
  | 'onboarding_guide'
  | 'key_entry_points'
  | 'module_dependencies';

export interface DocGenerateRequest {
  doc_type: DocType;
  session_id?: string;
}
```

> **Không cần RTK Query mutation** — Doc Generator dùng raw `fetch()` + `ReadableStream` giống ChatBox vì SSE không được native support trong RTK Query. Tái dụng pattern đã có.

---

### Task 3.6 — Frontend: `DocGenerator.tsx` Component

**File**: `apps/dashboard/src/components/docs/DocGenerator.tsx` [NEW]

**UI layout:**
```
┌─────────────────────────────────────────────────────┐
│ 📄 Document Generator                                │
│                                                      │
│  ┌─────────────────────────────┐  ┌──────────────┐  │
│  │ Select Document Type:       │  │ [Generate]   │  │
│  │ ○ Architecture Overview     │  │ [Download]   │  │
│  │ ○ Onboarding Guide         │  │ [Copy]       │  │
│  │ ○ Key Entry Points         │  └──────────────┘  │
│  │ ○ Module Dependencies      │                     │
│  └─────────────────────────────┘                     │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │ [Status: Assembling context...]                  │ │
│  │                                                  │ │
│  │ # Architecture Overview                          │ │
│  │ ## Core Modules                                  │ │
│  │ ...streaming Markdown content...                 │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**SSE consumer logic** — tái dụng trực tiếp từ `ChatBox.tsx`:
```typescript
const response = await fetch(`${API_URL}/docs/generate`, {
  method: 'POST',
  body: JSON.stringify({ doc_type: selectedType, session_id: 'doc-gen' }),
});
// ... reader loop giống ChatBox ...
// Khi nhận type === "message" → append content vào generatedDoc
// Khi nhận type === "status" → update statusText
// Khi nhận [DONE] → setIsGenerating(false)
```

**Render Markdown:**
```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {generatedDoc}
</ReactMarkdown>
```

**Download logic:**
```typescript
const handleDownload = () => {
  const blob = new Blob([generatedDoc], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${selectedType}-${Date.now()}.md`;
  a.click();
};
```

---

### Task 3.7 — Frontend: Trang `/docs`

**File**: `apps/dashboard/src/app/docs/page.tsx` [NEW]

Page đơn giản — chỉ wrap `DocGenerator.tsx` với store Provider (tương tự chat page):

```tsx
'use client';
import { DocGenerator } from '@/components/docs/DocGenerator';

export default function DocsPage() {
  return (
    <div className="h-full bg-zinc-950">
      <DocGenerator />
    </div>
  );
}
```

---

### Task 3.8 — Frontend: Update Navigation Sidebar

**File**: `apps/dashboard/src/components/layout/Sidebar.tsx` [MODIFY]

Thêm link `/docs` với icon `FileText` (từ `lucide-react`) vào navigation list.

---

### Task 3.9 — QA & Integration

**Checklist:**
- [ ] Chạy `uvx ruff format apps/api/src/routers/docs.py`.
- [ ] Chạy `uv run pytest apps/api/tests/ -v` — toàn bộ test suite pass.
- [ ] Chạy `npm run build` — exit code 0, không lỗi TypeScript.
- [ ] Manual test: Chọn "Architecture Overview" → Generate → thấy status "Assembling context..." → nội dung stream ra dần.
- [ ] Manual test: Nội dung Markdown render đúng (bold, headers, code blocks hiển thị).
- [ ] Manual test: Nút "Download .md" tải về file đúng tên và nội dung.
- [ ] Manual test: Nút "Copy" copy vào clipboard.

---

## Thứ Tự Thực Hiện

```
Day 1 (Backend):
  Task 3.1 → Task 3.2 → Task 3.3

Day 2 (Frontend):
  Task 3.4 (npm install) → Task 3.5 → Task 3.6

Day 3 (Frontend + QA):
  Task 3.7 → Task 3.8 → Task 3.9
```

---

## Files Sẽ Được Sửa Đổi

| File | Loại | Task |
|---|---|---|
| `apps/api/src/routers/docs.py` | [NEW] Context assembler + streaming endpoint | 3.1–3.3 |
| `apps/api/src/main.py` | [MODIFY] Include docs router | 3.3 |
| `apps/dashboard/src/lib/api-types.ts` | [MODIFY] Thêm DocType, DocGenerateRequest | 3.5 |
| `apps/dashboard/src/components/docs/DocGenerator.tsx` | [NEW] Main UI component | 3.6 |
| `apps/dashboard/src/app/docs/page.tsx` | [NEW] Route page | 3.7 |
| `apps/dashboard/src/components/layout/Sidebar.tsx` | [MODIFY] Thêm `/docs` link | 3.8 |

**Không sửa Reasoning Engine** — tái dụng nguyên xi `reasoning_service.stream_process_query()`.

---

## Acceptance Criteria (Giai đoạn 3)

- [ ] `POST /docs/generate` stream SSE response, content nhận được là Markdown hợp lệ.
- [ ] Nội dung **phản ánh đúng graph** (tên file/module thực tế trong codebase, không hallucinate).
- [ ] Generate Architecture Overview hoàn thành trong < 30 giây.
- [ ] Markdown render đẹp với header, code block, bảng.
- [ ] Download `.md` hoạt động.
- [ ] Copy to clipboard hoạt động.
- [ ] `npm run build` pass clean (exit code 0).
- [ ] Pytest toàn bộ suite pass.
