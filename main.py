# streamlit run main.py 로 실행하세요
# -*- coding: utf-8 -*-
import streamlit as st
import math
import re
from collections import defaultdict

# =====================================
# 페이지 기본 설정 + CSS 테마
# =====================================
st.set_page_config(page_title="화학식 정보 사전", page_icon="🧪", layout="wide")

# CSS 스타일 추가
st.markdown("""
    <style>
    body {
        background-color: #f4f9fd;
    }
    .main-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #005f73;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-title {
        font-size: 1.3em;
        color: #0a9396;
        margin-top: 25px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .compound-box {
        background: #e9f5f7;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #94d2bd;
        margin-bottom: 15px;
    }
    .stTable {
        background: white;
        border-radius: 8px;
        padding: 8px;
    }
    .search-box {
        background: white;
        border: 2px solid #0a9396;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================
# 헤더
# =====================================
st.markdown('<div class="main-title">🧪 화학식 정보 사전 (고등학생용)</div>', unsafe_allow_html=True)
st.write("👉 H2O, CO2, NaCl 같은 화학식이나 '물', '이산화탄소', '소금' 같은 한글 이름을 입력하면 정보를 확인할 수 있습니다.")

# =====================================
# 원자량 데이터
# =====================================
ATOMIC_DATA = {
    'H': (1.008, '수소'), 'C': (12.011, '탄소'), 'N': (14.007, '질소'), 'O': (15.999, '산소'),
    'Na': (22.990, '나트륨'), 'Mg': (24.305, '마그네슘'), 'Al': (26.982, '알루미늄'), 'Si': (28.085, '규소'), 'P': (30.974, '인'),
    'S': (32.06, '황'), 'Cl': (35.45, '염소'), 'K': (39.098, '칼륨'), 'Ca': (40.078, '칼슘'), 'Fe': (55.845, '철'),
    'Cu': (63.546, '구리'), 'Zn': (65.38, '아연')
}

TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+)")

def parse_formula(formula: str):
    tokens = TOKEN.findall(formula.replace(' ', ''))
    stack = [defaultdict(int)]
    i = 0
    def add(sym, n):
        stack[-1][sym] += n
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
            sym = t; i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            add(sym, mult)
    if len(stack) != 1: raise ValueError("괄호 처리 오류")
    return dict(stack[0])

# =====================================
# 화합물 데이터
# =====================================
COMPOUNDS = {
    "H2O": {"이름": "물", "상태(상온)": "액체", "종류": "산화물", "설명": "생명체에 필수적인 극성 용매.", "물리적 성질": "끓는점 100℃, 어는점 0℃", "안전": "일반적으로 안전."},
    "CO2": {"이름": "이산화탄소", "상태(상온)": "기체", "종류": "산화물", "설명": "호흡과 연소의 산물.", "물리적 성질": "드라이아이스 -78.5℃ 승화", "안전": "고농도는 질식 위험."},
    "NaCl": {"이름": "염화나트륨(소금)", "상태(상온)": "고체", "종류": "이온결합 화합물", "설명": "음식 조리에 사용.", "물리적 성질": "녹는점 801℃", "안전": "과다 섭취 시 위험."},
    "NH3": {"이름": "암모니아", "상태(상온)": "기체", "종류": "염기성 화합물", "설명": "비료 제조에 사용.", "물리적 성질": "끓는점 -33℃", "안전": "호흡기 자극 위험."},
    "CH4": {"이름": "메테인", "상태(상온)": "기체", "종류": "탄화수소", "설명": "천연가스의 주성분.", "물리적 성질": "끓는점 -161℃", "안전": "가연성 높음."},
    "C2H5OH": {"이름": "에탄올", "상태(상온)": "액체", "종류": "알코올", "설명": "소독제 및 음료 성분.", "물리적 성질": "끓는점 78℃", "안전": "과음은 중독 위험."},
    "H2SO4": {"이름": "황산", "상태(상온)": "액체", "종류": "산", "설명": "강산, 비료·화학 산업에 사용.", "물리적 성질": "끓는점 337℃", "안전": "부식성 매우 강함."},
    "HCl": {"이름": "염화수소(염산)", "상태(상온)": "기체", "종류": "산", "설명": "강산으로 금속과 반응.", "물리적 성질": "자극성 기체", "안전": "부식성 강함."},
    "CaCO3": {"이름": "탄산칼슘", "상태(상온)": "고체", "종류": "염", "설명": "석회석, 조개껍질 성분.", "물리적 성질": "녹는점 825℃", "안전": "안전함."},
    "NaHCO3": {"이름": "탄산수소나트륨(베이킹소다)", "상태(상온)": "고체", "종류": "염", "설명": "제과, 세정에 사용.", "물리적 성질": "흰색 분말", "안전": "대체로 안전."},
    "H2O2": {"이름": "과산화수소", "상태(상온)": "액체", "종류": "산화제", "설명": "소독, 표백에 사용.", "물리적 성질": "끓는점 150℃", "안전": "고농도는 화상 위험."},
    "HNO3": {"이름": "질산", "상태(상온)": "액체", "종류": "산", "설명": "비료, 폭약 제조.", "물리적 성질": "끓는점 83℃", "안전": "부식·산화력 강함."},
    "NaOH": {"이름": "수산화나트륨(가성소다)", "상태(상온)": "고체", "종류": "염기", "설명": "비누·세제 제조.", "물리적 성질": "잘 녹음", "안전": "피부 화상 유발."},
    "C6H12O6": {"이름": "포도당", "상태(상온)": "고체", "종류": "탄수화물", "설명": "생명체의 주요 에너지원.", "물리적 성질": "물에 잘 녹음", "안전": "대체로 안전."},
    "CH3COOH": {"이름": "아세트산(식초)", "상태(상온)": "액체", "종류": "산(유기산)", "설명": "식초 성분, 화학 원료.", "물리적 성질": "끓는점 118℃", "안전": "고농도는 부식성."}
}

NAME_TO_FORMULA = {
    "물": "H2O", "이산화탄소": "CO2", "소금": "NaCl", "염화나트륨": "NaCl",
    "암모니아": "NH3", "메테인": "CH4", "에탄올": "C2H5OH",
    "황산": "H2SO4", "염산": "HCl", "탄산칼슘": "CaCO3", "석회석": "CaCO3",
    "베이킹소다": "NaHCO3", "탄산수소나트륨": "NaHCO3",
    "과산화수소": "H2O2", "질산": "HNO3", "수산화나트륨": "NaOH", "가성소다": "NaOH",
    "포도당": "C6H12O6", "아세트산": "CH3COOH", "식초": "CH3COOH"
}

# =====================================
# 지원되는 화합물 목록
# =====================================
st.markdown('<div class="sub-title">📖 검색 가능한 화합물 목록</div>', unsafe_allow_html=True)
cols = st.columns(2)
half = len(COMPOUNDS) // 2 + len(COMPOUNDS) % 2
for i, (f, info) in enumerate(COMPOUNDS.items()):
    col = cols[0] if i < half else cols[1]
    col.markdown(f"<div class='compound-box'><b>{info['이름']}</b> ({f})</div>", unsafe_allow_html=True)

# =====================================
# 검색 박스
# =====================================
st.markdown('<div class="sub-title">🔍 화합물 검색</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    user_input = st.text_input("화학식 또는 한글 이름을 입력하세요:")
    st.markdown('</div>', unsafe_allow_html=True)

if user_input:
    formula = NAME_TO_FORMULA.get(user_input, user_input)
    if formula not in COMPOUNDS:
        st.error("❌ 해당 화합물은 데이터베이스에 없습니다.")
    else:
        info = COMPOUNDS[formula]
        st.markdown('<div class="sub-title">📌 기본 정보</div>', unsafe_allow_html=True)
        st.write(f"**이름**: {info['이름']} ({formula})")
        st.write(f"**상태(상온)**: {info['상태(상온)']}")
        st.write(f"**종류**: {info['종류']}")
        st.write(f"**설명**: {info['설명']}")
        st.write(f"**물리적 성질**: {info['물리적 성질']}")
        st.write(f"**안전**: {info['안전']}")

        try:
            comp = parse_formula(formula)
            st.markdown('<div class="sub-title">⚛ 원소 조성 및 몰질량</div>', unsafe_allow_html=True)
            total_mass = 0; rows = []
            for el, count in comp.items():
                if el in ATOMIC_DATA:
                    mass, kr = ATOMIC_DATA[el]
                    subtotal = mass * count
                    total_mass += subtotal
                    rows.append((f"{el} ({kr})", count, subtotal))
            st.table({"원소": [r[0] for r in rows], "개수": [r[1] for r in rows], "질량(g/mol)": [r[2] for r in rows]})
            st.success(f"**총 몰질량**: {total_mass:.3f} g/mol")
        except Exception as e:
            st.error(f"원소 분석 오류: {e}")
