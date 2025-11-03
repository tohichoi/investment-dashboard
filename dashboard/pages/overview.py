from typing import Tuple
import streamlit as st
import pandas as pd
import streamlit.components.v1 as st_components
from config import COLUMN_KEY_DESC, DATE_PRESETS, DOWNLOAD_DATA_DIR
from downloader.ecos import M2_ITEM_CODES, get_exchange_rate, get_m2_money_supply
import humanize
# import altair as alt


def get_dataset_path(dataset):
    return DOWNLOAD_DATA_DIR / f"{dataset}.xlsx"


def get_dataset_description(dataset):
    descriptions = {
        'domestic_stock_075_investor_daily_by_market': 'Daily investor statistics for domestic stocks by market segment.',
        # Add more dataset descriptions as needed
    }
    return descriptions.get(dataset, "No description available.")


# 'YYYYMMDD' 문자열을 datetime 객체로 변환하는 함수 정의
def date_converter(date_int):
    # 정수 형태의 YYYYMMDD를 문자열로 변환 후, pd.to_datetime으로 변환
    return pd.to_datetime(str(date_int), format='%Y%m%d')


def get_period(period_key) -> Tuple[str, str]:
    end_date = pd.Timestamp.now()
    days = DATE_PRESETS.get(period_key, DATE_PRESETS['14d'])
    if days['days'] is None:
        return end_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    else:
        start_date = end_date - pd.Timedelta(days=days['days'])
        return start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')


@st.cache_data
def load_data(dataset):
    p = get_dataset_path(dataset)
    df = pd.read_excel(p, converters={'stck_bsop_date': date_converter})
    df.set_index('stck_bsop_date', inplace=True)
    return df


def show_filtered_data(df, x_column, y_columns):
    if x_column is None:
        # df['date_only'] = df.index.strftime('%Y-%m-%d')
        new_df = df.copy()
        new_df.loc[:, 'date_only'] = new_df.index.strftime('%Y-%m-%d')
        new_x_column = 'date_only'
    else:
        new_x_column = x_column
        new_df = df
    st.bar_chart(new_df, x=new_x_column, y=y_columns, stack=False)
    # st.line_chart(df, x=x_column, y=y_columns)


def show_chart(df):
    # df_filter = _filter_data_by_date(df, 'stck_bsop_date', st.session_state.selected_period)
    
    # st.bar_chart(df_filter[['stck_bsop_date', 'bstp_nmix_prpr']], x='stck_bsop_date', y='bstp_nmix_prpr')
    pass

def _filter_data_by_date(df, date_column, period_key):
    days = DATE_PRESETS[period_key]['days']
    if days is None:
        return df
    else:
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        return df[df.index >= cutoff_date]
        # return df[df[date_column] >= cutoff_date]
    

def show_current_to_mean_ratio(df, column, scale_factor, help_text):
    if column not in df.columns:
            st.warning(f"Column '{column}' not found in DataFrame.")
            return
    if df.empty:
        st.warning("DataFrame is empty.")
        return
    
    current_value = round(df[column].iloc[0] * scale_factor, 2)
    if len(df) > 1:
        total_value_except_current = round(df[column].iloc[1:].mean() * scale_factor, 2)
    else:
        total_value_except_current = current_value
    st.metric(label=f"{COLUMN_KEY_DESC[column]['short_descs'][0]}", value=current_value, 
            delta=round(current_value-total_value_except_current), help=help_text)
    st.info(f"기간 평균 값: {total_value_except_current:.2f}")


def show_ntby_qty_metrics(df, column, scale_factor, help_text):
    """순매도/순매수 주식 수량

    Args:
        df (_type_): pd.DataFrame
        column (_type_): DataFrame 컬럼명
        help_text (_type_): st.metric 도움말 텍스트
    """
    show_current_to_mean_ratio(df, column, scale_factor, help_text)    


# frgn_ntby_tr_pbmn
def show_ntby_tr_metrics(df, column, help_text):
    """순매도/순매수 금액

    Args:
        df (_type_): pd.DataFrame
        column (_type_): DataFrame 컬럼명
        help_text (_type_): st.metric 도움말 텍스트
    """
    # current_value = df[column].iloc[0]
    # total_value_except_current = df[column].iloc[1:].mean().round(2)
    # st.metric(label=f"{COLUMN_KEY_DESC[column]['short_descs'][0]}", value=current_value, 
    #           delta=current_value-total_value_except_current, help=help_text)
    # st.info(f"기간 평균 값: {total_value_except_current:.2f}")
    show_current_to_mean_ratio(df, column, 0.01, help_text)


def analyze_data(df, dataset):
    # st.write(f"Analyzing dataset: {dataset}")
    # 외국인, 기관, 개인
    groups = ['frgn', 'orgn', 'prsn']
    group_names = ['🌐 외국인', '🏦 기관', '🙋 개인']
    delta_text = f"델타 값은 선택한 기간({DATE_PRESETS[st.session_state.selected_period]['label']}) 동안의 평균과 비교한 변화량을 나타냅니다."

    if dataset == 'domestic_stock_075_investor_daily_by_market':
        # st.write(f"Performing analysis specific to {dataset}")
        
        df_filter = _filter_data_by_date(df, 'stck_bsop_date', st.session_state.selected_period)
        if df_filter.empty:
            st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
            return
                
        target_date = df_filter.index[0]
        
        st.markdown(f"#### Data Analysis of date: {target_date.date()}")
        
        st.markdown('##### 순매도/순매수 주식 수량 분석 결과:')
        # cols = st.columns([0.3, 0.7], border=True)        
        # with cols[0]:
        #     group = 'frgn'
        #     group_name = '🌐 외국인'
        #     show_current_to_mean_ratio(df_filter, f'{group}_ntby_qty', 1.0,
        #                             f"{target_date.date()}기준 {group_name} 투자자의 순매수 주식 수량입니다. {delta_text}")
            
        # with cols[1]:
        #     group = 'frgn'
        #     group_name = '🌐 외국인'
        #     show_filtered_data(df_filter[[f'{group}_ntby_qty']], x_column=None, y_columns=[f'{group}_ntby_qty'])
            
        cols = st.columns(3, border=True)        
        for col, group, group_name in zip(cols, groups, group_names):
            # 순매도/순매수 주식 수량
            with col:
                show_current_to_mean_ratio(df_filter, f'{group}_ntby_qty', 1.0,
                                    f"{target_date.date()}기준 {group_name} 투자자의 순매수 주식 수량입니다. {delta_text}")

        show_filtered_data(df_filter[[f'{group}_ntby_qty' for group in groups]], 
                           x_column=None, y_columns=[f'{group}_ntby_qty' for group in groups])

        st.markdown('##### 순매도/순매수 금액(억 원) 분석 결과:')
        cols = st.columns(3, border=True)        
        for col, group, group_name in zip(cols, groups, group_names):
            # 순매도/순매수 주식 수량
            with col:
                show_current_to_mean_ratio(df_filter, f'{group}_ntby_tr_pbmn', 0.01,
                                    f"{target_date.date()}기준 {group_name} 투자자의 순매수 금액입니다. {delta_text}")
        show_filtered_data(df_filter[[f'{group}_ntby_tr_pbmn' for group in groups]], 
                           x_column=None, y_columns=[f'{group}_ntby_tr_pbmn' for group in groups])

        st.dataframe(df_filter)
        

def customize_page():
    js = r'''
    <script>
        function change_metric_colors() {
            let metrics = document.querySelectorAll('div[data-testid=stMetricValue] > div');
            metrics.forEach((metric) => {
                let value = metric.innerText;
                if (value[0] === '-') {
                    metric.style.color = 'red';
                } else {
                    metric.style.color = 'blue';
                }
            });
        }
        document.addEventListener("DOMContentLoaded", change_metric_colors);
    </script>
    '''
    st_components.html(js, width=0, height=0)

    
def load_stock_market_dataset():
    for dataset in st.session_state.selected_datasets:
        st.header(dataset, divider=True)
        st.markdown(get_dataset_description(dataset))
        
        df = load_data(dataset)

        st.subheader("Data Analysis")
        analyze_data(df, dataset)
        
        st.subheader("Data Preview")
        show_chart(df)
        
        st.subheader("Raw Data")
        st.dataframe(df)
        

def show_stock_market_forms():
    datasets = st.pills(
        "Select Dataset",
        options=[
            'domestic_stock_075_investor_daily_by_market',
            'test'
        ],
        selection_mode="multi",
        default=['domestic_stock_075_investor_daily_by_market'],
        format_func=lambda x: get_dataset_description(x)
    )

    selected_period = st.select_slider(
        "Select Date Range",
        options=DATE_PRESETS.keys(),
        format_func=lambda x: DATE_PRESETS[x]['label'],
        value="14d",
        key="date_range"
    )
    
    if datasets:
        st.session_state.selected_datasets = datasets
    else:
        st.session_state.selected_datasets = []
    
    st.session_state.selected_period = selected_period
    
    
def st_get_exchange_rate(start_date:str, end_date:str) -> Tuple[str, pd.DataFrame]:
    now = pd.Timestamp.now('Asia/Seoul')
    return now.isoformat(), get_exchange_rate(start_date, end_date)
    
    
@st.cache_data
def st_get_m2_money_supply(start_date:str, end_date:str) -> pd.DataFrame:
    return get_m2_money_supply(start_date, end_date)

    
def show_basic_statistics():
    # 환율
    st.header('Exchange rate', divider=True)
    cols = st.columns(1, border=True)        
    for col in cols:
        with col:
            st.session_state.selected_period
            
            start_date, end_date = get_period(st.session_state.selected_period)
            updated_timestamp, df = st_get_exchange_rate(start_date, end_date)
            st.badge(f"데이터 업데이트 시각: {humanize.naturalday(updated_timestamp)}")
            show_current_to_mean_ratio(df, 'DATA_VALUE', 1.0, "미국 달러 대비 원화 환율입니다.")        
            # st.metric(label="USD/KRW", value=df['DATA_VALUE'].iloc[0], delta="+5.30", help="미국 달러 대비 원화 환율입니다.")
            st.dataframe(df)
    
    st.header('M2 Liquidity', divider=True)
    df = st_get_m2_money_supply(start_date, end_date)
    
    cols = st.columns(5, border=True)        
    for item_code, col in zip(M2_ITEM_CODES, cols):
        with col:
            df_filter = df[df['ITEM_CODE1']==item_code].copy()
            df_filter.rename(columns={'DATA_VALUE': item_code}, inplace=True)
            start_date, end_date = get_period(st.session_state.selected_period)
            show_current_to_mean_ratio(df_filter, item_code, 1.0, item_code)        
            # st.metric(label="USD/KRW", value=df['DATA_VALUE'].iloc[0], delta="+5.30", help="미국 달러 대비 원화 환율입니다.")
            st.dataframe(df_filter)
            
def index():
    st.title("Data Overview")
        
    show_stock_market_forms()
    
    show_basic_statistics()
    
    load_stock_market_dataset()
    
    customize_page()
    

index()