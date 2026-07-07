# Phase 14 — Giai đoạn 1: Impact Analysis Engine
## Implementation Plan

> **Spec**: `docs/conductor/tracks/phase-14-enterprise-intelligence/spec.md`
> **Branch**: `feat/phase-14-impact-analysis`
> **Estimated**: 2–3 ngày (thực tế, không phải 4-5 ngày như spec dự báo)

---

## Audit Trạng Thái Hiện Tại (As-Is)

Sau khi đọc codebase, Phase 13 đã **implement sẵn phần lớn Giai đoạn 1**. Dưới đây là gap analysis thực tế:

| Hạng mục | Trạng thái | File |
|---|---|---|
| `GET /graph/impact/{node_id}` endpoint | ✅ Đã có | `apps/api/src/routers/graph.py:82` |
| `ImpactAnalysisResponse` type | ✅ Đã có | `apps/dashboard/src/lib/api-types.ts` |
| `useGetImpactQuery` RTK Query hook | ✅ Đã có | `apps/dashboard/src/store/api/aiekpApi.ts:38` |
| `NodeDetailPanel` với nút "Analyze Impact" | ✅ Đã có | `apps/dashboard/src/components/graph/NodeDetailPanel.tsx` |
| Grouped affected list (Direct / Indirect theo depth) | ✅ Đã có | `NodeDetailPanel.tsx:111–204` |
| "Export as Markdown" button | ✅ Đã có | `NodeDetailPanel.tsx:71–99` |
| `highlightedNodeIds` trong Redux + auto-expand | ✅ Đã có | `graphSlice.ts`, `GraphCanvas.tsx:151–166` |
| **Visual node highlight màu cam trên graph** | ❌ Gap | `CustomNodes.tsx` — node chỉ dim/bright, không có orange ring |
| **`rel_types` filter param trên API** | ❌ Gap | `graph.py` — chưa có query param lọc theo relationship type |
| **"Zoom to node" khi click item trong Affected list** | ⚠️ Partial | Click `setSelectedNodeId` nhưng không `fitView` tới node đó |
| **Unit test cho `/graph/impact` endpoint** | ❌ Gap | `apps/api/tests/test_api.py` — chưa có test nào cho impact |
| **`max_depth` param documented + validated** | ⚠️ Partial | Có param `depth` (max=5) nhưng tên khác với spec (`max_depth`) |

---

## Tasks (To-Do List)

### Task 1.1 — Backend: Thêm `rel_types` filter param
**File**: `apps/api/src/routers/graph.py`
**Gap**: Endpoint hiện dùng `[*1..{depth}]` traversal không có direction và không lọc được relationship type. Với graph lớn, traversal undirected sẽ trả về quá nhiều noise.

**Việc cần làm:**
- Thêm query param `rel_types: list[str] = Query(default=["CALLS", "IMPORTS", "INHERITS", "USES"])`.
- Thay Cypher pattern `[*1..{depth}]` thành dynamic relationship filter: `[r:CALLS|IMPORTS|INHERITS|USES*1..{depth}]`.
- Đổi tên param `depth` → `max_depth` để nhất quán với spec (backward-compatible: giữ `depth` làm alias hoặc đổi hẳn).
- Format lại response để group thành `direct` (depth=1) và `indirect` (depth≥2) thay vì flat list — hiện tại frontend đang tự group nhưng API nên cung cấp sẵn.

```python
# Target response schema:
{
  "source_node": { "id": "...", "type": "Function", "label": "..." },
  "affected": {
    "direct":   [{ "id": "...", "type": "...", "label": "...", "via_relation": "CALLS" }],
    "indirect": [{ "id": "...", "type": "...", "label": "...", "depth": 2, "via_relation": "IMPORTS" }]
  },
  "total_count": 12
}
```

> **ADR**: Thay đổi response schema sẽ break frontend hiện tại (đang dùng `impactData.affected` flat array). Cần update `api-types.ts` và `NodeDetailPanel.tsx` đồng thời. Tạo branch riêng để không ảnh hưởng main.

---

### Task 1.2 — Backend: Unit test cho `/graph/impact`
**File**: `apps/api/tests/test_api.py` (thêm mới)

**Việc cần làm:**
- Test case 1: `GET /graph/impact/nonexistent_node` → 404.
- Test case 2: `GET /graph/impact/{valid_id}` với Neo4j down → skip gracefully (pattern như `test_search_endpoint`).
- Test case 3: `GET /graph/impact/{valid_id}?max_depth=0` → 422 (validation error).
- Test case 4: `GET /graph/impact/{valid_id}?max_depth=6` → 422 (vượt max=5).

```python
def test_impact_endpoint_validation():
    with TestClient(app) as client:
        # Invalid max_depth
        response = client.get("/graph/impact/some_node?max_depth=0")
        assert response.status_code == 422

        response = client.get("/graph/impact/some_node?max_depth=6")
        assert response.status_code == 422

def test_impact_endpoint_not_found():
    with TestClient(app) as client:
        try:
            response = client.get("/graph/impact/node_does_not_exist_xyz_12345")
            assert response.status_code == 404
        except Exception as e:
            pytest.skip(f"DB not running: {e}")
```

---

### Task 1.3 — Frontend: Update `api-types.ts` cho response schema mới
**File**: `apps/dashboard/src/lib/api-types.ts`

**Việc cần làm**: Update type definition để match response schema mới (grouped direct/indirect).

```typescript
export interface AffectedNode {
  id: string;
  type: string;
  label: string;
  depth?: number;        // optional: chỉ có trong indirect
  via_relation: string;
}

export interface ImpactAnalysisResponse {
  source_node: { id: string; type: string; label: string };
  affected: {
    direct: AffectedNode[];
    indirect: AffectedNode[];
  };
  total_count: number;
}
```

---

### Task 1.4 — Frontend: Visual highlight màu cam (Impact orange ring) trên node
**File**: `apps/dashboard/src/components/graph/nodes/CustomNodes.tsx`

**Gap**: Hiện tại khi Impact Analysis chạy, `highlightedNodeIds` được set trong Redux, nhưng `BaseNode` trong `CustomNodes.tsx` chỉ apply `ring-blue-500` khi `selected`. Không có visual differentiation nào cho "impact highlighted" vs "search highlighted".

**Việc cần làm:**
1. Thêm `isImpactHighlighted` prop vào `BaseNode` — đọc từ Redux `highlightedNodeIds`.
2. Apply `ring-orange-400` ring khi node nằm trong `highlightedNodeIds` (màu cam, phân biệt với blue của selected).
3. Apply `opacity-30` cho các node **không** nằm trong highlighted set (dim effect) — chỉ khi highlighted set không rỗng.

```typescript
// Trong BaseNode:
const highlightedNodeIds = useSelector((s: RootState) => s.graph.highlightedNodeIds);
const isImpact = highlightedNodeIds.includes(id);
const hasImpact = highlightedNodeIds.length > 0;

// CSS logic:
// - isImpact → ring-orange-400 + scale-105
// - !isImpact && hasImpact → opacity-30
// - selected → ring-[color] (ưu tiên cao nhất)
```

---

### Task 1.5 — Frontend: "Zoom to node" khi click Affected item
**File**: `apps/dashboard/src/components/graph/NodeDetailPanel.tsx`

**Gap**: Hiện tại click vào item trong Affected list chỉ gọi `dispatch(setSelectedNodeId(node.id))`. Node trở thành selected nhưng không fitView tới đó — user phải tự scroll/zoom.

**Vấn đề**: `useReactFlow().fitView()` chỉ dùng được bên trong `ReactFlowProvider`. `NodeDetailPanel` nằm ngoài `ReactFlow` component nên không trực tiếp access được `fitView`.

**Giải pháp**: Thêm Redux action `zoomToNodeId: string | null` vào `graphSlice`. Trong `GraphCanvas` (bên trong ReactFlowProvider), watch `zoomToNodeId` và gọi `fitView({ nodes: [{ id }] })` khi nó thay đổi.

```typescript
// graphSlice.ts — thêm:
zoomToNodeId: string | null;

// action:
setZoomToNodeId: (state, action: PayloadAction<string | null>) => {
  state.zoomToNodeId = action.payload;
}

// GraphCanvas.tsx — thêm useEffect:
useEffect(() => {
  if (zoomToNodeId) {
    fitView({ nodes: [{ id: zoomToNodeId }], duration: 600, padding: 0.3 });
    dispatch(setZoomToNodeId(null)); // reset sau khi zoom
  }
}, [zoomToNodeId, fitView, dispatch]);

// NodeDetailPanel.tsx — onClick:
onClick={() => {
  dispatch(setSelectedNodeId(node.id));
  dispatch(setZoomToNodeId(node.id));
}}
```

---

### Task 1.6 — Frontend: Update `NodeDetailPanel` cho grouped response schema
**File**: `apps/dashboard/src/components/graph/NodeDetailPanel.tsx`

Sau khi Task 1.3 thay đổi `ImpactAnalysisResponse`, cần update cách render:

**Việc cần làm:**
- Thay `affectedByDepth` grouping logic (hiện đang group theo `depth` number) bằng `impactData.affected.direct` và `impactData.affected.indirect`.
- Update `handleAnalyzeImpact` để map cả `direct` và `indirect` nodes:
  ```typescript
  const allAffected = [...impactData.affected.direct, ...impactData.affected.indirect];
  dispatch(setHighlightedNodeIds(allAffected.map(n => n.id)));
  ```
- Update `handleExportMarkdown` tương ứng.
- Hiển thị badge tổng: `{impactData.total_count} affected nodes`.

---

### Task 1.7 — QA & Integration
**Checklist:**
- [ ] Chạy `uvx ruff format .` cho các file Python đã sửa.
- [ ] Chạy `uv run pytest apps/api/tests/test_api.py -v` — pass.
- [ ] Chạy `npm run lint` trong `apps/dashboard` — pass.
- [ ] Chạy `npm run build` — exit code 0.
- [ ] Manual test: Scan repo → click Function node → Analyze Impact → thấy orange ring → click affected item → graph zoom đến node.
- [ ] Manual test: Click "Export .md" → file download với đúng nội dung.

---

## Thứ Tự Thực Hiện

```
Day 1 (Backend):
  Task 1.1 → Task 1.2

Day 2 (Frontend types + Redux):
  Task 1.3 → Task 1.5 (graphSlice + GraphCanvas)

Day 3 (Frontend UI + QA):
  Task 1.4 → Task 1.6 → Task 1.7
```

> **Ghi chú quan trọng**: Task 1.1 (thay đổi response schema) phải được commit trước và cùng lúc với Task 1.3 + 1.6 (update frontend types). Không deploy backend mới mà không deploy frontend cùng lúc để tránh runtime error.

---

## Files Sẽ Được Sửa Đổi

| File | Loại thay đổi | Task |
|---|---|---|
| `apps/api/src/routers/graph.py` | MODIFY — thêm `rel_types`, đổi tên `depth→max_depth`, group response | 1.1 |
| `apps/api/tests/test_api.py` | MODIFY — thêm test cases cho `/graph/impact` | 1.2 |
| `apps/dashboard/src/lib/api-types.ts` | MODIFY — update `ImpactAnalysisResponse` type | 1.3 |
| `apps/dashboard/src/store/graphSlice.ts` | MODIFY — thêm `zoomToNodeId` state + action | 1.5 |
| `apps/dashboard/src/components/graph/GraphCanvas.tsx` | MODIFY — thêm useEffect watch `zoomToNodeId` | 1.5 |
| `apps/dashboard/src/components/graph/nodes/CustomNodes.tsx` | MODIFY — thêm impact orange ring + dim effect | 1.4 |
| `apps/dashboard/src/components/graph/NodeDetailPanel.tsx` | MODIFY — grouped render, zoom-to-node, total_count badge | 1.6 |

**Không tạo file mới** trong Giai đoạn 1. Toàn bộ là extend/improve infrastructure đã có.

---

## Acceptance Criteria (Giai đoạn 1)

- [ ] `GET /graph/impact/{node_id}?max_depth=3&rel_types=CALLS,IMPORTS` trả về grouped response (`direct`/`indirect`) trong < 3s.
- [ ] `GET /graph/impact/{node_id}?max_depth=0` trả về 422.
- [ ] Pytest cho impact endpoint pass (validation + 404 case).
- [ ] Affected nodes được highlight **màu cam** (orange ring) trên graph, phân biệt với selected (blue ring).
- [ ] Non-affected nodes bị dim (opacity 30%) khi impact mode bật.
- [ ] Click item trong Affected list → graph **zoom và pan** đến node đó.
- [ ] Export Markdown có section "Direct" và "Indirect" riêng.
- [ ] `npm run build` pass, ESLint clean.
