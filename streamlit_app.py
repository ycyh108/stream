import pandas as pd
import plotly.express as px
import streamlit as st

# 예시 데이터프레임
df = pd.DataFrame({
    '설비': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'B', 'C'],
    '측정값': [10.2, 10.5, 11.3, 10.8, 10.9, 11.1, 10.7, 11.0, 10.8],
    '불량여부': [0, 1, 0, 0, 0, 1, 0, 0, 0],
    '날짜': pd.date_range('2024-05-01', periods=9)
})

st.title("설비별 품질 통계 시각화 데모")

# 설비 선택
equipments = st.multiselect("설비 선택", df['설비'].unique(), default=df['설비'].unique())
filtered = df[df['설비'].isin(equipments)]

# 1. 설비별 Boxplot
st.subheader("설비별 측정값 분포(Boxplot)")
fig_box = px.box(filtered, x="설비", y="측정값", points="all")
st.plotly_chart(fig_box)

# 2. 설비별 평균값 Bar Chart
st.subheader("설비별 평균값")
mean_df = filtered.groupby("설비")["측정값"].mean().reset_index()
fig_mean = px.bar(mean_df, x="설비", y="측정값", text_auto=True)
st.plotly_chart(fig_mean)

# 3. 설비별 불량률 Bar Chart
st.subheader("설비별 불량률")
bad_rate_df = filtered.groupby("설비")["불량여부"].mean().reset_index()
bad_rate_df["불량률(%)"] = bad_rate_df["불량여부"] * 100
fig_bad = px.bar(bad_rate_df, x="설비", y="불량률(%)", text_auto=True)
st.plotly_chart(fig_bad)

# 4. 설비별 시계열
st.subheader("설비별 시계열(측정값)")
fig_time = px.line(filtered, x="날짜", y="측정값", color="설비", markers=True)
st.plotly_chart(fig_time)
