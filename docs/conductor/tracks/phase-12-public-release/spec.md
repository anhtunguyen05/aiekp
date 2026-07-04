# Phase 12: Alpha Public Release & Cloud DB Integration

## 1. Objective
Chuyển đổi AIEKP từ một công cụ chạy nội bộ bằng mã nguồn (qua `uv run`) thành một sản phẩm có thể phân phối công khai qua PyPI (`pip install aiekp-cli`). Để làm được điều này, hệ thống cần hỗ trợ cấu hình toàn cục (Global Configuration) cho phép người dùng nhập API Key (LLM) và kết nối tới các dịch vụ Database trên Cloud (Neo4j Aura, Qdrant Cloud) thay vì bắt buộc dùng Docker cục bộ.

## 2. Core Requirements
- **Global Config**: Người dùng có thể cấu hình thông qua CLI (ví dụ: `aiekp config set NEO4J_URI <uri>`). Cấu hình này được lưu tại `~/.aiekp/config.json`.
- **Backward Compatibility**: Hệ thống vẫn hỗ trợ đọc từ file `.env` cục bộ nếu người dùng muốn chạy trong dự án cụ thể, nhưng ưu tiên nạp từ Global Config nếu `.env` không chứa thông tin.
- **Cloud Database Support**: Đảm bảo các kết nối Neo4j, Qdrant và Postgres hỗ trợ remote URI (ví dụ: `neo4j+s://`).
- **Packaging**: Dự án phải được cấu hình bằng `pyproject.toml` (với Hatchling) để có thể build thành `.whl` và đẩy lên PyPI qua Twine.
- **Documentation**: Cập nhật `README.md` hướng dẫn chi tiết cách cài đặt qua `pip` và cấu hình hệ thống bằng Cloud DB.

## 3. Architecture Changes

### 3.1. Config Manager Module (`aiekp_cli/config_manager.py`)
- Lớp Singleton hoặc các hàm tiện ích để đọc/ghi file `~/.aiekp/config.json`.
- Các hằng số (Keys):
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
  - `QDRANT_URL`, `QDRANT_API_KEY`
  - `OPENAI_API_KEY`, `GEMINI_API_KEY`

### 3.2. CLI Command Updates (`aiekp_cli/main.py`)
- `aiekp config set <key> <value>`: Ghi đè hoặc thêm một cấu hình mới.
- `aiekp config list`: Hiển thị danh sách các cấu hình hiện tại (sẽ che dấu mật khẩu hoặc API Key bằng `***`).

### 3.3. Database Adapters & API Server
- Các engine (`packages/graph-engine`, `packages/context-engine`) cần cập nhật cơ chế nạp biến môi trường.
- `os.environ` sẽ được nạp bổ sung từ file `~/.aiekp/config.json` khi khởi động ứng dụng (hoặc qua một Dependency Injection layer).

### 3.4. Release Pipeline
- Bổ sung script `scripts/release.sh` để tự động:
  - Chạy format & linting (`ruff`).
  - Build package (`uv build`).
  - Upload lên PyPI (`twine upload dist/*`).

## 4. Verification
1. Lệnh `aiekp config set` hoạt động và sinh ra file `~/.aiekp/config.json` đúng định dạng.
2. Quá trình Ingestion và Reasoning có thể hoạt động hoàn toàn dựa trên thông tin lấy từ file config mà không cần file `.env`.
3. Package `.whl` được build thành công, khi cài đặt vào một venv trống có thể gọi lệnh `aiekp` trực tiếp từ command line.
