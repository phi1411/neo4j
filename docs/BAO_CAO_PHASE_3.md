# Báo cáo Phase 3 — Backend Flask + Neo4j

Thời điểm kiểm tra cuối: **2026-10-06T23:01:14.717565+07:00**, UTC+07:00 (Asia/Bangkok).

**Trạng thái: PASS.** Backend Flask đã chạy thật tại http://127.0.0.1:5000 với debug/reloader tắt. Neo4j Enterprise 2026.09.0; database quadrilateral; dataset quadrilateral-v1. Không làm frontend hoặc tài liệu Word. Không seed, migration hay thay đổi taxonomy.

## 1. Kiểm tra trước khi code

- Đã đọc source và tài liệu Phase 1/2, demo_queries.cypher và expected_results.json. Workspace chưa có Git repository, nên không có git status của repository để báo cáo.
- Kiểm tra kết nối bằng driver thật thành công. Dataset trước Phase 3: 44 node, 79 relationship; hash khớp Phase 2.
- Baseline lưu trong PHASE_3_BASELINE.json. Không in mật khẩu hoặc URI có credential.

## 2. Kiến trúc backend thực tế

Route trong app/routes/api.py → ShapeService/GraphService/QueryService/StatsService → Neo4jDatabase → Neo4j Driver → Neo4j.

- app factory create_app đọc .env/biến môi trường; API dùng dataset cố định, không cho request đổi dataset.
- Một driver cho mỗi app; session riêng theo thao tác, execute_read, transaction timeout; đóng driver khi process kết thúc. Không teardown driver theo request.
- Verify cả instance và database mục tiêu. Khi cấu hình/kết nối lỗi, server vẫn trả health/error JSON thật; không có dữ liệu fallback.
- Cypher nằm trong app/queries. Graph lân cận dùng lại Q14; whitelist dùng trực tiếp 15 statement của database/demo_queries.cypher, không copy query hoặc hard-code kết quả.
- Serialization giữ Node/Relationship/Path từ dict(record), dùng ID label:business_id và quan hệ nguồn/loại/đích, không dùng internal ID.
- Property được DISTINCT theo ID nhưng giữ đủ đường đa kế thừa. AND trong từng Condition; OR giữa các Condition của hình. Không tự kế thừa dấu hiệu nhận biết.

## 3. Endpoint đã triển khai

| Method | Endpoint |
|---|---|
| GET | `/api/graph/neighborhood/<shape_id>` |
| GET | `/api/graph/taxonomy` |
| GET | `/api/health` |
| GET | `/api/queries` |
| GET/POST | `/api/queries/<query_id>` |
| GET | `/api/search` |
| GET | `/api/shapes` |
| GET | `/api/shapes/<shape_id>` |
| GET | `/api/shapes/<shape_id>/ancestors` |
| GET | `/api/shapes/<shape_id>/conditions` |
| GET | `/api/shapes/<shape_id>/properties` |
| GET | `/api/stats` |

JSON thành công dùng success/data; lỗi dùng success=false/error.code/error.message. Health lỗi thêm data cho trạng thái Flask/Neo4j. Có xử lý 400/404/500/503 và HTTP errors chuẩn. Không trả raw exception, stack trace, URI hoặc password. Query POST chỉ nhận object tham số theo schema, không nhận arbitrary Cypher.

## 4. Kết quả pytest

**91/91 PASS**, 0 fail, 0 skip; thời gian trong JUnit khoảng 5.54 giây.

- 69 integration test: truy vấn Neo4j thật, không mock kết quả graph/tính chất/query.
- 22 unit test: chuẩn hóa tiếng Việt, validation kiểu/giá trị, lỗi cấu hình, lỗi xác thực/kết nối và không lộ chẩn đoán nội bộ.
- Integration kiểm tra health/stats/shapes, HV có hai cha/bốn tổ tiên/12 Property, nguồn HCN/HTHOI/HBH/TQ, hai đường kế thừa qua HBH, Condition AND/OR, tìm có dấu/không dấu/hoa thường, taxonomy, neighborhood và đủ 15 query.
- Trường hợp unavailable dùng driver thật tới một cổng cục bộ không có server; API trả 503, không tắt instance Neo4j của project. Lỗi Cypher được thử bằng statement chỉ đọc không hợp lệ và trả lỗi đã lược bỏ chi tiết.
- Thử input chứa MATCH/DETACH DELETE chỉ như chuỗi search hoặc body bị whitelist từ chối; không có lệnh ghi nào được gửi tới database.
- Fixture so hash trước/sau integration, xác nhận test không làm đổi graph.

Bằng chứng: PHASE_3_PYTEST.xml. Lệnh chạy lại:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=docs/PHASE_3_PYTEST.xml
```

## 5. Kết quả HTTP thật

**38/38 PASS**, không chỉ Flask test_client. Server được khởi động bằng Python run.py và script gọi URL thật bằng urllib.

| Kiểm tra | HTTP | Trạng thái |
|---|---:|---|
| health | 200 | PASS |
| stats | 200 | PASS |
| shapes | 200 | PASS |
| square_detail | 200 | PASS |
| properties | 200 | PASS |
| conditions | 200 | PASS |
| ancestors | 200 | PASS |
| search_hinh vuong | 200 | PASS |
| search_Hình vuông | 200 | PASS |
| search_VUONG | 200 | PASS |
| taxonomy | 200 | PASS |
| neighborhood_1 | 200 | PASS |
| neighborhood_2 | 200 | PASS |
| neighborhood_3 | 200 | PASS |
| query_catalog | 200 | PASS |
| Q01 | 200 | PASS |
| Q02 | 200 | PASS |
| Q03 | 200 | PASS |
| Q04 | 200 | PASS |
| Q05 | 200 | PASS |
| Q06 | 200 | PASS |
| Q07 | 200 | PASS |
| Q08 | 200 | PASS |
| Q09 | 200 | PASS |
| Q10 | 200 | PASS |
| Q11 | 200 | PASS |
| Q12 | 200 | PASS |
| Q13 | 200 | PASS |
| Q14 | 200 | PASS |
| Q15 | 200 | PASS |
| query_post | 200 | PASS |
| missing_shape | 404 | PASS |
| missing_query | 404 | PASS |
| depth_0 | 400 | PASS |
| depth_4 | 400 | PASS |
| empty_search | 400 | PASS |
| dataset_override | 400 | PASS |
| arbitrary_cypher_rejected | 400 | PASS |

Có GET tất cả nhóm endpoint, đủ Q01–Q15, POST Q14, search ba cách, depth 1/2/3 và các phản hồi 400/404. Chi tiết URL/phương thức/kết quả và hash response trong PHASE_3_HTTP_RESULTS.json. Không ghi password vào báo cáo.

Lệnh chạy lại khi server đang chạy:

```powershell
.\.venv\Scripts\python.exe scripts/http_smoke.py
```

## 6. Kiểm tra lại Phase 2

- Node thực tế: **44** (7 Shape, 19 Property, 18 Condition).
- Relationship thực tế: **79**.
- Validation: **20/20 PASS**.
- Query Phase 2 chạy trực tiếp lại: **15/15 PASS**.
- Không seed lại, không tạo node/relationship; snapshot dữ liệu ngoài dataset cũng giữ nguyên.

Hash trước: `bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8`

Hash sau: `bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8`

Lệnh review chỉ đọc:

```powershell
.\.venv\Scripts\python.exe scripts/review_phase3.py
```

## 7. Lỗi và xử lý

- Không gặp lỗi runtime trong các lần chạy pytest/HTTP chính thức; không có test bị bỏ qua.
- Các tình huống thiếu .env, unavailable, lỗi truy vấn và lỗi nội bộ được thử có chủ đích; phản hồi đã được kiểm tra để không lộ chi tiết riêng.
- Khi rà soát code, đặt nhánh ConfigurationError trước DriverError để lỗi cấu hình không bị báo nhầm là lỗi kết nối; giới hạn chuỗi số trước int() để tham số dài bất thường trả 400 thay vì lỗi nội bộ. Các nhánh này đã được kiểm thử.
- Không phát hiện lỗi Phase 2 nên không cần migration.

## 8. File tạo mới

- `app/__init__.py`
- `app/config.py`
- `app/db.py`
- `app/errors.py`
- `app/queries/__init__.py`
- `app/queries/ancestors.cypher`
- `app/queries/conditions.cypher`
- `app/queries/parents.cypher`
- `app/queries/properties.cypher`
- `app/queries/search.cypher`
- `app/queries/shape.cypher`
- `app/queries/shapes.cypher`
- `app/queries/stats.cypher`
- `app/queries/taxonomy.cypher`
- `app/routes/__init__.py`
- `app/routes/api.py`
- `app/serialization.py`
- `app/services/__init__.py`
- `app/services/graph_service.py`
- `app/services/query_service.py`
- `app/services/shape_service.py`
- `app/services/stats_service.py`
- `app/validation.py`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_api_integration.py`
- `tests/test_units.py`
- `run.py`
- `pytest.ini`
- `scripts/http_smoke.py`
- `scripts/review_phase3.py`
- `README.md`
- `docs/PHASE_3_BASELINE.json`
- `docs/PHASE_3_HTTP_RESULTS.json`
- `docs/PHASE_3_PYTEST.xml`
- `docs/PHASE_3_RESULTS.json`
- `docs/BAO_CAO_PHASE_3.md`

## 9. File sửa

- `requirements.txt`: thêm Flask==3.1.3 và pytest==9.1.1; giữ neo4j/python-dotenv đang dùng. Các phiên bản đều đã cài và kiểm thử thực tế.
- Các source/schema/dataset/taxonomy của Phase 2 không được sửa trong Phase 3.

## 10. Công việc còn lại cho Phase 4

- Giao diện tiếng Việt: navbar, dashboard thống kê thật, danh sách và chi tiết hình, tìm kiếm.
- Trang 15 query mẫu: hiển thị Cypher, form tham số theo schema, bảng kết quả và graph.
- Trực quan hóa taxonomy/neighborhood bằng graph JSON hiện có; phân màu node, nhãn cạnh, chọn độ sâu 1–3 và xem nguồn kế thừa.
- Trạng thái loading/empty/error để giao diện phản ánh lỗi API thật.
- Kiểm tra tích hợp giao diện trên backend; ảnh chụp thật và Word sẽ thực hiện ở các phase tương ứng, chưa tạo trong Phase 3.

Chi tiết cấu hình, API và lệnh chạy: README.md. Báo cáo tổng hợp máy đọc được: PHASE_3_RESULTS.json.
