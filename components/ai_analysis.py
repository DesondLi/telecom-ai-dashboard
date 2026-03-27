# -*- coding: utf-8 -*-
"""AI分析组件 - 双列布局展示投诉诊断和用户画像，默认自动展示"""

import streamlit as st
from utils.llm import explain_complaint_llm, generate_profile_llm

def render_ai_analysis(user_data):
    """渲染AI分析区域，包含投诉诊断和用户画像双列布局"""
    st.markdown("### 🤖 AI 智能分析结果")

    # 整体AI区域容器
    st.markdown("""
    <div style="
        background-color: #FAFCFE;
        border: 1px solid #E3F2FD;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    ">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # 左侧：AI投诉诊断
    with col1:
        st.markdown("#### 🔍 AI投诉诊断")
        st.markdown("""
        <div style="
            background-color: #FFFFFF;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            margin-bottom: 16px;
            min-height: 200px;
        ">
        """, unsafe_allow_html=True)

        # 使用session_state缓存结果，避免重复调用
        if 'diagnosis_result' not in st.session_state or st.session_state.get('current_user') != str(user_data['联系电话']):
            with st.spinner("🤖 AI 正在分析，请稍候..."):
                diagnosis_result = explain_complaint_llm(user_data)
                st.session_state['diagnosis_result'] = diagnosis_result
                st.session_state['current_user'] = str(user_data['联系电话'])
        else:
            diagnosis_result = st.session_state['diagnosis_result']

        # 展示结果
        st.markdown(f'<div style="font-size: 15px; line-height: 1.6; color: #4E5969;">{diagnosis_result}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 重新分析按钮
        if st.button("🔄 重新分析", use_container_width=True, type="primary", key="reanalyze_diagnosis"):
            with st.spinner("🤖 AI 正在重新分析..."):
                diagnosis_result = explain_complaint_llm(user_data)
                st.session_state['diagnosis_result'] = diagnosis_result
                st.experimental_rerun()

    # 右侧：AI用户画像
    with col2:
        st.markdown("#### 📝 AI用户画像")
        st.markdown("""
        <div style="
            background-color: #FFFFFF;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            margin-bottom: 16px;
            min-height: 200px;
        ">
        """, unsafe_allow_html=True)

        # 使用session_state缓存结果
        if 'profile_result' not in st.session_state or st.session_state.get('current_user') != str(user_data['联系电话']):
            with st.spinner("🤖 AI 正在生成画像..."):
                profile_result = generate_profile_llm(user_data)
                st.session_state['profile_result'] = profile_result
        else:
            profile_result = st.session_state['profile_result']

        # 展示结果
        st.markdown(profile_result)

        st.markdown("</div>", unsafe_allow_html=True)

        # 重新生成按钮
        if st.button("🔄 重新生成", use_container_width=True, type="primary", key="regenerate_profile"):
            with st.spinner("🤖 AI 正在重新生成..."):
                profile_result = generate_profile_llm(user_data)
                st.session_state['profile_result'] = profile_result
                st.experimental_rerun()

    # 关闭AI区域容器
    st.markdown("</div>", unsafe_allow_html=True)
