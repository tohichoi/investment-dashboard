import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# --- Configuration & Constants ---
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "stocks_config.json"
LOG_FILE = BASE_DIR / "monitor_log.txt"

# --- Data Persistence Functions ---
def load_data():
    default_data = {
        "telegram_token": "",
        "telegram_chat_id": "",
        "interval_min": 10,
        "stocks": []
    }
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_data, **data}
        except Exception:
            return default_data
    return default_data

def save_data(config_data):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"저장 오류: {e}")

@st.cache_data(ttl=86400)
def get_combined_stock_list():
    try:
        stock_url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        stocks = pd.read_html(stock_url, header=0, encoding='cp949')[0][['회사명', '종목코드']]
        stocks['type'] = 'Stock'
        
        etf_url = "https://finance.naver.com/api/sise/etfItemList.nhn"
        etfs = pd.DataFrame(requests.get(etf_url).json()['result']['etfItemList'])
        etfs = etfs[['itemname', 'itemcode']].rename(columns={'itemname': '회사명', 'itemcode': '종목코드'})
        etfs['type'] = 'ETF'

        df = pd.concat([stocks, etfs], ignore_index=True)
        df['종목코드'] = df['종목코드'].astype(str).str.zfill(6)
        df = df.drop_duplicates(subset=['종목코드'])
        df['display_name'] = "[" + df['type'] + "] " + df['회사명'] + " (" + df['종목코드'] + ")"
        return df.sort_values(by='회사명')
    except Exception:
        return pd.DataFrame(columns=['회사명', '종목코드', 'display_name', 'type'])

def calculate_atr(df, period=14):
    """Calculate ATR (Average True Range)"""
    high = df['High']
    low = df['Low']
    close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def get_market_data(ticker_code, period_days):
    try:
        for suffix in [".KS", ".KQ"]:
            full_ticker = ticker_code + suffix
            stock = yf.Ticker(full_ticker)
            # ATR 계산을 위해 14일 정도 더 여유있게 데이터를 가져옴
            df = stock.history(start=(datetime.now() - timedelta(days=period_days + 30)).strftime('%Y-%m-%d'))
            if not df.empty:
                df['ATR'] = calculate_atr(df)
                return df.tail(period_days), (stock.info.get('longName') or ticker_code), full_ticker
        return None, None, None
    except Exception:
        return None, None, None

def get_last_logs(n=20):
    if LOG_FILE.exists():
        with LOG_FILE.open("r", encoding="utf-8") as f:
            return f.readlines()[-n:][::-1]
    return ["로그가 없습니다. 워커를 실행해 주세요."]

def notify_price_threshold_index():
    """Main application function for price threshold monitoring UI."""
    if 'app_data' not in st.session_state:
        st.session_state.app_data = load_data()
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    stock_df = get_combined_stock_list()

    st.title("🖥️ 주식/ETF 다중 조건 및 변동성(ATR) 모니터링")

    with st.expander("⚙️ 시스템 설정", expanded=False):
        c1, c2, c3 = st.columns([2, 1, 1])
        new_token = c1.text_input("텔레그램 토큰", value=st.session_state.app_data.get("telegram_token", ""), type="password")
        new_chat_id = c2.text_input("Chat ID", value=st.session_state.app_data.get("telegram_chat_id", ""))
        new_interval = c3.number_input("주기(분)", min_value=1, value=st.session_state.app_data.get("interval_min", 10))
        
        if st.button("설정 저장", type="primary"):
            st.session_state.app_data.update({"telegram_token": new_token, "telegram_chat_id": new_chat_id, "interval_min": new_interval})
            save_data(st.session_state.app_data)
            st.success("저장 완료")

    st.divider()
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("1️⃣ 종목 및 전략 설정")
        with st.container(border=True):
            selected_label = st.selectbox("종목 검색", options=stock_df['display_name'].tolist() if not stock_df.empty else [], index=None)
            
            # ATR 전략을 옵션에 추가
            strategy_options = ["최고가 대비 하락", "최저가 대비 반등", "평균가 대비 이격", "ATR 변동성 추적 (지지)"]
            selected_strategies = st.multiselect(
                "감시 기준 선택 (중복 가능)",
                options=strategy_options,
                default=["최고가 대비 하락"]
            )
            
            c_opt1, c_opt2, c_opt3 = st.columns(3)
            days_input = c_opt1.number_input("기준 기간 (일)", min_value=1, max_value=365, value=90)
            ratio_input = c_opt2.number_input("알림 비율 (%)", value=-5.0, step=0.1, help="기존 전략(가격 대비)에서 사용")
            atr_mult_input = c_opt3.number_input("ATR 배수", value=2.0, step=0.1, help="ATR 전략 선택 시 사용 (보통 2.0~3.0)")

            if st.button("🔍 데이터 분석 미리보기", use_container_width=True):
                if not selected_label or not selected_strategies:
                    st.warning("종목과 기준을 선택하세요.")
                else:
                    code = stock_df[stock_df['display_name'] == selected_label]['종목코드'].values[0]
                    with st.spinner("분석 중..."):
                        df, name, full_ticker = get_market_data(code, days_input)
                        if df is not None:
                            last_atr = df['ATR'].iloc[-1]
                            current_p = df['Close'].iloc[-1]
                            st.session_state.preview_data = {
                                "code": full_ticker, "name": name, "days": days_input, "ratio": ratio_input, "atr_mult": atr_mult_input,
                                "strategies": selected_strategies, "current_p": current_p,
                                "max_p": df['High'].max(), "min_p": df['Low'].min(), "avg_p": df['Close'].mean(),
                                "atr": last_atr
                            }
                        else: st.error("데이터 로드 실패")

            if st.session_state.preview_data:
                p = st.session_state.preview_data
                st.info(f"💡 **{p['name']}** 현재가: {p['current_p']:,.0f}원\n\n"
                        f"- 최고: {p['max_p']:,.0f} | 최저: {p['min_p']:,.0f} | 평균: {p['avg_p']:,.0f} | **ATR(14): {p['atr']:,.2f}**")
                
                # ATR 전략 선택 시 예상 도달가 보여주기
                if "ATR 변동성 추적 (지지)" in p['strategies']:
                    atr_target = p['current_p'] - (p['atr'] * p['atr_mult'])
                    st.warning(f"🛡️ ATR 지지선 알림 예정: {atr_target:,.0f}원 이하 도달 시 (현재가 - {p['atr_mult']}*ATR)")

                if st.button("✅ 감시 목록에 추가", use_container_width=True):
                    strat_map = {
                        "최고가 대비 하락": "max_drop", 
                        "최저가 대비 반등": "min_rise", 
                        "평균가 대비 이격": "avg_gap",
                        "ATR 변동성 추적 (지지)": "atr_trailing"
                    }
                    new_stock = {
                        "code": p['code'], "name": p['name'], "days": int(p['days']), 
                        "ratio": float(p['ratio']), "atr_mult": float(p['atr_mult']),
                        "strategies": [strat_map[s] for s in p['strategies']]
                    }
                    st.session_state.app_data["stocks"].append(new_stock)
                    save_data(st.session_state.app_data)
                    st.session_state.preview_data = None
                    st.rerun()

        st.subheader("📋 실시간 감시 목록")
        if st.session_state.app_data["stocks"]:
            # 데이터프레임 표시를 위해 키 값 확인 (atr_mult가 없는 기존 데이터 호환성)
            display_df = pd.DataFrame(st.session_state.app_data["stocks"])
            if 'atr_mult' not in display_df.columns: display_df['atr_mult'] = 2.0
            
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "code": st.column_config.TextColumn("코드", disabled=True),
                    "name": st.column_config.TextColumn("종목명", disabled=True),
                    "strategies": st.column_config.ListColumn("전략"),
                    "days": st.column_config.NumberColumn("기간"),
                    "ratio": st.column_config.NumberColumn("비율(%)"),
                    "atr_mult": st.column_config.NumberColumn("ATR배수")
                },
                num_rows="dynamic", use_container_width=True
            )
            if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
                st.session_state.app_data["stocks"] = edited_df.to_dict('records')
                save_data(st.session_state.app_data)
                st.rerun()
        else: st.info("등록된 종목이 없습니다.")

    with col2:
        st.subheader("📡 워커 로그")
        logs = get_last_logs(20)
        st.text_area("Live Logs", value="".join(logs), height=600)
        if st.button("🔄 로그 새로고침"): st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="주식 모니터링", layout="wide")
    notify_price_threshold_index()