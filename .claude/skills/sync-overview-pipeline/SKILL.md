---
name: sync-overview-pipeline
description: Overview 同步流水线。从数据源生成 zh/en JSON 文件并入库。
---

# Sync Overview Pipeline

Overview 同步流水线。

## 工作流程

```
CSV / MD 数据源
        ↓ (提取概览信息)
  overview.zh.json
        ↓ (翻译)
  overview.en.json
```

## 数据目录

- 源数据: `Content/Arena/List of Arenas ZH.csv` + `Content/Arena/data/md/` 目录
- 输出文件: `Content/Arena/All Arenas/{arena-folder}/overview.zh.json`
- 输出文件: `Content/Arena/All Arenas/{arena-folder}/overview.en.json`

## 并行处理

为了提高效率，使用 **Agent 工具** 并行处理多个 arena。至少开 **3 个并行任务**：

```
用户调用此 skill 时，必须使用 Agent 工具启动至少 3 个并行子任务：
- 每个子任务处理一个 arena
- 使用 subagent_type: "general-purpose"
- 设置 run_in_background: true

并行处理示例：
- Agent 1: 处理 2-business-dashboard-website
- Agent 2: 处理 3-document-review-risk-control
- Agent 3: 处理 4-enterprise-demo-video
```

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. **扫描待处理 arena**：按以下优先级找出需要更新的目录：
   - **优先级 1（最高）**：缺少 `overview.zh.json` 或 `overview.en.json` 文件
   - **优先级 2**：`overview.zh.json` 内容为空或缺失关键字段（源数据已更新）
2. **并行生成 JSON**：使用 Agent 工具启动至少 3 个并行任务，每个任务：
   - 从 CSV 和 MD 数据源提取概览信息
   - 生成 overview.zh.json
   - 翻译生成 overview.en.json
3. **等待所有 Agent 完成**
4. **输出处理结果摘要**

## 增量更新判断逻辑

判断是否需要更新时，按以下顺序检查：

1. **首先检查文件是否存在**（优先级最高）：
   - 如果缺少 `overview.zh.json` → 需要生成
   - 如果缺少 `overview.en.json` → 需要生成
   - 文件缺失与修改时间无关，直接生成

2. **其次检查内容完整性**：
   - 检查 JSON 文件内容是否为空或缺失关键字段
   - 如果内容不完整或格式错误，则需要更新

## JSON 结构

```json
{
  "highlight": "业务亮点",
  "industry": "行业类别",
  "category": "应用类别",
  "cycle": "实施周期",
  "case_no": "编号",
  "sections": [
    {
      "title": "1. 业务亮点",
      "subsections": [
        {"title": "亮点", "content": ["- 亮点内容"]}
      ]
    },
    {
      "title": "2. 基本信息",
      "subsections": [
        {"title": "2.1 概况", "content": ["**业务背景**: ...", "**解决方案**: ..."]},
        {"title": "2.2 分类标签", "content": ["**行业类别**: ...", "**应用类别**: ..."]},
        {"title": "2.3 实施周期", "content": ["- ..."]},
        {"title": "2.4 团队构成", "content": ["- ..."]},
        {"title": "2.5 业务痛点", "content": ["- ..."]},
        {"title": "2.6 核心功能", "content": ["- ..."]}
      ]
    }
  ],
  "markdown": "## 1. 业务亮点\n\n### 亮点\n..."
}
```

## 用法

```bash
# 批量处理所有
$sync-overview-pipeline

# 处理指定 arena
$sync-overview-pipeline --folder 1-intelligent-research-system
```

