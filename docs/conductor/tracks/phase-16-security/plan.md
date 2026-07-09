# Phase 16: Implementation Plan

## Giai đoạn 1: Database & Models (Auth DB)
- [ ] Thêm thư viện `pyjwt`, `passlib[bcrypt]`, `bcrypt` vào dependency.
- [ ] Khởi tạo kết nối SQLAlchemy SQLite tại `apps/api/src/auth/database.py`.
- [ ] Tạo các mô hình `User`, `Tenant` (SQLAlchemy models) tại `apps/api/src/auth/models.py`.
- [ ] Viết các hàm CRUD cơ bản (tạo user, verify password) tại `apps/api/src/auth/crud.py`.

## Giai đoạn 2: Auth Endpoints & Middleware
- [ ] Cấu hình SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES.
- [ ] Viết hàm `create_access_token` và `decode_access_token`.
- [ ] Xây dựng các router `/auth/login`, `/auth/register` trong `apps/api/src/routers/auth.py`.
- [ ] Chỉnh sửa `apps/api/src/dependencies.py`:
  - Thay thế `verify_api_key` bằng `get_current_user` (xác minh JWT Token và trả về thông tin User chứa `tenant_id`).

## Giai đoạn 3: Multi-tenancy Integration (Graph & Vector)
- [ ] Cập nhật `GraphIngestor` để nhận `tenant_id` khi tạo dữ liệu (truyền vào metadata).
- [ ] Cập nhật `Neo4jGraphManager` để mọi thao tác tạo Node và Search Node đều ép điều kiện `{tenant_id: $tenant_id}`.
- [ ] Cập nhật `QdrantVectorManager` để `add_texts` đính kèm payload `tenant_id` và `search` có bộ lọc (filter) theo `tenant_id`.
- [ ] Cập nhật các service (Context, Reasoning) để lấy `tenant_id` từ Request (`get_current_user`) và truyền xuống các Database Manager.

## Giai đoạn 4: CLI Updates & Verification
- [ ] Bổ sung module auth vào CLI (`apps/cli/src/aiekp_cli/commands/auth.py`).
- [ ] Thêm chức năng lưu file JWT locally (`~/.aiekp/auth.json`).
- [ ] Chỉnh sửa cấu hình Axios/HTTP Client của frontend (nếu có) và CLI để gửi `Authorization: Bearer <token>` thay cho API Key cũ.
- [ ] Thực hiện test (unit test + end-to-end thủ công) chứng minh dữ liệu giữa 2 tenant hoàn toàn biệt lập (Ingest bằng Tenant A thì Tenant B không tìm kiếm thấy).
