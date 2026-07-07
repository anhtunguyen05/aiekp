# Phase 14 — Giai đoạn 2: Architectural Rule Engine
## Implementation Plan

> **Spec**: `docs/conductor/tracks/phase-14-enterprise-intelligence/spec.md`
> **Branch**: `feat/phase-14-rule-engine`
> **Estimated**: 3-4 ngày

---

## Tasks (To-Do List)

### Task 2.1 — Backend: Rule Definitions & Endpoint
**File**: `apps/api/src/routers/rules.py` (Mới)
**Việc cần làm:**
- Tạo schema Pydantic cho `RuleDefinition` (`type`, `threshold`, `params`).
- Tạo endpoint `POST /rules/check` nhận vào danh sách `RuleDefinition` và thực thi Cypher queries trên Neo4j.
- Viết 5 Cypher query template tương ứng với 5 rule types MVP: 
  - `no-circular-deps`
  - `max-fan-in`
  - `max-fan-out`
  - `no-cross-layer`
  - `max-complexity`
- Móc nối (include) `routers.rules.router` vào `main.py`.

### Task 2.2 — Backend: Unit Tests cho Rule Engine
**File**: `apps/api/tests/test_rules.py` (Mới)
**Việc cần làm:**
- Viết test check API validation cho `POST /rules/check`.
- Viết test cho logic Cypher bằng cách mock dữ liệu hoặc chạy trên db test.

### Task 2.3 — Frontend: Khai báo API Types
**File**: `apps/dashboard/src/lib/api-types.ts`
**Việc cần làm:**
- Thêm các types cần thiết như `RuleDefinition`, `RuleViolation`, và `RuleCheckResponse`.

### Task 2.4 — Frontend: Tích hợp API Endpoint
**File**: `apps/dashboard/src/store/api/aiekpApi.ts`
**Việc cần làm:**
- Thêm `checkRules` mutation endpoint sử dụng POST để gửi danh sách rule về backend.

### Task 2.5 — Frontend: Giao diện Rule Engine
**File**: `apps/dashboard/src/app/rules/page.tsx` (Mới)
**File**: `apps/dashboard/src/components/rules/RuleList.tsx` (Mới)
**File**: `apps/dashboard/src/components/rules/ViolationTable.tsx` (Mới)
**Việc cần làm:**
- Xây dựng layout cho trang `/rules`.
- `RuleList.tsx`: Hiển thị danh sách các rule để người dùng bật/tắt và cài đặt ngưỡng (`threshold`).
- `ViolationTable.tsx`: Bảng kết quả sau khi chạy "Run Audit". Click vào lỗi sẽ navigate/zoom đến Node bị lỗi trên biểu đồ (tận dụng action `zoomToNodeId` đã làm ở Giai đoạn 1).

### Task 2.6 — Frontend: Highlight Nodes Vi Phạm
**File**: `apps/dashboard/src/store/graphSlice.ts`
**File**: `apps/dashboard/src/components/graph/nodes/CustomNodes.tsx`
**Việc cần làm:**
- Cập nhật `graphSlice.ts` thêm biến trạng thái `violationNodeIds: string[]`.
- Cập nhật `CustomNodes.tsx` để node có viền đỏ (`ring-red-500`) nếu ID của nó nằm trong danh sách `violationNodeIds` (phân biệt với màu cam của Impact Analysis).

### Task 2.7 — Frontend: Update Navigation Sidebar
**File**: `apps/dashboard/src/components/layout/Sidebar.tsx`
**Việc cần làm:**
- Bổ sung một menu item dẫn tới đường dẫn `/rules`.

### Task 2.8 — QA & Integration
**Checklist:**
- [ ] Chạy linting, formatting `uvx ruff format .` cho code Python mới.
- [ ] Chạy `uv run pytest apps/api/tests/test_rules.py -v`.
- [ ] Chạy ESLint, build NextJS `npm run build` thành công.
- [ ] Manual test trực tiếp trên UI để đảm bảo các rule hoạt động đúng như spec.
