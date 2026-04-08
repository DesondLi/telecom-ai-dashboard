"""
Pydantic 模型定义

用于 LLM Skill 调用的参数模型定义，并可导出 JSON Schema。
"""

from pydantic import BaseModel, Field
from typing import Optional


class CleanAndMergeParams(BaseModel):
    """
    clean_and_merge 命令参数模型

    供 LLM 调用 Skill 时使用，定义了必填和可选参数。
    """
    complaint_file: str = Field(
        ...,
        description="客诉表 Excel 文件的本地绝对路径"
    )
    oao_file: str = Field(
        ...,
        description="OAO清单 Excel 文件的本地绝对路径"
    )
    join_key: str = Field(
        ...,
        description="用于关联两张表的主键列名，必须在两张表中都存在"
    )
    output_dir: Optional[str] = Field(
        "./output",
        description="输出目录路径，默认为 ./output"
    )


# 导出 JSON Schema 的入口点
def export_json_schema(output_path: str) -> None:
    """
    导出 Skill 的 JSON Schema 到文件

    Args:
        output_path: 输出文件路径
    """
    import json
    schema = CleanAndMergeParams.model_json_schema()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
