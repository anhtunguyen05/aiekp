# Phase 16: Security, Auth & Multi-Tenancy (RBAC) Specification

## Mục tiêu
Thiết lập hệ thống xác thực (Authentication) và phân quyền (Authorization) bằng JWT/OAuth2. Đồng thời, cấu hình hệ thống hỗ trợ Multi-tenancy (RBAC cấp độ Node) cho Neo4j và Qdrant để đảm bảo an toàn dữ liệu, cho phép nhiều team (tenant) sử dụng nền tảng AIEKP mà không lộ lọt dữ liệu code giữa các team.

## Thiết kế Kiến trúc

### 1. Authentication (Xác thực)
- **Phương thức:** Sử dụng OAuth2 Password Bearer flow, trả về JWT Token.
- **Provider:** Tự xây dựng (Built-in) để tối ưu và giảm thiểu phụ thuộc cho local development, dễ dàng mở rộng lên IdP (Auth0, Keycloak) trong tương lai.
- **Database:** Sử dụng SQLite (`auth.db`) qua SQLAlchemy để lưu thông tin.
- **Models:**
  - `User`: id, email, hashed_password, tenant_id, role.
  - `Tenant`: id, name, description.
- **Endpoints:**
  - `POST /auth/login`: Xác thực và lấy JWT Token.
  - `POST /auth/register`: Đăng ký User và tạo Tenant mới.
  - `GET /auth/me`: Lấy thông tin current user.

### 2. Multi-tenancy (Đa khách hàng) & RBAC
- Mỗi User sẽ thuộc về một Tenant duy nhất (hoặc là System Admin).
- **GraphDB (Neo4j):**
  - Mọi Node tạo ra thông qua Ingestion đều phải được gán property `tenant_id`.
  - Mọi Cypher query (`MATCH (n) ...`) trong hệ thống (Search, Reason, Context) đều phải bổ sung điều kiện lọc theo `tenant_id`.
- **VectorDB (Qdrant):**
  - Mọi payload được insert đều kẹp thêm trường `tenant_id`.
  - Mọi Vector Search Query đều phải có `Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])`.
  
### 3. CLI Integration
- CLI (aiekp-cli) sẽ được bổ sung module authentication.
- Lệnh `aiekp auth login` sẽ gọi API, lấy JWT Token và lưu vào `~/.aiekp/auth.json`.
- Các lệnh thao tác với API (`aiekp ingest`, `aiekp eval`) sẽ đính kèm Token trong header `Authorization: Bearer <token>`.
- Token này chứa `tenant_id` của user, backend API sẽ tự động trích xuất `tenant_id` và cô lập luồng dữ liệu cho đúng Tenant đó.

## Công nghệ & Thư viện bổ sung
- `pyjwt` (hoặc `python-jose`): Tạo và verify JWT Token.
- `passlib[bcrypt]`: Hashing mật khẩu an toàn.
- `fastapi.security`: Sử dụng OAuth2PasswordBearer.
