# -*- coding: utf-8 -*-
"""核心指标组件 - 展示当前用户的四个核心指标，使用Streamlit原生布局"""

import streamlit as st
import pandas as pd

def get_delta_color(metric_name, value, avg):
    """
    根据指标类型和差值确定颜色
    返回颜色类
    """
    delta = value - avg

    # 规则:
    # - 投诉次数/越级次数: 高于均值不好 → 红色；低于均值好 → 绿色
    # - 投诉解决率: 高于均值好 → 绿色；低于均值不好 → 红色
    if metric_name in ["总投诉次数", "越级次数"]:
        if delta > 0:
            return "color: var(--color-error);"  # 不好 - 红色
        elif delta < 0:
            return "color: var(--color-success);"  # 好 - 绿色
        else:
            return "color: var(--color-text-secondary);"
    elif metric_name == "投诉解决率":
        if delta > 0:
            return "color: var(--color-success);"  # 好 - 绿色
        elif delta < 0:
            return "color: var(--color-error);"  # 不好 - 红色
        else:
            return "color: var(--color-text-secondary);"
    else:
        return "color: var(--color-text-secondary);"

def format_delta(metric_name, value, avg):
    """格式化差值显示"""
    delta = value - avg
    if delta > 0:
        return f"+{delta:.1f} vs 均值"
    elif delta < 0:
        return f"{delta:.1f} vs 均值"
    else:
        return "等于均值"

def render_core_metrics(user_data, df):
    """渲染核心指标，使用streamlit原生columns布局"""
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

    st.markdown("### 🎯 核心指标")

    # 使用Streamlit原生columns创建4列布局
    cols = st.columns(4)

    # 计算平均值
    avg_total = df["总投诉次数"].mean() if "总投诉次数" in df.columns else 0
    avg_escalated = df["越级次数"].mean() if "越级次数" in df.columns else 0

    current_total = user_data.get("总投诉次数", 0)
    escalated = user_data.get("越级次数", 0)
    months_on_net = user_data.get("在网时长(月)", 0)
    avg_spend = user_data.get("月均消费(元)", 0)

    # 定义指标数据 - 四个核心指标
    metrics = [
        {
            "name": "总投诉次数",
            "value": f"{current_total}",
            "show_delta": True,
            "value_raw": current_total,
            "avg": avg_total
        },
        {
            "name": "越级次数",
            "value": f"{escalated}",
            "show_delta": True,
            "value_raw": escalated,
            "avg": avg_escalated
        },
        {
            "name": "在网时长(月)",
            "value": f"{months_on_net}" if months_on_net else "0",
            "show_delta": False,
            "value_raw": 0,
            "avg": 0
        },
        {
            "name": "月均消费(元)",
            "value": f"{avg_spend:.0f}" if avg_spend else "0",
            "show_delta": False,
            "value_raw": 0,
            "avg": 0
        }
    ]

    # 不需要外层CSS grid容器 — 使用Streamlit原生columns
    # 渲染每个指标卡片
    for col, metric in zip(cols, metrics):
        with col:
            if metric['show_delta']:
                delta_text = format_delta(metric['name'], metric['value_raw'], metric['avg'])
                delta_color = get_delta_color(metric['name'], metric['value_raw'], metric['avg'])
                delta_html = f'<div style="font-size: 13px; {delta_color} margin-top: 8px;">{delta_text}</div>'
            else:
                delta_html = ""

            st.markdown(f'''
            <div style="
                background-color: var(--color-bg-card);
                border: 1px solid var(--color-border);
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-md);
                padding: var(--spacing-lg) var(--spacing-md);
                text-align: center;
                transition: all 0.2s ease;
            ">
                <p style="
                    font-size: 14px;
                    color: var(--color-text-secondary);
                    margin-bottom: var(--spacing-sm);
                ">{metric['name']}</p>
                <p style="
                    font-family: 'Space Grotesk', 'Inter', sans-serif;
                    font-size: 42px;
                    font-weight: 700;
                    color: var(--color-text-title);
                    margin-bottom: var(--spacing-sm);
                    line-height: 1.2;
                ">{metric['value']}</p>
                {delta_html}
            </div>
            ''', unsafe_allow_html=True)

    # 关闭外层卡片容器
    st.markdown("</div>", unsafe_allow_html=True)
