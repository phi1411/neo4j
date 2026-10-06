# Kịch bản demo — khoảng 7 phút

## Chuẩn bị trước buổi demo

- Neo4j Desktop: instance Running, database `quadrilateral` online.
- Terminal tại gốc source: `.\.venv\Scripts\python.exe run.py`.
- Mở `http://127.0.0.1:5000`; chuẩn bị tab Neo4j Query/Browser chọn `quadrilateral`.
- Dashboard có 44 node/79 relationship; không chạy lại seed trong lúc thuyết trình.

## 0:00–0:40 — Giới thiệu đề tài

“Em mô hình hoá kiến thức về bảy loại tứ giác bằng Neo4j. Mỗi loại hình liên hệ với lớp tổng quát, tính chất và dấu hiệu nhận biết. Website giúp tra cứu và quan sát các quan hệ đó.”

Mở Tổng quan; chỉ các số 7 Shape, 19 Property, 18 Condition, tổng 44 node và 79 relationship.

## 0:40–1:20 — Vì sao dùng graph

“Bài toán có phân loại nhiều cấp, tính chất dùng chung và đa kế thừa. Graph cho phép biểu diễn các liên hệ thành cạnh và trả đường đi để giải thích kết quả. SQL vẫn làm được bằng bảng liên kết và truy vấn đệ quy; em chưa đo benchmark để so hiệu năng.”

Nói quy ước: xét tứ giác lồi, không suy biến; hình thang có **đúng một** cặp cạnh đối song song. Nhánh hình bình hành tách riêng.

## 1:20–2:10 — Taxonomy và đa kế thừa

Mở Khám phá Graph → Xem taxonomy. Có 7 node và 7 cạnh IS_A.

“IS_A đi từ loại đặc biệt tới loại tổng quát. Hình vuông có hai cha: Hình chữ nhật và Hình thoi. Cả hai nhánh dẫn tới Hình bình hành, rồi Tứ giác.”

Chỉ hai mũi tên từ HV. Không nói Hình bình hành là Hình thang trong taxonomy này.

## 2:10–3:20 — Tra cứu Hình vuông

Vào Các loại tứ giác → nhập `hinh vuong` → mở chi tiết. Chỉ hai cha, bốn tổ tiên, 12 tính chất hiệu lực và 0 tính chất khai báo trực tiếp.

“Neo4j không tự hiểu kế thừa. Cypher đi qua IS_A để hợp tính chất của hình và các tổ tiên. DISTINCT loại kết quả trùng khi cùng tính chất tới được qua hai nhánh.”

Cuộn tới Condition: “Trong một quy tắc là AND giữa ngữ cảnh và các giả thiết; nhiều quy tắc là OR. Ứng dụng hiện hiển thị tri thức, chưa tự suy luận từ dữ kiện người dùng nhập.”

## 3:20–4:30 — Q06 và Q08

Vào Truy vấn Neo4j; chọn rồi chạy từng query.

- **Q06**: HTHOI và HV có bốn cạnh bằng nhau. HV được tìm thấy qua kế thừa dù không có HAS_PROPERTY trực tiếp.
- **Q08**: HCN, HTC, HV có đường chéo bằng nhau. “Một tính chất riêng lẻ không đủ kết luận hình chữ nhật; điều kiện phải kèm ngữ cảnh.”

Cho giảng viên xem Cypher và bảng kết quả thay vì chỉ đọc tên query.

## 4:30–5:40 — Q15 chứng minh traversal/path

Chạy Q15, xem hai dòng và graph:

1. HV → HCN → HBH → DIAGONALS_BISECT_EACH_OTHER.
2. HV → HTHOI → HBH → cùng Property.

“Ba node đầu nối bằng IS_A; cạnh cuối là HAS_PROPERTY. Truy vấn trả đường đi để giải thích tính chất chia đôi đường chéo được khai báo ở Hình bình hành.”

Nếu dùng Q09 thay thế: hai đường TQ–HBH–HCN/HTHOI–HV, mỗi đường ba cạnh. Query liệt kê đường có độ dài 1–6, không phải lệnh shortestPath.

## 5:40–6:30 — Neo4j thật

Chuyển sang Neo4j Query/Browser, chọn database `quadrilateral` và khai báo:

```text
:params {dataset:'quadrilateral-v1',shape_id:'HV',depth:3}
```

Copy Q06 hoặc Q15 từ `database/demo_queries.cypher`, bấm Run; đối chiếu Table với web, chuyển Graph nếu có kết quả node/path. Không mở `.env` hoặc màn hình mật khẩu trước lớp.

## 6:30–7:00 — Kết quả và giới hạn

“Database đã đạt 20 validation và 15 query; vòng cuối có 92 pytest và 41 kiểm tra HTTP PASS. Hạn chế là chỉ bảy loại hình, chưa nhận dạng ảnh/toạ độ và chưa là theorem prover. Hướng mở rộng là thêm tri thức có nguồn và bộ nhận biết theo tập giả thiết.”

Nếu lỗi kết nối: kiểm tra Neo4j Running và báo lỗi thật; không trình bày ảnh cũ như kết quả đang chạy. Có thể dùng tài liệu để giải thích mô hình trong lúc khắc phục.
