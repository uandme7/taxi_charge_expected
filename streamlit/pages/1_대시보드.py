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

# Streamlit 제목
st.title("🚕 NYC 택시 데이터 대시보드")

# ✅ BigQuery 클라이언트 설정
bq_client = bigquery.Client(project=PROJECT_ID)

# ✅ 요약 데이터 조회
query_summary = f"""
SELECT
    COUNT(*) AS total_rides,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(trip_distance), 2) AS avg_distance
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`;
"""
df_summary = bq_client.query(query_summary).to_dataframe()

# ✅ 데이터 표시
st.metric("총 운행 횟수", f"{df_summary['total_rides'][0]:,}")
st.metric("평균 요금 ($)", f"${df_summary['avg_fare'][0]}")
st.metric("평균 거리 (마일)", f"{df_summary['avg_distance'][0]} mi")

# ✅ 최근 운행 데이터 조회
query_recent = f"""
SELECT
    pickup_time,
    passenger_count,
    trip_distance,
    fare_amount
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
ORDER BY pickup_time DESC
LIMIT 1000;
"""
df_recent = bq_client.query(query_recent).to_dataframe()

# ✅ 거리별 요금 분석
st.subheader("💰 거리별 평균 요금")
st.bar_chart(df_recent.groupby("trip_distance")["fare_amount"].mean())

# ✅ 승객 수 분포
st.subheader("🧑 승객 수 분포")
st.bar_chart(df_recent["passenger_count"].value_counts())

# ✅ 시간대별 평균 요금 분석
st.subheader("⏰ 시간대별 평균 요금")
query_hourly = f"""
SELECT EXTRACT(HOUR FROM pickup_time) AS pickup_hour, AVG(fare_amount) AS avg_fare
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY pickup_hour
ORDER BY pickup_hour;
"""
df_hourly = bq_client.query(query_hourly).to_dataframe()

plt.figure(figsize=(10, 5))
plt.plot(df_hourly["pickup_hour"], df_hourly["avg_fare"], marker="o", linestyle="-")
plt.xlabel("Hour")
plt.ylabel("Average Fare ($)")
st.pyplot(plt)

# ✅ 출발지/목적지별 택시 운행량 분석
st.subheader("📍 출발지 및 목적지별 택시 운행량")
query_pickup_zone = f"""
SELECT pickup_zone, COUNT(*) AS trip_count
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY pickup_zone
ORDER BY trip_count DESC
LIMIT 10;
"""
df_pickup_zone = bq_client.query(query_pickup_zone).to_dataframe()

st.write("🚖 **가장 많이 이용된 출발지 TOP 10**")
st.bar_chart(df_pickup_zone.set_index("pickup_zone"))

query_dropoff_zone = f"""
SELECT dropoff_zone, COUNT(*) AS trip_count
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
GROUP BY dropoff_zone
ORDER BY trip_count DESC
LIMIT 10;
"""
df_dropoff_zone = bq_client.query(query_dropoff_zone).to_dataframe()

st.write("🏁 **가장 많이 이용된 목적지 TOP 10**")
st.bar_chart(df_dropoff_zone.set_index("dropoff_zone"))

# ✅ 거리별 요금 분석
st.subheader("🗺️ 거리별 요금 분석")
query_distance = f"""
SELECT
    trip_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE trip_distance > 0
GROUP BY trip_distance
ORDER BY trip_distance
LIMIT 100;
"""
df_distance = bq_client.query(query_distance).to_dataframe()

st.bar_chart(df_distance.set_index("trip_distance"))
