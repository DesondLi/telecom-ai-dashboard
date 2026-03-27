# -*- coding: utf-8 -*-
"""
电信AI数据治理与用户画像分析系统 v2.0
重构优化版 - 组件化架构
基于增强版特征标签宽表
使用 AIHubMix Gemini API
"""

import streamlit as st
import pandas as pd

# 导入组件和工具函数
from components import (
    render_sidebar,
    render_risk_banner,
    render_overview_cards,
    render_core_metrics,
    render_chart_section,
    render_tags_section,
    render_ai_analysis,
    render_expandable_sections
)
from utils.data import load_enhanced_data, generate_mock_data

# 页面配置
st.set_page_config(
    page_title="电信AI数据治理与画像 v2.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# 加载自定义CSS
# =====================================
def load_css(css_path):
    """加载外部CSS文件"""
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# 加载基础样式表
import os
css_path = os.path.join(os.path.dirname(__file__), 'static/style.css')
try:
    load_css(css_path)
except FileNotFoundError:
    # 如果CSS文件不存在，使用内置基础样式
    st.markdown("""
    <style>
        /* 基础卡片和标签样式 */
        .main {
            background-color: #F5F7FA;
        }
        .stApp {
            background-color: #F5F7FA;
        }
    </style>
    """, unsafe_allow_html=True)


# =====================================
# 主应用逻辑
# =====================================

# 先根据选择加载数据 - 数据源选择决定数据
data_source = "增强版宽表(推荐)"

# 先加载数据 - 用户选择需要完整数据后才能渲染
if data_source == "增强版宽表(推荐)":
    df = load_enhanced_data("投诉业务_特征与标签宽表_增强版.xlsx")
    if df is None:
        df = generate_mock_data(500)
else:
    df = generate_mock_data(500)

if df is None:
    st.error("""
    ❌ **无法加载数据**

    找不到数据文件: `投诉业务_特征与标签宽表_增强版.xlsx`

    请检查:
    - 文件是否存在于项目根目录
    - 文件名是否正确
    - 文件权限是否正确

    你也可以选择"模拟数据演示"查看效果
    """)
    st.stop()

# 现在数据加载完成，使用完整数据渲染侧边栏获取用户选择
selected_user = None

selected_user, data_source = render_sidebar(df)

if selected_user is None:
    st.info("👋 请从侧边栏搜索并选择用户开始分析")
    st.stop()

# 获取当前用户数据
user_data = df[df["联系电话"] == selected_user].iloc[0]

    # 主标题
    st.markdown("<h1 style='font-size: 24px; font-weight: 700; color: #1D2129; margin-bottom: 8px;'>🧠 AI数据治理与投诉用户画像分析</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 14px; color: #86909C; margin-bottom: 24px;'>当前分析用户: <strong style='color: #1D2129;'>{selected_user}</strong></div>", unsafe_allow_html=True)

    # 1. 渲染风险警示条
    render_risk_banner(user_data)

    # 2. 渲染整体统计概览卡片
    render_overview_cards(df)

    # 3. 渲染核心指标
    render_core_metrics(user_data, df)

    # 4. 双列布局：左侧图表 + 右侧标签业务信息
    col_chart, col_tags = st.columns([1, 1])

    with col_chart:
        # 包装在卡片容器中
        st.markdown("""
        <div style="
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
        ">
        """, unsafe_allow_html=True)
        render_chart_section(user_data, df)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tags:
        # 包装在卡片容器中
        st.markdown("""
        <div style="
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
        ">
        """, unsafe_allow_html=True)
        render_tags_section(user_data)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. 渲染AI分析区域
    render_ai_analysis(user_data)

    # 6. 渲染可折叠扩展区域
    render_expandable_sections(user_data)

except Exception as e:
    st.error(f"应用运行错误: {str(e)}")
    st.exception(e)
