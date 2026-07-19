import streamlit as st
import pandas as pd
import numpy as np

# 1. 页面配置
st.set_page_config(page_title="周会核心结果指标看板", layout="wide")
st.title("📊 核心结果指标业务看板 (周会同步)")
st.caption("实时下钻分析：订单量与 CM3 损益表现 (YoY / WoW)")

# 2. 读取精细Excel数据 (请将你的Excel命名为 data.xlsx 放在同级目录)
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()
    
    # 3. 侧边栏多维筛选器
    st.sidebar.header("🔍 业务维度筛选")
    all_regions = ["全部"] + list(df['区域'].unique())
    selected_region = st.sidebar.selectbox("选择商圈/区域", all_regions)
    
    all_cats = ["全部"] + list(df['品类'].unique())
    selected_cat = st.sidebar.selectbox("选择品类", all_cats)
    
    all_staff = ["全部"] + list(df['负责人'].unique())
    selected_staff = st.sidebar.selectbox("选择责任人(员工)", all_staff)
    
    # 数据联动过滤
    filtered_df = df.copy()
    if selected_region != "全部":
        filtered_df = filtered_df[filtered_df['区域'] == selected_region]
    if selected_cat != "全部":
        filtered_df = filtered_df[filtered_df['品类'] == selected_cat]
    if selected_staff != "全部":
        filtered_df = filtered_df[filtered_df['负责人'] == selected_staff]

    # 4. 时间周期定义 (以当前周为例自动切片)
    latest_date = filtered_df['Date'].max()
    current_week_start = latest_date - pd.Timedelta(days=latest_date.weekday())
    
    # 筛选本周、上周、去年同期
    this_week = filtered_df[(filtered_df['Date'] >= current_week_start) & (filtered_df['Date'] <= latest_date)]
    last_week = filtered_df[(filtered_df['Date'] >= current_week_start - pd.Timedelta(weeks=1)) & (filtered_df['Date'] < current_week_start)]
    last_year = filtered_df[(filtered_df['Date'] >= current_week_start - pd.DateOffset(years=1)) & (filtered_df['Date'] <= latest_date - pd.DateOffset(years=1))]

    # 5. 核心指标计算
    metrics = {}
    for col, name in [('订单量', '订单量'), ('CM3', 'CM3 利润')]:
        tw_val = this_week[col].sum()
        lw_val = last_week[col].sum()
        ly_val = last_year[col].sum()
        
        wow = ((tw_val - lw_val) / lw_val * 100) if lw_val > 0 else 0
        yoy = ((tw_val - ly_val) / ly_val * 100) if ly_val > 0 else 0
        metrics[name] = {"val": tw_val, "wow": wow, "yoy": yoy}

    # 6. 渲染看板大屏样式
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"本周总订单量 ({selected_region}/{selected_cat})", 
            value=f"{metrics['订单量']['val']:,} 单", 
            delta=f"环比上周: {metrics['订单量']['wow']:.1f}% | 同比去年: {metrics['订单量']['yoy']:.1f}%"
        )
    with col2:
        st.metric(
            label=f"本周累计 CM3 表现", 
            value=f"${metrics['CM3']['val']:,.2f}", 
            delta=f"环比上周: {metrics['CM3']['wow']:.1f}% | 同比去年: {metrics['CM3']['yoy']:.1f}%"
        )

    # 7. 明细数据透视表展示
    st.subheader("📋 业务明细透视交叉表")
    pivoted = filtered_df.groupby(['区域', '品类', '负责人']).agg({'订单量': 'sum', 'CM3': 'sum'}).reset_index()
    st.dataframe(pivoted, use_container_width=True)

except Exception as e:
    st.error(f"请检查Excel数据源格式是否正确。错误信息: {e}")
