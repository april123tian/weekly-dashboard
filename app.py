import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 全局页面配置 (浅色皮肤调优)
# ==========================================
st.set_page_config(
    page_title="Region & CM3 Data Review",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入浅色高对比度 CSS 样式，并定义小箭头的颜色风格
st.markdown("""
    <style>
    /* 全局背景色调为明亮白/浅灰，文字为深色 */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
    }
    /* 标题与副标题样式 */
    h1, h2, h3 {
        color: #1a252c !important;
        font-weight: 700 !important;
    }
    /* 针对数据表格内霓虹红绿箭头的样式定义 */
    .up-trend {
        color: #28a745; /* 翠绿 */
        font-weight: bold;
    }
    .down-trend {
        color: #dc3545; /* 鲜红 */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 侧边栏导航控制 (删除“第一页”等字样，仅保留纯业务内容)
# ==========================================
menu = st.sidebar.radio(
    "控制面板 / 导航切换",
    ["全盘整体业绩看板", "多维交互探索中心", "BD个人目标达成对齐"]
)

# 模拟加载前两页的基础数据 (用于展示同环比箭头逻辑)
@st.cache_data
def load_base_data():
    # 假设这是你 data.xlsx 里的清洗后大盘映射
    try:
        df = pd.read_excel('data.xlsx')
        return df
    except:
        # 兜底测试数据
        return pd.DataFrame()

# 格式化带红绿箭头的百分比函数 (浅色版)
def format_pct_with_arrow(val):
    if val > 0:
        return f"🟢 ➕{val:.1f}%"
    elif val < 0:
        return f"🔴 ➖{abs(val):.1f}%"
    return f"{val:.1f}%"

# ==========================================
# 页面一：全盘整体业绩看板
# ==========================================
if menu == "全盘整体业绩看板":
    st.title("📊 全盘整体业绩看板")
    st.caption("同步更新至本周最新数据周期 • 浅色高对比度版")
    st.markdown("---")
    
    # 示例大盘核心KPI区块
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("本周总订单量", "52,974 单", "🔴 -4.7% (WoW)", delta_color="inverse")
    with col2:
        st.metric("本周 CM3 利润总额", "$251,473.40", "🔴 -5.1% (WoW)", delta_color="inverse")
    with col3:
        st.metric("CM3 历史同比利润", "对比去年同期", "🟢 +11.7% (YoY)")
        
    st.subheader("📍 核心商圈维度业绩阵列 (Top 排列)")
    # 这里放之前处理好的商圈浅色数据表格...
    st.info("💡 提示：所有比例指标已自动根据表现激活 🟢/🔴 警示灯。")

# ==========================================
# 页面二：多维交互探索中心
# ==========================================
elif menu == "多维交互探索中心":
    st.title("🔍 多维交互探索中心")
    st.caption("支持按区域、BD负责人、品类跨维度动态交叉过滤")
    st.markdown("---")
    
    # 筛选联动逻辑...
    st.write("请在左侧或上方选择筛选条件，系统将自动重绘浅色阵列数据。")

# ==========================================
# 页面三：BD个人目标达成对齐 (全新重构)
# ==========================================
elif menu == "BD个人目标达成对齐":
    st.title("🎯 BD 个人目标达成对齐看板")
    st.caption("数据计算基准：实际数据截至 7月18日 (共18天) | 月度预估系数：31天")
    st.markdown("---")
    
    # 1. 录入从图片中解析出来的最新数据源
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
    
    # 2. 动态计算与数据组装
    order_data = []
    cm3_data = []
    
    for bd in target_source.keys():
        act = actual_source.get(bd, {'daily_avg': 0, 'mtd_cm3': 0})
        tgt = target_source[bd]
        
        # --- 针对单量维度的计算 ---
        daily_act = act['daily_avg']
        daily_tgt = tgt['order_target']
        order_rate = (daily_act / daily_tgt) * 100 if daily_tgt else 0
        order_diff = daily_act - daily_tgt
        
        # 赋予单量差值正负号与箭头
        order_arrow = "🟢 " if order_diff >= 0 else "🔴 "
        
        order_data.append({
            "BD 负责人": bd,
            "当前日均单量": f"{daily_act:,}",
            "日均单量目标": f"{daily_tgt:,}",
            "目标完成度": f"{order_rate:.1f}%",
            "目标差值": f"{order_arrow}{order_diff:+d}"
        })
        
        # --- 针对 CM3 维度的计算 ---
        # 预估本月完成数 = MTD CM3 / 18 * 31 (底层纯数值计算，前台不留公式文本)
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
    
    # 3. 前端双表平铺渲染
    st.subheader("📋 表一：BD个人维度日均单量追踪")
    st.dataframe(df_order_final, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allowed_html=True)
    
    st.subheader("💰 表二：BD个人维度月度 CM3 预测对齐")
    st.dataframe(df_cm3_final, use_container_width=True, hide_index=True)
