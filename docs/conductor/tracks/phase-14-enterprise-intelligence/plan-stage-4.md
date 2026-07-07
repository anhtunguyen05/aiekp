# Phase 14 - Stage 4: Integration & QA

> **Context:** Giai đoạn 4 tập trung vào việc đảm bảo chất lượng, tích hợp các thành phần từ Giai đoạn 1, 2, 3 và chuẩn bị cho việc hoàn thành Phase 14.
> **Prerequisite:** Giai đoạn 1 (Impact Analysis), Giai đoạn 2 (Rule Engine) và Giai đoạn 3 (Doc Generator) đã hoàn thành.

## 1. Goal

- Đảm bảo toàn bộ hệ thống API backend và các màn hình Next.js frontend hoạt động trơn tru với nhau.
- Tăng độ bao phủ kiểm thử (Test Coverage) cho các module API mới (Impact, Rules, Docs).
- Fix toàn bộ các lỗi ESLint, TypeScript types.
- Cập nhật tài liệu roadmap và track record.

## 2. Tasks Breakdown

### Task 4.1 — Backend Integration Tests (Pytest)
**Mục tiêu**: Thêm test coverage cho toàn bộ endpoints mới trong Phase 14.
**Chi tiết**:
- Viết integration test cho `GET /graph/impact/{node_id}` để kiểm tra response trả về đúng format `direct`, `indirect`.
- Viết integration test cho `POST /rules/check` để verify luồng nhận payloads và xử lý các rule types (`no-circular-deps`, `max-fan-in`, v.v.).
- Đảm bảo mock Neo4j hoặc test database hoạt động chuẩn cho các bài test này.

### Task 4.2 — Frontend QA: Linting & Type Checking
**Mục tiêu**: Đảm bảo không có lỗi frontend trước khi build.
**Chi tiết**:
- Chạy `npm run lint` trong `apps/dashboard`.
- Chạy `npx tsc --noEmit` để bắt lỗi TypeScript.
- Khắc phục mọi lỗi liên quan đến types trong `graphSlice.ts`, `api-types.ts`, `ImpactAnalysisPanel.tsx`, `DocGenerator.tsx` và `RuleList.tsx`.

### Task 4.3 — End-to-End Build & Run
**Mục tiêu**: Xác nhận hệ thống production-ready.
**Chi tiết**:
- Chạy `npm run build` trong `apps/dashboard`.
- Đảm bảo Exit code là 0 và tất cả static/SSR pages compile thành công.
- Review tổng thể giao diện để tránh lỗi CSS/Layout ở các page `/rules` và `/docs`.

### Task 4.4 — Project Context & Documentation Update
**Mục tiêu**: Đóng lại Track Phase 14.
**Chi tiết**:
- Cập nhật `docs/conductor/roadmap.md` đánh dấu hoàn thành Phase 14.
- Cập nhật `docs/conductor/tracks.md` thay đổi trạng thái Phase 14 sang `[x] Completed`.
- Viết tổng hợp Changelog hoặc Release Notes (nếu cần).

---

## 3. Execution Checklist

- [ ] `Task 4.1.1` Bổ sung pytest cho Impact endpoint.
- [ ] `Task 4.1.2` Bổ sung pytest cho Rules endpoint.
- [ ] `Task 4.2.1` Fix ESLint errors (`npm run lint`).
- [ ] `Task 4.2.2` Fix TypeScript errors (`npx tsc --noEmit`).
- [ ] `Task 4.3.1` Chạy Next.js build thành công (`npm run build`).
- [ ] `Task 4.4.1` Update `roadmap.md`.
- [ ] `Task 4.4.2` Update `tracks.md`.

## 4. Verification Plan

- [ ] Pytest suite vượt qua thành công: `uv run pytest apps/api/tests/ -v`
- [ ] Frontend checks vượt qua: `npm run lint` và `npx tsc --noEmit`
- [ ] Build pipeline hoạt động: `npm run build` không lỗi.
