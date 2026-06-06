"""
ETF 정밀 비교 웹앱
실행: streamlit run etf_app.py
추가 설치 (더 많은 ETF 검색): pip install pykrx
"""

import math
import json
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# ─────────────────────────────────────────────
# 내장 ETF 목록 (주요 ETF 300여 개)
# ─────────────────────────────────────────────
BUILTIN_ETF = {
    # KODEX
    "069500": "KODEX 200",
    "229200": "KODEX 코스닥150",
    "122630": "KODEX 레버리지",
    "114800": "KODEX 인버스",
    "251340": "KODEX 코스닥150레버리지",
    "252670": "KODEX 200선물인버스2X",
    "278540": "KODEX MSCI Korea TR",
    "243890": "KODEX 한국대만IT프리미어",
    "379800": "KODEX 미국S&P500TR",
    "360750": "KODEX 미국S&P500",  # 실제로는 TIGER지만 편의상
    "133690": "KODEX 미국나스닥100TR",
    "304940": "KODEX 미국채울트라30년선물(H)",
    "308620": "KODEX 미국채10년선물",
    "200020": "KODEX 코스피100",
    "292150": "KODEX 200미국채혼합",
    "294400": "KODEX 삼성그룹",
    "102780": "KODEX 삼성그룹",
    "098560": "KODEX 은행",
    "091160": "KODEX 반도체",
    "091180": "KODEX 자동차",
    "266410": "KODEX 바이오",
    "143460": "KODEX 국고채10년",
    "148070": "KODEX 국고채3년",
    "272580": "KODEX 국고채30년액티브",
    "385540": "KODEX 단기채권PLUS",
    "153130": "KODEX 단기채권",
    "182480": "KODEX 단기변동금리부채권액티브",
    "214980": "KODEX 안정적배당주액티브",
    "280940": "KODEX 배당성장",
    "117460": "KODEX 배당가치",
    "352560": "KODEX 혁신기술테마액티브",
    "400070": "KODEX 2차전지산업",
    "466940": "KODEX 미국AI테크10",
    "453810": "KODEX 미국배당다우존스",
    "427150": "KODEX 미국빅테크10",
    "489870": "KODEX 미국나스닥100데일리커버드콜",
    # TIGER
    "360750": "TIGER 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "195930": "TIGER 해외상장리츠(합성H)",
    "232080": "TIGER 코스닥150",
    "104530": "TIGER 200",
    "143850": "TIGER 국고채3년",
    "148070": "TIGER 국고채10년",
    "306070": "TIGER MSCI Korea TR",
    "329200": "TIGER 미국채10년선물",
    "304660": "TIGER 미국채30년스트립액티브(합성H)",
    "411900": "TIGER 미국배당+3%프리미엄다우존스",
    "458730": "TIGER 미국배당다우존스",
    "381170": "TIGER 미국나스닥100TR",
    "364980": "TIGER 미국S&P500TR",
    "367380": "TIGER 미국테크TOP10INDXX",
    "466920": "TIGER 미국AI빅테크10",
    "434080": "TIGER 차이나항셍테크",
    "192090": "TIGER 차이나CSI300",
    "371460": "TIGER 미국MSCI리츠(합성H)",
    "273130": "TIGER 200커버드콜5%OTM",
    "290080": "TIGER 200커버드콜ATM",
    "161510": "TIGER 차이나항셍25",
    "310080": "TIGER 미국달러단기채권액티브",
    "333940": "TIGER 단기채권액티브",
    "219480": "TIGER 유로스탁스배당30",
    "245710": "TIGER 글로벌자원생산기업(합성H)",
    "491830": "TIGER 미국나스닥100커버드콜(합성)",
    "463050": "TIGER 미국S&P500커버드콜(합성)",
    "494670": "TIGER 미국배당다우존스커버드콜채권혼합",
    # ACE
    "360200": "ACE 미국S&P500",
    "195980": "ACE 미국나스닥100",
    "411060": "ACE 미국빅테크TOP7Plus",
    "449180": "ACE 미국배당다우존스",
    "442580": "ACE 미국30년국채액티브(H)",
    "292340": "ACE KRX금현물",
    "269540": "ACE 미국달러단기채권액티브",
    "396500": "TIGER 반도체TOP10",
    "426410": "ACE 글로벌메타버스테크액티브",
    "466110": "ACE 미국AI반도체나스닥",
    "480350": "ACE 미국AI빅테크TOP10 indxx",
    "475080": "ACE 미국배당다우존스커버드콜",
    # KBSTAR
    "308170": "KBSTAR 미국S&P500",
    "341000": "KBSTAR 미국나스닥100",
    "266160": "KBSTAR 200",
    "140710": "KBSTAR 단기통안채",
    "365780": "KBSTAR 미국장기국채선물(H)",
    "381060": "KBSTAR 글로벌리얼티인컴",
    "411400": "KBSTAR 미국배당킹ETF",
    "458760": "KBSTAR 미국배당다우존스",
    "459580": "KBSTAR 국고채30년액티브",
    # HANARO
    "367770": "HANARO 미국배당다우존스",
    "441680": "HANARO 글로벌반도체TOP10 SOLACTIVE",
    "243180": "HANARO 200",
    "313640": "HANARO 200선물인버스",
    "352560": "HANARO 혁신기술",
    "466490": "HANARO 미국AI반도체나스닥",
    # ARIRANG
    "152100": "ARIRANG 200",
    "253150": "ARIRANG 코스닥150",
    "266390": "ARIRANG 미국고배당주(합성H)",
    "352480": "ARIRANG 미국나스닥기술주",
    "413160": "ARIRANG 미국장기우량회사채혼합액티브",
    # KOSEF
    "078160": "KOSEF 200",
    "137610": "KOSEF 국고채10년",
    "148020": "KOSEF 단기자금",
    # 기타
    "069660": "KOSEF 200",
    "182490": "TIGER 단기통안채",
    "157450": "TIGER 국고채3년",
    "130680": "TIGER 모멘텀",
    "395160": "TIGER 미국필라델피아반도체나스닥",
    "396520": "TIGER 글로벌BBIG",
    "334700": "KODEX 2차전지핵심소재10Fn",
    "466970": "KODEX 인도Nifty50",
    "401440": "KODEX 인도Nifty50(H)",
    "448290": "TIGER 인도니프티50",
    "453850": "TIGER 인도빅테크INDXX",
    "453730": "ACE 인도컨슈머파워액티브",
    "453940": "KODEX 일본TOPIX100",
    "241180": "TIGER 일본니케이225",
    "192720": "KODEX 일본TOPIX(H)",
    "176710": "TIGER 라틴35",
    "244580": "KODEX 유럽",
    "261240": "KODEX 선진국MSCI World",
    "251350": "MIRAE ASSET TIGER 글로벌4차산업혁신기술(합성H)",
    "416800": "TIGER S&P글로벌인프라(합성H)",
    "329750": "TIGER 미국MSCIAll Country World",
    "396300": "TIGER 미국S&P500배당귀족",
    "463240": "TIGER 미국TSMC2배레버리지(합성)",
    "314700": "KODEX 200커버드콜",
    "458950": "KODEX 미국배당커버드콜액티브",
    "483290": "TIGER 미국S&P500커버드콜채권혼합액티브",
    "488290": "ACE 미국배당다우존스커버드콜(합성)",
    "490590": "KODEX 미국나스닥100커버드콜(합성)",
    "495660": "TIGER 인도니프티50커버드콜(합성)",
    "438300": "ACE KRX혁신기업나스닥20",
}

# ─────────────────────────────────────────────
# KRX ETF 목록 로드 (pykrx 또는 내장 목록)
# ─────────────────────────────────────────────
# API 키: 로컬은 하드코딩, 클라우드는 st.secrets에서 읽음
try:
    KRX_AUTH_KEY = st.secrets["KRX_AUTH_KEY"]
except Exception:
    KRX_AUTH_KEY = "9B144B5D81B44DE6BC503BF9F91C8C729785EF5F"
KRX_ETF_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"

@st.cache_data(ttl=3600, show_spinner=False)
def load_etf_list() -> pd.DataFrame:
    """ETF 목록: KRX 공식 API → 네이버 금융 → 내장 목록 순으로 시도"""
    errors = []

    # 1순위: KRX 공식 Open API
    try:
        import requests
        from datetime import datetime, timedelta
        headers = {"User-Agent": "Mozilla/5.0"}
        # 최근 영업일 순서대로 데이터 탐색
        d = datetime.now() - timedelta(days=1)
        for _ in range(7):
            if d.weekday() < 5:
                bas_dd = d.strftime("%Y%m%d")
                r = requests.get(KRX_ETF_URL,
                                 params={"AUTH_KEY": KRX_AUTH_KEY, "basDd": bas_dd},
                                 headers=headers, timeout=10)
                items = r.json().get("OutBlock_1", [])
                if items:
                    df = pd.DataFrame(items)[["ISU_CD", "ISU_NM"]].copy()
                    df.columns = ["code", "name"]
                    df["code"] = df["code"].str.strip()
                    df["name"] = df["name"].str.strip()
                    df["source"] = "krx"
                    df["errors"] = ""
                    return df
            d -= timedelta(days=1)
        errors.append("KRX: 최근 7일 데이터 없음")
    except Exception as e:
        errors.append(f"KRX: {e}")

    # 2순위: 네이버 금융 API
    try:
        import requests
        url = "https://finance.naver.com/api/sise/etfItemList.nhn"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0",
                                        "Referer": "https://finance.naver.com/"}, timeout=10)
        j = r.json()
        items = (j.get("resultData", {}).get("etfItemList")
                 or j.get("etfItemList")
                 or j.get("result", {}).get("etfItemList") or [])
        if items:
            df = pd.DataFrame(items)
            code_col = next((c for c in df.columns if "code" in c.lower() or "cd" in c.lower()), df.columns[0])
            name_col = next((c for c in df.columns if "name" in c.lower() or "nm" in c.lower()), df.columns[1])
            df = df[[code_col, name_col]].rename(columns={code_col: "code", name_col: "name"})
            df["code"] = df["code"].astype(str).str.strip()
            df["name"] = df["name"].astype(str).str.strip()
            df["source"] = "naver"
            df["errors"] = " | ".join(errors)
            return df
    except Exception as e:
        errors.append(f"네이버: {e}")

    # 3순위: 내장 목록
    rows = [{"code": k, "name": v} for k, v in BUILTIN_ETF.items()]
    df = pd.DataFrame(rows).drop_duplicates("code")
    df["source"] = "builtin"
    df["errors"] = " | ".join(errors)
    return df


# ─────────────────────────────────────────────
# 헬퍼 함수
# ─────────────────────────────────────────────
# 가독성 높은 고대비 색상 팔레트
COLORS = [
    "#2563EB",  # 블루
    "#DC2626",  # 레드
    "#16A34A",  # 그린
    "#D97706",  # 앰버
    "#7C3AED",  # 바이올렛
    "#0891B2",  # 시안
    "#DB2777",  # 핑크
    "#EA580C",  # 오렌지
    "#059669",  # 에메랄드
    "#4F46E5",  # 인디고
    "#B45309",  # 옐로우브라운
    "#BE185D",  # 로즈
]

def hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def normalize_ticker(raw: str) -> str:
    raw = raw.strip().upper()
    if raw.isdigit() and len(raw) == 6:
        return raw + ".KS"
    return raw

KRX_NAME_CORRECTIONS = {
    "396500": "TIGER 반도체TOP10",
}

def get_korean_name(ticker: str, etf_df: pd.DataFrame) -> str:
    code = ticker.replace(".KS", "")
    if not code.isdigit():
        return ticker  # 미국 ETF는 그대로
    # 최우선: 알려진 KRX 데이터 오류 하드코딩 수정
    if code in KRX_NAME_CORRECTIONS:
        return KRX_NAME_CORRECTIONS[code]
    # 1순위: 사용자가 직접 지정한 이름
    overrides = st.session_state.get("name_overrides", {})
    if code in overrides:
        return overrides[code]
    # 2순위: 로드된 ETF 목록
    row = etf_df[etf_df["code"] == code]
    if not row.empty:
        return row.iloc[0]["name"]
    # 3순위: 네이버 금융 개별 조회
    naver_name = fetch_naver_name(code)
    if naver_name:
        return naver_name
    return ticker

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_krx_name(code: str) -> str:
    """KRX Data Marketplace API에서 ETF 공식 이름 가져오기"""
    try:
        import requests
        url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr/",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "bld": "dbms/comm/finder/finderStkIsuSrch",
            "locale": "ko_KR",
            "searchText": code,
            "mktsel": "ETF",
            "pagePath": "/contents/MDC/MDI/mdiLoader/index.cmd",
        }
        r = requests.post(url, data=payload, headers=headers, timeout=5)
        data = r.json()
        rows = data.get("block1", [])
        for row in rows:
            if row.get("short_isin_cd", "").strip() == code:
                return row.get("isu_nm", "").strip()
    except Exception:
        pass
    return ""

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naver_name(code: str) -> str:
    """네이버 금융에서 ETF 이름 가져오기 (KRX 보조)"""
    try:
        import requests, re
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"}
        r = requests.get(url, headers=headers, timeout=5)
        match = re.search(r"<title>\s*(.+?)\s*:", r.text)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return ""

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker: str, period: str):
    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if hist.empty:
            return None
        return hist["Close"].dropna()
    except Exception:
        return None

def calc_metrics(closes: pd.Series, rf: float = 0.035) -> dict:
    if len(closes) < 5:
        return {}
    rets = closes.pct_change().dropna()
    total_ret = closes.iloc[-1] / closes.iloc[0] - 1
    years = len(rets) / 252
    cagr = (1 + total_ret) ** (1/years) - 1 if years > 0 else float("nan")
    vol = rets.std() * math.sqrt(252)
    mdd = ((closes - closes.cummax()) / closes.cummax()).min()
    sharpe = (cagr - rf) / vol if vol > 0 else float("nan")
    down = rets[rets < 0]
    dv = down.std() * math.sqrt(252) if len(down) > 0 else float("nan")
    sortino = (cagr - rf) / dv if (dv and not math.isnan(dv)) else float("nan")
    calmar = cagr / abs(mdd) if mdd != 0 else float("nan")
    return dict(total_ret=total_ret, cagr=cagr, vol=vol,
                mdd=mdd, sharpe=sharpe, sortino=sortino, calmar=calmar)

def color_val(v, is_pct=True):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    val = v * 100 if is_pct else v
    c = "#dc2626" if val > 0 else ("#2563eb" if val < 0 else "#6b7280")
    t = f"{val:+.1f}%" if is_pct else f"{val:+.2f}"
    return f'<span style="color:{c};font-weight:600">{t}</span>'


# ─────────────────────────────────────────────
# 앱 시작
# ─────────────────────────────────────────────
st.set_page_config(page_title="ETF 정밀 비교", page_icon="📊", layout="wide")
st.markdown("""
<style>
  /* ── 기본 레이아웃 ── */
  .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 1200px;
  }
  h1 { font-size: 1.6rem !important; font-weight: 800 !important; letter-spacing: -0.5px; }
  h3 { font-size: 1rem !important; font-weight: 700 !important; color: #1e293b; margin-top: 4px; }

  /* ── 버튼 ── */
  .stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    min-height: 40px !important;
    font-size: 14px !important;
    white-space: nowrap !important;
  }
  /* X 버튼 — 작게 */
  [data-testid="stSidebar"] .stButton button {
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 6px !important;
    font-size: 12px !important;
    line-height: 1 !important;
  }

  /* ── 입력창 ── */
  .stTextInput > div > div > input {
    min-height: 44px !important;
    font-size: 15px !important;
    border-radius: 8px !important;
  }

  /* ── 라디오 버튼 ── */
  .stRadio > div { gap: 4px; }
  .stRadio label { font-size: 13px !important; }

  /* ── 체크박스 ── */
  .stCheckbox label { font-size: 13px !important; }

  /* ── 테이블 가로 스크롤 ── */
  div[data-testid="stMarkdownContainer"] div[style*="overflow-x"] {
    -webkit-overflow-scrolling: touch;
  }

  /* ── 사이드바 ── */
  [data-testid="stSidebar"] {
    min-width: 260px !important;
    max-width: 320px !important;
  }
  [data-testid="stSidebar"] .block-container {
    padding: 1rem 0.8rem !important;
  }

  /* ── 모바일 (768px 이하) ── */
  @media (max-width: 768px) {
    .block-container {
      padding-left: 0.8rem !important;
      padding-right: 0.8rem !important;
    }
    h1 { font-size: 1.3rem !important; }
    h3 { font-size: 0.95rem !important; }

    /* 요약 카드 2열로 줄이기 */
    div[data-testid="column"] {
      min-width: 45% !important;
    }

    /* 차트 여백 줄이기 */
    .js-plotly-plot { margin: 0 !important; }

    /* 테이블 폰트 줄이기 */
    table { font-size: 11px !important; }
    th, td { padding: 6px 8px !important; }

    /* 버튼 전체 너비 */
    .stButton > button { width: 100% !important; }
  }

  /* ── 초소형 (480px 이하) ── */
  @media (max-width: 480px) {
    h1 { font-size: 1.15rem !important; }
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    table { font-size: 10px !important; }
    th, td { padding: 5px 6px !important; }
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 로그인 처리 (bcrypt 직접 사용)
# ─────────────────────────────────────────────
def do_login():
    st.markdown("## 🔐 ETF 정밀 비교 — 로그인")
    with st.form("login_form"):
        uid = st.text_input("아이디")
        pwd = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", use_container_width=True)
    if submitted:
        try:
            users = st.secrets["credentials"]["usernames"]
            if uid in users:
                stored = users[uid]["password"].strip().encode()
                if BCRYPT_AVAILABLE and bcrypt.checkpw(pwd.encode(), stored):
                    st.session_state["_auth"] = True
                    st.session_state["_username"] = uid
                    st.session_state["_name"] = users[uid].get("name", uid)
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 틀렸습니다.")
            else:
                st.error("❌ 존재하지 않는 아이디입니다.")
        except Exception as e:
            st.error(f"로그인 오류: {e}")

HAS_AUTH = "credentials" in st.secrets and BCRYPT_AVAILABLE

if HAS_AUTH:
    if not st.session_state.get("_auth"):
        do_login()
        st.stop()
    username     = st.session_state["_username"]
    current_user = st.session_state["_name"]
    USER_SAVE_FILE = Path(__file__).parent / f"watchlist_{username}.json"
else:
    username = "local"
    current_user = "로컬 사용자"
    USER_SAVE_FILE = Path(__file__).parent / "etf_watchlist.json"

# 캐시 강제 초기화 (데이터 소스 변경 반영)
load_etf_list.clear()

with st.spinner("ETF 목록 불러오는 중..."):
    etf_df = load_etf_list().copy()

# ── KRX 데이터 오류 수정 ──────────────────────────
# 1단계: 잘못된 이름 키워드로 수정
KNOWN_NAME_FIXES = {
    "피규어": "TIGER 반도체TOP10",  # 396500
}
for wrong_kw, correct in KNOWN_NAME_FIXES.items():
    etf_df.loc[etf_df["name"].str.contains(wrong_kw, na=False), "name"] = correct

# 2단계: 중복 이름 제거 (코드가 짧은 쪽 우선 유지)
etf_df["_code_len"] = etf_df["code"].str.len()
etf_df = etf_df.sort_values("_code_len").drop_duplicates("name", keep="first").drop(columns="_code_len").reset_index(drop=True)

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    # 사용자 정보 & 로그아웃
    col_user, col_logout = st.columns([3, 1])
    col_user.markdown(f"👤 **{current_user}**님")
    if HAS_AUTH:
        with col_logout:
            if st.button("나가기", key="logout_btn"):
                st.session_state["_auth"] = False
                st.rerun()

    st.markdown("## 📊 ETF 정밀 비교")
    source = etf_df["source"].iloc[0] if not etf_df.empty else "builtin"
    err_msg = etf_df["errors"].iloc[0] if "errors" in etf_df.columns else ""
    if source == "krx":
        st.caption(f"✅ KRX 공식 API · ETF {len(etf_df)}개")
    elif source == "naver":
        st.caption(f"✅ 네이버금융 · ETF {len(etf_df)}개")
    else:
        st.caption(f"⚠️ 내장 목록 · ETF {len(etf_df)}개")
    if err_msg:
        with st.expander("❌ 오류 상세 보기"):
            st.code(err_msg)

    # 전체 목록 검색기
    with st.expander("📋 전체 ETF 목록 보기"):
        all_q = st.text_input("이름/코드 검색", key="all_search")
        if all_q:
            found = etf_df[etf_df["name"].str.contains(all_q, case=False, na=False) |
                           etf_df["code"].str.contains(all_q, na=False)]
            st.dataframe(found[["code","name"]].reset_index(drop=True), height=200)
        else:
            st.dataframe(etf_df[["code","name"]].head(50).reset_index(drop=True), height=200)
    st.divider()

    # 종목 목록을 파일로 영구 저장 (앱 재시작 후에도 유지)
    # 사용자별 종목 파일 사용
    SAVE_FILE = USER_SAVE_FILE

    def load_tickers():
        try:
            return json.load(open(SAVE_FILE, encoding="utf-8"))
        except Exception:
            return []  # 디폴트 없음

    def save_tickers(tickers):
        try:
            json.dump(tickers, open(SAVE_FILE, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            pass

    # 사용자가 바뀌면 종목 목록 새로 로드
    if st.session_state.get("_username") != username:
        st.session_state["_username"] = username
        st.session_state.tickers = load_tickers()
        # 체크박스 상태 초기화
        for key in list(st.session_state.keys()):
            if key.startswith("chk_"):
                del st.session_state[key]

    if "tickers" not in st.session_state:
        st.session_state.tickers = load_tickers()

    # 이름 오버라이드 — 항상 초기화 (없을 때만)
    if "name_overrides" not in st.session_state:
        st.session_state.name_overrides = {}
    # 알려진 데이터 오류 자동 수정 (사용자가 지우지 않은 경우에만)
    # 알려진 KRX 데이터 오류 — 매번 강제 덮어쓰기
    known_fixes = {"396500": "TIGER 반도체TOP10"}
    for code, name in known_fixes.items():
        st.session_state.name_overrides[code] = name

    # ── 검색 ──
    st.markdown("### 🔍 ETF 검색")
    st.caption("종목명 또는 코드 검색")
    search_q = st.text_input("검색", placeholder="예: 코스피, 코스닥, 배당, 069500",
                              label_visibility="collapsed", key="search_input")

    if search_q.strip():
        q = search_q.strip()
        # 검색어를 공백으로 분리해 각 단어가 모두 포함된 결과 반환
        # 예: "반도체10" → "반도체", "10" 각각 검색
        # 예: "tiger 반도체" → "tiger", "반도체" 각각 검색
        tokens = q.split() if " " in q else [q]
        # 숫자+한글 혼합 토큰 분리 (예: "반도체10" → ["반도체", "10"])
        import re
        split_tokens = []
        for tok in tokens:
            parts = re.findall(r'[가-힣a-zA-Z]+|\d+', tok)
            split_tokens.extend(parts if parts else [tok])
        tokens = split_tokens

        mask = pd.Series([True] * len(etf_df), index=etf_df.index)
        for tok in tokens:
            mask &= (etf_df["name"].str.contains(tok, case=False, na=False) |
                     etf_df["code"].str.contains(tok, na=False))
        results = etf_df[mask].head(15)

        if results.empty:
            st.caption("검색 결과 없음")
            st.caption("코드를 직접 아는 경우 아래 '직접 입력'을 사용하세요.")
            if tokens:
                hint = etf_df[etf_df["name"].str.contains(tokens[0], case=False, na=False)].head(5)
                if not hint.empty:
                    st.caption(f"'{tokens[0]}' 관련 ETF:")
                    for _, r in hint.iterrows():
                        st.caption(f"  • {r['name']} ({r['code']})")
            st.markdown(
                "코드를 아는 경우 아래 **직접 입력**을 사용하거나,\n"
                "[네이버 금융 ETF 검색](https://finance.naver.com/sise/etf.naver)에서 찾아보세요.",
                unsafe_allow_html=False
            )
        else:
            for _, row in results.iterrows():
                ticker = row["code"] + ".KS"
                official_name = row["name"]
                c1, c2 = st.columns([7, 2])
                c1.markdown(
                    f'<div style="font-size:12px;line-height:1.4">'
                    f'<b>{official_name}</b><br>'
                    f'<span style="color:#9ca3af">{row["code"]}</span></div>',
                    unsafe_allow_html=True
                )
                if c2.button("추가", key=f"s_{row['code']}"):
                    if ticker not in st.session_state.tickers:
                        st.session_state.tickers.append(ticker)
                        save_tickers(st.session_state.tickers)
                    st.rerun()

    if st.button("🗑️ 전체삭제", use_container_width=True):
        st.session_state.tickers = []
        save_tickers([])
        st.rerun()

    st.divider()

    # ── 비교 종목 ──
    st.markdown("### 비교 종목")

    # 새로 추가된 종목의 체크박스 기본값을 True로 초기화
    for _t in st.session_state.tickers:
        if f"chk_{_t}" not in st.session_state:
            st.session_state[f"chk_{_t}"] = True

    if not st.session_state.tickers:
        st.caption("추가된 ETF가 없습니다.")
    else:
        for i, t in enumerate(st.session_state.tickers):
            kr = get_korean_name(t, etf_df)
            color = COLORS[i % len(COLORS)]
            is_active = st.session_state.get(f"chk_{t}", True)
            col_chk, col_name, col_del = st.columns([1, 5, 1])

            # 체크박스 (포함/제외) — 왼쪽
            col_chk.checkbox("", key=f"chk_{t}", label_visibility="collapsed")

            # 종목명 (비활성이면 흐리게)
            opacity = "1" if is_active else "0.35"
            col_name.markdown(
                f'<div style="color:{color};font-weight:700;font-size:12px;opacity:{opacity}">● {kr}</div>'
                f'<div style="color:#9ca3af;font-size:10px;opacity:{opacity}">{t}</div>',
                unsafe_allow_html=True
            )

            if col_del.button("✕", key=f"del_{i}"):
                st.session_state.tickers.remove(t)
                del st.session_state[f"chk_{t}"]
                save_tickers(st.session_state.tickers)
                st.rerun()

    st.divider()

    # ── 기간 ──
    st.markdown("### 비교 기간")
    period_map = {"1개월":"1mo","3개월":"3mo","6개월":"6mo",
                  "1년":"1y","2년":"2y","5년":"5y","전체":"max"}
    period_label = st.radio("기간", list(period_map.keys()),
                            index=2, label_visibility="collapsed")
    period = period_map[period_label]

    st.divider()
    run = st.button("▶ 실행", use_container_width=True, type="primary")

    st.divider()

    # ── 어제 수익률 TOP 10 ──
    st.markdown("### 🏆 어제 수익률 TOP 10")

    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_top10():
        try:
            from datetime import datetime, timedelta
            import requests
            headers = {"User-Agent": "Mozilla/5.0"}
            for i in range(1, 6):
                d = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                r = requests.get(KRX_ETF_URL,
                                 params={"AUTH_KEY": KRX_AUTH_KEY, "basDd": d},
                                 headers=headers, timeout=10)
                items = r.json().get("OutBlock_1", [])
                if items:
                    df = pd.DataFrame(items)
                    df["FLUC_RT"] = pd.to_numeric(df["FLUC_RT"], errors="coerce")
                    df["ISU_CD"] = df["ISU_CD"].str.strip()
                    top = df.nlargest(10, "FLUC_RT")[["ISU_CD","ISU_NM","FLUC_RT"]]
                    return top.values.tolist(), d
            return [], ""
        except Exception:
            return [], ""

    top10, top_date = fetch_top10()
    if top10:
        st.caption(f"{top_date[:4]}-{top_date[4:6]}-{top_date[6:]} 기준")
        for code, name, fluc in top10:
            t = code + ".KS"
            c1, c2 = st.columns([7, 2])
            c1.markdown(
                f'<div style="font-size:11px;font-weight:700">{name}</div>'
                f'<div style="font-size:10px;color:#dc2626">+{fluc:.2f}%</div>',
                unsafe_allow_html=True
            )
            if c2.button("추가", key=f"top_{code}"):
                if t not in st.session_state.tickers:
                    st.session_state.tickers.append(t)
                    save_tickers(st.session_state.tickers)
                st.rerun()
    else:
        st.caption("데이터를 불러올 수 없습니다.")


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
st.markdown("# 📊 ETF 정밀 비교")
st.caption("수익률 · 위험지표 · 상관관계 · 무제한 비교 | 데이터: Yahoo Finance")

if not st.session_state.tickers:
    st.info("👈 왼쪽에서 ETF를 검색하거나 추가 후 **실행**을 눌러주세요.")
    st.stop()

if not run and "last_data" not in st.session_state:
    st.info("👈 **🔍 실행** 버튼을 눌러주세요.")
    st.stop()

if run:
    data_map = {}
    # 체크박스로 활성화된 종목만 비교
    active = [t for t in st.session_state.tickers if t in st.session_state.get("active_tickers", set(st.session_state.tickers))]
    if not active:
        st.warning("활성화된 종목이 없습니다. 체크박스를 선택해주세요.")
        st.stop()
    with st.spinner("📥 데이터 불러오는 중..."):
        failed = []
        for t in active:
            c = fetch_data(t, period)
            if c is None or len(c) < 5:
                failed.append(t)
            else:
                data_map[t] = c
    if failed:
        st.warning(f"⚠️ 데이터 조회 실패: {', '.join(failed)}")
    if not data_map:
        st.error("유효한 데이터가 없습니다.")
        st.stop()
    st.session_state.last_data = data_map
    st.session_state.last_period = period
    st.session_state.last_period_label = period_label

# 전체 데이터에서 활성화된 종목만 필터링 (체크박스 즉시 반영)
active_set = {t for t in st.session_state.tickers if st.session_state.get(f"chk_{t}", True)}
data_map = {t: v for t, v in st.session_state.last_data.items() if t in active_set}

# 활성화 종목이 없으면 안내
if not data_map:
    st.info("☑️ 왼쪽 체크박스로 비교할 종목을 선택해주세요.")
    st.stop()

period = st.session_state.get("last_period", period)
period_label = st.session_state.get("last_period_label", period_label)
ticker_list = list(data_map.keys())
name_map = {t: get_korean_name(t, etf_df) for t in ticker_list}
closes_df = pd.DataFrame(data_map).dropna()

# ── 공통 차트 레이아웃 ──
CHART_LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="Noto Sans KR, Apple SD Gothic Neo, sans-serif", size=12, color="#0f172a"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, x=0,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#cbd5e1", borderwidth=1,
        font=dict(size=11, color="#0f172a")
    ),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc", font_size=12, bordercolor="#1e293b"),
    xaxis=dict(
        gridcolor="#e2e8f0", linecolor="#94a3b8",
        tickfont=dict(size=11, color="#1e293b"),
        title_font=dict(color="#1e293b")
    ),
    yaxis=dict(
        gridcolor="#e2e8f0", linecolor="#94a3b8",
        tickfont=dict(size=11, color="#1e293b"),
        title_font=dict(color="#1e293b")
    ),
    margin=dict(l=10, r=20, t=30, b=10),
)

# ── 요약 카드 ──
st.markdown("### 기간 수익률 요약")
n_cols = min(len(ticker_list), 4)  # 모바일 고려해 최대 4열
cols = st.columns(n_cols)
for i, t in enumerate(ticker_list):
    ret = data_map[t].iloc[-1] / data_map[t].iloc[0] - 1
    vol_ann = data_map[t].pct_change().dropna().std() * (252**0.5)
    color = COLORS[i % len(COLORS)]
    rc = "#16A34A" if ret > 0 else "#DC2626"
    nm = name_map[t]
    nm_s = nm[:15] + "…" if len(nm) > 15 else nm
    with cols[i % n_cols]:
        st.markdown(f"""
        <div style="background:#fff;border-top:3px solid {color};border-radius:10px;
             padding:12px 10px;box-shadow:0 1px 4px rgba(0,0,0,0.06);word-break:keep-all">
          <div style="color:{color};font-weight:700;font-size:11px;letter-spacing:0.3px;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nm_s}</div>
          <div style="color:#94a3b8;font-size:10px;margin:2px 0 6px">{t.replace('.KS','')}</div>
          <div style="color:{rc};font-weight:800;font-size:22px;line-height:1">{ret*100:+.1f}%</div>
          <div style="color:#94a3b8;font-size:10px;margin-top:5px">변동성 {vol_ann*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 누적 수익률 차트 ──
st.markdown("### 📈 누적 수익률 비교")
norm_df = closes_df / closes_df.iloc[0] * 100
fig = go.Figure()
for i, col in enumerate(norm_df.columns):
    color = COLORS[i % len(COLORS)]
    fig.add_trace(go.Scatter(
        x=norm_df.index, y=norm_df[col].round(2),
        name=name_map[col],
        mode="lines",
        line=dict(color=color, width=2.5),
        hovertemplate=f"<b>{name_map[col]}</b>: %{{y:.1f}}<extra></extra>"
    ))
fig.update_layout(**CHART_LAYOUT, height=340)
fig.update_yaxes(title="기준 100", title_font=dict(size=11))
st.plotly_chart(fig, use_container_width=True)

# ── 위험 지표 테이블 ──
st.markdown("### 📊 위험·성과 지표")
st.caption("무위험수익률 3.5% 가정 · 연환산 기준")

th_s = ("background:#f8fafc;color:#475569;font-size:11px;font-weight:700;"
        "padding:10px 14px;text-align:right;border-bottom:2px solid #e2e8f0;"
        "white-space:nowrap;letter-spacing:0.3px")
th_l = th_s.replace("text-align:right", "text-align:left")
td_r = "padding:10px 14px;border-bottom:1px solid #f1f5f9;text-align:right;vertical-align:middle"
td_l = td_r.replace("text-align:right", "text-align:left")

html = (f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #e2e8f0;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.04)">'
        f'<table style="width:100%;border-collapse:collapse;font-size:12px">'
        f'<thead><tr>')
for h, align in [("ETF명","l"),("코드","l"),("기간수익률","r"),("CAGR","r"),
                  ("변동성","r"),("MDD","r"),("Sharpe","r"),("Sortino","r"),("Calmar","r")]:
    html += f'<th style="{th_l if align=="l" else th_s}">{h}</th>'
html += "</tr></thead><tbody>"

for i, t in enumerate(ticker_list):
    m = calc_metrics(data_map[t])
    if not m:
        continue
    color = COLORS[i % len(COLORS)]
    dot = (f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
           f'background:{color};margin-right:8px;vertical-align:middle"></span>')
    bg = "#fafafa" if i % 2 == 0 else "#ffffff"
    row_style = f'background:{bg}'
    html += f"""<tr style="{row_style}">
      <td style="{td_l}">{dot}<strong style="color:#1e293b">{name_map[t]}</strong></td>
      <td style="{td_l};color:#94a3b8;font-size:11px;font-family:monospace">{t.replace('.KS','')}</td>
      <td style="{td_r}">{color_val(m['total_ret'])}</td>
      <td style="{td_r}">{color_val(m['cagr'])}</td>
      <td style="{td_r}">{color_val(m['vol'])}</td>
      <td style="{td_r}">{color_val(m['mdd'])}</td>
      <td style="{td_r}">{color_val(m['sharpe'],False)}</td>
      <td style="{td_r}">{color_val(m['sortino'],False)}</td>
      <td style="{td_r}">{color_val(m['calmar'],False)}</td>
    </tr>"""
html += "</tbody></table></div>"
st.markdown(html, unsafe_allow_html=True)

with st.expander("지표 설명"):
    st.markdown("""
| 지표 | 설명 |
|---|---|
| **기간수익률** | 선택 기간 전체 수익률 |
| **CAGR** | 연평균 복리 수익률 |
| **변동성** | 연환산 표준편차. 낮을수록 안정적 |
| **MDD** | 최고점 대비 최대 낙폭 |
| **Sharpe** | 위험 대비 초과수익 (rf=3.5%). 높을수록 좋음 |
| **Sortino** | 하방 위험 대비 초과수익 |
| **Calmar** | CAGR ÷ MDD. 1 이상이면 우수 |
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── 상관관계 매트릭스 ──
st.markdown("### 🔗 상관관계 매트릭스")
if len(ticker_list) >= 2:
    corr = closes_df.pct_change().dropna().corr().round(2)
    labels = [name_map[t] for t in corr.columns]
    # RdBu_r: 음수=파랑, 0=흰색, 양수=빨강 — 직관적인 표준 색상
    fig2 = go.Figure(go.Heatmap(
        z=corr.values, x=labels, y=labels,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=12, color="black"),
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        showscale=True,
        colorbar=dict(
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0<br>역상관", "-0.5", "0<br>무관", "0.5", "+1.0<br>동조"],
            thickness=14, len=0.8,
            tickfont=dict(size=10)
        ),
        hovertemplate="<b>%{y}</b><br>vs %{x}<br>상관계수: %{z:.2f}<extra></extra>"
    ))
    cell_size = max(55, min(80, 500 // max(len(ticker_list), 1)))
    fig2.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k not in ("xaxis","yaxis","hovermode")},
        height=max(320, len(ticker_list) * cell_size + 120),
        hovermode="closest",
        xaxis=dict(tickfont=dict(size=11, color="#1e293b"), tickangle=-30, side="bottom"),
        yaxis=dict(tickfont=dict(size=11, color="#1e293b"), autorange="reversed"),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("파랑 → 역상관 | 흰색 → 무관 | 빨강 → 강한 동조")
else:
    st.info("ETF 2개 이상부터 표시됩니다.")

st.markdown("<br>", unsafe_allow_html=True)

# ── 드로우다운 차트 ──
st.markdown("### 📉 최대낙폭 (Drawdown) 추이")
fig3 = go.Figure()
for i, t in enumerate(ticker_list):
    c = data_map[t]
    dd = (c - c.cummax()) / c.cummax() * 100
    color = COLORS[i % len(COLORS)]
    fig3.add_trace(go.Scatter(
        x=dd.index, y=dd.round(2),
        name=name_map[t],
        mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=1.8),
        fillcolor=hex_to_rgba(color, 0.08),
        hovertemplate=f"<b>{name_map[t]}</b>: %{{y:.2f}}%<extra></extra>"
    ))
fig3.update_layout(**CHART_LAYOUT, height=320)
fig3.update_yaxes(ticksuffix="%", title="낙폭(%)", title_font=dict(size=11))
st.plotly_chart(fig3, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 연도별 수익률 ──────────────────────────────
st.markdown("### 📅 연도별 수익률")

yearly_data = {}
for t in ticker_list:
    closes = data_map[t]
    closes.index = pd.to_datetime(closes.index)
    # 연도별 첫날/마지막날 기준 수익률
    annual = closes.resample("YE").last().pct_change().dropna() * 100
    yearly_data[name_map[t]] = annual

if yearly_data:
    years = sorted(set().union(*[s.index.year for s in yearly_data.values()]))
    fig_yr = go.Figure()
    bar_width = max(0.1, 0.7 / len(ticker_list))
    for i, (nm, series) in enumerate(yearly_data.items()):
        color = COLORS[i % len(COLORS)]
        y_vals = [series[series.index.year == yr].iloc[0] if yr in series.index.year else None for yr in years]
        fig_yr.add_trace(go.Bar(
            name=nm, x=[str(y) for y in years], y=y_vals,
            marker_color=color,
            text=[f"{v:.1f}%" if v is not None else "" for v in y_vals],
            textposition="outside",
            textfont=dict(size=10, color="#1e293b"),
            hovertemplate=f"<b>{nm}</b><br>%{{x}}년: %{{y:.2f}}%<extra></extra>"
        ))
    fig_yr.update_layout(**CHART_LAYOUT, height=380, barmode="group")
    fig_yr.update_yaxes(ticksuffix="%", zeroline=True, zerolinecolor="#94a3b8")
    st.plotly_chart(fig_yr, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 월별 수익률 히트맵 (첫 번째 ETF) ──────────────
st.markdown("### 🗓️ 월별 수익률 히트맵")
st.caption("ETF별로 탭을 선택해 확인하세요")

tabs = st.tabs([name_map[t][:18] for t in ticker_list])
for tab, t in zip(tabs, ticker_list):
    with tab:
        closes = data_map[t].copy()
        closes.index = pd.to_datetime(closes.index)
        monthly = closes.resample("ME").last().pct_change().dropna() * 100
        monthly_df = pd.DataFrame({
            "year": monthly.index.year,
            "month": monthly.index.month,
            "ret": monthly.values
        })
        pivot = monthly_df.pivot(index="year", columns="month", values="ret")
        pivot = pivot.reindex(columns=range(1, 13))  # 없는 월은 NaN으로 채우기
        pivot.columns = ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"]

        # 연간 수익률 추가
        pivot["연간"] = pivot.sum(axis=1)

        text_vals = [[f"{v:.1f}%" if not pd.isna(v) else "" for v in row] for row in pivot.values]

        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=[str(y) for y in pivot.index],
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=11, color="black"),
            colorscale=[[0,"#1d4ed8"],[0.5,"#ffffff"],[1,"#dc2626"]],
            zmid=0,
            showscale=True,
            colorbar=dict(thickness=12, len=0.8, tickfont=dict(size=10)),
            hovertemplate="%{y}년 %{x}: %{z:.2f}%<extra></extra>"
        ))
        fig_hm.update_layout(
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ("xaxis","yaxis","hovermode","margin")},
            height=max(200, len(pivot) * 36 + 100),
            hovermode="closest",
            margin=dict(l=10, r=20, t=40, b=10),
        )
        fig_hm.update_xaxes(tickfont=dict(size=11, color="#1e293b"), side="top")
        fig_hm.update_yaxes(tickfont=dict(size=11, color="#1e293b"), autorange="reversed")
        st.plotly_chart(fig_hm, use_container_width=True)
        st.caption("파랑=손실 · 흰색=0% · 빨강=수익")

st.markdown("<br>", unsafe_allow_html=True)

# ── 롤링 변동성 ──────────────────────────────────
st.markdown("### 〰️ 롤링 변동성 (30일)")
st.caption("단기 변동성 추이 — 높을수록 위험 구간")

fig_rv = go.Figure()
for i, t in enumerate(ticker_list):
    rets = data_map[t].pct_change().dropna()
    rolling_vol = rets.rolling(30).std() * (252 ** 0.5) * 100
    color = COLORS[i % len(COLORS)]
    fig_rv.add_trace(go.Scatter(
        x=rolling_vol.index, y=rolling_vol.round(2),
        name=name_map[t], mode="lines",
        line=dict(color=color, width=2),
        hovertemplate=f"<b>{name_map[t]}</b>: %{{y:.1f}}%<extra></extra>"
    ))
fig_rv.update_layout(**CHART_LAYOUT, height=320)
fig_rv.update_yaxes(ticksuffix="%", title="연환산 변동성", title_font=dict(size=11))
st.plotly_chart(fig_rv, use_container_width=True)

st.markdown("---")
st.caption("⚠️ 본 자료는 참고용이며 투자 권유가 아닙니다. 데이터 출처: Yahoo Finance · KRX")
