import pandas as pd
from typing import List, Dict, Any
from .binance_service import BinanceService

class Analyzer:
    def __init__(self, binance_service: BinanceService):
        self.binance_service = binance_service

    def calculate_rsi(self, df: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)."""
        delta = df.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def analyze_markets(self) -> List[Dict[str, Any]]:
        """
        Scan all USDT futures limits, look for 4 to 6 consecutive green 4H candles,
        and calculate metrics like RSI, % change, and funding rate for shorting strategy.
        """
        results = []
        symbols = self.binance_service.get_usdt_futures_symbols()
        
        # For a quick test we limit if symbols is too large or just process them all
        # To avoid being blocked, we just iterate normally
        
        for symbol in symbols:
            # We fetch 30 candles to have enough data for RSI(14) calculation
            df = self.binance_service.get_ohlcv(symbol, timeframe='4h', limit=30)
            if df.empty or len(df) < 15:
                continue

            recent_candles = df.tail(6).copy()
            # Green candle condition: close > open
            recent_candles['is_green'] = recent_candles['close'] > recent_candles['open']
            
            # Count consecutive green candles looking backwards from the most recent one
            consecutive_green = 0
            for is_green in reversed(recent_candles['is_green'].tolist()):
                if is_green:
                    consecutive_green += 1
                else:
                    break
            
            # Check if it has 4 to 6 consecutive green candles
            if 4 <= consecutive_green <= 6:
                # Calculate RSI
                df['rsi'] = self.calculate_rsi(df['close'], 14)
                current_rsi = df['rsi'].iloc[-1]
                
                if pd.isna(current_rsi):
                    current_rsi = 50.0 # Default fallback
                
                # Calculate % price change over these consecutive green candles
                start_candle = recent_candles.iloc[-consecutive_green]
                end_candle = recent_candles.iloc[-1]
                
                start_price = start_candle['open']
                end_price = end_candle['close']
                pct_change = ((end_price - start_price) / start_price) * 100
                
                # Fetch funding rate (only for symbols that matched to save API calls)
                funding_rate = self.binance_service.get_funding_rate(symbol)
                
                # Suggest shorting strategy
                if current_rsi > 70:
                    strategy = "🔴 Gợi ý Short: RSI vượt mức 70 (Quá mua). Cân nhắc Short với stoploss chặt."
                elif current_rsi > 60:
                    strategy = "🟡 Theo dõi: Giá tăng mạnh nhưng RSI chưa vào vùng quá mua rõ ràng."
                else:
                    strategy = "⚪ Không rõ ràng: Cần thêm tín hiệu xác nhận."

                # Get details of the green candles to include in the report
                candle_details = []
                for i in range(consecutive_green):
                    idx = -consecutive_green + i
                    c = recent_candles.iloc[idx]
                    candle_details.append({
                        'open': float(c['open']),
                        'close': float(c['close']),
                        'high': float(c['high']),
                        'low': float(c['low']),
                        'timestamp': c['timestamp'].strftime('%Y-%m-%d %H:%M')
                    })

                results.append({
                    'symbol': symbol,
                    'consecutive_green': consecutive_green,
                    'pct_change': pct_change,
                    'funding_rate': funding_rate * 100,  # to percentage
                    'rsi': current_rsi,
                    'strategy': strategy,
                    'candles': candle_details
                })
                
        # Sort by consecutive green (descending) and pct_change (descending)
        results.sort(key=lambda x: (x['consecutive_green'], x['pct_change']), reverse=True)
        return results
