import streamlit as st
import pandas as pd
import datetime

# 1. 页面配置与大标题 (Dashboard Main Title)
st.set_page_config(page_title="每周业绩核心指标看板", layout="wide")
st.title("📊 核心业绩指标互动看板 (YoY & WoW & WoW2)")
st.markdown("针对多区域、多品类、负责人维度的周度业绩追踪与多维同比环比分析。")

# 2. 读取数据
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # 确保日期格式正确
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"❌ 请检查 Excel 数据源格式或列名是否正确。错误信息: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # --- 3. 侧边栏筛选器 (Sidebar Filters) ---
    st.sidebar.header("🔍 维度筛选")
    
    # 区域筛选
    regions = ["全部区域"] + list(df_raw['Region'].unique())
    selected_region = st.sidebar.selectbox("选择区域 (Region)", regions)
    
    # 品类筛选
    categories = ["全部品类"] + list(df_raw['Category'].unique())
    selected_category = st.sidebar.selectbox("选择品类 (Category)", categories)
    
    # 负责人筛选
    staffs = ["全部负责人"] + list(df_raw['Staff'].unique())
    selected_staff = st.sidebar.selectbox("选择负责人 (Staff)", staffs)
    
    # 数据过滤逻辑
    df_filtered = df_raw.copy()
    if selected_region != "全部区域":
        df_filtered = df_filtered[df_filtered['Region'] == selected_region]
    if selected_category != "全部品类":
        df_filtered = df_filtered[df_filtered['Category'] == selected_category]
    if selected_staff != "全部负责人":
        df_filtered = df_filtered[df_filtered['Staff'] == selected_staff]
        
    # --- 4. 核心时间切片逻辑 (Time-Slicing) ---
    max_date = df_filtered['Date'].max()
    
    if pd.isna(max_date):
        st.warning("⚠️ 当前筛选条件下无有效数据，请重新调整筛选器。")
    else:
        # 本周 (Current Week): 过去7天
        start_cw = max_date - datetime.timedelta(days=6)
        df_cw = df_filtered[(df_filtered['Date'] >= start_cw) & (df_filtered['Date'] <= max_date)]
        
        # 上周 (Last Week): 过去第 8-14 天
        start_lw = start_cw - datetime.timedelta(days=7)
        end_lw = start_cw - datetime.timedelta(days=1)
        df_lw = df_filtered[(df_filtered['Date'] >= start_lw) & (df_filtered['Date'] <= end_lw)]
        
        # 上上周 (2 Weeks Ago): 过去第 15-21 天
        start_2w = start_lw - datetime.timedelta(days=7)
        end_2w = start_lw - datetime.timedelta(days=1)
        df_2w = df_filtered[(df_filtered['Date'] >= start_2w) & (df_filtered['Date'] <= end_2w)]
        
        # 去年同期 (YoY Week): 去年对应的这一周 (往前推 52 周 / 364 天)
        start_yoy = start_cw - datetime.timedelta(days=364)
        end_yoy = max_date - datetime.timedelta(days=364)
        df_yoy = df_filtered[(df_filtered['Date'] >= start_yoy) & (df_filtered['Date'] <= end_yoy)]
        
        # --- 5. 指标计算 ---
        metrics = {
            'Orders': {
                'cw': df_cw['Orders'].sum(),
                'lw': df_lw['Orders'].sum(),
                'w2': df_2w['Orders'].sum(),
                'yoy': df_yoy['Orders'].sum()
            },
            'CM3': {
                'cw': df_cw['CM3'].sum(),
                'lw': df_lw['CM3'].sum(),
                'w2': df_2w['CM3'].sum(),
                'yoy': df_yoy['CM3'].sum()
            }
        }
        
        # 百分比计算辅助函数
        def pct_change(current, baseline):
            if baseline and baseline != 0:
                return ((current - baseline) / baseline) * 100
            return 0.0

        # --- 6. 页面数据可视化 ---
        st.markdown(f"🗓️ **当前分析周报区间**：`{start_cw.strftime('%Y-%m-%d')}` 至 `{max_date.strftime('%Y-%m-%d')}`")
        st.markdown("---")
        
        # 核心指标卡片排版
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📦 订单表现 (Orders Trend)")
            cw_orders = metrics['Orders']['cw']
            lw_orders = metrics['Orders']['lw']
            w2_orders = metrics['Orders']['w2']
            yoy_orders = metrics['Orders']['yoy']
            
            wow_ord = pct_change(cw_orders, lw_orders)
            wow2_ord = pct_change(cw_orders, w2_orders)
            yoy_ord = pct_change(cw_orders, yoy_orders)
            
            # 主数值卡片
            st.metric(label="本周总订单量 (Current Week)", value=f"{cw_orders:,.0f}")
            
            # 联动多维对比小卡片
            sub_c1, sub_c2, sub_c3 = st.columns(3)
            sub_c1.metric(label="环比上周 (WoW)", value=f"{wow_ord:+.1f}%", delta=f"{wow_ord:.1f}%")
            sub_c2.metric(label="同比去年 (YoY)", value=f"{yoy_ord:+.1f}%", delta=f"{yoy_ord:.1f}%")
            sub_c3.metric(label="对比上上周 (WoW2)", value=f"{wow2_ord:+.1f}%", delta=f"{wow2_ord:.1f}%")
            
        with col2:
            st.markdown("### 💰 利润表现 (CM3 Profit)")
            cw_cm3 = metrics['CM3']['cw']
            lw_cm3 = metrics['CM3']['lw']
            w2_cm3 = metrics['CM3']['w2']
            yoy_cm3 = metrics['CM3']['yoy']
            
            wow_cm3 = pct_change(cw_cm3, lw_cm3)
            wow2_cm3 = pct_change(cw_cm3, w2_cm3)
            yoy_cm3_pct = pct_change(cw_cm3, yoy_cm3)
            
            # 主数值卡片
            st.metric(label="本周总 CM3 利润", value=f"${cw_cm3:,.2f}")
            
            # 联动多维对比小卡片
            sub_c4, sub_c5, sub_c6 = st.columns(3)
            sub_c4.metric(label="环比上周 (WoW)", value=f"{wow_cm3:+.1f}%", delta=f"{wow_cm3:.1f}%")
            sub_c5.metric(label="同比去年 (YoY)", value=f"{yoy_cm3_pct:+.1f}%", delta=f"{yoy_cm3_pct:.1f}%")
            sub_c6.metric(label="对比上上周 (WoW2)", value=f"{wow2_cm3:+.1f}%", delta=f"{wow2_cm3:.1f}%")

        # --- 7. 每日细节趋势图 ---
        st.markdown("---")
        st.markdown("### 📈 本周内每日业绩细节趋势 (Daily Detail)")
        
        df_daily = df_cw.groupby('Date')[['Orders', 'CM3']].sum().reset_index()
        df_daily['Date'] = df_daily['Date'].dt.strftime('%m-%d')
        df_daily = df_daily.set_index('Date')
        
        st.line_chart(df_daily)
