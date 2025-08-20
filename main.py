# streamlit run app.py 로 실행하세요
# -*- coding: utf-8 -*-
import streamlit as st
import math
import re
from collections import defaultdict

# =====================================
# 기본 설정
# =====================================
st.set_page_config(page_title="화학식 정보 사전", page_icon="🧪")
st.title("🧪 화학식 정보 사전 (고등학생용)")
st.write("예: H2O, CO2, NaCl 같은 화학식이나 '물', '이산화탄소', '소금' 같은 한글 이름을 입력하면 정보를 보여줍니다.")

# =====================================
# 원자량 데이터 + 한국어 이름
# =====================================
ATOMIC_DATA = {
    'H': (1.008, '수소'), 'C': (12.011, '탄소'), 'N': (14.007, '질소'), 'O': (15.999, '산소'),
    'Na': (22.990, '나트륨'), 'Mg': (24.305, '마그네슘'), 'Al': (26.982, '알루미늄'), 'Si': (28.085, '규소'), 'P': (30.974, '인'),
    'S': (32.06, '황'), 'Cl': (35.45, '염소'), 'K': (39.098, '칼륨'), 'Ca': (40.078, '칼슘'), 'Fe': (55.845, '철'),
    'Cu': (63.546, '구리'), 'Zn': (65.38, '아연')
}

# =====================================
# 간단 화학식 파서
# =====================================
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
            stack.append(defaultdict(int))
            i += 1
        elif t == ')':
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            group = stack.pop()
            for k, v in group.items():
                add(k, v * mult)
        elif t.isdigit():
            raise ValueError("숫자가 앞에 오는 표기는 지원하지 않습니다.")
        else:
            sym = t; i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            add(sym, mult)
    if len(stack) != 1:
        raise ValueError("괄호 처리 오류")
    return dict(stack[0])

# =====================================
# 내장 화합물 정보 (상세)
# =====================================
COMPOUNDS = {
    "H2O": {
        "이름": "물",
        "상태(상온)": "액체",
        "종류": "산화물",
        "설명": "지구에서 가장 풍부한 물질 중 하나로, 생명체에 필수적입니다. 극성 용매로서 많은 물질을 용해시킬 수 있어 화학 반응의 매개체 역할을 합니다.",
        "물리적 성질": "끓는점 100℃(1atm), 어는점 0℃, 밀도 약 1 g/cm³",
        "안전": "일반적으로 안전하나, 전기와 함께 사용할 경우 감전 위험이 있습니다."
    },
    "CO2": {
        "이름": "이산화탄소",
        "상태(상온)": "기체",
        "종류": "산화물",
        "설명": "호흡과 연소의 산물이며, 대기 중 약 0.04% 존재합니다. 광합성에 사용되고, 드라이아이스 형태로도 존재합니다.",
        "물리적 성질": "무색, 무취의 기체. 드라이아이스는 -78.5℃에서 승화.",
        "안전": "고농도에서는 질식 위험이 있으며, 밀폐된 공간에서는 환기가 필요합니다."
    },
    "NaCl": {
        "이름": "염화 나트륨(소금)",
        "상태(상온)": "고체",
        "종류": "이온결합 화합물",
        "설명": "바닷물과 암염의 주성분이며, 음식 조리에 널리 사용됩니다.",
        "물리적 성질": "무색 결정. 녹는점 801℃, 끓는점 1413℃.",
        "안전": "보통 안전하나, 과다 섭취는 건강에 해롭습니다."
    }
}

# 한글 이름 → 화학식 매핑
NAME_TO_FORMULA = {
    "물": "H2O",
    "이산화탄소": "CO2",
    "소금": "NaCl",
    "염화나트륨": "NaCl"
}

# =====================================
# 계산 함수
# =====================================

def molar_mass(comp: dict):
    m = 0.0
    for el, n in comp.items():
        if el not in ATOMIC_DATA:
            raise KeyError(f"원자량 데이터 없음: {el}")
        m += ATOMIC_DATA[el][0] * n
    return m

# =====================================
# 입력 영역
# =====================================
user_input = st.text_input("화학식 또는 한글 이름 입력", value="H2O", help="예: H2O, CO2, NaCl 또는 물, 이산화탄소, 소금")

if user_input:
    formula = user_input.strip()
    # 한글 이름이면 화학식으로 변환
    if formula in NAME_TO_FORMULA:
        formula = NAME_TO_FORMULA[formula]
        st.info(f"입력한 '{user_input}' 은(는) '{formula}' 화학식으로 변환되었습니다.")

    try:
        comp = parse_formula(formula)
        M = molar_mass(comp)

        key_like = formula.replace(' ', '')
        info = COMPOUNDS.get(key_like)

        st.subheader("기본 정보")
        if info:
            st.write(f"**이름:** {info['이름']}")
            st.write(f"**종류:** {info['종류']} | **상태(상온):** {info['상태(상온)']}")
            st.write(f"**설명:** {info['설명']}")
            st.write(f"**물리적 성질:** {info['물리적 성질']}")
            st.write(f"**안전:** {info['안전']}")
        else:
            st.info("내장 사전에 없는 화합물입니다. 아래 계산 정보만 제공합니다.")

        st.subheader("조성 및 몰질량")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**원소별 개수 (한국어 이름 포함)**")
            rows = []
            for el, n in comp.items():
                name_kr = ATOMIC_DATA[el][1] if el in ATOMIC_DATA else "(알 수 없음)"
                rows.append((el, name_kr, n))
            st.table({"원소 기호": [r[0] for r in rows], "한글 이름": [r[1] for r in rows], "개수": [r[2] for r in rows]})
        with col2:
            st.metric("몰질량 (g/mol)", f"{M:.3f}")

        st.markdown("**질량 백분율(%)**")
        rows = []
        for el, n in comp.items():
            part = ATOMIC_DATA[el][0] * n
            pct = part / M * 100
            rows.append((el, ATOMIC_DATA[el][1], round(pct, 3)))
        st.table({"원소 기호": [r[0] for r in rows], "한글 이름": [r[1] for r in rows], "질량%": [r[2] for r in rows]})

    except Exception as e:
        st.error(f"해석/계산 오류: {e}")

st.divider()
st.caption("※ 교육용 간이 도구입니다. 정확한 수치/안전 정보는 교과서와 공인 자료를 확인하세요.")
