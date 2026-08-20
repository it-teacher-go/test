import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="1세대 포켓몬 151마리 성향 분석기",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ 1세대 포켓몬(151마리) 자동 성향 분석기")
st.caption("PokeAPI의 능력치(스탯) 데이터를 파이썬 알고리즘으로 자동 분석하여 151마리 포켓몬 중 내 성향과 가장 닮은 Top 5를 찾습니다.")

# -----------------------------------------------------------------------------
# 2. 이용 안내 상자
# -----------------------------------------------------------------------------
st.markdown("""
<div style="background-color: #f7efe2; border-left: 5px solid #e76f51; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <b>💡 능력치 기반 자동 성향 부여 알고리즘</b><br>
    PokeAPI에서 가져온 포켓몬의 스탯을 기반으로 성향(E/I, N/S) 점수를 자동 계산합니다!<br>
    - <b>스피드 / 공격력</b>이 높을수록 👉 <b>외향적(E)</b> 성향 증가<br>
    - <b>특수공격 / 특수방어</b>가 높을수록 👉 <b>직관적(N)</b> 성향 증가<br>
    사이드바에서 본인의 성향 비중(%)을 조절하여 151마리 전체 포켓몬 중 나와 가장 닮은 포켓몬을 찾아보세요.
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 1세대 포켓몬 한국어 이름 데이터 (1~151번)
# -----------------------------------------------------------------------------
KOREAN_NAMES = {
    1: "이상해씨", 2: "이상해풀", 3: "이상해꽃", 4: "파이리", 5: "리자드", 6: "리자몽",
    7: "꼬북이", 8: "어니부기", 9: "거북왕", 10: "캐터피", 11: "단데기", 12: "버터플",
    13: "뿔충이", 14: "딱충이", 15: "독침붕", 16: "구구", 17: "피죤", 18: "피죤투",
    19: "꼬렛", 20: "레트라", 21: "깨비참", 22: "깨비드릴조", 23: "아보", 24: "아보크",
    25: "피카츄", 26: "라이츄", 27: "모래두지", 28: "고지", 29: "니드런♀", 30: "니드리나",
    31: "니드퀸", 32: "니드런♂", 33: "니드리노", 34: "니드킹", 35: "삐삐", 36: "픽시",
    37: "식식이", 38: "나인테일", 39: "푸린", 40: "모구리", 41: "주뱃", 42: "골뱃",
    43: "뚜벅쵸", 44: "냄새꼬", 45: "라플레시아", 46: "파라스", 47: "파라섹트", 48: "콘팡",
    49: "도나리", 50: "디그다", 51: "닥트리오", 52: "나옹", 53: "페르시온", 54: "고라파덕",
    55: "골덕", 56: "망키", 57: "성원숭", 58: "가디", 59: "윈디", 60: "발챙이",
    61: "수륙챙이", 62: "강챙이", 63: "캐시", 64: "윤겔라", 65: "후딘", 66: "알통몬",
    67: "근육몬", 68: "괴력몬", 69: "모다피", 70: "우츠동", 71: "우츠보트", 72: "왕눈해",
    73: "독파리", 74: "꼬마돌", 75: "데구리", 76: "딱구리", 77: "포니타", 78: "날씽마",
    79: "야돈", 80: "야도란", 81: "코일", 82: "레어코일", 83: "파오리", 84: "두두",
    85: "두트리오", 86: "쥬쥬", 87: "쥬레곤", 88: "질퍽이", 89: "질뻐기", 90: "셀러",
    91: "파르셀", 92: "고스", 93: "고스트", 94: "팬텀", 95: "롱스톤", 96: "슬프기",
    97: "슬리퍼", 98: "크랩", 99: "킹크랩", 100: "찌리리공", 101: "붐볼", 102: "아라리",
    103: "나시", 104: "탕구리", 105: "텅구리", 106: "시라소몬", 107: "홍수몬", 108: "내루미",
    109: "또가스", 110: "또도가스", 111: "뿔카노", 112: "코뿔소", 113: "럭키", 114: "덩쿠리",
    115: "캥카", 116: "쏘드라", 117: "시드라", 118: "콘치", 119: "왕콘치", 120: "별가사리",
    121: "아쿠스타", 122: "마임맨", 123: "스컬지", 124: "루주라", 125: "에레브", 126: "마그마",
    127: "쁘사이저", 128: "켄타로스", 129: "잉어킹", 130: "갸라도스", 131: "라프라스", 132: "메타몽",
    133: "이브이", 134: "샤미드", 135: "쥬피썬더", 136: "부스터", 137: "폴리곤", 138: "암나이트",
    139: "암스타", 140: "투구", 141: "투구푸스", 142: "프테라", 143: "잠만보", 144: "프리져",
    145: "썬더", 146: "파이어", 147: "미뇽", 148: "신룡", 149: "망나뇽", 150: "뮤츠", 151: "뮤"
}

# -----------------------------------------------------------------------------
# 4. PokeAPI 연동 및 스탯 기반 성향 자동 계산 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=86400)  # 하루 동안 캐싱하여 빠른 로드 지원
def load_all_pokemon_data():
    """1세대 151마리의 스탯을 가져와 E/N 성향 점수를 자동 계산합니다."""
    pokemon_list = []
    
    # 151마리 데이터 순회
    for poke_id in range(1, 152):
        url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
            
            hp = stats.get("hp", 50)
            attack = stats.get("attack", 50)
            defense = stats.get("defense", 50)
            sp_atk = stats.get("special-attack", 50)
            sp_def = stats.get("special-defense", 50)
            speed = stats.get("speed", 50)
            
            # --- 능력치 기반 자동 성향 계산 알고리즘 ---
            # 1) 외향성(E) 점수: 스피드와 공격력이 높을수록 외향적 (0~100 정규화)
            raw_e = (speed * 0.6) + (attack * 0.4)
            e_weight = min(100, max(0, int((raw_e / 130) * 100)))
            
            # 2) 직관성(N) 점수: 특수공격과 특수방어가 높을수록 직관/전략적 (0~100 정규화)
            raw_n = (sp_atk * 0.6) + (sp_def * 0.4)
            n_weight = min(100, max(0, int((raw_n / 130) * 100)))
            
            # MBTI 문자열 생성
            mbti_e = "E" if e_weight >= 50 else "I"
            mbti_n = "N" if n_weight >= 50 else "S"
            mbti_type = f"{mbti_e}{mbti_n}XX"
            
            # 고화질 이미지 URL
            img_url = data["sprites"]["other"]["official-artwork"]["front_default"]
            if not img_url:
                img_url = data["sprites"]["front_default"]
                
            k_name = KOREAN_NAMES.get(poke_id, f"포켓몬 #{poke_id}")
            
            pokemon_list.append({
                "id": poke_id,
                "k_name": k_name,
                "mbti": mbti_type,
                "e_weight": e_weight,
                "n_weight": n_weight,
                "img_url": img_url,
                "hp": hp,
                "attack": attack,
                "defense": defense,
                "sp_attack": sp_atk,
                "sp_defense": sp_def,
                "speed": speed
            })
    return pokemon_list

# -----------------------------------------------------------------------------
# 5. 사이드바 - 성향 입력 슬라이더
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 내 성향 설정 (MBTI 비중)")

user_e = st.sidebar.slider("외향성 (E) 비중 (%)", 0, 100, 70, help="높을수록 스피드/공격력이 높은 외향적 포켓몬과 매칭됩니다.")
user_n = st.sidebar.slider("직관성 (N) 비중 (%)", 0, 100, 80, help="높을수록 특수공격/특수방어가 높은 전략적 포켓몬과 매칭됩니다.")

if st.sidebar.button("🔄 성향 다시 고르기"):
    st.rerun()

# -----------------------------------------------------------------------------
# 6. 데이터 로딩 및 실시간 매칭
# -----------------------------------------------------------------------------
with st.spinner("1세대 포켓몬 151마리의 능력을 불러오고 분석하는 중입니다... ⚡"):
    all_pokemons = load_all_pokemon_data()

calculated_list = []
for p in all_pokemons:
    # 유사도 거리 계산 (유클리드 거리)
    dist = ((p["e_weight"] - user_e) ** 2 + (p["n_weight"] - user_n) ** 2) ** 0.5
    calculated_list.append({**p, "distance": dist})

# 거리순 정렬 후 Top 5 선정
df_results = pd.DataFrame(calculated_list).sort_values("distance").head(5).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 7. 화면 출력
# -----------------------------------------------------------------------------
if not df_results.empty:
    top1 = df_results.iloc[0]

    st.markdown(f"### 🏆 151마리 중 1위 매칭: **{top1['k_name']}** (추정 성향: {top1['mbti']})")

    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image(top1["img_url"], caption=f"도감 번호: #{top1['id']} {top1['k_name']}", width=230)
    with col_info:
        st.subheader(f"✨ {top1['k_name']}와(과) 닮은 이유 (능력치 분석)")
        st.write(
            f"• **스피드 ({top1['speed']}) / 공격력 ({top1['attack']})** 기반 계산된 외향성(E) 점수: **{top1['e_weight']}점**\n"
            f"• **특수공격 ({top1['sp_attack']}) / 특수방어 ({top1['sp_defense']})** 기반 계산된 직관성(N) 점수: **{top1['n_weight']}점**\n"
            f"• 입력하신 성향(E: {user_e}%, N: {user_n}%)과 가장 유사한 스탯 분포를 보여줍니다."
        )
        st.metric(label="성향 일치도", value=f"{max(0, int(100 - top1['distance'] * 0.7))}%")

    st.markdown("---")

    # Top 5 레이더 차트
    st.markdown("### 📊 Top 5 포켓몬 능력치 비교 (Plotly 레이더 차트)")

    categories = ['체력(HP)', '공격력', '방어력', '특수공격', '특수방어', '스피드']
    fig = go.Figure()

    colors = ["#E76F51", "#2A9D8F", "#457B9D", "#F4A261", "#E9C46A"]

    for idx, row in df_results.iterrows():
        stats_values = [
            row["hp"], row["attack"], row["defense"],
            row["sp_attack"], row["sp_defense"], row["speed"]
        ]
        stats_values.append(stats_values[0])
        cat_closed = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=stats_values,
            theta=cat_closed,
            fill='toself' if idx == 0 else 'none',
            name=f"{idx+1}위: {row['k_name']} (#{row['id']})",
            line=dict(color=colors[idx % len(colors)], width=3 if idx == 0 else 1.5)
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 160])),
        showlegend=True,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=40, r=40, t=30, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 하단 Top 5 카드
    st.markdown("### 🐾 매칭된 Top 5 전체 보기")
    cols = st.columns(5)
    for idx, row in df_results.iterrows():
        with cols[idx]:
            st.markdown(f"**{idx+1}위. {row['k_name']}**")
            st.image(row["img_url"], use_container_width=True)
            st.caption(f"외향성(E): {row['e_weight']}점")
            st.caption(f"직관성(N): {row['n_weight']}점")
