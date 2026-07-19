import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色高对比度皮肤)
# ==========================================
st.set_page_config(
    page_title="Region & CM3 Data Review",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入浅色主题 CSS 样式
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
    /* 统一加粗表格内文字 */
    .dataframe th {
        background-color: #e9ecef !important;
        color: #212529 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True) # <-- 已修正

# ==========================================
# 1. 动态数据加载与处理引擎
# ==========================================
def get_pct(current, gap):
    baseline = current - gap
    if pd.isna(baseline) or baseline == 0:
        return 0.0
    return (gap / baseline) * 100

def add_arrow_prefix(val, is_currency=False):
    """根据正负值自动添加绿色上升或红色下降小箭头"""
    if val > 0:
        return f"🟢 +{val:.1f}%"
    elif val < 0:
        return f"🔴 -{abs(val):.1f}%"
    return f"{val:.1f}%"

@st.cache_data
def load_and_process_data():
    df = pd.read_excel('data.xlsx')
    return df

# 加载原始大盘数据
try:
    df_raw = load_and_process_data()
    data_loaded = True
except Exception as e:
    st.error(f"无法读取 data.xlsx 文件，请确保文件存在于根目录中。错误信息: {e}")
    data_loaded = False

# ==========================================
# 2. 侧边栏导航控制 (已删除“第一页”等字样)
# ==========================================
menu = st.sidebar.radio(
    "控制面板 / 导航切换",
    ["全盘整体业绩看板", "多维交互探索中心", "BD个人目标达成对齐"]
)

if data_loaded:
    # ==========================================
    # 页面一：全盘整体业绩看板
    # ==========================================
    if menu == "全盘整体业绩看板":
        st.title("📊 全盘整体业绩看板")
        st.caption("基于本周原始数据集自动聚合 • 浅色高对比度版")
        st.markdown("---")
        
        # 核心指标计算
        total_orders = df_raw['Orders'].sum()
        total_order_gap = df_raw['weekly_order_gap'].sum()
        total_order_wow = get_pct(total_orders, total_order_gap)
        
        total_cm3 = df_raw['CM3'].sum()
        total_cm3_gap = df_raw['weekly_cm3_gap'].sum()
        total_cm3_wow = get_pct(total_cm3, total_cm3_gap)
        
        total_cm3_yoy_gap = df_raw['weekly_yoy_cm3_gap'].sum()
        total_cm3_yoy = get_pct(total_cm3, total_cm3_yoy_gap)
        
        # 顶层 KPI 卡片展示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("本周总订单量", f"{total_orders:,} 单", f"{'-' if total_order_wow < 0 else '+'}{abs(total_order_wow):.1f}% (WoW)", delta_color="inverse")
        with col2:
            st.metric("本周 CM3 利润总额", f"${total_cm3:,.2f}", f"{'-' if total_cm3_wow < 0 else '+'}{abs(total_cm3_wow):.1f}% (WoW)", delta_color="inverse")
        with col3:
            st.metric("CM3 利润去年同比走势", f"${total_cm3:,.2f}", f"+{total_cm3_yoy:.1f}% (YoY)")
            
        st.markdown("<br>", unsafe_allow_html=True) # <-- 已修正
        
        # 核心商圈表格聚合展示
        st.subheader("📍 核心商圈维度业绩阵列 (Top 排列)")
        region_agg = df_raw.groupby('Region').agg({
            'Orders': 'sum', 'weekly_order_gap': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_cm3_gap': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        region_agg['订单环比 (WoW)'] = region_agg.apply(lambda r: add_arrow_prefix(get_pct(r['Orders'], r['weekly_order_gap'])), axis=1)
        region_agg['订单同比 (YoY)'] = region_agg.apply(lambda r: add_arrow_prefix(get_pct(r['Orders'], r['weekly_yoy_order_gap'])), axis=1)
        region_agg['CM3环比 (WoW)'] = region_agg.apply(lambda r: add_arrow_prefix(get_pct(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        region_agg['CM3同比 (YoY)'] = region_agg.apply(lambda r: add_arrow_prefix(get_pct(r['CM3'], r['weekly_yoy_cm3_gap'])), axis=1)
        
        region_disp = region_agg.sort_values(by='Orders', ascending=False).head(10)
        region_table = region_disp[['Region', 'Orders', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3', 'CM3环比 (WoW)', 'CM3同比 (YoY)']]
        region_table.columns = ['商圈名称', '订单量', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3利润', 'CM3环比 (WoW)', 'CM3同比 (YoY)']
        
        st.dataframe(region_table, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面二：多维交互探索中心
    # ==========================================
    elif menu == "多维交互探索中心":
        st.title("🔍 多维交互探索中心")
        st.caption("支持按区域、BD负责人、品类跨维度动态交叉过滤")
        st.markdown("---")
        
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            selected_staff = st.multiselect("按 BD 负责人筛选:", options=df_raw['Staff'].unique())
        with filter_col2:
            selected_cat = st.multiselect("按 核心品类筛选:", options=df_raw['Category'].unique())
            
        df_filtered = df_raw.copy()
        if selected_staff:
            df_filtered = df_filtered[df_filtered['Staff'].isin(selected_staff)]
        if selected_cat:
            df_filtered = df_filtered[df_filtered['Category'].isin(selected_cat)]
            
        st.subheader("📋 过滤后的多维明细阵列")
        df_filtered['订单环比'] = df_filtered.apply(lambda r: add_arrow_prefix(get_pct(r['Orders'], r['weekly_order_gap'])), axis=1)
        df_filtered['CM3环比'] = df_filtered.apply(lambda r: add_arrow_prefix(get_pct(r['CM3'], r['weekly_cm3_gap'])), axis=1)
        
        show_cols = ['MerchantName', 'Region', 'Staff', 'Category', 'Orders', '订单环比', 'CM3', 'CM3环比']
        st.dataframe(df_filtered[show_cols], use_container_width=True, hide_index=True)

    # ==========================================
    # 页面三：BD个人目标达成对齐 (全新图片数据源)
    # ==========================================
    elif menu == "BD个人目标达成对齐":
        st.title("🎯 BD 个人目标达成对齐看板")
        st.caption("数据计算基准：实际数据截至 7月18日 (共18天) | 月度预估系数：31天")
        st.markdown("---")
        
        actual_source = {
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
        
        target_source = {
            'Mabel Wang': {'order_target': 1819, 'cm3_target': 302025},
            '张宇庭': {'order_target': 1779, 'cm3_target': 306880},
            '覃念慈': {'order_target': 1418, 'cm3_target': 232002},
            '李晓彤': {'order_target': 1924, 'cm3_target': 262125},
            '田雨卿': {'order_target': 1914, 'cm3_target': 285255},
            'Terry Meng': {'order_target': 1785, 'cm3_target': 301457},
            'Qichong Wang': {'order_target': 790, 'cm3_target': 81810},
            '时晨': {'order_target': 2310, 'cm3_target': 378308},
            'Yuan Dong': {'order_target': 2310, 'cm3_target': 321785},
        }
        
        order_data = []
        cm3_data = []
        
        for bd in target_source.keys():
            act = actual_source.get(bd, {'daily_avg': 0, 'mtd_cm3': 0})
            tgt = target_source[bd]
            
            # 单量维度
            daily_act = act['daily_avg']
            daily_tgt = tgt['order_target']
            order_rate = (daily_act / daily_tgt) * 100 if daily_tgt else 0
            order_diff = daily_act - daily_tgt
            order_arrow = "🟢 " if order_diff >= 0 else "🔴 "
            
            order_data.append({
                "BD 负责人": bd,
                "当前日均单量": f"{daily_act:,}",
                "日均单量目标": f"{daily_tgt:,}",
                "目标完成度": f"{order_rate:.1f}%",
                "目标差值": f"{order_arrow}{order_diff:+d}"
            })
            
            # CM3 维度 (纯计算，不暴露公式)
            mtd_val = act['mtd_cm3']
            est_month_cm3 = (mtd_val / 18) * 31
            cm3_tgt = tgt['cm3_target']
            cm3_rate = (est_month_cm3 / cm3_tgt) * 100 if cm3_tgt else 0
            cm3_diff = est_month_cm3 - cm3_tgt
            cm3_arrow = "🟢 " if cm3_diff >= 0 else "🔴 "
            
            cm3_data.append({
                "BD 负责人": bd,
                "本月预估 CM3 完成数": f"${est_month_cm3:,.2f}",
                "月度 CM3 目标值": f"${cm3_tgt:,.2f}",
                "目标完成度": f"{cm3_rate:.1f}%",
                "目标差值": f"{cm3_arrow}${cm3_diff:+,.2f}"
            })
            
        df_order_final = pd.DataFrame(order_data)
        df_cm3_final = pd.DataFrame(cm3_data)
        
        st.subheader("📋 表一：BD个人维度日均单量追踪")
        st.dataframe(df_order_final, use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True) # <-- 已修正
        
        st.subheader("💰 表二：BD个人维度月度 CM3 预测对齐")
        st.dataframe(df_cm3_final, use_container_width=True, hide_index=True)
