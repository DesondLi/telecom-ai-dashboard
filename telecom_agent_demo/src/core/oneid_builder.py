"""
OneID 身份归一化核心模块

基于 Union-Find (并查集) 算法实现多标识连通分量计算，生成全域唯一 OneID。
支持不同置信度级别的级联匹配规则。
"""

import os
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass

import pandas as pd


@dataclass
class BuildOneIDResult:
    """OneID 构建结果"""
    errcode: int
    errmsg: str
    total_records: int = 0
    unique_oneids: int = 0
    output_path: str = ""
    hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典用于 JSON 输出"""
        result = {
            "errcode": self.errcode,
            "errmsg": self.errmsg,
        }
        if self.errcode == 0:
            result.update({
                "total_records": self.total_records,
                "unique_oneids": self.unique_oneids,
                "output_path": self.output_path,
            })
        else:
            result["hint"] = self.hint
        return result


class UnionFind:
    """并查集实现，用于计算连通分量"""
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.size: Dict[str, int] = {}

    def find(self, x: str) -> str:
        """查找根节点，路径压缩"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> None:
        """合并两个集合"""
        if x not in self.parent:
            self.parent[x] = x
            self.size[x] = 1
        if y not in self.parent:
            self.parent[y] = y
            self.size[y] = 1

        rx = self.find(x)
        ry = self.find(y)

        if rx != ry:
            # 按大小合并
            if self.size[rx] < self.size[ry]:
                rx, ry = ry, rx
            self.parent[ry] = rx
            self.size[rx] += self.size[ry]

    def get_root_map(self) -> Dict[str, str]:
        """获取每个节点对应的根节点"""
        return {k: self.find(k) for k in self.parent}


class ConfidenceLevel:
    """置信度级别定义"""
    HIGH = "high"       # 仅流水号匹配
    MEDIUM = "medium"   # 流水号 + 客户标识
    LOW = "low"         # 流水号 + 客户标识 + 手机号


class OneIDBuilder:
    """
    OneID 身份归一化构建器

    根据不同置信度级别，提取多表身份标识，通过并查集计算连通分量，生成唯一 OneID。
    """

    # 预设标识列分类
    STRONG_IDENTITY_COLS = [  # 强标识 - 高置信度
        '流水号', '流水', 'flow', 'Flow'
    ]
    MEDIUM_IDENTITY_COLS = [  # 中标识 - 中置信度
        '客户标识', '客户id', '用户id', '客户编号', '用户编号',
        'customer', 'Customer', 'user', 'User'
    ]
    WEAK_IDENTITY_COLS = [  # 弱标识 - 低置信度
        '手机', '电话', '手机号', '电话号码', '联系电话',
        'phone', 'mobile', 'tel', '联系电话'
    ]

    def __init__(self, confidence_level: str = ConfidenceLevel.HIGH):
        self.confidence_level = confidence_level
        self.uf = UnionFind()

    def _get_active_identity_cols(self, columns: List[str]) -> List[str]:
        """
        根据置信度级别确定当前激活哪些类型的标识列

        Args:
            columns: 表格实际列名列表

        Returns:
            需要使用的标识列名列表（在当前表格中存在的）
        """
        active_cols: List[str] = []

        # high: 仅强标识（流水号）
        for pattern in self.STRONG_IDENTITY_COLS:
            for col in columns:
                col_str = str(col).lower()
                if pattern.lower() in col_str:
                    if col not in active_cols:
                        active_cols.append(col)

        if self.confidence_level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]:
            # medium: 加上中标识（客户标识）
            for pattern in self.MEDIUM_IDENTITY_COLS:
                for col in columns:
                    col_str = str(col).lower()
                    if pattern.lower() in col_str:
                        if col not in active_cols:
                            active_cols.append(col)

        if self.confidence_level == ConfidenceLevel.LOW:
            # low: 加上弱标识（手机号）
            for pattern in self.WEAK_IDENTITY_COLS:
                for col in columns:
                    col_str = str(col).lower()
                    if pattern.lower() in col_str:
                        if col not in active_cols:
                            active_cols.append(col)

        return active_cols

    def process_file(
        self,
        file_path: str,
        active_cols: List[str]
    ) -> List[Tuple[str, List[str]]]:
        """
        处理单个文件，提取每条记录的非空标识列表

        Args:
            file_path: Excel 文件路径
            active_cols: 当前置信度下激活的列名列表（已匹配到的）

        Returns:
            list of (record_id, identity_values) - 每条记录的ID和非空标识值列表
        """
        # 尝试多种方式读取，自动兼容
        df = None
        exceptions = []

        # 尝试 1: 自动检测
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            exceptions.append(str(e))

        # 尝试 2: xlrd for xls
        if df is None:
            try:
                import xlrd
                df = pd.read_excel(file_path, engine='xlrd')
            except Exception as e:
                exceptions.append(str(e))

        # 尝试 3: openpyxl
        if df is None:
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception as e:
                exceptions.append(str(e))

        if df is None:
            raise ValueError(f"无法读取文件 {file_path}: {'; '.join(exceptions)}")

        results: List[Tuple[str, List[str]]] = []

        # 检查激活列是否都存在
        for col in active_cols:
            if col not in df.columns:
                raise KeyError(f"标识列 '{col}' 不存在")

        # 遍历每一行，提取非空标识值
        for idx, row in df.iterrows():
            # 记录ID = 文件名 + 行号
            record_id = f"{os.path.basename(file_path)}#L{idx+1}"
            identity_values: List[str] = []

            for col in active_cols:
                val = row[col]
                if not pd.isna(val) and str(val).strip():
                    # 规范化：转为字符串，去除空白
                    val_str = str(val).strip()
                    # 格式化为 列名:值 作为唯一标识键
                    identity_key = f"{col}={val_str}"
                    identity_values.append(identity_key)

            if identity_values:
                results.append((record_id, identity_values))

        return results, df.shape[0]

    def build(
        self,
        input_files: List[str],
        output_dir: str
    ) -> BuildOneIDResult:
        """
        构建 OneID 映射表

        Args:
            input_files: 输入 Excel 文件列表
            output_dir: 输出目录

        Returns:
            BuildOneIDResult 构建结果
        """
        all_columns: Dict[str, List[str]] = {}  # file -> columns
        all_records: List[Dict[str, Any]] = []  # 最终映射表数据
        total_input_records = 0

        try:
            # 第一阶段：收集所有文件的列信息，确定每个文件的激活标识列
            file_active_cols: Dict[str, List[str]] = {}
            for file_path in input_files:
                # 尝试多种方式读取表头
                df = None
                # 尝试 1: 自动检测
                try:
                    df = pd.read_excel(file_path, nrows=0)
                except Exception:
                    pass

                # 尝试 2: xlrd
                if df is None:
                    try:
                        df = pd.read_excel(file_path, nrows=0, engine='xlrd')
                    except Exception:
                        pass

                # 尝试 3: openpyxl
                if df is None:
                    try:
                        df = pd.read_excel(file_path, nrows=0, engine='openpyxl')
                    except Exception:
                        pass

                if df is None:
                    # 无法读取，返回错误
                    hint = self._format_hint(all_columns)
                    return BuildOneIDResult(
                        errcode=1,
                        errmsg=f"无法读取文件 {os.path.basename(file_path)}",
                        hint=hint
                    )

                cols = list(df.columns)
                all_columns[file_path] = cols
                active_cols = self._get_active_identity_cols(cols)
                file_active_cols[file_path] = active_cols

                if not active_cols:
                    # 根据置信度配置，一个标识列都找不到
                    hint = self._format_hint(all_columns)
                    return BuildOneIDResult(
                        errcode=1,
                        errmsg="找不到符合要求的身份标识列",
                        hint=hint
                    )

            # 第二阶段：提取所有记录的标识，构建并查集
            for file_path, active_cols in file_active_cols.items():
                records, total_rows = self.process_file(file_path, active_cols)
                total_input_records += total_rows

                for record_id, identity_values in records:
                    if len(identity_values) >= 2:
                        # 同一个记录上的多个标识互相连通
                        first = identity_values[0]
                        for other in identity_values[1:]:
                            self.uf.union(first, other)
                    elif len(identity_values) == 1:
                        # 单个标识也加入并查集
                        val = identity_values[0]
                        if val not in self.uf.parent:
                            self.uf.union(val, val)

            # 第三阶段：得到每个标识对应的根（OneID）
            root_map = self.uf.get_root_map()

            # 创建 OneID -> 顺序编号 映射
            unique_roots = set(root_map.values())
            root_to_oneid = {
                root: f"ONEID_{i+1:08d}"
                for i, root in enumerate(sorted(unique_roots))
            }

            # 第四阶段：构建输出映射表
            # 重新遍历每个文件，为每条记录分配 OneID
            # 一条记录可能有多个标识，但它们连通到同一个 OneID
            output_rows: List[Dict[str, Any]] = []

            for file_path, active_cols in file_active_cols.items():
                df = pd.read_excel(file_path)
                filename = os.path.basename(file_path)

                for idx, row in df.iterrows():
                    # 收集这条记录上所有标识的根
                    roots: Set[str] = set()
                    for col in active_cols:
                        val = row[col]
                        if not pd.isna(val) and str(val).strip():
                            val_str = str(val).strip()
                            identity_key = f"{col}={val_str}"
                            if identity_key in root_map:
                                roots.add(root_map[identity_key])

                    if roots:
                        # 所有标识都应该连通到同一个根，取第一个
                        root = next(iter(roots))
                        oneid = root_to_oneid[root]
                    else:
                        oneid = ""

                    output_rows.append({
                        "source_file": filename,
                        "source_row": idx + 1,
                        "oneid": oneid,
                        "matched_identities": "|".join([f"{col}={row[col]}" for col in active_cols if not pd.isna(row[col])])
                    })

            # 第五阶段：输出 Excel
            output_df = pd.DataFrame(output_rows)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"oneid_mapping_{timestamp}.xlsx"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            output_df.to_excel(output_path, index=False)

            return BuildOneIDResult(
                errcode=0,
                errmsg="ok",
                total_records=len(output_df),
                unique_oneids=len(unique_roots),
                output_path=output_path
            )

        except KeyError:
            # Schema Drift: 找不到指定列，返回实际列信息
            hint = self._format_hint(all_columns)
            return BuildOneIDResult(
                errcode=1,
                errmsg="找不到预设的身份标识列",
                hint=hint
            )
        except Exception as e:
            hint = self._format_hint(all_columns)
            return BuildOneIDResult(
                errcode=2,
                errmsg=f"构建过程发生错误: {str(e)}",
                hint=hint
            )

    def _format_hint(self, all_columns: Dict[str, List[str]]) -> str:
        """格式化错误提示"""
        hints = []
        for file_path, cols in all_columns.items():
            filename = os.path.basename(file_path)
            hints.append(f"{filename} 可用字段: {cols}")
        return "; ".join(hints)


def build_oneid(
    input_files: List[str],
    confidence_level: str,
    output_dir: str
) -> BuildOneIDResult:
    """
    顶层接口：构建 OneID 映射表

    Args:
        input_files: 输入 Excel 文件路径列表
        confidence_level: 置信度级别 high/medium/low
        output_dir: 输出目录

    Returns:
        BuildOneIDResult 构建结果
    """
    builder = OneIDBuilder(confidence_level=confidence_level)
    return builder.build(input_files, output_dir)
