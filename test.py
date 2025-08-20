# streamlit run app.py 로 실행하세요
# -*- coding: utf-8 -*-
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import streamlit as st

# ----------------------------
# 기본 설정
# ----------------------------
st.set_page_config(
    page_title="화학식 백과 & 계산기",
    page_icon="🧪",
    layout="wide",
)

# ----------------------------
# 데이터: 원자량 테이블 (IUPAC 표준 원자량 근사치)
# 참고: 학습/교육용으로 소수점은 적당히 반올림
# ----------------------------
ATOMIC_MASS: Dict[str, float] = {
    'H': 1.008, 'He': 4.0026,
    'Li': 6.94, 'Be': 9.0122, 'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180,
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.06, 'Cl': 35.45, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845,
    'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.971,
    'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 'Nb': 92.906, 'Mo': 95.95,
    'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.91, 'Pd': 106.42, 'Ag': 107.87, 'Cd': 112.41, 'In': 114.82, 'Sn': 118.71,
    'Sb': 121.76, 'Te': 127.60, 'I': 126.90, 'Xe': 131.29, 'Cs': 132.91, 'Ba': 137.33, 'La': 138.91, 'Ce': 140.12,
    'Pr': 140.91, 'Nd': 144.24, 'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.96, 'Gd': 157.25, 'Tb': 158.93, 'Dy': 162.50,
    'Ho': 164.93, 'Er': 167.26, 'Tm': 168.93, 'Yb': 173.05, 'Lu': 174.97, 'Hf': 178.49, 'Ta': 180.95, 'W': 183.84,
    'Re': 186.21, 'Os': 190.23, 'Ir': 192.22, 'Pt': 195.08, 'Au': 196.97, 'Hg': 200.59, 'Tl': 204.38, 'Pb': 207.2,
    'Bi': 208.98, 'Po': 209.0, 'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.04,
    'Pa': 231.04, 'U': 238.03, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0, 'Bk': 247.0, 'Cf': 251.0,
    'Es': 252.0, 'Fm': 257.0, 'Md': 258.0, 'No': 259.0, 'Lr': 266.0, 'Rf': 267.0, 'Db': 268.0, 'Sg': 269.0,
    'Bh': 270.0, 'Hs': 277.0, 'Mt': 278.0, 'Ds': 281.0, 'Rg': 282.0, 'Cn': 285.0, 'Nh': 286.0, 'Fl': 289.0,
    'Mc': 289.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0,
}

# ----------------------------
# 유틸: 화학식 파서 (괄호/중첩 지원)
# 예: Ca(OH)2, Al2(SO4)3, Fe(NO3)3·9H2O
# ----------------------------
TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\.|·|\d+)")

def parse_formula(formula: str) -> Dict[str, int]:
    tokens = TOKEN.findall(formula.replace(' ', ''))
    stack: List[Dict[str, int]] = [dict()]
    i = 0
    def add(elem: str, count: int):
        stack[-1][elem] = stack[-1].get(elem, 0) + count
    while i < len(tokens):
        t = tokens[i]
        if t in ('(',):
            stack.append(dict())
            i += 1
        elif t in (')',):
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            group = stack.pop()
            for k, v in group.items():
                add(k, v * mult)
        elif t in ('.', '·'):
            # hydrate separator, just skip dot and continue
            i += 1
        elif t.isdigit():
            # standalone leading coefficient (e.g., 9H2O in hydrates)
            # apply to next token/group: implement as multiplying following unit
            coeff = int(t); i += 1
            if i < len(tokens) and tokens[i] == '(':
                # start group with coeff
                stack.append(dict())
                i += 1
                # parse until matching ')'
                depth = 1
                start_idx = i
                temp = []
                while i < len(tokens) and depth > 0:
                    if tokens[i] == '(':
                        depth += 1
                    elif tokens[i] == ')':
                        depth -= 1
                    if depth > 0:
                        temp.append(tokens[i])
                    i += 1
                # now optional multiplier after ')'
                mult2 = 1
                if i < len(tokens) and tokens[i].isdigit():
                    mult2 = int(tokens[i]); i += 1
                # recursively parse temp
                sub = parse_formula(''.join(temp))
                for k, v in sub.items():
                    add(k, v * coeff * mult2)
            else:
                # next should be element
                if i < len(tokens) and re.match(r"[A-Z][a-z]?", tokens[i]):
                    elem = tokens[i]; i += 1
                    submult = 1
                    if i < len(tokens) and tokens[i].isdigit():
                        submult = int(tokens[i]); i += 1
                    add(elem, coeff * submult)
                else:
                    raise ValueError("잘못된 화학식입니다.")
        else:
            # element
            elem = t; i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            add(elem, mult)
    if len(stack) != 1:
        raise ValueError("괄호가 올바르게 닫히지 않았습니다.")
    return stack[0]


def molar_mass(formula: str) -> float:
    comp = parse_formula(formula)
    mass = 0.0
    for el, cnt in comp.items():
        if el not in ATOMIC_MASS:
            raise KeyError(f"원소 기호 '{el}' 의 원자량 정보가 없습니다.")
        mass += ATOMIC_MASS[el] * cnt
    return mass

# ----------------------------
# 공통 수식 렌더 유틸
# ----------------------------
def latex_eq(eq: str):
    st.latex(eq)

def number_input(label: str, value: Optional[float] = None, min_value: Optional[float] = None,
                  max_value: Optional[float] = None, step: Optional[float] = None, key: Optional[str] = None):
    return st.number_input(label, value=value, min_value=min_value, max_value=max_value, step=step, key=key)

# ----------------------------
# 수식 사전 (표시용)
# ----------------------------
@dataclass
class Formula:
    title: str
    latex: str
    desc: str

CATALOG: List[Formula] = [
    Formula("이상기체 법칙", r"PV = nRT", "압력 P(atm), 부피 V(L), 몰수 n(mol), 기체상수 R(0.082057 L·atm·mol^{-1}·K^{-1}), 온도 T(K)"),
    Formula("몰농도", r"M = \frac{n}{V}", "용액의 몰농도 M(mol·L^{-1})는 용질 몰수 n을 용액 부피 V로 나눈 값"),
    Formula("묽힘 법칙", r"C_1 V_1 = C_2 V_2", "희석/농축 시 농도와 부피의 곱은 일정"),
    Formula("Henderson–Hasselbalch", r"\mathrm{pH} = \mathrm{p}K_a + \log\left(\frac{[A^-]}{[HA]}\right)", "완충용액의 pH 추정"),
    Formula("강산/강염기 pH", r"\mathrm{pH}=-\log[H^+]\quad,\quad \mathrm{pOH}=-\log[OH^-]", "25℃ 순수물에서 pH + pOH = 14"),
    Formula("아보가드로 관계", r"n = \frac{N}{N_A}", "입자수 N과 아보가드로수 N_A(≈6.022×10^{23} mol^{-1})"),
    Formula("끓는점 상승", r"\Delta T_b = i K_b m", "몰랄농도 m, 반트호프 인자 i, 용매 상수 K_b"),
    Formula("어는점 내림", r"\Delta T_f = i K_f m", "몰랄농도 m, 반트호프 인자 i, 용매 상수 K_f"),
    Formula("반감기", r"N = N_0\left(\tfrac{1}{2}\right)^{t/t_{1/2}}", "방사성 붕괴/1차 반응 근사"),
]

# ----------------------------
# 사이드바 네비게이션
# ----------------------------
st.sidebar.title("🧪 화학식 백과 & 계산기")
query = st.sidebar.text_input("수식/키워드 검색", placeholder="예: 이상기체, pH, 몰농도…")
section = st.sidebar.radio("섹션", [
    "수식 모아보기", "계산기", "몰질량 계산기", "원자량 표",
])

st.sidebar.info("이 앱은 교육용입니다. 단위/상수에 주의하세요.")

# ----------------------------
# 메인 헤더
# ----------------------------
st.title("화학식 백과 & 계산기")
st.markdown("작품 의도: 자주 쓰는 화학식을 정리하고, 간단 계산기를 제공하는 Streamlit 웹앱입니다.")

# ----------------------------
# 수식 모아보기
# ----------------------------
if section == "수식 모아보기":
    st.subheader("📚 대표 화학식")
    items = [f for f in CATALOG if (not query) or (query.lower() in f.title.lower() or query.lower() in f.desc.lower())]
    if not items:
        st.warning("검색 결과가 없습니다. 다른 키워드를 입력해보세요.")
    for f in items:
        with st.expander(f"{f.title}"):
            latex_eq(f.latex)
            st.caption(f.desc)

# ----------------------------
# 계산기 섹션
# ----------------------------
elif section == "계산기":
    st.subheader("🧮 자주 쓰는 계산기")
    tabs = st.tabs(["이상기체", "몰농도/묽힘", "pH", "완충(H–H)", "콜리가티브", "반감기/1차반응"])

    # 이상기체
    with tabs[0]:
        st.markdown("#### 이상기체 법칙: ")
        latex_eq(r"PV = nRT,\quad R=0.082057\,\mathrm{L\,atm\,mol^{-1}\,K^{-1}}")
        st.caption("알려진 4개 중 3개를 입력하면 나머지 1개를 계산합니다.")
        col1, col2, col3, col4 = st.columns(4)
        P = col1.number_input("압력 P (atm)", value=1.0)
        V = col2.number_input("부피 V (L)", value=22.4)
        n = col3.number_input("몰수 n (mol)", value=1.0)
        T = col4.number_input("온도 T (K)", value=273.15)
        target = st.selectbox("어느 값을 구할까요?", ["P", "V", "n", "T"])
        R = 0.082057
        result = None
        try:
            if target == "P":
                result = n * R * T / V
            elif target == "V":
                result = n * R * T / P
            elif target == "n":
                result = P * V / (R * T)
            elif target == "T":
                result = P * V / (R * n)
            if result is not None:
                st.success(f"{target} = {result:.6g}")
        except Exception as e:
            st.error(f"계산 오류: {e}")

    # 몰농도/묽힘
    with tabs[1]:
        st.markdown("#### 몰농도/묽힘")
        c1, v1, c2, v2 = st.columns(4)
        C1 = c1.number_input("C1 (mol/L)", value=1.0)
        V1 = v1.number_input("V1 (L)", value=1.0)
        C2 = c2.number_input("C2 (mol/L)", value=0.5)
        V2 = v2.number_input("V2 (L)", value=2.0)
        target = st.selectbox("구할 값", ["C1", "V1", "C2", "V2"], key="dil_target")
        try:
            ans = None
            if target == "C1":
                ans = C2 * V2 / V1
            elif target == "V1":
                ans = C2 * V2 / C1
            elif target == "C2":
                ans = C1 * V1 / V2
            elif target == "V2":
                ans = C1 * V1 / C2
            if ans is not None:
                st.success(f"{target} = {ans:.6g}")
        except Exception as e:
            st.error(f"계산 오류: {e}")

        st.divider()
        st.markdown("##### 질량 ↔ 몰수 변환")
        colA, colB, colC = st.columns(3)
        formula = colA.text_input("화학식 (예: H2O, Al2(SO4)3·18H2O)", value="H2O", key="mol_mass_conv")
        mass_in = colB.number_input("질량 (g)", value=18.0)
        try:
            M = molar_mass(formula)
            moles = mass_in / M
            colC.metric("몰수 (mol)", f"{moles:.6g}", help=f"몰질량 M = {M:.4f} g/mol")
        except Exception as e:
            st.error(f"몰질량 계산 오류: {e}")

    # pH
    with tabs[2]:
        st.markdown("#### 강산/강염기 pH(25℃ 근사)")
        mode = st.radio("종류", ["강산 (HCl 등)", "강염기 (NaOH 등)"])
        C = st.number_input("용질 농도 (mol/L)", value=1e-3, format="%e")
        if mode.startswith("강산"):
            pH = -math.log10(C) if C > 0 else float('nan')
            st.success(f"pH ≈ {pH:.4f}")
        else:
            pOH = -math.log10(C) if C > 0 else float('nan')
            pH = 14 - pOH
            st.success(f"pH ≈ {pH:.4f}")
        st.caption("희석/활동도/자가이온화 등은 무시한 단순 근사")

    # 완충
    with tabs[3]:
        st.markdown("#### Henderson–Hasselbalch")
        pKa = st.number_input("pKa", value=4.75)
        A = st.number_input("염기형 [A-] (mol/L)", value=0.1)
        HA = st.number_input("산형 [HA] (mol/L)", value=0.1)
        if A > 0 and HA > 0:
            pH = pKa + math.log10(A/HA)
            st.success(f"pH ≈ {pH:.4f}")
        else:
            st.warning("[A-], [HA] 는 0보다 커야 합니다.")

    # 콜리가티브
    with tabs[4]:
        st.markdown("#### 콜리가티브 성질")
        col1, col2, col3, col4 = st.columns(4)
        i = col1.number_input("반트호프 인자 i", value=1.0)
        K = col2.number_input("용매 상수 K (Kb 또는 Kf)", value=0.512)
        m = col3.number_input("몰랄농도 m (mol/kg)", value=1.0)
        kind = col4.selectbox("종류", ["끓는점 상승 ΔTb", "어는점 내림 ΔTf"])
        dT = i * K * m
        st.success(f"{kind} = {dT:.6g} K")

    # 반감기
    with tabs[5]:
        st.markdown("#### 반감기/1차 반응")
        N0 = st.number_input("초기량 N0", value=100.0)
        t = st.number_input("시간 t", value=10.0)
        t12 = st.number_input("반감기 t1/2", value=5.0)
        N = N0 * (0.5 ** (t / t12)) if t12 > 0 else float('nan')
        st.success(f"N = {N:.6g}")
        st.caption("1차 반응 속도식: N = N0 e^{-kt}, k = ln2 / t1/2")

# ----------------------------
# 몰질량 계산기
# ----------------------------
elif section == "몰질량 계산기":
    st.subheader("⚖️ 몰질량 계산기")
    formula = st.text_input("화학식 입력", value="Al2(SO4)3·18H2O")
    if formula:
        try:
            comp = parse_formula(formula)
            mass = 0.0
            rows = []
            for el, cnt in sorted(comp.items()):
                if el not in ATOMIC_MASS:
                    raise KeyError(f"원소 '{el}'의 원자량 데이터가 없습니다.")
                m = ATOMIC_MASS[el] * cnt
                rows.append((el, cnt, ATOMIC_MASS[el], m))
                mass += m
            st.markdown("**구성 원소**")
            st.table({"원소": [r[0] for r in rows], "개수": [r[1] for r in rows], "원자량": [r[2] for r in rows], "기여 질량": [r[3] for r in rows]})
            st.metric("몰질량 (g/mol)", f"{mass:.4f}")
        except Exception as e:
            st.error(f"오류: {e}")
    st.caption("수화물은 '·' 또는 '.' 로 연결해 입력할 수 있습니다. 예: CuSO4·5H2O")

# ----------------------------
# 원자량 표
# ----------------------------
elif section == "원자량 표":
    st.subheader("📖 원자량 표 (교육용)")
    st.dataframe(
        {"원소": list(ATOMIC_MASS.keys()), "원자량(g/mol)": list(ATOMIC_MASS.values())},
        use_container_width=True,
    )

# ----------------------------
# 푸터
# ----------------------------
st.divider()
st.caption(
    "이 앱은 교육 목적 예시입니다. 실험/연구에는 최신 표준과 안전 지침을 반드시 확인하세요.")

