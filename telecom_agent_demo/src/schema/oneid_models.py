"""
Pydantic 模型定义 - OneID 身份归一化

用于 LLM Skill 调用的参数模型定义，并可导出 JSON Schema。
"""

from pydantic import BaseModel, Field
from typing import List


class BuildOneIDParams(BaseModel):
    """
    build_oneid 命令参数模型

    供 LLM 调用 Skill 时使用，定义了必填和可选参数。
    """
    input_files: List[str] = Field(
        ...,
        description="需要参与OneID构建的Excel文件路径列表，从线下表数据目录中选取"
    )
    confidence_level: str = Field(
        default="high",
        description="置信度级别，控制匹配规则：high(仅流水号)/medium(+客户标识)/low(+手机号)，可选值: high, medium, low"
    )
    output_dir: str = Field(
        default="./output",
        description="输出目录路径，默认为 ./output"
    )


# 导出 JSON Schema 的入口点
def export_json_schema(output_path: str) -> None:
    """
    导出 OneID Skill 的 JSON Schema 到文件

    Args:
        output_path: 输出文件路径
    """
    import json
    schema = BuildOneIDParams.model_json_schema()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
