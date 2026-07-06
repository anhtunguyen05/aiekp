# Phase 13: Web Dashboard & Visual Knowledge Graph

> **Context**: Read `docs/project-context.md` before implementing any feature in this phase.
> **Principle**: Context precedes code. This spec defines WHAT and WHY before any HOW.

---

## 1. Objective

Tạo ra một **Web Dashboard** là bộ mặt chính thức (Visual Interface) của AIEKP, cho phép người dùng:

1. **Xem** toàn bộ Knowledge Graph dưới dạng đồ thị phân cấp (Hierarchical Graph) tương tác theo cấu trúc thư mục → file → class → function.
2. **Tra cứu** Impact Analysis (Phân tích Ảnh hưởng): Click vào một Node (file, hàm) và thấy ngay những component nào sẽ bị ảnh hưởng.
3. **Chat** với AI qua giao diện Chatbot giống ChatGPT nhưng được hỗ trợ bởi Knowledge Engine (Evidence-based Reasoning), không phải trả lời chung chung.
4. **Quản lý** việc Scan repository và theo dõi tiến trình cập nhật Knowledge Graph.

> **Mục tiêu cốt lõi:** Biến AIEKP từ một công cụ backend thầm lặng trở thành một sản phẩm có thể **demo được ngay lập tức** (trong vòng 30 giây) với bất kỳ ai không có kiến thức kỹ thuật.

---

## 2. Target Users

| Người dùng | Nhu cầu | Tính năng Dashboard phù hợp |
|---|---|---|
| **Tech Lead / Architect** | Hiểu kiến trúc tổng thể, review PR | Visual Graph (Hierarchical), Impact Analysis |
| **Developer mới (Onboarding)** | Hiểu nhanh codebase lạ | Chat AI, Graph khám phá theo folder |
| **Engineering Manager** | Theo dõi độ phức tạp kỹ thuật | Dashboard tổng quan, Stats |
| **External Stakeholder** | Demo sản phẩm | Trang Overview, Chat demo |

---

## 3. Core Features (MVP)

### 3.1. Visual Knowledge Graph (Feature chính)

Vẽ toàn bộ Knowledge Graph từ Neo4j ra màn hình dưới dạng đồ thị phân cấp tương tác (Hierarchical Drill-down Graph).

**Yêu cầu:**
- Hiển thị theo cấu trúc phân cấp: **Folder → File → Class → Function** (drill-down).
- Tổng hợp **Virtual Directory Nodes** từ file paths (API chỉ trả về File/Class/Function, không có Directory node).
- Phân biệt loại Node bằng màu sắc và icon riêng biệt:
  - 🟡 `Directory` — màu amber, icon Folder/FolderOpen
  - 🔵 `File` — màu blue, icon File
  - 🟣 `Class` — màu purple, icon Cube
  - 🟢 `Function` — màu emerald, icon Function
- Hiển thị đường kết nối phân cấp (hierarchy edges) với màu sắc phân biệt:
  - Amber dashed: Directory → Subfolder/File
  - Blue dashed: File → Class → Function
  - Blue animated: Semantic relationships (CALLS, IMPORTS, etc.)
- Nút `+` / `-` trên từng node để **expand/collapse** cấp con.
- Hỗ trợ **zoom in/zoom out**, **pan**, và **search** node theo tên.
- Khi **click vào Node** → mở panel chi tiết bên phải (metadata, docstring, parameters).
- ELK.js layout tự động tính toán vị trí node để không chồng chéo, có đủ spacing.

> **ADR:** Chuyển từ Sigma.js sang **React Flow + ELK.js** (quyết định trong Giai đoạn 2). React Flow cung cấp khả năng tương tác phong phú hơn với custom node/edge, phù hợp với yêu cầu phân cấp. ELK.js xử lý auto-layout cho hierarchical graph tốt hơn ForceAtlas2 trong trường hợp này.

### 3.2. Impact Analysis Panel

Từ một Node đang được chọn, tự động tìm và **highlight toàn bộ các Node bị ảnh hưởng** (Affected Nodes) nếu Node đó bị thay đổi.

**Yêu cầu:**
- Có nút "Analyze Impact" khi đang chọn 1 Node.
- Vẽ nổi bật (highlight bằng màu đỏ/cam) các Node sẽ bị ảnh hưởng.
- Liệt kê danh sách các Node bị ảnh hưởng theo thứ tự độ ưu tiên (trực tiếp → gián tiếp).
- Xuất báo cáo Impact Analysis ra định dạng Markdown.

### 3.3. AI Chat Interface

Giao diện chat giống ChatGPT, nhưng mỗi câu trả lời đều kèm theo **Evidence** (bằng chứng) lấy từ Knowledge Graph.

**Yêu cầu:**
- Chat box với streaming response (real-time output, không chờ toàn bộ câu trả lời).
- Mỗi câu trả lời hiển thị phần **"Evidence"** thu gọn (collapsible) bên dưới, chứa danh sách các Node/file liên quan.
- Khi click vào một Evidence item → tự động zoom đến Node đó trên Visual Graph.
- Lưu lịch sử chat trong session (không cần persist vào DB ở MVP).

### 3.4. Repository Management Panel

Giao diện để trigger và theo dõi quá trình Scan repository.

**Yêu cầu:**
- Form nhập URL repository (hoặc path cục bộ).
- Nút "Scan Now" gọi đến API `/api/v1/ingest`.
- Hiển thị real-time progress của quá trình scan (dùng WebSocket hoặc Server-Sent Events).
- Danh sách các repository đã được scan cùng trạng thái và thời gian scan gần nhất.

### 3.5. Dashboard Overview (Home Page)

Trang chủ hiển thị tổng quan sức khỏe của Knowledge Graph.

**Yêu cầu:**
- Hiển thị các thống kê: Tổng số Files, Classes, Functions, API Endpoints, DB Tables đã được index.
- Card "Recent Activity" hiển thị các file được cập nhật gần nhất.
- Card "Complexity Hotspots" hiển thị top 5 file/class phức tạp nhất (có nhiều dependencies nhất).

---

## 4. Architecture Design

### 4.1. Vị trí trong Monorepo

```
apps/
└── dashboard/          # [NEW] - Phase 13
    ├── src/
    │   ├── app/        # Next.js App Router pages
    │   ├── components/
    │   │   └── graph/  # GraphCanvas, SearchBar, NodeDetailPanel
    │   │       └── nodes/  # FileNode, ClassNode, FunctionNode, DirectoryNode
    │   ├── lib/        # graph-utils.ts, elk-layout.ts, api-client.ts
    │   └── store/      # Redux: graphSlice.ts (selectedNodeId, expandedNodeIds, highlightedNodeIds)
    ├── package.json
    └── next.config.js
```

### 4.2. Technology Stack

| Layer | Công nghệ | Lý do chọn |
|---|---|---|
| **Framework** | Next.js 15 (App Router) | Turbopack, React Server Components |
| **Language** | TypeScript | Type safety, IDE support tốt |
| **Styling** | Tailwind CSS + shadcn/ui | Nhanh, đẹp, customizable |
| **Graph Visualization** | **`@xyflow/react` (React Flow)** | Custom node/edge, expand/collapse, tương tác phong phú |
| **Graph Layout** | **`elkjs`** | Auto-layout hierarchical graph, orthogonal edge routing |
| **State Management** | Redux Toolkit (RTK) + RTK Query | expandedNodeIds, selectedNodeId, search state |
| **Real-time** | SSE (Server-Sent Events) | Đơn giản hơn WebSocket, đủ cho use case progress bar |
| **Package Manager** | pnpm | Nhất quán với monorepo setup |

> **ADR (Sigma.js → React Flow):** Ban đầu spec chọn Sigma.js/WebGL để xử lý graph lớn. Trong quá trình triển khai Giai đoạn 2, nhận thấy yêu cầu **phân cấp drill-down** (expand/collapse per node) đòi hỏi khả năng tùy biến node/edge render rất cao mà Sigma.js không hỗ trợ tốt. React Flow + ELK.js được chọn thay thế, cho phép custom React component cho mỗi node type và hierarchical layout tự động.

### 4.3. Giao tiếp với Backend (API Contract)

Dashboard chỉ giao tiếp qua **REST API** (đã có từ Phase 9). Không truy cập trực tiếp vào Neo4j hay bất kỳ database nào.

**API endpoints cần thiết:**

| Endpoint | Method | Trạng thái | Dùng cho |
|---|---|---|---|
| `/graph/nodes` | GET | ✅ Hoạt động | Visual Graph - lấy danh sách nodes |
| `/graph/edges` | GET | ✅ Hoạt động | Visual Graph - lấy danh sách edges |
| `/graph/impact/{node_id}` | GET | 🔲 Cần tạo mới | Impact Analysis |
| `/chat` | POST (stream) | 🔲 Cần kiểm tra | AI Chat với streaming |
| `/ingest` | POST | ✅ Có sẵn | Trigger scan repository |
| `/stats` | GET | 🔲 Cần tạo mới | Dashboard Overview stats |

### 4.4. State Management (Redux graphSlice)

```typescript
interface GraphState {
  selectedNodeId: string | null;       // Node đang được click
  expandedNodeIds: string[];           // Nodes đã được expand (drill-down)
  highlightedNodeIds: string[];        // Nodes được highlight (search/impact)
  searchQuery: string;                 // Chuỗi tìm kiếm hiện tại
}
```

---

## 5. UI/UX Design Principles

- **Layout chính:** Sidebar trái (Navigation) + Main content area (Graph) + Panel phải (Details).
- **Dark mode first:** Giao diện tối (dark theme) làm mặc định, phù hợp với công cụ developer. (`bg-zinc-950`, glassmorphism với `backdrop-blur-md`).
- **Graph là trung tâm:** Visual Graph chiếm 60-70% diện tích màn hình trên mọi trang.
- **Progressive Disclosure:** Thông tin chi tiết chỉ hiện ra khi cần (expand node, click node), không overload UI.
- **Tốc độ cảm nhận:** Dùng skeleton loading và optimistic UI để giao diện luôn có cảm giác nhanh.
- **Hierarchy clarity:** Màu sắc node và đường kết nối phải đủ phân biệt để người dùng hiểu cấu trúc phân cấp ngay lập tức.

---

## 6. Out of Scope (Không làm trong Phase 13)

- Authentication / Login (sẽ làm ở Phase 16).
- Multi-tenancy / RBAC (sẽ làm ở Phase 16).
- Chỉnh sửa Knowledge Graph trực tiếp trên UI.
- Mobile responsive (ưu tiên desktop-first).
- Deploy lên production server công khai (chỉ chạy local).
- WebGL rendering cho graph cực lớn (>5000 nodes) — sẽ xem xét ở Phase 14.

---

## 7. Implementation Phases (Thực tế)

### Giai đoạn 1: Foundation & API Audit ✅ Hoàn thành
- Next.js project, layout cơ bản, RTK Query API client, audit endpoints.

### Giai đoạn 2: Visual Knowledge Graph ✅ Hoàn thành
**Thực tế đã làm (khác với kế hoạch ban đầu):**
- Dùng `@xyflow/react` + `elkjs` thay vì `@react-sigma/core`.
- Tổng hợp **Virtual Directory Nodes** trong `graph-utils.ts` từ file paths (API không có directory node).
- Custom nodes: `DirectoryNode`, `FileNode`, `ClassNode`, `FunctionNode` (với expand/collapse button).
- `GraphCanvas.tsx`: logic visibility (cha visible + expanded → con visible), edge lifting, hierarchy edges auto-generated trong ELK layout.
- `elk-layout.ts`: Tự động tạo hierarchy edges (amber dashed cho Directory→*, blue dashed cho File→Class) với spacing lớn (80px node-node, 120px between-layers).
- `SearchBar.tsx`: tìm kiếm và highlight node.
- Redux `graphSlice.ts`: `expandedNodeIds`, `selectedNodeId`, `highlightedNodeIds`.

### Giai đoạn 3: Impact Analysis & AI Chat 🔲 Tiếp theo
- Xem `plan.md` phần Giai đoạn 3 để biết chi tiết.

### Giai đoạn 4: Repository Management & Dashboard Overview 🔲 Kế hoạch
- Xem `plan.md` phần Giai đoạn 4 để biết chi tiết.

---

## 8. Acceptance Criteria (Điều kiện hoàn thành)

- [x] Dashboard chạy được ở `http://localhost:3000` sau lệnh `pnpm dev`.
- [x] Visual Graph hiển thị đúng dữ liệu từ Neo4j với phân cấp Folder → File → Class → Function.
- [x] Tính năng expand/collapse node hoạt động, có đường kết nối màu sắc phân biệt.
- [x] Search/highlight node hoạt động.
- [x] TypeScript compile sạch (`tsc --noEmit` pass).
- [ ] Tính năng Impact Analysis trả về kết quả chính xác trong vòng 3 giây.
- [ ] Chat Interface gửi câu hỏi và nhận streaming response từ Reasoning Engine.
- [ ] Form Scan Repository trigger được API và hiển thị thông báo thành công/thất bại.
- [ ] Dashboard Overview hiển thị đúng số liệu thống kê từ Knowledge Graph.
- [ ] Không có lỗi ESLint.
