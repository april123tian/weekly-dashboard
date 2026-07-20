import streamlit as st
import pandas as pd

st.set_page_config(page_title="悉尼BD 数据经营看板", layout="wide")
st.title("📊 悉尼BD 经营例会数据看板")

# 1. 动态读取文件
uploaded_file = st.file_uploader("请上传订单数据文件 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file)
    # 统一列名映射（根据之前提供的图片）
    df_raw = df_raw.rename(columns={
        'Satff': 'Staff', '单量': 'Orders', '上周cm3': 'Weekly_CM3', 'Region': 'Region', 'Category': 'Category'
    })
    
    # 统一清洗数据类型
    df_raw['Orders'] = pd.to_numeric(df_raw['Orders'], errors='coerce').fillna(0)
    df_raw['Weekly_CM3'] = pd.to_numeric(df_raw['Weekly_CM3'], errors='coerce').fillna(0)

    # 创建三个页面
    tab1, tab2, tab3 = st.tabs(["📊 第一页：全盘数据概览", "🔍 第二页：区域与品类筛选", "🎯 第三页：目标完成进度"])

    # --- 第一页：全盘概览 ---
    with tab1:
        st.subheader("🌐 整体运营大盘")
        c1, c2 = st.columns(2)
        c1.metric("MTD 总订单量", f"{int(df_raw['Orders'].sum()):,}")
        c2.metric("MTD CM3 总额", f"${df_raw['Weekly_CM3'].sum():,.0f}")
        
        st.markdown("### BD 个人贡献排行")
        st.dataframe(df_raw.groupby('Staff')[['Orders', 'Weekly_CM3']].sum().sort_values(by='Weekly_CM3', ascending=False), use_container_width=True)

    # --- 第二页：交叉筛选 ---
    with tab2:
        st.subheader("🔍 数据透视分析")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        # 筛选逻辑
        regions = col_f1.multiselect("筛选区域", options=df_raw['Region'].unique())
        staffs = col_f2.multiselect("筛选BD", options=df_raw['Staff'].unique())
        cats = col_f3.multiselect("筛选品类", options=df_raw['Category'].unique())
        
        df_filter = df_raw.copy()
        if regions: df_filter = df_filter[df_filter['Region'].isin(regions)]
        if staffs: df_filter = df_filter[df_filter['Staff'].isin(staffs)]
        if cats: df_filter = df_filter[df_filter['Category'].isin(cats)]
        
        st.dataframe(df_filter, use_container_width=True)

    # --- 第三页：目标对比 ---
    with tab3:
        st.subheader("🎯 目标达成情况")
        extra_map = {'Mabel Wang': 266733, 'Zhang Yuting': 283552, 'Tian Yuqing': 254767, 'Tan Nianci': 229803, 'Li Xiaotong': 232436}
        targets = {'Mabel Wang': 302025, 'Zhang Yuting': 306880, 'Tan Nianci': 232002, 'Li Xiaotong': 262125, 'Tian Yuqing': 285255}
        
        data_list = []
        for staff, tgt in targets.items():
            mtd_cm3 = df_raw[df_raw['Staff'] == staff]['Weekly_CM3'].sum()
            projected = (mtd_cm3 / 19) * 31 + extra_map.get(staff, 0)
            data_list.append({
                "BD": staff, "预估值": projected, "目标值": tgt, 
                "差距": projected - tgt, "达成率": f"{(projected/tgt)*100:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(data_list), use_container_width=True)

else:
    st.warning("请上传数据文件 (.xlsx)")
