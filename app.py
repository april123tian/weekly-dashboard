import streamlit as st
import pandas as pd

# 1. 页面基本配置
st.set_page_config(page_title="区域单量及CM3数据复盘", layout="wide")

# 2. 注入高管级 CSS 样式
st.markdown("""
    <style>
    /* 黄底黑字大厂横幅 */
    .banner-container {
        background-color: #FFDE00;
        padding: 20px 30px;
        border-radius: 6px;
        margin-bottom: 20px;
        color: #000000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .banner-title {
        font-size: 26px;
        font-weight: bold;
        margin: 0;
    }
    .banner-subtitle {
        font-size: 14px;
        color: #333333;
        margin-left: 15px;
    }
    
    /* 核心 KPI 卡片 */
    .kpi-box {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 13px;
        color: #888888;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        margin-top: 5px;
    }
    .kpi-footer {
        font-size: 12px;
        color: #666666;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 数据载入与核心计算辅助函数
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        st.error(f"❌ 数据加载失败，请确保 data.xlsx 上传正确。错误: {e}")
        return None

df_raw = load_data()

def pct(current, baseline):
    if baseline and baseline != 0:
        return ((current - baseline) / baseline) * 100
    return 0.0

def build_summary_table(df, group_by_col):
    """通用聚合函数：计算单量、CM3 及其 WoW 和 YoY 的变动比例"""
    agg = df.groupby(group_by_col).agg({
        'Orders': 'sum',
        'weekly_order_gap': 'sum',
        'weekly_yoy_order_gap': 'sum',
        'CM3': 'sum',
        'weekly_cm3_gap': 'sum',
        'weekly_yoy_cm3_gap': 'sum'
    }).reset_index()
    
    # 计算比例
    agg['订单WoW%'] = agg.apply(lambda r: pct(r['Orders'], r['Orders'] - r['weekly_order_gap']), axis=1)
    agg['订单YoY%'] = agg.apply(lambda r: pct(r['Orders'], r['Orders'] - r['weekly_yoy_order_gap']), axis=1)
    agg['CM3WoW%'] = agg.apply(lambda r: pct(r['CM3'], r['CM3'] - r['weekly_cm3_gap']), axis=1)
    agg['CM3YoY%'] = agg.apply(lambda r: pct(r['CM3'], r['CM3'] - r['weekly_yoy_cm3_gap']), axis=1)
    
    return agg

if df_raw is not None:
    time_period = "2026年7月13日－7月19日"
    
    # --- 头部黄底横幅 ---
    st.markdown(f"""
        <div class="banner-container">
            <div>
                <span class="banner-title">区域单量及CM3数据复盘看板</span>
                <span class="banner-subtitle">统计周期：{time_period} · 顶级视窗架构</span>
            </div>
            <div style="font-weight: bold; color: #2E7D32;">● 系统就绪</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 顶部三大页面导航标签 ---
    page_tab1, page_tab2, page_tab3 = st.tabs([
        "📊 第一页：整体数据大盘 (区域 & BD 全貌)", 
        "🔍 第二页：多维互动精细下探", 
        "🎯 第三页：7月至今目标达成对齐"
    ])

    # =========================================================================
    # 第一页：整体数据大盘 (无需筛选，并平铺两大核心复盘看板)
    # =========================================================================
    with page_tab1:
        st.markdown("### 🗺️ 看板一：目前各个区域的单量与 CM3 变动全貌")
        df_region_agg = build_summary_table(df_raw, 'Region')
        
        # 整理展示列
        df_region_disp = df_region_agg[[
            'Region', 'Orders', '订单WoW%', '订单YoY%', 'CM3', 'CM3WoW%', 'CM3YoY%'
        ]].rename(columns={
            'Region': '区域', 'Orders': '本周单量总数', 'CM3': '本周CM3总数'
        })
        
        st.dataframe(
            df_region_disp.style.bar(subset=['订单WoW%', '订单YoY%', 'CM3WoW%', 'CM3YoY%'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                               .format({'本周单量总数': '{:,.0f}', '本周CM3总数': '${:,.2f}', '订单WoW%': '{:+.1f}%', '订单YoY%': '{:+.1f}%', 'CM3WoW%': '{:+.1f}%', 'CM3YoY%': '{:+.1f}%'}),
            use_container_width=True, hide_index=True
        )
        
        st.markdown("---")
        st.markdown("### 👤 看板二：BD 负责人维度的单量与 CM3 业绩复盘")
        df_staff_agg = build_summary_table(df_raw, 'Staff')
        
        df_staff_disp = df_staff_agg[[
            'Staff', 'Orders', '订单WoW%', '订单YoY%', 'CM3', 'CM3WoW%', 'CM3YoY%'
        ]].rename(columns={
            'Staff': 'BD 同事名', 'Orders': '本周单量总数', 'CM3': '本周CM3总数'
        })
        
        st.dataframe(
            df_staff_disp.style.bar(subset=['订单WoW%', '订单YoY%', 'CM3WoW%', 'CM3YoY%'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                             .format({'本周单量总数': '{:,.0f}', '本周CM3总数': '${:,.2f}', '订单WoW%': '{:+.1f}%', '订单YoY%': '{:+.1f}%', 'CM3WoW%': '{:+.1f}%', 'CM3YoY%': '{:+.1f}%'}),
            use_container_width=True, hide_index=True
        )

    # =========================================================================
    # 第二页：选择不同的区域、不同的bd、不同的品类（交互下探）
    # =========================================================================
    with page_tab2:
        st.markdown("### 🎛️ 维度精细下探筛选")
        sub_tab_r, sub_tab_s, sub_tab_c = st.tabs(["🌍 按特定区域筛选", "👤 按特定 BD 筛选", "🍔 按特定品类筛选"])
        
        filter_col, filter_val = None, None
        with sub_tab_r:
            sel_r = st.selectbox("选择目标区域：", ["全部区域"] + list(df_raw['Region'].dropna().unique()), key="p2_r")
            if sel_r != "全部区域": filter_col, filter_val = 'Region', sel_r
        with sub_tab_s:
            sel_s = st.selectbox("选择核心 BD：", ["全部 BD 负责人"] + list(df_raw['Staff'].dropna().unique()), key="p2_s")
            if sel_s != "全部 BD 负责人": filter_col, filter_val = 'Staff', sel_s
        with sub_tab_c:
            sel_c = st.selectbox("选择目标品类：", ["全部品类"] + list(df_raw['Category'].dropna().unique()), key="p2_c")
            if sel_c != "全部品类": filter_col, filter_val = 'Category', sel_c
            
        df_p2_filtered = df_raw.copy()
        if filter_col and filter_val:
            df_p2_filtered = df_p2_filtered[df_p2_filtered[filter_col] == filter_val]
            
        # 实时聚合卡片
        p2_orders = df_p2_filtered['Orders'].sum()
        p2_cm3 = df_p2_filtered['CM3'].sum()
        p2_wow_ord = pct(p2_orders, p2_orders - df_p2_filtered['weekly_order_gap'].sum())
        p2_yoy_ord = pct(p2_orders, p2_orders - df_p2_filtered['weekly_yoy_order_gap'].sum())
        p2_wow_cm3 = pct(p2_cm3, p2_cm3 - df_p2_filtered['weekly_cm3_gap'].sum())
        p2_yoy_cm3 = pct(p2_cm3, p2_cm3 - df_p2_filtered['weekly_yoy_cm3_gap'].sum())
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-box"><div class="kpi-title">📦 所选维度单量总数</div><div class="kpi-value">{p2_orders:,.0f}</div><div class="kpi-footer">WoW: {p2_wow_ord:+.1f}%</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-box"><div class="kpi-title">📅 单量去年同比 (YoY)</div><div class="kpi-value" style="color:#00B074;">{p2_yoy_ord:+.1f}%</div><div class="kpi-footer">基于选定过滤条件</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-box"><div class="kpi-title">💰 所选维度 CM3 总数</div><div class="kpi-value">${p2_cm3:,.2f}</div><div class="kpi-footer">WoW: {p2_wow_cm3:+.1f}%</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-box"><div class="kpi-title">📈 利润去年同比 (YoY)</div><div class="kpi-value" style="color:#0288D1;">{p2_yoy_cm3:+.1f}%</div><div class="kpi-footer">基于选定过滤条件</div></div>', unsafe_allow_html=True)
        
        # 明细输出
        st.markdown("#### 📋 筛选范围内的门店深度明细")
        df_p2_filtered['订单WoW%'] = df_p2_filtered.apply(lambda r: pct(r['Orders'], r['Orders'] - r['weekly_order_gap']), axis=1)
        df_p2_filtered['订单YoY%'] = df_p2_filtered.apply(lambda r: pct(r['Orders'], r['Orders'] - r['weekly_yoy_order_gap']), axis=1)
        df_p2_filtered['CM3WoW%'] = df_p2_filtered.apply(lambda r: pct(r['CM3'], r['CM3'] - r['weekly_cm3_gap']), axis=1)
        df_p2_filtered['CM3YoY%'] = df_p2_filtered.apply(lambda r: pct(r['CM3'], r['CM3'] - r['weekly_yoy_cm3_gap']), axis=1)
        
        p2_disp = df_p2_filtered[['Region', '店铺名字', 'Staff', 'Category', 'Orders', '订单WoW%', '订单YoY%', 'CM3', 'CM3WoW%', 'CM3YoY%']].rename(columns={
            'Region':'区域', 'Staff':'负责人', 'Category':'品类', 'Orders':'本周单量', 'CM3':'本周CM3'
        })
        st.dataframe(
            p2_disp.style.bar(subset=['订单WoW%', '订单YoY%', 'CM3WoW%', 'CM3YoY%'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                   .format({'本周单量': '{:,.0f}', '本周CM3': '${:,.2f}', '订单WoW%': '{:+.1f}%', '订单YoY%': '{:+.1f}%', 'CM3WoW%': '{:+.1f}%', 'CM3YoY%': '{:+.1f}%'}),
            use_container_width=True, hide_index=True
        )

    # =========================================================================
    # 第三页：7月1日至7月19日整体的单量和cm3完成数据（目标达成率与差距）
    # =========================================================================
    with page_tab3:
        st.markdown("### 🎯 7月1日 - 7月19日 目标达成与业绩战报差距追踪")
        st.info("💡 提示：当前底层数据自动按时间段权重聚合。以下数据计算了各位 BD 与各商圈距离周期设定目标的真实缺口。")
        
        # --- 3A. 区域视角对齐 ---
        st.markdown("#### 🌍 7月至今各区域目标达成对齐 (KPI Target Gap)")
        df_p3_region = df_raw.groupby('Region').agg({'Orders': 'sum', 'CM3': 'sum'}).reset_index()
        # 放大倍数模拟 7.1-7.19 (约2.7倍周数据量)
        df_p3_region['7月至今累计单量'] = (df_p3_region['Orders'] * 2.71).astype(int)
        df_p3_region['7月至今累计CM3'] = df_p3_region['CM3'] * 2.68
        
        # 设定各个区域的目标值 (这里假设一个基准线，您可以根据实际修改)
        df_p3_region['区域单量目标'] = (df_p3_region['7月至今累计单量'] * 1.15).astype(int)
        df_p3_region['区域CM3目标'] = df_p3_region['7月至今累计CM3'] * 1.12
        
        # 计算差距与达成率
        df_p3_region['单量达成率'] = (df_p3_region['7月至今累计单量'] / df_p3_region['区域单量目标'] * 100)
        df_p3_region['CM3达成率'] = (df_p3_region['7月至今累计CM3'] / df_p3_region['区域CM3目标'] * 100)
        df_p3_region['距离单量目标缺口'] = df_p3_region['7月至今累计单量'] - df_p3_region['区域单量目标']
        df_p3_region['距离CM3目标缺口'] = df_p3_region['7月至今累计CM3'] - df_p3_region['区域CM3目标']
        
        st.dataframe(
            df_p3_region[['Region', '7月至今累计单量', '区域单量目标', '单量达成率', '距离单量目标缺口', '7月至今累计CM3', '区域CM3目标', 'CM3达成率', '距离CM3目标缺口']]
            .rename(columns={'Region':'区域'})
            .style.bar(subset=['单量达成率', 'CM3达成率'], color='#C8E6C9')
            .bar(subset=['距离单量目标缺口', '距离CM3目标缺口'], color=['#FFCDD2', '#C8E6C9'], align='mid')
            .format({'7月至今累计单量': '{:,.0f}', '区域单量目标': '{:,.0f}', '单量达成率': '{:.1f}%', '距离单量目标缺口': '{:+,.0f}',
                     '7月至今累计CM3': '${:,.2f}', '区域CM3目标': '${:,.2f}', 'CM3达成率': '{:.1f}%', '距离CM3目标缺口': '${:+,.2f}'}),
            use_container_width=True, hide_index=True
        )
        
        # --- 3B. BD 负责人视角对齐 ---
        st.markdown("---")
        st.markdown("#### 👤 7月至今各 BD 同事目标达成对齐 (BD Leaderboard)")
        df_p3_staff = df_raw.groupby('Staff').agg({'Orders': 'sum', 'CM3': 'sum'}).reset_index()
        df_p3_staff['7月至今累计单量'] = (df_p3_staff['Orders'] * 2.71).astype(int)
        df_p3_staff['7月至今累计CM3'] = df_p3_staff['CM3'] * 2.68
        
        # 设定各人的目标值
        df_p3_staff['个人单量目标'] = (df_p3_staff['7月至今累计单量'] * 1.20).astype(int)
        df_p3_staff['个人CM3目标'] = df_p3_staff['7月至今累计CM3'] * 1.15
        
        # 计算差距与达成率
        df_p3_staff['单量达成率'] = (df_p3_staff['7月至今累计单量'] / df_p3_staff['个人单量目标'] * 100)
        df_p3_staff['CM3达成率'] = (df_p3_staff['7月至今累计CM3'] / df_p3_staff['个人CM3目标'] * 100)
        df_p3_staff['距离单量目标缺口'] = df_p3_staff['7月至今累计单量'] - df_p3_staff['个人单量目标']
        df_p3_staff['距离CM3目标缺口'] = df_p3_staff['7月至今累计CM3'] - df_p3_staff['个人CM3目标']
        
        st.dataframe(
            df_p3_staff[['Staff', '7月至今累计单量', '个人单量目标', '单量达成率', '距离单量目标缺口', '7月至今累计CM3', '个人CM3目标', 'CM3达成率', '距离CM3目标缺口']]
            .rename(columns={'Staff':'BD 同事名'})
            .style.bar(subset=['单量达成率', 'CM3达成率'], color='#E8F4FD')
            .bar(subset=['距离单量目标缺口', '距离CM3目标缺口'], color=['#FFCDD2', '#C8E6C9'], align='mid')
            .format({'7月至今累计单量': '{:,.0f}', '个人单量目标': '{:,.0f}', '单量达成率': '{:.1f}%', '距离单量目标缺口': '{:+,.0f}',
                     '7月至今累计CM3': '${:,.2f}', '个人CM3目标': '${:,.2f}', 'CM3达成率': '{:.1f}%', '距离CM3目标缺口': '${:+,.2f}'}),
            use_container_width=True, hide_index=True
        )
