# -*- coding: utf-8 -*-
"""LLM分析功能模块 - 使用AIHubMix Gemini API"""

import os
import streamlit as st
from openai import OpenAI

# AIHubMix API 配置 - 从环境变量读取，默认值保留向后兼容
AIHUB_API_KEY = os.getenv("AIHUB_API_KEY", "sk-B3dOLsy6g9wA6wLJ8177A66aEb4348Ed843847Dc1b0eCb05")
AIHUB_BASE_URL = "https://aihubmix.com/v1"

# 创建 OpenAI 客户端
client = OpenAI(api_key=AIHUB_API_KEY, base_url=AIHUB_BASE_URL)

# LLM 模型配置
LLM_MODEL = "coding-minimax-m2.7-free"

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

    profile = """## 📋 用户画像报告

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
