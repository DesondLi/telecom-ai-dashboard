# telecom-cli 设计文档

## 架构概述

`telecom-cli` 是一个为电信项目设计的本地数据处理命令行工具，专为 LLM 调度而设计。所有数据处理在本地闭环执行，保证敏感数据不泄露。

## 模块结构

```
telecom_agent_demo/
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口，typer 应用定义
│   ├── core/
│   │   ├── __init__.py
│   │   └── data_processor.py  # 核心数据清洗与合并逻辑
│   └── schema/
│       ├── __init__.py
│       └── models.py       # Pydantic 模型定义，用于生成 Skill JSON Schema
├── tests/                  # 测试用例
├── requirements.txt        # 依赖清单
└── DESIGN.md              # 本文档
```

## 模块职责

| 模块 | 职责 |
|------|------|
| `cli.py` | 使用 `typer` 定义命令行接口，处理参数输入，调用核心处理逻辑，输出标准化 JSON |
| `data_processor.py` | 实现数据清洗（去空、手机号规范化）和 Left Join 逻辑，内置 Schema Drift 错误捕获机制 |
| `models.py` | 定义 Pydantic 输入参数模型，用于导出 LLM Skill 的 JSON Schema |

## 调用关系

```
LLM 调度
    ↓
telecom-cli data clean_and_merge <complaint_file> <oao_file> <join_key> [--output <output_dir>]
    ↓
cli.py 解析参数 → 包装成 DataProcessorRequest
    ↓
data_processor.py.clean_and_merge()
    ↓
  → 成功：返回 ResultOutput 结构化结果 → CLI 输出 JSON
  → KeyError：捕获异常，提取实际表头 → 返回错误信息 JSON
```

## JSON 输出接口定义

### 成功响应 (errcode = 0)

```json
{
  "errcode": 0,
  "errmsg": "ok",
  "total_processed": 1500,
  "dropped_rows": 50,
  "output_path": "/path/to/output/merged.xlsx"
}
```

字段说明：
- `errcode`: 错误码，`0` 表示成功
- `errmsg`: 状态信息，成功时为 `"ok"`
- `total_processed`: 处理后总行数
- `dropped_rows`: 因主键为空被剔除的行数
- `output_path`: 合并结果输出文件路径

### 错误响应 - 主键不存在 (errcode = 1)

```json
{
  "errcode": 1,
  "errmsg": "找不到主键",
  "hint": "客诉表可用字段: [字段1, 字段2, ...]; OAO表可用字段: [字段A, 字段B, ...]"
}
```

字段说明：
- `errcode`: 错误码，`1` 表示找不到主键
- `errmsg`: 错误描述
- `hint`: 线索提示，包含两张表实际可用的表头字段列表，供 LLM 自我纠错

### 其他错误 (errcode >= 2)

预留扩展，可根据实际需求增加。

## 处理流程

1. **读取文件**: 使用 pandas 读取两个 Excel 文件
2. **清洗主键**: 剔除 `join_key` 列为空的行
3. **手机号规范化**: 若存在手机号列，统一格式为 `+86` 前缀或纯数字（根据实际需求调整）
4. **Left Join**: 按照指定 `join_key` 左联接两个表
5. **输出结果**: 将合并结果写入 `output` 目录
6. **错误处理**: 若 `KeyError` 发生，立即捕获并返回带表头线索的错误 JSON
