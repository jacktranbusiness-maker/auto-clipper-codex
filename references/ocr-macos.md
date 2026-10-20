# OCR phụ đề đốt trên hình bằng macOS Vision

Dùng khi máy là macOS, có `swiftc`, phụ đề đọc được trên hình và không có subtitle track/sidecar tốt hơn, hoặc cần kiểm tra một vùng SRT nghi sai theo [quy trình SRT YouTube](subtitles.md). Nếu SRT đã khớp qua kiểm tra mẫu, chỉ OCR vùng còn nghi vấn.

1. Trích khung hình ở đầu, giữa và cuối để xác định vùng phụ đề. Vision dùng tọa độ chuẩn hóa có gốc **góc dưới trái**, khác crop pixel FFmpeg. Tránh logo, chữ title và watermark; không lấy crop của video trước cho mọi video.
2. Biên dịch helper vào folder scratch riêng của job:

```bash
swiftc -O <skill-dir>/scripts/subtitle_ocr.swift -o /path/scratch/subtitle-ocr
/path/scratch/subtitle-ocr '/path/source.mp4' '/path/scratch/ocr.tsv' 1 en-US 0.03 0.08 0.94 0.42
```

Tham số sau output: bước lấy mẫu giây, ngôn ngữ Vision, ROI x/y/width/height. Crop ví dụ là điểm khởi đầu cho phụ đề phía dưới video dọc, cần xem mẫu thực tế. Helper ghi TSV `seconds<TAB>text`, progress vào stderr, lỗi nếu không đọc được frame nào. Không coi khoảng TSV trống là cảnh không thoại.

3. Đọc mẫu kết quả trước khi chạy batch; chỉnh crop/ngôn ngữ nếu bắt chữ rác hoặc hụt phụ đề. Gộp câu lặp theo thời gian để đọc nhưng giữ TSV raw. Không xóa câu giống nhau ở cảnh xa nhau.
4. Khi thiếu transcript đáng dùng trên toàn nguồn, quét phủ video để hiểu truyện; lỗi frame được đếm trong log. Khi chỉ một vùng SRT nghi sai, trích clip tạm của vùng đó và chạy helper trên clip: helper hiện quét hết file đầu vào, không có tham số start/end. Cộng thời điểm bắt đầu clip vào timestamp OCR để quy về nguồn; giữ nguyên video gốc. Vùng thiếu dữ liệu cần ảnh/audio bổ sung trước khi chốt mốc. Với candidate boundary, rà cửa sổ ±5–10 giây và tinh chỉnh tới frame thích hợp; không tiếp tục quét rộng khi nghi vấn đã được giải quyết.

AVFoundation API đồng bộ trong helper có thể phát deprecation warnings trên macOS mới; biên dịch và thử sample thực tế để xác nhận hoạt động. Nếu không có Vision, dùng OCR/ASR local có sẵn phù hợp và ghi rõ nguồn timestamp.
