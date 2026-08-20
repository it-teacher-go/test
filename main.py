import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="따뜻한 주식 차트 탐색기",
    page_icon="📈",
    layout="wide"
)

# 따뜻하고 친근한 분위기를 위한 테마 스타일 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 배경색 및 기본 폰트 색상 느낌 부여 */
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
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 메인 타이틀 및 서비스 소개
# -----------------------------------------------------------------------------
st.title("📈 한눈에 보는 주식 동향")
st.caption("관심 있는 종목의 지난 1년간 주가 흐름과 주요 지표를 따뜻하고 간편하게 확인해보세요 🌿")
st.markdown("---")

# -----------------------------------------------------------------------------
# 3. 사용자 입력 (종목 코드 입력창)
# -----------------------------------------------------------------------------
# 기본값으로 삼성전자(005930.KS) 제공
ticker_input = st.text_input(
    label="🔍 궁금한 주식 종목 코드를 입력해주세요",
    value="005930.KS",
    placeholder="예: 005930.KS (삼성전자), AAPL (애플), TSLA (테슬라)",
    help="한국 주식은 코드 뒤에 '.KS'(코스피) 또는 '.KQ'(코스닥)를 붙여주세요."
)

# -----------------------------------------------------------------------------
# 4. 데이터 불러오기 및 계산 (yfinance 연동)
# -----------------------------------------------------------------------------
if ticker_input:
    # 종목 코드 양끝 공백 제거 및 대문자 변환
    symbol = ticker_input.strip().upper()
    
    # 1년 전 날짜 계산
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    # st.spinner를 사용해 로딩 상태 표시
    with st.spinner(f"'{symbol}' 종목의 데이터를 불러오는 중입니다..."):
        try:
            # yfinance를 통한 주가 데이터 수집
            ticker_data = yf.Ticker(symbol)
            df = ticker_data.history(start=start_date, end=end_date)
            
            # 종목 통화(Currency) 및 정보 가져오기
            info = ticker_data.info
            currency = info.get('currency', '')
            # 통화 기호 가독성 처리
            currency_symbol = "₩" if currency == "KRW" else ("$" if currency == "USD" else currency)

        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
            df = None

    # 데이터가 정상적으로 존재하는 경우 처리
    if df is not None and not df.empty:
        # 최근 종가(현재가) 및 1년 전 종가 추출
        current_price = df['Close'].iloc[-1]
        first_price = df['Close'].iloc[0]

        # 1년간 변동금액 및 등락률 계산
        price_change = current_price - first_price
        change_rate = (price_change / first_price) * 100

        # -----------------------------------------------------------------------------
        # 5. 핵심 지표 카드 (Metric) 표시
        # -----------------------------------------------------------------------------
        st.subheader("💡 주요 지표")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="현재가 (최근 종가)",
                value=f"{currency_symbol} {current_price:,.2f}" if currency != "KRW" else f"{currency_symbol} {int(current_price):,}"
            )

        with col2:
            st.metric(
                label="1년 등락율",
                value=f"{change_rate:+.2f}%",
                delta=f"{price_change:+.2f} {currency}",
                delta_color="normal" # 상승시 빨강/초록 지표
            )

        with col3:
            st.metric(
                label="1년 최고가",
                value=f"{currency_symbol} {df['High'].max():,.2f}" if currency != "KRW" else f"{currency_symbol} {int(df['High'].max()):,}"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # -----------------------------------------------------------------------------
        # 6. Plotly 꺾은선 그래프 그리기
        # -----------------------------------------------------------------------------
        st.subheader("📊 최근 1년 주가 추이")

        # Plotly 인터랙티브 그래프 생성
        fig = go.Figure()

        # 꺾은선(라인) 차트 추가
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='종가',
            line=dict(color='#E76F51', width=2.5), # 따뜻한 주황/코랄 톤 색상
            hovertemplate='<b>날짜</b>: %{x|%Y-%m-%d}<br><b>종가</b>: %{y:,.2f}<extra></extra>'
        ))

        # 차트 레이아웃 디자인 설정
        fig.update_layout(
            title=dict(
                text=f"<b>{symbol}</b> 주가 흐름",
                font=dict(size=18, color="#2A9D8F")
            ),
            xaxis=dict(
                title="날짜",
                showgrid=True,
                gridcolor='#f0e6d2'
            ),
            yaxis=dict(
                title=f"주가 ({currency_symbol})",
                showgrid=True,
                gridcolor='#f0e6d2'
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            hovermode="x unified",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Streamlit 화면에 Plotly 차트 출력
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ 입력하신 종목 코드의 데이터를 찾을 수 없습니다. 코드를 올바르게 입력했는지 확인해보세요!")
        st.info("💡 **팁**: 한국 주식은 코스피 `005930.KS`, 코스닥 `091990.KQ`처럼 뒤에 `.KS` 또는 `.KQ`를 붙여야 합니다.")
