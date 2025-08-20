# streamlit run main.py
# -*- coding: utf-8 -*-
import streamlit as st
import re
from collections import defaultdict

# =====================================
# 기본 설정 & CSS
# =====================================
st.set_page_config(page_title="화학식 정보 사전", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
        body { 
            background: linear-gradient(to bottom, #e0f7ff 0%, #ffffff 100%);
            font-family: 'Arial', sans-serif;
        }
        .main-title {
            font-size: 42px; font-weight: bold; text-align: center; color: #1a237e; margin-bottom: 20px;
            text-shadow: 1px 1px 2px #90caf9;
        }
        .sub-title {
            font-size: 22px; font-weight: bold; color: #1565c0; margin-top: 20px; text-shadow: 1px 1px 1px #bbdefb;
        }
        .compound-box {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 14px;
            padding: 12px;
            margin: 6px 0;
            border: 2px solid #90caf9;
            font-size: 16px;
            color: #0d47a1;
            text-align: center;
            font-weight: 500;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            transition: 0.3s;
        }
        .compound-box:hover {
            background: rgba(144, 202, 249, 0.3);
            cursor: pointer;
        }
        .info-card {
            background: rgba(255,255,255,0.85);
            border: 2px solid #64b5f6;
            border-radius: 20px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 3px 3px 12px rgba(0,0,0,0.15);
            color: #0d1b2a;
        }
        .info-row {
            display: grid;
            grid-template-columns: 140px 1fr;
            padding: 6px 0;
            border-bottom: 1px solid #cfd8dc;
            align-items: center;
        }
        .info-label {
            font-weight: 600;
            color: #1e88e5;
            font-size: 16px;
        }
        .info-value {
            color: #0d1b2a;
            font-size: 15px;
        }
        .info-card .info-row:last-child {
            border-bottom: none;
        }
        input[type="text"] {
            border-radius: 12px;
            border: 2px solid #64b5f6;
            padding: 8px;
            width: 100%;
            font-size: 16px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧪🔬 실험실 화학식 정보 사전</div>', unsafe_allow_html=True)
st.write("H2O, CO2 같은 화학식이나 '물', '이산화탄소' 같은 한글 이름을 입력하면 정보를 알려줍니다.")

# =====================================
# 원자량 데이터
# =====================================
ATOMIC_DATA = {
    'H': (1.008, '수소'), 'C': (12.011, '탄소'), 'N': (14.007, '질소'), 'O': (15.999, '산소'),
    'Na': (22.990, '나트륨'), 'Mg': (24.305, '마그네슘'), 'Al': (26.982, '알루미늄'),
    'Si': (28.085, '규소'), 'P': (30.974, '인'), 'S': (32.06, '황'),
    'Cl': (35.45, '염소'), 'K': (39.098, '칼륨'), 'Ca': (40.078, '칼슘'),
    'Fe': (55.845, '철'), 'Cu': (63.546, '구리'), 'Zn': (65.38, '아연')
}

# =====================================
# 화학식 파서
# =====================================
TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+)")

def parse_formula(formula: str):
    tokens = TOKEN.findall(formula.replace(' ', ''))
    stack = [defaultdict(int)]
    i = 0
    def add(sym, n): stack[-1][sym] += n
    while i < len(tokens):
        t = tokens[i]
        if t == '(':
            stack.append(defaultdict(int)); i += 1
        elif t == ')':
            i += 1; mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            group = stack.pop()
            for k, v in group.items(): add(k, v * mult)
        elif t.isdigit():
            raise ValueError("숫자가 앞에 오는 표기는 지원하지 않습니다.")
        else:
            sym = t; i += 1; mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            add(sym, mult)
    if len(stack) != 1: raise ValueError("괄호 처리 오류")
    return dict(stack[0])

# =====================================
# 화합물 데이터베이스
# =====================================
COMPOUNDS = {
    "H2O": {"이름": "물", "상태(상온)": "액체", "종류": "산화물",
            "설명": "생명체에 필수적인 극성 용매로 많은 물질을 용해시킵니다.",
            "물리적 성질": "끓는점 100℃, 어는점 0℃, 밀도 1 g/cm³",
            "안전": "보통 안전하지만 전기와 함께 사용 시 감전 위험 있음."},
    "CO2": {"이름": "이산화탄소", "상태(상온)": "기체", "종류": "산화물",
            "설명": "호흡과 연소의 산물, 광합성에 사용되며 드라이아이스 형태로도 존재.",
            "물리적 성질": "무색 무취, 드라이아이스는 -78.5℃에서 승화",
            "안전": "고농도는 질식 위험. 환기 필요."},
    "NaCl": {"이름": "염화 나트륨(소금)", "상태(상온)": "고체", "종류": "이온결합 화합물",
             "설명": "바닷물과 암염의 주성분, 음식 조리에 사용.",
             "물리적 성질": "무색 결정, 녹는점 801℃",
             "안전": "과다 섭취는 건강에 해로움."},
    "NH3": {"이름": "암모니아", "상태(상온)": "기체", "종류": "염기성 화합물",
            "설명": "자극적인 냄새가 나는 기체, 비료와 세정제 제조에 사용.",
            "물리적 성질": "무색 자극성 기체, 끓는점 -33℃",
            "안전": "고농도는 호흡기 자극 및 위험."},
    "CH4": {"이름": "메테인", "상태(상온)": "기체", "종류": "탄화수소",
            "설명": "천연가스의 주성분, 연료로 사용.",
            "물리적 성질": "무색 무취 기체, 끓는점 -161℃",
            "안전": "가연성이 높음."},
    "C2H5OH": {"이름": "에탄올", "상태(상온)": "액체", "종류": "알코올",
               "설명": "알코올 음료의 성분, 소독제로도 사용.",
               "물리적 성질": "무색 액체, 끓는점 78℃",
               "안전": "섭취 시 알코올 중독 위험."},
    "H2SO4": {"이름": "황산", "상태(상온)": "액체", "종류": "산",
              "설명": "매우 강한 산, 비료와 화학 산업에서 광범위하게 사용.",
              "물리적 성질": "무색-갈색 점성 액체, 끓는점 337℃",
              "안전": "부식성이 매우 강해 화상 위험."},
    "HCl": {"이름": "염화수소(염산)", "상태(상온)": "기체(수용액은 염산)", "종류": "산",
            "설명": "강한 산성을 띠며 금속과 반응.",
            "물리적 성질": "무색 자극성 기체",
            "안전": "강산으로 부식성이 강함."},
    "CaCO3": {"이름": "탄산칼슘", "상태(상온)": "고체", "종류": "염",
              "설명": "석회석, 대리석, 조개껍질의 주성분.",
              "물리적 성질": "흰색 고체, 녹는점 825℃",
              "안전": "상대적으로 안전."},
    "NaHCO3": {"이름": "탄산수소나트륨(베이킹소다)", "상태(상온)": "고체", "종류": "염",
               "설명": "제과, 세정, 완충작용 등에 사용.",
               "물리적 성질": "흰색 결정성 분말",
               "안전": "대체로 안전."},
    "C6H12O6": {"이름": "포도당", "상태(상온)": "고체", "종류": "탄수화물",
                "설명": "생명체의 주요 에너지원으로 사용되는 단당류.",
                "물리적 성질": "흰색 결정성 분말, 녹는점 146℃",
                "안전": "대체로 안전."},
    "H2O2": {"이름": "과산화수소", "상태(상온)": "액체", "종류": "산화제",
             "설명": "강한 산화력으로 소독과 표백에 사용.",
             "물리적 성질": "무색 액체, 끓는점 150℃",
             "안전": "고농도는 피부 화상 및 폭발 위험."}
}

# =====================================
# 한글 이름 → 화학식 변환
# =====================================
NAME_TO_FORMULA = {
    "물": "H2O", "이산화탄소": "CO2", "소금": "NaCl", "염화나트륨": "NaCl",
    "암모니아": "NH3", "메테인": "CH4", "에탄올": "C2H5OH",
    "황산": "H2SO4", "염산": "HCl", "탄산칼슘": "CaCO3", "석회석": "CaCO3",
    "베이킹소다": "NaHCO3", "탄산수소나트륨": "NaHCO3", "포도당": "C6H12O6",
    "과산화수소": "H2O2"
}

# =====================================
# 지원 화합물 목록 (카드 스타일)
# =====================================
st.markdown('<div class="sub-title">📖 검색 가능한 화합물 목록</div>', unsafe_allow_html=True)
cols = st.columns(2)
half = len(COMPOUNDS) // 2 + len(COMPOUNDS) % 2
for i, (f, info) in enumerate(COMPOUNDS.items()):
    col = cols[0] if i < half else cols[1]
    col.markdown(f'<div class="compound-box">{info["이름"]} ({f})</div>', unsafe_allow_html=True)

# =====================================
# 검색 입력
# =====================================
user_input = st.text_input("🔎 화학식 또는 한글 이름을 입력하세요:")
if user_input:
    formula = NAME_TO_FORMULA.get(user_input.strip(), user_input.strip())
    if formula not in COMPOUNDS:
        st.error("해당 화합물은 데이터베이스에 없습니다.")
    else:
        info = COMPOUNDS[formula]

        # ----- 기본 정보 (아이콘 포함 카드) -----
        st.markdown('<div class="sub-title">기본 정보</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-row"><div class="info-label">🧪 이름</div><div class="info-value">{info['이름']} ({formula})</div></div>
                <div class="info-row"><div class="info-label">🌡️ 상태(상온)</div><div class="info-value">{info['상태(상온)']}</div></div>
                <div class="info-row"><div class="info-label">📂 종류</div><div class="info-value">{info['종류']}</div></div>
                <div class="info-row"><div class="info-label">📝 설명</div><div class="info-value">{info['설명']}</div></div>
                <div class="info-row"><div class="info-label">⚛️ 물리적 성질</div><div class="info-value">{info['물리적 성질']}</div></div>
                <div class="info-row"><div class="info-label">⚠ 안전</div><div class="info-value">{info['안전']}</div></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ----- 원소 조성 및 몰질량 -----
        try:
            comp = parse_formula(formula)
            st.markdown('<div class="sub-title">원소 조성 및 몰질량</div>', unsafe_allow_html=True)
            total_mass = 0.0
            rows = []
            for el, count in comp.items():
                if el in ATOMIC_DATA:
                    mass, kr = ATOMIC_DATA[el]
                    subtotal = mass * count
                    total_mass += subtotal
                    rows.append((f"{el} ({kr})", count, round(subtotal, 3)))
                else:
                    rows.append((f"{el} (데이터 없음)", count, None))
            st.table({"원소": [r[0] for r in rows], "개수": [r[1] for r in rows], "질량(g/mol)": [r[2] for r in rows]})
            st.success(f"총 몰질량: {total_mass:.3f} g/mol")
        except Exception as e:
            st.error(f"원소 분석 오류: {e}")
