# -*- coding: utf-8 -*-
"""指标对比图表组件 - 柱状图对比当前用户与平均值"""

import streamlit as st
import pandas as pd

def render_chart_section(user_data, df):
    """渲染投诉指标对比柱状图"""
    st.markdown("### 📊 投诉指标详情对比")

    # 定义要展示的指标
    metrics = {
        "近7天投诉": user_data.get("近7天投诉", 0),
        "近30天投诉": user_data.get("近30天投诉", 0),
        "越级次数": user_data.get("越级次数", 0),
        "越级占比": user_data.get("越级占比", 0),
        "投诉类型广度": user_data.get("投诉类型广度", 0),
        "流转总次数": user_data.get("流转总次数", 0),
        "涉及流水号数": user_data.get("涉及流水号数", 0)
    }

    # 创建DataFrame用于图表
    chart_data = pd.DataFrame({
        "指标": list(metrics.keys()),
        "当前用户": list(metrics.values()),
        "平均值": [df[k].mean() for k in metrics.keys()]
    }).set_index("指标")

    # 使用Streamlit的bar_chart直接渲染
    # 注意：Streamlit的bar_chart会自动处理颜色，但我们可以通过自定义配置优化
    # 由于Streamlit原生限制，无法完全自定义柱子颜色，但保证基本功能可用
    st.bar_chart(chart_data, height=350, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
