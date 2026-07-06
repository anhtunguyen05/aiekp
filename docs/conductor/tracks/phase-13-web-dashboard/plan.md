# Phase 13: Implementation Plan - Web Dashboard & Visual Knowledge Graph

> **Spec**: See `spec.md` for full requirements and architecture decisions.
> **Estimated Duration**: 3-4 weeks (solo developer)

---

## Phase Breakdown

Phase 13 được chia thành 4 giai đoạn nhỏ, mỗi giai đoạn tạo ra một "milestone" có thể demo độc lập.

---

## Giai đoạn 1: Foundation & API Audit (2-3 ngày)

Mục tiêu: Dựng khung dự án và kiểm tra lại toàn bộ API backend cần thiết.

### Tasks

- [ ] **1.1** Khởi tạo project Next.js 16 tại `apps/dashboard/` với TypeScript.
- [ ] **1.2** Cài đặt dependencies: `tailwindcss`, `shadcn/ui`, `@reduxjs/toolkit`, `react-redux`, `sigma`, `graphology`.
- [ ] **1.3** Thiết lập layout cơ bản: Sidebar + Main Area + Right Panel.
- [ ] **1.4** Cấu hình environment variables: `NEXT_PUBLIC_API_URL` trỏ đến FastAPI backend.
- [ ] **1.5** **API Audit**: Gọi thử các endpoint hiện có, liệt kê những endpoint cần tạo mới ở backend:
  - `GET /api/v1/graph/nodes` - kiểm tra format response.
  - `GET /api/v1/graph/edges` - kiểm tra format response.
  - `GET /api/v1/stats` - **cần tạo mới** nếu chưa có.
  - `GET /api/v1/graph/impact/{node_id}` - **cần tạo mới**.
- [ ] **1.6** Tạo API client TypeScript (`lib/api-client.ts`) với type definitions cho tất cả response.

**Milestone 1:** `http://localhost:3000` hiển thị layout trống với sidebar và title "AIEKP Dashboard".

---

## Giai đoạn 2: Visual Knowledge Graph (5-7 ngày)

Mục tiêu: Tính năng cốt lõi - vẽ được Knowledge Graph tương tác.

### Tasks

- [ ] **2.1** Tích hợp Sigma.js vào component `KnowledgeGraph.tsx`.
- [ ] **2.2** Fetch dữ liệu nodes và edges từ API, map sang format của `graphology` (thư viện graph data structure dùng kèm Sigma).
- [ ] **2.3** Phân màu và icon theo loại Node: `File` (xanh dương), `Class` (tím), `Function` (xanh lá), `API Endpoint` (cam), `DB Table` (đỏ).
- [ ] **2.4** Implement tương tác cơ bản: zoom, pan, hover hiển thị tooltip tên Node.
- [ ] **2.5** Implement click vào Node → mở **Right Panel** hiển thị chi tiết node (file path, metadata, docstring nếu có).
- [ ] **2.6** Implement thanh tìm kiếm: gõ tên → highlight node trên graph và scroll đến node đó.
- [ ] **2.7** Xử lý trường hợp graph quá lớn: implement layout algorithm (`ForceAtlas2`) để các node không bị chồng chéo.

**Milestone 2:** Có thể nhìn thấy và tương tác với Knowledge Graph thật từ Neo4j.

---

## Giai đoạn 3: Impact Analysis & AI Chat (5-7 ngày)

Mục tiêu: Hai tính năng "wow factor" chính của Dashboard.

### Tasks (Impact Analysis)

- [ ] **3.1** Tạo backend endpoint `GET /api/v1/graph/impact/{node_id}` truy vấn Neo4j để tìm tất cả node bị ảnh hưởng (BFS/DFS traversal).
- [ ] **3.2** Trong Dashboard, khi một Node đang được chọn → hiện nút "Analyze Impact".
- [ ] **3.3** Khi click Analyze Impact → gọi API → highlight các node bị ảnh hưởng bằng màu đỏ/cam trên graph.
- [ ] **3.4** Panel bên phải liệt kê danh sách affected nodes chia theo cấp độ (trực tiếp, gián tiếp).
- [ ] **3.5** Nút "Export as Markdown" tạo ra file báo cáo Impact Analysis.

### Tasks (AI Chat)

- [ ] **3.6** Tạo trang `/chat` với layout 2 cột: Chat history (trái) + Graph highlight (phải).
- [ ] **3.7** Implement Chat Box với streaming: dùng `fetch` với `ReadableStream` để nhận response từng chunk.
- [ ] **3.8** Hiển thị phần "Evidence" thu gọn bên dưới mỗi AI response (danh sách file/node liên quan).
- [ ] **3.9** Click vào Evidence item → chuyển tab sang Graph và zoom đến đúng node đó.
- [ ] **3.10** Thêm "suggested questions" gợi ý câu hỏi mẫu cho user mới.

**Milestone 3:** Có thể hỏi "Hàm này ảnh hưởng đến những gì?" và thấy kết quả trực quan trên graph.

---

## Giai đoạn 4: Repository Management & Dashboard Overview (3-4 ngày)

Mục tiêu: Hoàn thiện các tính năng quản lý và tổng quan.

### Tasks (Repository Management)

- [ ] **4.1** Tạo trang `/repositories` với form nhập repository URL/path.
- [ ] **4.2** Kết nối nút "Scan Now" với API `/api/v1/ingest`.
- [ ] **4.3** Implement real-time progress bar dùng SSE (Server-Sent Events) từ backend.
- [ ] **4.4** Hiển thị danh sách repositories đã scan với thông tin: tên, số files, thời gian scan cuối.

### Tasks (Dashboard Overview)

- [ ] **4.5** Tạo backend endpoint `GET /api/v1/stats` trả về: tổng nodes, files, functions, API endpoints, DB tables.
- [ ] **4.6** Trang chủ (`/`) hiển thị Stats Cards với animation số đếm (count-up animation).
- [ ] **4.7** Widget "Complexity Hotspots" liệt kê top 5 file có nhiều dependencies nhất.
- [ ] **4.8** Widget "Recent Scans" hiển thị activity feed.

### Tasks (Polish & QA)

- [ ] **4.9** Dark mode toàn bộ dashboard.
- [ ] **4.10** Skeleton loading cho tất cả component cần fetch data.
- [ ] **4.11** Error states khi API call thất bại (hiển thị thông báo lỗi thân thiện).
- [ ] **4.12** Kiểm tra `tsc --noEmit` và `eslint` pass 100%.

**Milestone 4 (Final):** Dashboard hoàn chỉnh, có thể demo toàn bộ tính năng từ A đến Z.

---

## Dependencies & Prerequisites

Trước khi bắt đầu, đảm bảo:
- [ ] Backend API (Phase 9) đang chạy và `GET /api/v1/graph/nodes` trả về dữ liệu.
- [ ] Neo4j đang có dữ liệu (đã chạy ít nhất một lần scan repository).
- [ ] Node.js >= 18 và pnpm đã được cài đặt.

---

## Risks & Mitigations

| Rủi ro | Mức độ | Hướng xử lý |
|---|---|---|
| Graph quá lớn, render chậm | Cao | Dùng WebGL renderer của Sigma.js + phân trang (chỉ hiện subgraph quanh node đang xem) |
| Backend API không đủ endpoint | Trung bình | Audit trước ở Giai đoạn 1, tạo mock data để frontend phát triển song song |
| Streaming response phức tạp | Thấp | Dùng thư viện `ai` (Vercel AI SDK) nếu tự implement quá phức tạp |
