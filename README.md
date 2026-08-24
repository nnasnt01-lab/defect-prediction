# defect-prediction

반도체 제조 데이터를 가지고 데이터 분석·머신러닝 기초를 배우는 한국어 커리큘럼 저장소. 하루(day)마다 실습(lab)·미션(mission) 노트북이 쌓이고, day06에는 수율(yield)을 예측하는 캡스톤 프로젝트가 있다.

## 이 저장소는 무엇인가

- pandas / matplotlib / scikit-learn으로 데이터 분석과 기초 ML을 배우는 day-by-day 주피터 노트북 모음
- 별도의 애플리케이션 코드나 테스트 스위트는 없고, 각 랩의 결과물은 실제로 실행되어 출력이 남아있는 `.ipynb` 노트북 그 자체
- 노트북 안의 코드 주석·변수명·설명은 모두 한국어

## 실행 환경

- Windows, PowerShell
- Python 3.14.7
- pandas, matplotlib, scikit-learn (numpy/scipy 포함), nbconvert, nbformat, nbclient, jupyter_client, ipykernel

## 노트북 실행 방법

노트북 하나를 그 자리에서 직접 실행하려면:

```powershell
python -m jupyter nbconvert --to notebook --execute --inplace "day0X\labNN_xxx\labNN_xxx.ipynb"
```

- 실행 위치는 노트북이 있는 폴더 기준이라, 데이터 경로는 `../../data/04_secom.csv`처럼 상위 폴더를 거슬러 올라가는 상대경로로 되어 있다.
- 그래프에 한글이 박스로 깨져 보이면, 그래프를 그리기 전에 아래 설정이 필요하다.
  ```python
  plt.rcParams["font.family"] = "Malgun Gothic"
  plt.rcParams["axes.unicode_minus"] = False
  ```

## 폴더 구조

```
data/                          여러 랩이 공유하는 원본 데이터
day01/ ~ day06/                하루 단위 폴더
  labNN_kebab-case-name/       랩 하나 = 폴더 하나
    labNN_snake_case_name.ipynb
    results/                   그 랩이 만들어낸 산출물(차트, 정제된 csv 등). 있는 랩만 존재
```

### day별 랩·미션 목록 (폴더명 기준)

| day | 폴더 | 주제(폴더명 기준) |
|---|---|---|
| day01 | lab01_review | review |
| day01 | lab02_workspace | workspace |
| day01 | lab03_process-card | 공정 카드 만들기 |
| day01 | mission01_bottling | 병입(bottling) 공정 미션 |
| day02 | lab04_control-chart | 관리도 |
| day02 | lab05_sensor-diagnosis | 센서 진단 |
| day02 | lab06_clean-dataset | 데이터셋 정제 |
| day03 | lab07_train-test-split | 학습/테스트 분리 |
| day03 | lab08_baseline-model | 기준(baseline) 모델 |
| day03 | lab09_confusion-matrix | 혼동행렬 |
| day03 | mission03_greenhouse | 온실(greenhouse) 미션 |
| day04 | lab10_imbalance | 불균형 데이터 |
| day04 | lab11_tuning | 튜닝 |
| day04 | lab12_cross-validation | 교차검증 |
| day04 | mission04_battery | 배터리 미션 |
| day05 | lab13_anomaly | 이상탐지 |
| day05 | lab14_overlap | overlap |
| day05 | lab15_timeseries | 시계열 |
| day05 | mission05_coldchain | 콜드체인 미션 |
| day06 | project_v1 | 캡스톤 프로젝트 — 수율(yield) 예측 |

day02(lab04→05→06)와 day03(lab07→08)은 서로 이어져서, 뒤 노트북이 앞 노트북이 저장한 결과 파일을 다시 불러오는 구조다.

## 데이터 (`data/`)

| 파일 | 행 수 | 열 수 |
|---|---|---|
| `04_secom.csv` | 1567 | 592 |
| `day01_bottling.csv` | 4800 | 13 |
| `day03_greenhouse.csv` | 2000 | 13 |
| `day04_battery.csv` | 2847 | 14 |
| `day05_coldchain.csv` | 3412 | 12 |
| `semiconductor_yield_forecasting_data.csv` | 1250 | 28 |

**데이터 출처**: [ ] — 비워둠. 어디서 받은 데이터인지 기록이 없어 확인이 필요하다.

## day06 캡스톤 프로젝트 — project_v1 (수율 예측)

`semiconductor_yield_forecasting_data.csv`를 가지고 웨이퍼의 수율(`yield`)을 예측하는 회귀 문제를 다룬다.

### 문제 정의 카드

| 항목 | 내용 |
|---|---|
| 누가 쓰나 | 공정 엔지니어 |
| 무엇을 결정하나 | 공정 파라미터(`etch_rate`, `pressure`, `temperature`, `exposure_time`, `focus_offset`, `dose`, `deposition_rate`, `thickness_uniformity`, `implant_energy`, `tilt_angle`)로 `yield`를 예측한다 |
| 언제 결정하나 | 계측값(`critical_dimension` 등)이 나오기 전, 남은 공정이 아직 남아있는 시점 |
| 판단이 늦으면 | 남은 공정(리소·증착·임플란트 등)에 장비·소재를 이미 투입한 뒤라 되돌릴 수 없음 |

**문제 정의 (한 문장)**
> 공정 엔지니어는 공정 파라미터를 바탕으로, 계측값이 나오기 전 — 즉 남은 공정이 아직 남아있는 시점에 — 이 웨이퍼의 예상 `yield`를 예측한다.

### 지금까지 확인된 것

- `yield`는 결측치 없이 1250개 값이 모두 채워져 있고, 평균 0.4568 / 표준편차 0.1753 / 왜도 0.7405
- `yield`와의 상관관계는 계측값 쪽(`critical_dimension` -0.65, `vth` -0.54, `oxide_thickness` -0.51)이 공정 파라미터 쪽(`thickness_uniformity` -0.12, `focus_offset` 0.07, `dose` 0.06)보다 뚜렷하게 크게 나타난다 — 다만 이건 상관관계일 뿐이고, 공정 파라미터만으로 `yield`를 얼마나 잘 예측할 수 있는지는 아직 모델을 만들어봐야 알 수 있다
- 아직 회귀 모델은 만들지 않았다 (현재 노트북은 데이터 확인·분포·상관관계까지만 진행됨)

## 아직 채워지지 않은 내용

- **데이터 출처**: `data/` 안의 6개 csv가 각각 어디서 받은 것인지 기록이 없다
- **라이선스**: 저장소에 LICENSE 파일이 없다
- **day06 모델 성능**: 아직 회귀 모델을 학습하지 않아서 정확도·오차 같은 결과가 없다
- **day01, day04, day05 각 랩·미션의 세부 학습 목표**: 이 문서에는 폴더명에서 짐작할 수 있는 주제만 적었고, 각 노트북이 정확히 무엇을 가르치는지는 아직 정리되지 않았다
