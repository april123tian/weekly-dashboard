import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色高对比度、现代化 executive 风格)
# ==========================================
st.set_page_config(
    page_title="Region & CM3 Data Review",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入清爽的浅色视觉主题样式
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
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
    </style>
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

# ==========================================
# 3. 侧边栏清爽导航
# ==========================================
st.sidebar.title("数据控制中心")
menu = st.sidebar.radio(
    "请选择汇报页面：",
    ["📊 整体数据复盘看板", "🔍 多维交叉明细探索", "🎯 BD个人目标达成对齐"]
)

if data_loaded:
    
    # ==========================================
    # 页面一：整体数据复盘看板
    # ==========================================
    if menu == "📊 整体数据复盘看板":
        st.title("📊 整体数据复盘看板")
        st.caption("全自动聚合分析大盘、商圈及团队层面的单量与利润趋势")
        st.markdown("---")
        
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
        
        # 顶层 KPI 卡片
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("总订单量", f"{total_orders:,} 单", format_trend_indicator(order_wow) + " (WoW)", delta_color="inverse")
        kpi_col2.metric("总订单量同比", f"{total_orders:,} 单", format_trend_indicator(order_yoy) + " (YoY)")
        kpi_col3.metric("CM3 利润总额", f"${total_cm3:,.2f}", format_trend_indicator(cm3_wow) + " (WoW)", delta_color="inverse")
        kpi_col4.metric("CM3 利润同比", f"${total_cm3:,.2f}", format_trend_indicator(cm3_yoy) + " (YoY)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
    elif menu == "🔍 多维交叉明细探索":
        st.title("🔍 多维交叉明细探索")
        st.caption("通过上方横向多选框，进行多维联动的精准商户级明细排查")
        st.markdown("---")
        
        # 横向并排排列的过滤器
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sel_regions = st.multiselect("📍 选择不同区域:", options=sorted(df_raw['Region'].dropna().unique()))
        with f_col2:
            sel_staffs = st.multiselect("👤 选择不同 BD:", options=sorted(df_raw['Staff'].dropna().unique()))
        with f_col3:
            sel_cats = st.multiselect("🍔 选择不同品类:", options=sorted(df_raw['Category'].dropna().unique()))
            
        # 联动过滤逻辑
        df_filtered = df_raw.copy()
        if sel_regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(sel_regions)]
        if sel_staffs:
            df_filtered = df_filtered[df_filtered['Staff'].isin(sel_staffs)]
        if sel_cats:
            df_filtered = df_filtered[df_filtered['Category'].isin(sel_cats)]
            
        st.subheader("📋 联动筛选结果明细表")
        
        # 计算每一行的环比和同比
        df_filtered['订单环比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_order_gap'])), axis=1)
        df_filtered['订单同比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap'])), axis=1)
        df_filtered['CM3环比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        df_filtered['CM3同比'] = df_filtered.apply(lambda r: format_trend_indicator(calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap'])), axis=1)
        
        detail_cols = ['店铺名字', 'Region', 'Staff', 'Category', 'Orders', '订单环比', '订单同比', 'CM3', 'CM3环比', 'CM3同比']
        df_disp_detail = df_filtered[detail_cols].rename(columns={
            'Region': '所属区域', 'Staff': '负责人', 'Category': '商品品类', 'Orders': '本周单量', 'CM3': 'CM3利润'
        })
        
        st.dataframe(df_disp_detail, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面三：BD个人目标达成对齐
    # ==========================================
    elif menu == "🎯 BD个人目标达成对齐":
        st.title("🎯 BD 个人目标达成对齐看板")
        st.caption("基准数据：实际业绩截至7月18日（共18天） | 月度预估系数：31天全月推算")
        st.markdown("---")
        
        # 静态精准绑定的运营指标数据
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
            
            # 1. 订单量计算
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
            
            # 2. CM3 预测计算 (纯后台科学预估，绝无计算公式文本外露)
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("💰 表二：BD个人维度月度 CM3 预测对齐")
        st.dataframe(pd.DataFrame(cm3_rows), use_container_width=True, hide_index=True)
