from collections import OrderedDict
import json
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path('data')

def read_master_sheet(xls, sheet_name):
    df = pd.read_excel(xls, sheet_name=sheet_name)
    return df

def read_api_sheet(xls, sheet_name):
    def parse_params(df):
        params = OrderedDict()
        for idx, row in df.iterrows():
            params[row['Element']] = {
                '한글명': row['한글명'],
                'Type': row['Type'],
                'Required': row['Required'],
                'Length': row['Length'],
                'Description': row['Description'],} 
        return params

    columns =['구분', 'Element', '한글명', 'Type', 'Required', 'Length', 'Description']

    df = pd.read_excel(xls, sheet_name=sheet_name, header=None, names=columns)
    df['구분'] = df['구분'].ffill()
    df = df.replace({np.nan: None})
    
    # 컬럼 : 6개
    spec = {
        'api_name': df['구분'].iloc[0],
        'api_comm_type': df['Element'].iloc[1],
        'menu_position': df['Element'].iloc[2],
        'api_name': df['Element'].iloc[3],
        'api_id': df['Element'].iloc[4],
        'real_tr_id': df['Element'].iloc[5],
        'fake_tr_id': df['Element'].iloc[6],
        'http_method': df['Element'].iloc[8],
        'read_domain': df['Element'].iloc[9],
        'fake_domain': df['Element'].iloc[10],
        'url': df['Element'].iloc[11],
        'description': df['Element'].iloc[13],
    }
    
    groups = df.iloc[16:].groupby('구분')
    if 'Request Header' in groups.groups:
        spec['request_header'] = parse_params(groups.get_group('Request Header'))
    if 'Request Body' in groups.groups:
        spec['request_body'] = parse_params(groups.get_group('Request Body'))
    if 'Response Header' in groups.groups:
        spec['response_header'] = parse_params(groups.get_group('Response Header'))
    if 'Response Body' in groups.groups:
        spec['response_body'] = parse_params(groups.get_group('Response Body'))
    if 'Request Example (Python)' in groups.groups:
        spec['request_example(python)'] = df.iloc[groups.get_group('Request Example (Python)').index[0], 1]
    if 'Response Example' in groups.groups:
        spec['response_example'] = df.iloc[groups.get_group('Response Example').index[0], 1]
    return spec

xls = pd.ExcelFile(DATA_DIR / '한국투자증권_오픈API_전체문서_20260118_030000.xlsx')
sheet_names = xls.sheet_names

api_specs = dict()
for sheet_name in sheet_names[1:]:
    api_specs[sheet_name] = read_api_sheet(xls, sheet_name)

with open(DATA_DIR / 'api_specs.json', 'w', encoding='utf-8') as f:
    f.write(
        json.dumps(api_specs, ensure_ascii=False, indent=4)
    )

# print(sheets)
# def get_sheet(sheet_name):
#     return sheets.get(sheet_name)