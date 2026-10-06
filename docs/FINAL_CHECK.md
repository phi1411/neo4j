# Final check — Phase 7

Ngày kiểm tra: 07/10/2026. **Các hạng mục kỹ thuật PASS. GitHub đã công bố. Bài nộp NOT READY chỉ vì thông tin cá nhân trên bìa chưa được cung cấp.**

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Project | PASS | Source, catalog, Cypher, tests, static và tài liệu nằm trong repository; không thêm tính năng lớn |
| Database | PASS | Neo4j thật 44 node/79 relationship; 20/20 validation, 15/15 query |
| Backend | PASS | Server thật và 41 HTTP PASS, gồm health, stats, danh sách, HV, taxonomy |
| Frontend | PASS | 11 kiểm tra browser: các trang chính, search hinh vuong, HV depth 1, Q06/Q09/Q15; không ghi nhận console error |
| Tests | PASS | 92 pytest PASS, 0 skip; bản clone GitHub cũng đạt 92 pytest và 41 HTTP |
| Documents | PASS | Hai DOCX 24/21 trang, đã kiểm tra trực quan toàn bộ 45 trang; URL GitHub thật; ảnh kết quả thật |
| README | PASS | Clone, tạo venv, kích hoạt tùy chọn, requirements, cấu hình, tạo/chọn database, seed, validation, chạy app; ảnh được commit |
| Secrets | PASS | Quét source công khai, DOCX XML, staging và lịch sử Git cục bộ; không phát hiện credential thật; .env/.venv/.qa bị loại khỏi Git |
| Git | PASS | Nhánh main, remote do người dùng cung cấp; commit và push thông thường; không force push/rewrite history |
| GitHub | PASS | [phi1411/neo4j](https://github.com/phi1411/neo4j); đã push và clone qua mạng thành công |
| Demo script | PASS | Kịch bản 7 phút và 26 câu hỏi phản biện đã có |
| Bài nộp | NOT READY | Cần điền thông tin bìa rồi lưu lại hai DOCX trước khi nộp |

Repository có app, dataset/catalog, 5 file Cypher, tests, requirements, README, ảnh thật và hai Word. Không có .env, môi trường ảo hoặc cache trong nội dung commit. Bản Word cuối và báo cáo nghiệm thu được cập nhật vào repository sau lần kiểm thử bản clone; source app, database và tests không thay đổi giữa hai lần công bố.

## Bằng chứng

- Database: [PHASE_7_DB_RESULTS.json](PHASE_7_DB_RESULTS.json), [bản clone](PHASE_7_FRESH_DB_RESULTS.json).
- Tests: [PHASE_7_PYTEST.xml](PHASE_7_PYTEST.xml), [bản clone](PHASE_7_FRESH_PYTEST.xml).
- HTTP: [PHASE_7_HTTP_RESULTS.json](PHASE_7_HTTP_RESULTS.json), [bản clone](PHASE_7_FRESH_HTTP_RESULTS.json).
- Browser: [PHASE_7_UI_RESULTS.json](PHASE_7_UI_RESULTS.json) và [ảnh Q15](images/phase7/01_final_Q15.jpg).
- Cài từ GitHub: [PHASE_7_FRESH_START.json](PHASE_7_FRESH_START.json).
- Tài liệu: [PHASE_7_DOCUMENT_RESULTS.json](PHASE_7_DOCUMENT_RESULTS.json).
- Audit: [PHASE_7_AUDIT.json](PHASE_7_AUDIT.json). Báo cáo lưu lần quét trước commit cuối; đã quét lại commit sau khi tạo bằng chế độ không ghi đè báo cáo.

## Phạm vi kiểm tra

Không seed lại ở Phase 7. Snapshot dữ liệu project và dữ liệu ngoài project giữ nguyên. Bản clone dùng venv mới, chỉ cài requirements.txt và cấu hình .env riêng để kết nối Neo4j hiện có; không reset hoặc tạo database mới để thử. Các bước seed và idempotent đã kiểm thử ở Phase 2/5, được đối chiếu với README ở vòng này.

Git được khởi tạo mới trong source gốc; không có commit lịch sử cũ tại đây. Remote ban đầu không có nhánh. Secret scan kiểm tra mọi commit cục bộ sẵn có, không suy ra kết quả cho lịch sử đã bị xóa trước khi thực hiện dự án. Keyword password/secret/token trong tài liệu, test, tên cấu hình và thư viện được phân biệt với giá trị credential. Ảnh được kiểm tra trực quan; không dùng ảnh dựng lại.

Các thư mục .qa, .venv và cache chỉ phục vụ chạy/kiểm thử cục bộ, đã bị Git bỏ qua. Không tạo ZIP hoặc GitHub Release vì bài tập chưa yêu cầu. Flask vẫn phục vụ demo cục bộ tại http://127.0.0.1:5000; server thử bản clone ở cổng 5007 đã dừng.

## Việc còn lại trước khi nộp

Điền **[Trường], [Khoa], [Họ tên sinh viên], [MSSV], [Lớp], [Giảng viên], [Năm học]** trên bìa hai tài liệu. Không suy ra thông tin này từ Git profile hoặc ảnh lớp học. Sau khi điền, lưu Word, kiểm tra lại trang bìa và cập nhật bản nộp/GitHub nếu cần. Chưa còn lỗi kỹ thuật được ghi nhận trong các kiểm tra trên.

Ba thành phần bài nộp: [TONG_QUAN_DU_AN.docx](TONG_QUAN_DU_AN.docx), [GitHub URL](https://github.com/phi1411/neo4j), [HUONG_DAN_SU_DUNG.docx](HUONG_DAN_SU_DUNG.docx).

Kịch bản demo: [DEMO_SCRIPT.md](DEMO_SCRIPT.md). Câu hỏi phản biện: [CAU_HOI_PHAN_BIEN.md](CAU_HOI_PHAN_BIEN.md).
