---
name: auto-clipper-codex
description: Chia video dài hoặc full series thành các ep/part liên tiếp khoảng 60–90 giây, giữ mạch truyện. Title và filename theo mẫu Tên phim (Ep01) hoặc Tên phim (Part01). Dùng cho một video hoặc batch video.
---

# Auto Clipper Codex

Tạo series có thể xem nối tiếp từ video gốc: chọn mốc theo nội dung, giữ trọn trình tự hình/tiếng, xuất từng ep và tiêu đề có căn cứ.

## Quy ước mặc định

- Mỗi ep/part mục tiêu 60–90 giây. Ưu tiên hết câu, đủ phản ứng và điểm ngắt hoặc cliffhanger tự nhiên. Giữ mạch truyện giữa các ep; không cắt máy móc theo đồng hồ. Cân lại các mốc liền kề và các tập cuối để tránh đuôi quá ngắn. Chỉ lệch nhẹ khi cần giữ trọn câu hoặc tình tiết, ghi rõ lý do; tuân thủ giới hạn cứng nếu người dùng yêu cầu.
- Các khoảng nguồn liên tiếp từ 0 tới hết video, không mất cảnh, đảo thứ tự hoặc lặp nội dung. Không tự thêm intro, recap, crop, chữ, nhạc hay phụ đề mới.
- Output mặc định của Codex là `output-codex/<stem video>/`, chứa các clip, `titles.txt`, `cutlist.csv`, `split_plan.md`. Với input trong folder `source`, `source2`, …, đặt `output-codex` cạnh folder nguồn (ví dụ `long vids/source` → `long vids/output-codex`); các trường hợp khác đặt `output-codex` trong folder chứa video nguồn. Dùng output root riêng nếu người dùng chỉ định. Không tự dùng folder `output` hoặc `output-claude` dành cho Claude. Nếu trùng folder bộ phim, tạo tên folder có suffix thay vì ghi đè bản cũ.
- Title = tên phim khoảng 5–7 từ + một dấu cách + (Ep01) hoặc (Part01). Giữ nguyên tên phim người dùng cung cấp, kể cả khi ngoài khoảng 5–7 từ. Nếu chưa có tên phim, chọn tên ngắn phù hợp nội dung. Dùng cùng tên phim cho toàn bộ các ep của bộ, chỉ thay số tập.
- Mặc định dùng (Ep01); dùng (Part01) khi người dùng yêu cầu. Chỉ dùng một kiểu xuyên suốt mỗi bộ. Đánh số 01, 02, ... 99, 100, 101; bắt đầu lại từ 01 cho mỗi bộ phim. Không dùng tiền tố Episode Unicode.
- Filename clip = nguyên title + .mp4. Ví dụ: HANDS off my TWIN (Ep01).mp4 hoặc HANDS off my TWIN (Part01).mp4. Không thêm hashtag, mô tả dài hoặc tiền tố số tập khác. Nếu tên không hợp lệ với filesystem, sửa thống nhất tên phim trong titles.txt và toàn bộ filename của bộ.
- Khi đổi tên hoặc chuyển các bộ đã render, thực hiện trực tiếp trên file, không chỉ sửa TXT; cập nhật filename/path trong cutlist, report, manifest và link bàn giao liên quan. Chỉ chuyển output xác định thuộc Codex; giữ nguyên nguồn và output của công cụ khác.
- `titles.txt`: mỗi ep đúng một title hoàn chỉnh, mỗi title một dòng theo thứ tự ep. Dùng cùng tên phim và cùng kiểu hậu tố cho cả bộ; chỉ tăng số tập. Không tạo nhiều lựa chọn và không thêm hashtag.
- Với “N video đầu”: lọc file video trực tiếp trong folder, sắp xếp tên ổn định rồi lấy N; thông báo danh sách đã chọn. Không lấy ảnh, folder output hay file tạm.

## Thực hiện

1. Kiểm tra đường dẫn và công cụ hiện có. Dùng `ffprobe` đọc thời lượng, stream, kích thước, fps, audio và subtitle; không giả định video là stream 0. Giữ nguyên nguồn. Chỉ hỏi thông tin thiếu nếu nó chặn công việc.
2. Đọc nội dung **toàn bộ** video trước khi chốt mốc. Ưu tiên subtitle có timestamp sẵn. Nếu subtitle đốt trên hình, đọc [quy trình OCR](references/ocr-macos.md); crop và ngôn ngữ phải được hiệu chỉnh cho từng video. Không có subtitle thì dùng ASR sẵn có phù hợp. Quyền xử lý local không tự mở rộng thành quyền upload video tới dịch vụ khác.
3. Lập bản đồ diễn biến có timestamp: nhân vật, xung đột, tiết lộ, phản ứng, chuyển cảnh. OCR/ASR có thể sai tên và bỏ sót cảnh im lặng; đối chiếu khung hình và âm thanh ở điểm quan trọng. Scene detection/silence chỉ là tín hiệu phụ.
4. Chọn mốc để mỗi ep/part dài khoảng 60–90 giây theo toàn bộ câu chuyện. Ưu tiên điểm ngắt tự nhiên; cân lại các mốc liền kề trước khi chấp nhận lệch nhẹ và ghi lý do. Xem/nghe hai phía mỗi mốc để tránh cắt ngang câu, phản ứng hoặc hành động. OCR lấy mẫu chỉ định vị ứng viên, không chứng minh mốc chính xác tới frame. Kiểm tra cuối ep trước nối đầu ep sau để bảo đảm mạch truyện liên tục, dễ hiểu, không bỏ hoặc lặp cảnh.
5. Chốt tên phim và kiểu hậu tố; ghi mỗi ep một title vào `titles.txt`, filename bằng title + `.mp4`. Ghi `cutlist.csv` và `split_plan.md` trước khi render, gồm source, thời lượng, mốc in/out, độ dài, lý do kết tập, nguồn transcript và giới hạn kiểm chứng. Nếu yêu cầu cắt thì tiếp tục xuất clip; nếu chỉ yêu cầu kế hoạch thì dừng ở kế hoạch. Không tự thêm bước xin duyệt.
6. Xuất bằng FFmpeg. Đọc [hợp đồng render và kiểm tra](references/render.md), dùng `scripts/render_episodes.py` cho encode H.264/AAC thông thường. Giữ tỷ lệ, kích thước hiển thị và nhịp hình nguồn; không ép mọi video thành 30 fps. Cắt chính xác thường cần encode lại; stream copy chỉ dùng khi phù hợp keyframe và chấp nhận sai lệch. Không gọi encode lại là lossless.
7. Kiểm tra đủ ep và mỗi ep đúng một title trong TXT UTF-8. Title dùng cùng tên phim và một kiểu hậu tố (EpNN) hoặc (PartNN), đánh số liên tục từ 01. Kiểm tra filename MP4 thực tế bằng nguyên title + `.mp4`, không hashtag hoặc tiền tố Unicode. Nếu sai, sửa file thực tế và cập nhật TXT, cutlist, report, manifest liên quan.
8. Kiểm tra metadata từng file, thời lượng so với cutlist, audio nếu nguồn có, khả năng decode và khung hình đầu/cuối. Nghe/xem joins để xác nhận mạch truyện và sync; script không thay thế QA nội dung. Sửa ep lỗi rồi kiểm tra lại ep bị ảnh hưởng. Báo rõ nếu chỉ kiểm tra bằng metadata/ảnh mà chưa nghe.

## Giao kết quả

Link folder output và `titles.txt`, nêu số ep, khoảng thời lượng, ngoại lệ và hạn chế QA còn lại. Với batch, báo theo từng video và tiếp tục các video độc lập nếu một file lỗi; không báo hoàn tất khi render còn chạy. Không đăng tải lên nền tảng khi chưa có yêu cầu.

Skill rút từ session `01a14984-3c9d-7073-af2e-d2799b694bc1`: thử nghiệm đã xuất 6 ep từ video 20:43 bằng OCR local + FFmpeg. Đường dẫn, nhân vật và mốc thử nghiệm không phải mặc định cho video mới. Lượt batch 3 video còn đang chạy lúc đọc session, không được coi là bằng chứng đã hoàn thành.
