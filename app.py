import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="홈앤쇼핑 매출 현황",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 한글 폰트 설정
import platform
if platform.system() == 'Windows':
    matplotlib.rcParams['font.family'] = 'Malgun Gothic'
else:
    matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# CSV 읽기
@st.cache_data
def load_data():
    df = pd.read_csv('data/sales.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# 데이터 처리
dates = sorted(df['date'].unique())
latest_date = dates[-1]
previous_date = latest_date - timedelta(days=1)

# 일별 매출 집계
daily_sales = df.groupby('date')['sales'].sum().reset_index()
daily_sales = daily_sales.sort_values('date')

# 오늘/어제 매출
today_sales = daily_sales[daily_sales['date'] == latest_date]['sales'].sum()
yesterday_sales = daily_sales[daily_sales['date'] == previous_date]['sales'].sum()

# 증감률
growth_rate = ((today_sales - yesterday_sales) / yesterday_sales * 100) if yesterday_sales > 0 else 0

# 금액 포맷팅
def format_currency(value):
    return f"₩{int(value):,}"

# 페이지 제목
st.title("🏪 홈앤쇼핑 일일 매출 현황")

# 3개 메트릭 카드
st.markdown("")  # 여백
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="오늘 매출",
        value=format_currency(today_sales),
        delta=None
    )

with col2:
    st.metric(
        label="어제 매출",
        value=format_currency(yesterday_sales),
        delta=None
    )

with col3:
    st.metric(
        label="어제 대비 증감률",
        value=f"{growth_rate:+.1f}%",
        delta=format_currency(today_sales - yesterday_sales)
    )

# 구분선
st.divider()

# 차트 영역
col_chart1, col_chart2 = st.columns(2)

# 왼쪽: 일별 매출 추이
with col_chart1:
    st.subheader("📈 일별 매출 추이")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor('white')

    # 선 그래프
    ax.plot(daily_sales['date'], daily_sales['sales']/1e6,
            marker='o', linewidth=2.5, markersize=5, color='#2E86AB', label='매출액')
    ax.fill_between(daily_sales['date'], daily_sales['sales']/1e6,
                    alpha=0.15, color='#2E86AB')

    # 스타일
    ax.set_xlabel('날짜', fontsize=11, fontweight='bold')
    ax.set_ylabel('매출액 (백만 원)', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#f8f9fa')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# 오른쪽: 카테고리별 매출 비중
with col_chart2:
    st.subheader("🍽️ 카테고리별 매출 비중")

    category_sales = df.groupby('category')['sales'].sum().reset_index()
    category_sales = category_sales.sort_values('sales', ascending=False)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor('white')

    # 차분한 톤의 색상
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

    wedges, texts, autotexts = ax.pie(
        category_sales['sales'],
        labels=category_sales['category'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )

    # 퍼센트 텍스트 스타일
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# 하단 통계 정보
st.divider()
col_info1, col_info2, col_info3 = st.columns(3)

total_sales = df['sales'].sum()
total_orders = df['orders'].sum()
avg_daily_sales = daily_sales['sales'].mean()

with col_info1:
    st.metric(
        label="총 매출액 (4월)",
        value=format_currency(total_sales)
    )

with col_info2:
    st.metric(
        label="총 주문수",
        value=f"{int(total_orders):,}건"
    )

with col_info3:
    st.metric(
        label="일평균 매출",
        value=format_currency(avg_daily_sales)
    )
