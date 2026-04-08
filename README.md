# telecom-ai-dashboard - 电信 LLM 数据处理前端

> 📊 基于 Streamlit 的 LLM 自然语言调度电信数据处理工具，支持公网部署，云端文件上传。

本地电信数据处理工具 + LLM 自然语言调度前端。

**核心特点：所有数据处理在本地/云端闭环执行，敏感原始数据只会发送给 LLM 自然语言请求，LLM 仅负责参数提取和调度。满足数据安全合规要求。**

## ✨ 新增功能（公网部署版）

- ✅ 支持**网页上传 Excel 文件** - 云端部署后用户可以直接在网页上传数据文件
- ✅ 支持**环境变量配置** - API Key 通过 Streamlit Cloud Secrets 安全配置，不需要提交代码
- ✅ 完全开源免费，一键部署

## 📁 项目结构

```
d:/电信AI/
├── telecom_agent_demo/          # CLI 工具核心项目
│   ├── src/
│   │   ├── cli.py               # typer CLI 入口
│   │   ├── core/
│   │   │   └── data_processor.py  # 数据清洗与合并
│   │   └── schema/
│   │       └── models.py        # Pydantic 参数模型
│   ├── DESIGN.md                # 设计文档
│   ├── requirements.txt         # 核心依赖
│   └── skill_definition.json    # LLM Skill JSON Schema
├── 线下表数据/                   # 原始数据（用户提供）
├── test_frontend.py             # Streamlit 测试前端
├── config.py.example            # LLM 配置模板
├── requirements-frontend.txt    # 前端依赖
└── README.md                    # 本文档
```

## 🚀 本地部署步骤

### 1. 安装依赖

```bash
# 安装核心 + 前端依赖
pip install -r requirements-frontend.txt
pip install -r telecom_agent_demo/requirements.txt
```

### 2. 配置 LLM API

```bash
# 复制配置模板
cp config.py.example config.py
```

编辑 `config.py`，填入你的 aihubmix API Key：

```python
# aihubmix API 配置
AIHUBMIX_API_KEY = "your-actual-api-key-here"
AIHUBMIX_BASE_URL = "https://aihubmix.com/v1"
AIHUBMIX_MODEL = "gpt-4o-mini"  # 可根据需要修改
```

### 3. 启动服务

#### 本地访问（仅本机）
```bash
streamlit run test_frontend.py
```

#### 局域网内访问（同一网络其他人可通过 IP 访问）
```bash
streamlit run test_frontend.py --server.address=0.0.0.0 --server.port=8501
```

启动后，同一局域网内的其他人可以通过 `http://<你的IP>:8501` 访问。

## 🌐 公网访问方案

### 方案一：ngrok 内网穿透（快速测试）

1. 下载安装 [ngrok](https://ngrok.com/)
2. 启动 streamlit：
```bash
streamlit run test_frontend.py --server.address=0.0.0.0 --server.port=8501
```
3. 新开终端运行 ngrok：
```bash
ngrok http 8501
```
4. ngrok 会给你一个类似 `https://xxx-xxx-xxx.ngrok.io` 的公网 URL，分享给他人即可。

### 方案二：Streamlit Cloud（推荐演示）

**一键部署到公网，任何人都可以通过互联网访问：**

1. 将整个项目推送到 GitHub 公开仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io/)，使用 GitHub 账号登录
3. 点击 "New app"
4. 选择：
   - Repository: `你的用户名/telecom-ai-dashboard`
   - Branch: `master`
   - Main file path: `test_frontend.py`
5. 点击 "Advanced settings"
6. 在 "Secrets" 添加环境变量：
   - `AIHUBMIX_API_KEY` → 你的 AIHubMix API Key
   - （可选）`AIHUBMIX_BASE_URL` → API 地址，默认 `https://aihubmix.com/v1`
   - （可选）`AIHUBMIX_MODEL` → 模型名称，默认 `gpt-4o-mini`
7. 点击 "Deploy"
8. 部署完成后获得公开 URL，分享给他人即可访问

**云端使用说明：**
- 在侧边栏 "📤 上传新文件" 上传你的 Excel 文件
- 上传完成后文件自动保存，可以在下拉框选择
- 支持表合并（两个文件）和 OneID 构建（多个文件）
- 处理完成后可以预览结果，下载输出文件

> ⚠️ **注意**：
> - 原始数据 `线下表数据/` 已经在 `.gitignore` 中排除，不会推送到 GitHub，保证数据安全
> - Streamlit Cloud 免费版 30 分钟无访问会进入冬眠，下次访问需要几秒唤醒

### 方案三：服务器部署

如果你有自己的服务器：

```bash
# 1. clone 项目到服务器
git clone <your-repo>
cd <project-dir>

# 2. 安装依赖
pip install -r requirements-frontend.txt
pip install -r telecom_agent_demo/requirements.txt

# 3. 配置 config.py

# 4. 使用 nohup 后台运行
nohup streamlit run test_frontend.py --server.address=0.0.0.0 --server.port=8501 &
```

然后可以通过 Nginx 反向代理 + SSL 配置域名访问。

## ✨ 使用示例

**输入自然语言：**
```
帮我合并投诉受理清单0313.xlsx 和 OAO清单.xlsx，用客户标识作为关联主键
```

**LLM 输出 JSON：**
```json
{
  "thinking": "用户需要合并客诉表和OAO清单，选择对应文件，关联主键使用客户标识。",
  "action": "clean_and_merge",
  "parameters": {
    "complaint_file": "投诉受理清单0313.xlsx",
    "oao_file": "OAO清单.xlsx",
    "join_key": "客户标识"
  }
}
```

**CLI 处理结果：**
```json
{
  "errcode": 0,
  "errmsg": "ok",
  "total_processed": 2558,
  "dropped_rows": 393,
  "output_path": "./test_output/merged_xxxx.xlsx"
}
```

**前端预览结果** - 显示合并后的前 20 行数据。

## 🔧 错误处理

| errcode | 含义 | 处理方式 |
|---------|------|---------|
| 0 | 成功 | 下载/预览结果 |
| 1 | 找不到主键 | 返回两张表实际列名，LLM 可自我纠错 |
| 2 | 文件未找到 | 检查文件路径 |
| 3 | 读取文件失败 | 检查文件格式 |
| 4 | 处理过程错误 | 根据错误信息排查 |

## 🔒 安全性

- ✅ **本地闭环**：所有 Excel 数据处理在本地完成
- ✅ **原始数据不上传**：LLM 只接收自然语言请求，看不到原始数据
- ✅ **输出结果**：仅输出统计信息和合并后的文件，仍保存在本地

## 📋 需求背景

为甲方电信项目开发：
- 本地数据清洗合并工具
- LLM 负责自然语言调度
- 满足数据安全合规要求
