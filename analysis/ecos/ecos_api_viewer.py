from collections import OrderedDict
from datetime import datetime
import json
import sys
import os
from pathlib import Path
from typing import Tuple
import requests
import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


st.set_page_config(layout="wide")


# cwd = BASE_DIR / analysis
cwd = Path(os.getcwd())
sys.path.append(str(cwd.parents[1]))
# downloader
sys.path.append(str(cwd.parents[1] / 'dashboard'))
sys.path.append(str(cwd.parents[1] / 'dashboard' / 'downloader'))


from dashboard.config import config, DATA_DIR, KIS_DATABASE_PATH, DATE_PRESETS
from dashboard.downloader.ecos import build_url, download_ecos_data
from dashboard.pages.short_term_view import draw_filtered_data, get_period
from dashboard.pages.long_term_view import show_search_forms


BASE_URL = config['ECOS']['BASE_URL']
API_KEY = config['ECOS']['API_KEY']


ST_DATAFRAME_HEIGHT='stretch'


# @st.cache_resource를 사용하여 모델 및 임베딩을 캐시합니다.
@st.cache_resource(show_spinner=True)
def load_and_embed_data(data_list):
    # 모델 로드 (한 번만 실행)
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    
    # 데이터 임베딩 (한 번만 실행)
    embeddings = model.encode(data_list)
    return model, embeddings


@st.cache_data(show_spinner=True)
def load_stat_code() -> pd.DataFrame:
    database_path = Path('ecos.db')
    
    with sqlite3.connect(database_path) as conn:
        sql = '''
        SELECT
        T1.id as code_id,
        STAT_CODE,
        STAT_NAME,
        -- 첫 번째 공백의 위치를 찾고 그 다음 문자부터 끝까지 자릅니다.
        SUBSTR(
            T1.STAT_NAME, 
            INSTR(T1.STAT_NAME, ' ') + 1
        ) AS CLEAN_STAT_NAME,
        CYCLE,
        SRCH_YN,
        ORG_NAME
        FROM
        StatisticTableList T1
        '''
        df = pd.read_sql(sql, conn)
        df['id'] = df['code_id']
        df.set_index('id', inplace=True)
        return df
    
    
def get_stat_items(df_selected_item):
    database_path = Path('ecos.db')

    with sqlite3.connect(database_path) as conn:
        sql = f'''
        SELECT *
        FROM
        StatisticItemList
        WHERE code_id in ({', '.join(['?']*len(df_selected_item))})
        '''
        df = pd.read_sql(sql, conn, params=df_selected_item['code_id'].tolist())
        df.set_index('id', inplace=True)
        return df
    
    
def get_stat_values(df_selected_item):
    database_path = Path('ecos.db')
    
    with sqlite3.connect(database_path) as conn:
        sql = f'''
        SELECT *
        FROM
        StatisticItemValueList
        WHERE item_id in ({', '.join(['?']*len(df_selected_item))})
        '''
        df = pd.read_sql(sql, conn, params=df_selected_item['id'].tolist())
        df.set_index('id', inplace=True)
        return df
    
    
def get_query_url(stat_code:str, df_stat_item:pd.DataFrame, from_date: str, to_date: str) -> pd.DataFrame:
    url_infos = []
    for index, row in df_stat_item.iterrows():
        url_info = {
            'pstat_name': row['P_ITEM_NAME'],
            'item_name': row['ITEM_NAME'],
            'stat_code': stat_code,
            'item_code': None,
            'cycle': None,
            'url': None
        }
        # def build_url(stat_code:str, item_code, date_metric:str, from_date: str, to_date: str) -> str:
        url_info['item_code'] = row['ITEM_CODE']
        url_info['cycle'] = row['CYCLE']
        url_info['url'] = build_url(stat_code, row['ITEM_CODE'], row['CYCLE'], from_date, to_date)
        url_infos.append(url_info)
        
    return pd.DataFrame(url_infos)

    
@st.cache_data(show_spinner=True)
def get_ecos_data(df_urls:pd.DataFrame) -> pd.DataFrame:
    # def download_ecos_data(service_name: str, url: str, valid_columns, time_format) -> pd.DataFrame:
    # valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', 'UNIT_NAME']
    time_format = {
        'D': '%Y%m%d',
        'M': '%Y%m',
        'A': '%Y'
    }
    df_all = pd.DataFrame()
    for index, row in df_urls.iterrows():
        df = download_ecos_data('StatisticSearch', row['url'], None, time_format[row['cycle']])
        df_all = pd.concat([df_all, df])
    
    return df_all
    
    
def min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Pandas Series를 0과 1 사이로 정규화합니다.
    최대값과 최소값이 같을 경우 0으로 반환하여 0 나누기 오류를 방지합니다.
    """
    min_val = series.min()
    max_val = series.max()
    
    if max_val == min_val:
        return 0.0 * series # 모든 값이 같으면 0으로 채워진 Series 반환
    else:
        return (series - min_val) / (max_val - min_val)
    
    
def normalize_column_group_values(df, group_column, value_column) -> Tuple[pd.DataFrame, str]:
    new_column = f'NORMALIZED_{value_column}' 
    df[new_column] = df.groupby(group_column)[value_column].transform(min_max_normalize)
    return df, new_column


def normalize_column_values(df) -> pd.DataFrame:
    # 1. 정규화 대상 컬럼 선택 (수치형 컬럼만)
    # 'select_dtypes(include=np.number)'를 사용하면 수치형 컬럼만 자동 선택됩니다.
    numeric_cols = df.select_dtypes(include=np.number).columns

    # 2. Min-Max 정규화 적용
    for col in numeric_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        
        # 0으로 나누는 오류 방지 (최소값과 최대값이 같은 경우)
        if max_val != min_val:
            df[col] = (df[col] - min_val) / (max_val - min_val)
        else:
            # 모든 값이 같으면 0 또는 1로 설정 (여기서는 0으로 설정)
            df[col] = 0.0
    
    return df


def _format_df_selected_urls(index):
    df = st.session_state.get('df_selected_urls', pd.DataFrame([]))

    # disp = '{}:{}'.format(df[['CLEAN_STAT_NAME', 'CLEAN_ITEM_NAME']].iloc[index])
    disp = '{}'.format(df.loc[index]['item_name'])
    return disp
    
    
def show_selected_urls(df_selected_urls):
    if len(df_selected_urls) > 0:
        return st.pills(label='Selected items', options=df_selected_urls.index,
                        selection_mode='multi',
                        default=df_selected_urls.index,
                        format_func=_format_df_selected_urls)
    

def update_period_in_url(df):
    # https://ecos.bok.or.kr/api/StatisticSearch/T53AWNWQU4O1QH9CY81R/json/kr/1/1825/731Y001/D/20201111/20251110/0000001
    # def build_url(stat_code:str, item_code, date_metric:str, from_date: str, to_date: str) -> str:
    # df['url']=df['url'].apply()
    from_date, to_date = get_period(st.session_state.selected_period)
    
    def _update_url(row):
        return build_url(row['stat_code'], row['item_code'], row['cycle'], from_date, to_date)
        
    df['url'] = df.apply(_update_url, axis=1)
    
    return df
    
    
df_stat_code_info = load_stat_code()
df_stat_code_info.sort_values('STAT_NAME')
df_stat_code_filter = df_stat_code_info.copy()

data_list = list(df_stat_code_info['CLEAN_STAT_NAME'].tolist())
df_selected_stat_items = []
llm_model, embedded_data = load_and_embed_data(data_list)

# initialize states
st.session_state.show_charts = False
if 'df_selected_urls' not in st.session_state:
    st.session_state['df_selected_urls'] = pd.DataFrame()
    
with st.sidebar:
    st.header('통계코드')
    user_query = st.text_input('검색어')
    with st.container():
        only_show_having_stat_item = st.checkbox('Only show data having stat items')
        remove_duplicate = st.checkbox('Remove duplicated items')
    st.header('Selected StatItems')
    # st.dataframe(st.session_state.get('df_selected_urls', []))

    selected_urls_indices = show_selected_urls(st.session_state.get('df_selected_urls', []))

    clear_selected_urls = st.button(':material/clear: Clear')
    if clear_selected_urls:
        st.session_state['df_selected_urls'] = pd.DataFrame()
        st.rerun()
        
    with st.form('query_form'):
        selected_period = st.select_slider(
            "Select Date Range",
            options=DATE_PRESETS.keys(),
            format_func=lambda x: DATE_PRESETS[x]['label'],
            value='1y',
            key="long_term_date_range"
        )
        normalize_values = st.checkbox('Normalize values')    
        st.session_state.selected_period = selected_period
        st.session_state.long_term_search_form_submitted = st.form_submit_button(':material/search: 조회')

    
if user_query:
    query_embedding = llm_model.encode([user_query])
    similarities = cosine_similarity(query_embedding, embedded_data)
    df_stat_code_filter['similarity']=similarities[0]
    df_stat_code_filter.sort_values('similarity', ascending=False, inplace=True)

if only_show_having_stat_item:
    df_stat_code_filter = df_stat_code_filter[df_stat_code_filter['SRCH_YN']=='Y']

if remove_duplicate:
    df_stat_code_filter = df_stat_code_filter.drop_duplicates(subset=['CLEAN_STAT_NAME'])

with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
    st.subheader('통계코드')
    st.write(f'Matched  results: {len(df_stat_code_filter)}')
    
stat_code_event = st.dataframe(df_stat_code_filter, key='df_stat_code_filter', 
                               selection_mode='single-row', on_select='rerun',
                               height=ST_DATAFRAME_HEIGHT)
selected_codes = stat_code_event.selection['rows']
if len(selected_codes) > 0:
    
    st.subheader('통계아이템')
    df_stat_item_filter = pd.DataFrame([])
    df_stat_item = get_stat_items(df_stat_code_filter.iloc[selected_codes])
    stat_item_event = st.dataframe(df_stat_item, key='df_stat_item_filter',
                                   selection_mode='multi-row', on_select='rerun',
                                   height=ST_DATAFRAME_HEIGHT)
    
    selected_items = stat_item_event.selection['rows']
    if len(selected_items) > 0:
        # with st.container(horizontal=True):
        #     from_date = st.date_input('대상기간 시작일', datetime.now(), format='YYYY-MM-DD')
        #     to_date = st.date_input('대상기간 종료일', datetime.now(), format='YYYY-MM-DD')
        
        if st.session_state.selected_period:
            from_date, to_date = get_period(st.session_state.selected_period)
        
        df_stat_item_filter = df_stat_item.copy()
        stat_code = df_stat_code_filter['STAT_CODE'].iloc[selected_codes[0]]
        df_urls = get_query_url(stat_code, df_stat_item_filter.iloc[selected_items], 
                                from_date, to_date)
        url_event = st.dataframe(df_urls, selection_mode='multi-row', on_select='rerun')
        if len(url_event.selection['rows']) > 0:
            add_items = st.button('Add selected item to the list')
            if add_items:
                if not st.session_state.df_selected_urls.empty:
                    st.session_state.df_selected_urls = pd.concat([st.session_state.df_selected_urls,
                                                            df_urls.iloc[url_event.selection['rows']]],
                                                                  ignore_index=True)
                    st.session_state.df_selected_urls.reindex()
                else:
                    st.session_state.df_selected_urls = df_urls.iloc[url_event.selection['rows']]
                st.rerun()
                
if st.session_state.long_term_search_form_submitted:
    df_org = st.session_state.df_selected_urls.loc[selected_urls_indices]
    df_url_updated = update_period_in_url(df_org)
    df_ecos = get_ecos_data(df_url_updated)
    
    with st.expander('View Chart', expanded=True):        
        df_chart = df_ecos.sort_index(ascending=True)
        new_column = 'DATA_VALUE'
        if normalize_values:
            df_chart, new_column = normalize_column_group_values(df_chart, 'ITEM_NAME1', 'DATA_VALUE')
            
        fig = px.line(
            df_chart.reset_index(),
            x='TIME',
            y=new_column,
            color='ITEM_NAME1',
            labels={
                "TIME": "시간",
                new_column: "데이터 값",
                "ITEM_NAME1": "ITEM Name"
            }
        )
        fig.update_layout(
            hovermode="x unified",  # 마우스를 움직일 때 두 선의 정보를 한 번에 표시
            legend_title_text='ITEM Code',
            xaxis_title="기간",
            yaxis_title=f"데이터 값 ({df_chart['UNIT_NAME'].iloc[0]})"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with st.expander('View DataFrame'):
        st.dataframe(df_ecos)
        
