# -*- coding: utf-8 -*-
"""标签展示组件和业务信息网格 - 按风险等级显示彩色标签"""

import streamlit as st

def get_tag_class(tag_text):
    """根据标签内容返回对应的CSS类和样式"""
    if "🚨" in tag_text or "❌" in tag_text:
        return "background-color: #FFEBEE; color: #B71C1C;"
    elif "🔥" in tag_text or "⚠️" in tag_text:
        return "background-color: #FFF3E0; color: #E65100;"
    elif "✅" in tag_text:
        return "background-color: #E8F5E9; color: #2E7D32;"
    else:
        return "background-color: #F5F7FA; color: #4E5969;"

def render_tags_section(user_data):
    """渲染客服行动标签和业务信息网格"""
    st.markdown("### 🏷️ 客服行动标签")

    # 获取标签并分割
    tags = user_data.get("客服行动标签", "无")
    tag_list = tags.split(" | ") if " | " in tags else [tags]

    # 构建HTML
    tag_html = ""
    for tag in tag_list:
        style = get_tag_class(tag)
        tag_html += f'<span style="display: inline-block; {style} font-size: 14px; font-weight: 500; line-height: 1.4; padding: 6px 16px; border-radius: 20px; margin-right: 8px; margin-bottom: 8px;">{tag}</span>'

    # 渲染标签容器
    st.markdown(
        f'<div style="margin-bottom: 20px;">{tag_html}</div>',
        unsafe_allow_html=True
    )

    # 业务信息网格
    st.markdown("### 📋 业务信息")

    # 两列网格布局
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">最常投诉类型</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('最常投诉类型', '未知')}</div>
        </div>
        <div style="margin-bottom: 16px;">
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">OAO办理次数</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('OAO办理次数', 0)} 次</div>
        </div>
        <div>
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">投诉处理地</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('投诉处理地', '未知')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">退订次数</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('退订次数', 0)} 次</div>
        </div>
        <div style="margin-bottom: 16px;">
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">重点客户等级</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('重点服务客户等级', '未知')}</div>
        </div>
        <div>
            <div style="font-size: 13px; color: #86909C; font-weight: 400; margin-bottom: 4px;">落地支局</div>
            <div style="font-size: 15px; color: #1D2129; font-weight: 500;">{user_data.get('落地支局', '未知')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
