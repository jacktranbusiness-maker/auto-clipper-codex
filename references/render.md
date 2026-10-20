# Render và kiểm tra

## Cutlist

CSV UTF-8, mỗi hàng một ep, dùng giây thập phân:

```csv
episode,start_seconds,end_seconds,filename,story_beat
1,0,210,A Rabbit Shifter's Fated Match (Part1).mp4,A complete beat followed by a new conflict
2,210,430,A Rabbit Shifter's Fated Match (Part2).mp4,The next beat resolves
```

Filename là nguyên title đề xuất (lựa chọn 1) + `.mp4`: tên series dùng nhất quán và hậu tố `(Ep01)`, `(Ep02)`, … hoặc `(Part1)`, `(Part2)`, … đúng số phần. Ví dụ `Her Husband's Love Kept Her From Heaven (Ep01).mp4`. Theo kiểu người dùng/title gốc, mặc định dùng `Part` nếu chưa có; số ASCII, `Ep` ít nhất 2 chữ số, `Part` không thêm số 0 phía trước. Title và filename mặc định không có hashtag hoặc tiền tố Episode Unicode. Chọn tên series biên tập theo quy tắc trong `SKILL.md`, rồi chốt title trước khi ghi cutlist để helper xuất đúng tên ngay từ đầu. Mốc ví dụ chỉ minh họa schema; mỗi ep/part mục tiêu 180–250 giây. Có thể thêm `duration_seconds`; helper tính từ in/out. Mốc bắt đầu ep sau bằng mốc kết ep trước; cuối cùng bằng thời lượng nguồn. Thời gian quy về timeline nguồn bắt đầu từ 0.

## Helper

Yêu cầu Python 3 standard library, `ffmpeg`, `ffprobe` trong PATH. Không tự cài dependency hệ thống.

```bash
python3 <skill-dir>/scripts/render_episodes.py --source '/path/video.mp4' --cutlist '/path/cutlist.csv' --output '/path/output-codex/Source Stem' --check-only
python3 <skill-dir>/scripts/render_episodes.py --source '/path/video.mp4' --cutlist '/path/cutlist.csv' --output '/path/output-codex/Source Stem'
```

Helper kiểm tra cutlist, từ chối output file đã tồn tại, xuất tuần tự vào file `.partial.mp4` rồi rename sau kiểm tra. Đọc `render_report.json` để biết kết quả kỹ thuật. Encode mặc định libx264 CRF 19 / veryfast, AAC 192k, yuv420p, faststart; có `--crf` và `--preset`. Chọn stream bằng `0:v:0` và `0:a:0?`, không dựa vào thứ tự stream toàn cục. Nguồn không audio vẫn xuất được. Không thêm fade mặc định; fade rất ngắn chỉ cân nhắc khi có tiếng click và không che lời thoại.

Helper dành cho video SDR thông thường có kích thước chẵn; nguồn HDR, nhiều audio track cần giữ, kích thước lẻ hoặc rotation bất thường cần chuẩn bị lệnh phù hợp riêng, không âm thầm đổi màu hoặc nội dung. Helper không tự chọn mốc, tạo title hay đảm bảo chất lượng nội dung. Output có thể lớn hơn source sau encode lại.

Nếu render gián đoạn, kiểm tra report và file đã xuất. Để render lại ep lỗi, dùng lệnh FFmpeg riêng theo cùng mốc/setting hoặc dùng folder mới. Cutlist tạm chỉ chứa ep lỗi không thỏa full coverage. Không xóa output cũ của người dùng để chạy lại.

## QA

- Full coverage là invariant của cutlist, không suy ra chỉ từ tổng duration MP4; container/audio padding có thể lệch vài phần giây.
- So sánh từng ep với in/out; helper từ chối sai lệch quá 0.25 giây. Với nguồn fps rất thấp cần đánh giá tolerance riêng.
- Đối chiếu hình hiển thị, fps/time base, codec, audio; nghe vài giây hai phía **mọi** join.
- Kiểm tra decode: `ffmpeg -v error -i <clip> -f null -`. Đây là kiểm tra đọc/giải mã, không xác nhận nội dung hay sync cảm nhận.
- Kiểm tra thời lượng mục tiêu 180–250 giây cho từng ep/part; cân lại mốc liền kề để tránh đuôi quá ngắn. Ghi trong `split_plan.md` lý do tập ngoài khoảng và QA đã thực sự thực hiện.
