# -*- coding: utf-8 -*-
"""指标对比图表组件 - 柱状图对比当前用户与平均值"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # 创建数据
    metric_names = list(metrics.keys())
    current_values = list(metrics.values())
    avg_values = [df[k].mean() for k in metrics.keys()]

    # 使用matplotlib绘制自定义柱状图，满足设计规范：
    # - 当前用户: 蓝色 #1976D2
    # - 平均值: 灰色 #E0E0E0
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # 设置柱状图宽度和位置
    bar_width = 0.35
    index = range(len(metric_names))

    # 绘制两组数据
    bars1 = ax.bar([i - bar_width/2 for i in index], current_values, bar_width,
                   label='当前用户', color='#1976D2', zorder=2)
    bars2 = ax.bar([i + bar_width/2 for i in index], avg_values, bar_width,
                   label='平均值', color='#E0E0E0', zorder=2)

    # 自定义样式
    ax.set_ylabel('数值', fontsize=12, color='#86909C')
    ax.set_xticks(index)
    ax.set_xticklabels(metric_names, rotation=30, ha='right', fontsize=10, color='#4E5969')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', linestyle='--', color='#F0F0F0', alpha=0.8, zorder=1)
    ax.set_facecolor('white')
    fig.set_facecolor('white')

    # 调整布局防止标签被截断
    plt.tight_layout()

    # 在streamlit中展示
    st.pyplot(fig, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
