from pathlib import Path
import sqlite3
import sys
import logging
import pendulum
import pandas as pd
import os
from sqlalchemy.types import FLOAT, INTEGER, TEXT, NUMERIC, String
import numpy as np


# Add parent directory to system path to find kis_auth module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_dir = os.path.join(parent_dir, 'data/downloaded')

kis_database_file_name = os.path.join(data_dir, 'databasees/kis.db')

sys.path.insert(0, parent_dir)


DEFAULT_LASTEST_DATE = '19830104'


KIS_DATAFRAME_DTYPES = {
    'domestic_stock_075_investor_daily_by_market': {
        # 'stck_bsop_date' : datetime 으로 이미 변환되었기 때문에 생략
        # 'stck_bsop_date': str,
        'bstp_nmix_prpr': np.float64,
        'bstp_nmix_prdy_vrss': np.float64,
        'prdy_vrss_sign': np.float64,
        'bstp_nmix_prdy_ctrt': np.float64,
        'bstp_nmix_oprc': np.float64,
        'bstp_nmix_hgpr': np.float64,
        'bstp_nmix_lwpr': np.float64,
        'stck_prdy_clpr': np.float64,
        'frgn_ntby_qty': np.float64,
        'frgn_reg_ntby_qty': np.float64,
        'frgn_nreg_ntby_qty': np.float64,
        'prsn_ntby_qty': np.float64,
        'orgn_ntby_qty': np.float64,
        'scrt_ntby_qty': np.float64,
        'ivtr_ntby_qty': np.float64,
        'pe_fund_ntby_vol': np.float64,
        'bank_ntby_qty': np.float64,
        'insu_ntby_qty': np.float64,
        'mrbn_ntby_qty': np.float64,
        'fund_ntby_qty': np.float64,
        'etc_ntby_qty': np.float64,
        'etc_orgt_ntby_vol': np.float64,
        'etc_corp_ntby_vol': np.float64,
        'frgn_ntby_tr_pbmn': np.float64,
        'frgn_reg_ntby_pbmn': np.float64,
        'frgn_nreg_ntby_pbmn': np.float64,
        'prsn_ntby_tr_pbmn': np.float64,
        'orgn_ntby_tr_pbmn': np.float64,
        'scrt_ntby_tr_pbmn': np.float64,
        'ivtr_ntby_tr_pbmn': np.float64,
        'pe_fund_ntby_tr_pbmn': np.float64,
        'bank_ntby_tr_pbmn': np.float64,
        'insu_ntby_tr_pbmn': np.float64,
        'mrbn_ntby_tr_pbmn': np.float64,
        'fund_ntby_tr_pbmn': np.float64,
        'etc_ntby_tr_pbmn': np.float64,
        'etc_orgt_ntby_tr_pbmn': np.float64,
        'etc_corp_ntby_tr_pbmn': np.float64,
    }
}


import downloader.kis_auth as ka
from downloader.kis_samples.domestic_stock.domestic_stock_functions import *

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

##############################################################################################
# [국내주식] 시세분석 > 시장별 투자자매매동향(일별) [국내주식-075]
##############################################################################################

start_date = pendulum.now()
# end_date = pendulum.now().format('YYYYMMDD')

# fid_input_date_1=sd,
# fid_input_date_2=sd,


def create_database(table_name, df):
    conn = sqlite3.connect(kis_database_file_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    
    
def get_latest_date_of_database_table(table_name, column_name):
    conn = sqlite3.connect(kis_database_file_name)
    cursor = conn.cursor()
    
    # 날짜 포함
    latest_date = DEFAULT_LASTEST_DATE
    
    # find last data
    latest_date_query = f"SELECT MAX({column_name}) FROM {table_name}"
    try:
        latest_date = cursor.execute(latest_date_query).fetchone()[0]
    except sqlite3.OperationalError as e:
        if f'no such table: {table_name}' in str(e):
            logger.info(f"Table {table_name} does not exist. Starting from default date.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}. Maybe the database is absent or locked.")
    except Exception as e:
        logger.error(f"Error occurred while fetching last date: {e}")
        raise e
    finally:
        conn.close()
        return latest_date
    

def set_dtype_of_dataframe(table_name, df):
    if table_name in KIS_DATAFRAME_DTYPES:
        dtype_mapping = KIS_DATAFRAME_DTYPES[table_name]
        for column, dtype in dtype_mapping.items():
            if column in df.columns:
                df[column] = df[column].astype(dtype)
    return df


def update_or_read_database(table_name, df, column_name):
    os.makedirs(os.path.dirname(kis_database_file_name), exist_ok=True)
    
    conn = sqlite3.connect(kis_database_file_name)
    # df_filter = df[df['stck_bsop_date'] > last_date_str]
    if df is not None and not df.empty:
        df.to_sql(table_name, conn, if_exists='append', index=False)
    
    df_all = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY {column_name} DESC", conn)
    df_all[column_name] = pd.to_datetime(df_all[column_name], format='%Y%m%d')
    df_all = set_dtype_of_dataframe(table_name, df_all)
    # df_all[column_name].apply(date_converter)
    df_all.set_index(column_name, drop=False, inplace=True)
    conn.close()

    return df_all 
    
    
def download_data(table_name, column_name):
    oldest_date_str = get_latest_date_of_database_table(table_name, column_name)
    current_date_str = pendulum.now().format('YYYYMMDD')
    
    if oldest_date_str == current_date_str:
        print("Data is already up to date.")
        return update_or_read_database(table_name, None, column_name)
    last_date_str = pendulum.parse(oldest_date_str).in_tz('Asia/Seoul').add(days=1).format('YYYYMMDD')
    print(f"Querying from data after {last_date_str} from KIS API...")
    df = query_data(current_date_str, last_date_str)
    df_all = update_or_read_database(table_name, df, column_name)
    return df_all
    
    
def query_data(latest_date:str, oldest_date:str) -> pd.DataFrame:
    """_summary_

    Args:
        latest_date (str): 조회를 시작할 날짜.
        oldest_date (str): 우리가 가지고 있는 데이터에서 가장 오래된 날짜이므로 이 날짜 이후의 데이터만 쿼리함.

    Returns:
        pd.DataFrame: _description_
    """
    # 쿼리를 시작할 날짜. 날짜 역순이므로 최근 날짜가 됨
    query_begin_date = latest_date
    df = pd.DataFrame()
    while True:
        # query_begin_date=query_begin_date.format('YYYYMMDD')
        if query_begin_date == DEFAULT_LASTEST_DATE or query_begin_date == oldest_date:
            break
        print(f"Fetching data for date: {query_begin_date}")
        result = inquire_investor_daily_by_market(
            fid_cond_mrkt_div_code="U",
            fid_input_iscd="0001",
            fid_input_date_1=query_begin_date,
            fid_input_iscd_1="KSP",
            fid_input_date_2=oldest_date,
            fid_input_iscd_2="0001",
        )
        if len(result) == 0:
            logger.info("No more data available. Exiting loop.")
            break
        
        # oldest_date 이후의 데이터만 필터링
        result_filtered = result[result['stck_bsop_date'] >= oldest_date]
        if len(result_filtered) == 0:
            logger.info("No new data found after filtering. Exiting loop.")
            break
        
        df = pd.concat([df, result_filtered], ignore_index=True)
        # print(result)

        query_begin_date = pendulum.parse(result_filtered['stck_bsop_date'].min()).in_tz('Asia/Seoul').format('YYYYMMDD')
        # print(last_date)

    return df


def download_all_kis_data():
    # file_path = data_dir / Path("domestic_stock_075_investor_daily_by_market.xlsx")
    df = download_data("domestic_stock_075_investor_daily_by_market", "stck_bsop_date")
    return df


if __name__ == "__main__":
    download_all_kis_data()    


def date_converter(date_int):
    # 정수 형태의 YYYYMMDD를 문자열로 변환 후, pd.to_datetime으로 변환
    return pd.to_datetime(str(date_int), format='%Y%m%d')