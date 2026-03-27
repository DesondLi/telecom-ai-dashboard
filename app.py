# -*- coding: utf-8 -*-
"""
电信AI数据治理与用户画像分析系统 v2.0
基于增强版特征标签宽表
使用 AIHubMix Gemini API
"""

import pandas as pd
import numpy as np
import streamlit as st
from openai import OpenAI

# AIHubMix API 配置
AIHUB_API_KEY = "sk-B3dOLsy6g9wA6wLJ8177A66aEb4348Ed843847Dc1b0eCb05"
AIHUB_BASE_URL = "https://aihubmix.com/v1"

# 创建 OpenAI 客户端
client = OpenAI(api_key=AIHUB_API_KEY, base_url=AIHUB_BASE_URL)

# LLM 模型配置
LLM_MODEL = "coding-minimax-m2.7-free"

# =====================================
# 数据血缘配置
# =====================================
DATA_LINEAGE = {
    "投诉受理清单": ["联系电话", "投诉类型", "投诉单状态", "是否提级处理"],
    "OAO清单": ["设备号", "业务类型", "状态"],
    "增值业务退订": ["客户标识", "退订订单号", "订单退订状态"],
    "IVVR概述": ["呼叫流水号", "接触编码"],
    "热词概述": ["流水号", "热词", "关键词"]
}

def render_lineage_graphviz():
    dot_code = """
    digraph G {
        rankdir=LR;
        node [shape=box, style="filled,rounded", color="#E1F5FE", fontname="Microsoft YaHei"];
        edge [color="#BDBDBD"];
        
        subgraph cluster_sources {
            label = "业务源系统";
            style = dashed;
            color = "#BDBDBD";
            投诉受理清单 [label="投诉受理清单", shape=cylinder, fillcolor="#FFF9C4"];
            OAO清单 [label="OAO清单", shape=cylinder, fillcolor="#FFF9C4"];
            增值业务退订 [label="增值业务退订", shape=cylinder, fillcolor="#FFF9C4"];
            IVVR概述 [label="IVVR概述", shape=cylinder, fillcolor="#FFF9C4"];
            热词概述 [label="热词概述", shape=cylinder, fillcolor="#FFF9C4"];
        }

        subgraph cluster_governance {
            label = "AI 数据治理层 (增强版宽表)";
            fillcolor = "#F5F5F5";
            style = filled;
            base_info [label="基础信息\n(电话, 客户标识, 等级)"];
            complaint_stats [label="投诉统计\n(次数, 解决率, 越级)"];
            flow_tracking [label="流转追踪\n(流水号, 部门流转)"];
            business_tags [label="业务标签\n(OAO, 退订, 类型)"];
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

        AI_Wide_Table [label="增强版宽表", shape=component, fillcolor="#C8E6C9"];
        AI_Wide_Table -> AI_Profile [label="驱动"];
        AI_Wide_Table -> AI_Anomaly [label="诊断"];

        AI_Profile [label="🤖 AI 用户画像报告", fillcolor="#BBDEFB"];
        AI_Anomaly [label="🔍 AI 异常诊断分析", fillcolor="#FFCCBC"];
    }
    """
    st.graphviz_chart(dot_code)

st.set_page_config(
    page_title="电信AI数据治理与画像 v2.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# 数据加载
# =====================================
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

# =====================================
# LLM 分析功能 - 使用 Gemini API
# =====================================
def call_llm(prompt, system_prompt=None):
    """调用 LLM API"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API调用失败: {str(e)}")
        return None

def explain_complaint_llm(row):
    """使用Gemini分析投诉用户"""
    metrics_desc = f"""
- 联系电话: {row.get('联系电话', '未知')}
- 客户等级: {row.get('重点服务客户等级', '未知')}
- 总投诉次数: {row.get('总投诉次数', 0)} 次
- 投诉解决率: {row.get('投诉解决率', 0):.1f}%
- 越级次数: {row.get('越级次数', 0)} 次
- 最常投诉类型: {row.get('最常投诉类型', '未知')}
- 流转次数: {row.get('流转总次数', 0)}
- OAO办理次数: {row.get('OAO办理次数', 0)}
- 退订次数: {row.get('退订次数', 0)}
"""

    prompt = f"""你是一名电信行业的资深客服管理专家。请根据以下用户投诉画像，分析特点并给出处理建议。

用户投诉画像：
{metrics_desc}
客服行动标签：{row.get('客服行动标签', '无')}

请按以下格式回复：
1. 用户特征分析（30字以内）
2. 风险等级评估
3. 客服处理建议（2-3条）
"""

    result = call_llm(prompt)
    if result:
        return result
    return generate_local_explanation(row)
    
def generate_local_explanation(row):
    """本地生成分析建议（当API不可用时）"""
    tags = str(row.get('客服行动标签', ''))
    total = row.get('总投诉次数', 0)
    resolution = row.get('投诉解决率', 0)
    complaint_type = str(row.get('最常投诉类型', '未知'))
    recent = row.get('距最近投诉天数', 0)
    escalated = row.get('越级次数', 0)
    
    risk_level = "高危" if escalated > 0 else ("中高危" if '🔥' in tags or '❌' in tags else ("中等" if '⚡' in tags or '⚠️' in tags else "低风险"))
    
    return f"""【用户特征分析】
该用户总投诉{total}次，解决率{resolution:.1f}%，主要投诉类型为{complaint_type}，距最近投诉{recent}天。

【风险等级】{"🔴" if risk_level=="高危" else "🟠" if "中高" in risk_level else "🟡" if risk_level=="中等" else "🟢"} {risk_level}

【客服处理建议】
1. 根据投诉历史制定个性化处理方案
2. 主动联系用户了解真实诉求
3. 建立跟踪档案确保问题闭环"""

def generate_profile_llm(row):
    """使用Gemini生成用户画像"""
    metrics_desc = f"""
- 联系电话: {row.get('联系电话', '未知')}
- 客户等级: {row.get('重点服务客户等级', '未知')}
- 总投诉次数: {row.get('总投诉次数', 0)} 次
- 投诉解决率: {row.get('投诉解决率', 0):.1f}%
- 越级次数: {row.get('越级次数', 0)} 次
- 最常投诉类型: {row.get('最常投诉类型', '未知')}
- 投诉类型广度: {row.get('投诉类型广度', 0)} 种
- 流转次数: {row.get('流转总次数', 0)}
- 距最近投诉: {row.get('距最近投诉天数', 0)} 天
"""

    prompt = f"""你是电信运营商的CRM专家。基于以下用户投诉数据，生成用户画像和服务建议。

用户信息：{metrics_desc}
标签：{row.get('客服行动标签', '无')}

请生成一份详细的用户画像报告，包含：
1. 用户速写（一句话概括）
2. 投诉模式分析
3. 服务策略建议（分短期、中期、长期三个阶段，每阶段3条建议）
"""

    result = call_llm(prompt)
    if result:
        return result
    return generate_local_profile(row)

def generate_local_profile(row):
    """本地生成用户画像（当API不可用时）"""
    tags = str(row.get('客服行动标签', ''))
    total = row.get('总投诉次数', 0)
    complaint_type = str(row.get('最常投诉类型', '未知'))
    resolution = row.get('投诉解决率', 0)
    flow = row.get('流转总次数', 0)
    oao = row.get('OAO办理次数', 0)
    unsub = row.get('退订次数', 0)
    recent = row.get('距最近投诉天数', 0)
    
    profile = f"""## 📋 用户画像报告

### 1️⃣ 用户速写
"""
    
    if '🚨' in tags:
        profile += f"该用户为**高危越级投诉用户**，存在越级投诉记录，需重点关注和优先处理。该用户历史投诉{total}次，解决率{resolution:.1f}%，主要反映{complaint_type}问题。"
    elif '🔥' in tags:
        profile += f"该用户为**情绪激动型投诉用户**，近期投诉频繁，需要及时安抚和处理。该用户历史投诉{total}次，解决率{resolution:.1f}%，建议优先安排经验丰富的客服跟进。"
    elif '❌' in tags:
        profile += f"该用户为**投诉积压用户**，存在历史未解决的投诉问题，需要专项跟进。该用户历史投诉{total}次，但解决率仅{resolution:.1f}%，需重点解决历史遗留问题。"
    elif total >= 5:
        profile += f"该用户为**老客户高频投诉用户**，有{total}次投诉记录，服务粘性较差。该用户曾办理{oao}次OAO业务，退订{unsub}次，业务行为波动较大。"
    elif total == 1:
        profile += f"该用户为**新投诉用户**，首次接触投诉，距今{recent}天，需抓住机会提供优质服务体验，争取转为忠诚用户。"
    else:
        profile += f"该用户为**常规投诉用户**，投诉{total}次，解决率{resolution:.1f}%，主要反映{complaint_type}问题，可按标准流程处理。"
    
    profile += f"""

### 2️⃣ 投诉模式分析

| 指标 | 数值 | 解读 |
|------|------|------|
| 总投诉次数 | {total} 次 | {'频率较高' if total >= 3 else '频率正常'} |
| 投诉解决率 | {resolution:.1f}% | {'偏低需关注' if resolution < 70 else '正常水平'} |
| 主要投诉类型 | {complaint_type} | 核心诉求方向 |
| 越级记录 | {'有' if '🚨' in tags else '无'} | {'高风险信号' if '🚨' in tags else '正常'} |
| 流转次数 | {flow} 次 | {'多次转办处理困难' if flow > 0 else '一次处理'} |
| OAO办理 | {oao} 次 | {'业务办理活跃' if oao > 2 else '一般'} |
| 退订次数 | {unsub} 次 | {'流失风险较高' if unsub > 1 else '基本稳定'} |
"""
    
    profile += """
### 3️⃣ 服务策略建议

"""

    if '🚨' in tags:
        profile += f"""**短期行动（立即执行）：**
1. 立即升级至高级客服或管理人员亲自跟进，24小时内主动联系用户致歉
2. 成立专项处理小组，召集相关部门分析越级原因，制定针对性解决方案
3. 记录用户诉求，承诺明确的处理时间节点（不超过48小时）

**中期跟进（1-2周）：**
1. 每周至少主动联系用户一次，汇报处理进展
2. 协调技术/网络/业务等部门联合诊断问题根源
3. 评估是否需要补偿方案（如话费减免、业务优惠等）

**长期维护（1个月以上）：**
1. 建立专属客服档案，后续投诉优先分配
2. 定期关怀回访，节日生日祝福等情感维护
3. 考虑纳入VIP客户管理体系"""
    elif '🔥' in tags:
        profile += f"""**短期行动（立即执行）：**
1. 安排经验丰富、沟通能力强的资深客服优先处理
2. 准备好用户历史投诉记录，主动说明已在关注中
3. 采用"先听再说"的沟通策略，先让用户充分表达情绪

**中期跟进（1-2周）：**
1. 承诺限时处理（48小时内给出初步方案）
2. 处理完成后48小时内主动回访确认满意度
3. 建立重点关注名单，持续跟踪1-3个月

**长期维护（1个月以上）：**
1. 定期主动关怀（每周一次电话或短信）
2. 提供专属服务通道（如经理热线）
3. 考虑积分/权益等长期激励计划"""
    elif '💰' in tags:
        profile += f"""**短期行动（立即执行）：**
1. 调取用户近6个月账单明细，逐项核查收费情况
2. 如发现异常收费，主动提出退还或抵扣方案
3. 准备相关业务资费和套餐资料，详细解释收费依据

**中期跟进（1-2周）：**
1. 推荐更合适的套餐方案，降低月费支出
2. 如用户有高额漫游/增值业务需求，可考虑包年优惠
3. 设置费用预警服务，主动提醒超额风险

**长期维护（1个月以上）：**
1. 每月主动推送账单明细和分析报告
2. 新业务推广时充分告知收费规则
3. 提供专属客服跟进费用相关问题"""
    elif '📶' in tags:
        profile += f"""**短期行动（立即执行）：**
1. 协调网络部门查询该区域网络状况和设备状态
2. 如是用户设备问题，安排技术人员远程或上门检测
3. 提供临时解决方案（如信号增强器等）

**中期跟进（1-2周）：**
1. 网络部门现场勘测，评估改善方案
2. 如短期内无法彻底解决，提供替代服务方案
3. 定期反馈网络优化进展

**长期维护（1个月以上）：**
1. 跟踪网络改善效果
2. 定期上门检测设备状态
3. 考虑更换更优质的网络服务计划"""
    else:
        profile += f"""**短期行动（立即执行）：**
1. 按标准投诉处理流程，在规定时限内完成处理
2. 处理完成后主动联系用户确认满意度
3. 如用户有后续问题，保持沟通渠道畅通

**中期跟进（1-2周）：**
1. 一周内进行满意度回访
2. 如问题涉及业务优化，收集反馈提交相关部门
3. 记录用户建议作为服务改进参考

**长期维护（1个月以上）：**
1. 如用户为高价值客户，考虑建立专属服务关系
2. 新业务/优惠活动可优先通知
3. 定期关怀维护，提升客户忠诚度"""
    
    return profile

# =====================================
# 加载自定义CSS
# =====================================
def load_css(css_path):
    """加载外部CSS文件"""
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# 加载基础样式表
load_css('static/style.css')

# 保留原有的标签样式兼容
st.markdown("""
<style>
    /* 兼容现有标签样式 */
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .tag {
        display: inline-block;
        background-color: #F5F7FA;
        color: #4E5969;
        font-size: 14px;
        font-weight: 500;
        line-height: 1.4;
        padding: 6px 16px;
        border-radius: 20px;
    }
    .tag-critical { background-color: #FFEBEE; color: #B71C1C; }
    .tag-warning { background-color: #FFF3E0; color: #E65100; }
    .tag-success { background-color: #E8F5E9; color: #2E7D32; }
</style>
""", unsafe_allow_html=True)

# =====================================
# 侧边栏
# =====================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("控制面板 v2.0")
    
    st.markdown("### 📊 数据源选择")
    data_source = st.radio(
        "选择数据来源", 
        ["增强版宽表(推荐)", "模拟数据演示"],
        index=0,
        help="增强版包含真实投诉数据清洗后的特征"
    )
    
    # 加载数据
    if data_source == "增强版宽表(推荐)":
        df = load_enhanced_data("投诉业务_特征与标签宽表_增强版.xlsx")
        if df is not None:
            st.success(f"✅ 已加载 {len(df)} 个用户")
    else:
        df = generate_mock_data(500)
        st.info("📝 使用模拟数据进行演示")
    
    if df is None:
        st.error("无法加载数据，请检查文件是否存在")
        st.stop()
    
    st.markdown("---")
    st.markdown("### 🔍 用户选择")
    
    # 用户选择器
    user_options = df["联系电话"].unique().tolist()
    selected_user = st.selectbox("选择用户", user_options, index=0)
    
    st.markdown("---")
    st.markdown("### 📈 统计概览")
    
    # 计算统计
    total_users = len(df)
    high_risk = df["客服行动标签"].str.contains("🚨").sum()
    emotional = df["客服行动标签"].str.contains("🔥").sum()
    unsolved = df["客服行动标签"].str.contains("❌").sum()
    avg_resolution = df["投诉解决率"].mean()
    
    st.metric("用户总数", f"{total_users}")
    st.metric("高危越级", f"{high_risk}", delta_color="inverse")
    st.metric("情绪爆发", f"{emotional}", delta_color="inverse")
    st.metric("投诉积压", f"{unsolved}", delta_color="inverse")
    st.metric("平均解决率", f"{avg_resolution:.1f}%", delta_color="normal")

# =====================================
# 主界面
# =====================================
user_data = df[df["联系电话"] == selected_user].iloc[0]

st.title("🧠 AI数据治理与投诉用户画像分析")
st.markdown(f"**当前分析用户:** `{selected_user}`")

# 第一行：核心指标
col1, col2, col3, col4 = st.columns(4)

with col1:
    total = user_data.get("总投诉次数", 0)
    st.metric("总投诉次数", f"{total}", 
              delta=f"{total - df['总投诉次数'].mean():.1f} vs Avg",
              delta_color="inverse")

with col2:
    rate = user_data.get("投诉解决率", 0)
    st.metric("投诉解决率", f"{rate:.1f}%",
              delta=f"{rate - df['投诉解决率'].mean():.1f}%",
              delta_color="normal" if rate >= 50 else "inverse")

with col3:
    escalated = user_data.get("越级次数", 0)
    status = "🔴 越级" if escalated > 0 else "🟢 正常"
    st.metric("越级状态", status)

with col4:
    recent = user_data.get("距最近投诉天数", 0)
    st.metric("距最近投诉", f"{recent} 天")

# 第二行：详细信息
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("📊 投诉指标详情")
    
    metrics = {
        "近7天投诉": user_data.get("近7天投诉", 0),
        "近30天投诉": user_data.get("近30天投诉", 0),
        "越级次数": user_data.get("越级次数", 0),
        "越级占比": user_data.get("越级占比", 0),
        "投诉类型广度": user_data.get("投诉类型广度", 0),
        "流转总次数": user_data.get("流转总次数", 0),
        "涉及流水号数": user_data.get("涉及流水号数", 0)
    }
    
    chart_data = pd.DataFrame({
        "指标": list(metrics.keys()),
        "用户值": list(metrics.values()),
        "平均值": [df[k].mean() for k in metrics.keys()]
    }).set_index("指标")
    
    st.bar_chart(chart_data)

with c2:
    st.subheader("🏷️ 客服行动标签")
    
    tags = user_data.get("客服行动标签", "无")
    st.markdown(f"**当前标签:**")
    
    # 标签展示
    tag_list = tags.split(" | ") if " | " in tags else [tags]
    tag_html = ""
    for tag in tag_list:
        if "🚨" in tag or "❌" in tag:
            color_class = "tag-critical"
        elif "🔥" in tag or "⚠️" in tag:
            color_class = "tag-warning"
        elif "✅" in tag:
            color_class = "tag-success"
        else:
            color_class = ""
        tag_html += f'<span class="tag {color_class}">{tag}</span>'
    
    st.markdown(f'<div class="tag-container">{tag_html}</div>', unsafe_allow_html=True)
    
    # 业务信息
    st.markdown("---")
    st.markdown("**📋 业务信息**")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.write(f"最常投诉: `{user_data.get('最常投诉类型', '未知')}`")
        st.write(f"OAO办理: `{user_data.get('OAO办理次数', 0)}` 次")
    with col_b2:
        st.write(f"退订次数: `{user_data.get('退订次数', 0)}` 次")
        st.write(f"客户等级: `{user_data.get('重点服务客户等级', '未知')}`")
    
    st.markdown("**📍 处理信息**")
    st.write(f"处理地: `{user_data.get('投诉处理地', '未知')}`")
    st.write(f"落地支局: `{user_data.get('落地支局', '未知')}`")

# 第三行：AI分析
st.markdown("---")
st.subheader("🤖 AI 智能分析")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown("**🔍 投诉诊断分析**")
    if st.button("🚀 启动AI诊断", use_container_width=True, key="ai_diagnose"):
        with st.spinner("🤖 AI 正在分析..."):
            result = explain_complaint_llm(user_data)
            st.info(result)
    else:
        st.caption("点击按钮获取AI投诉诊断建议")

with col_ai2:
    st.markdown("**📝 完整用户画像**")
    if st.button("✨ 生成画像报告", type="primary", use_container_width=True, key="ai_profile"):
        with st.spinner("🤖 AI 正在生成..."):
            result = generate_profile_llm(user_data)
            st.markdown(result)
    else:
        st.caption("点击按钮生成完整的AI用户画像报告")

# 底部：数据血缘
st.markdown("---")
with st.expander("🔗 数据血缘追踪", expanded=False):
    st.markdown("增强版宽表由以下数据源汇聚清洗生成：")
    render_lineage_graphviz()

with st.expander("📄 查看用户完整数据"):
    st.json(user_data.astype(str).to_dict())
