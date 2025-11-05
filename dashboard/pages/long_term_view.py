import sqlite3
from typing import Tuple
import streamlit as st
import pandas as pd
import streamlit.components.v1 as st_components
from config import COLUMN_KEY_DESC, DATE_PRESETS, DOWNLOAD_DATA_DIR
from dashboard.downloader.kis import date_converter, download_data, update_or_read_database
from downloader.ecos import M2_ITEM_CODES, get_exchange_rate, get_m2_money_supply, get_stock_market_funds
import humanize

from pages.short_term_view import get_period, show_current_to_mean_ratio
# import altair as alt


def get_dataset_path(dataset):
    return DOWNLOAD_DATA_DIR / f"{dataset}.xlsx"



def show_search_forms():
    with st.form('search_form'):
        selected_period = st.select_slider(
            "Select Date Range",
            options=DATE_PRESETS.keys(),
            format_func=lambda x: DATE_PRESETS[x]['label'],
            value="14d",
            key="date_range"
        )
        
        st.session_state.selected_period = selected_period
        st.form_submit_button('조회')

    
@st.cache_data
def st_get_m2_money_supply(start_date:str, end_date:str) -> pd.DataFrame:
    return get_m2_money_supply(start_date, end_date)

    
def show_basic_statistics():
    start_date, end_date = get_period(st.session_state.selected_period)

    st.header('M2 Liquidity', divider=True)
    m2_money_supply = st_get_m2_money_supply(start_date, end_date)
    
    cols = st.columns(5, border=True)        
    for item_code, col in zip(M2_ITEM_CODES, cols):
        with col:
            df_filter = m2_money_supply[m2_money_supply['ITEM_CODE1']==item_code].copy()
            df_filter.rename(columns={'DATA_VALUE': item_code}, inplace=True)
            show_current_to_mean_ratio(df_filter, item_code, 1.0, item_code)        
            # st.metric(label="USD/KRW", value=df['DATA_VALUE'].iloc[0], delta="+5.30", help="미국 달러 대비 원화 환율입니다.")
    with st.expander('원본 데이터 보기'):
        st.dataframe(df_filter)

    # 증시자금 추이
    st.header('Stock Market Funds', divider=True)    
    df_stock_market_funds = get_stock_market_funds(start_date, end_date)
    df_filter = df_stock_market_funds[df_stock_market_funds['ITEM_CODE1']==item_code].copy()
    df_filter.rename(columns={'DATA_VALUE': item_code}, inplace=True)
    with st.expander('원본 데이터 보기'):
        st.dataframe(df_stock_market_funds)
    
    
def index():
    st.title("Data Overview")
        
    show_search_forms()
    
    show_basic_statistics()
    

index()