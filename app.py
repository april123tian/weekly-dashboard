import streamlit as st
import pandas as pd

# ==========================================
# 0. 页面全局配置
# ==========================================
st.set_page_config(page_title="悉尼BD 数据经营看板", layout="wide")

st.markdown("""
    <style>
    .kpi-card { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #eef0f2; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #1a252c; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 悉尼BD 经营例会数据看板 (7.13-7.19)")

# ==========================================
# 1. 数据加载与标准化
# ==========================================
uploaded_file = st.file_uploader("请上传最新的订单数据文件 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file)
    
    # 强制标准化列名 (请根据您表格的实际表头进行微调)
    df_raw = df_raw.rename(columns={
        'BD名字': 'Staff',
        '总单量': 'Orders',
        'MTD订单量': 'MTD_Orders',
        'MTD CM3': 'MTD_CM3',
        '当前日均': 'Daily_Avg'
    })

    tab1, tab2, tab3 = st.tabs(["📊 整体数据复盘", "🔍 交叉明细探索", "🎯 BD目标达成追踪"])

    # ---------------- Tab 1: 整体复盘 ----------------
    with tab1:
        st.subheader("🌐 全盘核心运营总览")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>MTD 总订单量</div><div class='kpi-value'>{df_raw['MTD_Orders'].sum():,}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>MTD CM3 总利润</div><div class='kpi-value'>${df_raw['MTD_CM3'].sum():,.0f}</div></div>", unsafe_allow_html=True)
        
        st.dataframe(df_raw[['Staff', 'Orders', 'MTD_Orders', 'MTD_CM3']], use_container_width=True)

    # ---------------- Tab 2: 交叉探索 ----------------
    with tab2:
        st.subheader("🔍 筛选明细数据")
        st.dataframe(df_raw, use_container_width=True)

    # ---------------- Tab 3: BD个人目标达成对齐 ----------------
    with tab3:
        st.subheader("🎯 BD个人经营目标预测")
        
        # 修正逻辑的额外叠加值
        extra_cm3_map = {
            'Mabel Wang': 266733, '田雨卿': 254767, '张宇庭': 283552, 
            '覃念慈': 229803, '李晓彤': 232436
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
                return 'color: #28a745; font-weight: bold;' if rate >= 90 else 'color: #dc3545; font-weight: bold;' if rate < 70 else 'color: #1a252c;'
            except: return 'color: #1a252c;'

        cm3_data = []
        for name, tgt in target_perf.items():
            perf_row = df_raw[df_raw['Staff'] == name]
            mtd_cm3 = perf_row['MTD_CM3'].values[0] if not perf_row.empty else 0
            
            # 您的公式：(MTD / 19) * 31 + Extra
            est_cm3 = (mtd_cm3 / 19) * 31 + extra_cm3_map.get(name, 0)
            c_rate = (est_cm3 / tgt['cm3_tgt']) * 100
            c_diff = est_cm3 - tgt['cm3_tgt']
            
            cm3_data.append({
                "BD负责人": name, 
                "本月预估": f"${est_cm3:,.0f}", 
                "目标值": f"${tgt['cm3_tgt']:,}", 
                "完成度": f"{c_rate:.1f}%", 
                "缺口/盈余": f"${c_diff:,.0f}"
            })

        st.dataframe(pd.DataFrame(cm3_data).style.map(color_rate, subset=['完成度']), use_container_width=True, hide_index=True)

else:
    st.warning("请上传数据文件以启动看板")
