import streamlit as st

st.set_page_config(page_title="NYC Taxi Dashboard", layout="wide")

st.title("🚕 뉴욕 택시 데이터 분석 프로젝트")
st.write("""
이 프로젝트는 뉴욕 택시 데이터를 활용하여 **대시보드 시각화, 지도 분석, 요금 예측, 실시간 데이터 스트리밍**을 제공합니다.
왼쪽 사이드바에서 원하는 기능을 선택하세요.
""")

st.sidebar.success("📌 왼쪽 메뉴에서 원하는 페이지를 선택하세요.")
