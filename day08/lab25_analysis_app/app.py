# -*- coding: utf-8 -*-
# 이 파일이 한글을 utf-8로 읽고 쓰도록 명시함
import streamlit as st  # 화면을 그리는 streamlit 도구를 불러옴
import pandas as pd  # 표 데이터를 다루는 pandas 도구를 불러옴
from sklearn.model_selection import train_test_split  # 학습용·시험용을 나누는 도구를 불러옴
from datetime import datetime  # 현재 시각을 가져오기 위한 도구를 불러옴

st.set_page_config(page_title="계측값으로 공정 수율 예측하기")  # 브라우저 탭 이름을 큰 제목과 같게 설정함

st.title("계측값으로 공정 수율 예측하기")  # 화면 맨 위 큰 제목을 표시함
st.caption("공정 조건으로 수율을 예측합니다")  # 제목 아래 작은 설명 글씨를 표시함

탭_데이터훑기, 탭_전처리, 탭_학습, 탭_결과, 탭_리포트 = st.tabs(  # 탭 다섯 개를 만들고 각 탭 객체를 이름에 담음
    ["데이터 훑기", "전처리", "학습", "결과", "리포트"]  # 화면에 보일 탭 이름 목록
)

with 탭_데이터훑기:  # 데이터 훑기 탭 안쪽 내용을 시작함
    업로드_파일 = st.file_uploader("CSV 파일을 올려주세요", type=["csv"])  # CSV 파일을 올릴 수 있는 자리를 만듦

    if 업로드_파일 is not None:  # 파일이 올라왔으면
        df = pd.read_csv(업로드_파일)  # 올라온 CSV 파일을 표로 읽어들임

        st.write(f"행 {df.shape[0]}개, 열 {df.shape[1]}개")  # 행 수와 열 수를 한 줄로 보여줌

        st.write("앞의 다섯 줄")  # 다섯 줄 표 위에 붙일 안내 문구
        st.dataframe(df.head())  # 앞의 다섯 줄을 표로 보여줌

        빈칸_전체 = int(df.isnull().sum().sum())  # 전체 빈칸 개수를 셈
        st.write(f"빈칸 {빈칸_전체}개")  # 빈칸이 모두 몇 개인지 한 줄로 보여줌

        if 빈칸_전체 > 0:  # 빈칸이 있으면
            빈칸_개수 = df.isnull().sum()  # 열별 빈칸 개수를 셈
            빈칸_열 = 빈칸_개수[빈칸_개수 > 0]  # 빈칸이 있는 열만 추림
            빈칸_표 = pd.DataFrame({  # 빈칸 있는 열들을 정리한 표를 만듦
                "열 이름": 빈칸_열.index,
                "빈칸 개수": 빈칸_열.values,
                "빈칸 비율(%)": (빈칸_열.values / len(df) * 100).round(2),
            })
            st.dataframe(빈칸_표)  # 빈칸이 있는 열들을 표로 이어서 보여줌
        else:  # 빈칸이 없으면
            st.write("빈칸 없음")  # 빈칸 없음 한 줄만 보여줌

        st.write("맞는 열인지 확인하세요")  # 선택 상자 위에 확인 문구를 붙임
        결과_열 = st.selectbox(  # 결과 열을 고르는 선택 상자
            "결과 열을 고르세요", df.columns, index=len(df.columns) - 1  # 처음 값은 맨 마지막 열로 지정함
        )

        개수_표 = df[결과_열].value_counts().reset_index()  # 결과 열의 값별 개수를 셈
        개수_표.columns = ["값", "개수"]  # 표의 열 이름을 지정함
        개수_표["비율(%)"] = (개수_표["개수"] / 개수_표["개수"].sum() * 100).round(2)  # 값별 비율을 계산함
        st.dataframe(개수_표)  # 값별 개수와 비율을 표로 보여줌

        st.session_state["df"] = df  # 다른 탭에서도 쓸 수 있게 표 데이터를 저장함
        st.session_state["결과_열"] = 결과_열  # 다른 탭에서도 쓸 수 있게 고른 결과 열을 저장함

    else:  # 파일을 아직 안 올렸으면
        st.write("파일을 올려주세요")  # 안내 문구 한 줄만 보여줌

with 탭_전처리:  # 전처리 탭 안쪽 내용을 시작함
    if st.session_state.get("df") is None:  # 데이터 훑기 탭에서 올린 파일이 아직 없으면
        st.write("먼저 데이터 훑기 탭에서 파일을 올려주세요")  # 안내 문구 한 줄만 보여줌
    else:  # 파일이 이미 올라와 있으면
        df = st.session_state["df"]  # 데이터 훑기 탭에서 저장해둔 표를 그대로 가져옴
        결과_열 = st.session_state["결과_열"]  # 데이터 훑기 탭에서 고른 결과 열을 그대로 가져옴

        빈칸_원본 = int(df.isnull().sum().sum())  # 처리 전 전체 빈칸 개수를 셈
        st.write(f"빈칸 {빈칸_원본}개")  # 빈칸이 몇 개인지 맨 위에 보여줌

        if 빈칸_원본 == 0:  # 빈칸이 없으면
            st.write("빈칸이 없습니다. 채울 것이 없어요")  # 채울 것이 없다는 한 줄만 보여줌
            채움_방법 = None  # 채울 방법을 고를 필요가 없음
        else:  # 빈칸이 있으면
            채움_방법 = st.selectbox("빈칸을 무엇으로 채울까요", ["중앙값", "평균", "0"])  # 채울 방법을 고르는 선택 상자

        글자_열_목록 = [c for c in df.columns if df[c].dtype == "object" and c != 결과_열]  # 결과 열을 뺀 글자 열 목록을 찾음
        if 글자_열_목록:  # 글자로 된 열이 있으면
            st.write("글자로 된 열: " + ", ".join(글자_열_목록))  # 글자 열 목록을 보여줌
            글자_처리 = st.selectbox("글자 열을 어떻게 할까요", ["학습에서 빼기", "숫자로 바꾸기"])  # 처리 방법을 고르는 선택 상자
        else:  # 글자로 된 열이 없으면
            글자_처리 = None  # 처리할 글자 열이 없음

        결과_값_목록 = df[결과_열].dropna().unique().tolist()  # 결과 열에 실제로 있는 값 목록을 찾음
        목표값 = st.selectbox("결과 열의 어느 값을 1로 볼까요", 결과_값_목록)  # 1로 볼 값을 고르는 선택 상자

        학습비율 = st.slider("학습용 비율(%)", min_value=50, max_value=95, value=80, step=5)  # 학습:시험 비율을 고르는 슬라이더, 기본 8대 2
        st.write(f"학습용 {학습비율}% / 시험용 {100 - 학습비율}%")  # 고른 비율을 한 줄로 보여줌

        if st.button("적용"):  # 적용 단추를 눌렀으면
            작업_df = df.copy()  # 원본 표를 건드리지 않기 위해 복사본을 만듦

            if 글자_열_목록:  # 글자 열이 있었으면
                if 글자_처리 == "학습에서 빼기":  # 빼기를 골랐으면
                    작업_df = 작업_df.drop(columns=글자_열_목록)  # 글자 열들을 통째로 뺌
                    글자_설명 = f"글자 열 {len(글자_열_목록)}개를 학습에서 뺐습니다"  # 처리 결과 설명
                else:  # 숫자로 바꾸기를 골랐으면
                    for col in 글자_열_목록:  # 글자 열 하나씩
                        작업_df[col] = pd.factorize(작업_df[col])[0]  # 글자 값을 숫자로 바꿈
                    글자_설명 = f"글자 열 {len(글자_열_목록)}개를 숫자로 바꿨습니다"  # 처리 결과 설명
            else:  # 글자 열이 없었으면
                글자_설명 = "글자로 된 열이 없습니다"  # 처리 결과 설명

            작업_df["불량여부"] = (작업_df[결과_열] == 목표값).astype(int)  # 고른 값을 1로, 나머지를 0으로 바꿈
            작업_df = 작업_df.drop(columns=[결과_열])  # 원래 결과 열은 뺌

            빈칸_전 = int(작업_df.drop(columns=["불량여부"]).isnull().sum().sum())  # 빈칸 채우기 전 빈칸 개수

            if 채움_방법 is not None:  # 채울 방법을 골랐으면
                숫자_열_목록 = [c for c in 작업_df.columns if c != "불량여부"]  # 불량여부를 뺀 나머지 열
                if 채움_방법 == "중앙값":  # 중앙값을 골랐으면
                    작업_df[숫자_열_목록] = 작업_df[숫자_열_목록].fillna(작업_df[숫자_열_목록].median())  # 각 열의 중앙값으로 채움
                elif 채움_방법 == "평균":  # 평균을 골랐으면
                    작업_df[숫자_열_목록] = 작업_df[숫자_열_목록].fillna(작업_df[숫자_열_목록].mean())  # 각 열의 평균으로 채움
                else:  # 0을 골랐으면
                    작업_df[숫자_열_목록] = 작업_df[숫자_열_목록].fillna(0)  # 0으로 채움

            빈칸_후 = int(작업_df.drop(columns=["불량여부"]).isnull().sum().sum())  # 빈칸 채운 뒤 남은 빈칸 개수

            X = 작업_df.drop(columns=["불량여부"])  # 학습에 쓸 입력값들
            y = 작업_df["불량여부"]  # 학습에 쓸 정답값

            X_train, X_test, y_train, y_test = train_test_split(  # 학습용과 시험용으로 나눔
                X, y, test_size=(100 - 학습비율) / 100, random_state=42, stratify=y
            )

            st.write(f"빈칸 {빈칸_전}개 → {빈칸_후}개로 줄었습니다")  # 빈칸이 줄어든 정도를 한 줄로 보여줌
            st.write(글자_설명)  # 글자 열을 어떻게 처리했는지 한 줄로 보여줌
            st.write(f"학습용 {len(X_train)}행, 시험용 {len(X_test)}행")  # 나뉜 행 수를 한 줄로 보여줌

            학습_1개수 = int(y_train.sum())  # 학습용에서 1인 개수
            시험_1개수 = int(y_test.sum())  # 시험용에서 1인 개수
            분포_표 = pd.DataFrame({  # 학습용·시험용의 1 분포를 정리한 표를 만듦
                "구분": ["학습용", "시험용"],
                "전체 행 수": [len(y_train), len(y_test)],
                "1 개수": [학습_1개수, 시험_1개수],
                "1 비율(%)": [
                    round(학습_1개수 / len(y_train) * 100, 2),
                    round(시험_1개수 / len(y_test) * 100, 2),
                ],
            })
            st.dataframe(분포_표)  # 학습용·시험용 각각의 1 개수와 비율을 표로 보여줌

with 탭_학습:  # 학습 탭 안쪽 내용을 시작함
    st.write("여기는 아직 비어 있습니다")  # 아직 채우지 않았다는 안내 문구를 표시함

with 탭_결과:  # 결과 탭 안쪽 내용을 시작함
    st.write("여기는 아직 비어 있습니다")  # 아직 채우지 않았다는 안내 문구를 표시함

with 탭_리포트:  # 리포트 탭 안쪽 내용을 시작함
    st.write("여기는 아직 비어 있습니다")  # 아직 채우지 않았다는 안내 문구를 표시함

st.caption(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")  # 화면 맨 아래에 지금 시각을 표시함
