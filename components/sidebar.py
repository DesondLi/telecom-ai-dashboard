# -*- coding: utf-8 -*-
"""侧边栏组件 - 重构优化后的侧边栏"""

import streamlit as st
import pandas as pd

def render_sidebar(df):
    """
    渲染重构后的侧边栏
    返回: (selected_user, df) - 选中的用户和数据框
    """
    with st.sidebar:
        # 品牌区域
        st.markdown("""
        <div style="text-align: center; padding: 8px 0 16px 0; border-bottom: 1px solid #E5E6EB; margin-bottom: 16px;">
            <img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" width="64" style="margin-bottom: 8px;">
            <h2 style="margin: 0; font-size: 18px; font-weight: 600; color: #1D2129;">🧠 电信AI数据治理</h2>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #86909C;">用户投诉智能分析系统</p>
        </div>
        """, unsafe_allow_html=True)

        # 数据源选择区域
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("### 📊 数据源选择")
        data_source = st.radio(
            "选择数据来源",
            ["增强版宽表(推荐)", "模拟数据演示"],
            index=0,
            help="增强版包含真实投诉数据清洗后的特征"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 用户搜索区域
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("### 🔍 搜索用户")

        # 搜索框
        search_query = st.text_input(
            "输入电话号码或用户名搜索",
            placeholder="搜索用户...",
            key="user_search"
        )

        # 根据搜索过滤用户列表
        all_users = df["联系电话"].unique().tolist()

        if search_query:
            filtered_users = [
                user for user in all_users
                if search_query.lower() in str(user).lower()
            ]
        else:
            filtered_users = all_users

        # 用户选择下拉框
        if filtered_users:
            selected_user = st.selectbox(
                "选择目标用户",
                filtered_users,
                index=0,
                key="user_select"
            )
        else:
            st.markdown("""
            <div style="text-align: center; padding: 20px 10px; background: #F5F7FA; border-radius: 8px;">
                <div style="font-size: 24px; margin-bottom: 8px;">🔍</div>
                <div style="font-size: 14px; color: #86909C;">未找到匹配的用户</div>
                <div style="font-size: 12px; color: #C9CDD4; margin-top: 4px;">请尝试其他关键词</div>
            </div>
            """, unsafe_allow_html=True)
            selected_user = None

        st.markdown('</div>', unsafe_allow_html=True)

        # 添加帮助信息区域 (折叠)
        with st.expander("❓ 使用帮助", expanded=False):
            st.markdown("""
            <div style="font-size: 13px; line-height: 1.6; color: #4E5969;">
            <p><strong>功能说明:</strong></p>
            <ul>
                <li><b>数据源选择:</b> 选择增强版宽表或模拟数据</li>
                <li><b>搜索用户:</b> 输入关键词快速定位目标用户</li>
                <li><b>风险警示:</b> 顶部条颜色表示风险等级</li>
                <li><b>AI分析:</b> 自动生成诊断和用户画像</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        return selected_user, data_source
