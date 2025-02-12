import os
import streamlit as st
import pandas as pd
import xgboost as xgb
import numpy as np
from google.cloud import bigquery
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

bq_client = bigquery.Client(project=PROJECT_ID)

st.title("💰 NYC 택시 요금 예측")

# ✅ 사용자 입력 UI
st.subheader("📌 예측을 위한 입력값 설정")
col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("📏 여행 거리 (마일)", min_value=0.1, max_value=50.0, value=2.0)
with col2:
    hour = st.slider("⏰ 출발 시간 (0~23)", 0, 23, 12)

col1, col2 = st.columns(2)
with col1:
    weekday = st.slider("📅 요일 선택 (1=일요일, 7=토요일)", 1, 7, 3)
with col2:
    passenger = st.slider("🧑 승객 수", 1, 6, 1)

# ✅ 모델 선택 UI
st.subheader("📌 예측 모델 선택")
model_option = st.multiselect(
    "비교할 모델을 선택하세요",
    ["BigQuery ML (XGBoost)", "LOCAL XGBoost", "BigQuery ML LINEAR"],
    default=["LOCAL XGBoost"]
)

# ✅ 실행 버튼 추가
if st.button("🚀 요금 예측 실행"):
    input_data = pd.DataFrame([[distance, hour, weekday, passenger, distance**2,
                                1 if weekday in [1, 7] else 0,  # is_weekend
                                1 if hour < 6 or hour >= 22 else 0,  # is_night
                                1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0,  # rush_hour
                                distance / (distance+0.01)]],  # fare_per_mile
                              columns=["trip_distance", "pickup_hour", "pickup_weekday", "passenger_count",
                                       "trip_distance_sq", "is_weekend", "is_night", "rush_hour", "fare_per_mile"])

    st.subheader("📊 예측 결과")
    results = {}

    # ✅ BigQuery ML XGBoost 예측
    if "BigQuery ML (XGBoost)" in model_option:
        query_xgb = f"""
        SELECT predicted_fare_amount FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{BIGQUERY_DATASET}.fare_prediction_xgb`,
            (SELECT {distance} AS trip_distance, {hour} AS pickup_hour, {weekday} AS pickup_weekday, {passenger} AS passenger_count,
                    {distance**2} AS trip_distance_sq,
                    {1 if weekday in [1, 7] else 0} AS is_weekend,
                    {1 if hour < 6 or hour >= 22 else 0} AS is_night,
                    {1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0} AS rush_hour,
                    {distance / (distance+0.01)} AS fare_per_mile)
        );
        """
        df_pred_xgb = bq_client.query(query_xgb).to_dataframe()
        predicted_fare_bq_xgb = df_pred_xgb.iloc[0]["predicted_fare_amount"]
        results["BigQuery ML XGBoost"] = predicted_fare_bq_xgb

    # ✅ 로컬 XGBoost 예측
    if "LOCAL XGBoost" in model_option:
        model = xgb.XGBRegressor()
        model.load_model("/home/JGC/proj/mlmodel/optimize/xgboost_fare_model_optimized.json")
        predicted_fare_local = model.predict(input_data)[0]
        results["LOCAL XGBoost"] = predicted_fare_local

    # ✅ BigQuery ML 선형 회귀 예측
    if "BigQuery ML LINEAR" in model_option:
        query_linear = f"""
        SELECT predicted_fare_amount FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{BIGQUERY_DATASET}.fare_prediction_linear`,
            (SELECT {distance} AS trip_distance, {hour} AS pickup_hour, {weekday} AS pickup_weekday, {passenger} AS passenger_count,
                    {distance**2} AS trip_distance_sq,
                    {1 if weekday in [1, 7] else 0} AS is_weekend,
                    {1 if hour < 6 or hour >= 22 else 0} AS is_night,
                    {1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0} AS rush_hour,
                    {distance / (distance+0.01)} AS fare_per_mile)
        );
        """
        df_pred_linear = bq_client.query(query_linear).to_dataframe()
        predicted_fare_bq_linear = df_pred_linear.iloc[0]["predicted_fare_amount"]
        results["BigQuery ML LINEAR"] = predicted_fare_bq_linear

    # ✅ 모델 비교 그래프 표시
    st.subheader("📉 모델별 예측 요금 비교")
    results_df = pd.DataFrame(list(results.items()), columns=["MODEL", "GUESS CHARGE ($)"])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(results_df["MODEL"], results_df["GUESS CHARGE ($)"], color=["blue", "green", "red"])
    ax.set_ylabel("GUESS CHARGE ($)")
    st.pyplot(fig)
