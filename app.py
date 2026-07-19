import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色高对比度、现代化 Executive 看板风格)
# ==========================================
st.set_page_config(
    page_title="悉尼 BD 单量&CM3数据周报看板",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入高对比度、纯白阴影卡片、复刻截图风格的 CSS 样式
st.markdown("""
    <style>
    /* 基础背景与文字颜色锁死，防止亮暗主题切换导致白字不可见 */
    .stApp {
        background-color: #f4f5f7 !important;
        color: #1a252c !important;
    }
    
    /* 顶部明黄条高亮 */
    .header-bar {
        background-color: #FFDE00;
        padding: 24px;
        border-radius: 6px;
        margin-bottom: 25px;
        color: #1a252c !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 强力锁死所有标题与正常文本颜色 */
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown {
        color: #1a252c !important;
    }
    
    /* 复刻截图：白底、圆角、微阴影的高级数据指标卡片 */
    .kpi-card {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #eef0f2;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 15px;
        min-height: 140px;
    }
    .kpi-title {
        color: #6c757d !important;
        font-size: 13px !important;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #1a252c !important;
        font-size: 28px !important;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .kpi-desc {
        color: #8c96a0 !important;
        font-size: 12px !important;
    }
    .trend-up {
        color: #28a745 !important;
        font-weight: bold;
    }
    .trend-down {
        color: #dc3545 !important;
        font-weight: bold;
    }

    /* 顶部大标签页选中的现代化按钮视觉优化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #ffffff;
        border-radius: 6px;
        padding: 5px 24px;
        border: 1px solid #e2e8f0;
        color: #4a5568 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a252c !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 顶部大 Banner (保持跟第一版一致的悉尼看板名头)
st.markdown("""
    <div class="header-bar">
        <h1 style='margin:0; font-size: 26px; font-weight:700;'>悉尼 BD 招商数据周报看板</h1>
        <p style='margin:6px 0 0 0; opacity: 0.8; font-size: 13px;'>统计周期：2026年7月13日－7月19日（周一至周日） </p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心工具函数：趋势与增长计算
# ==========================================
def calculate_growth_rate(current, gap):
    baseline = current - gap
    if pd.isna(baseline) or baseline == 0:
        return 0.0
    return (gap / baseline) * 100

def get_trend_html(val, label_suffix=""):
    """输出美观的红绿HTML趋势标签，解决官方组件颜色发白或者错乱问题"""
    if pd.isna(val):
        return "<span style='color:#8c96a0;'>-</span>"
    if val > 0:
        return f"<span class='trend-up'>▲ +{val:.1f}%</span> <span style='color:#8c96a0; font-size:11px;'>{label_suffix}</span>"
    elif val < 0:
        return f"<span class='trend-down'>▼ -{abs(val):.1f}%</span> <span style='color:#8c96a0; font-size:11px;'>{label_suffix}</span>"
    return f"<span style='color:#1a252c;'>{val:.1f}%</span>"

# ==========================================
# 2. 数据加载引擎
# ==========================================
@st.cache_data
def load_and_process_perf_data():
    df = pd.read_excel('data.xlsx')
    return df

try:
    df_raw = load_and_process_perf_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ 无法读取 data.xlsx，请确保其存放在项目根目录下。错误详情: {e}")
    data_loaded = False

if data_loaded:
    
    # ==========================================
    # 顶部横向标签页切换 (完全移除侧边栏)
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📊 整体数据复盘看板", "🔍 多维交叉明细探索", "🎯 BD个人目标达成对齐"])

    # ------------------------------------------
    # 标签页一：整体数据复盘看板
    # ------------------------------------------
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:15px;'>🌐 全盘核心运营总览</h3>", unsafe_allow_html=True)
        
        # 计算大盘全局指标
        total_orders = df_raw['Orders'].sum()
        order_wow = calculate_growth_rate(total_orders, df_raw['weekly_order_gap'].sum())
        order_yoy = calculate_growth_rate(total_orders, df_raw['weekly_yoy_order_gap'].sum())
        
        total_cm3 = df_raw['CM3'].sum()
        cm3_wow = calculate_growth_rate(total_cm3, df_raw['weekly_cm3_gap'].sum())
        cm3_yoy = calculate_growth_rate(total_cm3, df_raw['weekly_yoy_cm3_gap'].sum())
        
        # 复刻模板：横向平铺的白底高级指标卡片阵列
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">本周总订单量</div>
                    <div class="kpi-value">{total_orders:,} <span style='font-size:14px; font-weight:normal;'>单</span></div>
                    <div class="kpi-desc">{get_trend_html(order_wow, "WoW")}</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">总订单量同比</div>
                    <div class="kpi-value">{total_orders:,} <span style='font-size:14px; font-weight:normal;'>单</span></div>
                    <div class="kpi-desc">{get_trend_html(order_yoy, "YoY")}</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">CM3 利润总额</div>
                    <div class="kpi-value">${total_cm3:,.2f}</div>
                    <div class="kpi-desc">{get_trend_html(cm3_wow, "WoW")}</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi_col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">CM3 利润同比</div>
                    <div class="kpi-value">${total_cm3:,.2f}</div>
                    <div class="kpi-desc">{get_trend_html(cm3_yoy, "YoY")}</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:30px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        # 单独区域阵列表格呈现
        st.markdown("<h3 style='margin-bottom:15px;'>📍 各个单独区域业绩阵列</h3>", unsafe_allow_html=True)
        region_agg = df_raw.groupby('Region').agg({
            'Orders': 'sum', 'weekly_order_gap': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_cm3_gap': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        region_agg['订单环比 (WoW)'] = region_agg.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_order_gap']):.1f}%", axis=1)
        region_agg['订单同比 (YoY)'] = region_agg.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap']):.1f}%", axis=1)
        region_agg['CM3利润'] = region_agg['CM3'].apply(lambda x: f"${x:,.2f}")
        region_disp = region_agg[['Region', 'Orders', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3利润']].sort_values('Orders', ascending=False)
        region_disp.columns = ['区域名称', '本周订单量', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3 利润总计']
        st.dataframe(region_disp, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # 标签页二：多维交叉明细探索 (含动态联动大卡片)
    # ------------------------------------------
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 顶部并排展示的干净筛选器
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sel_regions = st.multiselect("📍 选择筛选区域 (可多选):", options=sorted(df_raw['Region'].dropna().unique()))
        with f_col2:
            sel_staffs = st.multiselect("👤 选择负责 BD (可多选):", options=sorted(df_raw['Staff'].dropna().unique()))
        with f_col3:
            sel_cats = st.multiselect("🍔 选择商品品类 (可多选):", options=sorted(df_raw['Category'].dropna().unique()))
            
        # 过滤数据
        df_filtered = df_raw.copy()
        if sel_regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(sel_regions)]
        if sel_staffs:
            df_filtered = df_filtered[df_filtered['Staff'].isin(sel_staffs)]
        if sel_cats:
            df_filtered = df_filtered[df_filtered['Category'].isin(sel_cats)]
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:15px;'>📊 所选维度动态运营汇总</h3>", unsafe_allow_html=True)
        
        # 计算联动过滤指标
        f_orders = df_filtered['Orders'].sum()
        f_order_wow = calculate_growth_rate(f_orders, df_filtered['weekly_order_gap'].sum())
        f_order_yoy = calculate_growth_rate(f_orders, df_filtered['weekly_yoy_order_gap'].sum())
        
        f_cm3 = df_filtered['CM3'].sum()
        f_cm3_wow = calculate_growth_rate(f_cm3, df_filtered['weekly_cm3_gap'].sum())
        f_cm3_yoy = calculate_growth_rate(f_cm3, df_filtered['weekly_yoy_cm3_gap'].sum())
        
        # 渲染动态联动的顶部汇总卡片
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        with sum_col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">当前维度订单量</div>
                    <div class="kpi-value">{f_orders:,} <span style='font-size:14px; font-weight:normal;'>单</span></div>
                    <div class="kpi-desc">{get_trend_html(f_order_wow, "WoW")}</div>
                </div>
            """, unsafe_allow_html=True)
        with sum_col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">当前订单量同比</div>
                    <div class="kpi-value">{f_orders:,} <span style='font-size:14px; font-weight:normal;'>单</span></div>
                    <div class="kpi-desc">{get_trend_html(f_order_yoy, "YoY")}</div>
                </div>
            """, unsafe_allow_html=True)
        with sum_col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">当前维度 CM3 总计</div>
                    <div class="kpi-value">${f_cm3:,.2f}</div>
                    <div class="kpi-desc">{get_trend_html(f_cm3_wow, "WoW")}</div>
                </div>
            """, unsafe_allow_html=True)
        with sum_col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">当前 CM3 利润同比</div>
                    <div class="kpi-value">${f_cm3:,.2f}</div>
                    <div class="kpi-desc">{get_trend_html(f_cm3_yoy, "YoY")}</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:25px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        # 下方联动明细数据表
        st.markdown("<h3 style='margin-bottom:15px;'>📋 联动筛选结果明细表</h3>", unsafe_allow_html=True)
        df_filtered['Orders_Format'] = df_filtered['Orders'].apply(lambda x: f"{x:,}")
        df_filtered['CM3_Format'] = df_filtered['CM3'].apply(lambda x: f"${x:,.2f}")
        
        detail_cols = ['店铺名字', 'Region', 'Staff', 'Category', 'Orders_Format', 'CM3_Format']
        df_disp_detail = df_filtered[detail_cols].rename(columns={
            'Region': '所属区域', 'Staff': '负责人', 'Category': '品类', 'Orders_Format': '本周单量', 'CM3_Format': 'CM3利润'
        })
        st.dataframe(df_disp_detail, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # 标签页三：BD个人目标达成对齐
    # ------------------------------------------
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
            
            # 单量追踪计算
            daily_act = act['daily_avg']
            daily_tgt = tgt['order_tgt']
            o_rate = (daily_act / daily_tgt) * 100 if daily_tgt else 0
            o_diff = daily_act - daily_tgt
            o_sign = "+" if o_diff > 0 else ""
            
            order_rows.append({
                "BD负责人": name,
                "当前日均单量": f"{daily_act:,}",
                "日均单量目标": f"{daily_tgt:,}",
                "目标完成度": f"{o_rate:.1f}%",
                "目标差值": f"{o_sign}{o_diff:,}" if o_diff != 0 else "0"
            })
            
            # CM3 月度预测与对齐数
            mtd_cm3_val = act['mtd_cm3']
            est_month_cm3 = (mtd_cm3_val / 18) * 31
            cm3_tgt_val = tgt['cm3_tgt']
            c_rate = (est_month_cm3 / cm3_tgt_val) * 100 if cm3_tgt_val else 0
            c_diff = est_month_cm3 - cm3_tgt_val
            c_sign = "+" if c_diff > 0 else ""
            
            cm3_rows.append({
                "BD负责人": name,
                "本月预估 CM3 完成数": f"${est_month_cm3:,.2f}",
                "月度 CM3 目标值": f"${cm3_tgt_val:,.2f}",
                "目标完成度": f"{c_rate:.1f}%",
                "目标差值": f"{c_sign}${c_diff:,.2f}" if c_diff != 0 else "$0.00"
            })
            
        st.markdown("<h3 style='margin-bottom:15px;'>📋 表一：BD个人维度日均单量追踪</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)
        
        st.markdown("<hr style='margin:25px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='margin-bottom:15px;'>💰 表二：BD个人维度月度 CM3 预测对齐</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(cm3_rows), use_container_width=True, hide_index=True)
