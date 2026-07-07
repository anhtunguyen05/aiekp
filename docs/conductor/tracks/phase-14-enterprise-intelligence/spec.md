# Phase 14: Enterprise Intelligence Features

> **Context**: Read `docs/conductor/product.md` và `tracks/phase-13-web-dashboard/spec.md` trước khi triển khai.
> **Principle**: Context precedes code. Spec này định nghĩa WHAT và WHY trước HOW.
> **Prerequisite**: Phase 13 (Web Dashboard) phải hoàn thành. ✅ Done (Tag: v0.1.2)

---

## 1. Objective

Phase 14 biến AIEKP từ một công cụ *xem* Knowledge Graph thành một công cụ *thông minh hóa* codebase — có khả năng tự động phân tích rủi ro, phát hiện vi phạm kiến trúc, và tạo tài liệu kỹ thuật mà không cần developer viết thủ công.

Ba tính năng "killer":

1. **Impact Analysis Engine** — Phân tích ảnh hưởng khi một node thay đổi, visualized trực tiếp trên Knowledge Graph.
2. **Architectural Rule Engine** — Định nghĩa và enforce các quy tắc kiến trúc tùy chỉnh (custom rules) trên Knowledge Graph.
3. **Automated Onboarding Doc Generator** — AI tự tạo tài liệu onboarding từ codebase context hiện tại.

> **Mục tiêu cốt lõi:** Trong 30 giây, một Tech Lead có thể trả lời "Nếu tôi đổi hàm X, cái gì sẽ bị ảnh hưởng?" mà không cần đọc code.

---

## 2. Target Users

| Người dùng | Nhu cầu | Tính năng Phase 14 |
|---|---|---|
| **Tech Lead / Architect** | Hiểu ripple effect của thay đổi | Impact Analysis + Graph highlight |
| **Engineering Manager** | Phát hiện technical debt / vi phạm quy tắc | Architectural Rule Engine |
| **Developer mới (Onboarding)** | Hiểu nhanh codebase lạ | Automated Onboarding Doc |
| **Code Reviewer** | Kiểm tra impact của PR | Impact Analysis export |

---

## 3. Core Features

### 3.1. Impact Analysis Engine

Từ một Node đang được chọn trên graph, tự động tìm toàn bộ các Node bị ảnh hưởng nếu Node đó thay đổi.

**Backend — `GET /graph/impact/{node_id}`:**
- Traversal BFS/DFS theo các relationship types: `CALLS`, `IMPORTS`, `INHERITS`, `USES`.
- Trả về danh sách affected nodes chia theo cấp: `direct` (cách 1 hop) và `indirect` (2+ hops).
- Có thể lọc theo relationship type và max depth.
- Response format:
```json
{
  "source_node": { "id": "...", "name": "...", "type": "Function" },
  "affected": {
    "direct": [{ "id": "...", "name": "...", "type": "...", "relationship": "CALLS" }],
    "indirect": [...]
  },
  "total_count": 12
}
```

**Frontend — `ImpactAnalysisPanel.tsx`:**
- Nút "Analyze Impact" xuất hiện trong `NodeDetailPanel` khi chọn một node.
- Gọi API → highlight affected nodes bằng màu cam/đỏ trên graph (thêm Redux state `highlightedImpactIds`).
- Panel bên phải liệt kê affected nodes chia theo `direct` / `indirect`.
- Nút "Export as Markdown" tải về file báo cáo Impact Analysis.

**Acceptance Criteria:**
- [ ] Impact Analysis trả về kết quả trong vòng 3 giây cho graph ≤ 2000 nodes.
- [ ] Highlight đúng các affected nodes trên visual graph.
- [ ] Export Markdown có đủ thông tin: node gốc, danh sách affected, relationship path.

---

### 3.2. Architectural Rule Engine

Cho phép định nghĩa các quy tắc kiến trúc tùy chỉnh (custom rules) và tự động detect vi phạm trên Knowledge Graph hiện tại.

**Rule types (MVP):**
| Rule | Mô tả | Cypher pattern |
|---|---|---|
| `no-circular-deps` | Phát hiện vòng phụ thuộc (circular dependency) | `MATCH (a)-[*]->(a)` |
| `max-fan-in` | Hàm/file bị gọi bởi quá nhiều nơi (>N callers) | Đếm incoming CALLS edges |
| `max-fan-out` | Hàm/file gọi quá nhiều nơi khác (>N calls) | Đếm outgoing CALLS edges |
| `no-cross-layer` | Tầng UI không được import trực tiếp vào tầng DB | Path pattern giữa layer nodes |
| `max-complexity` | File có quá nhiều functions (>N) | Đếm CONTAINS edges |

**Backend — `POST /rules/check`:**
- Nhận list rule definitions, chạy tương ứng Cypher query trên Neo4j.
- Trả về danh sách violations kèm node_ids vi phạm.

**Frontend — `RuleEnginePage.tsx` (trang `/rules`):**
- Giao diện để chọn/bật/tắt rules, set threshold (N).
- Nút "Run Audit" → gọi API → highlight violation nodes bằng màu đỏ trên graph.
- Bảng liệt kê violations kèm đường link tới node vi phạm.

**Acceptance Criteria:**
- [ ] Ít nhất 3 rule types hoạt động đúng.
- [ ] Violations được highlight trên visual graph.
- [ ] Rule audit chạy xong trong 5 giây cho graph ≤ 2000 nodes.

---

### 3.3. Automated Onboarding Doc Generator

AI (Reasoning Engine) tự động tạo tài liệu onboarding dựa trên Knowledge Graph của codebase.

**Tài liệu được tạo tự động:**
1. **Architecture Overview** — Mô tả tổng quan kiến trúc: các layer chính, modules, luồng dữ liệu.
2. **Key Entry Points** — Danh sách các hàm/file quan trọng nhất (high fan-in).
3. **Module Dependencies Map** — Sơ đồ phụ thuộc dạng text/Mermaid diagram.
4. **Getting Started Guide** — Hướng dẫn "Bắt đầu từ đâu?" cho developer mới.

**Backend — `POST /docs/generate`:**
- Nhận `doc_type` (e.g., `architecture_overview`, `onboarding_guide`).
- Orchestrator lấy context từ Knowledge Graph (top nodes, key relationships).
- Gọi Reasoning Engine để generate text.
- Streaming response (SSE) để show progress.

**Frontend — `DocGeneratorPage.tsx` (trang `/docs`):**
- Dropdown chọn loại tài liệu cần tạo.
- Nút "Generate" → gọi API với streaming.
- Hiển thị kết quả dạng Markdown (render với `react-markdown`).
- Nút "Download .md" và "Copy to clipboard".

**Acceptance Criteria:**
- [ ] Generate Architecture Overview trong < 30 giây.
- [ ] Output là Markdown hợp lệ, có thể render đúng.
- [ ] Nội dung phản ánh đúng cấu trúc codebase đã scan (không hallucinate).

---

## 4. Architecture Design

### 4.1. Vị trí trong Monorepo

```
apps/
├── api/src/routers/
│   ├── graph.py            # [MODIFY] Thêm GET /graph/impact/{node_id}
│   ├── rules.py            # [NEW] POST /rules/check
│   └── docs.py             # [NEW] POST /docs/generate (streaming)
└── dashboard/src/
    ├── app/
    │   ├── rules/page.tsx  # [NEW] Architectural Rule Engine page
    │   └── docs/page.tsx   # [NEW] Doc Generator page
    └── components/
        ├── graph/
        │   └── ImpactAnalysisPanel.tsx  # [NEW]
        ├── rules/
        │   ├── RuleList.tsx             # [NEW]
        │   └── ViolationTable.tsx       # [NEW]
        └── docs/
            └── DocGenerator.tsx         # [NEW]
```

### 4.2. Technology Stack (bổ sung so với Phase 13)

| Layer | Công nghệ | Ghi chú |
|---|---|---|
| **Impact Traversal** | Neo4j Cypher (BFS/DFS via `shortestPath` và `apoc.path.subgraphAll`) | Cần APOC plugin hoặc pure Cypher fallback |
| **Rule Engine** | Custom Cypher templates per rule type | Không dùng library ngoài |
| **Doc Generation** | Reasoning Engine (LangGraph) hiện có | Tái dụng infrastructure Phase 7/11 |
| **Markdown Render** | `react-markdown` + `remark-gfm` | Thêm dependency mới |
| **Graph Highlight** | Redux `highlightedImpactIds` + React Flow node style | Extend graphSlice.ts |

### 4.3. API Contract

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/graph/impact/{node_id}` | GET | None | BFS impact traversal |
| `/graph/impact/{node_id}` | GET | None | Query params: `max_depth` (default: 3), `rel_types` |
| `/rules/check` | POST | x-api-key | Run architectural rules audit |
| `/docs/generate` | POST | None | Generate onboarding doc (streaming SSE) |

### 4.4. State Management (extend graphSlice)

```typescript
interface GraphState {
  // ... existing fields from Phase 13 ...
  highlightedImpactIds: string[];       // [NEW] Impact analysis affected nodes
  impactAnalysisSource: string | null;  // [NEW] Node đang được analyze
  violationNodeIds: string[];           // [NEW] Rule violations
}
```

---

## 5. Implementation Plan

### Giai đoạn 1: Impact Analysis Engine (4-5 ngày)

- [ ] **1.1** Viết Cypher query BFS traversal theo CALLS/IMPORTS/INHERITS/USES relationships.
- [ ] **1.2** Tạo `GET /graph/impact/{node_id}` endpoint trong `graph.py`, có param `max_depth` và `rel_types`.
- [ ] **1.3** Unit test: verify traversal đúng trên test graph (mock Neo4j hoặc test container).
- [ ] **1.4** Frontend: extend `graphSlice.ts` với `highlightedImpactIds`, `impactAnalysisSource`.
- [ ] **1.5** `ImpactAnalysisPanel.tsx`: nút "Analyze Impact" trong NodeDetailPanel, gọi API và highlight.
- [ ] **1.6** Panel list: chia direct/indirect, mỗi item clickable → zoom tới node.
- [ ] **1.7** "Export as Markdown" button: tạo và download file `impact-{node_name}.md`.

**Milestone 1:** Click một function → thấy tất cả callers/importers highlight đỏ trên graph trong < 3s.

### Giai đoạn 2: Architectural Rule Engine (3-4 ngày)

- [ ] **2.1** Thiết kế Rule Definition schema (JSON): `{ "type": "no-circular-deps", "threshold": null }`.
- [ ] **2.2** Implement Cypher template cho từng rule type (5 types MVP).
- [ ] **2.3** `POST /rules/check` endpoint: nhận list rules, chạy Cypher, trả violations.
- [ ] **2.4** Trang `/rules` với danh sách rules, toggle on/off, threshold input.
- [ ] **2.5** "Run Audit" → violations highlight trên graph (màu đỏ khác với impact orange).
- [ ] **2.6** `ViolationTable.tsx`: bảng violations, click → zoom tới node vi phạm.
- [ ] **2.7** Sidebar: thêm link `/rules` vào navigation.

**Milestone 2:** Detect circular dependency và highlight các file vi phạm trên graph.

### Giai đoạn 3: Automated Onboarding Doc Generator (4-5 ngày)

- [ ] **3.1** Thiết kế prompt templates cho từng loại tài liệu (architecture_overview, onboarding_guide).
- [ ] **3.2** Context assembly: query Knowledge Graph để lấy top nodes, key relationships, entry points.
- [ ] **3.3** `POST /docs/generate` endpoint với streaming SSE response.
- [ ] **3.4** Install `react-markdown` + `remark-gfm` vào dashboard.
- [ ] **3.5** `DocGenerator.tsx`: dropdown, nút Generate, streaming progress, Markdown render.
- [ ] **3.6** Download button và Copy to clipboard.
- [ ] **3.7** Sidebar: thêm link `/docs` vào navigation.

**Milestone 3:** Click "Generate Architecture Overview" → nhận tài liệu Markdown mô tả đúng codebase trong < 30s.

### Giai đoạn 4: Integration & QA (2-3 ngày)

- [ ] **4.1** Integration test: toàn bộ luồng Impact Analysis từ UI → API → Neo4j → highlight.
- [ ] **4.2** Integration test: Rule Engine detect circular dep trên real codebase.
- [ ] **4.3** ESLint + TypeScript strict pass cho tất cả components mới.
- [ ] **4.4** `next build` pass clean.
- [ ] **4.5** CI/CD: thêm test cases cho các endpoint mới trong pytest.
- [ ] **4.6** Cập nhật `docs/conductor/roadmap.md` và `tracks.md`.

---

## 6. Out of Scope (Không làm trong Phase 14)

- Authentication / Login (Phase 16).
- Real-time rule monitoring / auto-trigger khi có commit mới.
- Export tài liệu sang PDF hoặc Confluence.
- Impact Analysis cho graph > 5000 nodes (WebGL optimization — Phase 15+).
- Custom rule DSL (chỉ dùng pre-defined rule types ở MVP).

---

## 7. Risks & Mitigations

| Rủi ro | Mức độ | Hướng xử lý |
|---|---|---|
| Neo4j APOC không có sẵn | Cao | Implement pure Cypher fallback cho BFS thay vì dùng `apoc.path.subgraphAll` |
| Doc generation hallucinate | Trung bình | Grounding prompt với structured context từ graph; verify với actual node names |
| Impact traversal quá chậm với graph lớn | Trung bình | Giới hạn `max_depth=3` default; paginate kết quả nếu > 50 nodes |
| Circular dep Cypher query timeout | Thấp | Set query timeout 10s; fallback message nếu timeout |

---

## 8. Acceptance Criteria

- [ ] `GET /graph/impact/{node_id}` trả về kết quả đúng trong < 3 giây.
- [ ] Affected nodes được highlight đúng màu cam trên visual graph.
- [ ] Ít nhất 3 rule types phát hiện đúng violations trên test codebase.
- [ ] Rule violations highlight đúng màu đỏ trên graph, khác biệt với impact highlight.
- [ ] Doc Generator tạo ra Markdown onboarding guide hợp lệ trong < 30 giây.
- [ ] ESLint + TypeScript pass cho tất cả code mới.
- [ ] `next build` pass clean (exit code 0).
- [ ] CI/CD pipeline (GitHub Actions) pass.
