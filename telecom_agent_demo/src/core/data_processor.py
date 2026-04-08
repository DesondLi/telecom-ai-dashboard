"""
数据清洗与合并核心模块

实现了读取 Excel、剔除空主键、手机号规范化、Left Join 以及 Schema Drift 错误处理。
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

import pandas as pd


class ProcessingResult:
    """处理结果数据类"""
    def __init__(
        self,
        errcode: int,
        errmsg: str,
        total_processed: int = 0,
        dropped_rows: int = 0,
        output_path: str = "",
        hint: str = ""
    ):
        self.errcode = errcode
        self.errmsg = errmsg
        self.total_processed = total_processed
        self.dropped_rows = dropped_rows
        self.output_path = output_path
        self.hint = hint

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典用于 JSON 输出"""
        result = {
            "errcode": self.errcode,
            "errmsg": self.errmsg,
        }
        if self.errcode == 0:
            result.update({
                "total_processed": self.total_processed,
                "dropped_rows": self.dropped_rows,
                "output_path": self.output_path,
            })
        else:
            result["hint"] = self.hint
        return result


def normalize_phone(phone: Any) -> str:
    """
    规范化手机号格式

    移除所有非数字字符，保留开头的 + 号（若存在）。
    如果是 11 位纯数字手机号，保持不变。

    Args:
        phone: 原始手机号（可以是任何类型）

    Returns:
        规范化后的手机号字符串
    """
    if pd.isna(phone):
        return ""

    phone_str = str(phone).strip()
    # 移除非数字字符，但保留开头的 +
    if phone_str.startswith('+'):
        digits = '+' + re.sub(r'\D', '', phone_str)
    else:
        digits = re.sub(r'\D', '', phone_str)

    return digits


def clean_and_merge(
    complaint_file: str,
    oao_file: str,
    join_key: str,
    output_dir: str
) -> ProcessingResult:
    """
    清洗客诉表和 OAO 表并按指定主键进行 Left Join

    处理流程：
    1. 读取两个 Excel 文件
    2. 剔除 join_key 为空的行
    3. 规范化手机号格式（如果存在手机号相关列）
    4. 按 join_key 进行 Left Join
    5. 输出结果到 output_dir

    关键错误处理：
    - 如果 join_key 在任一表中不存在，捕获 KeyError 并返回包含实际字段列表的错误信息

    Args:
        complaint_file: 客诉表 Excel 文件路径
        oao_file: OAO 表 Excel 文件路径
        join_key: 关联主键列名
        output_dir: 输出目录路径

    Returns:
        ProcessingResult 处理结果对象
    """
    try:
        # 1. 读取 Excel 文件，尝试多种方式自动兼容
        def read_excel_auto(path: str) -> pd.DataFrame:
            df = None
            # 尝试 1: 自动检测
            try:
                df = pd.read_excel(path)
            except Exception:
                pass

            # 尝试 2: xlrd for xls
            if df is None:
                try:
                    df = pd.read_excel(path, engine='xlrd')
                except Exception:
                    pass

            # 尝试 3: openpyxl
            if df is None:
                try:
                    df = pd.read_excel(path, engine='openpyxl')
                except Exception:
                    pass

            if df is None:
                raise ValueError(f"无法读取文件 {path}，尝试多种引擎都失败")
            return df

        df_complaint = read_excel_auto(complaint_file)
        df_oao = read_excel_auto(oao_file)

    except FileNotFoundError as e:
        return ProcessingResult(
            errcode=2,
            errmsg=f"文件未找到: {str(e)}",
            hint=""
        )
    except Exception as e:
        return ProcessingResult(
            errcode=3,
            errmsg=f"读取文件失败: {str(e)}",
            hint=""
        )

    # 获取列名供错误提示使用
    complaint_cols: List[str] = list(df_complaint.columns)
    oao_cols: List[str] = list(df_oao.columns)

    try:
        # 2. 统计并剔除主键为空的行
        complaint_dropped = int(df_complaint[join_key].isna().sum())
        oao_dropped = int(df_oao[join_key].isna().sum())
        total_dropped = complaint_dropped + oao_dropped

        df_complaint_clean = df_complaint.dropna(subset=[join_key])
        df_oao_clean = df_oao.dropna(subset=[join_key])

        # 统一主键类型为字符串，避免不同数据类型合并错误
        df_complaint_clean[join_key] = df_complaint_clean[join_key].astype(str)
        df_oao_clean[join_key] = df_oao_clean[join_key].astype(str)

        # 3. 规范化手机号 - 查找所有可能包含手机号的列并规范化
        # 识别手机号列（包含"手机"、"电话"、"phone"、"mobile"关键词）
        phone_pattern = re.compile(r'(手机|电话|phone|mobile)', re.IGNORECASE)
        for col in list(df_complaint_clean.columns) + list(df_oao_clean.columns):
            if phone_pattern.search(str(col)):
                if col in df_complaint_clean.columns:
                    df_complaint_clean[col] = df_complaint_clean[col].apply(normalize_phone)
                if col in df_oao_clean.columns:
                    df_oao_clean[col] = df_oao_clean[col].apply(normalize_phone)

        # 4. Left Join
        merged = pd.merge(
            left=df_complaint_clean,
            right=df_oao_clean,
            on=join_key,
            how='left'
        )

        # 5. 输出到文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"merged_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 保存结果
        merged.to_excel(output_path, index=False)

        return ProcessingResult(
            errcode=0,
            errmsg="ok",
            total_processed=len(merged),
            dropped_rows=total_dropped,
            output_path=output_path
        )

    except KeyError:
        # Schema Drift 处理 - 返回实际可用字段作为提示
        hint = f"客诉表可用字段: {complaint_cols}; OAO表可用字段: {oao_cols}"
        return ProcessingResult(
            errcode=1,
            errmsg="找不到主键",
            hint=hint
        )
    except Exception as e:
        hint = f"客诉表可用字段: {complaint_cols}; OAO表可用字段: {oao_cols}"
        return ProcessingResult(
            errcode=4,
            errmsg=f"处理过程发生错误: {str(e)}",
            hint=hint
        )
