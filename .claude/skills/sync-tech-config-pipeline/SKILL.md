---
name: sync-tech-config-pipeline
description: 技术配置同步流水线。从 Original Documents/implementation-details.md 生成 zh/en JSON 文件。
---

# Sync Tech Config Pipeline

技术配置同步流水线。

## 工作流程

```
Original Documents/implementation-details.md
        ↓ (提取技术步骤)
  tech-configuration.zh.json
        ↓ (翻译)
  tech-configuration.en.json
```

## 数据目录

- 源文件: `Content/Arena/All Arenas/{arena-folder}/Original Documents/implementation-details.md`
- 输出文件: `Content/Arena/All Arenas/{arena-folder}/tech-configuration.zh.json`
- 输出文件: `Content/Arena/All Arenas/{arena-folder}/tech-configuration.en.json`

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
   - **优先级 1（最高）**：缺少 `tech-configuration.zh.json` 或 `tech-configuration.en.json` 文件
   - **优先级 2**：`Original Documents/implementation-details.md` 的修改时间晚于 `tech-configuration.zh.json`（源文件已更新）
2. **并行生成 JSON**：使用 Agent 工具启动至少 3 个并行任务，每个任务：
   - 读取 Original Documents/implementation-details.md
   - 提取技术步骤表格（"3\. **技术步骤**" 部分）
   - 生成 tech-configuration.zh.json
   - 翻译生成 tech-configuration.en.json
3. **等待所有 Agent 完成**
4. **输出处理结果摘要**

## 增量更新判断逻辑

判断是否需要更新时，按以下顺序检查：

1. **首先检查文件是否存在**（优先级最高）：
   - 如果缺少 `tech-configuration.zh.json` → 需要生成
   - 如果缺少 `tech-configuration.en.json` → 需要生成
   - 文件缺失与修改时间无关，直接生成

2. **其次检查修改时间**：
   - 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
   - 如果 `Original Documents/implementation-details.md` 时间戳 > `tech-configuration.zh.json` 时间戳，则需要更新

## JSON 结构

```json
{
  "steps": [
    {
      "number": 1,
      "title": "步骤名称",
      "subsections": [
        {"title": "步骤定义", "content": ["..."]},
        {"title": "参与人员", "content": ["..."]},
        {"title": "本步输入", "content": ["..."]},
        {"title": "本步产出", "content": ["..."]},
        {"title": "预估时间", "content": ["..."]}
      ]
    }
  ]
}
```

## 用法

```bash
# 批量处理所有
$sync-tech-config-pipeline

# 处理指定 arena
$sync-tech-config-pipeline --folder 1-intelligent-research-system
```

