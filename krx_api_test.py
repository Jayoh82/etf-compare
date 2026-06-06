"""
KRX Open API - ETF 전체 목록 수신 테스트
실행: python krx_api_test.py
"""
import requests
from datetime import datetime, timedelta

AUTH_KEY = "9B144B5D81B44DE6BC503BF9F91C8C729785EF5F"
BASE_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
headers = {"User-Agent": "Mozilla/5.0"}

# 최근 5 영업일 순서대로 시도
def recent_business_days(n=5):
    days, d = [], datetime.now() - timedelta(days=1)
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d.strftime("%Y%m%d"))
        d -= timedelta(days=1)
    return days

print("데이터 있는 날짜 탐색 중...")
for bas_dd in recent_business_days(5):
    r = requests.get(BASE_URL, params={"AUTH_KEY": AUTH_KEY, "basDd": bas_dd}, headers=headers, timeout=10)
    data = r.json().get("OutBlock_1", [])
    print(f"  {bas_dd}: {len(data)}개")
    if data:
        print(f"\n✅ 성공! {bas_dd} 기준 ETF {len(data)}개")
        print(f"첫 3개 항목:")
        for item in data[:3]:
            print(f"  코드={item.get('ISU_CD','?')}  종목명={item.get('ISU_NM','?')}")
        print(f"\n전체 키 목록: {list(data[0].keys())}")
        break
