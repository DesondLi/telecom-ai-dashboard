"""
telecom-cli 命令行入口

使用 typer 定义命令行接口，输出标准化 JSON 格式供上层 LLM 解析。
"""

import json
import typer
from typing import List

from src.core.data_processor import clean_and_merge, ProcessingResult
from src.core.oneid_builder import build_oneid, BuildOneIDResult
from src.schema.models import CleanAndMergeParams, export_json_schema

app = typer.Typer(
    name="telecom-cli",
    help="本地电信数据处理工具 - 供 LLM 调度使用",
    add_completion=False
)

data_app = typer.Typer(
    name="data",
    help="数据处理子命令"
)
app.add_typer(data_app)


@data_app.command("clean_and_merge")
def clean_and_merge_command(
    complaint_file: str = typer.Argument(..., help="客诉表 Excel 文件路径"),
    oao_file: str = typer.Argument(..., help="OAO表 Excel 文件路径"),
    join_key: str = typer.Argument(..., help="关联主键列名"),
    output_dir: str = typer.Option("./output", help="输出目录路径")
) -> None:
    """
    清洗客诉表和 OAO 表并按主键左联接合并

    输出为标准 JSON 格式，包含处理统计或错误提示。
    """
    # 参数验证通过后执行处理
    result: ProcessingResult = clean_and_merge(
        complaint_file=complaint_file,
        oao_file=oao_file,
        join_key=join_key,
        output_dir=output_dir
    )

    # 输出 JSON 到标准输出
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


@data_app.command("export-schema")
def export_schema_command(
    output_path: str = typer.Argument("skill_definition.json", help="输出 JSON Schema 文件路径")
) -> None:
    """
    导出 LLM Skill 的 JSON Schema 定义

    生成的 JSON 文件可直接用于 LLM 工具调用配置。
    """
    export_json_schema(output_path)
    print(json.dumps({
        "errcode": 0,
        "errmsg": "ok",
        "schema_path": output_path
    }, ensure_ascii=False, indent=2))


@data_app.command("build_oneid")
def build_oneid_command(
    input_files: List[str] = typer.Argument(..., help="输入Excel文件路径列表，多个文件空格分隔"),
    confidence_level: str = typer.Option("high", help="置信度级别: high/medium/low"),
    output_dir: str = typer.Option("./output", help="输出目录路径")
) -> None:
    """
    OneID 身份归一化 - 从多个表格构建全域唯一 OneID 映射

    规则级联:
    - high: 仅通过流水号匹配
    - medium: 流水号 + 客户标识匹配
    - low: 流水号 + 客户标识 + 手机号匹配

    输出为标准 JSON 格式，包含处理统计或错误提示。
    """
    result: BuildOneIDResult = build_oneid(
        input_files=input_files,
        confidence_level=confidence_level,
        output_dir=output_dir
    )

    # 输出 JSON 到标准输出
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


@data_app.command("export-oneid-schema")
def export_oneid_schema_command(
    output_path: str = typer.Argument("oneid_skill_definition.json", help="输出 JSON Schema 文件路径")
) -> None:
    """
    导出 OneID 构建工具的 LLM Skill JSON Schema 定义

    生成的 JSON 文件可直接用于 LLM 工具调用配置。
    """
    from src.schema.oneid_models import BuildOneIDParams, export_json_schema
    export_json_schema(output_path)
    print(json.dumps({
        "errcode": 0,
        "errmsg": "ok",
        "schema_path": output_path
    }, ensure_ascii=False, indent=2))


def main():
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    main()
