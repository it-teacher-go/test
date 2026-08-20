import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 따뜻한 디자인 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="따뜻한 대한민국 기온 탐색기",
    page_icon="☀️",
    layout="wide"
)

# 따뜻하고 오가닉한 느낌의 CSS 스타일링
st.markdown("""
    <style>
    /* 전체 메인 배경색 */
    .main {
        background-color: #faf6f0;
    }
    /* 카드 지표(Metric) 스타일링 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.04);
        border: 1px solid #f0e6d2;
    }
    /* 안내 상자 커스텀 스타일 */
    .guide-box {
        background-color: #f7efe2;
        border-left: 5px solid #e76f51;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 이용방법 안내 섹션 (초보자용 가이드)
# -----------------------------------------------------------------------------
st.title("☀️ 우리 동네 1년 기온 변화 탐색기")
st.caption("가입 없이 이용 가능한 Open-Meteo 무료 API를 활용하여 대한민국 주요 도시의 기온 데이터를 시각화합니다.")

st.markdown("""
<div class="guide-box">
    <b>💡 초보자를 위한 이용 안내</b><br>
    1. <b>지역 선택</b>: 아래 드롭다운 메뉴에서 기온 흐름을 확인하고 싶은 도시를 선택해주세요.<br>
    2. <b>오늘의 기온 지표</b>: 상단 카드에서 선택한 지역의 오늘 최고/최저 기온과 평균 기온을 한눈에 볼 수 있습니다.<br>
    3. <b>월별 기온 추이 그래프</b>: 지난 1년간의 월별 평균 최고/최저 기온 변화를 꺾은선 그래프로 확인하세요. (그래프 위로 마우스를 올리면 상세 온도가 표시됩니다!)
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 주요 도시 위도/경도 데이터 정의
# -----------------------------------------------------------------------------
CITIES = {
    "서울특별시": {"lat": 37.5665, "lon": 126.9780},
    "부산광역시": {"lat": 35.1796, "lon": 129.0756},
    "대구광역시": {"lat": 35.8714, "lon": 128.6014},
    "인천광역시": {"lat": 37.4563, "lon": 126.7052},
    "광주광역시": {"lat": 35.1595, "lon": 126.8526},
    "대전광역시": {"lat": 36.3510, "lon": 127.3850},
    "울산광역시": {"lat": 35.5384, "lon": 129.3114},
    "제주특별자치도": {"lat": 33.4996, "lon": 126.5312},
    "강원도 (춘천)": {"lat": 37.8813, "lon": 127.7298}
}

# -----------------------------------------------------------------------------
# 4. 사용자 입력 (지역 선택)
# -----------------------------------------------------------------------------
selected_city = st.selectbox(
    "📍 조회할 지역을 선택해주세요",
    options=list(CITIES.keys()),
    index=0
)

# -----------------------------------------------------------------------------
# 5. Open-Meteo API 연동 및 데이터 불러오기 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)  # 1시간 동안 API 호출 결과 캐싱하여 빠른 실행 지원
def load_weather_data(lat, lon):
    """Open-Meteo Historical Weather API를 호출해 지난 1년간의 일별 최고/최저 기온을 받아오는 함수"""
    today = datetime.today().date()
    start_date = today - timedelta(days=365)
    
    # Open-Meteo Historical Weather API URL 구축
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={start_date}&end_date={today}&"
        f"daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean&"
        f"timezone=Asia%2FTokyo"
    )
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})
        df = pd.DataFrame({
            "date": pd.to_datetime(daily_data.get("time", [])),
            "temp_max": daily_data.get("temperature_2m_max", []),
            "temp_min": daily_data.get("temperature_2m_min", []),
            "temp_mean": daily_data.get("temperature_2m_mean", [])
        })
        return df
    else:
        return None

# -----------------------------------------------------------------------------
# 6. 데이터 연동 및 화면 출력
# -----------------------------------------------------------------------------
lat = CITIES[selected_city]["lat"]
lon = CITIES[selected_city]["lon"]

with st.spinner(f"'{selected_city}'의 지난 1년 날씨 데이터를 가져오는 중입니다... 🌿"):
    df_weather = load_weather_data(lat, lon)

if df_weather is not None and not df_weather.empty:
    # 가장 최근 날짜(오늘/어제) 데이터 추출
    latest_row = df_weather.iloc[-1]
    latest_date_str = latest_row["date"].strftime("%Y년 %m월 %d일")
    
    # --- [상단] 오늘(최근) 기온 지표 카드 ---
    st.markdown(f"### 🌡️ 최근 기온 현황 <small style='font-size: 14px; color: #888;'>({latest_date_str} 기준)</small>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="최고 기온",
            value=f"{latest_row['temp_max']:.1f} °C"
        )
    with col2:
        st.metric(
            label="최저 기온",
            value=f"{latest_row['temp_min']:.1f} °C"
        )
    with col3:
        st.metric(
            label="일평균 기온",
            value=f"{latest_row['temp_mean']:.1f} °C"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- [하단] 지난 1년 월별 기온 추이 Plotly 꺾은선 그래프 ---
    st.markdown("### 📊 최근 1년 월별 기온 추이")
    
    # 월별 그룹화 (년-월 기준으로 평균 계산)
    df_weather["year_month"] = df_weather["date"].dt.to_period("M").astype(str)
    monthly_df = df_weather.groupby("year_month")[["temp_max", "temp_min", "temp_mean"]].mean().reset_index()

    # Plotly 그래프 생성
    fig = go.Figure()

    # 월별 평균 최고 기온 선 (따뜻한 주황색)
    fig.add_trace(go.Scatter(
        x=monthly_df["year_month"],
        y=monthly_df["temp_max"],
        mode="lines+markers",
        name="월평균 최고기온",
        line=dict(color="#E76F51", width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>평균 최고기온: %{y:.1f} °C<extra></extra>"
    ))

    # 월별 평균 기온 선 (녹색/티일)
    fig.add_trace(go.Scatter(
        x=monthly_df["year_month"],
        y=monthly_df["temp_mean"],
        mode="lines+markers",
        name="월평균 기온",
        line=dict(color="#2A9D8F", width=2.5, dash="dash"),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>월평균 기온: %{y:.1f} °C<extra></extra>"
    ))

    # 월별 평균 최저 기온 선 (시원한 푸른색)
    fig.add_trace(go.Scatter(
        x=monthly_df["year_month"],
        y=monthly_df["temp_min"],
        mode="lines+markers",
        name="월평균 최저기온",
        line=dict(color="#457B9D", width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>평균 최저기온: %{y:.1f} °C<extra></extra>"
    ))

    # 레이아웃 스타일 설정
    fig.update_layout(
        title=dict(
            text=f"<b>[{selected_city}] 지난 1년간 월별 기온 변화</b>",
            font=dict(size=18, color="#264653")
        ),
        xaxis=dict(
            title="연월 (Year-Month)",
            showgrid=True,
            gridcolor="#f0e6d2"
        ),
        yaxis=dict(
            title="기온 (°C)",
            showgrid=True,
            gridcolor="#f0e6d2"
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("⚠️ 날씨 데이터를 가져오는 중에 문제가 발생했습니다. 잠시 후 다시 시도해주세요!")
