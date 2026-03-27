# -*- coding: utf-8 -*-
"""数据加载工具模块"""

import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_enhanced_data(file_path):
    """加载增强版特征标签宽表"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"加载失败: {e}")
        return None

@st.cache_data
def generate_mock_data(n=500):
    """生成模拟数据用于演示"""
    np.random.seed(42)

    mock_data = {
        "联系电话": [f"用户_{i:04d}" for i in range(n)],
        "客户标识": [f"C{i:06d}" for i in np.random.randint(100000, 999999, n)],
        "重点服务客户等级": np.random.choice(["普通", "银卡", "金卡", "钻石"], n, p=[0.5, 0.3, 0.15, 0.05]),
        "总投诉次数": np.random.poisson(1.5, n),
        "已解决数": np.random.poisson(1.2, n),
        "投诉解决率": np.random.uniform(50, 100, n).round(1),
        "近7天投诉": np.random.poisson(0.3, n),
        "近30天投诉": np.random.poisson(0.8, n),
        "距最近投诉天数": np.random.randint(0, 90, n),
        "越级次数": np.random.poisson(0.1, n),
        "越级占比": np.random.uniform(0, 50, n).round(1),
        "最常投诉类型": np.random.choice(["资费投诉", "网络问题", "服务态度", "业务办理", "其他"], n),
        "投诉类型广度": np.random.randint(1, 4, n),
        "流转总次数": np.random.poisson(0.5, n),
        "涉及流水号数": np.random.randint(1, 6, n),
        "OAO办理次数": np.random.poisson(0.8, n),
        "退订次数": np.random.poisson(0.3, n),
        "客服行动标签": ["✅ 常规跟进"] * n,
        "投诉处理地": np.random.choice(["杭州", "宁波", "温州", "嘉兴", "绍兴"], n),
        "落地支局": np.random.choice(["支局A", "支局B", "支局C", "支局D"], n),
        "问题是否解决(是/否)": np.random.choice(["是", "否"], n, p=[0.8, 0.2])
    }

    df = pd.DataFrame(mock_data)

    # 生成更真实的标签
    for idx, row in df.iterrows():
        tags = []
        if row["越级次数"] >= 1:
            tags.append("🚨 高危越级预警")
        elif row["近7天投诉"] >= 2:
            tags.append("🔥 情绪爆发/极易怒")
        elif row["近30天投诉"] >= 3:
            tags.append("⚠️ 高频投诉用户")

        if row["投诉类型广度"] >= 3:
            tags.append("🌐 多点不满/需全面诊断")
        if row["流转总次数"] >= 1:
            tags.append("⏳ 多次流转/处理困难")

        if row["投诉解决率"] < 50:
            tags.append("❌ 投诉积压/未解决")
        elif row["距最近投诉天数"] <= 3:
            tags.append("🆕 新投诉/需及时处理")

        if "资费" in str(row["最常投诉类型"]):
            tags.append("💰 资费极度敏感")
        elif "网络" in str(row["最常投诉类型"]):
            tags.append("📶 网络体验受损")

        if row["OAO办理次数"] >= 3:
            tags.append("📋 OAO高频办理")
        if row["退订次数"] >= 2:
            tags.append("⚡ 高频退订用户")

        if row["总投诉次数"] >= 5:
            tags.append("📊 老客户/历史问题多")
        elif row["总投诉次数"] == 1:
            tags.append("🆕 新投诉用户/首次接触")

        if not tags:
            tags.append("✅ 常规跟进")

        df.at[idx, "客服行动标签"] = " | ".join(tags)

    return df
