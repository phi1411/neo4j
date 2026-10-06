# Báo cáo Phase 6 — Documentation / Bài nộp

Trạng thái: **PASS trong phạm vi Phase 6**. Ngày kiểm tra: 07/10/2026.

## 1. Đầu ra

| Hạng mục | Trạng thái |
|---|---|
| README tiếng Việt | Hoàn thiện đủ 26 mục theo yêu cầu; taxonomy và kiến trúc có Mermaid |
| [TONG_QUAN_DU_AN.docx](TONG_QUAN_DU_AN.docx) | Hoàn thiện, 24 trang; đủ 9 chương, kết luận và tài liệu tham khảo |
| [HUONG_DAN_SU_DUNG.docx](HUONG_DAN_SU_DUNG.docx) | Hoàn thiện, 21 trang; đủ 24 mục hướng dẫn và xử lý lỗi |
| Data + Source App | Có catalog, script Cypher, Flask, frontend, test và hướng dẫn chạy |
| Link GitHub | Chưa công bố; chờ audit Phase 7 đúng yêu cầu người dùng |

Hai DOCX dùng khổ A4, Times New Roman, Heading styles, mục lục có liên kết đã cập nhật, đánh số trang, caption bảng/hình và code Consolas. Ảnh nhúng trực tiếp trong tài liệu, giữ tỷ lệ gốc. Tổng quan có 5 hình; hướng dẫn có 13 hình.

## 2. Đối chiếu với project thật

- Database `quadrilateral`, dataset `quadrilateral-v1`, Neo4j Enterprise 2026.09.0.
- 44 node: 7 Shape, 19 Property, 18 Condition; 79 relationship thuộc 5 type.
- Taxonomy có 7 cạnh IS_A, hai nhánh cha của HV; không thêm HBH → HT hoặc HCN → HTC.
- Hình thang có **đúng một** cặp cạnh đối song song theo quy ước project. Chỉ xét tứ giác lồi, không suy biến.
- Property kế thừa qua IS_A; HV có 12 tính chất hiệu lực và 0 HAS_PROPERTY trực tiếp. Condition không kế thừa, AND trong một Condition, OR giữa nhiều Condition.
- Nội dung query lấy trực tiếp từ `database/demo_queries.cypher`. Báo cáo phân tích Q02, Q04, Q06, Q08, Q09, Q10, Q12, Q15 và tổng hợp đủ 15 query. Q09 liệt kê đường có độ dài 1–6; không gọi sai thành thuật toán shortestPath. Hai đường hiện tại cùng dài 3 cạnh.
- Số liệu kiểm thử đọc từ báo cáo đã nghiệm thu: Phase 2 20/20 validation và 15/15 query; Phase 3 91 pytest, 38 HTTP; Phase 5 92 pytest, 41 HTTP chính, 8 HTTP lỗi/search, 78 UI. Môi trường ảo mới: 92 pytest, 41 HTTP; không reset database và chưa clone GitHub remote.
- Không bổ sung chức năng vào app, không seed hoặc sửa dữ liệu trong Phase 6. Không tuyên bố benchmark Neo4j nhanh hơn SQL.

Nguồn: `PHASE_2_RESULTS.json`, `PHASE_3_RESULTS.json`, `PHASE_5_RESULTS.json`, catalog JSON, route/service và README đối chiếu với mã nguồn.

## 3. Ảnh đã có và ảnh còn thiếu

Đã có 21 JPEG gốc trong `docs/images/phase5/`, gồm dashboard, taxonomy, danh sách, chi tiết HV, Property, Condition, lân cận độ sâu 1–3, danh mục query, Q06/Q07/Q08/Q09/Q15, tooltip, màn hình hẹp, lỗi Neo4j và Neo4j Query/Browser.

Phase 6 bổ sung `docs/images/04_search_hinh_vuong.jpg`: chụp trực tiếp trang `/shapes`, nhập `hinh vuong`, trả một kết quả HV. Không thay hoặc chỉnh sửa screenshot nghiệm thu Phase 5. Mã hash 21 ảnh cũ được đối chiếu và giữ nguyên.

**Không thiếu ảnh cho các mục hướng dẫn bắt buộc.** Bộ minh chứng hiện tại có 22 ảnh thật. Danh mục ở [images/README.md](images/README.md), kích thước và SHA-256 ở [PHASE_6_IMAGE_MANIFEST.json](PHASE_6_IMAGE_MANIFEST.json). Ảnh Browser chụp ở cửa sổ hẹp nên nhãn graph nhỏ; bảng query đọc được và có graph taxonomy trên ứng dụng để trình bày rõ tên hình.

## 4. Kiểm tra Word

Đã thử renderer đi kèm skill documents. Renderer báo `LibreOffice soffice.exe was not found on PATH`. Máy có Microsoft Word, nên dùng Word mở cả hai DOCX, cập nhật field/mục lục, repaginate và xuất PDF kiểm tra; dùng Poppler đi kèm runtime tạo PNG từng trang. Không cài LibreOffice hoặc dùng ảnh giả để thay việc render.

Đã xem đủ **24/24 trang tổng quan và 21/21 trang hướng dẫn** ở độ phân giải gốc của bản render. Sau khi sửa nội dung Q09, URL truy cập và cập nhật lại mục lục, đã xem lại mọi trang thay đổi; các trang còn lại được đối chiếu hash ảnh render.

| Kiểm tra | Kết quả |
|---|---|
| Tiếng Việt, Heading, mục lục và số trang | PASS |
| Ảnh đủ, không méo, caption đúng | PASS |
| Bảng trong lề, không mất hàng/cột | PASS |
| Code Cypher/PowerShell trong lề, không cắt | PASS |
| Không có trang trắng bất thường | PASS |
| Không có marker chèn ảnh, TODO hoặc “AI generated” | PASS |
| Link README tới file cục bộ | PASS |
| Link tài liệu tham khảo trong DOCX | Có hyperlink tới nguồn chính thức/nguồn phân tích |

Bản PDF/PNG dùng kiểm tra nằm trong `.qa/phase6-render/`, được `.gitignore` loại trừ; không phải file bài nộp. Kết quả và SHA-256 DOCX cuối ở [PHASE_6_RESULTS.json](PHASE_6_RESULTS.json).

## 5. Kiểm tra thông tin nhạy cảm

Đã so sánh riêng với mật khẩu Neo4j cấu hình trong `.env`, không in giá trị đó ra log. Không phát hiện giá trị mật khẩu trong XML/relationships/metadata hai DOCX, văn bản PDF render, README hoặc các file tài liệu Phase 6. Các ảnh đưa vào Word đã được xem, không có màn hình nhập mật khẩu. Ví dụ chỉ dùng `NEO4J_PASSWORD=your_password`.

`.env`, `.venv`, `.qa`, cache và log đã có quy tắc loại trừ. `.qa` còn chứa bằng chứng kiểm thử cục bộ và cấu hình riêng từ Phase 5; không đưa nguyên thư mục làm gói source công khai. Kiểm tra này chỉ phục vụ tài liệu Phase 6, **không thay thế audit toàn bộ nội dung staging/commit ở Phase 7**. Phase 6 không init Git, commit, upload hoặc public repository.

## 6. Thông tin cá nhân cần điền

Trang bìa hai tài liệu giữ các placeholder: `[Trường]`, `[Khoa]`, `[Họ tên sinh viên]`, `[MSSV]`, `[Lớp]`, `[Giảng viên]`, `[Năm học]`. Metadata tác giả cũng dùng placeholder. Không suy ra tên sinh viên hoặc giảng viên từ ảnh chụp giao diện lớp học.

Người thực hiện điền thông tin thật trước khi nộp và cập nhật mục lục bằng Word nếu sửa nội dung làm đổi số trang. Môn học đã xác định: NoSQL.

## 7. File tạo hoặc sửa

- Sửa: `README.md`.
- Tạo: hai DOCX, `docs/BAO_CAO_PHASE_6.md`, `docs/PHASE_6_RESULTS.json`, `docs/PHASE_6_IMAGE_MANIFEST.json`, `docs/images/README.md`, ảnh tìm kiếm và `docs/requirements-documentation.txt`.
- Tạo công cụ tái lập: `scripts/build_phase6_docs.py`, `scripts/render_phase6_word.ps1`, `scripts/audit_phase6_docs.py`. Dependencies tài liệu tách riêng, không đổi `requirements.txt` của ứng dụng. Render Word yêu cầu Microsoft Word trên Windows; raster yêu cầu Poppler qua tham số `--poppler-path`.
- Giữ nguyên source app, dataset, các file Cypher và báo cáo kiểm thử các phase trước.

Đối chiếu bài nộp: DOCX tổng quan đáp ứng mục 1; Data + Source App đã chuẩn bị cho mục 2; DOCX hướng dẫn có ảnh thật đáp ứng mục 3. Bài nộp đầy đủ còn cần thông tin bìa thật và link GitHub sau Phase 7.
