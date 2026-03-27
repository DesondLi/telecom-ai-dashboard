# -*- coding: utf-8 -*-
"""风险警示条组件 - 根据风险等级显示对应颜色的警示条"""

import streamlit as st

def get_risk_info(user_data):
    """
    根据用户数据判断风险等级并返回对应信息
    返回: (risk_text, bg_color, text_color, icon)
    """
    tags = str(user_data.get("客服行动标签", ""))
    escalated = user_data.get("越级次数", 0)

    if "🚨" in tags or escalated >= 1:
        return (
            "🔴 🚨 高危用户 - 请优先安排处理",
            "#FFEBEE",
            "#B71C1C"
        )
    elif "🔥" in tags or "❌" in tags:
        return (
            "🟠 ⚠️ 中危用户 - 建议尽快处理",
            "#FFF3E0",
            "#E65100"
        )
    elif "⚠️" in tags or "⚡" in tags:
        return (
            "🟡 ⚾ 关注用户 - 定期跟进观察",
            "#FFFDE7",
            "#F57F17"
        )
    else:
        return (
            "🟢 ✅ 低风险用户 - 按常规流程处理",
            "#E8F5E9",
            "#2E7D32"
        )

def render_risk_banner(user_data):
    """渲染风险等级警示条"""
    risk_text, bg_color, text_color = get_risk_info(user_data)

    st.markdown(f"""
    <div style="
        width: 100%;
        height: 48px;
        background-color: {bg_color};
        color: {text_color};
        border-radius: 8px;
        display: flex;
        align-items: center;
        padding: 0 16px;
        margin-bottom: 24px;
        font-size: 14px;
        font-weight: 500;
        box-sizing: border-box;
    ">
        {risk_text}
    </div>
    """, unsafe_allow_html=True)
