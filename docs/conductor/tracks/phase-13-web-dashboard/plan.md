# Phase 13: Implementation Plan - Web Dashboard & Visual Knowledge Graph

> **Spec**: See `spec.md` for full requirements and architecture decisions.
> **Status**: ✅ Completed — 4/4 giai đoạn hoàn thành. Tag: `v0.1.2`

---

## Phase Breakdown

Phase 13 được chia thành 4 giai đoạn nhỏ, mỗi giai đoạn tạo ra một "milestone" có thể demo độc lập.

---

## Giai đoạn 1: Foundation & API Audit (2-3 ngày)

Mục tiêu: Dựng khung dự án và kiểm tra lại toàn bộ API backend cần thiết.

### Tasks

- [x] **1.1** Khởi tạo project Next.js 16 tại `apps/dashboard/` với TypeScript.
- [x] **1.2** Cài đặt dependencies: `tailwindcss`, `shadcn/ui`, `@reduxjs/toolkit`, `react-redux`, `@xyflow/react`, `elkjs`.
- [x] **1.3** Thiết lập layout cơ bản: Sidebar + Main Area + Right Panel (`AppShell.tsx`, `Sidebar.tsx`).
- [x] **1.4** Cấu hình environment variables: `NEXT_PUBLIC_API_URL` trỏ đến FastAPI backend.
- [x] **1.5** **API Audit**: Xác định endpoints cần tạo mới — tạo `GET /stats` và `DELETE /graph/` trong backend.
- [x] **1.6** Tạo RTK Query API client (`store/api/aiekpApi.ts`) với type definitions đầy đủ.

**Milestone 1 ✅:** Layout cơ bản chạy tại `http://localhost:3000`.

---

## Giai đoạn 2: Visual Knowledge Graph (5-7 ngày)

Mục tiêu: Tính năng cốt lõi - vẽ được Knowledge Graph tương tác.

### Tasks

- [x] **2.1** Tích hợp `@xyflow/react` (React Flow) thay Sigma.js — hỗ trợ custom node/edge tốt hơn.
- [x] **2.2** Synthesize Virtual Directory Nodes từ file paths trong `graph-utils.ts`; fetch nodes/edges từ RTK Query.
- [x] **2.3** Custom node components: `DirectoryNode` (amber), `FileNode` (blue), `ClassNode` (purple), `FunctionNode` (emerald).
- [x] **2.4** Zoom, pan tích hợp sẵn trong React Flow; `NodeDetailPanel.tsx` mở bên phải khi click.
- [x] **2.5** `GraphCanvas.tsx`: visibility logic (cha expanded → con visible), expand/collapse button trên mỗi node.
- [x] **2.6** `SearchBar.tsx`: highlight + zoom đến node theo tên.
- [x] **2.7** `elk-layout.ts`: ELK layered algorithm với spacing 150px/200px; hierarchy edges tự sinh.

**Milestone 2 ✅:** Knowledge Graph tương tác đầy đủ với dữ liệu thật từ Neo4j.

---

## Giai đoạn 3: Impact Analysis & AI Chat (5-7 ngày)

Mục tiêu: Hai tính năng "wow factor" chính của Dashboard.

### Tasks (Impact Analysis)

> **ADR:** Impact Analysis API (`/graph/impact/{node_id}`) được dời sang Phase 14 — đây là tính năng phức tạp hơn MVP.

- [x] **3.1** `ChatBox.tsx`: streaming với `ReadableStream` + `fetch`, hiển thị từng chunk real-time.
- [x] **3.2** `EvidencePanel.tsx`: hiển thị danh sách source nodes có `snippet` field thu gọn.
- [x] **3.3** Trang `/repositories` với form nhập path, nút "Scan Now" gọi POST `/ingest`.
- [x] **3.4** SSE progress bar: EventSource kết nối `/ingest/progress`, cập nhật real-time.
- [x] **3.5** `DashboardOverlay.tsx`: nút "Clear Graph" với confirm dialog → DELETE `/graph/` kèm `x-api-key` header.
- [x] **3.6** Backend: Persistent scan status lưu `scan_status.json`, không mất khi server restart.

**Milestone 3 ✅:** Chat AI streaming hoạt động; Repository scan + progress real-time hoạt động.

---

## Giai đoạn 4: Repository Management & Dashboard Overview (3-4 ngày)

Mục tiêu: Hoàn thiện các tính năng quản lý và tổng quan.

### Tasks (Repository Management)

- [x] **4.1** ESLint strict mode — fix tất cả `any`, missing deps, state mutation issues.
- [x] **4.2** TypeScript strict — fix type errors trong `NodeDetailPanel`, `aiekpApi`, `ChatBox`.
- [x] **4.3** `next build` pass clean (Turbopack, exit code 0, không có module not found).
- [x] **4.4** Fix `.gitignore` root: `lib/` → `/lib/` để `apps/dashboard/src/lib` không bị ignore.
- [x] **4.5** Commit và push `src/lib/` (elk-layout, graph-utils, utils, api-types, node-colors) lên GitHub.
- [x] **4.6** CI/CD pipeline (GitHub Actions) pass — cả frontend build lẫn backend ruff/pytest.

**Milestone 4 ✅:** CI/CD xanh hoàn toàn. Phase 13 done.

---

## Dependencies & Prerequisites

Trước khi bắt đầu, đảm bảo:
- [ ] Backend API (Phase 9) đang chạy và `GET /api/v1/graph/nodes` trả về dữ liệu.
- [ ] Neo4j đang có dữ liệu (đã chạy ít nhất một lần scan repository).
- [ ] Node.js >= 18 và pnpm đã được cài đặt.

---

## Risks & Mitigations

| Rủi ro | Mức độ | Thực tế xử lý |
|---|---|---|
| Graph quá lớn, render chậm | Cao | ELK layered layout + expand/collapse giảm nodes hiển thị đồng thời |
| Backend API không đủ endpoint | Trung bình | Tạo mới `/stats` và `DELETE /graph/` trong phase — giải quyết hoàn toàn |
| Streaming response phức tạp | Thấp | Tự implement ReadableStream với fetch — đơn giản và hoạt động tốt |
| `src/lib` bị git ignore | Không lường trước | Phát hiện qua CI/CD fail; fix `.gitignore` root từ `lib/` → `/lib/` |
