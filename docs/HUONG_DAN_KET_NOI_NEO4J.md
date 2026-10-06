# Kết nối Neo4j — trạng thái hiện tại

Phase 2 đã kết nối và kiểm thử thành công với Neo4j Enterprise 2026.09.0, database riêng `quadrilateral`, dataset `quadrilateral-v1`.

Ở lần kiểm tra trước Desktop đã cài nhưng server chưa chạy. Ở lần tiếp tục, server đã mở 7474/7687; thư mục project chỉ có .env.example nên đã tạo .env cục bộ bằng thông tin người dùng cung cấp trong ảnh và xác thực thành công. Không hiển thị/ghi mật khẩu vào source hoặc báo cáo. .env đã được .gitignore loại khỏi Git.

Ban đầu instance có neo4j và system. Đã tạo thêm database quadrilateral dành riêng cho bài tập; không xóa/sửa dữ liệu ở database khác.

Đã tạo schema, seed hai lần, chạy 20 validation và đối chiếu 15 query. Kết quả thật: **44 node, 79 relationship; 20/20 validation và 15/15 query PASS; idempotent PASS**.

- Báo cáo dễ đọc: [BAO_CAO_PHASE_2.md](BAO_CAO_PHASE_2.md).
- Kết quả chi tiết: [PHASE_2_RESULTS.json](PHASE_2_RESULTS.json).
- Lệnh chạy lại: [database/README.md](../database/README.md).

## Mở và xem dữ liệu

1. Giữ instance Running trong Neo4j Desktop 2.
2. Mở Connect → Query, chọn database quadrilateral.
3. Khai báo `:params {dataset:'quadrilateral-v1', shape_id:'HV', depth:3}`.
4. Chạy từng query trong database/demo_queries.cypher. Q01 hiển thị toàn bộ graph; Q09/Q15 hiển thị đường phân loại và đường giải thích tính chất.

Desktop 2 dùng Query tích hợp làm công cụ Browser. Khi đổi máy, tạo database riêng và .env theo .env.example, sau đó chạy hướng dẫn Phase 2 trong database/README.md.

Chưa triển khai Flask/frontend. Không cần cài lại Desktop, reset database, hoặc import dữ liệu mẫu ngoài project.

Tài liệu chính thức: https://neo4j.com/docs/desktop/current/operations/database-management/ và https://neo4j.com/docs/browser/deployment-modes/neo4j-desktop/.
