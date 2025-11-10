import copy
import json
import sqlite3
import sys
import os
from pathlib import Path
import time
import requests
import sqlite3
from sqlite3 import Error


# cwd = BASE_DIR / analysis
cwd = Path(os.getcwd())
sys.path.append(str(cwd.parents[1]))
# downloader
sys.path.append(str(cwd.parents[1] / 'dashboard'))
sys.path.append(str(cwd.parents[1] / 'dashboard' / 'downloader'))


from dashboard.config import config


BASE_URL = config['ECOS']['BASE_URL']
API_KEY = config['ECOS']['API_KEY']


database_path = Path('ecos.db')
stat_code_info_path = Path('ecos_stat_code_info.json')
stat_code_item_info_path = Path('ecos_stat_code_item_info.json')


def download_statistics_table():
    PINDEX = 1   # 시작 인덱스
    PSIZE = 868  # 요청 건수
    TYPE = "json"
    LANG = "kr"  # 한국어

    # API 요청 URL 구성
    url = f"https://ecos.bok.or.kr/api/StatisticTableList/{API_KEY}/{TYPE}/{LANG}/{PINDEX}/{PSIZE}/"
    # url_input = st.text_input('url', value=url)

    # API 요청
    response = requests.get(url)
    stat_code_info = response.json()
    
    if stat_code_info.get('RESULT'):
        print(stat_code_info)

    with open(stat_code_info_path , 'w+', encoding='utf-8') as fd:
        json.dump(stat_code_info, fd, indent=2)

    # 하나씩 읽어서 통계항목을 가져온다.
    sci = stat_code_info

    rows = sci['StatisticTableList']['row']
    new_rows = []
    for index, row in enumerate(rows):
        new_row = copy.copy(row)
        new_row['extra_info']=None        
        if row['SRCH_YN'] == 'Y':
            stat_code = row['STAT_CODE']
            stat_name = row['STAT_NAME']
            print(f'{index}/{len(rows)} : {stat_name} {stat_code}')
            url = f"https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/{TYPE}/{LANG}/{PINDEX}/{PSIZE}/{stat_code}"
            response = requests.get(url)
            stat_code_item_info = response.json()
            if stat_code_item_info.get('StatisticItemList'):
                new_row['STAT_ITEM']=stat_code_item_info['StatisticItemList']['row']
            else:
                new_row['STAT_ITEM']=[]
                new_row['extra_info']=json.dumps(stat_code_item_info)
            time.sleep(1)
        new_rows.append(new_row)
    sci['StatisticTableList']['row'] = new_rows

    with open(stat_code_item_info_path, 'w+', encoding='utf-8') as fd:
        json.dump(sci, fd, indent=2)


def create_connection(db_file):
    """
    SQLite 데이터베이스 연결을 생성합니다.
    :param db_file: 데이터베이스 파일 이름
    :return: Connection 객체 또는 None
    """
    conn = None
    try:
        # 데이터베이스 파일이 없으면 생성합니다.
        conn = sqlite3.connect(db_file)
        # 외래 키 제약 조건 활성화 (SQLite는 기본적으로 비활성화되어 있습니다)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_tables(conn, drop_tables):
    """
    주어진 SQL 명령을 사용하여 테이블을 생성합니다.
    :param conn: Connection 객체
    :return: None
    """
        
    
    # 1. StatisticTableList 테이블 생성 SQL
    sql_create_tablelist_table = """
    CREATE TABLE IF NOT EXISTS "StatisticTableList" (
        "id" 	    INTEGER NOT NULL UNIQUE,
        "P_STAT_CODE" 	TEXT,
        "STAT_CODE"     TEXT,
        "STAT_NAME"     TEXT,
        "CYCLE" 	TEXT,
        "SRCH_YN" 	TEXT,
        "ORG_NAME" 	TEXT,
        "extra_info"        TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    """

    # 2. StatisticItemList 테이블 생성 SQL
    # 주의: FOREIGN KEY 정의 시 'REFERENCES 테이블 이름 (컬럼 이름)' 형태로 수정했습니다.
    # 원래 정의: REFERENCES code_id (id) -> 수정: REFERENCES StatisticTableList (id)
    sql_create_itemlist_table = """
    CREATE TABLE IF NOT EXISTS "StatisticItemList" (
        "id" 	                INTEGER NOT NULL UNIQUE,
        "code_id"           INTEGER NOT NULL,
        "GRP_CODE" 	        TEXT,
        "GRP_NAME" 	        TEXT,
        "ITEM_CODE" 	        TEXT,
        "ITEM_NAME" 	        TEXT,
        "P_ITEM_CODE" 	        TEXT,
        "P_ITEM_NAME" 	        TEXT,
        "CYCLE" 	        TEXT,
        "START_TIME" 	        TEXT,
        "END_TIME" 	        TEXT,
        "DATA_CNT" 	        TEXT,
        "UNIT_NAME" 	        TEXT,
        "WEIGHT" 	        TEXT, 
        PRIMARY KEY("id" AUTOINCREMENT),
        FOREIGN KEY (code_id)
            REFERENCES StatisticTableList (id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );
    """
    sql_create_valuelist_table = """
    CREATE TABLE IF NOT EXISTS "StatisticItemValueList" (
        "id" 	        INTEGER NOT NULL UNIQUE,
        "item_id"       INTEGER NOT NULL,
        "ITEM_CODE1"	INTEGER,
        "ITEM_NAME1"	TEXT,
        "ITEM_CODE2"	INTEGER,
        "ITEM_NAME2"	TEXT,
        "ITEM_CODE3"	INTEGER,
        "ITEM_NAME3"	TEXT,
        "ITEM_CODE4"	INTEGER,
        "ITEM_NAME4"	TEXT,        
        "UNIT_NAME"	    TEXT,
        "WGT"           TEXT,
        "TIME"	        TEXT,
        "DATA_VALUE"	REAL,
        PRIMARY KEY("id" AUTOINCREMENT),
        FOREIGN KEY (item_id)
            REFERENCES StatisticItemList (id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    )
    """
    
    try:
        c = conn.cursor()
        if drop_tables:
            c.execute('drop table if exists StatisticItemValueList')
            c.execute('drop table if exists StatisticItemList')
            c.execute('drop table if exists StatisticTableList')
        
        print("StatisticTableList 테이블 생성 시도...")
        c.execute(sql_create_tablelist_table)
        print("StatisticTableList 테이블 생성 완료.")
        
        print("StatisticItemList 테이블 생성 시도...")
        c.execute(sql_create_itemlist_table)
        print("StatisticItemList 테이블 생성 완료.")
        
        print("StatisticItemValueList 테이블 생성 시도...")
        c.execute(sql_create_valuelist_table)
        print("StatisticItemValueList 테이블 생성 완료.")
        
        conn.commit()
        
    except Error as e:
        print(f"Error creating tables: {e}")


def insert_data(conn, stat_code_item_info):
    
    cursor = conn.cursor()

    # 레코드 삽입
    for row in stat_code_item_info['StatisticTableList']['row']:
        columns = list(row.keys())
        values = list(row.values())
        if 'STAT_ITEM' in columns:
            columns.remove('STAT_ITEM')
            values.pop()
        cols = ','.join(['{}']*len(columns))
        sql_insert_format=f'INSERT INTO StatisticTableList({cols}) VALUES (?, ?, ?, ?, ?, ?, ?)'
        sql_insert = sql_insert_format.format(*columns)
        cursor.execute(sql_insert, values)
        statistic_table_list_id = cursor.lastrowid
        for item_row in row.get('STAT_ITEM', []):
            filtered_item_row = copy.copy(item_row)
            del(filtered_item_row['STAT_CODE'])
            del(filtered_item_row['STAT_NAME'])
            item_columns = list(filtered_item_row.keys())
            item_values = list(filtered_item_row.values())
            item_columns.insert(0, 'code_id')
            item_values.insert(0, statistic_table_list_id)
            sql_insert_item='''INSERT INTO StatisticItemList(
                {}, {}, {}, {}, {}, 
                {}, {}, {}, {}, {}, 
                {}, {}, {}) 
                VALUES 
                (?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, 
                ?, ?, ?)'''.format(*item_columns)
            cursor.execute(sql_insert_item, item_values)

    conn.commit()
        
def main():
    
    # download_statistics_table()
    
    with open(stat_code_item_info_path, 'r', encoding='utf-8') as fd:
        stat_code_item_info = json.load(fd)
            
    # 데이터베이스 연결 생성
    conn = create_connection(database_path)

    if conn is not None:
        # 테이블 생성
        create_tables(conn, drop_tables=True)
        insert_data(conn, stat_code_item_info)
        conn.close()
    else:
        print("데이터베이스 연결을 생성할 수 없습니다.")


if __name__ == '__main__':
    main()
    

 
