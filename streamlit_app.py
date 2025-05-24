import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

np.random.seed(42)

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

equip_means = {equip: 10.0 + i*0.2 for i, equip in enumerate(equipments)}
df['측정값'] = [np.random.normal(loc=equip_means[e], scale=0.15) for e in df['설비']]

target = 10.5
lsl = 10.2
usl = 10.8
df['불량여부'] = ((df['측정값'] < lsl) | (df['측정값'] > usl)).astype(int)

n_outlier = int(0.01 * n_data)
outlier_indices = np.random.choice(df.index, n_outlier, replace=False)
df.loc[outlier_indices, '측정값'] = np.random.uniform(9.8, 11.3, n_outlier)
df['불량여부'] = ((df['측정값'] < lsl) | (df['측정값'] > usl)).astype(int)

st.title("설비별 품질 통계 대시보드 (Altair 버전)")

# 설비 선택
equipments_sel = st.multiselect("설비 선택", df['설비'].unique(), default=df['설비'].unique())
filtered = df[df['설비'].isin(equipments_sel)]

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.subheader("설비별 시계열(산점도)")
    chart = alt.Chart(filtered).mark_circle(size=40).encode(
        x='날짜:T',
        y='측정값:Q',
        color='설비:N',
        tooltip=['설비', '측정값', '날짜', 'Lot', 'Wafer']
    ).interactive().properties(title="설비별 측정값 산점도")
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("설비별 측정값 분포(Boxplot)")
    box = alt.Chart(filtered).mark_boxplot().encode(
        x='설비:N',
        y='측정값:Q',
        color='설비:N',
    ).properties(title="설비별 Boxplot")
    st.altair_chart(box, use_container_width=True)

with col3:
    st.subheader("설비별 평균값 (Bar Chart)")
    mean_df = filtered.groupby("설비")["측정값"].mean().reset_index()
    bar = alt.Chart(mean_df).mark_bar().encode(
        x='설비:N',
        y='측정값:Q',
        color='설비:N',
        tooltip=['설비', '측정값']
    ).properties(title="설비별 평균")
    st.altair_chart(bar, use_container_width=True)

with col4:
    st.subheader("설비별 불량률 (Bar Chart)")
    bad_rate_df = filtered.groupby("설비")["불량여부"].mean().reset_index()
    bad_rate_df["불량률(%)"] = bad_rate_df["불량여부"] * 100
    bad = alt.Chart(bad_rate_df).mark_bar().encode(
        x='설비:N',
        y=alt.Y('불량률(%):Q', scale=alt.Scale(domain=[0,100])),
        color='설비:N',
        tooltip=['설비', '불량률(%)']
    ).properties(title="설비별 불량률")
    st.altair_chart(bad, use_container_width=True)
