import streamlit as st
import pandas as pd

# 1. 页面配置与大标题
st.set_page_config(page_title="每周业绩核心指标看板", layout="wide")
st.title("📊 核心业绩指标互动看板 (YoY & WoW & WoW2)")
st.markdown("针对多区域、多品类、负责人维度的周度业绩追踪与多维同比环比分析。")

# 2. 读取数据
@st.cache_data
def load_data():
    try:
        # 读取第一个 Sheet
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        st.error(f"❌ 请检查 Excel 数据源格式是否正确。错误信息: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # 动态获取表格里写的时间周期作为标题展示
    time_period = df_raw['Date'].iloc[0] if 'Date' in df_raw.columns and not df_raw.empty else "本周"

    # --- 3. 侧边栏筛选器 (Sidebar Filters) ---
    st.sidebar.header("🔍 维度筛选")
    
    # 区域筛选
    regions = ["全部区域"] + list(df_raw['Region'].dropna().unique())
    selected_region = st.sidebar.selectbox("选择区域 (Region)", regions)
    
    # 品类筛选
    categories = ["全部品类"] + list(df_raw['Category'].dropna().unique())
    selected_category = st.sidebar.selectbox("选择品类 (Category)", categories)
    
    # 负责人筛选
    staffs = ["全部负责人"] + list(df_raw['Staff'].dropna().unique())
    selected_staff = st.sidebar.selectbox("选择负责人 (Staff)", staffs)
    
    # 数据过滤逻辑
    df_filtered = df_raw.copy()
    if selected_region != "全部区域":
        df_filtered = df_filtered[df_filtered['Region'] == selected_region]
    if selected_category != "全部品类":
        df_filtered = df_filtered[df_filtered['Category'] == selected_category]
    if selected_staff != "全部负责人":
        df_filtered = df_filtered[df_filtered['Staff'] == selected_staff]
        
    # --- 4. 直接聚合表格内已有的各项指标 ---
    # 本周数据 (Current Week)
    cw_orders = df_filtered['Orders'].sum()
    cw_cm3 = df_filtered['CM3'].sum()
    
    # 上周单量计算 (由于表里上周只有收入，这里环比上周单量通过现成的 gap 倒推，或直接做汇总)
    # 巧妙利用表格里的 gap 字段算出各项对比基准
    lw_orders = cw_orders - df_filtered['weekly_order_gap'].sum()
    lw_cm3 = cw_cm3 - df_filtered['weekly_cm3_gap'].sum()
    
    # 上上周数据 (2 Weeks Ago)
    w2_orders = df_filtered['上上周单量'].sum() if '上上周单量' in df_filtered.columns else 0
    w2_cm3 = df_filtered['上上周cm3'].sum() if '上上周cm3' in df_filtered.columns else 0
    
    # 去年同期数据 (YoY)
    yoy_orders = df_filtered['去年上周单量'].sum() if '去年上周单量' in df_filtered.columns else 0
    yoy_cm3 = df_filtered['去年上周cm3'].sum() if '去年上周cm3' in df_filtered.columns else 0

    # 百分比计算辅助函数
    def pct_change(current, baseline):
        if baseline and baseline != 0:
            return ((current - baseline) / baseline) * 100
        return 0.0

    # 计算各维度增长率
    wow_ord = pct_change(cw_orders, lw_orders)
    wow2_ord = pct_change(cw_orders, w2_orders)
    yoy_ord = pct_change(cw_orders, yoy_orders)
    
    wow_cm3 = pct_change(cw_cm3, lw_cm3)
    wow2_cm3 = pct_change(cw_cm3, w2_cm3)
    yoy_cm3_pct = pct_change(cw_cm3, yoy_cm3)

    # --- 5. 页面数据可视化展示 ---
    st.markdown(f"🗓️ **当前分析周报区间**：`{time_period}`")
    st.markdown("---")
    
    # 核心指标卡片排版
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 订单表现 (Orders Trend)")
        # 主数值卡片
        st.metric(label="本周总订单量 (Current Week)", value=f"{cw_orders:,.0f}")
        
        # 联动多维对比小卡片
        sub_c1, sub_c2, sub_c3 = st.columns(3)
        sub_c1.metric(label="环比上周 (WoW)", value=f"{wow_ord:+.1f}%", delta=f"{wow_ord:.1f}%")
        sub_c2.metric(label="同比去年 (YoY)", value=f"{yoy_ord:+.1f}%", delta=f"{yoy_ord:.1f}%")
        sub_c3.metric(label="对比上上周 (WoW2)", value=f"{wow2_ord:+.1f}%", delta=f"{wow2_ord:.1f}%")
        
    with col2:
        st.markdown("### 💰 利润表现 (CM3 Profit)")
        # 主数值卡片
        st.metric(label="本周总 CM3 利润", value=f"${cw_cm3:,.2f}")
        
        # 联动多维对比小卡片
        sub_c4, sub_c5, sub_c6 = st.columns(3)
        sub_c4.metric(label="环比上周 (WoW)", value=f"{wow_cm3:+.1f}%", delta=f"{wow_cm3:.1f}%")
        sub_c5.metric(label="同比去年 (YoY)", value=f"{yoy_cm3_pct:+.1f}%", delta=f"{yoy_cm3_pct:.1f}%")
        sub_c6.metric(label="对比上上周 (WoW2)", value=f"{wow2_cm3:+.1f}%", delta=f"{wow2_cm3:.1f}%")

    # --- 6. 核心商户及明细展示 ---
    st.markdown("---")
    st.markdown("### 📋 本周筛选维度下的明细数据")
    
    # 整理一下展示的列，让看报告的人更直观
    display_cols = ['Region', '店铺名字', 'Staff', 'Category', 'Orders', 'CM3', 'weekly_order_gap', 'weekly_cm3_gap']
    df_display = df_filtered[display_cols].rename(columns={
        'Region': '区域',
        'Staff': '负责人',
        'Category': '品类',
        'Orders': '本周单量',
        'CM3': '本周CM3',
        'weekly_order_gap': '较上周单量差额',
        'weekly_cm3_gap': '较上周CM3差额'
    })
    
    st.dataframe(df_display, use_container_width=True)
