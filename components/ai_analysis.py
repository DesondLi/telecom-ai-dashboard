# -*- coding: utf-8 -*-
"""AI分析组件 - 全宽布局展示投诉诊断和用户画像，按钮触发生成"""

import streamlit as st
from utils.llm import explain_complaint_llm, generate_profile_llm, generate_local_explanation, generate_local_profile

def render_ai_analysis(user_data):
    """渲染AI分析区域，包含投诉诊断和用户画像全宽布局，按钮触发生成"""

    # 整体AI区域容器打开
    container_open = """
    <div style="
        background-color: var(--color-primary-ultra-light);
        border: 1px solid var(--color-primary-extra-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-lg);
    ">
    """
    st.markdown(container_open, unsafe_allow_html=True)

    # 标题
    st.markdown("### 🤖 AI 智能分析")

    # 用户ID用于缓存
    user_id = str(user_data['联系电话'])

    # 显示持久化的LLM错误信息
    if 'llm_error' in st.session_state and st.session_state['llm_error'] is not None:
        st.error(f"🤖 LLM API 调用失败: {st.session_state['llm_error']}")

    # AI投诉诊断 - 全宽单列
    st.markdown("#### 🔍 AI投诉诊断")

    # 检查是否已有缓存结果
    has_result = (
        'diagnosis_result' in st.session_state and
        st.session_state.get('ai_analysis_user') == user_id
    )

    # 生成按钮
    if not has_result:
        if st.button("🚀 开始分析投诉", use_container_width=True, type="primary", key="generate_diagnosis"):
            # 清除之前的错误信息
            st.session_state['llm_error'] = None
            with st.spinner("🤖 AI 正在分析，请稍候..."):
                diagnosis_result = explain_complaint_llm(user_data)
                st.session_state['diagnosis_result'] = diagnosis_result
                st.session_state['ai_analysis_user'] = user_id
                st.rerun()
    else:
        # 展示结果
        diagnosis_result = st.session_state['diagnosis_result']
        st.markdown("""
        <div style="
            background-color: var(--color-bg-card);
            border-radius: var(--radius-sm);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--spacing-lg);
            min-height: 100px;
        ">
        """, unsafe_allow_html=True)
        if diagnosis_result is None:
            # API 调用失败，显示本地回退内容，但保留错误提示
            local_result = generate_local_explanation(user_data)
            st.error("⚠️ AI API 调用失败，已使用本地分析。请检查网络和 API Key 配置。")
            st.markdown(f'<div style="font-size: 15px; line-height: 1.7; color: var(--color-text-body);">{local_result}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="font-size: 15px; line-height: 1.7; color: var(--color-text-body);">{diagnosis_result}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 重新分析按钮
        if st.button("🔄 重新分析", use_container_width=True, key="reanalyze_diagnosis"):
            # 清除之前的错误信息
            st.session_state['llm_error'] = None
            with st.spinner("🤖 AI 正在重新分析..."):
                diagnosis_result = explain_complaint_llm(user_data)
                st.session_state['diagnosis_result'] = diagnosis_result
                st.session_state['ai_analysis_user'] = user_id
                st.rerun()

    # AI用户画像 - 全宽单列（在投诉诊断下方）
    st.markdown("#### 📝 AI用户画像")

    # 检查是否已有缓存结果
    has_profile = (
        'profile_result' in st.session_state and
        st.session_state.get('ai_analysis_user') == user_id
    )

    if not has_profile:
        if st.button("🚀 生成用户画像", use_container_width=True, type="primary", key="generate_profile"):
            # 清除之前的错误信息
            st.session_state['llm_error'] = None
            with st.spinner("🤖 AI 正在生成画像..."):
                profile_result = generate_profile_llm(user_data)
                st.session_state['profile_result'] = profile_result
                st.session_state['ai_analysis_user'] = user_id
                st.rerun()
    else:
        # 展示结果
        profile_result = st.session_state['profile_result']
        st.markdown("""
        <div style="
            background-color: var(--color-bg-card);
            border-radius: var(--radius-sm);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--spacing-md);
            min-height: 100px;
        ">
        """, unsafe_allow_html=True)
        if profile_result is None:
            # API 调用失败，显示本地回退内容，但保留错误提示
            local_result = generate_local_profile(user_data)
            st.error("⚠️ AI API 调用失败，已使用本地生成。请检查网络和 API Key 配置。")
            st.markdown(local_result, unsafe_allow_html=True)
        else:
            st.markdown(profile_result, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 重新生成按钮
        if st.button("🔄 重新生成", use_container_width=True, key="regenerate_profile"):
            # 清除之前的错误信息
            st.session_state['llm_error'] = None
            with st.spinner("🤖 AI 正在重新生成..."):
                profile_result = generate_profile_llm(user_data)
                st.session_state['profile_result'] = profile_result
                st.session_state['ai_analysis_user'] = user_id
                st.rerun()

    # 整体AI区域容器关闭
    st.markdown("</div>", unsafe_allow_html=True)
