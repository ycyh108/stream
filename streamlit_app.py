import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from streamlit_plotly_events import plotly_events

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


st.title("설비별 품질 통계 대시보드 (Plotly-Streamlit 연동)")

# -------------- 2. 필터링 ------------------
equipments_sel = st.multiselect("설비 선택", df['설비'].unique(), default=df['설비'].unique())
filtered = df[df['설비'].isin(equipments_sel)]

# -------------- 3. 2x2 레이아웃 ------------------
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# -------------- 4. 메인 산점도 (인터랙티브) --------------
with col1:
    st.subheader("설비별 시계열(측정값, 산점도)")
    fig_time = px.scatter(
        filtered, x="날짜", y="측정값", color="설비",
        hover_data=["Lot", "Wafer"],
        title="설비별 측정값 산점도"
    )
    selected_points = plotly_events(
        fig_time,
        click_event=True,
        select_event=True
    )


# -------------- 5. 선택/브러싱 데이터 추출 --------------
if selected_points:
    sel_idx = [pt["pointIndex"] for pt in selected_points]
    sel_df = filtered.iloc[sel_idx]
    st.info(f"{len(sel_df)}개의 데이터가 선택되었습니다.")
else:
    sel_df = filtered

# -------------- 6. 나머지 3개 차트 연동 업데이트 --------------
with col2:
    st.subheader("설비별 측정값 분포(Boxplot)")
    fig_box = px.box(sel_df, x="설비", y="측정값", points="all", title="설비별 Boxplot")
    st.plotly_chart(fig_box, use_container_width=True)

with col3:
    st.subheader("설비별 평균값")
    mean_df = sel_df.groupby("설비")["측정값"].mean().reset_index()
    fig_mean = px.bar(mean_df, x="설비", y="측정값", text_auto=True, title="설비별 평균")
    st.plotly_chart(fig_mean, use_container_width=True)

with col4:
    st.subheader("설비별 불량률")
    bad_rate_df = sel_df.groupby("설비")["불량여부"].mean().reset_index()
    bad_rate_df["불량률(%)"] = bad_rate_df["불량여부"] * 100
    fig_bad = px.bar(bad_rate_df, x="설비", y="불량률(%)", text_auto=True, title="설비별 불량률")
    st.plotly_chart(fig_bad, use_container_width=True)
