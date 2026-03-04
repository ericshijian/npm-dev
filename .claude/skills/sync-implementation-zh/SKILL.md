---
name: sync-implementation-zh
description: 从 implementation-details.md 读取方案概览部分，生成 implementation.zh.json 文件到对应 arena 目录。每次处理一条数据。
---

# Sync Implementation Zh

从 implementation-details.md 提取方案概览（PHASE 部分），生成中文 JSON 配置文件。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 文件: `implementation-details.md`
- 目标: `implementation.zh.json`（同目录）

## JSON 结构

```json
{
  "phases": [
    {
      "number": 1,
      "title": "PHASE 1 需求识别与团队构建",
      "subsections": [
        {"title": "团队构成", "content": ["..."]},
        {"title": "实施内容", "content": ["..."]},
        {"title": "相关资源", "content": ["..."]},
        {"title": "结果产出", "content": ["..."]},
        {"title": "实施周期", "content": ["..."]}
      ]
    }
  ]
}
```

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 遍历 `Content/Arena/All Arenas/` 下的 arena 目录
2. 找到下一条待处理的记录：
   - 没有 `implementation.zh.json` 文件，或者
   - `implementation-details.md` 的修改时间晚于 `implementation.zh.json`（源文件已更新）
3. 读取 `implementation-details.md` 文件
4. 定位 "1\. **方案概览**" 部分中的 PHASE 表格
5. 解析每个 PHASE 表格，提取：
   - PHASE 序号和名称
   - 团队构成
   - 实施内容
   - 相关资源
   - 结果产出
   - 实施周期
6. 构建 JSON 结构
7. 写入 `implementation.zh.json` 文件
8. 输出处理结果

## 增量更新

通过比较文件修改时间判断是否需要更新：
- 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
- 如果 `implementation-details.md` 时间戳 > `implementation.zh.json` 时间戳，则需要更新

## 用法

```bash
# 调用 skill 处理下一条
$sync-implementation-zh

# 指定 arena-folder
$sync-implementation-zh --folder 1-intelligent-research-system
```
