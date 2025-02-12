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

st.title("💰 NYC 택시 요금 예측 (ver4)")

# ✅ 사용자 입력 UI
st.subheader("📌 예측을 위한 입력값 설정")
distance = st.number_input("📏 여행 거리 (마일)", min_value=0.1, max_value=50.0, value=2.0)
hour = st.slider("⏰ 출발 시간 (0~23)", 0, 23, 12)
weekday = st.slider("📅 요일 선택 (1=일요일, 7=토요일)", 1, 7, 3)
passenger = st.slider("🧑 승객 수", 1, 6, 1)

# ✅ 모델 선택 UI
st.subheader("📌 예측 모델 선택")
model_option = st.multiselect(
    "비교할 모델을 선택하세요",
    ["BigQuery ML XGBoost (ver2)", "LOCAL XGBoost", "BigQuery ML LINEAR (ver2)"],
    default=["BigQuery ML XGBoost (ver2)", "LOCAL XGBoost", "BigQuery ML LINEAR (ver2)"]
)

st.subheader("📊 모델 성능 비교")
st.write("- **BigQuery XGBoost**  RSME : 0.87  (모든 데이터 활용)")
st.write("- **LOCAL XGBoost**  RSME : 0.03  (30만 개 데이터 제한)")
st.write("- **BigQuery Linear**  RSME : 3.98  (모든 데이터 활용)")

# 🚀 실행 버튼 추가
if st.button("🚀 요금 예측 실행"):
    input_data = pd.DataFrame([[distance, hour, weekday, passenger, distance**2,
                                1 if weekday in [1, 7] else 0,  # is_weekend
                                1 if hour < 6 or hour >= 22 else 0,  # is_night
                                1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0,  # rush_hour
                                distance / (distance+0.01),  # fare_per_mile
                                np.log1p(distance),  # log_trip_distance
                                np.log1p(15)]],  # log_fare_amount (평균값 사용)
                              columns=["trip_distance", "pickup_hour", "pickup_weekday", "passenger_count",
                                       "trip_distance_sq", "is_weekend", "is_night", "rush_hour", "fare_per_mile",
                                       "log_trip_distance", "log_fare_amount"])

    st.subheader("📊 예측 결과")
    results = {}

    # ✅ BigQuery ML XGBoost 예측 (ver2 적용)
    if "BigQuery ML XGBoost (ver2)" in model_option:
        query_xgb = f"""
        SELECT predicted_fare_amount FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{BIGQUERY_DATASET}.fare_prediction_xgb_ver2`,
            (SELECT {distance} AS trip_distance, {hour} AS pickup_hour, {weekday} AS pickup_weekday, {passenger} AS passenger_count,
                    {distance**2} AS trip_distance_sq,
                    {1 if weekday in [1, 7] else 0} AS is_weekend,
                    {1 if hour < 6 or hour >= 22 else 0} AS is_night,
                    {1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0} AS rush_hour,
                    {distance / (distance+0.01)} AS fare_per_mile,
                    LOG({distance} + 1) AS log_trip_distance,
                    LOG(15 + 1) AS log_fare_amount)
        );
        """
        df_pred_xgb = bq_client.query(query_xgb).to_dataframe()
        results["BigQuery ML XGBoost (ver2)"] = df_pred_xgb.iloc[0]["predicted_fare_amount"]

    # ✅ 로컬 XGBoost 예측
    if "LOCAL XGBoost" in model_option:
        model = xgb.XGBRegressor()
        model.load_model("/home/JGC/proj/mlmodel/optimize/xgboost_fare_model_optimized.json")
        results["LOCAL XGBoost"] = model.predict(input_data)[0]

    # ✅ BigQuery ML 선형 회귀 예측 (ver2 적용)
    if "BigQuery ML LINEAR (ver2)" in model_option:
        query_linear = f"""
        SELECT predicted_fare_amount FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{BIGQUERY_DATASET}.fare_prediction_linear_ver2`,
            (SELECT {distance} AS trip_distance, {hour} AS pickup_hour, {weekday} AS pickup_weekday, {passenger} AS passenger_count,
                    {distance**2} AS trip_distance_sq,
                    {1 if weekday in [1, 7] else 0} AS is_weekend,
                    {1 if hour < 6 or hour >= 22 else 0} AS is_night,
                    {1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0} AS rush_hour,
                    {distance / (distance+0.01)} AS fare_per_mile,
                    LOG({distance} + 1) AS log_trip_distance,
                    LOG(15 + 1) AS log_fare_amount)
        );
        """
        df_pred_linear = bq_client.query(query_linear).to_dataframe()
        results["BigQuery ML LINEAR (ver2)"] = df_pred_linear.iloc[0]["predicted_fare_amount"]

    # 📊 모델 비교 그래프
    st.subheader("📉 모델별 예측 요금 비교")
    results_df = pd.DataFrame(list(results.items()), columns=["MODEL", "GUESS CHARGE ($)"])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(results_df["MODEL"], results_df["GUESS CHARGE ($)"], color=["blue", "green", "red"])
    ax.set_ylabel("GUESS CHARGE ($)")
    st.pyplot(fig)

    # 🚖 실제 요금 분포 vs 예측 요금 비교
    st.subheader("📊 실제 요금 분포 vs 예측 요금 비교")
    query_hist = f"""
    SELECT fare_amount FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE trip_distance BETWEEN {distance - 1} AND {distance + 1}
    """
    df_hist = bq_client.query(query_hist).to_dataframe()
    df_hist_filtered = df_hist[df_hist["fare_amount"].between(0, 100)]

    plt.figure(figsize=(8, 4))
    plt.hist(df_hist_filtered["fare_amount"], bins=50, alpha=0.6, color="gray", label="REAL CHARGE INFO")

    colors = ["blue", "green", "red", "purple", "orange"]  # 최대 5개의 모델 지원

    # 예측 요금을 그래프에 추가 (각 모델마다 다른 색상 적용)
    for i, (model, fare) in enumerate(results.items()):
        plt.axvline(fare, color=colors[i % len(colors)], linestyle="dashed", linewidth=2, label=f"{model}: ${fare:.2f}")

    plt.xlabel("CHARGE ($)")
    plt.ylabel("frequency")
    plt.xlim(0, 100)
    plt.legend()
    st.pyplot(plt)
