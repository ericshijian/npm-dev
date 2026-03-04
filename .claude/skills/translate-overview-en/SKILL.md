---
name: translate-overview-en
description: 读取 overview.zh.json，翻译得到 overview.en.json。保持 JSON 结构一致。每次处理一条数据。
---

# Translate Overview En

将中文 overview JSON 文件翻译为英文版本。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 源文件: `overview.zh.json`
- 目标文件: `overview.en.json`（同目录）

## 翻译规则

1. **保持 JSON 结构一致**：sections、subsections 结构不变
2. **翻译所有中文内容**：
   - `highlight` 字段
   - `industry` 字段
   - `category` 字段
   - `cycle` 字段
   - `sections` 中的 `title` 字段
   - `subsections` 中的 `title` 和 `content` 数组中的文本
   - `markdown` 字段
3. **不翻译的字段**：
   - `case_no` (编号保持原样)
4. **术语一致性**：
   - 行业类别 -> Industry
   - 应用类别 -> Category
   - 实施周期 -> Implementation Cycle
   - 业务痛点 -> Business Pain Points
   - 核心功能 -> Core Functions
   - 业务亮点 -> Business Highlights
   - 最佳实践 -> Best Practice

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 遍历 `Content/Arena/All Arenas/` 下的 arena 目录
2. 找到下一条待处理的记录：
   - 有 `overview.zh.json` 文件
   - 没有 `overview.en.json` 文件，或者
   - `overview.zh.json` 的修改时间晚于 `overview.en.json`（源文件已更新）
3. 读取 `overview.zh.json` 文件
4. 翻译所有中文内容为英文，保持 JSON 结构
5. 写入 `overview.en.json` 文件
6. 输出处理结果

## 增量更新

通过比较文件修改时间判断是否需要更新：
- 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
- 如果 `overview.zh.json` 时间戳 > `overview.en.json` 时间戳，则需要更新

## 用法

```bash
# 调用 skill 处理下一条
$translate-overview-en

# 指定 arena-folder
$translate-overview-en --folder 1-intelligent-research-system
```
