# PipeAI — 排水管道缺陷智能检测与评估一体化系统

端到端的排水管道缺陷智能诊断平台。融合 YOLOv11n 轻量化目标检测模型与多模态大语言模型，通过"先检测、后评估"的两阶段协同架构，实现从视觉定位到语义判断的完整诊断链路。

## 系统架构

```
原始图像 → [YOLOv11n检测] → 结构化先验转换 → [LLM评估] → 报告生成
              ↑                                    ↑
         置信度筛选                          CJJ 181-2012 标准知识库
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + Next.js 16 + Tailwind CSS 4 |
| 后端 | FastAPI (Python) |
| 包管理 | uv |
| 智能体 | LangGraph (ReAct 推理) |
| 检测模型 | YOLOv11n (Ultralytics) |
| LLM 接入 | OpenAI 兼容 API 统一适配层 |
| 报告生成 | python-docx |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- CUDA 12.1+ (本地 GPU 模式)
- [uv](https://docs.astral.sh/uv/) (Python 包管理)

### 安装依赖

```bash
# 后端 (uv 自动创建虚拟环境并安装)
uv sync

# 可选：微调依赖（unsloth 和 vllm 互斥，选其一）
uv sync --extra unsloth
# 或
uv sync --extra vllm

# 前端
cd frontend
npm install
```

### 启动服务

```bash
# 启动后端 (端口 8080)
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload

# 启动前端 (端口 3000)
cd frontend
npm run dev
```

### Docker 部署

```bash
docker-compose up -d
```

## 工作模式

### 问答模式
- 单张图像上传 + 多轮文本对话
- 实时 WebSocket 流式推送
- 支持标准知识库查询、追问质疑
- 可选单图评估报告导出

### 批量模式
- 多张图像上传（文件夹/ZIP）
- 自动流水线：检测 → 评估 → 综合报告
- 实时进度追踪
- Word 格式综合报告下载

## 项目结构

```
├── backend/                 # Python 后端
│   ├── main.py             # FastAPI 入口
│   ├── routers/            # API 路由
│   ├── services/           # 核心服务
│   │   ├── detector.py     # YOLOv11n 检测器
│   │   ├── llm_provider.py # LLM 统一接入层
│   │   ├── chat_engine.py  # 问答模式引擎 (LangGraph)
│   │   ├── batch_engine.py # 批量模式引擎
│   │   ├── report_generator.py # 报告生成器
│   │   ├── prompts.py      # 提示词模板
│   │   ├── knowledge_base.py # 标准知识库
│   │   └── tools/          # 规程工具集
│   ├── models/             # 数据模型
│   └── config/             # 配置文件
├── frontend/               # Next.js 前端
│   ├── app/                # 页面路由
│   ├── components/         # UI 组件
│   └── lib/                # 工具库
├── data/                   # 数据文件
│   └── knowledge_base/     # CJJ 181-2012 标准知识库
├── models/                 # 模型权重
│   └── detector/           # YOLOv11n 权重
├── outputs/reports/        # 生成的报告
└── docker-compose.yml      # Docker 部署
```

## 模型配置

系统支持多种 LLM 后端，通过前端配置页面一键切换：

- **通义千问-VL-Max** (云端) — 阿里云 DashScope API
- **通义千问-VL-Plus** (云端) — 阿里云 DashScope API
- **GPT-4o** (云端) — OpenAI API
- **本地模型** (vLLM) — Qwen3-VL-8B 本地部署

## 评估标准

严格依据 CJJ 181-2012《城镇排水管道检测与评估技术规程》进行缺陷等级判定。

## 免责声明

本系统生成的评估报告为 AI 辅助决策参考，不替代 CJJ 181-2012 标准附录 D 定义的正式检测成果表，不具备工程归档效力。建议由持证技术人员审核确认后使用。
