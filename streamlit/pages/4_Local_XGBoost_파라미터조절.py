import os
import streamlit as st
import pandas as pd
import xgboost as xgb
from google.cloud import bigquery
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

st.title("⚙️ XGBoost 하이퍼파라미터 조정 및 학습")
st.write("현재 기본으로 설정되어있는 데이터 개수는 10만개입니다.")
st.write("현재 Local XGBOOST RSME 값은 0.2 입니다.")

# ✅ 하이퍼파라미터 입력 UI
st.header("📌 XGBoost 하이퍼파라미터 설정")
n_estimators = st.slider("🌲 트리 개수 (n_estimators)", 50, 500, 100, step=50)
learning_rate = st.slider("📉 학습률 (learning_rate)", 0.01, 0.3, 0.1, step=0.01)
max_depth = st.slider("📏 트리 깊이 (max_depth)", 2, 10, 4, step=1)
subsample = st.slider("🔄 샘플링 비율 (subsample)", 0.5, 1.0, 0.8, step=0.1)
colsample_bytree = st.slider("📊 피처 샘플링 비율 (colsample_bytree)", 0.5, 1.0, 0.8, step=0.1)

# ✅ 실행 버튼 추가
if st.button("🚀 모델 학습 시작"):
    st.write("🛠️ **모델을 학습 중입니다. 잠시만 기다려 주세요...**")

    # ✅ BigQuery 클라이언트 설정
    bq_client = bigquery.Client(project=PROJECT_ID)

    # ✅ 데이터 로드 쿼리
    query = f"""
    SELECT trip_distance,
           EXTRACT(HOUR FROM pickup_time) AS pickup_hour,
           EXTRACT(DAYOFWEEK FROM pickup_time) AS pickup_weekday,
           passenger_count,
           fare_amount
    FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE trip_distance > 0 AND fare_amount > 0
    LIMIT 100000;
    """
    df = bq_client.query(query).to_dataframe()

    # ✅ 추가 변수 생성
    df["trip_distance_sq"] = df["trip_distance"] ** 2
    df["is_weekend"] = df["pickup_weekday"].apply(lambda x: 1 if x in [1, 7] else 0)
    df["is_night"] = df["pickup_hour"].apply(lambda x: 1 if x < 6 or x >= 22 else 0)
    df["rush_hour"] = df["pickup_hour"].apply(lambda x: 1 if (7 <= x <= 9) or (17 <= x <= 19) else 0)

    # ✅ 데이터 분리
    X = df.drop(columns=["fare_amount"])
    y = df["fare_amount"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ✅ XGBoost 모델 학습 (사용자가 입력한 하이퍼파라미터 적용)
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        random_state=42
    )
    model.fit(X_train, y_train)

    # ✅ 성능 평가 (RMSE 계산)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5  # RMSE 계산

    st.success(f"🚀 학습 완료! RMSE: **{rmse:.2f}**")
    
    # ✅ 모델 저장
    model_path = "/home/JGC/proj/mlmodel/xgboost_fare_model_custom.json"
    model.save_model(model_path)
    st.write(f"💾 **모델이 저장되었습니다!** ({model_path})")
