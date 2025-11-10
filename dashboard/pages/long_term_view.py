import sqlite3
from typing import Tuple
import streamlit as st
import pandas as pd
import streamlit.components.v1 as st_components
from config import COLUMN_KEY_DESC, DATE_PRESETS, DOWNLOAD_DATA_DIR, M2_ITEM_CODES, STOCK_MARKET_FUNDS_ITEM_CODES, save_settings, settings
from downloader.kis import date_converter, download_data, update_or_read_database
from downloader.ecos import get_exchange_rate, get_m2_money_supply, get_stock_market_funds
import humanize

from pages.short_term_view import draw_filtered_data, get_period, show_current_to_mean_ratio
# import altair as alt


if 'long_term_search_form_submitted' not in st.session_state:
    st.session_state.long_term_search_form_submitted = False


def get_dataset_path(dataset):
    return DOWNLOAD_DATA_DIR / f"{dataset}.xlsx"


def show_search_forms():
    with st.form('long_term_search_form'):
        selected_period = st.select_slider(
            "Select Date Range",
            options=DATE_PRESETS.keys(),
            format_func=lambda x: DATE_PRESETS[x]['label'],
            value=settings['STATE']['long_term_view']['selected_period'],
            key="long_term_date_range"
        )
        
        st.session_state.selected_period = selected_period
        st.session_state.long_term_search_form_submitted = st.form_submit_button('조회')

    # with st.form 내부에 있으면 업데이트된 값이 아님
    # https://docs.streamlit.io/develop/concepts/architecture/forms
    settings['STATE']['long_term_view']['selected_period'] = selected_period
    save_settings()
    
    
@st.cache_data
def st_get_m2_money_supply(start_date:str, end_date:str) -> pd.DataFrame:
    return get_m2_money_supply(start_date, end_date)


@st.cache_data
def st_get_stock_market_funds(start_date, end_date):
    return get_stock_market_funds(start_date, end_date)

    
def show_basic_statistics():
    start_date, end_date = get_period(st.session_state.selected_period)

    st.header('M2 Liquidity', divider=True)
    m2_money_supply = st_get_m2_money_supply(start_date, end_date)
    
    if len(m2_money_supply) < 1:
        st.error('No data. Please expand time window')
    else:
        cols = st.columns(len(m2_money_supply.columns), border=True)        
        for item_code, col in zip(m2_money_supply.columns, cols):
            with col:
                df_filter:pd.DataFrame = m2_money_supply[item_code].to_frame()
                show_current_to_mean_ratio(df_filter, item_code, 1.0, 
                                           COLUMN_KEY_DESC[item_code]['short_descs'][0], 
                                           COLUMN_KEY_DESC[item_code]['full_desc'])
        with st.expander('그래프 보기'):    
            df_chart = m2_money_supply.reset_index()
            df_chart.rename(columns=M2_ITEM_CODES, inplace=True)
            draw_filtered_data(df_chart, 'TIME', M2_ITEM_CODES.values(), chart_type='line')
        with st.expander('원본 데이터 보기'):
            st.dataframe(df_chart)

    # 증시자금 추이
    st.header('Stock Market Funds', divider=True)    
    df_stock_market_funds = st_get_stock_market_funds(start_date, end_date)
    if len(df_stock_market_funds) < 1:
        st.error('No data. Please expand time window')
    else:
        cols = st.columns(len(df_stock_market_funds.columns), border=True)        
        for item_code, col in zip(df_stock_market_funds.columns, cols):
            with col:
                df_filter = df_stock_market_funds[item_code].to_frame()
                df_filter.fillna(0, inplace=True)
                show_current_to_mean_ratio(df_filter, item_code, 1.0, 
                                           COLUMN_KEY_DESC[item_code]['short_descs'][0], 
                                           COLUMN_KEY_DESC[item_code]['full_desc'])   
        with st.expander('그래프 보기'):    
            df_chart = df_stock_market_funds.reset_index()
            df_chart.rename(columns=STOCK_MARKET_FUNDS_ITEM_CODES, inplace=True)
            draw_filtered_data(df_chart, 'TIME', STOCK_MARKET_FUNDS_ITEM_CODES.values(), chart_type='line')

        with st.expander('원본 데이터 보기'):
            st.dataframe(df_stock_market_funds)
        
    
def long_term_view_index():
    st.title("Data Overview")
        
    show_search_forms()
    
    show_basic_statistics()
