# -*- coding: utf-8 -*-
"""风险警示条组件 - 根据风险等级显示对应颜色的警示条，符合新设计系统"""

import streamlit as st

def get_risk_info(user_data):
    """
    根据用户数据判断风险等级并返回信息
    返回: (icon, title, description, css_class)
    """
    tags = str(user_data.get("客服行动标签", ""))
    escalated = user_data.get("越级次数", 0)

    if "🚨" in tags or escalated >= 1:
        return (
            "⚠️",
            "高危用户 - 需要重点关注",
            "该用户有多次投诉记录且包含越级投诉行为",
            "risk-alert risk-alert-critical"
        )
    elif "🔥" in tags or "❌" in tags:
        return (
            "⚠️",
            "中危用户 - 建议尽快处理",
            "用户有多次投诉记录，问题未完全解决",
            "risk-alert risk-alert-warning"
        )
    elif "⚠️" in tags or "⚡" in tags:
        return (
            "ℹ️",
            "关注用户 - 定期跟进观察",
            "用户有投诉记录，需要持续关注",
            "risk-alert risk-alert-watch"
        )
    else:
        return (
            "✅",
            "正常用户 - 按常规流程处理",
            "用户无投诉记录或投诉已圆满解决",
            "risk-alert risk-alert-normal"
        )

def render_risk_banner(user_data):
    """渲染风险等级警示条，符合精致企业科技风设计，与demo完全一致"""
    icon, title, description, css_class = get_risk_info(user_data)

    st.markdown(f'''
    <div class="{css_class}">
        <span class="risk-icon">{icon}</span>
        <div class="risk-content">
            <strong>{title}</strong>
            <span style="opacity: 0.8;">{description}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
