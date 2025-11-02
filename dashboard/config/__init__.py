from pathlib import Path
import toml

BASE_DIR = Path(__file__).resolve().parent.parent

config=toml.load(BASE_DIR  / "config.toml")

DATA_DIR = BASE_DIR / "data"
DOWNLOAD_DATA_DIR = DATA_DIR / "downloaded"

COLUMN_KEY_DESC = {
    'stck_bsop_date': {
        'short_descs': ['기준 날짜', '영업일자'],
        'full_desc': '해당 데이터가 기록된 거래일 또는 영업 기준 날짜입니다. (일반적으로 YYYYMMDD 형식)'
    },
    'bstp_nmix_prpr': {
        'short_descs': ['시장지수 종가', '종가'],
        'full_desc': '해당 영업일의 한국 증권시장(KOSPI) 마감 시점의 시장지수 가격입니다.'
    },
    'bstp_nmix_prdy_vrss': {
        'short_descs': ['전일 대비 가격 차이', '전일 대비 등락'],
        'full_desc': '당일의 종가와 직전 영업일의 종가 간의 가격 차이(등락폭)입니다.'
    },
    'prdy_vrss_sign': {
        'short_descs': ['전일 대비 등락 부호 (1:상한, 2:상승, 3:보합, 4:하락, 5:하한)', '전일 대비 부호'],
        'full_desc': '당일 종가가 전일 종가 대비 변동한 방향을 나타내는 부호(코드)입니다.'
    },
    'bstp_nmix_prdy_ctrt': {
        'short_descs': ['전일 대비 변화율 (%)', '전일 대비 등락률'],
        'full_desc': '당일의 종가가 전일 종가 대비 변동한 비율(%)입니다. (수익률 또는 손실률)'
    },
    'bstp_nmix_oprc': {
        'short_descs': ['시장지수 시가', '시가'],
        'full_desc': '해당 영업일의 한국 증권시장(KOSPI)이 장을 시작했을 때의 시장지수 가격입니다.'
    },
    'bstp_nmix_hgpr': {
        'short_descs': ['시장지수 최고가', '고가'],
        'full_desc': '해당 영업일 중 시장지수가 기록한 가장 높은 가격입니다.'
    },
    'bstp_nmix_lwpr': {
        'short_descs': ['시장지수 최저가', '저가'],
        'full_desc': '해당 영업일 중 시장지수가 기록한 가장 낮은 가격입니다.'
    },
    'stck_prdy_clpr': {
        'short_descs': ['기준일 전날의 종가', '전일 종가'],
        'full_desc': '당일 거래의 기준이 되는 직전 영업일의 시장지수 최종 마감 가격입니다.'
    },
    # 🌐 외국인', '🏦 기관', '🙋 개인'
    'frgn_ntby_qty': {
        'short_descs': ['🌐 외국인 순매도/순매수 주식 수량', '🌐 외국인 순매수 수량'],
        'full_desc': '🌐 외국인 투자자들이 해당 영업일에 매수한 총 주식 수량에서 매도한 총 주식 수량을 뺀 순(Net) 거래 수량입니다.'
    },
    'frgn_reg_ntby_qty': {
        'short_descs': ['등록 🌐 외국인의 순매수 주식 수량', '🌐 외국인 등록자 순매수 수량'],
        'full_desc': '대한민국 금융 당국에 투자자 등록을 완료한 🌐 외국인 투자자들의 순매수 수량입니다.'
    },
    'frgn_nreg_ntby_qty': {
        'short_descs': ['미등록 🌐 외국인 등의 순매수 주식 수량', '🌐 외국인 미등록자 순매수 수량'],
        'full_desc': '등록되지 않은 🌐 외국인 투자자나 기타 역외 투자자들의 순매수 수량입니다.'
    },
    'prsn_ntby_qty': {
        'short_descs': ['🙋 개인 투자자 순매도/순매수 주식 수량', '🙋 개인 순매수 수량'],
        'full_desc': '개인 투자자들이 해당 영업일에 순수하게 매수한(매수량 - 매도량) 주식 수량입니다.'
    },
    'orgn_ntby_qty': {
        'short_descs': ['🏦 기관 투자자 전체 순매수 주식 수량', '🏦 기관 순매수 수량'],
        'full_desc': '증권, 투신, 은행, 보험, 연기금 등 모든 기관 투자자들의 총 순매수 수량입니다.'
    },
    'scrt_ntby_qty': {
        'short_descs': ['증권사(투자회사) 순매수 주식 수량', '증권 순매수 수량'],
        'full_desc': '증권사나 자기자본으로 투자하는 투자회사의 순매수 수량입니다.'
    },
    'ivtr_ntby_qty': {
        'short_descs': ['투자신탁업(투신) 순매수 주식 수량', '투신 순매수 수량'],
        'full_desc': '집합 투자 기구(펀드)를 운용하는 투자 신탁 회사의 순매수 수량입니다.'
    },
    'pe_fund_ntby_vol': {
        'short_descs': ['사모펀드 순매수 주식 수량', '사모펀드 순매수 수량'],
        'full_desc': '소수의 투자자를 대상으로 비공개적으로 자금을 모집하여 운용하는 사모펀드의 순매수 수량입니다.'
    },
    'bank_ntby_qty': {
        'short_descs': ['은행 순매수 주식 수량', '은행 순매수 수량'],
        'full_desc': '시중 은행 및 기타 금융 기관의 자기자본 운용에 의한 순매수 수량입니다.'
    },
    'insu_ntby_qty': {
        'short_descs': ['보험사 순매수 주식 수량', '보험 순매수 수량'],
        'full_desc': '보험사의 자산 운용을 통한 순매수 주식 수량입니다.'
    },
    'mrbn_ntby_qty': {
        'short_descs': ['기타 금융기관 순매수 주식 수량', '기타금융 순매수 수량'],
        'full_desc': '위에 열거된 기관 외의 기타 금융 기관(예: 신용협동기구 등)의 순매수 수량입니다.'
    },
    'fund_ntby_qty': {
        'short_descs': ['연기금 및 공제회 순매수 주식 수량', '연기금 순매수 수량'],
        'full_desc': '국민연금 등 연기금과 각종 공제회(교직원 공제회 등)의 순매수 수량입니다.'
    },
    'etc_ntby_qty': {
        'short_descs': ['기타 법인 순매수 주식 수량', '기타법인 순매수 수량'],
        'full_desc': '금융 기관 및 일반 법인이 아닌 기타 법인(주로 일반 기업)의 순매수 주식 수량입니다.'
    },
    'etc_orgt_ntby_vol': {
        'short_descs': ['기타 기관 순매수 주식 수량', '기타 기관 순매수 수량'],
        'full_desc': '위에 명시된 주요 기관 투자자 외의 기타 기관 분류에 속하는 투자 주체의 순매수 수량입니다.'
    },
    'etc_corp_ntby_vol': {
        'short_descs': ['기타 법인 순매수 주식 수량', '기타 법인 순매수 수량'],
        'full_desc': '일반적인 금융 투자자가 아닌 일반 기업, 공공 기관 등 기타 법인 분류의 순매수 수량입니다.'
    },
    'frgn_ntby_tr_pbmn': {
        'short_descs': ['🌐 외국인 순매도/순매수 금액', '🌐 외국인 순매수 거래 대금'],
        'full_desc': '외국인 투자자들이 해당 영업일에 매매한 주식의 순수 거래 대금(매수 금액 - 매도 금액)입니다.'
    },
    'frgn_reg_ntby_pbmn': {
        'short_descs': ['등록 🌐 외국인의 순매수 금액', '🌐 외국인 등록자 순매수 거래 대금'],
        'full_desc': '투자자 등록을 완료한 🌐 외국인 투자자들의 순매수 거래 대금입니다.'
    },
    'frgn_nreg_ntby_pbmn': {
        'short_descs': ['미등록 🌐 외국인 등의 순매수 금액', '🌐 외국인 미등록자 순매수 거래 대금'],
        'full_desc': '등록되지 않은 🌐 외국인 투자자나 기타 역외 투자자들의 순매수 거래 대금입니다.'
    },
    'prsn_ntby_tr_pbmn': {
        'short_descs': ['🙋 개인 투자자 순매도/순매수 금액', '🙋 개인 순매수 거래 대금'],
        'full_desc': '개인 투자자들이 해당 영업일에 순수하게 거래한 주식의 순매수 거래 대금입니다.'
    },
    'orgn_ntby_tr_pbmn': {
        'short_descs': ['🏦 기관 투자자 전체 순매수 금액', '🏦 기관 순매수 거래 대금'],
        'full_desc': '모든 기관 투자자(증권, 투신, 연기금 등)들의 총 순매수 거래 대금입니다.'
    },
    'scrt_ntby_tr_pbmn': {
        'short_descs': ['증권사(투자회사) 순매수 금액', '증권 순매수 거래 대금'],
        'full_desc': '증권사나 투자회사의 순매수 거래 대금입니다.'
    },
    'ivtr_ntby_tr_pbmn': {
        'short_descs': ['투자신탁업(투신) 순매수 금액', '투신 순매수 거래 대금'],
        'full_desc': '집합 투자 기구(펀드)를 운용하는 투자 신탁 회사의 순매수 거래 대금입니다.'
    },
    'pe_fund_ntby_tr_pbmn': {
        'short_descs': ['사모펀드 순매수 금액', '사모펀드 순매수 거래 대금'],
        'full_desc': '사모펀드의 순매수 거래 대금입니다.'
    },
    'bank_ntby_tr_pbmn': {
        'short_descs': ['은행 순매수 금액', '은행 순매수 거래 대금'],
        'full_desc': '시중 은행 및 기타 금융 기관의 자기자본 운용에 의한 순매수 거래 대금입니다.'
    },
    'insu_ntby_tr_pbmn': {
        'short_descs': ['보험사 순매수 금액', '보험 순매수 거래 대금'],
        'full_desc': '보험사의 자산 운용을 통한 순매수 거래 대금입니다.'
    },
    'mrbn_ntby_tr_pbmn': {
        'short_descs': ['기타 금융기관 순매수 금액', '기타금융 순매수 거래 대금'],
        'full_desc': '위에 열거된 기관 외의 기타 금융 기관의 순매수 거래 대금입니다.'
    },
    'fund_ntby_tr_pbmn': {
        'short_descs': ['연기금 및 공제회 순매수 금액', '연기금 순매수 거래 대금'],
        'full_desc': '국민연금 등 연기금과 각종 공제회(교직원 공제회 등)의 순매수 거래 대금입니다.'
    },
    'etc_ntby_tr_pbmn': {
        'short_descs': ['기타 법인 순매수 금액', '기타법인 순매수 거래 대금'],
        'full_desc': '금융 기관 및 일반 법인이 아닌 기타 법인(주로 일반 기업)의 순매수 거래 대금입니다.'
    },
    'etc_orgt_ntby_tr_pbmn': {
        'short_descs': ['기타 기관 순매수 금액', '기타 기관 순매수 거래 대금'],
        'full_desc': '위에 명시된 주요 기관 투자자 외의 기타 기관 분류에 속하는 투자 주체의 순매수 거래 대금입니다.'
    },
    'etc_corp_ntby_tr_pbmn': {
        'short_descs': ['기타 법인 순매수 금액', '기타 법인 순매수 거래 대금'],
        'full_desc': '일반적인 금융 투자자가 아닌 일반 기업, 공공 기관 등 기타 법인 분류의 순매수 거래 대금입니다.'
    },
    ## ECOS
    'DATA_VALUE': {
        'short_descs': ['데이터 값', '값'],
        'full_desc': 'ECOS API를 통해 조회된 특정 통계 항목의 데이터 값입니다.'
    },
    'BBHS00': {
        'short_descs': ['M2(평잔, 계절조정계열)'],
        'full_desc': '한국은행이 발표하는 M2 통화지표로, 계절조정이 적용된 평잔 기준의 광의통화량입니다.'
    },
    'BBHSJ1': {
        'short_descs': ['가계 및 비영리단체'],
        'full_desc': 'M2 통화지표 내에서 가계 및 비영리단체가 보유한 통화량을 나타냅니다.'
    },
    'BBHSJ2': {
        'short_descs': ['기업'],
        'full_desc': 'M2 통화지표 내에서 기업이 보유한 통화량을 나타냅니다.'
    },
    'BBHSJ3': {
        'short_descs': ['기타금융기관'],
        'full_desc': 'M2 통화지표 내에서 기타 금융기관이 보유한 통화량을 나타냅니다.'
    },
    'BBHSJ4': {
        'short_descs': ['기타부문'],
        'full_desc': 'M2 통화지표 내에서 기타 부문(정부, 비금융법인 등)이 보유한 통화량을 나타냅니다.'
    },
}


DATE_PRESETS = {
    "1d": {"label": "어제", "days": 1},
    "7d": {"label": "최근 7일", "days": 7},
    "14d": {"label": "최근 14일", "days": 14},
    "30d": {"label": "최근 30일", "days": 30},
    "90d": {"label": "최근 90일", "days": 90},
    "1y": {"label": "최근 1년", "days": 365},
    "2y": {"label": "최근 2년", "days": 730},
    "3y": {"label": "최근 3년", "days": 1095},
    "4y": {"label": "최근 4년", "days": 1460},
    "5y": {"label": "최근 5년", "days": 1825},
    "10y": {"label": "최근 10년", "days": 3650},
    "20y": {"label": "최근 20년", "days": 7300},
    "30y": {"label": "최근 30년", "days": 10950},
    "40y": {"label": "최근 40년", "days": 14600},
    "50y": {"label": "최근 50년", "days": 18250},
    "all": {"label": "전체 기간", "days": None},
}