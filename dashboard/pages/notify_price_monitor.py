import yfinance as yf
import time
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# --- Configuration & Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "stocks_config.json"
LOG_FILE = BASE_DIR / "monitor_log.txt"

def load_config():
    """Load settings and stock list from the JSON configuration file."""
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def write_log(message):
    """Write system logs to a text file with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(log_entry)
    print(log_entry.strip())

def send_telegram(token, chat_id, message):
    """Send alert messages via Telegram Bot API."""
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception as e:
        print(f"Telegram API Error: {e}")

def calculate_atr(df, period=14):
    """Calculate Average True Range (ATR) for volatility checking."""
    high = df['High']
    low = df['Low']
    close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def check_stock_strategies(stock, token, chat_id):
    """Execute monitoring logic for each assigned strategy."""
    code = stock['code']
    days = stock.get('days', 90)
    ratio = stock.get('ratio', -5.0)
    atr_mult = stock.get('atr_mult', 2.0)
    strategies = stock.get('strategies', [])
    
    try:
        ticker = yf.Ticker(code)
        # Fetch extra data for accurate ATR (14 period) and Moving Average calculations
        df = ticker.history(start=(datetime.now() - timedelta(days=days + 30)).strftime('%Y-%m-%d'))
        if df.empty:
            return
        
        # Calculate Technical Indicators
        df['ATR'] = calculate_atr(df)
        
        # Current status
        curr = df['Close'].iloc[-1]
        results = []
        
        # Logic for each selected strategy
        for strat in strategies:
            if strat == "max_drop":
                # High-water mark drop
                ref = df['High'].tail(days).max()
                target = ref * (1 + ratio / 100)
                if curr <= target:
                    results.append(f"📉 최고가 하락: 고점({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 이하")
            
            elif strat == "min_rise":
                # Low-water mark rebound
                ref = df['Low'].tail(days).min()
                target = ref * (1 + ratio / 100)
                if curr >= target:
                    results.append(f"📈 저점 반등: 저점({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 이상")
            
            elif strat == "avg_gap":
                # Moving Average deviation
                ref = df['Close'].tail(days).mean()
                target = ref * (1 + ratio / 100)
                is_above = ratio >= 0
                if (is_above and curr >= target) or (not is_above and curr <= target):
                    results.append(f"⚖️ 평균가 이격: 평균({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 도달")

            elif strat == "atr_trailing":
                # Volatility-based support (Trailing Stop/Support)
                atr = df['ATR'].iloc[-1]
                # Use 5-day MA as a baseline for trailing support
                ref_ma = df['Close'].tail(5).mean()
                target = ref_ma - (atr * atr_mult)
                if curr <= target:
                    results.append(f"🛡️ ATR 지지선 붕괴: 지지선({target:,.0f}) 이하 도달 (ATR: {atr:,.2f}, 배수: {atr_mult})")

        if results:
            msg = f"🚨 [감시 조건 도달] {stock['name']}({code.split('.')[0]})\n"
            msg += f"현재가: {curr:,.0f}원\n"
            msg += "\n".join(results)
            send_telegram(token, chat_id, msg)
            write_log(f"ALERT SENT: {stock['name']} triggered {len(results)} strategy(s).")
            
    except Exception as e:
        write_log(f"Error processing {code}: {e}")

def run_monitor():
    """Main background loop to check stocks based on configured intervals."""
    write_log("Stock Monitor Worker Started. (ATR Strategy Integrated)")
    last_check_time = datetime.min
    
    while True:
        config = load_config()
        if not config:
            time.sleep(10)
            continue
            
        interval = config.get("interval_min", 10)
        # Check if the interval has passed
        if (datetime.now() - last_check_time).total_seconds() / 60.0 >= interval:
            stocks = config.get("stocks", [])
            token = config.get("telegram_token")
            chat_id = config.get("telegram_chat_id")
            
            if stocks:
                write_log(f"Starting check cycle for {len(stocks)} stocks...")
                for stock in stocks:
                    check_stock_strategies(stock, token, chat_id)
                write_log("Check cycle completed.")
            else:
                write_log("No stocks registered in config.")
                
            last_check_time = datetime.now()
        
        # Sleep briefly before next config check
        time.sleep(30)

if __name__ == "__main__":
    run_monitor()