import streamlit as st
import pandas as pd

# 1. 页面基本配置
st.set_page_config(page_title="BD 招商业绩周报看板", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS 样式，让看板更有现代商业感
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        color: #1E1E1E;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 数据载入
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        st.error(f"❌ 数据加载失败，请确保 data.xlsx 上传正确。错误: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # 动态周期标题
    time_period = df_raw['Date'].iloc[0] if 'Date' in df_raw.columns and not df_raw.empty else "未知周期"
    
    st.title("🎯 BD 招商周报核心业绩看板")
    st.markdown(f"🗓️ **当前周报统计周期**：`{time_period}`")
    st.markdown("---")

    # --- 3. 侧边栏高级筛选 ---
    st.sidebar.header("🔍 核心维度筛选")
    
    regions = ["🌍 全部区域"] + list(df_raw['Region'].dropna().unique())
    selected_region = st.sidebar.selectbox("所属区域 (Region)", regions)
    
    categories = ["🍔 全部品类"] + list(df_raw['Category'].dropna().unique())
    selected_category = st.sidebar.selectbox("商户品类 (Category)", categories)
    
    staffs = ["👤 全部负责人"] + list(df_raw['Staff'].dropna().unique())
    selected_staff = st.sidebar.selectbox("BD 负责人 (Staff)", staffs)
    
    # 过滤数据
    df_filtered = df_raw.copy()
    if selected_region != "🌍 全部区域":
        df_filtered = df_filtered[df_filtered['Region'] == selected_region]
    if selected_category != "🍔 全部品类":
        df_filtered = df_filtered[df_filtered['Category'] == selected_category]
    if selected_staff != "👤 全部负责人":
        df_filtered = df_filtered[df_filtered['Staff'] == selected_staff]

    # --- 4. 核心指标数据计算 ---
    cw_orders = df_filtered['Orders'].sum()
    cw_cm3 = df_filtered['CM3'].sum()
    
    # 倒推历史基准
    lw_orders = cw_orders - df_filtered['weekly_order_gap'].sum()
    lw_cm3 = cw_cm3 - df_filtered['weekly_cm3_gap'].sum()
    w2_orders = df_filtered['上上周单量'].sum() if '上上周单量' in df_filtered.columns else 0
    w2_cm3 = df_filtered['上上周cm3'].sum() if '上上周cm3' in df_filtered.columns else 0
    yoy_orders = df_filtered['去年上周单量'].sum() if '去年上周单量' in df_filtered.columns else 0
    yoy_cm3 = df_filtered['去年上周cm3'].sum() if '去年上周cm3' in df_filtered.columns else 0

    def pct(current, baseline):
        if baseline and baseline != 0:
            return ((current - baseline) / baseline) * 100
        return 0.0

    # 计算变动率
    wow_ord, wow2_ord, yoy_ord = pct(cw_orders, lw_orders), pct(cw_orders, w2_orders), pct(cw_orders, yoy_orders)
    wow_cm3, wow2_cm3, yoy_cm3_pct = pct(cw_cm3, lw_cm3), pct(cw_cm3, w2_cm3), pct(cw_cm3, yoy_cm3)

    # --- 5. 顶层大指标大卡片 (Executive Summary) ---
    st.markdown('<div class="section-title">🚀 核心业绩指标概览</div>', unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("""
            <div style='background-color: #EDF7ED; padding: 15px; border-radius: 8px; border-left: 5px solid #2E7D32;'>
                <p style='margin:0; font-size:14px; color:#1E4620; font-weight:bold;'>📦 核心单量大盘 (Orders)</p>
                <h1 style='margin:5px 0 0 0; color:#1E7D32;'>{cw_orders:,.0f} <span style='font-size:16px; font-weight:normal;'>单</span></h1>
            </div>
        """.format(cw_orders=cw_orders), unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("环比上周 (WoW)", f"{wow_ord:+.1f}%", f"{df_filtered['weekly_order_gap'].sum():+,.0f} 单")
        c2.metric("对比上上周 (WoW2)", f"{wow2_ord:+.1f}%")
        c3.metric("同比去年 (YoY)", f"{yoy_ord:+.1f}%")
        
    with m_col2:
        st.markdown("""
            <div style='background-color: #E8F4FD; padding: 15px; border-radius: 8px; border-left: 5px solid #0288D1;'>
                <p style='margin:0; font-size:14px; color:#014361; font-weight:bold;'>💰 核心利润大盘 (CM3)</p>
                <h1 style='margin:5px 0 0 0; color:#0288D1;'>${cw_cm3:,.2f}</h1>
            </div>
        """.format(cw_cm3=cw_cm3), unsafe_allow_html=True)
        
        c4, c5, c6 = st.columns(3)
        c4.metric("环比上周 (WoW)", f"{wow_cm3:+.1f}%", f"${df_filtered['weekly_cm3_gap'].sum():+,.2f}")
        c5.metric("对比上上周 (WoW2)", f"{wow2_cm3:+.1f}%")
        c6.metric("同比去年 (YoY)", f"{yoy_cm3_pct:+.1f}%")

    # --- 6. 周会抓手：BD 负责人与商圈排行榜 ---
    st.markdown("---")
    st.markdown('<div class="section-title">🏆 周会管理抓手（业绩与缺口分析）</div>', unsafe_allow_html=True)
    
    rank_col1, rank_col2 = st.columns(2)
    
    with rank_col1:
        st.subheader("👤 BD 团队单量贡献排行")
        # 聚合BD负责人数据
        df_staff = df_filtered.groupby('Staff')[['Orders', 'weekly_order_gap']].sum().sort_values(by='Orders', ascending=False)
        df_staff.columns = ['本周单量', '较上周增减']
        st.dataframe(df_staff.style.bar(subset=['本周单量'], color='#C8E6C9')
                                   .bar(subset=['较上周增减'], color=['#FFCDD2', '#C8E6C9'], align='mid'), 
                     use_container_width=True)
                     
    with rank_col2:
        st.subheader("🌍 商圈 / 区域单量表现")
        df_region = df_filtered.groupby('Region')[['Orders', 'weekly_order_gap']].sum().sort_values(by='Orders', ascending=False)
        df_region.columns = ['本周单量', '较上周增减']
        st.dataframe(df_region.style.bar(subset=['本周单量'], color='#B3E5FC')
                                    .bar(subset=['较上周增减'], color=['#FFCDD2', '#C8E6C9'], align='mid'), 
                     use_container_width=True)

    # --- 7. 精细化下探：商户明细诊断表 ---
    st.markdown("---")
    st.markdown('<div class="section-title">🏪 门店穿透诊断明细 (Merchant Level)</div>', unsafe_allow_html=True)
    st.markdown("> *开会时可以直接利用此表定位具体是哪家门店单量或者利润出现了大幅下跌（红色条长短代表拉胯程度）*")
    
    # 筛选展示用列
    display_cols = ['Region', '店铺名字', 'Staff', 'Category', 'Orders', 'CM3', 'weekly_order_gap', 'weekly_cm3_gap']
    df_merchants = df_filtered[display_cols].copy()
    df_merchants.columns = ['区域', '店铺名字', '负责人', '品类', '本周单量', '本周CM3', '单量环比差额', 'CM3环比差额']
    
    # 使用 Streamlit 高级样式，为差额字段增加进度条背景，负数显示红色，正数显示绿色
    st.dataframe(
        df_merchants.style.bar(subset=['单量环比差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                          .bar(subset=['CM3环比差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                          .format({'本周CM3': '${:,.2f}', 'CM3环比差额': '${:,.2f}', '本周单量': '{:,.0f}', '单量环比差额': '{:+,.0f}'}),
        use_container_width=True,
        hide_index=True
    )
