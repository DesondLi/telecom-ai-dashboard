# -*- coding: utf-8 -*-
"""指标对比图表组件 - 柱状图对比当前用户与平均值"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def render_chart_section(user_data, df):
    """渲染投诉指标对比柱状图"""
    # 外层白色卡片包装，和demo对齐
    st.markdown("""
    <div style="
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.1), 0 2px 4px -1px rgba(15, 23, 42, 0.06);
        margin-bottom: 24px;
    ">
    """, unsafe_allow_html=True)

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

    # 使用matplotlib绘制自定义柱状图，符合新设计系统：
    # - 当前用户: 专业蓝 #1E40AF
    # - 平均值: 浅灰 #E2E8F0
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # 设置柱状图宽度和位置
    bar_width = 0.35
    index = range(len(metric_names))

    # 绘制两组数据
    bars1 = ax.bar([i - bar_width/2 for i in index], current_values, bar_width,
                   label='当前用户', color='#1E40AF', zorder=2)
    bars2 = ax.bar([i + bar_width/2 for i in index], avg_values, bar_width,
                   label='平均值', color='#E2E8F0', zorder=2)

    # 自定义样式
    ax.set_ylabel('数值', fontsize=12, color='#64748B')
    ax.set_xticks(index)
    ax.set_xticklabels(metric_names, rotation=30, ha='right', fontsize=10, color='#334155')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', linestyle='--', color='#F1F5F9', alpha=0.8, zorder=1)
    ax.set_facecolor('white')
    fig.set_facecolor('white')

    # 调整布局防止标签被截断
    plt.tight_layout()

    # 在streamlit中展示
    st.pyplot(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
