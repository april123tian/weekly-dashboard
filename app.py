import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色高对比度、行政看板风格)
# ==========================================
st.set_page_config(
    page_title="悉尼BD 单量&CM3数据周报看板",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入 CSS 样式
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f5f7 !important;
        color: #1a252c !important;
    }
    .header-bar {
        background-color: #FFDE00;
        padding: 24px;
        border-radius: 6px;
        margin-bottom: 25px;
        color: #1a252c !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown {
        color: #1a252c !important;
    }
    
    /* Tabs 样式 */
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px !important;
        background-color: transparent !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        color: #64748b !important; 
        border: 1px solid #e2e8f0 !important;
        border-radius: 20px !important; 
        padding: 8px 24px !important;
        height: auto !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important; 
        color: #1a252c !important;           
        font-weight: 700 !important;           
        border: 2px solid #1a252c !important;  
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important; 
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8f9fa !important;
        color: #1a252c !important;
        border-color: #cbd5e1 !important;
    }

    /* KPI 卡片 */
    .kpi-card {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #eef0f2;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 15px;
        min-height: 130px;
    }
    .kpi-title {
        color: #6c757d !important;
        font-size: 14px !important;
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
        font-size: 13px !important;
    }
    .trend-up {
        color: #28a745 !important;
        font-weight: bold;
    }
    .trend-down {
        color: #dc3545 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h1 style='margin:0; font-size: 26px; font-weight:700;'>悉尼BD 单量&CM3数据周报看板</h1>
        <p style='margin:6px 0 0 0; opacity: 0.8; font-size: 13px;'>统计周期：2026年7月13日－7月19日（周一至周日） · 统计口径：跟进人提交时间</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. 计算通用工具函数
# ==========================================
def calculate_growth_rate(current, gap):
    baseline = current - gap
    if pd.isna(baseline) or baseline == 0:
        return 0.0
    return (gap / baseline) * 100

def get_trend_html(val, label_suffix=""):
    if pd.isna(val):
        return "<span style='color:#8c96a0;'>-</span>"
    if val > 0:
        return f"<span class='trend-up'>▲ +{val:.1f}%</span> <span style='color:#8c96a0; font-size:12px;'>{label_suffix}</span>"
    elif val < 0:
        return f"<span class='trend-down'>▼ -{abs(val):.1f}%</span> <span style='color:#8c96a0; font-size:12px;'>{label_suffix}</span>"
    return f"<span style='color:#1a252c;'>{val:.1f}%</span> <span style='color:#8c96a0; font-size:12px;'>{label_suffix}</span>"

def get_pure_trend_value_html(val):
    if pd.isna(val):
        return "-"
    if val > 0:
        return f"<span class='trend-up'>+{val:.1f}%</span>"
    elif val < 0:
        return f"<span class='trend-down'>-{abs(val):.1f}%</span>"
    return f"<span>{val:.1f}%</span>"

# ==========================================
# 2. 数据处理与引擎加载
# ==========================================
@st.cache_data
def load_and_process_perf_data():
    df = pd.read_excel('data.xlsx')
    return df

try:
    df_raw = load_and_process_perf_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ 无法读取 data.xlsx，错误详情: {e}")
    data_loaded = False

if data_loaded:
    
    tab1, tab2, tab3 = st.tabs(["📊 整体数据复盘看板", "🔍 多维交叉明细探索", "🎯 BD个人目标达成对齐"])

    # ------------------------------------------
    # 标签页一：整体数据复盘看板
    # ------------------------------------------
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:15px;'>🌐 全盘核心运营总览</h3>", unsafe_allow_html=True)
        
        total_orders = df_raw['Orders'].sum()
        order_wow = calculate_growth_rate(total_orders, df_raw['weekly_order_gap'].sum())
        order_yoy = calculate_growth_rate(total_orders, df_raw['weekly_yoy_order_gap'].sum())
        
        total_cm3 = df_raw['CM3'].sum()
        cm3_wow = calculate_growth_rate(total_cm3, df_raw['weekly_cm3_gap'].sum())
        cm3_yoy = calculate_growth_rate(total_cm3, df_raw['weekly_yoy_cm3_gap'].sum())
        
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
                    <div class="kpi-title">总订单量同比 (YoY)</div>
                    <div class="kpi-value">{get_pure_trend_value_html(order_yoy)}</div>
                    <div class="kpi-desc" style='color:#8c96a0;'>对比去年同期增减幅</div>
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
                    <div class="kpi-title">CM3 利润同比 (YoY)</div>
                    <div class="kpi-value">{get_pure_trend_value_html(cm3_yoy)}</div>
                    <div class="kpi-desc" style='color:#8c96a0;'>对比去年同期增减幅</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:30px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        # 区域阵列
        st.markdown("<h3 style='margin-bottom:15px;'>📍 各个单独区域业绩阵列</h3>", unsafe_allow_html=True)
        region_agg = df_raw.groupby('Region').agg({
            'Orders': 'sum', 'weekly_order_gap': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_cm3_gap': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        region_agg['订单环比 (WoW)'] = region_agg.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_order_gap']):.1f}%", axis=1)
        region_agg['订单同比 (YoY)'] = region_agg.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap']):.1f}%", axis=1)
        region_agg['CM3 利润总计'] = region_agg['CM3'].apply(lambda x: f"${x:,.2f}")
        region_agg['CM3 同比 (YoY)'] = region_agg.apply(lambda r: f"{calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap']):.1f}%", axis=1)
        
        region_disp = region_agg.sort_values('Orders', ascending=False)
        region_disp = region_disp[['Region', 'Orders', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3 利润总计', 'CM3 同比 (YoY)']]
        region_disp.columns = ['区域名称', '本周订单量', '订单环比 (WoW)', '订单同比 (YoY)', 'CM3 利润总计', 'CM3 同比趋势 (YoY)']
        st.dataframe(region_disp, use_container_width=True, hide_index=True)

        st.markdown("<hr style='margin:30px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

        # BD大表
        st.markdown("<h3 style='margin-bottom:15px;'>👤 表三：BD 个人全维综合战报 (单量 & CM3 & YoY)</h3>", unsafe_allow_html=True)
        bd_agg = df_raw.groupby('Staff').agg({
            'Orders': 'sum', 'weekly_yoy_order_gap': 'sum',
            'CM3': 'sum', 'weekly_yoy_cm3_gap': 'sum'
        }).reset_index()
        
        bd_agg['订单同比 (YoY)'] = bd_agg.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap']):.1f}%", axis=1)
        bd_agg['CM3 同比 (YoY)'] = bd_agg.apply(lambda r: f"{calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap']):.1f}%", axis=1)
        bd_agg['本周总单量'] = bd_agg['Orders'].apply(lambda x: f"{x:,}")
        bd_agg['CM3 利润完成数'] = bd_agg['CM3'].apply(lambda x: f"${x:,.2f}")
        
        bd_sorted = bd_agg.sort_values('Orders', ascending=False)
        bd_disp = bd_sorted[['Staff', '本周总单量', '订单同比 (YoY)', 'CM3 利润完成数', 'CM3 同比 (YoY)']]
        bd_disp.columns = ['BD 负责人', '本周总单量', '订单同比 (YoY)', 'CM3 利润完成总额', 'CM3 利润同比 (YoY)']
        st.dataframe(bd_disp, use_container_width=True, hide_index=True)


    # ------------------------------------------
    # 标签页二：多维交叉明细探索
    # ------------------------------------------
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sel_regions = st.multiselect("📍 选择筛选区域 (可多选):", options=sorted(df_raw['Region'].dropna().unique()), key="sel_reg")
        with f_col2:
            sel_staffs = st.multiselect("👤 选择负责 BD (可多选):", options=sorted(df_raw['Staff'].dropna().unique()), key="sel_staff")
        with f_col3:
            sel_cats = st.multiselect("🍔 选择商品品类 (可多选):", options=sorted(df_raw['Category'].dropna().unique()), key="sel_cat")
            
        df_filtered = df_raw.copy()
        if sel_regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(sel_regions)]
        if sel_staffs:
            df_filtered = df_filtered[df_filtered['Staff'].isin(sel_staffs)]
        if sel_cats:
            df_filtered = df_filtered[df_filtered['Category'].isin(sel_cats)]
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:15px;'>📊 所选维度动态运营汇总</h3>", unsafe_allow_html=True)
        
        f_orders = df_filtered['Orders'].sum()
        f_order_wow = calculate_growth_rate(f_orders, df_filtered['weekly_order_gap'].sum())
        f_order_yoy = calculate_growth_rate(f_orders, df_filtered['weekly_yoy_order_gap'].sum())
        
        f_cm3 = df_filtered['CM3'].sum()
        f_cm3_wow = calculate_growth_rate(f_cm3, df_filtered['weekly_cm3_gap'].sum())
        f_cm3_yoy = calculate_growth_rate(f_cm3, df_filtered['weekly_yoy_cm3_gap'].sum())
        
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
                    <div class="kpi-title">当前订单量同比 (YoY)</div>
                    <div class="kpi-value">{get_pure_trend_value_html(f_order_yoy)}</div>
                    <div class="kpi-desc" style='color:#8c96a0;'>所选维度同比增减幅</div>
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
                    <div class="kpi-title">当前 CM3 利润同比 (YoY)</div>
                    <div class="kpi-value">{get_pure_trend_value_html(f_cm3_yoy)}</div>
                    <div class="kpi-desc" style='color:#8c96a0;'>所选维度同比增减幅</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:25px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

        # 🍔 品类战报看板 (已修复顺序错乱 bug)
        st.markdown("<h3 style='margin-bottom:15px;'>🍔 核心品类业绩战报（已过滤日均单量 ≤ 30单的细分品类）</h3>", unsafe_allow_html=True)
        if not df_filtered.empty:
            cat_agg = df_filtered.groupby('Category').agg({
                'Orders': 'sum', 'weekly_yoy_order_gap': 'sum',
                'CM3': 'sum', 'weekly_yoy_cm3_gap': 'sum'
            }).reset_index()
            
            # 关键过滤：日均 > 30单 (周总量 > 210单)
            cat_agg_filtered = cat_agg[cat_agg['Orders'] > 210].copy()
            
            if not cat_agg_filtered.empty:
                cat_agg_filtered['订单同比 (YoY) 趋势'] = cat_agg_filtered.apply(lambda r: f"{calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap']):+.1f}%", axis=1)
                cat_agg_filtered['CM3 利润同比 (YoY) 趋势'] = cat_agg_filtered.apply(lambda r: f"{calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap']):+.1f}%", axis=1)
                cat_agg_filtered['本周单量完成数'] = cat_agg_filtered['Orders'].apply(lambda x: f"{x:,}")
                cat_agg_filtered['CM3利润完成额'] = cat_agg_filtered['CM3'].apply(lambda x: f"${x:,.2f}")
                
                # 正确的列处理顺序：先排序，再选出指定老列并规范好显示顺序
                cat_disp = cat_agg_filtered.sort_values('Orders', ascending=False)
                cat_disp = cat_disp[['Category', '本周单量完成数', '订单同比 (YoY) 趋势', 'CM3利润完成额', 'CM3 利润同比 (YoY) 趋势']]
                
                # 最后做展现层的重命名映射
                cat_disp.columns = ['品类名称', '本周单量', '订单同比 (YoY) 趋势', 'CM3 利润', 'CM3 利润同比 (YoY) 趋势']
                st.dataframe(cat_disp, use_container_width=True, hide_index=True)
            else:
                st.info("💡 当前筛选范围内，没有任何一个品类的日均订单量能够超过 30 单。")
        else:
            st.info("💡 当前筛选条件下没有品类数据。")

        st.markdown("<hr style='margin:25px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        # 联动筛选结果明细表
        st.markdown("<h3 style='margin-bottom:15px;'>📋 联动筛选结果明细表 (含 YoY 趋势)</h3>", unsafe_allow_html=True)
        
        df_filtered['单量 YoY'] = df_filtered.apply(lambda r: calculate_growth_rate(r['Orders'], r['weekly_yoy_order_gap']), axis=1)
        df_filtered['CM3 YoY'] = df_filtered.apply(lambda r: calculate_growth_rate(r['CM3'], r['weekly_yoy_cm3_gap']), axis=1)
        
        df_filtered['单量 YoY_Format'] = df_filtered['单量 YoY'].apply(lambda x: f"{x:+.1f}%")
        df_filtered['CM3 YoY_Format'] = df_filtered['CM3 YoY'].apply(lambda x: f"{x:+.1f}%")
        df_filtered['Orders_Format'] = df_filtered['Orders'].apply(lambda x: f"{x:,}")
        df_filtered['CM3_Format'] = df_filtered['CM3'].apply(lambda x: f"${x:,.2f}")
        
        detail_cols = ['店铺名字', 'Region', 'Staff', 'Category', 'Orders_Format', '单量 YoY_Format', 'CM3_Format', 'CM3 YoY_Format']
        df_disp_detail = df_filtered[detail_cols].rename(columns={
            'Region': '所属区域', 'Staff': '负责人', 'Category': '品类', 'Orders_Format': '本周单量',
            '单量 YoY_Format': '单量 YoY 趋势', 'CM3_Format': 'CM3利润', 'CM3 YoY_Format': 'CM3 YoY 趋势'
        })
        st.dataframe(df_disp_detail, use_container_width=True, hide_index=True)

        st.markdown("<hr style='margin:25px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

        # 🚨 业务漏斗预警
        st.markdown("<h3 style='color:#dc3545 !important; margin-bottom:15px;'>🚨 业务漏斗预警：当前筛选下 YoY 同比下滑最严重店铺 Top 10（过滤日均 ≤ 10单小店）</h3>", unsafe_allow_html=True)
        
        df_high_vol = df_filtered[df_filtered['Orders'] > 70].copy()
        
        if not df_high_vol.empty:
            df_top_drop = df_high_vol.sort_values(by='单量 YoY', ascending=True).head(10)
            
            drop_cols = ['店铺名字', 'Region', 'Staff', 'Orders_Format', '单量 YoY_Format', 'CM3_Format', 'CM3 YoY_Format']
            df_disp_drop = df_top_drop[drop_cols].rename(columns={
                'Region': '所属区域', 'Staff': '负责人', 'Orders_Format': '本周单量',
                '单量 YoY_Format': '单量同比下滑幅', 'CM3_Format': 'CM3利润', 'CM3同比下滑幅': 'CM3同比下滑幅'
            })
            st.dataframe(df_disp_drop, use_container_width=True, hide_index=True)
        else:
            st.info("💡 当前筛选维度下，没有日均单量大于 10 单的店铺。")

   # ------------------------------------------
    # 标签页三：BD个人目标达成对齐 (CM3数据已精准更新)
    # ------------------------------------------
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 已更新修正数据的 actual_perf
        actual_perf = {
            'Yuan Dong': {'daily_avg': 2332, 'mtd_cm3': 132357},
            '时晨': {'daily_avg': 1616, 'mtd_cm3': 152273},
            'Terry Meng': {'daily_avg': 1340, 'mtd_cm3': 127075},
            'Qichong Wang': {'daily_avg': 804, 'mtd_cm3': 50940},
            'Mabel Wang': {'daily_avg': 1572, 'mtd_cm3': 266733},  # 已更新
            '田雨卿': {'daily_avg': 1543, 'mtd_cm3': 254767},     # 已更新
            '张宇庭': {'daily_avg': 1650, 'mtd_cm3': 283552},     # 已更新
            '覃念慈': {'daily_avg': 1397, 'mtd_cm3': 229803},     # 已更新
            '李晓彤': {'daily_avg': 1600, 'mtd_cm3': 232436},     # 已更新
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

        def color_rate(val_str):
            try:
                rate = float(str(val_str).strip('%'))
                if rate >= 90: return 'color: #28a745; font-weight: bold;'
                if rate < 70: return 'color: #dc3545; font-weight: bold;'
                return 'color: #1a252c;'
            except:
                return 'color: #1a252c;'

        order_data, cm3_data = [], []
        for name, tgt in target_perf.items():
            act = actual_perf.get(name, {'daily_avg': 0, 'mtd_cm3': 0})
            
            # 单量计算
            o_rate = (act['daily_avg'] / tgt['order_tgt']) * 100
            o_diff = act['daily_avg'] - tgt['order_tgt']
            order_data.append({"BD负责人": name, "当前日均": f"{act['daily_avg']:,}", "目标值": f"{tgt['order_tgt']:,}", "完成度": f"{o_rate:.1f}%", "缺口/盈余": f"{o_diff:+,}"})
            
            # CM3计算 (基于修正后的数据)
            est_cm3 = (act['mtd_cm3'] / 19) * 31
            c_rate = (est_cm3 / tgt['cm3_tgt']) * 100
            c_diff = est_cm3 - tgt['cm3_tgt']
            cm3_data.append({"BD负责人": name, "本月预估": f"${est_cm3:,.0f}", "目标值": f"${tgt['cm3_tgt']:,}", "完成度": f"{c_rate:.1f}%", "缺口/盈余": f"${c_diff:,.0f}"})

        st.markdown("### 📋 BD个人维度日均单量追踪")
        st.dataframe(pd.DataFrame(order_data).style.map(color_rate, subset=['完成度']), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 💰 BD个人维度月度 CM3 预测对齐")
        st.dataframe(pd.DataFrame(cm3_data).style.map(color_rate, subset=['完成度']), use_container_width=True, hide_index=True)
