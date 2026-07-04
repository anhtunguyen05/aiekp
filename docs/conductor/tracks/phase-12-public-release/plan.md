# Phase 12: Implementation Plan

- [ ] **Step 1: Xây dựng Config Manager**
  - Tạo `apps/cli/src/aiekp_cli/config_manager.py`.
  - Viết các hàm `read_config()`, `write_config(key, value)` xử lý file `~/.aiekp/config.json`.

- [ ] **Step 2: Tích hợp lệnh `aiekp config` vào CLI**
  - Thêm command group `config` vào `apps/cli/src/aiekp_cli/main.py`.
  - Cài đặt `aiekp config set` và `aiekp config list`.

- [ ] **Step 3: Cập nhật cơ chế nạp cấu hình toàn cục**
  - Chỉnh sửa file `apps/api/src/main.py` và các module khởi tạo Engine để tự động nạp các biến từ `config.json` vào `os.environ` hoặc sử dụng trực tiếp nếu file `.env` không có.

- [ ] **Step 4: Cập nhật cấu hình Packaging (PyPI)**
  - Chỉnh sửa `apps/cli/pyproject.toml` (và root `pyproject.toml` nếu cần).
  - Khai báo phiên bản, tác giả, mô tả, và điểm neo (entry points) cho lệnh `aiekp`.

- [ ] **Step 5: Viết script Release và cập nhật README**
  - Tạo `scripts/release.sh`.
  - Cập nhật `README.md` với các hướng dẫn cài đặt từ PyPI và cấu hình Cloud DB.

- [ ] **Step 6: Kiểm thử cục bộ (Build & Install)**
  - Chạy `uv build` và cài đặt file `.whl` vào một môi trường ảo để test.
