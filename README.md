# Binance Futures Telegram Bot

Bot Telegram giúp theo dõi thị trường Binance Futures, tìm kiếm các đồng coin đang có chuỗi 4-6 cây nến 4H tăng giá liên tiếp và gửi thông báo cho bạn kèm theo phí funding, mức độ tăng, và gợi ý chiến lược Short.

## Tính năng
- Scan toàn bộ các cặp giao dịch USDT Futures trên Binance.
- Lọc các cặp có 4 đến 6 nến 4H xanh (nến tăng) liên tiếp.
- Tính toán % thay đổi giá trong đợt tăng.
- Tính toán chỉ số RSI để đưa ra gợi ý chiến lược Short khi giá ở vùng quá mua (>70).
- Hiển thị Funding Rate hiện tại để tham khảo phí nắm giữ vị thế.
- Bot có thể **chạy định kỳ** (VD: mỗi 4 tiếng) và **nhận lệnh /scan** trực tiếp trên Telegram.

## Yêu cầu
- Python 3.10+

## Cài đặt và Chạy

1. Cài đặt các thư viện yêu cầu:
   ```bash
   pip install -r requirements.txt
   ```

2. Cấu hình biến môi trường:
   - Copy file `.env.example` thành `.env`
   - Điền Token Telegram của bot bạn vào biến `TELEGRAM_BOT_TOKEN`.
   - Điền ID Chat của bạn vào `TELEGRAM_CHAT_ID` để bot biết gửi tin nhắn tự động vào đâu.
   - Sửa đổi chu kỳ quét (mặc định 240 phút = 4 tiếng) nếu cần ở biến `SCAN_INTERVAL`.

3. Chạy Bot:
   ```bash
   python main.py
   ```

## Sử dụng
- Gửi lệnh `/scan` trên bot Telegram để quét ngay lập tức.
- Bot cũng sẽ tự động quét và gửi tin nhắn về cho bạn theo chu kỳ đã đặt trong `SCAN_INTERVAL`.
