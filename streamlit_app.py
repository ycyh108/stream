import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

np.random.seed(42)  # 재현성

# 설비 5대, Lot 30개, Wafer 10개씩, 날짜는 한 달치로 분포
n_data = 3000
equipments = [f'Equip_{i}' for i in range(1, 6)]
lots = [f'Lot_{i}' for i in range(101, 131)]
wafers = [f'W{i:02d}' for i in range(1, 11)]

df = pd.DataFrame({
    '설비': np.random.choice(equipments, n_data),
    'Lot': np.random.choice(lots, n_data),
    'Wafer': np.random.choice(wafers, n_data),
    '날짜': pd.to_datetime('2024-05-01') + pd.to_timedelta(np.random.randint(0, 30, n_data), unit='D'),
})

# 측정값(μm): 설비별로 살짝 다른 평균, 불량은 일부러 생성
equip_means = {equip: 10.0 + i*0.2 for i, equip in enumerate(equipments)}
df['측정값'] = [np.random.normal(loc=equip_means[e], scale=0.15) for e in df['설비']]

# LSL/USL, 불량여부
target = 10.5
lsl = 10.2
usl = 10.8
df['불량여부'] = ((df['측정값'] < lsl) | (df['측정값'] > usl)).astype(int)

# 랜덤하게 일부러 외란(불량 데이터) 추가
n_outlier = int(0.01 * n_data)
outlier_indices = np.random.choice(df.index, n_outlier, replace=False)
df.loc[outlier_indices, '측정값'] = np.random.uniform(9.8, 11.3, n_outlier)
df['불량여부'] = ((df['측정값'] < lsl) | (df['측정값'] > usl)).astype(int)

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
fig_time = px.scatter(filtered, x="날짜", y="측정값", color="설비", markers=True)
st.plotly_chart(fig_time)
