import streamlit as st

st.set_page_config(page_title="생활 속 pH 게임", page_icon="🧪", layout="wide")

st.title("🖱 생활 속 pH 포인트 앤 클릭 게임")
st.write("물체를 클릭하면 해당 물질의 pH 정보를 확인할 수 있어요!")

# pH 데이터
ph_data = {
    "🍋 레몬": {"pH": "2~3 (강한 산성)", "설명": "레몬은 구연산이 들어 있어 강한 산성을 띱니다."},
    "🥤 탄산음료": {"pH": "3~4 (약산성)", "설명": "탄산가스와 첨가된 산 때문에 약산성입니다."},
    "🥛 우유": {"pH": "6~7 (중성 가까움)", "설명": "우유는 단백질과 젖산균 영향으로 약산성에 가깝습니다."},
    "🥚 달걀 흰자": {"pH": "8~9 (염기성)", "설명": "단백질 성분 때문에 염기성을 띱니다."},
    "🧴 세제": {"pH": "9~12 (강염기성)", "설명": "세제는 지방을 잘 녹이도록 강한 염기성을 띱니다."},
    "🌧 빗물": {"pH": "5~6 (약산성)", "설명": "대기 중 이산화탄소와 만나 약산성을 띱니다."},
    "🌊 바닷물": {"pH": "약 8 (약염기성)", "설명": "염분과 미네랄 영향으로 약염기성을 보입니다."},
}

# 2열 또는 3열로 배치 (게임 보드처럼 보이게)
cols = st.columns(3)

# 세션 상태로 클릭된 물체 저장
if "selected" not in st.session_state:
    st.session_state["selected"] = None

# 버튼으로 게임처럼
i = 0
for item in ph_data.keys():
    with cols[i % 3]:  # 3열 배치
        if st.button(item, use_container_width=True):
            st.session_state["selected"] = item
    i += 1

# 선택된 결과 보여주기
if st.session_state["selected"]:
    choice = st.session_state["selected"]
    info = ph_data[choice]
    st.markdown("---")
    st.subheader(f"🔎 {choice}")
    st.write(f"**pH 범위:** {info['pH']}")
    st.info(info["설명"])
