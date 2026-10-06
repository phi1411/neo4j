# Kiểm thử lại giao diện Phase 4

Chạy Neo4j và server chính bằng Python trong `.venv`: `python run.py`. Mở http://127.0.0.1:5000. Kết quả dưới đây là kỳ vọng của dataset đã duyệt, không phải dữ liệu để đưa vào frontend.

## Dữ liệu và thao tác chính

1. `/`: chờ tải xong; đối chiếu thống kê với `/api/stats`. Dataset hiện tại: Shape 7, Property 19, Condition 18; tổng 44 node, 79 relationship.
2. Taxonomy: 7 node/7 cạnh. Bấm Hình vuông: hai nhánh cha HCN/HTHOI. Bấm cạnh để xem nguồn/đích và ý nghĩa. Kéo nền, cuộn zoom, bấm Vừa khung.
3. `/shapes`: đủ 7 hình. Tìm lần lượt “Hình vuông”, “hinh vuong”, “VUONG”: chỉ HV. Tìm “khongtimthay”: empty state. Xem tất cả khôi phục danh sách từ API.
4. `/shapes/HV`: hai cha; bốn tổ tiên HCN, HTHOI, HBH, TQ; 12 tính chất, 0 khai báo trực tiếp. Không có HT/HTC trong tổ tiên.
5. Nguồn DIAGONALS_EQUAL là HCN; DIAGONALS_PERPENDICULAR là HTHOI; DIAGONALS_BISECT_EACH_OTHER là HBH. Mở đường kế thừa của tính chất chia đôi: hai đường riêng qua HCN/HTHOI.
6. HV có 5 quy tắc, OR giữa quy tắc. C_HV_05: TQ AND FOUR_EQUAL_SIDES AND FOUR_RIGHT_ANGLES ⇒ HV. Không thay AND bằng OR.
7. Chi tiết các hình khác: số tính chất hiệu lực/trực tiếp lần lượt TQ 2/2, HT 4/2, HTC 7/3, HBH 7/5, HCN 9/2, HTHOI 10/3.
8. `/graph`: mặc định HV/depth 1. Đổi depth: 1 có 8/11, 2 có 23/43, 3 có 39/71 node/cạnh. Đây là induced graph, không phải hình sao hoặc tập tổ tiên.
9. Chọn node bằng dropdown/bàn phím và bấm node/cạnh trên canvas. Kiểm tra nhãn tiếng Việt, mũi tên, tooltip, legend. Nút Xem taxonomy trả graph phân loại.
10. `/queries`: đủ Q01–Q15; từng query có mục đích, cách đọc kết quả, Cypher nguồn whitelist và tham số theo schema. Chạy từng query, so `database/expected_results.json`; Q14 mặc định depth 3. Không có ô nhập Cypher tự do.
11. Query đồ thị Q01/Q09/Q14/Q15 phải có graph; các query còn lại có bảng. Khi đổi query/tham số, kết quả cũ biến mất. Query không có dòng vẫn báo empty state rõ ràng.
12. `/about`: quy ước hình thang đúng một cặp, phạm vi, cơ chế kế thừa và giới hạn suy luận trình bày đúng.

## Lỗi và responsive

- `/shapes/UNKNOWN`: thông báo không tìm thấy; không còn nội dung chi tiết giả/đã tải trước.
- `/shapes/HV%27`: ID không hợp lệ, giao diện vẫn có navbar/footer.
- Depth trên UI chỉ cho 1/2/3. Gọi `/api/graph/neighborhood/HV?depth=0` hoặc `depth=4`: API 400; pytest kiểm tra cả kiểu sai và tham số lặp.
- Chạy server thử riêng: `.\.venv\Scripts\python.exe scripts/fault_preview.py --port 5001`. Mở http://127.0.0.1:5001: health/stats/graph trả 503 từ driver thật; UI báo mất Neo4j, không có stats/graph thay thế. Instance chính không bị tắt hoặc sửa.
- Giữ trang cổng phụ mở, dừng server phụ bằng Ctrl+C và bấm kiểm tra kết nối: UI báo không liên lạc được Flask. Sau đó đóng tab thử; server chính 5000 vẫn chạy.
- Thử các trang ở 1280×900 và 390×844: navbar/form/card không tràn ngang toàn trang; bảng query có vùng cuộn riêng. Chạy Q02 trên mobile: 12 dòng kết quả. Graph hỗ trợ cuộn/chụm để zoom.
- Đọc console sau các thao tác chính: không có lỗi JavaScript ngoài dự kiến. HTTP 400/404/503 trong các ca lỗi có chủ đích không được hiểu là query thành công.

## Bằng chứng và bảo toàn

Chỉ chụp ảnh bằng trình duyệt trên app thật. Lưu ảnh JPEG vào `docs/images`; không dựng mockup hoặc sinh ảnh giả. `PHASE_4_UI_RESULTS.json` lưu các đối chiếu của lần chạy trình duyệt ngày triển khai; muốn nghiệm thu máy khác phải chạy lại các bước, không coi báo cáo cũ là bằng chứng mới.

Chạy pytest với JUnit `docs/PHASE_4_PYTEST.xml`, sau đó `scripts/review_phase4.py`. Review chỉ đọc Neo4j, chạy 20 validation và 15 query Phase 2, so hash dataset/dữ liệu ngoài dataset với baseline Phase 3. Không seed để “sửa” kết quả kiểm thử.
