import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

st.title("📅 날짜별 데이터 조회")

# ✅ 날짜 선택 위젯
selected_date = st.date_input("조회할 날짜를 선택하세요", pd.to_datetime("2024-01-01"))

# ✅ BigQuery 클라이언트 설정
bq_client = bigquery.Client(project=PROJECT_ID)

# ✅ 날짜별 데이터 조회 쿼리
query = f"""
SELECT * FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE DATE(pickup_time) = "{selected_date}"
LIMIT 1000;
"""
df = bq_client.query(query).to_dataframe()

# ✅ 데이터 표시
st.write(f"📊 {selected_date}의 택시 운행 데이터 (최대 1,000개)")
st.dataframe(df)
