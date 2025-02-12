**NYC 택시 요금 예측 시스템**

1. 프로젝트 개요
	•	목표: NYC 택시 데이터를 기반으로 한 요금 예측 시스템을 개발하고, BigQuery ML과 로컬 XGBoost 모델을 활용한 비교 분석을 통해 예측 정확도를 높이는 것을 목표로 합니다.
	•	기술 스택:
	•	데이터 저장: BigQuery, Google Cloud Storage (GCS)
	•	모델 학습: BigQuery ML (XGBoost, Linear), 로컬 XGBoost
	•	프론트엔드: Streamlit
	•	데이터 시각화: Matplotlib, Pandas
	•	환경: Python, Google Cloud Platform (GCP)
	•	주요 구현 기능:
	•	NYC 택시 데이터 정제 및 ETL (Extract, Transform, Load)
	•	BigQuery ML과 로컬 XGBoost 모델 학습
	•	Streamlit을 이용한 예측 UI 및 시각화 기능 구현
	•	요금 예측 모델의 성능 비교 및 분석

2. 개발 기간
	•	기간: 2025년 2월 8일 ~ 2025년 2월 12일

3. 데이터셋
	•	사용 데이터셋: new_york_yellow_taxi_tripdata_2024
	•	2024년도의 NYC 택시 운행 데이터
	https://www.kaggle.com/datasets/maxkharlam/nyc-yellow-taxi-trip-records-2024

5. 구현 및 분석

데이터 정제 및 ETL
	•	NYC 택시 데이터를 정제하고, 필요한 정보를 추출하여 BigQuery와 GCS에 적재하는 작업을 진행했습니다.

모델 학습 및 비교
	•	BigQuery ML (XGBoost, Linear): Google BigQuery ML을 사용하여 XGBoost와 선형 회귀 모델을 학습하고, 예측 결과를 비교했습니다.
	•	로컬 XGBoost: 로컬 환경에서 XGBoost 모델을 학습하여, BigQuery ML과 비교할 수 있는 모델을 생성했습니다.

Streamlit UI
	•	Streamlit을 사용하여 예측된 요금을 시각화하고, 사용자 입력을 받는 UI를 구현했습니다.

5. 배운 점
	•	빅쿼리 활용: Google Cloud BigQuery를 통해 대규모 데이터를 빠르고 효율적으로 쿼리하고 분석할 수 있었습니다.
	•	GCS 사용: Google Cloud Storage를 사용하여 데이터를 안전하게 저장하고, 데이터베이스와 연동하여 활용할 수 있었습니다.
	•	MLOps 경험: 모델 학습과 성능 비교 및 예측 결과를 실시간으로 확인할 수 있는 시스템을 구축하여 MLOps의 흐름을 경험했습니다.

6. 향후 계획
	•	추가적인 모델 튜닝 및 하이퍼파라미터 최적화를 통해 예측 성능을 향상시킬 예정입니다.
	•	실시간 데이터 스트리밍을 통해 예측을 실시간으로 제공하는 기능을 구현할 계획입니다.

이와 같이 프로젝트의 목적과 성과를 포트폴리오용으로 간결하게 정리하였습니다. 추가할 사항이나 수정할 부분이 있다면 알려주세요!
