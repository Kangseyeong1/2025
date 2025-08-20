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
st.write("예: H2O, CO2, NaCl 같은 화학식의 기본 정보를 보여주고, 몰질량과 구성비를 계산합니다.")

# =====================================
# 최소 원자량 데이터 (교육용 반올림)
# 필요한 원소만 간단히 수록
# =====================================
ATOMIC_MASS = {
    'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974,
    'S': 32.06, 'Cl': 35.45, 'K': 39.098, 'Ca': 40.078, 'Fe': 55.845,
    'Cu': 63.546, 'Zn': 65.38
}

# =====================================
# 간단 화학식 파서 (괄호 소규모 지원)
# 예: H2O, CO2, Ca(OH)2
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
            # 숫자가 먼저 나오는 복잡한 경우는 고등학교 수준에서 제외
            # (예: 5H2O 같은 표기는 이 앱에서 지원하지 않음)
            raise ValueError("숫자가 앞에 오는 표기는 지원하지 않습니다.")
        else:
            # 원소 심볼
            sym = t; i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            add(sym, mult)
    if len(stack) != 1:
        raise ValueError("괄호 처리 오류")
    return dict(stack[0])

# =====================================
# 내장 화합물 정보 (간단 설명)
# =====================================
COMPOUNDS = {
    "H2O": {
        "이름": "물",
        "상태(상온)": "액체",
        "종류": "산화물",
        "설명": "가장 흔한 용매. 끓는점 100℃(1atm), 어는점 0℃.",
        "안전": "일반적으로 안전하나, 전기기기와 함께 사용 주의."
    },
    "CO2": {
        "이름": "이산화탄소",
        "상태(상온)": "기체",
        "종류": "산화물",
        "설명": "호흡의 산물, 드라이아이스의 기체. 산성 산화물.",
        "안전": "고농도 흡입 주의(질식 위험). 밀폐공간 환기 필요."
    },
    "O2": {
        "이름": "산소",
        "상태(상온)": "기체",
        "종류": "단원소 분자",
        "설명": "연소와 호흡에 필수.",
        "안전": "자체는 가연성 아님. 다만 연소를 강하게 돕는다."
    },
    "N2": {
        "이름": "질소",
        "상태(상온)": "기체",
        "종류": "단원소 분자",
        "설명": "공기의 약 78% 구성.",
        "안전": "고농도에서 산소 결핍 위험."
    },
    "NaCl": {
        "이름": "염화 나트륨(소금)",
        "상태(상온)": "고체",
        "종류": "이온결합(염)",
        "설명": "바닷물의 주된 염. 물에 잘 녹음.",
        "안전": "보통 안전. 과다섭취 주의."
    },
    "HCl": {
        "이름": "염화수소(염산)",
        "상태(상온)": "수용액은 강산",
        "종류": "산",
        "설명": "강한 산성. 금속과 반응해 수소 발생.",
        "안전": "부식성. 피부/눈 보호구 필수."
    },
    "NH3": {
        "이름": "암모니아",
        "상태(상온)": "기체",
        "종류": "염기성 분자",
        "설명": "특유의 자극성 냄새. 비료 원료.",
        "안전": "자극성/독성. 환기, 보호구 필요."
    },
    "CH4": {
        "이름": "메테인(메탄)",
        "상태(상온)": "기체",
        "종류": "탄화수소",
        "설명": "천연가스의 주성분.",
        "안전": "가연성. 누출/점화원 주의."
    },
    "C2H5OH": {
        "이름": "에탄올",
        "상태(상온)": "액체",
        "종류": "알코올",
        "설명": "소독제, 용매, 연료.",
        "안전": "인화성. 불꽃/열원 주의."
    },
    "H2SO4": {
        "이름": "황산",
        "상태(상온)": "액체",
        "종류": "강산",
        "설명": "강한 탈수성/산화성. 비료/배터리 제조.",
        "안전": "강부식성. 물과 혼합 시 발열(반드시 산에 물)."
    },
    "NaHCO3": {
        "이름": "탄산수소나트륨(베이킹소다)",
        "상태(상온)": "고체",
        "종류": "염",
        "설명": "약염기성. 제과, 청소.",
        "안전": "보통 안전. 눈/피부 접촉 시 세척."
    },
    "CaCO3": {
        "이름": "탄산칼슘",
        "상태(상온)": "고체",
        "종류": "염",
        "설명": "석회석/조개껍질의 주성분.",
        "안전": "분진 흡입 주의."
    }
}

# =====================================
# 계산 함수
# =====================================

def molar_mass(comp: dict):
    m = 0.0
    for el, n in comp.items():
        if el not in ATOMIC_MASS:
            raise KeyError(f"원자량 데이터 없음: {el}")
        m += ATOMIC_MASS[el] * n
    return m

# =====================================
# 입력 영역
# =====================================
formula = st.text_input("화학식 입력", value="H2O", help="예: H2O, CO2, NaCl, Ca(OH)2")

if formula:
    try:
        comp = parse_formula(formula)
        M = molar_mass(comp)

        # 이름/기본정보 찾기 (대문자/숫자 형태로 키 맞춤)
        key_like = formula.replace(' ', '')
        info = COMPOUNDS.get(key_like)

        st.subheader("기본 정보")
        if info:
            st.write(f"**이름:** {info['이름']}")
            st.write(f"**종류:** {info['종류']} | **상태(상온):** {info['상태(상온)']}")
            st.write(f"**설명:** {info['설명']}")
            st.write(f"**안전:** {info['안전']}")
        else:
            st.info("내장 사전에 없는 화합물입니다. 아래 계산 정보만 제공합니다.")

        st.subheader("조성 및 몰질량")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**원소별 개수**")
            st.table({"원소": list(comp.keys()), "개수": list(comp.values())})
        with col2:
            st.metric("몰질량 (g/mol)", f"{M:.3f}")

        # 질량 백분율
        st.markdown("**질량 백분율(%)**")
        rows = []
        for el, n in comp.items():
            part = ATOMIC_MASS[el] * n
            pct = part / M * 100
            rows.append((el, round(pct, 3)))
        st.table({"원소": [r[0] for r in rows], "질량%": [r[1] for r in rows]})

        # 간단 분류 힌트 (규칙성 매우 단순화)
        st.subheader("간단 분류 힌트")
        els = set(comp.keys())
        if els == {"H", "O"} and comp.get("H",0)==2 and comp.get("O",0)==1:
            st.write("물(H2O): 극성 분자, 우수한 용매")
        elif "Na" in els and "Cl" in els and len(els)==2:
            st.write("이온결합 염으로 분류")
        elif "C" in els and "H" in els and len(els) == 2:
            st.write("탄화수소의 한 종류일 가능성(예: CH4, C2H6)")
        elif "C" in els and "O" in els and len(els) == 2:
            st.write("탄소의 산화물일 가능성(예: CO, CO2)")
        else:
            st.write("일반적 분류를 단순 추정하기 어려움. 구성 원소를 참고하세요.")

    except Exception as e:
        st.error(f"해석/계산 오류: {e}")

st.divider()
st.caption("※ 교육용 간이 도구입니다. 정확한 수치/안전 정보는 교과서와 공인 자료를 확인하세요.")
