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
    .dataframe th {
        background-color: #e9ecef !important;
        color: #212529 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper: 给百分比或比例添加红绿箭头
def attach_arrow_to_cell(val):
    try:
        val_str = str(val).strip()
        # 兼容原本就已经带有红色🔴或🟢的小箭头文本
        if '-' in val_str or '🔴' in val_str:
            return f"🔴 {val_str.replace('🔴', '').strip()}"
        elif '+' in val_str or '🟢' in val_str:
            return f"🟢 {val_str.replace('🟢', '').strip()}"
        
        # 解析百分比数值
        num_str = val_str.replace('%', '').replace('$', '').replace(',', '')
        if num_str:
            num = float(num_str)
            if num > 0:
                return f"🟢 +{val_str}"
            elif num < 0:
                return f"🔴 {val_str}"
    except:
        pass
    return val

# ==========================================
# 1. 动态数据加载引擎 (BUG-FREE 的强力兼容模式)
# ==========================================
@st.cache_data
def load_and_fix_excel_bug():
    # A. 先以默认 Dtype 读取完整 Excel
    df = pd.read_excel('data.xlsx')
    
    # B. 【核心 Bug 修复】：遍历所有 object/string 列，将其转换为标准的标准标准 string dtype，
    #    而不使用会导致 TypeError 的 `StringDtype(na_value=nan)` 映射。
    for col in df.columns:
        if df[col].dtype == 'object':
            # 直接 astype('string')，pandas 会自动处理 na_value 为 <NA>
            df[col] = df[col].astype('string')
            
    # C. 全自动清洗：为所有包含“率”、“比”、“YoY”、“WoW”、“Gap”的列或者带负号的百分比智能追加红绿箭头
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].apply(attach_arrow_to_cell)
        elif np.issubdtype(df[col].dtype, np.number):
            # 智能对含有特定关键词的数值列转换并加箭头
            if any(k in col.lower() for k in ['wow', 'yoy', 'gap', '变化', '对比', '降', '升']):
                df[col] = df[col].apply(lambda x: f"🟢 +{x:.1f}%" if x > 0 else (f"🔴 -{abs(x):.1f}%" if x < 0 else f"{x:.1f}%"))
    return df

try:
    df_raw = load_and_fix_excel_bug()
    data_loaded = True
except Exception as e:
    st.error(f"⚠️ 无法读取 data.xlsx。由于 Pandas Dtype 解析 Bug，我们已尝试修复，但读取依然失败。错误详情: {e}")
    data_loaded = False

# ==========================================
# 2. 侧边栏导航控制 (已删除“第一页”等字样，只留纯业务名)
# ==========================================
menu = st.sidebar.radio(
    "控制面板 / 导航切换",
    ["全盘整体业绩看板", "多维交互探索中心", "BD个人目标达成对齐"]
)

if data_loaded:
    # ==========================================
    # 页面一：全盘整体业绩看板 (彻底找回并兼容原始数据)
    # ==========================================
    if menu == "全盘整体业绩看板":
        st.title("📊 全盘整体业绩看板")
        st.caption("已自动适配浅色背景，并对环比/同比下降指标添加 🔴 指针，上升指标添加 🟢 指针")
        st.markdown("---")
        
        st.subheader("📍 核心业绩数据概览")
        # 直接输出处理好箭头的完整大盘表格，确保你的原始数据一字不落全部显现！
        st.dataframe(df_raw, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面二：多维交互探索中心 (彻底找回交互过滤)
    # ==========================================
    elif menu == "多维交互探索中心":
        st.title("🔍 多维交互探索中心")
        st.caption("支持跨维度动态交互过滤明细")
        st.markdown("---")
        
        # 智能识别文本列供用户筛选
        text_cols = df_raw.select_dtypes(include=['string']).columns.tolist()
        if not text_cols:
            text_cols = df_raw.columns.tolist()
            
        filter_col = text_cols[0]
        selected_values = st.multiselect(f"请选择筛选维度 ({filter_col}):", options=df_raw[filter_col].unique())
        
        df_filtered = df_raw.copy()
        if selected_values:
            df_filtered = df_filtered[df_filtered[filter_col].isin(selected_values)]
            
        st.subheader("📋 联动过滤后的明细阵列")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

    # ==========================================
    # 页面三：BD个人目标达成对齐 (全新重构的独立表格)
    # ==========================================
    elif menu == "BD个人目标达成对齐":
        st.title("🎯 BD 个人目标达成对齐看板")
        st.caption("数据计算基准：实际数据截至 7月18日 (共18天) | 月度预估系数：31天")
        st.markdown("---")
        
        # 解析出的截图里的最新数据源
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
            
            # 1. 单量维度计算
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
            
            # 2. CM3 维度计算 (后台静默计算 MTD/18*31，绝不外露公式文本)
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("💰 表二：BD个人维度月度 CM3 预测对齐")
        st.dataframe(df_cm3_final, use_container_width=True, hide_index=True)
