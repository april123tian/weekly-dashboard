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
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h1 style='margin:0; font-size: 26px; font-weight:700;'>悉尼BD 目标对齐动态看板（第三页专用独立版）</h1>
        <p style='margin:6px 0 0 0; opacity: 0.8; font-size: 13px;'>统计截止：2026年7月19日 · 核心逻辑：基于 MTD 数据 / 19 * 31 动态预估</p>
    </div>
""", unsafe_allow_html=True)

# 百分比高亮着色逻辑
def style_completion_rate(val):
    try:
        rate = float(str(val).replace('%', '').strip())
        if rate >= 90:
            return 'color: #28a745; font-weight: bold;'
        elif rate < 70:
            return 'color: #dc3545; font-weight: bold;'
        return 'color: #1a252c;'
    except:
        return 'color: #1a252c;'

# ==========================================
# 1. 数据引擎自动加载与清洗
# ==========================================
try:
    df_raw = pd.read_excel('data.xlsx')
    
    # 适配最新真实表头
    df_raw = df_raw.rename(columns={
        'BD名字': 'Staff',
        '当前日均': 'Daily_Avg_Actual',
        'MTD CM3': 'MTD_CM3_Actual'
    })
    
    # 清洗名字去除空格
    df_raw['Staff'] = df_raw['Staff'].astype(str).str.strip()
    
    # 统一英文名映射
    name_map = {
        '张宇庭': 'Zhang Yuting',
        '田雨卿': 'Tian Yuqing',
        '覃念慈': 'Tan Nianci',
        '李晓彤': 'Li Xiaotong'
    }
    df_raw['Staff'] = df_raw['Staff'].replace(name_map)
    
    # 提取 BD 实际数据字典
    bd_data = df_raw.groupby('Staff').agg({
        'Daily_Avg_Actual': 'sum',
        'MTD_CM3_Actual': 'sum'
    }).to_dict('index')
    
    data_loaded = True
except Exception as e:
    st.error(f"❌ 自动读取本地 data.xlsx 失败。请确保文件在同级目录且表头包含[BD名字]、[当前日均]、[MTD CM3]。错误详情: {e}")
    data_loaded = False

if data_loaded:
    # 静态配置目标字典与专属增量池
    target_perf = {
        'Mabel Wang': {'order_tgt': 1819, 'cm3_tgt': 302025, 'extra': 266733},
        'Zhang Yuting': {'order_tgt': 1779, 'cm3_tgt': 306880, 'extra': 283552},
        'Tan Nianci': {'order_tgt': 1418, 'cm3_tgt': 232002, 'extra': 229803},
        'Li Xiaotong': {'order_tgt': 1924, 'cm3_tgt': 262125, 'extra': 232436},
        'Tian Yuqing': {'order_tgt': 1914, 'cm3_tgt': 285255, 'extra': 254767},
        'Terry Meng': {'order_tgt': 1785, 'cm3_tgt': 301457, 'extra': 0},
        'Qichong Wang': {'order_tgt': 790, 'cm3_tgt': 81810, 'extra': 0},
        '时晨': {'order_tgt': 2310, 'cm3_tgt': 378308, 'extra': 0},
        'Yuan Dong': {'order_tgt': 2310, 'cm3_tgt': 321785, 'extra': 0},
    }
    
    order_rows = []
    cm3_rows = []
    
    for name, tgt in target_perf.items():
        # 获取 Excel 中当前 BD 的实际数据行
        actual = bd_data.get(name, {'Daily_Avg_Actual': 0, 'MTD_CM3_Actual': 0})
        
        # ----------------------------
        # 计算表一：日均单量追踪
        # ----------------------------
        daily_act = int(actual['Daily_Avg_Actual'])
        daily_tgt = tgt['order_tgt']
        cm3_tgt_val = tgt['cm3_tgt']
        
        o_rate = (daily_act / daily_tgt) * 100 if daily_tgt else 0
        o_diff = daily_act - daily_tgt
        o_sign = "+" if o_diff > 0 else ""
        
        order_rows.append({
            "BD负责人": name,
            "日均单量目标": daily_tgt,
            "本月 CM3 目标值": f"${cm3_tgt_val:,.2f}",
            "当前日均单量": daily_act,
            "单量完成度": f"{o_rate:.1f}%",
            "单量目标差值": f"{o_sign}{o_diff:,}" if o_diff != 0 else "0"
        })
        
        # ----------------------------
        # 计算表二：月度 CM3 预测对齐
        # ----------------------------
        mtd_cm3 = actual['MTD_CM3_Actual']
        # 公式: (MTD CM3 / 19) * 31 + 额外增量池
        est_month_cm3 = (mtd_cm3 / 19) * 31 + tgt['extra']
        
        c_rate = (est_month_cm3 / cm3_tgt_val) * 100 if cm3_tgt_val else 0
        c_diff = est_month_cm3 - cm3_tgt_val
        c_sign = "+" if c_diff > 0 else ""
        
        cm3_rows.append({
            "BD负责人": name,
            "月度 CM3 目标值": f"${cm3_tgt_val:,.2f}",
            "MTD 实际 CM3": f"${mtd_cm3:,.2f}",
            "本月预估 CM3 完成数": f"${est_month_cm3:,.2f}",
            "预估完成度": f"{c_rate:.1f}%",
            "预估目标差值": f"{c_sign}${c_diff:,.2f}" if c_diff != 0 else "$0.00"
        })

    # ==========================================
    # 3. 前端大屏呈现
    # ==========================================
    st.markdown("<h3 style='margin-bottom:15px;'>📋 表一：BD 个人维度日均单量目标追踪</h3>", unsafe_allow_html=True)
    df_order_final = pd.DataFrame(order_rows)
    # 按目标排序，并应用 Styler.map 进行百分比变色
    st.dataframe(
        df_order_final.style.map(style_completion_rate, subset=['单量完成度']), 
        use_container_width=True, 
        hide_index=True
    )
    
    st.markdown("<br><hr style='border-top:1px solid #e2e8f0;'><br>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-bottom:15px;'>💰 表二：BD 个人维度月度 CM3 预测对齐看板</h3>", unsafe_allow_html=True)
    df_cm3_final = pd.DataFrame(cm3_rows)
    st.dataframe(
        df_cm3_final.style.map(style_completion_rate, subset=['预估完成度']), 
        use_container_width=True, 
        hide_index=True
    )
