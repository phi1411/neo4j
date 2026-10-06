# Báo cáo Phase 5 — System test / Final QA

**Kết luận: PASS. Dự án đủ điều kiện bắt đầu tài liệu cuối ở Phase 6.** Báo cáo chỉ xác nhận phạm vi nghiệm thu ứng dụng; chưa tạo hai file Word hoặc đưa source lên GitHub.

## 1. Môi trường và phạm vi

- Windows; Python 3.13.5; Neo4j Enterprise 2026.09.0 thật, database `quadrilateral`, dataset `quadrilateral-v1`.
- Flask 3.1.3, neo4j driver 6.4.0, python-dotenv 1.2.4, pytest 9.1.1; vis-network 10.1.2 lưu cục bộ.
- Server chính `http://127.0.0.1:5000`; server môi trường sạch 5002; server thử lỗi 5001. Hai server phụ đã dừng sau kiểm thử.
- Duyệt source, kiểm thử database/HTTP/UI thực tế. Không mock kết quả Neo4j; không dùng ảnh tạo dựng. Không thêm chức năng sản phẩm hoặc thay taxonomy.
- Bằng chứng có thời gian chạy ở từng JSON/XML. Kiểm thử ngày 06/10/2026 và tổng hợp cuối qua ngày 07/10/2026, múi giờ Việt Nam/Thái Lan UTC+7; JSON Phase 5 có thể ghi UTC.

## 2. Database regression và bảo toàn dữ liệu

Kiểm tra **trước seed** đã khớp catalog và hash Phase 2. Sau đó chạy `connect → schema → build-seed → seed → finish` trong bản sao source sạch; `finish` kiểm tra validation trước lần seed thứ hai. Sau toàn bộ HTTP/UI, kiểm tra lại chỉ đọc.

| Hạng mục | Kết quả thật |
|---|---|
| Node | 44 = 7 Shape + 19 Property + 18 Condition |
| Relationship | 79 = 7 IS_A + 17 HAS_PROPERTY + 18 HAS_CONDITION + 18 REQUIRES_SHAPE + 19 REQUIRES_PROPERTY |
| Constraint | 3 uniqueness composite `(dataset,id)` |
| Index của project | 4 ONLINE, gồm 3 backing index của constraint và 1 index tìm kiếm |
| Validation V01–V20 | 20/20 PASS, tất cả `violations=0` |
| Demo Q01–Q15 | 15/15 PASS; so tập ID/đường đi, không chỉ đếm dòng |
| Seed hai lần | Cả hai lần tạo thêm 0 node, 0 cạnh; snapshot toàn bộ giữ nguyên |
| Ngoài dataset | Hash trước/sau giữ nguyên |

Không trùng ID/cạnh, không orphan, không self-loop, không chu trình IS_A, không cạnh nối qua dataset. Không có `HBH → HT` hoặc `HCN → HTC`. Bảy cạnh phân loại khớp đúng Phase 1 đã duyệt. File seed sinh lại trong bản sao giống hệt file gốc; constraints/indexes chạy lại không tạo thêm schema.

Hash dataset trước seed, sau seed và sau UI cùng bằng:

```text
bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8
```

Hash ngoài dataset:

```text
f89e607a3788c8af815b0341b616423832479706a7bfbb80a07ecff0beacb18c
```

Hash được tính trên label, ID nghiệp vụ, toàn bộ thuộc tính node/cạnh và hướng/loại cạnh; không phụ thuộc ID nội bộ Neo4j. `properties_set` ở seed lại khác 0 vì SET được thực thi; idempotent được chứng minh bằng snapshot bằng nhau và không tạo thực thể mới. Không DELETE/DROP/reset database hoặc điều chỉnh dữ liệu để ép hash khớp.

Bằng chứng: [trước seed](PHASE_5_DB_PREFLIGHT.json), [hai lần seed/schema](PHASE_5_SEED_RESULTS.json), [sau toàn bộ kiểm thử](PHASE_5_DB_POSTFLIGHT.json).

## 3. Kết quả 15 query thực tế

Tham số mặc định HV; Q14 kiểm tra riêng cả ba độ sâu.

| Query | Kết quả khớp expected | Kết luận |
|---|---|---|
| Q01 | 1 dòng chứa graph 44 node/79 cạnh | PASS |
| Q02 | 12 Property hiệu lực của HV, nguồn khai báo đúng | PASS |
| Q03 | HCN, HTHOI | PASS |
| Q04 | HBH, HCN, HTHOI, TQ; không HT/HTC | PASS |
| Q05 | HCN, HTHOI, HV | PASS |
| Q06 | HTHOI, HV | PASS |
| Q07 | HCN, HV | PASS |
| Q08 | HCN, HTC, HV | PASS |
| Q09 | TQ→HBH→HCN→HV và TQ→HBH→HTHOI→HV; mỗi đường 3 cạnh | PASS |
| Q10 | 9 Property chung của HV và HCN | PASS |
| Q11 | 10 Property chung của HV và HTHOI | PASS |
| Q12 | HTHOI, HV đồng thời có đường chéo vuông góc và chia đôi nhau | PASS |
| Q13 | 7 dòng thống kê theo hình; từng cột degree/loại/chiều khớp expected | PASS |
| Q14 | Depth 1: 8/11; depth 2: 23/43; depth 3: 39/71 node/cạnh | PASS |
| Q15 | HV→HCN→HBH→DIAGONALS_BISECT_EACH_OTHER và HV→HTHOI→HBH→DIAGONALS_BISECT_EACH_OTHER | PASS |

Chi tiết từng kết quả và kiểm tra tập node/cạnh nằm trong DB_POSTFLIGHT và SEED_RESULTS. Q06/Q07/Q08/Q09/Q15 còn được chạy bằng nút trên UI và so dữ liệu bảng với expected. Trong Neo4j Browser, truy vấn chỉ đọc bốn cạnh bằng nhau cũng trả HTHOI/HV.

## 4. Backend và HTTP

**92/92 pytest PASS; 0 fail, 0 error, 0 skip.** Gồm 69 integration đọc Neo4j thật, 22 unit có sẵn và 1 unit mới kiểm tra che nội dung lỗi CLI. Bộ test kiểm tra hash trước/sau để xác nhận không ghi dataset.

**41 kiểm tra HTTP thật trên server chính PASS**, gồm toàn bộ endpoint bắt buộc, tất cả 15 query, POST Q14 và lỗi đầu vào. Response thành công thống nhất `success/data`; lỗi có `success=false` và `error.code/message`. Health lỗi vẫn ghi Flask đang chạy.

**8 kiểm tra HTTP bổ sung PASS:** search khoảng trắng trả 400; ký tự lạ/từ không tồn tại trả danh sách rỗng; health/stats/shape/taxonomy/query của server lỗi trả 503. Server lỗi dùng driver thật tới socket không listen, giữ socket trong thời gian chạy. Không tắt instance Neo4j của dự án.

Hình không tồn tại/query ngoài whitelist trả 404; depth 0/4 trả 400. Không trả traceback hoặc cấu hình đăng nhập. Truy vấn tự do và ghi đè dataset bị từ chối. Kiểm thử injection chỉ truyền chuỗi tìm kiếm làm tham số; không thực thi Cypher người dùng.

Bằng chứng: [pytest](PHASE_5_PYTEST.xml), [HTTP chính](PHASE_5_HTTP_RESULTS.json), [HTTP lỗi/tìm kiếm](PHASE_5_ERROR_HTTP.json).

## 5. Frontend, dữ liệu và Condition

**78 kiểm tra trình duyệt PASS.** Mở ứng dụng thật và dùng controls/link/nút thật trên `/`, `/shapes`, `/shapes/HV`, `/graph`, `/queries`.

| Luồng | Quan sát |
|---|---|
| A: Dashboard → chọn HV trong graph → chi tiết → properties → graph | Đúng trang, 12 tính chất và graph detail 8/11 |
| B: Search `hinh vuong` → HV → chi tiết | Danh sách chỉ có HV; link mở đúng chi tiết |
| C: Graph HV depth 1 → 2 → 3 | 8/11 → 23/43 → 39/71, có canvas sau ổn định |
| D: Q06/Q07/Q08/Q09/Q15 | Kết quả bảng khớp; Q09/Q15 có graph; đổi query xóa kết quả trước |

Đối chiếu UI với response từ Neo4j thật đã được kiểm thử trực tiếp:

- Cha HV: HCN và HTHOI; tổ tiên: HCN, HTHOI, HBH, TQ; không HT/HTC.
- 12 Property duy nhất, nguồn của từng Property khớp database.
- DIAGONALS_EQUAL từ HCN; DIAGONALS_PERPENDICULAR từ HTHOI; DIAGONALS_BISECT_EACH_OTHER từ HBH.
- Hai đường kế thừa tới tính chất chia đôi đường chéo được hiển thị riêng.
- Năm Condition độc lập, bốn dấu OR ngăn giữa chúng. Mỗi Condition hiển thị ngữ cảnh AND từng Property. C_HV_01 là HCN AND ADJACENT_SIDES_EQUAL; C_HV_05 là TQ AND FOUR_EQUAL_SIDES AND FOUR_RIGHT_ANGLES. Không gộp giả thiết của các quy tắc.

Search trên UI đã thử cả `Hình vuông`, `hình vuông`, `hinh vuong`, `HINH VUONG`, `VUONG`, `vuong`: đều chỉ HV. Search rỗng/khoảng trắng ở UI được hiểu là xem tất cả 7 hình; API search rỗng trả 400 theo hợp đồng. Ký tự lạ/từ không tồn tại trả trạng thái không tìm thấy, không crash. Trang hình không tồn tại có thông báo và không hiển thị dữ liệu cũ.

Bằng chứng: [quan sát UI](PHASE_5_UI_RESULTS.json). Không dùng file UI_RESULTS Phase 4 để thay thế kiểm thử lần này.

## 6. Graph và console

- Taxonomy 7 node/7 cạnh; đúng đa kế thừa HV. Mũi tên theo IS_A từ hình đặc biệt tới tổng quát, nhãn relationship đọc được.
- Neighborhood khớp tập node/cạnh Q14 đã kiểm thử bằng driver; UI có đúng số lượng và không trùng ID trong node picker. Validation V02 xác nhận không trùng cạnh; serializer gộp ID nghiệp vụ.
- Bấm trực tiếp HV và cạnh IS_A trên canvas mở đúng inspector. Tooltip HV xuất hiện với nội dung thật. Chọn Property trong danh sách mở đúng thông tin.
- Legend phân biệt Shape/Property/Condition; nút Vừa khung hoạt động.
- Thử viewport 1280×900 → 390×844 → 1280×900; trang graph không tràn ngang, canvas và inspector hoạt động. Trả viewport về kích thước mặc định khi kết thúc.
- Không ghi nhận error/warn console bất thường trong các luồng bình thường. HTTP 400/404/503 ở ca lỗi được chủ động tạo và kiểm tra riêng, không dùng để kết luận lỗi sản phẩm.
- Hash bốn file vendor/giấy phép vis-network khớp manifest; ứng dụng không cần CDN lúc demo.

## 7. Source, bảo mật và môi trường sạch

Đã xem backend/service/query/template/JavaScript/CSS, scripts, tests, catalog, seed, validation và tài liệu cài đặt. Không tìm thấy TODO/FIXME, debug bật hoặc `console.log` trong source riêng. Các `print` còn lại trong runner là tiến độ và kết quả kiểm thử có chủ đích. Không có đường dẫn máy cố định trong source/tài liệu công khai; đường dẫn runtime dựa trên `Path(__file__)`.

Quét source/báo cáo công khai không có mật khẩu Neo4j thật. URI thực tế không nhúng user/password. `.env.example` không chứa mật khẩu. `.env`, `.venv`, cache và `.qa` được bỏ qua Git; thử `git check-ignore` trong Git repo riêng của bản sao với năm nhóm đều PASS. Mã/tài liệu không ghi dump database nhạy cảm. Ảnh chụp không có trường mật khẩu.

Thư mục gốc **chưa là Git repository**, vì vậy không có danh sách commit/remote để xác nhận. Không khởi tạo Git ở gốc hoặc công bố source trong Phase 5. Việc kiểm tra lại staging/commit trước khi đưa lên GitHub vẫn là bước cần làm lúc xuất bản.

Mô phỏng clone bằng source copy không kèm venv/cache cũ. Tạo venv mới, chỉ cài `requirements.txt`, `pip check` đạt. Tạo `.env` từ example và điền cấu hình riêng; chạy schema/seed/finish thật, pytest 92 PASS, HTTP 41 PASS. Server 5002 mở bằng browser: dashboard kết nối, chi tiết HV có 12 tính chất và graph đúng, không lỗi console.

Giới hạn fresh-start: dùng database đã có sau khi kiểm tra hash; không reset hoặc tạo database trống. Không có remote nên chưa kiểm thử `git clone` qua mạng. README đã bổ sung đầy đủ trình tự clone → venv → install → example/env → tạo database → seed → run, với URL GitHub được ghi rõ là placeholder.

Bằng chứng: [fresh-start](PHASE_5_FRESH_START.json), [pytest mới](PHASE_5_FRESH_PYTEST.xml), [HTTP mới](PHASE_5_FRESH_HTTP_RESULTS.json), [source audit](PHASE_5_AUDIT.json).

## 8. Lỗi phát hiện, sửa và kiểm thử lại

| Vấn đề | Nguyên nhân và file | Cách sửa | Kiểm tra lại |
|---|---|---|---|
| CLI có thể ghi chẩn đoán riêng vào log khi lỗi | `scripts/phase2.py`, `scripts/http_smoke.py` đưa nguyên văn exception ra stderr | Chỉ ghi tên loại lỗi và hướng dẫn chung; Phase 2 dùng `report_failure` | Unit mới truyền exception có thông tin riêng, xác nhận không xuất hiện; toàn bộ 92 pytest và CLI Phase 2 chạy thật PASS |
| HTTP runner chỉ có tên báo cáo Phase 3 cố định | `scripts/http_smoke.py` chưa cho chọn output | Thêm `--report`; giữ bằng chứng Phase 2–4, dùng file riêng Phase 5 | 41 HTTP chính và 41 HTTP fresh đều có report riêng PASS |
| Hướng dẫn source mới chưa đủ bước seed trước chạy web; trạng thái tài liệu database cũ | `README.md`, `database/README.md` giả định database đã seed và còn câu chưa có frontend | Bổ sung full fresh-start, làm rõ instance/database và cập nhật trạng thái | Thực hiện thứ tự bằng bản sao source/venv mới, server thật PASS |

Trong quá trình viết công cụ audit Phase 5, mẫu đường dẫn ban đầu tự khớp chuỗi mẫu của chính script. Đã sửa sang regex tổng quát cho đường dẫn Windows và chạy lại thành công. Đây là lỗi của công cụ kiểm tra mới, không phải phụ thuộc đường dẫn của ứng dụng.

Không phát hiện lỗi nghiêm trọng còn lại của database/backend/frontend trong phạm vi đã thử. Không thay source Flask/frontend hay dữ liệu để che lỗi.

**Hạn chế dọn tạm:** duyệt tự động chặn xóa đệ quy `.qa`, sau đó cũng chặn xóa riêng các bản sao đăng nhập, với thông báo “blocked by policy”. Không dùng công cụ khác để vượt chặn. Môi trường kiểm thử và bản sao cấu hình còn ở `.qa`, đã được loại khỏi Git. Không đóng gói thư mục này khi gửi source; người dùng có thể dọn thủ công khi không cần. Server phụ đã dừng; `.env` gốc không sửa.

## 9. Ảnh thật

21 ảnh JPEG nguyên bản từ trình duyệt, không chuyển định dạng để giả thành PNG, không vẽ lại hoặc chỉnh dữ liệu trên ảnh. SHA-256 từng ảnh nằm trong PHASE_5_RESULTS.json.

| Ảnh | Nội dung |
|---|---|
| [01_dashboard](images/phase5/01_dashboard.jpg) | Dashboard kết nối, thống kê 44/79 |
| [02_taxonomy_graph](images/phase5/02_taxonomy_graph.jpg) | Taxonomy của ứng dụng |
| [03_shapes](images/phase5/03_shapes.jpg) | Danh sách loại hình |
| [04_shape_hv_overview](images/phase5/04_shape_hv_overview.jpg) | Chi tiết và phân loại HV |
| [05_shape_hv_properties](images/phase5/05_shape_hv_properties.jpg) | Nguồn và hai đường kế thừa tính chất |
| [06_shape_hv_conditions](images/phase5/06_shape_hv_conditions.jpg) | AND trong quy tắc, OR giữa quy tắc |
| [07_graph_depth1](images/phase5/07_graph_depth1.jpg) | 8/11 |
| [08_graph_depth2](images/phase5/08_graph_depth2.jpg), [depth3](images/phase5/08_graph_depth3.jpg) | 23/43, 39/71 |
| [09_queries_list](images/phase5/09_queries_list.jpg) | Danh mục và Cypher |
| [10_query_Q06](images/phase5/10_query_Q06.jpg) | HTHOI, HV |
| [11_query_Q09](images/phase5/11_query_Q09.jpg) | Hai đường phân loại |
| [12_query_Q15](images/phase5/12_query_Q15.jpg), [graph](images/phase5/12_query_Q15_graph.jpg) | Hai đường tới nguồn khai báo |
| [13_neo4j_graph](images/phase5/13_neo4j_graph.jpg) | Neo4j Browser thật, database quadrilateral, 7 node/7 IS_A |
| [14_neo4j_query](images/phase5/14_neo4j_query.jpg) | Neo4j Browser thật, kết quả HTHOI/HV |
| [15_graph_tooltip](images/phase5/15_graph_tooltip.jpg) | Tooltip và inspector HV |
| [16_mobile_graph](images/phase5/16_mobile_graph.jpg) | Graph trên viewport hẹp |
| [17_neo4j_unavailable](images/phase5/17_neo4j_unavailable.jpg) | Ca lỗi driver thật an toàn |
| [query_Q07](images/phase5/query_Q07.jpg), [query_Q08](images/phase5/query_Q08.jpg) | Kết quả bốn góc vuông, đường chéo bằng nhau |

Ảnh Neo4j Browser ở viewport mặc định hẹp; ảnh graph ứng dụng rõ tên hình, hướng và nhãn cạnh để dùng khi giải thích taxonomy. Chỉ đăng nhập/chạy truy vấn đọc trong Browser; không chạy seed mẫu Movies hoặc thao tác xóa dữ liệu.

## 10. File tạo/sửa và nghiệm thu

Source sửa: `.gitignore`, `README.md`, `database/README.md`, `scripts/phase2.py`, `scripts/http_smoke.py`. Source mới: `scripts/phase5.py`, `tests/test_cli_security.py`.

Bằng chứng mới: `BAO_CAO_PHASE_5.md`, `PHASE_5_RESULTS.json`, `PHASE_5_DB_PREFLIGHT.json`, `PHASE_5_DB_POSTFLIGHT.json`, `PHASE_5_SEED_RESULTS.json`, `PHASE_5_PYTEST.xml`, `PHASE_5_HTTP_RESULTS.json`, `PHASE_5_ERROR_HTTP.json`, `PHASE_5_UI_RESULTS.json`, `PHASE_5_FRESH_START.json`, `PHASE_5_FRESH_PYTEST.xml`, `PHASE_5_FRESH_HTTP_RESULTS.json`, `PHASE_5_AUDIT.json`, và 21 ảnh trong `docs/images/phase5/`. Bằng chứng Phase 2–4 giữ nguyên.

- [x] Database 44/79; 20 validation và 15 query thực tế PASS.
- [x] Pytest và HTTP thực tế PASS.
- [x] Các luồng frontend, search, graph, query UI PASS.
- [x] Dữ liệu HV, nguồn Property và logic Condition đúng.
- [x] Không có credential thật trong source/báo cáo công khai; ignore hoạt động.
- [x] Cài đặt từ source/venv mới thành công, hướng dẫn đủ bước.
- [x] Không lỗi console bất thường ở luồng bình thường.
- [x] Có ảnh ứng dụng, Neo4j graph/query thật.

**PASS Phase 5.** Có thể bắt đầu soạn TONG_QUAN_DU_AN.docx và HUONG_DAN_SU_DUNG.docx ở Phase 6 dựa trên bằng chứng thực tế này. Chưa thực hiện Phase 6 trong lượt này.
