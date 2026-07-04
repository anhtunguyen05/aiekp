# AIEKP Release Process

Tài liệu này mô tả quy trình tự động phát hành (Auto Release) gói `aiekp-cli` lên hệ thống PyPI thông qua GitHub Actions.

## 1. Cơ chế hoạt động (CI/CD)

Dự án AIEKP sử dụng **GitHub Actions** để tự động hoá việc build và upload.
- **Workflow file**: `.github/workflows/release.yml`
- **Điều kiện kích hoạt**: Khi một `Tag` mới được tạo trên GitHub và bắt đầu bằng chữ `v` (ví dụ: `v0.1.2`).
- **Xác thực**: Sử dụng GitHub Secret `PYPI_API_TOKEN` chứa API Token của PyPI để cấp quyền tải lên.

## 2. Quy ước đặt tên phiên bản (Versioning)

Dự án tuân thủ chuẩn **Semantic Versioning** (`MAJOR.MINOR.PATCH`).

- **Bản ổn định (Stable)**: `v0.1.2`, `v1.0.0`
- **Bản thử nghiệm (Alpha/Beta)**:
  - Alpha: `v0.1.3-alpha.1` (Tương đương `0.1.3a1` trên PyPI).
  - Beta: `v0.1.3-beta.1` (Tương đương `0.1.3b1` trên PyPI).

## 3. Các bước thực hiện Release một phiên bản mới

Để phát hành một bản mới, lập trình viên thực hiện các bước sau:

### Bước 1: Cập nhật version trong Code
Mở file `apps/cli/pyproject.toml` và sửa thông số `version` thành phiên bản mới nhất.
Ví dụ:
```toml
name = "aiekp-cli"
version = "0.1.2"
```

### Bước 2: Commit thay đổi
Commit sự thay đổi này vào nhánh `main`.
```bash
git add apps/cli/pyproject.toml
git commit -m "chore: bump version to 0.1.2"
git push origin main
```

### Bước 3: Tạo Git Tag và đẩy lên GitHub
Tạo tag đánh dấu phiên bản mới. Chú ý: Tên tag **phải** bắt đầu bằng chữ `v` và khớp với version trong file `pyproject.toml`.

```bash
git tag v0.1.2
git push origin v0.1.2
```

*(Hoặc bạn có thể truy cập giao diện GitHub > Releases > Draft a new release > Gõ tên tag `v0.1.2` > Publish release).*

### Bước 4: Theo dõi quá trình tự động
- Truy cập vào tab **Actions** trên GitHub repository.
- Bạn sẽ thấy workflow **Publish to PyPI** đang chạy.
- Sau khi workflow hoàn tất (khoảng 1 phút), gói tin sẽ có mặt trên PyPI và người dùng có thể tải về bằng lệnh `pip install aiekp-cli` hoặc `uv tool install aiekp-cli`.
