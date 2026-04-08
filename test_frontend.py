"""
telecom-cli LLM 调度测试前端
独立应用，不修改 telecom_agent_demo 原有代码
支持：1. clean_and_merge 表合并  2. build_oneid OneID身份归一化
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

# 导入配置（优先从环境变量读取，支持 Streamlit Cloud Secrets）
AIHUBMIX_API_KEY = os.environ.get('AIHUBMIX_API_KEY', '')
AIHUBMIX_BASE_URL = os.environ.get('AIHUBMIX_BASE_URL', 'https://aihubmix.com/v1')
AIHUBMIX_MODEL = os.environ.get('AIHUBMIX_MODEL', 'gpt-4o-mini')
DATA_DIR = os.environ.get('DATA_DIR', './线下表数据')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', './test_output')

# 如果本地有 config.py，覆盖环境变量配置（方便本地开发）
try:
    import config
    if hasattr(config, 'AIHUBMIX_API_KEY'):
        AIHUBMIX_API_KEY = config.AIHUBMIX_API_KEY
    if hasattr(config, 'AIHUBMIX_BASE_URL'):
        AIHUBMIX_BASE_URL = config.AIHUBMIX_BASE_URL
    if hasattr(config, 'AIHUBMIX_MODEL'):
        AIHUBMIX_MODEL = config.AIHUBMIX_MODEL
    if hasattr(config, 'DATA_DIR'):
        DATA_DIR = config.DATA_DIR
    if hasattr(config, 'OUTPUT_DIR'):
        OUTPUT_DIR = config.OUTPUT_DIR
except ImportError:
    # 没有本地 config.py，使用环境变量（部署环境）
    pass

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 页面设置
st.set_page_config(
    page_title="telecom-cli LLM 测试",
    page_icon="📊",
    layout="wide"
)

st.title("📊 telecom-cli LLM 调度测试")
st.markdown("---")

# 选项卡
tab1, tab2 = st.tabs(["🔗 表合并 (clean_and_merge)", "🆔 OneID归一 (build_oneid)"])

# 初始化 OpenAI 客户端
@st.cache_resource
def get_client():
    if AIHUBMIX_API_KEY:
        return OpenAI(
            api_key=AIHUBMIX_API_KEY,
            base_url=AIHUBMIX_BASE_URL
        )
    return None

client = get_client()

# 扫描线下表数据文件夹
data_path = Path(DATA_DIR)
# 确保目录存在（云端部署时自动创建）
data_path.mkdir(exist_ok=True, parents=True)
if data_path.exists() and any(data_path.iterdir()):
    excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
    excel_files = [f for f in excel_files if not f.name.startswith('~$')]
    excel_names = [f.name for f in excel_files]
else:
    excel_files = []
    excel_names = []
    st.sidebar.info(f"ℹ️ {DATA_DIR} 目录已创建，当前没有数据文件")

# ========== Tab 1: clean_and_merge ==========
with tab1:
    # 侧边栏 - 文件选择
    st.sidebar.header("📁 已有文件 (合并)")

    # 文件上传
    st.sidebar.header("📤 上传新文件")
    uploaded_complaint = st.sidebar.file_uploader("上传客诉表文件", type=['xlsx', 'xls'])
    if uploaded_complaint is not None:
        # 保存上传的文件到 DATA_DIR
        complaint_path = data_path / uploaded_complaint.name
        with open(complaint_path, "wb") as f:
            f.write(uploaded_complaint.getbuffer())
        st.sidebar.success(f"✅ 已保存: {uploaded_complaint.name}")
        # 刷新文件列表
        excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
        excel_files = [f for f in excel_files if not f.name.startswith('~$')]
        excel_names = [f.name for f in excel_files]

    uploaded_oao = st.sidebar.file_uploader("上传OAO表文件", type=['xlsx', 'xls'])
    if uploaded_oao is not None:
        # 保存上传的文件到 DATA_DIR
        oao_path = data_path / uploaded_oao.name
        with open(oao_path, "wb") as f:
            f.write(uploaded_oao.getbuffer())
        st.sidebar.success(f"✅ 已保存: {uploaded_oao.name}")
        # 刷新文件列表
        excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
        excel_files = [f for f in excel_files if not f.name.startswith('~$')]
        excel_names = [f.name for f in excel_files]

    st.sidebar.markdown("---")

    complaint_file = st.sidebar.selectbox(
        "选择客诉表文件",
        excel_names,
        index=next((i for i, f in enumerate(excel_names) if '投诉' in f or '客诉' in f), 0) if excel_names else 0
    ) if excel_names else None

    oao_file = st.sidebar.selectbox(
        "选择OAO表文件",
        excel_names,
        index=next((i for i, f in enumerate(excel_names) if 'OAO' in f or 'oao' in f), 0) if excel_names else 0
    ) if excel_names else None

    st.sidebar.markdown("---")

    # 用户查询
    st.header("💬 自然语言查询 (表合并)")

    user_query_merge = st.text_area(
        "输入你的需求（例如：帮我合并投诉受理清单和OAO清单，用客户标识作为关联主键）",
        height=100,
        placeholder="例如：帮我合并 投诉受理清单0313.xlsx 和 OAO清单.xlsx，使用客户标识关联"
    )

    SYSTEM_PROMPT_MERGE = """你是 telecom-cli 数据处理工具的调度助手。
用户需要合并两个 Excel 表，你需要根据用户的自然语言请求，提取参数并调用 clean_and_merge 工具。

工具定义：
{
  "name": "clean_and_merge",
  "description": "清洗客诉表和 OAO 表并按主键左联接合并",
  "parameters": {
    "complaint_file": "客诉表文件名（在 DATA_DIR 目录下）",
    "oao_file": "OAO表文件名（在 DATA_DIR 目录下）",
    "join_key": "关联主键列名，必须是两个表都存在的列名"
  }
}

当前 DATA_DIR 目录下可用文件列表：
{{files_list}}

请严格按照 JSON 格式回复，格式如下：
{
  "thinking": "简要分析用户需求，说明你选择的参数",
  "action": "clean_and_merge",
  "parameters": {
    "complaint_file": "客诉表文件名",
    "oao_file": "OAO表文件名",
    "join_key": "主键列名"
  }
}

重要：只返回纯 JSON，不要添加任何其他文字、解释、markdown 代码块（```）等内容。直接输出 JSON。
"""

    col1, col2 = st.columns([1, 3])

    with col1:
        run_button_merge = st.button("🚀 执行 LLM 调度", disabled=not client or not excel_files, key="merge_btn")

    def run_clean_and_merge(complaint_filename: str, oao_filename: str, join_key: str) -> dict:
        """
        直接调用 telecom-cli 核心处理函数
        不走 subprocess，避免环境问题
        """
        # 添加 telecom_agent_demo 到 Python 路径
        telecom_dir = os.path.join(os.path.dirname(__file__), 'telecom_agent_demo')
        if telecom_dir not in sys.path:
            sys.path.insert(0, telecom_dir)

        # 导入核心处理函数
        from src.core.data_processor import clean_and_merge, ProcessingResult

        complaint_path = str(Path(DATA_DIR) / complaint_filename)
        oao_path = str(Path(DATA_DIR) / oao_filename)

        try:
            result: ProcessingResult = clean_and_merge(
                complaint_file=complaint_path,
                oao_file=oao_path,
                join_key=join_key,
                output_dir=OUTPUT_DIR
            )
            return result.to_dict()

        except Exception as e:
            return {
                "errcode": 98,
                "errmsg": f"执行失败: {str(e)}"
            }

    if run_button_merge and user_query_merge and client:
        with st.spinner("🧠 LLM 思考中..."):
            # 获取文件列表
            if data_path.exists():
                files_list = "\n".join([f"- {f.name}" for f in excel_files])
            else:
                files_list = "无法读取文件列表"

            # 构建提示词
            prompt = SYSTEM_PROMPT_MERGE.replace("{{files_list}}", files_list)

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query_merge}
            ]

            try:
                # 调用 LLM
                response = client.chat.completions.create(
                    model=AIHUBMIX_MODEL,
                    messages=messages,
                    temperature=0.0
                )

                # 检查响应
                if not response.choices or len(response.choices) == 0:
                    st.error("❌ LLM 返回空响应 choices")
                    st.code(str(response))
                    raise ValueError("Empty response from LLM")

                message = response.choices[0].message
                if not message.content:
                    st.error("❌ LLM 返回空内容 message.content")
                    st.code(str(message))
                    raise ValueError("Empty content from LLM")

                content = message.content.strip()

                # 显示原始内容长度
                st.info(f"LLM 返回内容长度: {len(content)} 字符")

                # 清理 LLM 输出 - 去除 markdown 代码块包裹和 think 标签
                def clean_json_output(text: str) -> str:
                    """清理 LLM 输出，去除：
                    1. ```json ... ``` markdown 代码块包裹
                    2. <think>...</think> 思考过程标签
                    3. 首尾空行
                    """
                    if not text:
                        return ""

                    # 去掉 <think>...</think> 思考过程
                    import re
                    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
                    # 去掉 /* ... */ 风格注释
                    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
                    # 去掉 // 注释（行注释）
                    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)

                    # 处理多种markdown包裹形式
                    lines = text.splitlines()
                    # 去掉首尾空行
                    lines = [line for line in lines if line.strip() != '']
                    if not lines:
                        return ""
                    # 如果第一行是```开头，去掉第一行
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    # 如果最后一行是```结尾，去掉最后一行
                    if lines and lines[-1].strip().startswith('```'):
                        lines = lines[:-1]
                    cleaned = '\n'.join(lines)
                    return cleaned.strip()

                cleaned_content = clean_json_output(content)

                # 显示 LLM 思考过程
                st.subheader("🧠 LLM 分析")
                st.markdown(f"**原始长度:** {len(content)}, **清理后长度:** {len(cleaned_content)}")

                try:
                    if not cleaned_content:
                        st.error("❌ 清理后内容为空")
                        st.markdown("**原始输出:**")
                        st.code(repr(content))
                        raise ValueError("Empty content after cleaning")

                    llm_output = json.loads(cleaned_content)
                    st.json(llm_output)

                    if llm_output.get("action") == "clean_and_merge":
                        params = llm_output["parameters"]

                        st.subheader("⚙️ 执行命令")
                        with st.spinner("⚙️ 数据处理中..."):
                            result = run_clean_and_merge(
                                params["complaint_file"],
                                params["oao_file"],
                                params["join_key"]
                            )

                        st.subheader("📋 执行结果")
                        st.json(result)

                        if result.get("errcode") == 0:
                            st.success(f"""
                            ✅ 处理完成！
                            - 总处理行数: {result['total_processed']}
                            - 剔除空行: {result['dropped_rows']}
                            - 输出文件: {result['output_path']}
                            """)

                            # 检查输出文件是否存在并可预览
                            output_path = Path(result['output_path'])
                            if output_path.exists():
                                # 读取并显示前几行
                                import pandas as pd
                                df_preview = pd.read_excel(output_path, nrows=20)
                                st.subheader("🔍 结果预览（前20行）")
                                st.dataframe(df_preview)

                        elif result.get("errcode") == 1:
                            st.warning("ℹ️ LLM 可以根据 hint 中的实际字段信息重新选择主键进行自我纠错")

                except json.JSONDecodeError as e:
                    st.error(f"❌ LLM 输出不是有效 JSON: {str(e)}")
                    st.markdown("**原始输出（含markdown）:**")
                    st.code(content)
                    st.markdown("**清理后（尝试解析）:**")
                    st.code(cleaned_content if cleaned_content else "(空)")
                    st.markdown("**原始内容repr:**")
                    st.code(repr(content))

            except Exception as e:
                st.error(f"❌ 调用 LLM 失败: {str(e)}")

    elif not client:
        st.info("👈 请先配置 config.py 中的 API Key")

# ========== Tab 2: build_oneid ==========
with tab2:
    # 侧边栏 - 文件选择
    st.sidebar.header("📤 上传新文件 (OneID)")

    # 多文件上传
    uploaded_files = st.sidebar.file_uploader(
        "上传多个Excel文件",
        type=['xlsx', 'xls'],
        accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded in uploaded_files:
            # 保存上传的文件到 DATA_DIR
            file_path = data_path / uploaded.name
            with open(file_path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.sidebar.success(f"✅ 已保存: {uploaded.name}")
        # 刷新文件列表
        excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
        excel_files = [f for f in excel_files if not f.name.startswith('~$')]
        excel_names = [f.name for f in excel_files]

    st.sidebar.markdown("---")
    st.sidebar.header("📁 已有文件 (OneID)")

    selected_files = st.sidebar.multiselect(
        "选择参与OneID构建的文件（多选）",
        excel_names,
        default=[f for f in excel_names if '投诉' in f or 'OAO' in f or '增值' in f][:3] if excel_names else []
    )

    confidence_level = st.sidebar.selectbox(
        "置信度级别",
        ["high", "medium", "low"],
        index=0,
        help="high=仅流水号, medium=+客户标识, low=+手机号"
    )

    st.sidebar.markdown("---")

    # 执行方式选择
    mode = st.radio(
        "执行方式",
        ["🤖 LLM 自然语言", "⚡ 手动直接执行"],
        index=1,
        help="手动执行：直接使用侧边栏选择的文件，不需要 LLM"
    )

    def run_build_oneid(input_files: list, confidence_level: str) -> dict:
        """
        直接调用 OneID 构建核心处理函数
        """
        # 添加 telecom_agent_demo 到 Python 路径
        telecom_dir = os.path.join(os.path.dirname(__file__), 'telecom_agent_demo')
        if telecom_dir not in sys.path:
            sys.path.insert(0, telecom_dir)

        # 导入核心处理函数
        from src.core.oneid_builder import build_oneid, BuildOneIDResult

        input_paths = [str(Path(DATA_DIR) / f) for f in input_files]

        try:
            result: BuildOneIDResult = build_oneid(
                input_files=input_paths,
                confidence_level=confidence_level,
                output_dir=OUTPUT_DIR
            )
            return result.to_dict()

        except Exception as e:
            return {
                "errcode": 98,
                "errmsg": f"执行失败: {str(e)}"
            }

    # ========== 手动直接执行 ==========
    if mode == "⚡ 手动直接执行":
        st.header("⚡ 手动执行 OneID 构建")
        st.info("""
        使用说明：在左侧边栏选择文件和置信度级别，然后点击执行。
        不需要经过 LLM，直接执行，更快更稳定。
        """)

        col1, col2 = st.columns([1, 3])
        with col1:
            run_button_manual = st.button(
                "▶️ 立即执行构建",
                disabled=not selected_files,
                key="oneid_manual_btn"
            )

        if run_button_manual:
            if not selected_files:
                st.error("❌ 请至少选择一个文件")
            else:
                st.subheader("⚙️ 执行参数")
                st.write({
                    "input_files": selected_files,
                    "confidence_level": confidence_level
                })

                st.subheader("⚙️ 执行命令")
                with st.spinner("⚙️ 构建 OneID 中...（可能需要几分钟）"):
                    result = run_build_oneid(selected_files, confidence_level)

                st.subheader("📋 执行结果")
                st.json(result)

                if result.get("errcode") == 0:
                    st.success(f"""
                    ✅ OneID 构建完成！
                    - 总记录数: {result['total_records']}
                    - 唯一 OneID 数量: {result['unique_oneids']}
                    - 输出文件: {result['output_path']}
                    """)

                    # 检查输出文件是否存在并可预览
                    output_path = Path(result['output_path'])
                    if output_path.exists():
                        # 读取并显示前几行
                        import pandas as pd
                        df_preview = pd.read_excel(output_path, nrows=20)
                        st.subheader("🔍 结果预览（前20行）")
                        st.dataframe(df_preview)

                elif result.get("errcode") == 1:
                    st.warning("ℹ️ 找不到预设的身份标识列，请检查文件是否包含流水号")

    # ========== LLM 自然语言查询 ==========
    else:
        # 用户查询
        st.header("💬 自然语言查询 (OneID身份归一)")

        user_query_oneid = st.text_area(
            "输入你的需求（例如：帮我给投诉受理清单、OAO清单、增值业务清单构建OneID，使用高置信度）",
            height=100,
            placeholder="例如：帮我用高置信度给投诉受理清单0313.xlsx 和 OAO清单.xlsx 构建 OneID"
        )

        SYSTEM_PROMPT_ONEID = """你是 telecom-cli 数据处理工具的调度助手。
用户需要从多个 Excel 表构建全域唯一 OneID 身份映射，你需要根据用户的自然语言请求，提取参数并调用 build_oneid 工具。

工具定义：
{
  "name": "build_oneid",
  "description": "OneID身份归一化 - 从多个表格提取客户身份标识，通过规则级联合并生成全域唯一 OneID",
  "parameters": {
    "input_files": "需要参与OneID构建的Excel文件名列表（从上述列表选择）",
    "confidence_level": "置信度级别，控制匹配规则：high(仅流水号匹配)/medium(流水号+客户标识)/low(流水号+客户标识+手机号)，默认 high",
    "output_dir": "输出目录路径，可选，默认为 ./output"
  }
}

置信度级别说明：
- high: 仅通过流水号匹配，准确率最高，召回率最低
- medium: 流水号 + 客户标识匹配，准确率中等，召回率中等
- low: 流水号 + 客户标识 + 手机号匹配，准确率最低，召回率最高

当前 DATA_DIR 目录下可用文件列表：
{{files_list}}

请严格按照 JSON 格式回复，格式如下：
{
  "thinking": "简要分析用户需求，说明你选择的参数",
  "action": "build_oneid",
  "parameters": {
    "input_files": ["文件1.xlsx", "文件2.xlsx", ...],
    "confidence_level": "high"
  }
}

重要：只返回纯 JSON，不要添加任何其他文字、解释、markdown 代码块（```）等内容。直接输出 JSON。
"""

        col1, col2 = st.columns([1, 3])

        with col1:
            run_button_oneid = st.button("🚀 执行 LLM 调度", disabled=not client or not excel_names, key="oneid_btn")

        if run_button_oneid and user_query_oneid and client:
            with st.spinner("🧠 LLM 思考中..."):
                # 获取文件列表
                if data_path.exists():
                    files_list = "\n".join([f"- {f.name}" for f in excel_files])
                else:
                    files_list = "无法读取文件列表"

                # 构建提示词
                prompt = SYSTEM_PROMPT_ONEID.replace("{{files_list}}", files_list)

                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_query_oneid}
                ]

                try:
                    # 调用 LLM
                    response = client.chat.completions.create(
                        model=AIHUBMIX_MODEL,
                        messages=messages,
                        temperature=0.0
                    )

                    # 检查响应
                    if not response.choices or len(response.choices) == 0:
                        st.error("❌ LLM 返回空响应 choices")
                        st.code(str(response))
                        raise ValueError("Empty response from LLM")

                    message = response.choices[0].message
                    if not message.content:
                        st.error("❌ LLM 返回空内容 message.content")
                        st.code(str(message))
                        raise ValueError("Empty content from LLM")

                    content = message.content.strip()

                    # 显示原始内容长度
                    st.info(f"LLM 返回内容长度: {len(content)} 字符")

                    # 清理 LLM 输出
                    def clean_json_output(text: str) -> str:
                        """清理 LLM 输出"""
                        if not text:
                            return ""
                        import re
                        text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
                        text = re.sub(r'/\*[\s\S]*?\*/', '', text)
                        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
                        lines = text.splitlines()
                        lines = [line for line in lines if line.strip() != '']
                        if not lines:
                            return ""
                        if lines[0].startswith('```'):
                            lines = lines[1:]
                        if lines and lines[-1].strip().startswith('```'):
                            lines = lines[:-1]
                        cleaned = '\n'.join(lines)
                        return cleaned.strip()

                    cleaned_content = clean_json_output(content)

                    # 显示 LLM 思考过程
                    st.subheader("🧠 LLM 分析")
                    st.markdown(f"**原始长度:** {len(content)}, **清理后长度:** {len(cleaned_content)}")

                    try:
                        if not cleaned_content:
                            st.error("❌ 清理后内容为空")
                            st.markdown("**原始输出:**")
                            st.code(repr(content))
                            raise ValueError("Empty content after cleaning")

                        llm_output = json.loads(cleaned_content)
                        st.json(llm_output)

                        if llm_output.get("action") == "build_oneid":
                            params = llm_output["parameters"]
                            input_files_param = params.get("input_files", selected_files)
                            confidence_param = params.get("confidence_level", confidence_level)

                            st.subheader("⚙️ 执行命令")
                            with st.spinner("⚙️ 构建 OneID 中...（可能需要几分钟）"):
                                result = run_build_oneid(
                                    input_files_param,
                                    confidence_param
                                )

                            st.subheader("📋 执行结果")
                            st.json(result)

                            if result.get("errcode") == 0:
                                st.success(f"""
                                ✅ OneID 构建完成！
                                - 总记录数: {result['total_records']}
                                - 唯一 OneID 数量: {result['unique_oneids']}
                                - 输出文件: {result['output_path']}
                                """)

                                # 检查输出文件是否存在并可预览
                                output_path = Path(result['output_path'])
                                if output_path.exists():
                                    # 读取并显示前几行
                                    import pandas as pd
                                    df_preview = pd.read_excel(output_path, nrows=20)
                                    st.subheader("🔍 结果预览（前20行）")
                                    st.dataframe(df_preview)

                            elif result.get("errcode") == 1:
                                st.warning("ℹ️ LLM 可以根据 hint 中的实际字段信息重新选择参数进行自我纠错")

                    except json.JSONDecodeError as e:
                        st.error(f"❌ LLM 输出不是有效 JSON: {str(e)}")
                        st.markdown("**原始输出（含markdown）:**")
                        st.code(content)
                        st.markdown("**清理后（尝试解析）:**")
                        st.code(cleaned_content if cleaned_content else "(空)")
                        st.markdown("**原始内容repr:**")
                        st.code(repr(content))

                except Exception as e:
                    st.error(f"❌ 调用 LLM 失败: {str(e)}")

        elif not client:
            st.info("👈 请先配置 config.py 中的 API Key")

# 说明信息
with st.expander("ℹ️ 使用说明"):
    st.markdown("""
### 功能说明

这是一个 **LLM 自然语言调度 telecom-cli** 的测试前端：

**1. 表合并 (clean_and_merge)**
- 清洗两个表（客诉表 + OAO表）
- 剔除空主键，手机号规范化，按指定主键左联接

**2. OneID归一 (build_oneid)**
- 从多个表提取身份标识（流水号/客户标识/手机号）
- 根据置信度级别规则构建连通图
- 生成全域唯一 OneID 映射表

### 置信度级别

| 级别 | 匹配规则 | 特点 |
|------|---------|------|
| high | 仅流水号匹配 | 准确率最高，召回率最低 |
| medium | 流水号 + 客户标识 | 准确率中等，召回率中等 |
| low | 流水号 + 客户标识 + 手机号 | 准确率最低，召回率最高 |

### 工作流程

```
自然语言 → LLM 参数提取 → 本地 Python 处理 → 结果返回预览
```

所有数据处理在**本地闭环**执行，原始数据不会上传给 LLM，满足数据安全合规。
""")

# 页脚
st.markdown("---")
st.caption("telecom-cli - 本地电信数据处理工具 | LLM 调度测试前端")
