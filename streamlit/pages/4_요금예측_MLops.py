import os
import streamlit as st
import pandas as pd
import xgboost as xgb
import numpy as np
from google.cloud import bigquery
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")


bq_client = bigquery.Client(project=PROJECT_ID)

st.title("💰 NYC 택시 요금 예측")

# ✅ 사용자 입력 UI
st.header("📌 예측 모델 입력값")
distance = st.number_input("📏 여행 거리 (마일)", min_value=0.1, max_value=50.0, value=2.0)
hour = st.slider("⏰ 출발 시간 (0~23)", 0, 23, 12)
weekday = st.slider("📅 요일 (1=일, 7=토)", 1, 7, 3)
passenger = st.slider("🧑‍🤝‍🧑 승객 수", 1, 6, 1)

# ✅ 모델 선택 UI
st.subheader("📌 예측 모델 선택")
st.write("현재 로컬 XGBoost 모델의 RSME 가 0.2로 가장 낮습니다.")
model_option = st.radio(
    "사용할 예측 모델",
    ["BigQuery ML (XGBoost)", "로컬 XGBoost", "BigQuery ML (선형 회귀)", "모든 모델 비교"]
)

# 🚀 실행 버튼 추가
if st.button("🚀 시작"):
    # ✅ 입력 데이터 변환
    input_data = pd.DataFrame([[distance, hour, weekday, passenger, distance**2,
                                1 if weekday in [1, 7] else 0,  # is_weekend
                                1 if hour < 6 or hour >= 22 else 0,  # is_night
                                1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0,  # rush_hour
                                distance / (distance+0.01)  # fare_per_mile
                                ]],
                              columns=["trip_distance", "pickup_hour", "pickup_weekday", "passenger_count",
                                       "trip_distance_sq", "is_weekend", "is_night", "rush_hour", "fare_per_mile"])

    st.subheader("📊 예측 결과")

    # ✅ BigQuery ML XGBoost 예측
    if model_option in ["BigQuery ML (XGBoost)", "모든 모델 비교"]:
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
        st.write(f"💰 **BigQuery ML XGBoost 예측 요금:** **${predicted_fare_bq_xgb:.2f}**")

    # ✅ 로컬 XGBoost 예측
    if model_option in ["로컬 XGBoost", "모든 모델 비교"]:
        model = xgb.XGBRegressor()
        model.load_model("/home/JGC/proj/mlmodel/xgboost_fare_model_adaptive.json")
        predicted_fare_local = model.predict(input_data)[0]
        st.write(f"💰 **로컬 XGBoost 예측 요금:** **${predicted_fare_local:.2f}**")

    # ✅ BigQuery ML 선형 회귀 예측 추가
    if model_option in ["BigQuery ML (선형 회귀)", "모든 모델 비교"]:
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
        st.write(f"💰 **BigQuery ML 선형 회귀 예측 요금:** **${predicted_fare_bq_linear:.2f}**")

    # ✅ 모델 간 차이 비교
    if model_option == "모든 모델 비교":
        st.subheader("📉 모델 간 차이 비교:")
        st.write(f"- **BigQuery ML XGBoost vs. 로컬 XGBoost:** ${abs(predicted_fare_bq_xgb - predicted_fare_local):.2f}")
        st.write(f"- **BigQuery ML XGBoost vs. 선형 회귀:** ${abs(predicted_fare_bq_xgb - predicted_fare_bq_linear):.2f}")
        st.write(f"- **로컬 XGBoost vs. 선형 회귀:** ${abs(predicted_fare_local - predicted_fare_bq_linear):.2f}")
