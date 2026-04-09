# -*- coding: utf-8 -*-
"""标签展示组件和业务信息网格 - 按风险等级显示彩色标签，符合新设计系统"""

import streamlit as st

def get_tag_class(tag_text):
    """根据标签内容返回对应的CSS类名"""
    if "🚨" in tag_text or "❌" in tag_text:
        return "tag tag-critical"
    elif "🔥" in tag_text or "⚠️" in tag_text or "⚡" in tag_text:
        return "tag tag-warning"
    elif "✅" in tag_text:
        return "tag tag-normal"
    else:
        return "tag tag-neutral"

def render_tags_section(user_data):
    """渲染客服行动标签，业务信息单独全宽展示"""
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

    st.markdown("### 🏷️ 特征标签")

    # 获取标签并分割
    tags = user_data.get("客服行动标签", "无")
    tag_list = tags.split(" | ") if " | " in tags else [tags]

    # 使用CSS类构建标签
    st.markdown('<div class="tag-container">', unsafe_allow_html=True)
    for tag in tag_list:
        if tag.strip():
            css_class = get_tag_class(tag)
            st.markdown('<span class="%s">%s</span>' % (css_class, tag), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_biz_info_fullwidth(user_data):
    """渲染业务信息 - 全宽横向卡片布局，使用Streamlit原生columns"""
    # 外层白色卡片包装
    st.markdown("""
    <div style="
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.1), 0 2px 4px -1px rgba(15, 23, 42, 0.06);
        margin-bottom: 24px;
    ">
    """, unsafe_allow_html=True)

    st.markdown("### 📋 业务信息")

    # 使用 Streamlit 原生 columns 创建6列横向布局
    cols = st.columns(6)

    # 业务信息项列表
    biz_items = [
        {"label": "客户等级", "value": str(user_data.get('重点服务客户等级', '未知'))},
        {"label": "用户状态", "value": str(user_data.get('用户状态', '正常在网'))},
        {"label": "最常投诉类型", "value": str(user_data.get('最常投诉类型', '未知'))},
        {"label": "最近投诉", "value": f"{user_data.get('距最近投诉天数', 0)} 天前"},
        {"label": "OAO办理次数", "value": f"{user_data.get('OAO办理次数', 0)} 次"},
        {"label": "退订次数", "value": f"{user_data.get('退订次数', 0)} 次"},
    ]

    # 在每个列中渲染卡片
    for i, item in enumerate(biz_items):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background-color: var(--color-bg-block);
                border-radius: var(--radius-sm);
                border: 1px solid var(--color-border);
                padding: 12px 8px;
                text-align: center;
            ">
                <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 4px;">{item['label']}</div>
                <div style="font-size: 15px; color: var(--color-text-title); font-weight: 600;">{item['value']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 闭合外层容器
    st.markdown("</div>", unsafe_allow_html=True)
