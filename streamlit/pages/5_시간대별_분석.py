import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")


bq_client = bigquery.Client(project=PROJECT_ID)

st.title("📊 시간대별 택시 이용 분석")

# ✅ 시간대별 분석 쿼리
query = f"""
SELECT
    EXTRACT(HOUR FROM pickup_time) AS pickup_hour,
    COUNT(*) AS trip_count,
    AVG(trip_distance) AS avg_distance,
    AVG(fare_amount) AS avg_fare
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY pickup_hour
ORDER BY pickup_hour;
"""
df = bq_client.query(query).to_dataframe()

st.subheader("🚖 시간대별 택시 이용량")
st.line_chart(df.set_index("pickup_hour")["trip_count"])

st.subheader("💰 시간대별 평균 요금")
st.line_chart(df.set_index("pickup_hour")["avg_fare"])

st.subheader("📅 요일별 택시 이용량 분석")

# ✅ 요일별 분석 쿼리
query_weekday = f"""
SELECT
    EXTRACT(DAYOFWEEK FROM pickup_time) AS weekday,
    COUNT(*) AS trip_count,
    AVG(fare_amount) AS avg_fare
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY weekday
ORDER BY weekday;
"""
df_weekday = bq_client.query(query_weekday).to_dataframe()

st.bar_chart(df_weekday.set_index("weekday")["trip_count"])

st.subheader("⏰ 시간대별 택시 이용량 및 요금 분석 그래프")

# ✅ 시간대별 이용량 및 요금 분석 쿼리
query_time_fare = f"""
SELECT
    EXTRACT(HOUR FROM pickup_time) AS hour,
    COUNT(*) AS ride_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY hour
ORDER BY hour
"""
df_time_fare = bq_client.query(query_time_fare).to_dataframe()

# ✅ 그래프 출력
fig, ax1 = plt.subplots()

ax1.set_xlabel("TIME (24h)")
ax1.set_ylabel("USAGE", color="tab:blue")
ax1.bar(df_time_fare["hour"], df_time_fare["ride_count"], color="tab:blue", alpha=0.6)

ax2 = ax1.twinx()
ax2.set_ylabel("AVG CHARGE ($)", color="tab:red")
ax2.plot(df_time_fare["hour"], df_time_fare["avg_fare"], color="tab:red", marker="o")

st.pyplot(fig)
