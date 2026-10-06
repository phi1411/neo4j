# Báo cáo kiểm thử Phase 2 — Neo4j thật

Thời điểm kiểm tra: **2026-10-06T22:32:23.774520+07:00** (UTC+07:00, Asia/Bangkok).

**Trạng thái: PASS.** Neo4j Enterprise 2026.09.0; database `quadrilateral`; dataset `quadrilateral-v1`. Xác thực bằng driver và RETURN 1 thành công. Không làm Flask/frontend.

## Số lượng thực tế

| Loại node | Số lượng |
|---|---:|
| Condition | 18 |
| Property | 19 |
| Shape | 7 |
| Tổng | 44 |

| Loại relationship | Số lượng |
|---|---:|
| HAS_CONDITION | 18 |
| HAS_PROPERTY | 17 |
| IS_A | 7 |
| REQUIRES_PROPERTY | 19 |
| REQUIRES_SHAPE | 18 |
| Tổng | 79 |

## Schema thực tế

Ba uniqueness constraints cho `(dataset,id)` theo Shape/Property/Condition; một search index `(dataset,search_name)`. Cả bốn index (bao gồm ba backing index của constraints) đều ONLINE.

## Seed hai lần và bảo toàn dữ liệu

- Lần đầu: tạo 44 node và 79 relationship.
- Lần hai: tạo 0 node và 0 relationship.
- Toàn bộ ID, label, thuộc tính node/cạnh và các cặp relationship giống nhau giữa hai lần; không chỉ so số lượng.
- Dữ liệu ngoài dataset trong database mục tiêu được so snapshot trước/sau và giữ nguyên. Database mục tiêu mới ban đầu có 0 node. Không chạy DELETE/DROP hoặc ghi vào dữ liệu của database neo4j.
- SET vẫn được gọi lại ở lần hai, nên properties_set khác 0 không đồng nghĩa giá trị thuộc tính đổi.

Hash lần đầu: `bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8`

Hash lần hai: `bd30ff8cdf39d79d504036bd1a581f16ccc225e74611f01bf7620d703e8ac7d8`

## Validation: 20/20 PASS

| Mã | Kiểm tra | Vi phạm |
|---|---|---:|
| V01 | Trùng ID theo label/dataset | 0 |
| V02 | Trùng relationship | 0 |
| V03 | Orphan node | 0 |
| V04 | Self-loop | 0 |
| V05 | Chu trình IS_A | 0 |
| V06 | Taxonomy đúng bảy cặp | 0 |
| V07 | Hai cạnh bị loại không tồn tại | 0 |
| V08 | Label/trường chung bắt buộc | 0 |
| V09 | Trường riêng và logic AND | 0 |
| V10 | Relationship đúng kiểu node | 0 |
| V11 | Không có cạnh qua ranh giới dataset | 0 |
| V12 | Condition đủ kết luận/ngữ cảnh/giả thiết | 0 |
| V13 | AND hai giả thiết của C_HV_05 | 0 |
| V14 | Đường phân loại tới TQ | 0 |
| V15 | Số lượng node/cạnh theo từng loại | 0 |
| V16 | Nhãn ProjectEntity | 0 |
| V17 | Không kế thừa hai định nghĩa song song mâu thuẫn | 0 |
| V18 | Tập bảy ID Shape | 0 |
| V19 | Khai báo đường chéo bằng nhau độc lập | 0 |
| V20 | Property dùng cho Condition có liên kết | 0 |

## Query: 15/15 PASS

| Query | Kết quả thực tế đã đối chiếu | Trạng thái |
|---|---|---|
| Q01 | 44 node, 79 cạnh; trả graph thật | PASS |
| Q02 | 12 Property, DIAGONALS_EQUAL đến từ HCN, chia đôi nhau đến từ HBH | PASS |
| Q03 | HCN, HTHOI | PASS |
| Q04 | HBH, HCN, HTHOI, TQ | PASS |
| Q05 | HCN, HTHOI, HV | PASS |
| Q06 | HTHOI, HV | PASS |
| Q07 | HCN, HV | PASS |
| Q08 | HCN, HTC, HV | PASS |
| Q09 | 2 đường phân loại, mỗi đường 3 cạnh: TQ–HBH–HCN–HV và TQ–HBH–HTHOI–HV | PASS |
| Q10 | 9 tính chất chung HV/HCN | PASS |
| Q11 | 10 tính chất chung HV/HTHOI | PASS |
| Q12 | HTHOI, HV | PASS |
| Q13 | 7 dòng; degree/cạnh từng loại của cả 7 Shape khớp kỳ vọng độc lập | PASS |
| Q14 | depth 1: 8 node/11 cạnh; depth 2: 23 node/43 cạnh; depth 3: 39 node/71 cạnh | PASS |
| Q15 | 2 đường giải thích qua HCN/HBH hoặc HTHOI/HBH tới Property chia đôi đường chéo | PASS |

Q14 so cả tập ID node và các cặp cạnh với graph chuẩn từ catalog ở mỗi độ sâu. Chú thích sơ bộ 7 cạnh ở depth 1 đã được sửa thành 11 cạnh: có bảy cạnh tới HV và bốn cạnh ngữ cảnh giữa những node lân cận. Query trả induced graph, không chỉ graph hình sao. Sau chỉnh chú thích/kỳ vọng đã chạy lại validation và toàn bộ 15 query ở chế độ chỉ đọc, không seed lần ba.

### Kết quả Q13 chi tiết

| Shape | IS_A ra | Property trực tiếp | Condition | IS_A vào | REQUIRES_SHAPE vào | Tổng vào | Tổng ra |
|---|---:|---:|---:|---:|---:|---:|---:|
| HBH | 1 | 5 | 4 | 2 | 4 | 6 | 10 |
| HCN | 1 | 2 | 3 | 1 | 2 | 3 | 6 |
| HT | 1 | 2 | 1 | 1 | 2 | 3 | 4 |
| HTC | 1 | 3 | 2 | 0 | 0 | 0 | 6 |
| HTHOI | 1 | 3 | 3 | 1 | 2 | 3 | 7 |
| HV | 2 | 0 | 5 | 0 | 0 | 0 | 7 |
| TQ | 0 | 2 | 0 | 2 | 8 | 10 | 2 |

## Lỗi đã sửa

- Lần gọi đầu tiên gặp lỗi driver: Query object chỉ dùng với session.run, không dùng trực tiếp với managed transaction tx.run. Đã chuyển sang chuỗi Cypher trong tx.run; seed có transaction timeout và rollback khi lỗi. Lỗi xảy ra trước thao tác ghi; schema và seed sau sửa đều chạy thành công.
- Chú thích số cạnh Q14 được thống nhất với định nghĩa induced graph như giải thích trên.

## File tạo mới

- `database/constraints.cypher`
- `database/indexes.cypher`
- `database/properties.json`
- `database/conditions.json`
- `database/shapes.json`
- `database/relationships.json`
- `database/seed.cypher`
- `database/demo_queries.cypher`
- `database/validation.cypher`
- `database/expected_results.json`
- `database/README.md`
- `scripts/phase2.py`
- `requirements.txt`
- `docs/seed_first_run.json`
- `docs/PHASE_2_RESULTS.json`
- `docs/BAO_CAO_PHASE_2.md`
- `.env`: cấu hình cục bộ, bị .gitignore loại khỏi Git; không đưa mật khẩu vào báo cáo/source.
- `.venv/`: môi trường chạy cục bộ, bị .gitignore loại khỏi Git.

## File sửa

- `docs/PHASE_1_PHAN_TICH.md`: constraint theo dataset và chi tiết/kỳ vọng Q14, trạng thái triển khai.
- `docs/HUONG_DAN_KET_NOI_NEO4J.md`: cập nhật kết nối đã thành công và liên kết báo cáo.

## Bằng chứng và cách chạy lại

Kết quả từng dòng/node/path, schema và counter được lưu trong `PHASE_2_RESULTS.json`. Snapshot lần đầu nằm trong `seed_first_run.json`. Hướng dẫn chạy nằm trong `database/README.md`.

Các kết quả ở báo cáo lấy từ Neo4j thật. Không tạo ảnh giả; ảnh ứng dụng và tài liệu Word thuộc các phase sau.
