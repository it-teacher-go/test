import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="나와 닮은 포켓몬 찾기",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ 나의 성향 맞춤 포켓몬 Top 5 분석기")
st.caption("가입 없이 사용 가능한 PokeAPI와 Plotly를 활용해 내 성향과 가장 잘 어울리는 포켓몬을 찾고 비교합니다.")

# -----------------------------------------------------------------------------
# 2. 이용 안내 상자
# -----------------------------------------------------------------------------
st.markdown("""
<div style="background-color: #f7efe2; border-left: 5px solid #e76f51; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <b>💡 이용 안내</b><br>
    1. 왼쪽 사이드바에서 본인의 <b>MBTI 성향 비중(%)</b>을 슬라이더로 조절하세요.<br>
    2. 성향에 따라 <b>PokeAPI</b>에서 데이터를 계산하여 가장 어울리는 <b>Top 5 포켓몬</b>을 실시간으로 분석합니다.<br>
    3. 선택된 포켓몬의 <b>능력치 레이더 차트, 이미지, 어울리는 이유, 궁합</b>을 한눈에 확인하세요!
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 대표 포켓몬 12마리 정의 (PokeAPI ID 및 성향 가중치 사전 정의)
# -----------------------------------------------------------------------------
POKEMON_DB = [
    {"id": 25, "k_name": "피카츄", "mbti": "ENFP", "e_weight": 85, "n_weight": 80, "desc": "에너지 넘치고 호기심이 풍부하여 어디서든 인기가 많습니다. 새로운 아이디어를 떠올리는 데 탁월합니다.", "match": "INTJ (뮤츠)"},
    {"id": 4, "k_name": "파이리", "mbti": "ESTP", "e_weight": 80, "n_weight": 40, "desc": "열정적이고 모험을 두려워하지 않는 행동파입니다. 일단 도전하고 보는 강한 추진력을 갖고 있습니다.", "match": "ISFJ (꼬북이)"},
    {"id": 7, "k_name": "꼬북이", "mbti": "ISFP", "e_weight": 35, "n_weight": 30, "desc": "온화하고 마이페이스를 유지하며 주변 사람들을 묵묵히 챙깁니다. 여유로운 매력이 특징입니다.", "match": "ESTJ (괴력몬)"},
    {"id": 1, "k_name": "이상해씨", "mbti": "INFJ", "e_weight": 30, "n_weight": 85, "desc": "조용하지만 깊은 생각과 강한 신념을 가지고 있습니다. 타인의 감정을 잘 이해하고 배려합니다.", "match": "ENTP (팬텀)"},
    {"id": 143, "k_name": "잠만보", "mbti": "INFP", "e_weight": 20, "n_weight": 70, "desc": "평화롭고 상상력이 풍부하며 자신만의 풍부한 내면 세계를 가지고 있습니다. 느긋함 속에 강함이 숨어있습니다.", "match": "ENFJ (토게피)"},
    {"id": 150, "k_name": "뮤츠", "mbti": "INTJ", "e_weight": 15, "n_weight": 95, "desc": "냉철한 분석력과 완벽주의적 성향을 지닌 전략가입니다. 목표를 정하면 철저하게 달성해냅니다.", "match": "ENFP (피카츄)"},
    {"id": 39, "k_name": "푸린", "mbti": "ESFP", "e_weight": 90, "n_weight": 35, "desc": "사람들의 시선을 즐기며 사교성이 뛰어납니다. 감정 표현이 솔직하고 분위기를 밝게 만드는 에너지원입니다.", "match": "ISTJ (암나이트)"},
    {"id": 68, "k_name": "괴력몬", "mbti": "ESTJ", "e_weight": 85, "n_weight": 20, "desc": "체계적이고 원칙을 중시하는 리더 타입입니다. 강한 책임감으로 목표를 향해 끝까지 밀어붙입니다.", "match": "ISFP (꼬북이)"},
    {"id": 94, "k_name": "팬텀", "mbti": "ENTP", "e_weight": 88, "n_weight": 88, "desc": "재치 있고 독창적인 장난꾸러기입니다. 기존의 틀을 깨는 새로운 시도를 즐기는 창의적 인재입니다.", "match": "INFJ (이상해씨)"},
    {"id": 133, "k_name": "이브이", "mbti": "ENFJ", "e_weight": 75, "n_weight": 75, "desc": "다양한 가능성을 지니고 있으며 타인을 잘 이끄는 매력적인 존재입니다. 적응력이 뛰어나고 친근합니다.", "match": "INTP (고라파덕)"},
    {"id": 54, "k_name": "고라파덕", "mbti": "INTP", "e_weight": 25, "n_weight": 90, "desc": "호기심이 많고 깊은 생각에 잘 빠져듭니다. 독특한 관점으로 문제를 해결하는 잠재력을 가졌습니다.", "match": "ENFJ (이브이)"},
    {"id": 175, "k_name": "토게피", "mbti": "ESFJ", "e_weight": 80, "n_weight": 50, "desc": "주변에 행복과 온기를 전하는 긍정 아이콘입니다. 협동심이 강하고 관계를 대단히 중요시합니다.", "match": "INFP (잠만보)"}
]

# -----------------------------------------------------------------------------
# 4. PokeAPI 연동 함수 (포켓몬 이미지 및 능력치를 실시간 수집)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_pokemon_api_data(poke_id):
    """PokeAPI를 호출하여 포켓몬의 스탯 및 공식 고화질 이미지 URL을 가져옵니다."""
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # 공식 일러스트 이미지 추출
        img_url = data["sprites"]["other"]["official-artwork"]["front_default"]
        if not img_url:
            img_url = data["sprites"]["front_default"]
            
        # 6대 능력치 파싱
        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        
        return {
            "img_url": img_url,
            "hp": stats.get("hp", 50),
            "attack": stats.get("attack", 50),
            "defense": stats.get("defense", 50),
            "sp_attack": stats.get("special-attack", 50),
            "sp_defense": stats.get("special-defense", 50),
            "speed": stats.get("speed", 50)
        }
    return None

# -----------------------------------------------------------------------------
# 5. 사이드바 - 성향 입력 슬라이더
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 내 성향 설정 (MBTI 비중)")

user_e = st.sidebar.slider("외향성 (E) 비중 (%)", 0, 100, 70, help="높을수록 외향적(E), 낮을수록 내향적(I)")
user_n = st.sidebar.slider("직관성 (N) 비중 (%)", 0, 100, 80, help="높을수록 직관적(N), 낮을수록 감각적(S)")

# 다시 고르기 (초기화) 버튼
if st.sidebar.button("🔄 성향 다시 고르기"):
    st.rerun()

# -----------------------------------------------------------------------------
# 6. 사용자 성향 기반 Top 5 포켓몬 실시간 계산 로직
# -----------------------------------------------------------------------------
calculated_list = []
for p in POKEMON_DB:
    # 유사도 거리를 계산합니다. (입력값과의 수치 차이가 적을수록 유사)
    distance = ((p["e_weight"] - user_e) ** 2 + (p["n_weight"] - user_n) ** 2) ** 0.5
    
    # PokeAPI 데이터 호출
    api_data = fetch_pokemon_api_data(p["id"])
    if api_data:
        combined_info = {**p, **api_data, "distance": distance}
        calculated_list.append(combined_info)

# 일치도가 높은(거리가 짧은) 순서로 정렬 후 Top 5 선출
df_results = pd.DataFrame(calculated_list).sort_values("distance").head(5).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 7. 화면 출력 - 1위 포켓몬 프로필 및 Top 5 레이더 차트
# -----------------------------------------------------------------------------
if not df_results.empty:
    top1 = df_results.iloc[0]

    st.markdown(f"### 🏆 당신과 가장 어울리는 1위 포켓몬: **{top1['k_name']}** ({top1['mbti']})")

    # 상단 1위 포켓몬 이미지, 어울리는 이유, 궁합 출력
    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image(top1["img_url"], caption=f"ID: #{top1['id']} {top1['k_name']}", width=250)
    with col_info:
        st.subheader(f"✨ {top1['k_name']}와(과) 잘 어울리는 이유")
        st.write(top1["desc"])
        st.markdown(f"**❤️ 최고의 궁합(잘 맞는 유형):** `{top1['match']}`")
        st.metric(label="성향 일치도", value=f"{max(0, int(100 - top1['distance'] * 0.7))}%")

    st.markdown("---")

    # Top 5 레이더 차트 시각화 (Plotly)
    st.markdown("### 📊 Top 5 포켓몬 능력치 비교 (Plotly 레이더 차트)")

    categories = ['체력(HP)', '공격력', '방어력', '특수공격', '특수방어', '스피드']
    fig = go.Figure()

    colors = ["#E76F51", "#2A9D8F", "#457B9D", "#F4A261", "#E9C46A"]

    for idx, row in df_results.iterrows():
        stats_values = [
            row["hp"], row["attack"], row["defense"],
            row["sp_attack"], row["sp_defense"], row["speed"]
        ]
        # 방사형 연결을 위해 첫 번째 값을 끝에 추가
        stats_values.append(stats_values[0])
        cat_closed = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=stats_values,
            theta=cat_closed,
            fill='toself' if idx == 0 else 'none',  # 1위만 색 채우기
            name=f"{idx+1}위: {row['k_name']} ({row['mbti']})",
            line=dict(color=colors[idx % len(colors)], width=3 if idx == 0 else 1.5)
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 140])
        ),
        showlegend=True,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=40, r=40, t=30, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 하단 Top 5 전체 요약 카드 리스트
    st.markdown("### 🐾 매칭된 Top 5 포켓몬 전체 보기")
    cols = st.columns(5)
    for idx, row in df_results.iterrows():
        with cols[idx]:
            st.markdown(f"**{idx+1}위. {row['k_name']}**")
            st.image(row["img_url"], use_container_width=True)
            st.caption(f"MBTI: {row['mbti']}")
            st.caption(f"궁합: {row['match']}")
