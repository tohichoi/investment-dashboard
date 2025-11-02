from pathlib import Path
import sys
import logging
import pendulum
import pandas as pd
import os

# Add parent directory to system path to find kis_auth module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_dir = os.path.join(parent_dir, 'data/downloaded')
sys.path.insert(0, parent_dir)


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


def download_data(local_file_name):
    if local_file_name.exists():
        df = pd.read_excel(local_file_name)
        print(df)
        return df
    else:
        print(f"File {local_file_name} does not exist. Querying data from KIS API...")
        df = query_data(start_date)
        df.to_excel(local_file_name, index=False)
        return df
    
    
def query_data(start_date):
    last_date = start_date
    df = pd.DataFrame()
    while True:
        ld=last_date.format('YYYYMMDD')
        if ld == '19830104':
            break
        print(f"Fetching data for date: {ld}")
        result = inquire_investor_daily_by_market(
            fid_cond_mrkt_div_code="U",
            fid_input_iscd="0001",
            fid_input_date_1=ld,
            fid_input_iscd_1="KSP",
            fid_input_date_2=ld,
            fid_input_iscd_2="0001",
        )
        if len(result) == 0:
            logger.info("No more data available. Exiting loop.")
            break
        
        df = pd.concat([df, result], ignore_index=True)
        # print(result)

        last_date = pendulum.parse(result.tail(1)['stck_bsop_date'].to_list()[0]).in_tz('Asia/Seoul')
        # print(last_date)

    return df


def download_all_kis_data():
    file_path = data_dir / Path("domestic_stock_075_investor_daily_by_market.xlsx")
    df = download_data(file_path)
    return df


if __name__ == "__main__":
    download_all_kis_data()    