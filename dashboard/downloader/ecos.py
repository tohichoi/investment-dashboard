import copy
from typing import List
import dateutil
import requests
import pandas as pd
from config import config, M2_ITEM_CODES, STOCK_MARKET_FUNDS_ITEM_CODES


BASE_URL = config['ECOS']['BASE_URL']
API_KEY = config['ECOS']['API_KEY']


ECOS_RESPONSE_COLUMNS = {
    'STAT_CODE': '통계표코드',
    'STAT_NAME': '통계명',
    'GRP_CODE': '항목그룹코드',
    'GRP_NAME': '항목그룹명',
    'ITEM_CODE': '통계항목코드',
    'ITEM_NAME': '통계항목명',
    'P_ITEM_CODE': '상위통계항목코드',
    'P_ITEM_NAME': '상위통계항목명',
    'CYCLE': '주기',
    'START_TIME': '수록시작일자',
    'END_TIME': '수록종료일자',
    'DATA_CNT': '자료수',
    'UNIT_NAME': '단위',
    'WEIGHT': '가중치',
}


ECOS_RESPONSE_ERROR = {
    100: '인증키가 유효하지 않습니다. 인증키를 확인하십시오! 인증키가 없는 경우 인증키를 신청하십시오!',
    200: '해당하는 데이터가 없습니다.',
    100: '필수 값이 누락되어 있습니다. 필수 값을 확인하십시오! 필수 값이 누락되어 있으면 오류를 발생합니다. 요청 변수를 참고 하십시오!',
    101: '주기와 다른 형식의 날짜 형식입니다.',
    200: '파일타입 값이 누락 혹은 유효하지 않습니다. 파일타입 값을 확인하십시오! 파일타입 값이 누락 혹은 유효하지 않으면 오류를 발생합니다. 요청 변수를 참고 하십시오!',
    300: '조회건수 값이 누락되어 있습니다. 조회시작건수/조회종료건수 값을 확인하십시오! 조회시작건수/조회종료건수 값이 누락되어 있으면 오류를 발생합니다.',
    301: '조회건수 값의 타입이 유효하지 않습니다. 조회건수 값을 확인하십시오! 조회건수 값의 타입이 유효하지 않으면 오류를 발생합니다. 정수를 입력하세요.',
    400: '검색범위가 적정범위를 초과하여 60초 TIMEOUT이 발생하였습니다. 요청조건 조정하여 다시 요청하시기 바랍니다.',
    500: '서버 오류입니다. OpenAPI 호출시 서버에서 오류가 발생하였습니다.  해당 서비스를 찾을 수 없습니다.',
    600: 'DB Connection 오류입니다. OpenAPI 호출시 서버에서 DB접속 오류가 발생했습니다.',
    601: 'SQL 오류입니다. OpenAPI 호출시 서버에서 SQL 오류가 발생했습니다.',
    602: '과도한 OpenAPI호출로 이용이 제한되었습니다. 잠시후 이용해주시기 바랍니다.',    
}


ECOS_ITEM_VALUE_COLUMNS = [
    "STAT_CODE",
    "STAT_NAME",
    "ITEM_CODE1",
    "ITEM_NAME1",
    "ITEM_CODE2",
    "ITEM_NAME2",
    "ITEM_CODE3",
    "ITEM_NAME3",
    "ITEM_CODE4",
    "ITEM_NAME4",        
    "UNIT_NAME"	,
    "WGT"       ,
    "TIME"	    ,
    "DATA_VALUE"
]


def build_stat_url(start_index, end_index):
    # https://ecos.bok.or.kr/api/#/DevGuide/DevSpeciflcation
    url  = f'{BASE_URL}/StatisticTableList/{API_KEY}/json/kr/{start_index}/{end_index}/102Y004/'
    return url


def build_url(stat_code:str, item_code, date_metric:str, from_date: str, to_date: str) -> str:
    # service_name='StatisticTableList', 
    # url = f'{BASE_URL}/StatisticTableList/{API_KEY}/json/kr/{start_index}/{end_index}/102Y004'
    
    # service_name='StatisticSearch', 
    # url = f'{BASE_URL}/StatisticSearch/{API_KEY}/json/kr/{start_index}/{end_index}/731Y001/D/{from_date}/{to_date}/0000001'
    start_index = 1
    
    if date_metric == 'D':
        end_index = get_days_from_period(from_date, to_date)
        fixed_from_date = from_date
        fixed_to_date = to_date
    elif date_metric == 'M':
        end_index = get_months_from_period(from_date, to_date)
        fixed_from_date = from_date[:6]
        fixed_to_date = to_date[:6]
    elif date_metric == 'Q':
        end_index = get_quarters_from_period(from_date, to_date)
        fixed_from_date = from_date[:6]
        fixed_to_date = to_date[:6]
    elif date_metric == 'A':
        end_index = get_years_from_period(from_date, to_date)        
        fixed_from_date = from_date[:4]
        fixed_to_date = to_date[:4]
    else:
        raise ValueError(f"Invalid date_metric: {date_metric}")
    
    # StatisticSearch
    url  = f'{BASE_URL}/StatisticSearch/{API_KEY}/json/kr/{start_index}/{end_index}/{stat_code}'
    url += f'/{date_metric}/{fixed_from_date}/{fixed_to_date}/{item_code}'
    return url


def get_date_delta(from_date: str, to_date: str) -> int:
    start = dateutil.parser.parse(from_date)
    end = dateutil.parser.parse(to_date)
    delta = end - start
    return delta.days

def get_days_from_period(from_date: str, to_date: str) -> int:
    return get_date_delta(from_date, to_date) 


def get_months_from_period(from_date: str, to_date: str) -> int:
    return get_date_delta(from_date, to_date) // 30


def get_quarters_from_period(from_date: str, to_date: str) -> int:
    return get_date_delta(from_date, to_date) // 90


def get_years_from_period(from_date: str, to_date: str) -> int:
    return get_date_delta(from_date, to_date) // 365


def download_ecos_data(service_name: str, url: str, valid_columns:list|None, time_format:str) -> pd.DataFrame:
    # service_name : StatisticSearch
    start_index = 1
    total_count = 0
    row_data = []
    while start_index <= total_count or total_count == 0:        
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if data.get(service_name) is None:
                print(data)
                break
            total_count = int(data[service_name]['list_total_count'])
            row_data.extend(data[service_name]['row'])
            start_index += len(data[service_name]['row'])
        else:
            print(f"ECOS API request failed with status code {r.json()}")
            raise Exception(f"ECOS API request failed with status code {r.status_code}")
    
    if len(row_data) == 0:
        return pd.DataFrame([], columns=ECOS_ITEM_VALUE_COLUMNS)
    
    if service_name == 'StatisticSearch':
        index = pd.to_datetime([ item['TIME'] for item in row_data ], format=time_format)
        df = pd.DataFrame(row_data, index=index)
        df['TIME'] = pd.to_datetime(df['TIME'], format=time_format)
        df.set_index('TIME', inplace=True)
        df.sort_index(inplace=True, ascending=False)
        df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'])
    else:
        # 'StatisticTableList'
        df = pd.DataFrame(row_data)
        
    # TIME 은 인덱스로 설정되었기 때문에 스킵
    default_columns = copy.copy(ECOS_ITEM_VALUE_COLUMNS)
    default_columns.remove('TIME')
    df_filtered = df[valid_columns if valid_columns else default_columns]
    
    return df_filtered
    

def reshape_dataframe(df, item_code) -> pd.DataFrame:
    df.rename(columns={'DATA_VALUE': item_code}, inplace=True)
    df = df[item_code].to_frame()
    df.sort_index(inplace=True, ascending=False)
    return df
    
    
def get_m2_money_supply(from_date:str, to_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', 'UNIT_NAME']
     
    df_all = pd.DataFrame()
    for item_code in M2_ITEM_CODES:
        url = build_url(stat_code='101Y006', item_code=item_code, date_metric='M', from_date=from_date, to_date=to_date)
        # print(url)
        # df = pd.concat([df, download_ecos_data(url, valid_columns, time_format='%Y%m')])
        df = reshape_dataframe(download_ecos_data('StatisticSearch', url, valid_columns, time_format='%Y%m'), item_code)
        if len(df) > 0:
            df_all = pd.concat([df_all, df], axis=1)
    
    df_all.fillna(0, inplace=True)
    
    return df_all


def get_exchange_rate(from_date:str, to_date:str) -> pd.DataFrame:
    
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    
    url = build_url(stat_code='731Y001', item_code='0000001', date_metric='D', from_date=from_date, to_date=to_date)
    
    df = download_ecos_data('StatisticSearch', url, valid_columns, time_format='%Y%m%d')    
    
    return df
    
    
def get_kospi_stat(from_date:str, to_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    url = build_url(stat_code='802Y001', item_code='0001000', date_metric='D', from_date=from_date, to_date=to_date)
    
    df = download_ecos_data('StatisticSearch', url, valid_columns, time_format='%Y%m%d')    
    
    return df


# 증시자금 동향
def get_stock_market_funds(from_date:str, to_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    item_codes = ['S23'+x for x in ['A', 'B', 'C', 'D', 'E', 'F']]
    df_all = pd.DataFrame()
    for item_code in STOCK_MARKET_FUNDS_ITEM_CODES:
        url = build_url(stat_code='901Y056', item_code=item_code, date_metric='M', from_date=from_date, to_date=to_date)
        df = reshape_dataframe(download_ecos_data('StatisticSearch', url, valid_columns, time_format='%Y%m'), item_code)
        if len(df) > 0:
            df_all = pd.concat([df_all, df], axis=1)
    df_all.fillna(0, inplace=True)
    return df_all
    

if __name__ == '__main__':
    df = get_stock_market_funds('19830101', '20251101')
    print(df.columns)
    print(df.head(10))
    print(df.tail(10))