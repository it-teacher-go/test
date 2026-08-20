import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="따뜻한 주식 비교 탐색기",
    page_icon="📈",
    layout="wide"
)

# 따뜻하고 친근한 분위기를 위한 테마 스타일 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 배경색 느낌 부여 */
    .main {
        background-color: #faf6f0;
    }
    /* 카드 지표 배경 스타일 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #f0e6d2;
    }
    /* 라디오 버튼(기간 선택) 수평 정렬 간격 조정 */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 메인 타이틀 및 서비스 소개
# -----------------------------------------------------------------------------
st.title("📈 한눈에 보는 주식 비교 동향")
st.caption("관심 있는 종목 2개를 나란히 비교하고, 원하는 기간별 주가 추이와 주요 지표를 확인해보세요 🌿")
st.markdown("---")

# -----------------------------------------------------------------------------
# 3. 사용자 입력 (종목 코드 2개 및 기간 선택 버튼)
# -----------------------------------------------------------------------------
st.subheader("🔍 검색 설정")
col_input1, col_input2 = st.columns(2)

with col_input1:
    ticker_input1 = st.text_input(
        label="첫 번째 종목 코드",
        value="005930.KS",
        placeholder="예: 005930.KS (삼성전자)",
        help="한국 주식은 코드 뒤에 '.KS'(코스피) 또는 '.KQ'(코스닥)를 붙여주세요."
    )

with col_input2:
    ticker_input2 = st.text_input(
        label="두 번째 종목 코드 (선택)",
        value="000660.KS",
        placeholder="예: 000660.KS (SK하이닉스), AAPL (애플)",
        help="비교를 원치 않으시면 비워두셔도 됩니다."
    )

# 기간 선택 (라디오 버튼 형태)
period_option = st.radio(
    label="📅 조회 기간 선택",
    options=["1개월", "6개월", "1년", "5년"],
    index=2, # 기본값: 1년
    horizontal=True
)

# 선택한 기간에 따라 날짜 일수 계산
period_days_map = {
    "1개월": 30,
    "6개월": 180,
    "1년": 365,
    "5년": 1825
}
selected_days = period_days_map[period_option]

end_date = datetime.today()
start_date = end_date - timedelta(days=selected_days)

# -----------------------------------------------------------------------------
# 4. 데이터 불러오기 함수
# -----------------------------------------------------------------------------
def fetch_stock_data(symbol_text):
    """yfinance를 이용해 주가 데이터를 안전하게 불러오는 함수"""
    if not symbol_text.strip():
        return None, None, ""
    
    symbol = symbol_text.strip().upper()
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        if df.empty:
            return None, symbol, ""
        
        info = ticker.info
        currency = info.get('currency', '')
        currency_symbol = "₩" if currency == "KRW" else ("$" if currency == "USD" else currency)
        return df, symbol, currency_symbol
    except Exception as e:
        return None, symbol, ""

# -----------------------------------------------------------------------------
# 5. 데이터 처리 및 화면 출력
# -----------------------------------------------------------------------------
if ticker_input1:
    with st.spinner("주가 데이터를 불러오는 중입니다..."):
        df1, symbol1, curr1 = fetch_stock_data(ticker_input1)
        df2, symbol2, curr2 = fetch_stock_data(ticker_input2) if ticker_input2 else (None, None, "")

    if df1 is not None and not df1.empty:
        # --- [1] 상단 지표 카드 (현재가 & 등락률) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💡 현재가 및 등락률")
        
        metric_col1, metric_col2 = st.columns(2)
        
        # 종목 1 현황
        with metric_col1:
            st.markdown(f"**📌 {symbol1}**")
            c1, c2 = st.columns(2)
            curr_p1 = df1['Close'].iloc[-1]
            first_p1 = df1['Close'].iloc[0]
            change_p1 = curr_p1 - first_p1
            rate1 = (change_p1 / first_p1) * 100
            
            with c1:
                st.metric("현재가", f"{curr1} {curr_p1:,.2f}" if curr1 != "₩" else f"{curr1} {int(curr_p1):,}")
            with c2:
                st.metric(f"{period_option} 등락률", f"{rate1:+.2f}%", delta=f"{change_p1:+.2f} {curr1}")

        # 종목 2 현황 (입력 및 데이터가 존재하는 경우)
        if df2 is not None and not df2.empty:
            with metric_col2:
                st.markdown(f"**📌 {symbol2}**")
                c1, c2 = st.columns(2)
                curr_p2 = df2['Close'].iloc[-1]
                first_p2 = df2['Close'].iloc[0]
                change_p2 = curr_p2 - first_p2
                rate2 = (change_p2 / first_p2) * 100
                
                with c1:
                    st.metric("현재가", f"{curr2} {curr_p2:,.2f}" if curr2 != "₩" else f"{curr2} {int(curr_p2):,}")
                with c2:
                    st.metric(f"{period_option} 등락률", f"{rate2:+.2f}%", delta=f"{change_p2:+.2f} {curr2}")

        # --- [2] Plotly 주가 비교 그래프 ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"📊 {period_option} 주가 추이 비교")

        fig = go.Figure()

        # 첫 번째 종목 라인 추가 (코랄/주황)
        fig.add_trace(go.Scatter(
            x=df1.index,
            y=df1['Close'],
            mode='lines',
            name=symbol1,
            line=dict(color='#E76F51', width=2.5),
            hovertemplate=f'<b>{symbol1}</b><br>날짜: %{{x|%Y-%m-%d}}<br>종가: %{{y:,.2f}} {curr1}<extra></extra>'
        ))

        # 두 번째 종목 라인 추가 (청록)
        if df2 is not None and not df2.empty:
            fig.add_trace(go.Scatter(
                x=df2.index,
                y=df2['Close'],
                mode='lines',
                name=symbol2,
                line=dict(color='#2A9D8F', width=2.5),
                hovertemplate=f'<b>{symbol2}</b><br>날짜: %{{x|%Y-%m-%d}}<br>종가: %{{y:,.2f}} {curr2}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=f"<b>선택 기간 ({period_option}) 주가 흐름</b>", font=dict(size=18, color="#264653")),
            xaxis=dict(title="날짜", showgrid=True, gridcolor='#f0e6d2'),
            yaxis=dict(title="주가", showgrid=True, gridcolor='#f0e6d2'),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            hovermode="x unified",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- [3] 그래프 하단 상세 통계 카드 (최고가 · 최저가 · 평균가) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"📋 {period_option} 상세 요약 통계")

        stat_col1, stat_col2 = st.columns(2)

        # 종목 1 통화 포맷팅 지원 상세 카드
        with stat_col1:
            st.markdown(f"##### 🔹 {symbol1} 통계")
            s1_c1, s1_c2, s1_c3 = st.columns(3)
            high1, low1, avg1 = df1['High'].max(), df1['Low'].min(), df1['Close'].mean()
            
            s1_c1.metric("최고가", f"{curr1} {high1:,.2f}" if curr1 != "₩" else f"{curr1} {int(high1):,}")
            s1_c2.metric("최저가", f"{curr1} {low1:,.2f}" if curr1 != "₩" else f"{curr1} {int(low1):,}")
            s1_c3.metric("평균가", f"{curr1} {avg1:,.2f}" if curr1 != "₩" else f"{curr1} {int(avg1):,}")

        # 종목 2 상세 카드
        if df2 is not None and not df2.empty:
            with stat_col2:
                st.markdown(f"##### 🔸 {symbol2} 통계")
                s2_c1, s2_c2, s2_c3 = st.columns(3)
                high2, low2, avg2 = df2['High'].max(), df2['Low'].min(), df2['Close'].mean()
                
                s2_c1.metric("최고가", f"{curr2} {high2:,.2f}" if curr2 != "₩" else f"{curr2} {int(high2):,}")
                s2_c2.metric("최저가", f"{curr2} {low2:,.2f}" if curr2 != "₩" else f"{curr2} {int(low2):,}")
                s2_c3.metric("평균가", f"{curr2} {avg2:,.2f}" if curr2 != "₩" else f"{curr2} {int(avg2):,}")

    else:
        st.warning("⚠️ 입력하신 첫 번째 종목 코드의 데이터를 찾을 수 없습니다. 코드를 확인해주세요.")
