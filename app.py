import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色高对比度、现代化 executive 风格)
# ==========================================
st.set_page_config(
    page_title="悉尼 BD 招商数据周报看板",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏，腾出完整视野
)

# 注入清爽的浅色视觉主题样式与顶部明黄条高亮风格 (致敬截图风格)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    .header-bar {
        background-color: #FFDE00;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 25px;
        color: #1a252c;
    }
    h1, h2, h3 {
        color: #1a252c !important;
        font-weight: 700 !important;
    }
    .dataframe th {
        background-color: #e9ecef !important;
        color: #212529 !important;
        font-weight: bold !important;
        border-bottom: 2px solid #dee2e6 !important;
    }
    /* 调整 Tab 样式使其更大气 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 20px;
        padding: 5px 25px;
        border: 1px solid #dee2e6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a252c !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 顶部黄色大 Banner
st.markdown("""
    <div class="header-bar">
        <h1 style='margin:0; font-size: 28px;'>悉尼 BD 招商数据周报看板</h1>
        <p style='margin:5px 0 0 0; opacity: 0.8; font-size: 14px;'>统计周期：2026年7月13日－7月19日（周一至周日） · 统计口径：跟进人提交时间</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心工具函数：红绿趋势指示器
# ==========================================
def calculate_growth_rate(current, gap):
    """根据当前值与变动差额精准反推基准，计算增长率"""
    baseline = current - gap
    if pd.isna(baseline) or baseline == 0:
        return 0.0
    return (gap / baseline) * 100

def format_trend_indicator(val):
    """为变动率智能添加红绿趋势指针"""
    if pd.isna(val):
        return "-"
    if val > 0:
        return f"🟢 +{val:.1f}%"
    elif val < 0:
        return f"🔴 -{abs(val):.1f}%"
    return f"{val:.1f}%"

# ==========================================
# 2. 动态数据加载与处理引擎
# ==========================================
@st.cache_data
def load_and_process_perf_data():
    df = pd.read_excel('data.xlsx')
    return df

try:
    df_raw = load_and_process_perf_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ 无法读取 data.xlsx，请确保其存放在仓库根目录下。错误详情: {e}")
    data_loaded = False

if data_loaded:
    
    # ==========================================
    # 【核心调整一】使用顶部横向 Tabs 代替侧边栏
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📊 整体数据复盘看板", "🔍 多维交叉明细探索", "🎯 BD个人目标达成对齐"])

    # ==========================================
    # 页面一：整体数据复盘看板
    # ==========================================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- A. 整个大盘汇总 ---
        st.subheader("🌐 全盘核心运营总览")
        total_orders = df_raw['Orders'].sum()
        total_order_gap = df_raw['weekly_order_gap'].sum()
        total_order_yoy_gap = df_raw['weekly_yoy_order_gap'].sum()
        
        total_cm3 = df_raw['CM3'].sum()
        total_cm3_gap = df_raw['weekly_cm3_gap'].sum()
        total_cm3_yoy_gap = df_raw['weekly_yoy_cm3_gap'].sum()
        
        order_wow = calculate_growth_rate(total_orders, total_order_gap)
        order_yoy = calculate_growth_rate(total_orders, total_order_yoy_gap)
        cm3_wow = calculate_growth_rate(total_cm3, total_cm3_gap)
        cm3_yoy = calculate_growth_rate(total_cm3, total_cm3_yoy_gap)
        
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("总订单量", f"{total_orders:,} 单", format_trend_indicator(order_wow) + " (WoW)", delta_color="inverse")
        kpi_col2.metric("总订单量同比", f"{total_orders:,} 单", format_trend_indicator(order_yoy) + " (YoY)")
        kpi_col3.metric("CM3 利润总额", f"${total_cm3:,.2f}", format_trend_indicator(cm3_wow) + " (WoW)", delta_color="inverse")
        kpi_col4.metric("CM3 利润同比", f"${total_cm3:,.2f}", format_trend_indicator(cm3_yoy) + " (YoY)")
        
        st.markdown("---")
        
        # --- B. 单独区域维度业绩阵列 ---
        st.subheader("📍 各个单独区域业绩阵列")
        region_agg = df_raw.groupby('Region').agg({
            'Orders': 'sum', 'weekly_order_gap': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_cm3_gap': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        region_agg['订单环比 (WoW)'] = region_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_order_gap'])), axis=1)
        region_agg['订单同比 (YoY)'] = region_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap'])), axis=1)
        region_agg['CM3环比 (WoW)'] = region_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        region_agg['CM3同比 (YoY)'] = region_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap'])), axis=1)
        
        region_disp = region_agg[['Region', 'Orders', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3', 'CM3环比 (WoW)', 'CM3同比 (YoY)']].sort_values('Orders', ascending=False)
        region_disp.columns = ['区域名称', '本周订单量', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3利润', 'CM3环比 (WoW)', 'CM3同比 (YoY)']
        st.dataframe(region_disp, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # --- C. BD 个人维度业绩阵列 ---
        st.subheader("👤 BD 个人维度业绩阵列")
        staff_agg = df_raw.groupby('Staff').agg({
            'Orders': 'sum', 'weekly_order_gap': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_cm3_gap': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        staff_agg['订单环比 (WoW)'] = staff_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_order_gap'])), axis=1)
        staff_agg['订单同比 (YoY)'] = staff_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap'])), axis=1)
        staff_agg['CM3环比 (WoW)'] = staff_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        staff_agg['CM3同比 (YoY)'] = staff_agg.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap'])), axis=1)
        
        staff_disp = staff_agg[['Staff', 'Orders', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3', 'CM3环比 (WoW)', 'CM3同比 (YoY)']].sort_values('Orders', ascending=False)
        staff_disp.columns = ['BD负责人', '负责订单量', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3利润', 'CM3环比 (WoW)', 'CM3同比 (YoY)']
        st.dataframe(staff_disp, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面二：多维交叉明细探索
    # ==========================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 横向并排排列的筛选器
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sel_regions = st.multiselect("📍 筛选不同区域:", options=sorted(df_raw['Region'].dropna().unique()))
        with f_col2:
            sel_staffs = st.multiselect("👤 筛选不同 BD:", options=sorted(df_raw['Staff'].dropna().unique()))
        with f_col3:
            sel_cats = st.multiselect("🍔 筛选不同品类:", options=sorted(df_raw['Category'].dropna().unique()))
            
        # 执行动态数据过滤
        df_filtered = df_raw.copy()
        if sel_regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(sel_regions)]
        if sel_staffs:
            df_filtered = df_filtered[df_filtered['Staff'].isin(sel_staffs)]
        if sel_cats:
            df_filtered = df_filtered[df_filtered['Category'].isin(sel_cats)]
            
        # --- 【核心调整二】上方联动数据实时汇总 ---
        st.subheader("📊 所选维度动态运营汇总")
        
        f_total_orders = df_filtered['Orders'].sum()
        f_order_gap = df_filtered['weekly_order_gap'].sum()
        f_order_yoy_gap = df_filtered['weekly_yoy_order_gap'].sum()
        
        f_total_cm3 = df_filtered['CM3'].sum()
        f_cm3_gap = df_filtered['weekly_cm3_gap'].sum()
        f_cm3_yoy_gap = df_filtered['weekly_yoy_cm3_gap'].sum()
        
        f_order_wow = calculate_growth_rate(f_total_orders, f_order_gap)
        f_order_yoy = calculate_growth_rate(f_total_orders, f_order_yoy_gap)
        f_cm3_wow = calculate_growth_rate(f_total_cm3, f_cm3_gap)
        f_cm3_yoy = calculate_growth_rate(f_total_cm3, f_cm3_yoy_gap)
        
        # 联动展示当前筛选条件下的宏观汇总
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        sum_col1.metric("当前维度订单量", f"{f_total_orders:,} 单", format_trend_indicator(f_order_wow) + " (WoW)", delta_color="inverse")
        sum_col2.metric("当前订单量同比", f"{f_total_orders:,} 单", format_trend_indicator(f_order_yoy) + " (YoY)")
        sum_col3.metric("当前维度 CM3 总计", f"${f_total_cm3:,.2f}", format_trend_indicator(f_cm3_wow) + " (WoW)", delta_color="inverse")
        sum_col4.metric("当前 CM3 利润同比", f"${f_total_cm3:,.2f}", format_trend_indicator(f_cm3_yoy) + " (YoY)")
        
        st.markdown("---")
        
        # 联动筛选出的明细阵列
        st.subheader("📋 联动筛选结果明细表")
        df_filtered['订单环比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_order_gap'])), axis=1)
        df_filtered['订单同比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap'])), axis=1)
        df_filtered['CM3环比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        df_filtered['CM3同比 = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap'])), axis=1)
        
        detail_cols = ['店铺名字', 'Region', 'Staff', 'Category', 'Orders', '订单环比', '订单同比', 'CM3', 'CM3环比', 'CM3同比']
        df_disp_detail = df_filtered[detail_cols].rename(columns={
            'Region': '所属区域', 'Staff': '负责人', 'Category': '商品品类', 'Orders': '本周单量', 'CM3': 'CM3利润'
        })
        st.dataframe(df_disp_detail, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面三：BD个人目标达成对齐
    # ==========================================
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        
        actual_perf = {
            'Yuan Dong': {'daily_avg': 2316, 'mtd_cm3': 125359},
            '时晨': {'daily_avg': 1619, 'mtd_cm3': 145336},
            'Terry Meng': {'daily_avg': 1336, 'mtd_cm3': 119267},
            'Qichong Wang': {'daily_avg': 799, 'mtd_cm3': 47487},
            'Mabel Wang': {'daily_avg': 1572, 'mtd_cm3': 140476},
            '田雨卿': {'daily_avg': 1530, 'mtd_cm3': 126704},
            '张宇庭': {'daily_avg': 1635, 'mtd_cm3': 142211},
            '覃念慈': {'daily_avg': 1394, 'mtd_cm3': 119417},
            '李晓彤': {'daily_avg': 1593, 'mtd_cm3': 121866},
        }
        
        target_perf = {
            'Mabel Wang': {'order_tgt': 1819, 'cm3_tgt': 302025},
            '张宇庭': {'order_tgt': 1779, 'cm3_tgt': 306880},
            '覃念慈': {'order_tgt': 1418, 'cm3_tgt': 232002},
            '李晓彤': {'order_tgt': 1924, 'cm3_tgt': 262125},
            '田雨卿': {'order_tgt': 1914, 'cm3_tgt': 285255},
            'Terry Meng': {'order_tgt': 1785, 'cm3_tgt': 301457},
            'Qichong Wang': {'order_tgt': 790, 'cm3_tgt': 81810},
            '时晨': {'order_tgt': 2310, 'cm3_tgt': 378308},
            'Yuan Dong': {'order_tgt': 2310, 'cm3_tgt': 321785},
        }
        
        order_rows = []
        cm3_rows = []
        
        for name in target_perf.keys():
            act = actual_perf.get(name, {'daily_avg': 0, 'mtd_cm3': 0})
            tgt = target_perf[name]
            
            # 单量计算
            daily_act = act['daily_avg']
            daily_tgt = tgt['order_tgt']
            o_rate = (daily_act / daily_tgt) * 100 if daily_tgt else 0
            o_diff = daily_act - daily_tgt
            o_arrow = "🟢 +" if o_diff > 0 else ("🔴 " if o_diff < 0 else "")
            
            order_rows.append({
                "BD负责人": name,
                "当前日均单量": f"{daily_act:,}",
                "日均单量目标": f"{daily_tgt:,}",
                "目标完成度": f"{o_rate:.1f}%",
                "目标差值": f"{o_arrow}{o_diff:,}" if o_diff != 0 else "0"
            })
            
            # CM3 月度预估 (后台静默 18天到31天 线性放大)
            mtd_cm3_val = act['mtd_cm3']
            est_month_cm3 = (mtd_cm3_val / 18) * 31
            cm3_tgt_val = tgt['cm3_tgt']
            c_rate = (est_month_cm3 / cm3_tgt_val) * 100 if cm3_tgt_val else 0
            c_diff = est_month_cm3 - cm3_tgt_val
            c_arrow = "🟢 +" if c_diff > 0 else ("🔴 " if c_diff < 0 else "")
            
            cm3_rows.append({
                "BD负责人": name,
                "本月预估 CM3 完成数": f"${est_month_cm3:,.2f}",
                "月度 CM3 目标值": f"${cm3_tgt_val:,.2f}",
                "目标完成度": f"{c_rate:.1f}%",
                "目标差值": f"{c_arrow}${c_diff:,.2f}" if c_diff != 0 else "$0.00"
            })
            
        st.subheader("📋 表一：BD个人维度日均单量追踪")
        st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        st.subheader("💰 表二：BD个人维度月度 CM3 预测对齐")
        st.dataframe(pd.DataFrame(cm3_rows), use_container_width=True, hide_index=True)
