# -*- coding: utf-8 -*-
"""可折叠扩展区域组件 - 数据血缘追踪和完整原始数据查看"""

import streamlit as st

def render_lineage_graphviz():
    """渲染数据血缘图 - 使用Graphviz可视化"""
    dot_code = """
    digraph G {
        rankdir=LR;
        node [shape=box, style="filled,rounded", fontname="Microsoft YaHei"];
        edge [color="#1E40AF"];

        subgraph cluster_sources {
            label = "业务源系统";
            style = dashed;
            color = "#E2E8F0";
            投诉受理清单 [label="投诉受理清单", shape=cylinder, fillcolor="#EFF6FF", color="#1E40AF"];
            OAO清单 [label="OAO清单", shape=cylinder, fillcolor="#EFF6FF", color="#1E40AF"];
            增值业务退订 [label="增值业务退订", shape=cylinder, fillcolor="#EFF6FF", color="#1E40AF"];
            IVVR概述 [label="IVVR概述", shape=cylinder, fillcolor="#EFF6FF", color="#1E40AF"];
            热词概述 [label="热词概述", shape=cylinder, fillcolor="#EFF6FF", color="#1E40AF"];
        }

        subgraph cluster_governance {
            label = "AI 数据治理层 (增强版宽表)";
            fillcolor = "#F8FAFC";
            style = filled;
            base_info [label="基础信息\n(电话, 客户标识, 等级)", fillcolor="#FFF7ED", color="#F59E0B"];
            complaint_stats [label="投诉统计\n(次数, 解决率, 越级)", fillcolor="#FFF7ED", color="#F59E0B"];
            flow_tracking [label="流转追踪\n(流水号, 部门流转)", fillcolor="#FFF7ED", color="#F59E0B"];
            business_tags [label="业务标签\n(OAO, 退订, 类型)", fillcolor="#FFF7ED", color="#F59E0B"];
        }

        投诉受理清单 -> base_info;
        投诉受理清单 -> complaint_stats;
        投诉受理清单 -> flow_tracking;
        OAO清单 -> business_tags;
        增值业务退订 -> business_tags;

        base_info -> AI_Wide_Table;
        complaint_stats -> AI_Wide_Table;
        flow_tracking -> AI_Wide_Table;
        business_tags -> AI_Wide_Table;

        AI_Wide_Table [label="增强版宽表", shape=component, fillcolor="#F0FDF4", color="#16A34A"];
        AI_Wide_Table -> AI_Profile [label="驱动"];
        AI_Wide_Table -> AI_Anomaly [label="诊断"];

        AI_Profile [label="🤖 AI 用户画像报告", fillcolor="#EFF6FF", color="#1E40AF"];
        AI_Anomaly [label="🔍 AI 异常诊断分析", fillcolor="#EFF6FF", color="#1E40AF"];
    }
    """
    st.graphviz_chart(dot_code, use_container_width=True)

def render_expandable_sections(user_data):
    """渲染两个可折叠扩展区域"""

    # 数据血缘追踪
    with st.expander("🔗 数据血缘追踪", expanded=False):
        st.markdown("""
        <div style="font-size: 14px; color: var(--color-text-body); margin-bottom: 16px; line-height: 1.6;">
            增强版宽表由多个业务源系统汇聚，经过AI数据治理加工生成最终特征标签，支持AI驱动的用户画像和异常诊断。
        </div>
        """, unsafe_allow_html=True)
        render_lineage_graphviz()

    # 查看完整原始数据
    with st.expander("📄 查看用户完整原始数据", expanded=False):
        st.markdown("""
        <div style="font-size: 14px; color: var(--color-text-body); margin-bottom: 16px;">
            显示该用户的所有原始字段数据，用于调试和详细分析。
        </div>
        """, unsafe_allow_html=True)
        # 转换为字典并展示
        st.json(user_data.astype(str).to_dict())
