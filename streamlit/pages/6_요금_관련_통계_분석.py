import os
import streamlit as st
import pandas as pd
import time
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

st.title("💰 요금 통계 분석")

# ✅ 승객 수별 평균 요금 및 팁 분석 쿼리
query = f"""
SELECT
    passenger_count,
    COUNT(*) AS trip_count,
    AVG(fare_amount) AS avg_fare,
    AVG(tip_amount) AS avg_tip
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE passenger_count > 0
GROUP BY passenger_count
ORDER BY passenger_count;
"""
df = bq_client.query(query).to_dataframe()

st.subheader("🚖 승객 수별 평균 요금")
st.bar_chart(df.set_index("passenger_count")["avg_fare"])

st.subheader("💵 승객 수별 평균 팁")
st.bar_chart(df.set_index("passenger_count")["avg_tip"])

st.subheader("💵 요금과 팁의 관계 분석")

# ✅ 요금과 팁의 관계 분석 쿼리
query_tip = f"""
SELECT
    fare_amount,
    AVG(tip_amount) AS avg_tip
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY fare_amount
ORDER BY fare_amount;
"""
df_tip = bq_client.query(query_tip).to_dataframe()

st.line_chart(df_tip.set_index("fare_amount")["avg_tip"])

st.subheader("👥 승객 수 & 팁 분석")

# ✅ 승객 수 & 팁 분석 쿼리
query_passenger_tip = f"""
SELECT
    passenger_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(tip_amount), 2) AS avg_tip
FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE passenger_count > 0
GROUP BY passenger_count
ORDER BY passenger_count;
"""
df = bq_client.query(query_passenger_tip).to_dataframe()

# ✅ 그래프 출력
fig, ax1 = plt.subplots()

ax1.set_xlabel("PASSENGERS")
ax1.set_ylabel("AVG CHARGE ($)", color="tab:blue")
ax1.bar(df["passenger_count"], df["avg_fare"], color="tab:blue", alpha=0.6)

ax2 = ax1.twinx()
ax2.set_ylabel("AVG TIP ($)", color="tab:green")
ax2.plot(df["passenger_count"], df["avg_tip"], color="tab:green", marker="o")

st.pyplot(fig)
