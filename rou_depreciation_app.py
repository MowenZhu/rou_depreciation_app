import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import base64

def calculate_present_value(lease_payment, discount_rate, payment_frequency, lease_term_years):
    periods = int(lease_term_years * payment_frequency)
    present_value = 0
    for t in range(1, periods + 1):
        present_value += lease_payment / ((1 + discount_rate / payment_frequency) ** t)
    return present_value

def calculate_monthly_depreciation(initial_value, residual_value, lease_term_months):
    total_depreciation = initial_value - residual_value
    return total_depreciation / lease_term_months

def generate_depreciation_schedule(initial_value, residual_value, lease_term_months, start_date):
    monthly_depreciation = calculate_monthly_depreciation(initial_value, residual_value, lease_term_months)
    current_value = initial_value
    schedule = []

    for month in range(lease_term_months):
        date = start_date + timedelta(days=30*month)
        current_value -= monthly_depreciation
        schedule.append({
            "日期": date.strftime("%Y-%m-%d"),
            "账面价值": round(current_value, 2),
            "折旧额": round(monthly_depreciation, 2)
        })

    return schedule

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="depreciation_schedule.csv">下载折旧明细表 (CSV)</a>'
    return href

st.title('使用权资产折旧计算器')

col1, col2 = st.columns(2)

with col1:
    payment_frequency = st.selectbox('付款频率', ['年付', '半年付', '季付', '月付'], index=0)
    frequency_map = {'年付': 1, '半年付': 2, '季付': 4, '月付': 12}
    payment_frequency_value = frequency_map[payment_frequency]
    
    payment_label = f'每{payment_frequency[:-1]}租赁付款额'
    lease_payment = st.number_input(payment_label, min_value=0.0, value=100000.0, step=1000.0)
    
    lease_term_years = st.number_input('租赁期限(年)', min_value=0.1, value=5.0, step=0.5)
    start_date = st.date_input('开始日期', datetime.now())

with col2:
    discount_rate = st.number_input('折现率 (%)', min_value=0.0, max_value=100.0, value=5.0, step=0.0001, format="%.4f") / 100
    residual_value = st.number_input('预计残值', min_value=0.0, value=0.0, step=1000.0)
    initial_direct_costs = st.number_input('初始直接费用', min_value=0.0, value=0.0, step=1000.0)

if st.button('计算折旧'):
    lease_term_months = int(lease_term_years * 12)
    
    # 计算使用权资产的入账价值
    present_value = calculate_present_value(lease_payment, discount_rate, payment_frequency_value, lease_term_years)
    initial_value = present_value + initial_direct_costs
    
    schedule = generate_depreciation_schedule(initial_value, residual_value, lease_term_months, start_date)
    df = pd.DataFrame(schedule)
    
    st.subheader('使用权资产入账价值')
    st.write(f'租赁付款额现值: ¥{present_value:,.2f}')
    st.write(f'初始直接费用: ¥{initial_direct_costs:,.2f}')
    st.write(f'使用权资产入账价值: ¥{initial_value:,.2f}')
    
    st.subheader('折旧明细表')
    st.dataframe(df)
    
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    
    st.subheader('折旧曲线图')
    fig = px.line(df, x='日期', y='账面价值', title='使用权资产账面价值随时间变化')
    st.plotly_chart(fig)
    
    total_depreciation = initial_value - residual_value
    monthly_depreciation = calculate_monthly_depreciation(initial_value, residual_value, lease_term_months)
    
    st.subheader('折旧摘要')
    st.write(f'总折旧额: ¥{total_depreciation:,.2f}')
    st.write(f'月折旧额: ¥{monthly_depreciation:,.2f}')
