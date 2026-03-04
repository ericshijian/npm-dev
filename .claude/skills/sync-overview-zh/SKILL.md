---
name: sync-overview-zh
description: 从 arenas 表和数据源生成 overview.zh.json 文件到对应 arena 目录。每次处理一条数据。
---

# Sync Overview Zh

从 arenas 表和 MD 数据源提取概览信息，生成中文 JSON 配置文件。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 目标: `overview.zh.json`（同目录）
- 辅助数据: arenas 表中的基本信息

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
    },
    {
      "title": "3. 最佳实践版本",
      "subsections": [
        {"title": "3.1 版本信息", "content": ["- ..."]},
        {"title": "3.1.2 入选最佳实践理由", "content": ["- ..."]},
        {"title": "3.1.3 实施详情", "content": ["[实践详情](...)"]},
        {"title": "3.1.4 指标", "content": ["- ..."]}
      ]
    }
  ],
  "markdown": "## 1. 业务亮点\n\n### 亮点\n..."
}
```

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 读取 `Content/Arena/List of Arenas ZH.csv` 获取擂台基础信息
2. 找到下一条待处理的记录：
   - 没有 `overview.zh.json` 文件，或者
   - `overview.zh.json` 文件内容需要更新（基于内容校验或文件缺失）
3. 从 CSV 获取基本信息（title_zh, industry_zh, category_zh 等）
4. 如果存在源 MD 文件（`Content/Arena/data/md/` 目录下），解析提取更详细的信息
5. 构建 JSON 结构，包含 sections 和 markdown
6. 写入 `overview.zh.json` 文件
7. 输出处理结果

## 增量更新

通过比较文件存在性和内容判断是否需要更新：
- 如果文件不存在，需要生成
- 如果文件内容为空或缺失关键字段，需要更新

## 用法

```bash
# 调用 skill 处理下一条
$sync-overview-zh

# 指定 arena-folder
$sync-overview-zh --folder 1-intelligent-research-system
```
