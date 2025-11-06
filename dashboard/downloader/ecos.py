from typing import List
import requests
import pandas as pd
from config import config


BASE_URL = config['ECOS']['BASE_URL']
API_KEY = config['ECOS']['API_KEY']




def build_url(stat_code:str, item_code, date_metric, start_date: str, end_date: str) -> str:
    # url = f'{BASE_URL}/StatisticSearch/{API_KEY}/json/kr/{start_index}/{end_index}/731Y001/D/{start_date}/{end_date}/0000001'
    start_index = 1
    
    if date_metric == 'D':
        end_index = get_days_from_period(start_date, end_date)
        fixed_start_date = start_date
        fixed_end_date = end_date
    elif date_metric == 'M':
        end_index = get_months_from_period(start_date, end_date)
        fixed_start_date = start_date[:6]
        fixed_end_date = end_date[:6]
    elif date_metric == 'Q':
        fixed_start_date = start_date[:6]
        fixed_end_date = end_date[:6]
    elif date_metric == 'A':
        fixed_start_date = start_date[:4]
        fixed_end_date = end_date[:4]
    else:
        raise ValueError(f"Invalid date_metric: {date_metric}")
    
    url  = f'{BASE_URL}/StatisticSearch/{API_KEY}/json/kr/{start_index}/{end_index}/'
    url += f'{stat_code}/{date_metric}/{fixed_start_date}/{fixed_end_date}/{item_code}'
    return url


def get_days_from_period(start_date: str, end_date: str) -> int:
    start = pd.to_datetime(start_date, format='%Y%m%d')
    end = pd.to_datetime(end_date, format='%Y%m%d')
    delta = end - start
    return delta.days


def get_months_from_period(start_date: str, end_date: str) -> int:
    start = pd.to_datetime(start_date, format='%Y%m%d')
    end = pd.to_datetime(end_date, format='%Y%m%d')
    delta = end - start
    return delta.days // 30


def download_ecos_data(url: str, valid_columns, time_format) -> pd.DataFrame:
    start_index = 1
    total_count = 0
    row_data = []
    while start_index <= total_count or total_count == 0:        
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if data.get('StatisticSearch') is None:
                print(data)
                break
            total_count = int(data['StatisticSearch']['list_total_count'])
            row_data.extend(data['StatisticSearch']['row'])
            start_index += len(data['StatisticSearch']['row'])
        else:
            print(f"ECOS API request failed with status code {r.json()}")
            raise Exception(f"ECOS API request failed with status code {r.status_code}")
    
    if len(row_data) == 0:
        return pd.DataFrame([], columns=valid_columns)
    
    index = pd.to_datetime([ item['TIME'] for item in row_data ], format=time_format)

    df = pd.DataFrame(row_data, index=index)
    df['TIME'] = pd.to_datetime(df['TIME'], format=time_format)
    df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'])
    df.set_index('TIME', inplace=True)
    df.sort_index(inplace=True, ascending=False)
    df_filtered = df[valid_columns]
    
    return df_filtered
    

def reshape_dataframe(df, item_code) -> pd.DataFrame:
    df.rename(columns={'DATA_VALUE': item_code}, inplace=True)
    df = df[item_code].to_frame()
    df.sort_index(inplace=True, ascending=False)
    return df
    
    
def get_m2_money_supply(start_date:str, end_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', 'UNIT_NAME']
     
    df_all = pd.DataFrame()
    for item_code in M2_ITEM_CODES:
        url = build_url(stat_code='101Y006', item_code=item_code, date_metric='M', start_date=start_date, end_date=end_date)
        # print(url)
        # df = pd.concat([df, download_ecos_data(url, valid_columns, time_format='%Y%m')])
        df = reshape_dataframe(download_ecos_data(url, valid_columns, time_format='%Y%m'), item_code)
        if len(df) > 0:
            df_all = pd.concat([df_all, df], axis=1)
    
    df_all.fillna(0, inplace=True)
    
    return df_all


def get_exchange_rate(start_date:str, end_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    
    url = build_url(stat_code='731Y001', item_code='0000001', date_metric='D', start_date=start_date, end_date=end_date)
    
    df = download_ecos_data(url, valid_columns, time_format='%Y%m%d')    
    
    return df
    
    
def get_kospi_stat(start_date:str, end_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    url = build_url(stat_code='802Y001', item_code='0001000', date_metric='D', start_date=start_date, end_date=end_date)
    
    df = download_ecos_data(url, valid_columns, time_format='%Y%m%d')    
    
    return df


# 증시자금 동향
def get_stock_market_funds(start_date:str, end_date:str) -> pd.DataFrame:
    valid_columns = ['DATA_VALUE', 'STAT_CODE', 'STAT_NAME', 'ITEM_CODE1', 'ITEM_NAME1', ]
    item_codes = ['S23'+x for x in ['A', 'B', 'C', 'D', 'E', 'F']]
    df_all = pd.DataFrame()
    for item_code in STOCK_MARKET_FUNDS_ITEM_CODES:
        url = build_url(stat_code='901Y056', item_code=item_code, date_metric='M', start_date=start_date, end_date=end_date)
        df = reshape_dataframe(download_ecos_data(url, valid_columns, time_format='%Y%m'), item_code)
        if len(df) > 0:
            df_all = pd.concat([df_all, df], axis=1)
    df_all.fillna(0, inplace=True)
    return df_all
    

if __name__ == '__main__':
    df = get_stock_market_funds('19830101', '20251101')
    print(df.columns)
    print(df.head(10))
    print(df.tail(10))