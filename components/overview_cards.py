# -*- coding: utf-8 -*-
"""整体统计概览卡片组件 - 展示全量数据统计信息，使用Streamlit原生布局"""

import streamlit as st
import pandas as pd

def render_overview_cards(df):
    """渲染整体统计概览卡片，使用streamlit原生columns布局"""
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

    # 计算统计数据
    total_users = len(df)

    # 计算高危用户数量
    if "风险等级" in df.columns:
        high_risk = len(df[df["风险等级"] == "高危"])
    else:
        high_risk = df["客服行动标签"].str.contains("🚨").sum()

    # 计算其他类别
    if "距最近投诉天数" in df.columns:
        recent_complaints = len(df[df["距最近投诉天数"] <= 30])
    else:
        recent_complaints = 0

    if "投诉解决率" in df.columns:
        avg_resolution = df["投诉解决率"].mean()
    else:
        avg_resolution = 0

    if "总投诉次数" in df.columns:
        avg_complaints = df["总投诉次数"].mean()
    else:
        avg_complaints = 0

    st.markdown("### 📊 整体统计概览")

    # 使用Streamlit原生columns创建5列布局
    cols = st.columns(5)

    # 定义卡片数据
    cards = [
        {
            "name": "总用户数",
            "value": total_users,
            "emphasize": False
        },
        {
            "name": "高危用户",
            "value": high_risk,
            "emphasize": True
        },
        {
            "name": "本月新增投诉",
            "value": recent_complaints,
            "emphasize": False
        },
        {
            "name": "平均投诉次数",
            "value": f"{avg_complaints:.1f}",
            "emphasize": False
        },
        {
            "name": "解决率",
            "value": f"{avg_resolution:.1f}%" if avg_resolution > 0 else "0%",
            "emphasize": False,
            "good": avg_resolution >= 80
        }
    ]

    # 渲染每个卡片
    for col, card in zip(cols, cards):
        with col:
            if card['emphasize']:
                # 高危卡片特殊样式
                st.markdown(f"""
                <div style="
                    background-color: var(--color-risk-critical-bg);
                    border: 1px solid var(--color-risk-critical-border);
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-md);
                    padding: var(--spacing-md);
                    text-align: center;
                    transition: all 0.2s ease;
                ">
                    <p style="
                        font-size: 13px;
                        font-weight: 400;
                        color: var(--color-risk-critical-text);
                        margin-bottom: var(--spacing-sm);
                    ">{card['name']}</p>
                    <p style="
                        font-family: 'Space Grotesk', 'Inter', sans-serif;
                        font-size: 32px;
                        font-weight: 700;
                        color: var(--color-risk-critical-text);
                        margin: 0;
                    ">{card['value']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif card.get('good'):
                st.markdown(f"""
                <div style="
                    background-color: var(--color-bg-card);
                    border: 1px solid var(--color-border);
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-md);
                    padding: var(--spacing-md);
                    text-align: center;
                    transition: all 0.2s ease;
                ">
                    <p style="
                        font-size: 13px;
                        font-weight: 400;
                        color: var(--color-text-secondary);
                        margin-bottom: var(--spacing-sm);
                    ">{card['name']}</p>
                    <p style="
                        font-family: 'Space Grotesk', 'Inter', sans-serif;
                        font-size: 32px;
                        font-weight: 700;
                        color: var(--color-risk-normal-text);
                        margin: 0;
                    ">{card['value']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background-color: var(--color-bg-card);
                    border: 1px solid var(--color-border);
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-md);
                    padding: var(--spacing-md);
                    text-align: center;
                    transition: all 0.2s ease;
                ">
                    <p style="
                        font-size: 13px;
                        font-weight: 400;
                        color: var(--color-text-secondary);
                        margin-bottom: var(--spacing-sm);
                    ">{card['name']}</p>
                    <p style="
                        font-family: 'Space Grotesk', 'Inter', sans-serif;
                        font-size: 32px;
                        font-weight: 700;
                        color: var(--color-text-title);
                        margin: 0;
                    ">{card['value']}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: var(--spacing-lg);'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
