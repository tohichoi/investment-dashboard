import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Mock Calculation Logic (Same as app.py & monitor_worker.py) ---

def calculate_atr_logic(df, period=14):
    """Calculate ATR (Average True Range) for volatility-based alerts."""
    high = df['High']
    low = df['Low']
    close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def check_strategies_logic(stock_config, df):
    """
    Simulation of monitor_worker.py's strategy checking logic.
    Returns a list of triggered alert messages.
    """
    curr = df['Close'].iloc[-1]
    ratio = stock_config.get('ratio', -5.0)
    atr_mult = stock_config.get('atr_mult', 2.0)
    strategies = stock_config.get('strategies', [])
    results = []

    for strat in strategies:
        if strat == "max_drop":
            ref = df['High'].max()
            target = ref * (1 + ratio / 100)
            if curr <= target:
                results.append(f"📉 최고가 하락: 고점({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 이하 도달")
        
        elif strat == "min_rise":
            ref = df['Low'].min()
            target = ref * (1 + ratio / 100)
            if curr >= target:
                results.append(f"📈 저점 반등: 저점({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 이상 도달")
        
        elif strat == "avg_gap":
            ref = df['Close'].mean()
            target = ref * (1 + ratio / 100)
            is_above = ratio >= 0
            if (is_above and curr >= target) or (not is_above and curr <= target):
                results.append(f"⚖️ 평균가 이격: 평균({ref:,.0f}) 대비 {ratio}% 지점({target:,.0f}) 도달")
        
        elif strat == "atr_trailing":
            atr = df['ATR'].iloc[-1]
            # Simple trailing support: 5-day moving average - (ATR * multiplier)
            ref_ma = df['Close'].tail(5).mean()
            target = ref_ma - (atr * atr_mult)
            if curr <= target:
                results.append(f"🛡️ ATR 지지선 붕괴: 지지선({target:,.0f}) 이하 도달 (ATR: {atr:,.2f})")

    return results

# --- Mock Data Generation ---

def generate_scenario_data(scenario_type="stable"):
    """Generates 100 days of mock stock data based on scenarios."""
    dates = [datetime.now() - timedelta(days=i) for i in range(100)]
    dates.reverse()
    base_price = 100000
    np.random.seed(42)

    if scenario_type == "crash":
        # Price rises then crashes (to test max_drop)
        prices = [base_price * (1 + 0.01*i if i < 70 else 1.7 - 0.03*(i-70)) for i in range(100)]
    elif scenario_type == "rebound":
        # Price falls then rebounds (to test min_rise)
        prices = [base_price * (1 - 0.005*i if i < 80 else 0.6 + 0.02*(i-80)) for i in range(100)]
    elif scenario_type == "volatile":
        # High volatility (to test ATR)
        prices = base_price + np.random.normal(0, 3000, 100).cumsum()
    else:
        # Stable oscillation
        prices = [base_price + 2000 * np.sin(i/5) for i in range(100)]

    df = pd.DataFrame({
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices
    }, index=dates)
    
    df['ATR'] = calculate_atr_logic(df)
    return df

# --- Main Test Runner ---

def run_integration_test():
    print("="*60)
    print("🚀 주식 모니터링 시스템 통합 로직 테스트 (Simulation)")
    print("="*60)

    test_suites = [
        {
            "case": "Scenario 1: 고점 대비 15% 급락 상황",
            "scenario": "crash",
            "config": {
                "name": "급락주",
                "strategies": ["max_drop", "avg_gap"],
                "ratio": -15.0
            }
        },
        {
            "case": "Scenario 2: 저점 대비 10% 반등 상황",
            "scenario": "rebound",
            "config": {
                "name": "반등주",
                "strategies": ["min_rise"],
                "ratio": 10.0
            }
        },
        {
            "case": "Scenario 3: 변동성 확대 및 ATR 지지선 테스트",
            "scenario": "volatile",
            "config": {
                "name": "변동성종목",
                "strategies": ["atr_trailing"],
                "atr_mult": 1.5
            }
        }
    ]

    for test in test_suites:
        print(f"\n📌 테스트 케이스: {test['case']}")
        df = generate_scenario_data(test['scenario'])
        config = test['config']
        
        # Run logic
        alerts = check_strategies_logic(config, df)
        
        curr_price = df['Close'].iloc[-1]
        print(f"   [상태] 종목명: {config['name']} | 현재가: {curr_price:,.0f}원")
        
        if alerts:
            print(f"   ✅ 알림 발생 ({len(alerts)}건):")
            for a in alerts:
                print(f"      >> {a}")
        else:
            print("   ❌ 조건 미충족 (알림 없음)")
        print("-" * 40)

    print("\n✅ 모든 시뮬레이션 테스트가 완료되었습니다.")

if __name__ == "__main__":
    run_integration_test()