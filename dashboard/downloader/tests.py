import unittest
import requests
import urllib3
import rich
import pandas as pd


class TestECOSDownloader(unittest.TestCase):
    @unittest.skip("Placeholder test for ECOS API")
    def test_placeholder(self):
        from config import config
        base_url = config['ECOS']['BASE_URL']
        api_key = config['ECOS']['API_KEY']
        
        # https://ecos.bok.or.kr/api/StatisticTableList/<API_KEY>/xml/kr/1/10/903Y012
        
        # 소비자심리지수는 통계표코드 511Y004, 통계항목코드1 FME로 조회하실 수 있습니다.
        # 아래 url 이용하시기 바랍니다.
        #http://ecos.bok.or.kr/api/StatisticSearch/인증키/json/kr/1/48/511Y004/M/202207/999999/FME
        
        
        # # 요청 인자 (Parameter),필수 여부,자료형,설명
        # Key,필수,String,발급받은 인증키 (공공데이터포털 또는 ECOS 등록키)
        # Type,필수,String,"요청 파일 타입 (예: xml, json)"
        # Service Name,필수,String,호출할 서비스명 (예: StatisticSearch)
        # Start / End Index,필수,Integer,요청할 데이터의 시작/종료 위치 (예: 1/100)
        # P_CONT_ID,선택,String,(조건 검색) 통계표 코드 (예: 200Y001)
        # P_ITEM_ID,선택,String,(조건 검색) 통계 항목 코드 (예: I0001)
        # P_FROM / P_TO,선택,String,(기간 검색) 검색 시작/종료 기간 (예: 20240101/20241231)
        # P_CYCLE,선택,String,"(주기 검색) 데이터 주기 (예: D (일), M (월), Q (분기), A (연))"
        # P_UNIT,선택,String,"(단위 검색) 검색 단위 (예: 원, 천원)"
        
        #  3.1.1.1. 주요국 통화의 대원화환율
        url = f'{base_url}/StatisticSearch/{api_key}/json/kr/1/10/71Y001/D/20250101/20251031/0000001'
        
        # 1.1.3.2.1. M2 경제주체별 보유현황(평잔, 계절조정계열)
        url = f'{base_url}/StatisticSearch/{api_key}/json/kr/1/10/71Y001/D/20250101/20251031/0000001'
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            print(data)        

            print('Total count:', data['StatisticSearch']['list_total_count'])
            row_data = r.json()['StatisticSearch']['row']
            index = pd.to_datetime([ item['TIME'] for item in row_data ], format='%Y%m%d')
            
            df = pd.DataFrame(row_data, index=index)
            df['TIME'] = pd.to_datetime(df['TIME'], format='%Y%m%d')
            df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'])
            df.set_index('TIME', inplace=True)
            rich.print(df)
        else:
            print(f"ECOS API request failed with status code {r.json()}")
            raise Exception(f"ECOS API request failed with status code {r.status_code}")
        # rich.print(r.json())
        # self.assertTrue(True)
        
    def test_ecos_func(self):
        from downloader.ecos import get_m2_money_supply
        df = get_m2_money_supply('20250101', '20251031')
        rich.print(df)
        self.assertTrue(not df.empty)