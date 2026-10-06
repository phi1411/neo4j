# Báo cáo Phase 4 — Frontend và trực quan hoá graph

**Trạng thái: PASS.** Kiểm tra cuối: 2026-10-06T23:39:17.741507+07:00.

Ứng dụng chạy thật tại http://127.0.0.1:5000. Neo4j database `quadrilateral`, dataset `quadrilateral-v1`. Không seed, migration, xóa dữ liệu hoặc đổi taxonomy trong Phase 4. Chưa tạo tài liệu Word cuối kỳ hoặc đưa source lên GitHub.

## 1. Phạm vi và thay đổi backend

Đọc tài liệu Phase 1/2/3, dataset/kỳ vọng, Cypher và source backend trước khi triển khai. Kiểm tra HTTP thật health/stats/shapes/HV/taxonomy thành công trước khi code.

Thêm `app/routes/web.py` và đăng ký blueprint web trong `app/__init__.py`. Không sửa API, service, serializer, Cypher, schema hoặc dataset. Web routes trả layout Jinja, dữ liệu tri thức lấy bằng JavaScript qua API hiện có.

Trang query lấy **mã nguồn** Cypher bằng Jinja từ chính whitelist của QueryService để có thể đọc lệnh trước khi bấm chạy. Không chạy query ngầm để lấy mã và không có kết quả giả trong HTML. Danh mục/schema tham số vẫn lấy `/api/queries`; thực thi vẫn qua POST `/api/queries/<id>` với JSON tham số. Không có ô nhập Cypher tự do; hợp đồng Phase 3 giữ nguyên.

## 2. Các trang đã triển khai

| Trang | Nội dung và API |
|---|---|
| `/` | Tên đề tài đầy đủ; 5 card thống kê từ `/api/stats`; graph `/api/graph/taxonomy`; giải thích đa kế thừa, tính chất dùng chung, traversal và đường đi |
| `/shapes` | Danh sách từ `/api/shapes`; tìm kiếm `/api/search`; hỗ trợ tiếng Việt có dấu/không dấu/hoa thường; empty/error/loading state |
| `/shapes/<id>` | `/api/shapes/<id>`: định nghĩa, cha/tổ tiên, nhóm tính chất, direct/inherited, nguồn khai báo, đường kế thừa; Condition AND/OR; graph neighborhood depth 1–3 |
| `/graph` | Danh sách hình từ API; mặc định HV/depth 1; tải `/api/graph/neighborhood/<id>`; nút taxonomy, fit, zoom/pan, thông tin node và relationship |
| `/queries` | Q01–Q15: mục đích, cách đọc kết quả, Cypher, tham số theo schema; bảng kết quả và graph nếu API trả node/path |
| `/about` | Mục tiêu, mô hình, quy ước hình thang loại trừ, cơ chế kế thừa, AND/OR, kiến trúc và giới hạn |

Navbar/footer thống nhất, Unicode tiếng Việt, nền sáng, form/card responsive. Tất cả trang kiểm tra health; nút trạng thái cho phép kiểm tra lại kết nối.

Dữ liệu API dùng fetch `cache: no-store`. Khi thực hiện thao tác mới, xóa kết quả cũ; bỏ qua response đến muộn nếu người dùng đã đổi lựa chọn. Khi mất kết nối, báo lỗi, không dùng fallback. Các thông tin đã đọc trên một trang là kết quả của lần đọc đó; không có cơ chế đồng bộ thời gian thực ngầm.

## 3. Graph visualization

- vis-network **10.1.2** standalone local, kèm CSS, LICENSE-MIT, LICENSE-APACHE-2.0 và manifest SHA-256. Không có CDN/font ngoài; demo cần Flask và Neo4j, không cần internet.
- ID, nhãn, loại, nguồn/đích và mũi tên lấy từ JSON API. Không có tọa độ hard-code hoặc graph tĩnh trong JavaScript.
- Shape: ô xanh dương; Property: oval xanh lá; Condition: hình thoi vàng. Nhãn Condition rút gọn theo ID nghiệp vụ; tooltip và inspector giữ tên/nội dung đầy đủ.
- Taxonomy dùng layout phân cấp tự động; graph khác ổn định bố cục rồi tắt physics. Graph được hiện khi bố cục ban đầu ổn định để tránh chuyển động gây rối.
- Node/cạnh có thể bấm. Node có dropdown bổ sung để dùng bằng bàn phím. Tooltip, legend, zoom, pan và Vừa khung được kiểm tra trên canvas thật.
- Khi thay kích thước, căn graph sau khi canvas cập nhật ở animation frame kế tiếp. Không dùng transform của khung cũ.

Không tuyên bố Neo4j luôn nhanh hơn SQL. Ứng dụng minh hoạ truy vấn quan hệ và đường đi, chưa đo hiệu năng so sánh.

## 4. Kết quả kiểm thử

| Nhóm | Kết quả thật |
|---|---|
| Pytest backend | **91/91 PASS**, không fail/skip; gồm 69 integration và 22 unit test Phase 3 |
| Đối chiếu trình duyệt | **121 kiểm tra PASS**; thao tác trên ứng dụng thật qua Flask/Neo4j, không mock kết quả thành công |
| Truy vấn từ UI | **15/15 PASS**, so tập ID, đường đi, degree hoặc số node/cạnh với expected_results.json |
| Validation Phase 2 | **20/20 PASS**, mọi violations=0 |
| Query trực tiếp Phase 2 | **15/15 PASS**, chạy lại bằng Neo4j Driver thật |
| HTTP sau triển khai | 6 trang và health/stats đều HTTP 200 |
| Console | Không ghi nhận lỗi JavaScript ngoài dự kiến trong các lần kiểm tra chính |
| Responsive | 1280×900 và 390×844; không tràn ngang toàn trang; bảng có vùng cuộn riêng; Q02 mobile có 12 dòng |
| Thư viện local | Hash các file khớp manifest |
| Thông tin đăng nhập | Không phát hiện mật khẩu trong source/báo cáo do project tạo; .env/.venv được gitignore |

### Nội dung toán học trên UI

- HV có hai cha HCN, HTHOI; bốn tổ tiên HCN, HTHOI, HBH, TQ; không HT/HTC.
- HV có 12 Property, 0 khai báo trực tiếp; mọi Property có nguồn và đường tới nguồn. Tính chất đường chéo bằng nhau từ HCN, vuông góc từ HTHOI, chia đôi nhau từ HBH.
- Đường tới nguồn HBH qua HCN và HTHOI được giữ riêng, nhưng Property hiệu lực chỉ xuất hiện một lần.
- HV có 5 Condition, 4 dấu OR giữa các quy tắc. C_HV_05 có ngữ cảnh TQ và hai giả thiết AND.
- Các hình khác cũng được kiểm tra: tính chất hiệu lực/trực tiếp TQ 2/2, HT 4/2, HTC 7/3, HBH 7/5, HCN 9/2, HTHOI 10/3.
- Taxonomy: 7 node/7 cạnh. Neighborhood HV: depth 1 = 8/11; depth 2 = 23/43; depth 3 = 39/71 node/cạnh.

### Kết quả 15 query từ UI

| Query | Đối chiếu kết quả |
|---|---|
| Q01 | Graph 44 node/79 relationship |
| Q02 | 12 Property của HV, khớp tập ID expected |
| Q03 | HCN, HTHOI |
| Q04 | HBH, HCN, HTHOI, TQ |
| Q05 | HCN, HTHOI, HV |
| Q06 | HTHOI, HV |
| Q07 | HCN, HV |
| Q08 | HCN, HTC, HV |
| Q09 | Hai đường TQ–HBH–HCN–HV và TQ–HBH–HTHOI–HV |
| Q10 | 9 Property chung HV/HCN |
| Q11 | 10 Property chung HV/HTHOI |
| Q12 | HTHOI, HV; hai tính chất đồng thời |
| Q13 | 7 dòng; mọi cột cạnh vào/ra theo loại khớp expected |
| Q14 | Mặc định depth 3: 39 node/71 cạnh; trang graph thử cả 1/2/3 |
| Q15 | Hai đường HV–HCN–HBH–Property và HV–HTHOI–HBH–Property |

Các ảnh chụp kết quả là ảnh thật; danh sách ở bảng báo cáo là tổng hợp các đối chiếu, không được dùng để cấp dữ liệu cho UI.

### Thử lỗi

- ID không tồn tại: API 404, UI thông báo không tìm thấy và ẩn phần chi tiết.
- ID sai định dạng: API 400, UI vẫn có layout và thông báo tiếng Việt.
- Search không có kết quả: empty state, không giữ card cũ.
- Depth UI chỉ có 1/2/3. Các giá trị/kiểu sai bị API trả 400 và được kiểm tra bằng pytest; không sửa DOM để ép một giá trị ngoài dropdown.
- Mất Neo4j: chạy app Flask riêng cổng 5001 với driver thật tới cổng cục bộ không lắng nghe. Health/stats/graph trả 503, UI báo lỗi và không có số liệu/graph thay thế. Không tắt Neo4j chính.
- Flask ngừng chạy: dừng server phụ rồi bấm kiểm tra kết nối trên trang đã mở; UI báo không liên lạc được Flask. Server chính 5000 vẫn chạy; server phụ đã dừng.

## 5. Bảo toàn database

Thực tế sau Phase 4: **44 node**, **79 relationship**. Dataset và graph ngoài dataset đều không đổi so với baseline Phase 3.

SHA-256 dataset trước/sau:

`bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8`

Không chạy seed/schema/migration hoặc bất kỳ Cypher ghi nào. Source dữ liệu/schema/query Phase 2 giữ nguyên; hợp đồng API và test Phase 3 không thay đổi.

## 6. File tạo/sửa

### File tạo

- `app/routes/web.py`
- `app/templates/base.html`, `_graph.html`, `dashboard.html`, `shapes.html`, `detail.html`, `graph.html`, `queries.html`, `about.html`
- `app/static/css/app.css`
- `app/static/js/app.js`, `graph.js`
- `app/static/favicon.svg`
- `app/static/vendor/vis-network/vis-network.min.js`, `vis-network.min.css`, `LICENSE-MIT`, `LICENSE-APACHE-2.0`, `manifest.json`
- `scripts/fault_preview.py`, `scripts/review_phase4.py`
- `docs/PHASE_4_UI_RESULTS.json`, `PHASE_4_PYTEST.xml`, `PHASE_4_RESULTS.json`, `PHASE_4_TEST_CHECKLIST.md`, `BAO_CAO_PHASE_4.md`
- Ảnh JPEG trong `docs/images/` (danh sách bên dưới).

### File sửa

- `app/__init__.py`: đăng ký blueprint web; không sửa logic API/service/driver.
- `README.md`: cập nhật giao diện, kiến trúc, dependency local, cách demo/test và ảnh thật.

Không thêm thư viện Python hoặc sửa requirements trong Phase 4.

## 7. Screenshot thật

Đã lưu **17 ảnh** từ trình duyệt chạy ứng dụng. JPEG là định dạng native của công cụ chụp. Không sinh ảnh AI, mockup hoặc ghép ảnh để tạo kết quả. Các graph được chụp ở khung nhìn thật sau khi căn lại; một số trang không có canvas dùng ảnh toàn trang.

- `docs/images/01_dashboard.jpg`
- `docs/images/02_taxonomy_graph.jpg`
- `docs/images/03_shapes.jpg`
- `docs/images/04_shape_hv.jpg`
- `docs/images/05_hv_properties.jpg`
- `docs/images/06_hv_conditions.jpg`
- `docs/images/07_graph_depth1.jpg`
- `docs/images/08_graph_depth2.jpg`
- `docs/images/08_graph_depth3.jpg`
- `docs/images/09_queries.jpg`
- `docs/images/10_query_result.jpg`
- `docs/images/10_query_table.jpg`
- `docs/images/11_mobile_about.jpg`
- `docs/images/11_mobile_graph.jpg`
- `docs/images/11_mobile_query.jpg`
- `docs/images/12_neo4j_unavailable.jpg`
- `docs/images/13_flask_unavailable.jpg`

Ảnh lỗi cổng 5001 ghi lại ứng dụng kiểm thử mất kết nối; không phải trạng thái server chính sau hoàn tất. Chưa chụp Neo4j Browser trong Phase 4, chưa chèn ảnh vào DOCX.

## 8. Lỗi phát hiện và sửa

- Lần mở trực tiếp localhost bằng công cụ browser bị chặn. Mở app qua panel Codex rồi gắn vào tab đó và tải lại: truy cập app thật thành công; không dùng ảnh giả thay thế.
- Canvas bị phóng quá lớn khi khung đổi kích thước trong thao tác chụp toàn trang. Chuyển căn khung sang frame sau resize, thử desktop/mobile không reload; chụp lại graph ở viewport ổn định và xem lại ảnh lưu.
- Nhãn Condition dài làm graph khó đọc: rút gọn nhãn trên canvas theo ID, giữ nội dung đầy đủ khi hover/click.
- Điều chỉnh script đối chiếu trình duyệt theo **tên cột**, vì JSON Flask sắp xếp khóa và thứ tự cột có thể khác thứ tự khai báo Cypher. Đây là sửa cách kiểm tra; không thay dữ liệu hoặc query để khớp một kỳ vọng sai.
- Các locator kiểm thử được sửa để dùng đúng ID/selector đã quan sát; không thay UI/data để né lỗi kiểm thử. Không có test backend fail/skip ở lần chạy cuối.

## 9. Còn lại cho Phase 5 và các phase sau

Phase 5: nghiệm thu toàn hệ thống theo `PHASE_4_TEST_CHECKLIST.md`, thử cài/chạy từ source trên môi trường sạch, rà soát luồng demo và quá trình phục hồi sau mất kết nối. Neo4j mất kết nối đã được thử bằng cổng phụ; kiểm thử dừng/khởi động lại instance chính trong buổi nghiệm thu cần bảo toàn dữ liệu.

Phase 6: hoàn thiện README nộp môn học, tài liệu tổng quan/hướng dẫn DOCX, thêm ảnh Neo4j Browser thật và chèn ảnh app; chuẩn bị GitHub Data + Source. Phase 7: rà checklist toàn bộ, kiểm tra không có credential trong Git trước khi đưa lên GitHub.

Bằng chứng: `PHASE_4_UI_RESULTS.json` (đối chiếu browser), `PHASE_4_PYTEST.xml` (pytest), `PHASE_4_RESULTS.json` (review Neo4j/HTTP/hash). Cách kiểm thử lại: `PHASE_4_TEST_CHECKLIST.md` và README.
