# SRT tiếng Anh tự động từ YouTube

Dùng khi video có SRT đi kèm, đặc biệt phụ đề tiếng Anh tự động từ YouTube. File do người dùng chuẩn bị sẵn; quy trình này không tự tải lại từ YouTube.

## Ghép file và kiểm tra ban đầu

- Tự tìm trong folder video: ưu tiên `<stem>.en.srt`, rồi biến thể tiếng Anh như `<stem>.en-US.srt`, sau đó `<stem>.srt`. Ghép theo đúng stem hoặc ID video, không lấy SRT đầu tiên của cả folder. Nếu nhiều bản cùng phù hợp, đối chiếu nội dung để chọn; chỉ hỏi khi không thể xác định đúng bản. Nếu SRT không dùng được nhưng có subtitle track đáng tin cậy, dùng track trước khi tạo transcript mới.
- Đọc UTF-8/BOM; kiểm tra parse được, mốc không âm, start < end, thứ tự thời gian và mốc so với thời lượng nguồn. Cue chồng/lặp có thể do auto-caption kiểu cuốn: gộp phần trùng ở các cue liền nhau trong bản đọc tạm, giữ timestamp đối chiếu và SRT gốc; không xóa lời lặp ở cảnh khác.
- Đọc **toàn bộ SRT**, gộp cue thành câu/tình tiết để lập bản đồ truyện có timestamp. Đánh dấu khoảng trống lớn hoặc thiếu đoạn quan trọng để xem hình/âm thanh bổ sung. Khoảng không có subtitle không đồng nghĩa không có cảnh hay lời thoại; giữ nguồn từ 0 tới hết video, kể cả intro, cảnh im lặng và đoạn sau cue cuối.

## Kiểm tra khớp theo mẫu

Bắt đầu bằng ba cửa sổ có lời thoại khoảng 15–30 giây ở đầu, giữa và gần cuối; tránh chọn toàn nhạc/im lặng. So câu/tình tiết và thời gian với âm thanh hoặc phụ đề đốt sẵn trên hình. Nếu SRT tiếng Anh là bản dịch, so ý và thời điểm phát ngôn, không yêu cầu trùng từng từ với audio khác ngôn ngữ. Thêm mẫu ở đoạn nghi sai hoặc chuyển mạch lớn khi cần.

Phân biệt **khớp video/thời gian** với **đúng từng chữ**. Sai tên riêng, dấu câu, ký hiệu người nói hoặc từ bị YouTube che chưa đủ để loại SRT nếu vẫn hiểu được truyện và khớp timeline. Kiểm chứng tên/tình tiết dùng trong title ở chỗ có căn cứ; không đoán theo cách viết sai của ASR. Kiểm tra lấy mẫu không chứng minh phụ đề chính xác 100% hoặc sync từng frame.

| Kết quả quan sát | Cách tiếp tục |
|---|---|
| Đúng nội dung, thời gian nhất quán qua các mẫu | Dùng toàn bộ SRT làm transcript chính; rà hình/âm thanh tại mọi mốc cắt. Không chạy thêm một vòng OCR/ASR phủ toàn video. |
| Một vài câu sai/khó hiểu, vùng thiếu hoặc mốc cắt chưa rõ | Chỉ xem thêm, OCR hoặc ASR local ở vùng đó; mở rộng cửa sổ khi chưa đủ ngữ cảnh. |
| Cùng độ lệch ở các mẫu rải đều | Xác minh offset ở thêm một vùng; ghi offset và dùng timeline đã hiệu chỉnh trong bản làm việc, giữ SRT gốc. Rà lại đầu/giữa/cuối và các mốc cắt sau hiệu chỉnh. |
| Độ lệch thay đổi hoặc chỉ lệch sau một đoạn | Xác định các vùng bị ảnh hưởng, kiểm tra/hiệu chỉnh riêng; không áp một offset cho toàn file. |
| Khác video, không đọc được, thiếu nhiều hoặc sai thời gian trên phần lớn nguồn | Loại SRT khỏi nguồn mốc chính; tìm subtitle track/bản khác đáng tin cậy. Nếu không có, dùng OCR phụ đề trên hình hoặc ASR local phủ các phần chưa có transcript đáng dùng, có thể toàn video nếu cần. |

Ưu tiên xem/đối chiếu trực tiếp bằng công cụ hiện có. Chỉ chạy OCR/ASR khi đối chiếu trực tiếp chưa giải quyết được nghi vấn; không bắt buộc chạy cả hai cho cùng vùng đã rõ. OCR/ASR cũng có thể sai hoặc bịa lời trong nhạc/im lặng, nên đối chiếu với hình và ngữ cảnh. Quyền xử lý local không tự mở rộng thành quyền upload video/audio tới dịch vụ khác.

## Chọn mốc và ghi kết quả

- Mép cue chỉ định vị ứng viên: một câu có thể kéo qua nhiều cue, chữ có thể kết thúc sớm hoặc lưu lại sau tiếng nói. Với mỗi mốc dự kiến, rà hai phía khoảng 5–10 giây, mở rộng nếu cần; giữ trọn câu, phản ứng và hành động, kiểm tra cuối ep trước nối đầu ep sau. Chỉ OCR/ASR bổ sung nếu mốc còn mơ hồ. Cân mốc theo toàn series để mỗi ep/part khoảng 180–250 giây và tránh tập cuối quá ngắn.
- Trong `split_plan.md`, ghi file SRT đã ghép, các cửa sổ đã kiểm tra, nhận xét khớp thời gian/lỗi chữ, vùng hoặc offset hiệu chỉnh và giới hạn QA. Khi cần báo cáo riêng, dùng `subtitle_check.md`; không gọi thống kê so khớp chuỗi/OCR là tỷ lệ chính xác từng từ.
- Nếu chưa nghe trực tiếp audio mà chỉ đối chiếu qua hình hoặc ASR, ghi rõ. Không tự sửa chuẩn toàn bộ SRT, ghi đè bản gốc hay burn-in SRT mới; chỉ làm việc đó khi người dùng yêu cầu.
