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

        # 用户筛选区域 (P1-01)
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("### 🎯 用户筛选")

        # 风险等级筛选
        risk_options = ["全部", "高危", "中危", "低危", "正常"]
        selected_risk = st.selectbox("风险等级", risk_options, index=0)

        # 客户等级筛选
        if "客户等级" in df.columns:
            customer_levels = ["全部"] + sorted(df["客户等级"].dropna().unique().tolist())
            selected_customer_level = st.selectbox("客户等级", customer_levels, index=0)
        else:
            selected_customer_level = "全部"

        # 投诉次数范围筛选
        if "总投诉次数" in df.columns:
            min_complaint = int(df["总投诉次数"].min())
            max_complaint = int(df["总投诉次数"].max())
            complaint_range = st.slider(
                "投诉次数范围",
                min_value=min_complaint,
                max_value=max_complaint,
                value=(min_complaint, max_complaint)
            )
        else:
            complaint_range = None

        # 清除筛选按钮
        col_clear, _ = st.columns([1, 1])
        with col_clear:
            clear_filters = st.button("清空筛选", key="clear_filters")
            if clear_filters:
                # 清除筛选会触发rerun，通过session_state处理
                for key in ["user_search", "selected_risk", "selected_customer_level", "complaint_range"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()

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

        # 获取所有用户数据并应用多条件筛选
        filtered_df = df.copy()

        # 应用风险等级筛选
        # 需要根据风险等级判断逻辑过滤
        if selected_risk != "全部":
            # 根据现有数据中的风险相关特征判断
            # 假设风险等级由多个特征综合判断，这里简化处理
            if selected_risk == "高危":
                filtered_df = filtered_df[filtered_df["越级次数"] >= 1]
            elif selected_risk == "中危":
                filtered_df = filtered_df[(filtered_df["越级次数"] == 0) & (filtered_df["总投诉次数"] >= 3)]
            elif selected_risk == "低危":
                filtered_df = filtered_df[(filtered_df["越级次数"] == 0) & (filtered_df["总投诉次数"] >= 1) & (filtered_df["总投诉次数"] < 3)]
            elif selected_risk == "正常":
                filtered_df = filtered_df[filtered_df["总投诉次数"] == 0]

        # 应用客户等级筛选
        if selected_customer_level != "全部" and "客户等级" in df.columns:
            filtered_df = filtered_df[filtered_df["客户等级"] == selected_customer_level]

        # 应用投诉次数范围筛选
        if complaint_range is not None and "总投诉次数" in df.columns:
            filtered_df = filtered_df[
                (filtered_df["总投诉次数"] >= complaint_range[0]) &
                (filtered_df["总投诉次数"] <= complaint_range[1])
            ]

        # 应用关键词搜索过滤
        if search_query:
            filtered_df = filtered_df[
                filtered_df["联系电话"].astype(str).str.lower().str.contains(search_query.lower())
            ]

        # 获取过滤后的用户列表
        filtered_users = filtered_df["联系电话"].unique().tolist()

        # 用户选择下拉框
        if filtered_users:
            # 如果之前有选中的用户，尝试保持选择
            if "current_user" in st.session_state and st.session_state["current_user"] in filtered_users:
                default_index = filtered_users.index(st.session_state["current_user"])
            else:
                default_index = 0

            selected_user = st.selectbox(
                "选择目标用户",
                filtered_users,
                index=default_index,
                key="user_select"
            )
        else:
            st.markdown("""
            <div style="text-align: center; padding: 20px 10px; background: #F5F7FA; border-radius: 8px;">
                <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
                <div style="font-size: 14px; color: #86909C;">当前筛选条件下没有匹配的用户</div>
                <div style="font-size: 12px; color: #C9CDD4; margin-top: 4px;">请尝试调整筛选条件</div>
            </div>
            """, unsafe_allow_html=True)
            selected_user = None

        st.markdown('</div>', unsafe_allow_html=True)

        # 收藏功能 (P1-06)
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("### ⭐ 收藏用户")

        # 初始化收藏列表
        if 'favorite_users' not in st.session_state:
            st.session_state['favorite_users'] = []

        # 显示收藏列表
        if st.session_state['favorite_users']:
            for fav_user in st.session_state['favorite_users']:
                col_fav, col_del = st.columns([3, 1])
                with col_fav:
                    if st.button(f"📞 {fav_user}", key=f"fav_{fav_user}", use_container_width=True):
                        # 点击收藏用户快速切换
                        selected_user = fav_user
                        st.session_state["current_user"] = fav_user
                with col_del:
                    if st.button("🗑️", key=f"del_{fav_user}", use_container_width=True):
                        st.session_state['favorite_users'].remove(fav_user)
                        st.experimental_rerun()
        else:
            st.markdown("""
            <div style="font-size: 13px; color: #86909C; text-align: center; padding: 10px;">
                点击用户详情页的星标可收藏常用用户
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 添加帮助信息区域 (折叠)
        with st.expander("❓ 使用帮助", expanded=False):
            st.markdown("""
            <div style="font-size: 13px; line-height: 1.6; color: #4E5969;">
            <p><strong>功能说明:</strong></p>
            <ul>
                <li><b>数据源选择:</b> 选择增强版宽表或模拟数据</li>
                <li><b>用户筛选:</b> 按风险等级、客户等级、投诉次数筛选</li>
                <li><b>搜索用户:</b> 输入关键词快速定位目标用户</li>
                <li><b>收藏用户:</b> 在详情页点击星标收藏</li>
                <li><b>风险警示:</b> 顶部条颜色表示风险等级</li>
                <li><b>AI分析:</b> 自动生成诊断和用户画像</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        return selected_user, data_source
