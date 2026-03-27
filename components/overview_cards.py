# -*- coding: utf-8 -*-
"""整体统计概览卡片组件 - 展示全量数据统计信息"""

import streamlit as st
import pandas as pd

def render_overview_cards(df):
    """渲染整体统计概览卡片网格"""
    # 计算统计数据
    total_users = len(df)
    high_risk = df["客服行动标签"].str.contains("🚨").sum()
    emotional = df["客服行动标签"].str.contains("🔥").sum()
    unsolved = df["客服行动标签"].str.contains("❌").sum()
    avg_resolution = df["投诉解决率"].mean()

    st.markdown("### 📊 整体统计概览")

    # 使用Streamlit的columns创建响应式网格
    # Streamlit会自动处理响应式，我们定义5列
    cols = st.columns(5)

    # 定义卡片数据
    cards = [
        {
            "name": "用户总数",
            "value": total_users,
            "icon": "👥"
        },
        {
            "name": "高危越级",
            "value": high_risk,
            "icon": "🚨"
        },
        {
            "name": "情绪爆发",
            "value": emotional,
            "icon": "🔥"
        },
        {
            "name": "投诉积压",
            "value": unsolved,
            "icon": "❌"
        },
        {
            "name": "平均解决率",
            "value": f"{avg_resolution:.1f}%",
            "icon": "✅"
        }
    ]

    # 渲染每个卡片
    for i, (col, card) in enumerate(zip(cols, cards)):
        with col:
            st.markdown(f"""
            <div style="
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                text-align: center;
                margin-bottom: 16px;
            ">
                <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 8px;">
                    {card['icon']} {card['name']}
                </div>
                <div style="font-size: 24px; color: #1D2129; font-weight: 700; line-height: 1.2;">
                    {card['value']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
