# Data và Cypher — Phase 2

Dataset `quadrilateral-v1`, database riêng `quadrilateral`. Hình thang dùng quy ước đúng một cặp cạnh đối song song. Taxonomy và kỳ vọng xem `docs/PHASE_1_PHAN_TICH.md`.

## File dữ liệu

- `shapes.json`: bảy loại hình, định nghĩa và tên tìm kiếm.
- `properties.json`: 19 mệnh đề, nhóm, ký hiệu, mô tả và nguồn tham khảo.
- `conditions.json`: 18 quy tắc; target/context/properties dùng tạo relationship, không sao chép thành thuộc tính node. AND trong quy tắc, OR giữa các quy tắc.
- `relationships.json`: bảy cạnh IS_A và 17 khai báo HAS_PROPERTY.
- `seed.cypher`: Cypher độc lập, sinh từ bốn catalog; MERGE theo dataset/id; không xóa dữ liệu.
- `constraints.cypher`: ba uniqueness constraints composite `(dataset,id)`.
- `indexes.cypher`: index composite `(dataset,search_name)`; không trùng backing index của constraints.
- `demo_queries.cypher`: 15 truy vấn, giải thích và kỳ vọng.
- `expected_results.json`: kỳ vọng độc lập cho các tập ID, đường đi, degree và số lượng vùng lân cận.
- `validation.cypher`: 20 kiểm tra chỉ đọc; mọi kết quả phải là `violations=0`.

## Chạy với Python/driver

Tại thư mục gốc, tạo `.env` từ `.env.example` và điền riêng thông tin đăng nhập. Không đưa mật khẩu vào source hay lệnh có log.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/phase2.py connect
.\.venv\Scripts\python.exe scripts/phase2.py schema
.\.venv\Scripts\python.exe scripts/phase2.py build-seed
.\.venv\Scripts\python.exe scripts/phase2.py seed
.\.venv\Scripts\python.exe scripts/phase2.py finish
```

Runner chỉ cho phép database riêng `quadrilateral`, yêu cầu nó đã tồn tại và online. Dùng Neo4j Desktop tạo database trước nếu chưa có. Lần triển khai hiện tại đã tạo database này mà không xóa/sửa các database trước đó.

`seed` ghi snapshot lần đầu; `finish` kiểm tra validation trước khi seed lần hai, so toàn bộ snapshot và chạy cả 15 query. Một lỗi làm chương trình trả exit code khác 0. Không dùng fallback hay dataset giả.

`verify` kiểm tra lại chỉ đọc sau khi đã có báo cáo thành công; không seed lần ba:

```powershell
.\.venv\Scripts\python.exe scripts/phase2.py verify
```

Catalog JSON là nguồn dữ liệu chuẩn. Khi sửa catalog, chạy `build-seed` để cập nhật Cypher và kiểm tra lại kỳ vọng theo toán học. MERGE không xóa cạnh cũ khi taxonomy thay đổi; cần migration riêng có phạm vi cụ thể, không tự reset database.

## Chạy trong Neo4j Query/Browser

Chọn database `quadrilateral`. Chạy các statement của constraints, indexes rồi seed theo thứ tự. Seed không cần tham số vì dataset đã được ghi cố định trong file.

Đối với demo và validation, khai báo tham số trong Query/Browser:

```text
:params {dataset:'quadrilateral-v1', shape_id:'HV', depth:3}
```

Sau đó chạy từng query Q01–Q15 hoặc kiểm tra V01–V20. Đây là lệnh của Query/Browser, không phải Cypher đưa vào driver. Khi dùng Python, runner tự truyền tham số.

Q01/Q09/Q14/Q15 trả node/relationship/path thật để công cụ Neo4j hiển thị graph. Q14 là induced graph trên các node đạt được, không phải taxonomy: depth=1 gồm các cạnh giữa node lân cận nên có 11 cạnh thay vì chỉ bảy cạnh tới HV.

## Bằng chứng kiểm thử

- `docs/seed_first_run.json`: snapshot, hash và counter lần seed đầu.
- `docs/PHASE_2_RESULTS.json`: kết quả thật, schema, counter lần hai, validation, từng query và hash idempotent.
- `docs/BAO_CAO_PHASE_2.md`: báo cáo dễ đọc.

Snapshot không dùng ID nội bộ Neo4j: so label, ID nghiệp vụ, mọi thuộc tính, đầu cạnh, loại cạnh và thuộc tính cạnh. Counter `properties_set` có thể khác 0 ở seed lần hai vì SET được thực hiện lại; idempotent được xác nhận bằng snapshot/hash bằng nhau và không có node/cạnh mới.

Tài liệu này mô tả riêng Phase 2. Cách chạy Flask và giao diện xem README ở thư mục gốc. Các file JSON báo cáo là kết quả truy vấn database thật, không phải mock hay ảnh chụp màn hình.
