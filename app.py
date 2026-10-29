import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# ---------------------------------------------------------
# 0. 그래프 한글 폰트 깨짐 방지 설정 (클라우드 배포용)
# ---------------------------------------------------------
import os
import matplotlib.font_manager as fm

# 현재 폴더에 있는 NanumGothic.ttf 파일 경로 지정
font_path = 'NanumGothic.ttf'

if os.path.exists(font_path):
    # 폰트 파일이 있으면 직접 등록해서 적용
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
elif platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------
# 1. 웹앱 메인 제목
# ---------------------------------------------------------
st.title("🎓 대학교 캠퍼스 라이프 데이터 분석 대시보드")

# ---------------------------------------------------------
# 2. CSV 파일 업로드 위젯
# 사용자가 파일을 올릴 수 있게 해주는 스트림릿 기본 기능입니다.
# ---------------------------------------------------------
uploaded_file = st.file_uploader("분석할 CSV 파일을 업로드해주세요.", type=['csv'])

# 사용자가 파일을 업로드했을 때만 아래 코드들이 실행되도록 if문을 씁니다.
if uploaded_file is not None:
    # 판다스를 이용해 업로드된 CSV 파일을 데이터프레임(표 형식)으로 읽어옵니다.
    df = pd.read_csv(uploaded_file)

    # ---------------------------------------------------------
    # 3. 업로드된 원본 데이터 미리보기 표
    # ---------------------------------------------------------
    st.subheader("1. 원본 데이터 미리보기")
    st.dataframe(df)  # 화면에 표를 그대로 그려줍니다.

    # ---------------------------------------------------------
    # 4. 데이터 전처리 (잘못된 데이터 지우기) 및 결과 안내
    # ---------------------------------------------------------
    st.subheader("2. 데이터 전처리 결과")

    # 원본 데이터가 총 몇 줄인지 기억해둡니다.
    original_count = len(df)

    # (1) 빈칸(결측치)이 있는 행을 모두 지웁니다.
    df_clean = df.dropna()

    # (2) '만족도' 열에 '모름' 같은 글자가 있으면 안되니까 숫자로 억지로 바꿉니다.
    # 문자는 숫자로 못바꾸니까 NaN(결측치)으로 변하게 됩니다. (errors='coerce'의 역할)
    df_clean['만족도'] = pd.to_numeric(df_clean['만족도'], errors='coerce')

    # 다시 한번 결측치(원래 '모름'이었던 애들)가 된 행을 지워줍니다.
    df_clean = df_clean.dropna(subset=['만족도'])

    # 살아남은 깨끗한 데이터가 몇 줄인지 셉니다.
    clean_count = len(df_clean)

    # 원본 개수 - 살아남은 개수 = 지워진 개수
    excluded_count = original_count - clean_count

    # 결과를 화면에 글씨로 띄워줍니다.
    st.write(f"✅ 결측치 및 비정상 데이터 처리 완료!")
    st.write(f"🗑️ **제외된 비정상 데이터 건수: 총 {excluded_count}건**")

    # ---------------------------------------------------------
    # 5. 학과 선택 드롭다운 필터
    # ---------------------------------------------------------
    st.subheader("3. 학과별 데이터 분석")

    # 데이터에 있는 '학과' 이름들을 중복 없이 모아서 리스트로 만듭니다.
    dept_list = df_clean['학과'].unique()

    # 드롭다운 선택창을 만들고, 사용자가 고른 학과를 selected_dept 변수에 저장합니다.
    selected_dept = st.selectbox("분석하고 싶은 학과를 선택하세요:", dept_list)

    # 전체 데이터(df_clean) 중에서 사용자가 고른 학과랑 똑같은 줄만 쏙 뽑아냅니다.
    filtered_df = df_clean[df_clean['학과'] == selected_dept]

    # ---------------------------------------------------------
    # 6. 선택한 학과의 평균 만족도 점수 표시
    # ---------------------------------------------------------
    # 선택된 학과 학생들의 만족도 점수 평균을 계산합니다.
    avg_satisfaction = filtered_df['만족도'].mean()

    # st.metric을 쓰면 화면에 크고 예쁘게 숫자를 강조해서 띄울 수 있습니다.
    st.metric(label=f"⭐ [{selected_dept}] 학생들의 평균 학교생활 만족도",
              value=f"{avg_satisfaction:.2f}점")  # 소수점 둘째 자리까지 표시

    # ---------------------------------------------------------
    # 7. 시각화 그래프 영역 (막대그래프 & 산점도)
    # ---------------------------------------------------------
    st.subheader("4. 데이터 시각화 그래프")

    # 화면을 반으로 쪼개서 왼쪽(col1)엔 막대그래프, 오른쪽(col2)엔 산점도를 넣을 겁니다.
    col1, col2 = st.columns(2)

    with col1:
        # [첫 번째 그래프: 평균 생활 습관 막대그래프]
        # 해당 학과의 공부시간, 스마트폰, 수면시간 평균을 구합니다.
        avg_study = filtered_df['공부시간'].mean()
        avg_phone = filtered_df['스마트폰'].mean()
        avg_sleep = filtered_df['수면시간'].mean()

        # 그래프 도화지를 만듭니다.
        fig1, ax1 = plt.subplots()

        # x축에 들어갈 이름들과 y축에 들어갈 평균값들
        x_labels = ['공부시간', '스마트폰', '수면시간']
        y_values = [avg_study, avg_phone, avg_sleep]

        # 막대그래프를 그립니다. (색상도 다르게 지정)
        ax1.bar(x_labels, y_values, color=['skyblue', 'lightgreen', 'salmon'])

        # 제목, x축/y축 이름, 단위 설정
        ax1.set_title(f"[{selected_dept}] 평균 생활 습관")
        ax1.set_xlabel("생활 습관 항목")
        ax1.set_ylabel("평균 시간 (단위: 시간)")

        # 스트림릿 화면에 도화지(그래프)를 띄웁니다.
        st.pyplot(fig1)

    with col2:
        # [두 번째 그래프: 수면시간과 만족도의 관계를 보는 산점도]
        # 그래프 도화지를 새로 만듭니다.
        fig2, ax2 = plt.subplots()

        # x축엔 수면시간, y축엔 만족도를 넣고 점을 찍습니다. (alpha는 점의 투명도)
        ax2.scatter(x=filtered_df['수면시간'], y=filtered_df['만족도'], color='purple', alpha=0.7)

        # 제목, x축/y축 이름, 단위 설정
        ax2.set_title(f"[{selected_dept}] 수면시간과 만족도의 상관관계")
        ax2.set_xlabel("수면시간 (단위: 시간)")
        ax2.set_ylabel("학교생활 만족도 (단위: 점)")

        # 스트림릿 화면에 도화지(그래프)를 띄웁니다.
        st.pyplot(fig2)
        # ---------------------------------------------------------
        # 8. 학생 한줄의견 분석 (색상 구분 추가 버전)
        # ---------------------------------------------------------
        st.subheader("5. 학생 한줄의견 분석")

        # 선택된 학과의 '한줄의견' 데이터를 리스트로 가져옵니다.
        opinions = filtered_df['한줄의견'].dropna().tolist()

        # 띄어쓰기를 기준으로 모든 단어를 쪼개서 하나의 리스트에 모읍니다.
        all_words = []
        for text in opinions:
            words = text.split()
            all_words.extend(words)

        # 긍정/부정 단어 리스트 정의
        positive_words = ['좋아요.', '좋아요', '재미있어요.', '재미있어요', '맛있어요.', '맛있어요', '도움이']
        negative_words = ['부족해요.', '부족해요', '피곤해요.', '피곤해요', '불편해요.', '불편해요']

        # 긍정/부정 단어 개수 세기
        pos_count = 0
        neg_count = 0
        for word in all_words:
            if word in positive_words:
                pos_count += 1
            elif word in negative_words:
                neg_count += 1

        # 화면에 긍정/부정 단어 개수 표시
        st.write(f"**[{selected_dept}] 한줄의견 감성 분석**")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("😊 긍정 단어 등장 횟수", f"{pos_count}회")
        with col4:
            st.metric("😥 부정 단어 등장 횟수", f"{neg_count}회")

        # 단어별 등장 횟수 세기
        word_counts = {}
        for word in all_words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        # 등장 횟수 기준으로 내림차순 정렬하여 상위 10개 단어 뽑기
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        top_words = [item[0] for item in sorted_words]
        top_counts = [item[1] for item in sorted_words]

        # 가로 막대그래프 순서 맞추기 (1위가 맨 위로 오도록 반전)
        top_words.reverse()
        top_counts.reverse()

        # [핵심] 단어의 성격에 따라 막대 색상 리스트를 생성합니다.
        # 긍정: 파란색(cornflowerblue), 부정: 빨간색(lightcoral), 일반: 회색(lightgray)
        bar_colors = []
        for word in top_words:
            if word in positive_words:
                bar_colors.append('cornflowerblue')
            elif word in negative_words:
                bar_colors.append('lightcoral')
            else:
                bar_colors.append('lightgray')

        # 가로 막대그래프 그리기
        fig3, ax3 = plt.subplots()

        # color 매개변수에 우리가 만든 색상 리스트(bar_colors)를 넣어줍니다.
        ax3.barh(top_words, top_counts, color=bar_colors)

        # 제목, 축 이름, 단위 설정
        ax3.set_title(f"[{selected_dept}] 자주 등장하는 단어 Top 10 (파랑: 긍정 / 빨강: 부정)")
        ax3.set_xlabel("등장 횟수 (단위: 회)")
        ax3.set_ylabel("단어")

        # 화면에 그래프 출력
        st.pyplot(fig3)