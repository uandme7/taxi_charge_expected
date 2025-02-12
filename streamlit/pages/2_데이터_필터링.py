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

st.title("🔍 데이터 필터링")

st.header("📌 필터 옵션")
passenger_count = st.slider("승객 수", 1, 6, (1, 6))
min_distance, max_distance = st.slider("거리 (마일)", 0.1, 10.0, (0.1, 10.0))
min_fare, max_fare = st.slider("요금(달러)", 0, 800, (0, 800))

# ✅ BigQuery 클라이언트 설정
bq_client = bigquery.Client(project=PROJECT_ID)

# ✅ 필터링 적용된 BigQuery 쿼리
query = f"""
SELECT *
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE passenger_count BETWEEN {passenger_count[0]} AND {passenger_count[1]}
AND trip_distance BETWEEN {min_distance} AND {max_distance}
AND fare_amount BETWEEN {min_fare} AND {max_fare}
ORDER BY pickup_time DESC
LIMIT 1000;
"""
df = bq_client.query(query).to_dataframe()

st.write("📌 검색 결과 (최대 1000개)")
st.dataframe(df)
