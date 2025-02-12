import os
import pandas as pd
import xgboost as xgb
import numpy as np
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ 환경 변수 설정
PROJECT_ID = os.getenv("PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

# ✅ BigQuery 클라이언트 설정
bq_client = bigquery.Client(project=PROJECT_ID)
bq_storage_client = bigquery_storage_v1.BigQueryReadClient()

# ✅ BigQuery에서 데이터 로드
query = f"""
SELECT trip_distance,
       EXTRACT(HOUR FROM pickup_time) AS pickup_hour,
       EXTRACT(DAYOFWEEK FROM pickup_time) AS pickup_weekday,
       passenger_count,
       fare_amount
FROM `{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
WHERE trip_distance > 0 AND fare_amount > 0
LIMIT 300000;
"""

df = bq_client.query(query).to_dataframe(bqstorage_client=bq_storage_client)

# ✅ 데이터 정제 강화
df = df[(df["fare_amount"] > 2) & (df["fare_amount"] < 100)]  # 요금 이상치 필터링 강화
df = df[df["fare_amount"] / (df["trip_distance"] + 0.01) < 15]  # 마일당 요금 필터링

# ✅ 추가 변수 생성
df["trip_distance_sq"] = df["trip_distance"] ** 2
df["is_weekend"] = df["pickup_weekday"].apply(lambda x: 1 if x in [1, 7] else 0)
df["is_night"] = df["pickup_hour"].apply(lambda x: 1 if x < 6 or x >= 22 else 0)
df["rush_hour"] = df["pickup_hour"].apply(lambda x: 1 if (7 <= x <= 9) or (17 <= x <= 19) else 0)
df["fare_per_mile"] = df["fare_amount"] / (df["trip_distance"] + 0.01)

# ✅ 로그 변환 추가
df["log_trip_distance"] = np.log1p(df["trip_distance"])
df["log_fare_amount"] = np.log1p(df["fare_amount"])

# ✅ 데이터 크기에 따라 모델 설정 변경
if len(df) > 100000:
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,  # 트리 개수 증가
        learning_rate=0.05,  # 학습률 감소
        max_depth=6,  # 트리 깊이 증가
        subsample=0.8,  # 샘플링 비율 증가
        colsample_bytree=0.8,  # 피처 샘플링 비율 증가
        gamma=0.1,
        reg_lambda=1,
        reg_alpha=0,
        random_state=42
    )
else:
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=150,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.7,
        colsample_bytree=0.7,
        random_state=42
    )

# ✅ 데이터 분리
X = df.drop(columns=["fare_amount"])
y = df["fare_amount"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ 모델 학습
model.fit(X_train, y_train)

# ✅ 성능 평가
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5  # RMSE 계산

print(f"🚀 최적화된 XGBoost 모델 RMSE: {rmse:.2f}")

# ✅ 모델 저장
model.save_model("xgboost_fare_model_optimized.json")
print("🚀 모델 학습 완료: xgboost_fare_model_optimized.json 저장됨!")
