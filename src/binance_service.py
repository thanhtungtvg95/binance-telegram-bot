import ccxt
import pandas as pd
from typing import List

class BinanceService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'options': {
                'defaultType': 'future',
            },
            'enableRateLimit': True,
        })
        # Load market data on initialization
        self.exchange.load_markets()

    def get_usdt_futures_symbols(self) -> List[str]:
        """Fetch all active USDT-Margined Futures symbols."""
        markets = self.exchange.markets
        symbols = []
        for symbol, market in markets.items():
            if market.get('linear') and market.get('active') and market.get('quote') == 'USDT':
                symbols.append(symbol)
        return symbols

    def get_ohlcv(self, symbol: str, timeframe: str = '4h', limit: int = 7) -> pd.DataFrame:
        """Fetch historical candlestick data for a given symbol."""
        try:
            # fetch_ohlcv returns: [ [timestamp, open, high, low, close, volume], ... ]
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()

    def get_funding_rate(self, symbol: str) -> float:
        """Fetch the current funding rate for a symbol."""
        try:
            funding = self.exchange.fetch_funding_rate(symbol)
            return funding.get('fundingRate', 0.0)
        except Exception as e:
            print(f"Error fetching funding rate for {symbol}: {e}")
            return 0.0
