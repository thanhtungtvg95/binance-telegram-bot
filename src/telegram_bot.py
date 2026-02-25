import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.binance_service import BinanceService
from src.analyzer import Analyzer

class TGNotificationBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        
        self.binance_service = BinanceService()
        self.analyzer = Analyzer(self.binance_service)

    def format_message(self, results: list) -> str:
        if not results:
            return "✅ Hiện tại không có cặp coin nào có 4-6 cây nến 4H xanh liên tiếp."

        # Sort results by percentage change descending and take top 5
        sorted_results = sorted(results, key=lambda x: x['pct_change'], reverse=True)[:5]
            
        message = "🚨 <b>BÁO CÁO SCAN FUTURES (TOP 5 TĂNG MẠNH NHẤT)</b> 🚨\n\n"
        message += f"Tìm thấy <b>{len(results)}</b> cặp coin thỏa mãn điều kiện. Hiển thị top {len(sorted_results)}:\n\n"
        
        for idx, res in enumerate(sorted_results):
            symbol = res['symbol'].replace('/', '_') # Lách lỗi markdown/html đôi khi trên telegram
            green_count = res['consecutive_green']
            pct = res['pct_change']
            funding = res['funding_rate']
            rsi = res['rsi']
            
            # Đưa ra gợi ý Short rõ ràng hơn
            advice = "Neutral"
            if rsi > 75 and funding > 0.01:
                advice = "🔥 <b>RẤT NÊN SHORT</b> (RSI quá mua nặng + Funding cao)"
            elif rsi > 70:
                advice = "⚠️ <b>CÂN NHẮC SHORT</b> (RSI quá mua, chờ nến đảo chiều)"
            else:
                advice = "⏳ <b>QUAN SÁT THÊM</b> (Chưa đủ điều kiện an toàn để Short)"
                
            message += f"🟢 <b>{symbol}</b>\n"
            message += f"📈 Tăng liên tục: <b>{green_count} nến 4H</b> (<b>+{pct:.2f}%</b>)\n"
            message += f"💰 Funding Rate: <b>{funding:.4f}%</b>\n"
            message += f"📊 RSI(14): <b>{rsi:.2f}</b>\n"
            message += f"💡 Gợi ý: {advice}\n"
            
            message += "<pre>"
            message += "Thời gian      Mở     Đóng\n"
            message += "--------------------------\n"
            for candle in res['candles']:
                time_str = candle['timestamp'][5:] # Bỏ năm cho gọn
                o_str = f"{candle['open']:.4f}"
                c_str = f"{candle['close']:.4f}"
                message += f"{time_str} {o_str:>8} {c_str:>8}\n"
            message += "</pre>\n"
            
            if idx < len(sorted_results) - 1:
                message += "=====================\n\n"

        # Vì chỉ lấy top 5 nên không lo vượt quá 4000 ký tự nữa,
        # và không cắt ngang tag <pre> gây lỗi parse entities.
        return message

    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for /scan command."""
        await update.message.reply_text("🔄 Đang tiến hành quét thị trường Binance Futures... Vui lòng đợi trong giây lát.")
        
        try:
            results = self.analyzer.analyze_markets()
            msg = self.format_message(results)
            await update.message.reply_html(msg)
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi xảy ra trong quá trình scan: {e}")

    async def scheduled_scan(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for scheduled jobs."""
        try:
            results = self.analyzer.analyze_markets()
            if results: # Chỉ gửi nếu có kết quả để tránh spam
                msg = self.format_message(results)
                await context.bot.send_message(chat_id=self.chat_id, text=msg, parse_mode='HTML')
        except Exception as e:
            print(f"Error in scheduled scan: {e}")

    def run(self, default_interval_minutes: int = 240):
        """Run the bot."""
        app = Application.builder().token(self.token).build()

        # Add command handler
        app.add_handler(CommandHandler("scan", self.scan_command))
        
        # Add job queue for periodic scanning
        job_queue = app.job_queue
        # Convert minutes to seconds
        job_queue.run_repeating(self.scheduled_scan, interval=default_interval_minutes * 60, first=10)

        print(f"Bot started. Scheduled to run every {default_interval_minutes} minutes.")
        print("You can also send /scan to the bot at any time.")
        # Run the bot until the user presses Ctrl-C
        app.run_polling(allowed_updates=Update.ALL_TYPES)
