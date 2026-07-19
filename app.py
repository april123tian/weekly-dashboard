import streamlit as st
import pandas as pd

# 1. 页面基本配置
st.set_page_config(page_title="区域单量及CM3数据复盘", layout="wide")

# 2. 注入精美的大厂风横幅与 KPI 卡片 CSS 样式
st.markdown("""
    <style>
    /* 黄底黑字横幅样式 */
    .banner-container {
        background-color: #FFDE00;
        padding: 20px 30px;
        border-radius: 6px;
        margin-bottom: 25px;
        color: #000000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .banner-title {
        font-size: 26px;
        font-weight: bold;
        margin: 0;
        display: inline-block;
    }
    .banner-subtitle {
        font-size: 14px;
        color: #333333;
        margin-left: 15px;
        display: inline-block;
    }
    .status-dot {
        font-size: 14px;
        font-weight: 500;
    }
    
    /* 核心业绩 KPI 白底阴影卡片 */
    .kpi-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        min-height: 140px;
    }
    .kpi-title {
        font-size: 14px;
        color: #888888;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .kpi-footer {
        font-size: 13px;
        color: #666666;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 数据载入
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
    # 强制指定您要求的统计周期标题
    time_period = "2026年7月13日－7月19日"
    
    # --- 头部黄底横幅复刻 ---
    st.markdown(f"""
        <div class="banner-container">
            <div>
                <span class="banner-title">区域单量及CM3数据复盘</span>
                <span class="banner-subtitle">统计周期：{time_period}（周一至周日）· 统计口径：跟进人提交时间</span>
            </div>
            <div class="status-dot">
                <span style="color:#2E7D32;">● 数据已就绪</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 横向标签选择栏 (Tabs) ---
    st.markdown("### 🎛️ 横向多维看板切换")
    tab_region, tab_bd, tab_category = st.tabs(["🌍 按区域查看 (Region)", "👤 按 BD 负责人查看 (Staff)", "🍔 按商户品类查看 (Category)"])
    
    # 初始化筛选变量
    filter_col = None
    filter_val = None
    
    with tab_region:
        unique_regions = ["全部区域"] + list(df_raw['Region'].dropna().unique())
        selected_r = st.selectbox("选择目标区域：", unique_regions, key="sel_r")
        if selected_r != "全部区域":
            filter_col, filter_val = 'Region', selected_r
            
    with tab_bd:
        unique_staffs = ["全部 BD 负责人"] + list(df_raw['Staff'].dropna().unique())
        selected_s = st.selectbox("选择核心 BD：", unique_staffs, key="sel_s")
        if selected_s != "全部 BD 负责人":
            filter_col, filter_val = 'Staff', selected_s
            
    with tab_category:
        unique_categories = ["全部品类"] + list(df_raw['Category'].dropna().unique())
        selected_c = st.selectbox("选择目标品类：", unique_categories, key="sel_c")
        if selected_c != "全部品类":
            filter_col, filter_val = 'Category', selected_c

    # 执行过滤
    df_filtered = df_raw.copy()
    if filter_col and filter_val:
        df_filtered = df_filtered[df_filtered[filter_col] == filter_val]

    # --- 4. 真实核心指标数据汇总 ---
    cw_orders = df_filtered['Orders'].sum()
    cw_cm3 = df_filtered['CM3'].sum()
    
    # 从表里直接求和获取核心 gap（WoW 与 YoY）
    wow_order_gap = df_filtered['weekly_order_gap'].sum()
    wow_cm3_gap = df_filtered['weekly_cm3_gap'].sum()
    yoy_order_gap = df_filtered['weekly_yoy_order_gap'].sum()
    yoy_cm3_gap = df_filtered['weekly_yoy_cm3_gap'].sum()
    
    # 倒推历史基准值用于计算百分比
    lw_orders = cw_orders - wow_order_gap
    lw_cm3 = cw_cm3 - wow_cm3_gap
    ly_orders = cw_orders - yoy_order_gap
    ly_cm3 = cw_cm3 - yoy_cm3_gap

    def pct(current, baseline):
        if baseline and baseline != 0:
            return ((current - baseline) / baseline) * 100
        return 0.0

    # 计算各维度变动率
    wow_ord_pct = pct(cw_orders, lw_orders)
    yoy_ord_pct = pct(cw_orders, ly_orders)
    wow_cm3_pct = pct(cw_cm3, lw_cm3)
    yoy_cm3_pct = pct(cw_cm3, ly_cm3)

    # --- 5. 顶层横向核心数据表现 (KPI Summary - 包含 WoW 与 YoY 同时展示) ---
    st.markdown("---")
    st.markdown("### 📊 核心数据表现 (KPI Summary)")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">📦 本周总订单量</div>
                <div class="kpi-value" style="color: #1E1E1E;">{cw_orders:,.0f} <span style='font-size:16px; font-weight:normal;'>单</span></div>
                <div class="kpi-footer">环比上周(WoW)：{wow_order_gap:+,.0f} 单 ({wow_ord_pct:+.1f}%)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">📆 订单同比表现 (YoY)</div>
                <div class="kpi-value" style="color: #00B074;">{yoy_ord_pct:+.1f}%</div>
                <div class="kpi-footer">同比去年差额：{yoy_order_gap:+,.0f} 单</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">💰 本周总 CM3 利润</div>
                <div class="kpi-value" style="color: #1E1E1E;">${cw_cm3:,.2f}</div>
                <div class="kpi-footer">环比上周(WoW)：${wow_cm3_gap:+,.2f} ({wow_cm3_pct:+.1f}%)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">📈 利润同比表现 (YoY)</div>
                <div class="kpi-value" style="color: #0288D1;">{yoy_cm3_pct:+.1f}%</div>
                <div class="kpi-footer">同比去年差额：${yoy_cm3_gap:+,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- 6. 下方明细业绩数据联动表 (同时包含 WoW 和 YoY 的单量与 CM3 明细) ---
    st.markdown("---")
    st.markdown("### 📋 联动维度下的商户诊断明细")
    
    # 动态筛选并重命名列
    display_cols = [
        'Region', '店铺名字', 'Staff', 'Category', 
        'Orders', 'weekly_order_gap', 'weekly_yoy_order_gap',
        'CM3', 'weekly_cm3_gap', 'weekly_yoy_cm3_gap'
    ]
    df_disp = df_filtered[display_cols].copy()
    df_disp.columns = [
        '区域', '店铺名字', '负责人', '品类', 
        '本周订单', '订单WoW差额', '订单YoY差额',
        '本周CM3', 'CM3WoW差额', 'CM3YoY差额'
    ]
    
    # 使用色彩条突出业绩异动情况，负数显红，正数显绿
    st.dataframe(
        df_disp.style.bar(subset=['订单WoW差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                     .bar(subset=['订单YoY差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                     .bar(subset=['CM3WoW差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                     .bar(subset=['CM3YoY差额'], color=['#FFCDD2', '#C8E6C9'], align='mid')
                     .format({
                         '本周订单': '{:,.0f}', '订单WoW差额': '{:+,.0f}', '订单YoY差额': '{:+,.0f}',
                         '本周CM3': '${:,.2f}', 'CM3WoW差额': '${:,.2f}', 'CM3YoY差额': '${:,.2f}'
                     }),
        use_container_width=True,
        hide_index=True
    )
