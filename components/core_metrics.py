# -*- coding: utf-8 -*-
"""核心指标组件 - 展示当前用户的四个核心指标"""

import streamlit as st
import pandas as pd

def get_delta_color(metric_name, value, avg):
    """
    根据指标类型和差值确定颜色
    返回颜色十六进制值
    """
    # 差值
    delta = value - avg

    # 规则:
    # - 投诉次数/越级次数: 高于均值不好 → 红色；低于均值好 → 绿色
    # - 投诉解决率: 高于均值好 → 绿色；低于均值不好 → 红色
    if metric_name in ["总投诉次数", "越级次数"]:
        if delta > 0:
            return "#F44336"  # 不好 - 红色
        elif delta < 0:
            return "#4CAF50"  # 好 - 绿色
        else:
            return "#86909C"
    elif metric_name == "投诉解决率":
        if delta > 0:
            return "#4CAF50"  # 好 - 绿色
        elif delta < 0:
            return "#F44336"  # 不好 - 红色
        else:
            return "#86909C"
    else:
        return "#86909C"

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
    """渲染核心指标卡片网格"""
    st.markdown("### 🎯 核心指标")

    # 创建四列网格
    cols = st.columns(4)

    # 计算平均值
    avg_total = df["总投诉次数"].mean()
    avg_rate = df["投诉解决率"].mean()
    current_total = user_data.get("总投诉次数", 0)
    current_rate = user_data.get("投诉解决率", 0)
    escalated = user_data.get("越级次数", 0)
    escalated_status = "🔴 越级" if escalated > 0 else "🟢 正常"
    recent = user_data.get("距最近投诉天数", 0)

    # 定义指标数据
    metrics = [
        {
            "name": "总投诉次数",
            "value": f"{current_total}",
            "show_delta": True,
            "value_raw": current_total,
            "avg": avg_total
        },
        {
            "name": "投诉解决率",
            "value": f"{current_rate:.1f}%",
            "show_delta": True,
            "value_raw": current_rate,
            "avg": avg_rate
        },
        {
            "name": "越级状态",
            "value": escalated_status,
            "show_delta": False,
            "value_raw": 0,
            "avg": 0
        },
        {
            "name": "距最近投诉",
            "value": f"{recent} 天",
            "show_delta": False,
            "value_raw": 0,
            "avg": 0
        }
    ]

    # 渲染每个指标卡片
    for col, metric in zip(cols, metrics):
        with col:
            if metric['show_delta']:
                delta_text = format_delta(metric['name'], metric['value_raw'], metric['avg'])
                delta_color = get_delta_color(metric['name'], metric['value_raw'], metric['avg'])
                delta_html = f"""
                <div style="font-size: 13px; color: {delta_color}; margin-top: 8px;">
                    {delta_text}
                </div>
                """
            else:
                delta_html = ""

            st.markdown(f"""
            <div style="
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
                margin-bottom: 16px;
            ">
                <div style="font-size: 14px; color: #86909C; font-weight: 400; margin-bottom: 12px;">
                    {metric['name']}
                </div>
                <div style="font-size: 28px; color: #1D2129; font-weight: 700; line-height: 1.2;">
                    {metric['value']}
                </div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
